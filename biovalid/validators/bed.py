"""
BED file validator.

Per the UCSC FAQ and Ensembl BED page, cross-referenced with hts-specs BEDv1
(Niu, Denisko, Hoffman 2022) for rules the others leave implicit.

  https://genome.ucsc.edu/FAQ/FAQformat.html#format1
  https://grch37.ensembl.org/info/website/upload/bed.html
  https://samtools.github.io/hts-specs/BEDv1.pdf

The field separator [ \\t]+ (hts-specs §1.5) is treated as a single separator
between fields: a run of consecutive tabs or spaces does not synthesize an
empty field. Trailing horizontal whitespace on a line is likewise stripped
rather than treated as a trailing empty field. Strict §1.5 admits either
reading; we take the regex-literal one.
"""

import re
from logging import Logger
from pathlib import Path

from biovalid.validators.base import BaseValidator

# §1.4: valid line separators are LF, CR, CRLF; only one kind per file.
_LINE_SEPARATOR_RE = re.compile(rb"\r\n|\r|\n")
_SEPARATOR_NAMES = {b"\n": "LF", b"\r\n": "CRLF", b"\r": "CR"}

# §1.5: field separator is "[ \t]+" (one or more space or tab).
# UCSC FAQ: "whitespace-delimited or tab-delimited". Same regex covers both.
_FIELD_SEPARATOR_RE = re.compile(r"[ \t]+")

# Trailing [ \t] anchors the keyword so a chrom literally named "track" is not skipped.
_HEADER_LINE_RE = re.compile(r"^(browser|track)[ \t]")

_MIN_COLUMNS = 3
_VALID_STRANDS = frozenset({"+", "-", "."})
# §1.5 Table 2: chrom matches [[:alnum:]_]{1,255}; blockSizes/blockStarts are comma lists.
_CHROM_RE = re.compile(r"^[A-Za-z0-9_]{1,255}$")
_BLOCK_LIST_RE = re.compile(r"^[0-9]+(,[0-9]+)*,?$")
# §1.5 Table 2: name matches printable ASCII [\x20-\x7e]{1,255}. UCSC is silent
# but no real reader renders control bytes or non-ASCII meaningfully, so the
# hts rule is the sensible floor in both modes.
_NAME_RE = re.compile(r"^[\x20-\x7e]{1,255}$")


class BedValidator(BaseValidator):
    """Validator for BED files."""

    def __init__(
        self,
        filename: Path,
        logger: Logger | None = None,
        spec: str = "ucsc",
        bed_tier: str = "auto",
    ) -> None:
        super().__init__(filename, logger)
        self.spec = spec
        self.bed_tier = bed_tier

    def _hts_strict(self, msg: str, *args: object) -> None:
        """Error in --spec hts mode; silent in --spec ucsc mode."""
        if self.spec == "hts":
            self.logger.error(msg, *args)

    def _effective_n(self, ncols: int, line_num: int) -> int:
        """Resolve the BED tier N per --bed setting. Cols beyond N are opaque."""
        if self.bed_tier == "auto":
            if ncols in (10, 11):
                # §1.5: BED10 and BED11 are prohibited; UCSC FAQ is silent.
                self._hts_strict(
                    "File %s line %d has %d columns; hts-specs §1.5 prohibits BED10 and BED11 "
                    "(valid tiers are BED3-BED9 and BED12). Use --bed N to declare BED9+M.",
                    self.filename, line_num, ncols,
                )
            return min(ncols, 9) if ncols < 12 else 12
        n = int(self.bed_tier)
        if ncols < n:
            self.logger.error(
                "File %s line %d has %d columns but --bed %d requires at least %d.",
                self.filename, line_num, ncols, n, n,
            )
        return n

    def _check_line_separators(self) -> None:
        # Binary pre-pass: text mode's universal-newlines collapses CR/LF/CRLF
        # to \n, so mixed-separator detection has to happen before decoding.
        # Defer a trailing \r so a CRLF spanning a chunk boundary is not
        # miscounted as \r + \n. Early-exits once two separator types are seen.
        separators: set[bytes] = set()
        with open(self.filename, "rb") as f:
            leftover = b""
            while chunk := f.read(65536):
                if chunk.endswith(b"\r"):
                    data, leftover = leftover + chunk[:-1], b"\r"
                else:
                    data, leftover = leftover + chunk, b""
                separators.update(_LINE_SEPARATOR_RE.findall(data))
                if len(separators) > 1:
                    break
            if leftover:
                separators.update(_LINE_SEPARATOR_RE.findall(leftover))
        if len(separators) > 1:
            self.logger.error(
                "File %s mixes line separators (%s); hts-specs §1.4 requires a single consistent separator throughout the file.",
                self.filename,
                ", ".join(sorted(_SEPARATOR_NAMES[s] for s in separators)),
            )

    def validate(self) -> None:
        self._check_line_separators()

        expected_columns: int | None = None
        # latin-1 maps every byte to a codepoint, so any byte sequence decodes
        # without error. No spec mandates an encoding, so we don't impose one;
        # content rules (chrom charset in hts mode, numeric fields, etc.) do
        # the real validation.
        with open(self.filename, "r", encoding="latin-1") as f:
            for line_num, raw in enumerate(f, start=1):
                line = raw.rstrip("\n").rstrip("\r")
                if not line.strip() or line.startswith("#"):
                    continue
                if _HEADER_LINE_RE.match(line):
                    self._hts_strict(
                        "File %s line %d contains a 'browser' or 'track' header line; "
                        "hts-specs §5 says such a file is a track file, not a BED file.",
                        self.filename, line_num,
                    )
                    continue

                # §1.5: separator is [ \t]+. Strip leading/trailing horizontal
                # whitespace so a stray leading space does not synthesize an
                # empty first field.
                fields = _FIELD_SEPARATOR_RE.split(line.strip(" \t"))
                ncols = len(fields)

                if ncols < _MIN_COLUMNS:
                    self.logger.error(
                        "File %s line %d has %d fields; BED requires at least 3.",
                        self.filename, line_num, ncols,
                    )

                if expected_columns is None:
                    expected_columns = ncols
                elif ncols != expected_columns:
                    self.logger.error(
                        "File %s line %d has %d columns but the file's first data line had %d; column count must be uniform.",
                        self.filename, line_num, ncols, expected_columns,
                    )

                effective_n = self._effective_n(ncols, line_num)
                self._validate_fields(fields, line_num, effective_n)

    def _validate_fields(self, fields: list[str], line_num: int, effective_n: int) -> None:
        chrom = fields[0]
        if not _CHROM_RE.match(chrom):
            self._hts_strict(
                "File %s line %d has chrom '%s' that does not match the hts-specs character "
                "class [A-Za-z0-9_]{1,255}.",
                self.filename, line_num, chrom,
            )

        chrom_start = self._parse_nonneg_int(fields[1], "chromStart", line_num)
        chrom_end = self._parse_nonneg_int(fields[2], "chromEnd", line_num)
        if chrom_end < chrom_start:
            self.logger.error(
                "File %s line %d has chromEnd (%d) < chromStart (%d).",
                self.filename, line_num, chrom_end, chrom_start,
            )

        if effective_n >= 4:
            name = fields[3]
            if not _NAME_RE.match(name):
                # §1.5 Table 2: name is [\x20-\x7e]{1,255} (printable ASCII).
                self.logger.error(
                    "File %s line %d has a name field that does not match printable ASCII "
                    "[\\x20-\\x7e]{1,255}.",
                    self.filename, line_num,
                )

        if effective_n >= 5:
            # §1.7: score is an integer in [0, 1000]. UCSC FAQ score field:
            # "between 0 and 1000". Both specs agree, so the rule is universal.
            score_str = fields[4]
            if not score_str:
                self.logger.error("File %s line %d has empty score field.", self.filename, line_num)
            elif not score_str.isdigit():
                self.logger.error(
                    "File %s line %d has non-integer score '%s'.",
                    self.filename, line_num, score_str,
                )
            elif int(score_str) > 1000:
                self.logger.error(
                    "File %s line %d has score %s outside the spec range 0-1000.",
                    self.filename, line_num, score_str,
                )

        if effective_n >= 6 and fields[5] not in _VALID_STRANDS:
            self.logger.error(
                "File %s line %d has invalid strand '%s'; must be '+', '-', or '.'.",
                self.filename, line_num, fields[5],
            )

        if effective_n >= 8:
            thick_start = self._parse_nonneg_int(fields[6], "thickStart", line_num)
            thick_end = self._parse_nonneg_int(fields[7], "thickEnd", line_num)
            if thick_start < chrom_start or thick_end > chrom_end or thick_end < thick_start:
                self.logger.error(
                    "File %s line %d has thick range [%d, %d] outside chrom range [%d, %d] or inverted.",
                    self.filename, line_num, thick_start, thick_end, chrom_start, chrom_end,
                )

        if effective_n >= 9:
            self._validate_item_rgb(fields[8], line_num)

        if effective_n == 12:
            self._validate_blocks(fields[9], fields[10], fields[11], chrom_end - chrom_start, line_num)

    def _parse_nonneg_int(self, value: str, field_name: str, line_num: int) -> int:
        if value.startswith("-") and value[1:].isdigit():
            self.logger.error(
                "File %s line %d has negative %s '%s'; coordinates must be >= 0.",
                self.filename, line_num, field_name, value,
            )
        if not value or not value.isdigit():
            self.logger.error(
                "File %s line %d has non-integer %s '%s'.",
                self.filename, line_num, field_name, value,
            )
        return int(value)

    def _validate_item_rgb(self, value: str, line_num: int) -> None:
        # §1.8: a single "0" is a special-case shorthand for "0,0,0".
        if value == "0":
            return
        parts = value.split(",")
        if len(parts) != 3 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            self.logger.error(
                "File %s line %d has invalid itemRgb '%s'; must be '0' or 'R,G,B' with each component 0-255.",
                self.filename, line_num, value,
            )

    def _validate_blocks(self, count_str: str, sizes_str: str, starts_str: str, span: int, line_num: int) -> None:
        count = self._parse_nonneg_int(count_str, "blockCount", line_num)
        if count == 0:
            self.logger.error("File %s line %d has blockCount 0; must be >= 1.", self.filename, line_num)

        for label, raw in (("blockSizes", sizes_str), ("blockStarts", starts_str)):
            if not _BLOCK_LIST_RE.match(raw):
                self.logger.error(
                    "File %s line %d has malformed %s '%s'; must be comma-separated integers with an optional trailing comma.",
                    self.filename, line_num, label, raw,
                )
        sizes = [s for s in sizes_str.split(",") if s != ""]
        starts = [s for s in starts_str.split(",") if s != ""]
        if len(sizes) != count or len(starts) != count:
            self.logger.error(
                "File %s line %d: blockCount=%d but blockSizes has %d entries and blockStarts has %d.",
                self.filename, line_num, count, len(sizes), len(starts),
            )

        sizes_i = [self._parse_nonneg_int(s, "blockSizes entry", line_num) for s in sizes]
        starts_i = [self._parse_nonneg_int(s, "blockStarts entry", line_num) for s in starts]

        if starts_i[0] != 0:
            self.logger.error(
                "File %s line %d: first blockStart must be 0, got %d.",
                self.filename, line_num, starts_i[0],
            )
        if starts_i[-1] + sizes_i[-1] != span:
            self.logger.error(
                "File %s line %d: last blockStart (%d) + last blockSize (%d) must equal chromEnd - chromStart (%d).",
                self.filename, line_num, starts_i[-1], sizes_i[-1], span,
            )
        for i in range(1, count):
            if starts_i[i] < starts_i[i - 1] + sizes_i[i - 1]:
                self.logger.error(
                    "File %s line %d: block %d starts at %d, overlapping previous block ending at %d.",
                    self.filename, line_num, i, starts_i[i], starts_i[i - 1] + sizes_i[i - 1],
                )
