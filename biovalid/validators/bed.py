"""
BED file validator.

Per the UCSC FAQ and Ensembl BED page, cross-referenced with hts-specs BEDv1
(Niu, Denisko, Hoffman 2022) for rules the others leave implicit.

  https://genome.ucsc.edu/FAQ/FAQformat.html#format1
  https://grch37.ensembl.org/info/website/upload/bed.html
  https://samtools.github.io/hts-specs/BEDv1.pdf
"""

import re

from biovalid.validators.base import BaseValidator

# §1.3: valid line separators are LF, CR, CRLF; only one kind per file.
_LINE_SEPARATOR_RE = re.compile(rb"\r\n|\r|\n")
_SEPARATOR_NAMES = {b"\n": "LF", b"\r\n": "CRLF", b"\r": "CR"}

# Trailing [ \t] anchors the keyword so a chrom literally named "track" is not skipped.
_HEADER_LINE_RE = re.compile(r"^(browser|track)[ \t]")

_MIN_COLUMNS = 3
_VALID_STRANDS = frozenset({"+", "-", "."})
# §1.5 Table 2: chrom matches [[:alnum:]_]{1,255}; blockSizes/blockStarts are comma lists.
_CHROM_RE = re.compile(r"^[A-Za-z0-9_]{1,255}$")
_BLOCK_LIST_RE = re.compile(r"^[0-9]+(,[0-9]+)*,?$")


class BedValidator(BaseValidator):
    def _hts_strict(self, msg: str, *args: object) -> None:
        """Error in --spec hts mode; silent in --spec ucsc mode."""
        if self.spec == "hts":
            self.logger.error(msg, *args)

    def _effective_n(self, ncols: int, line_num: int) -> int:
        """Resolve the BED tier N per --bed setting. Cols beyond N are opaque."""
        if self.bed_tier == "auto":
            return min(ncols, 9) if ncols < 12 else 12
        n = int(self.bed_tier)
        if ncols < n:
            self.logger.error(
                "File %s line %d has %d columns but --bed %d requires at least %d.",
                self.filename, line_num, ncols, n, n,
            )
        return n

    def validate(self) -> None:
        # Chunked scan keeps memory bounded for large (multi-GB) BED files.
        # Defer a trailing \r to the next chunk so a CRLF spanning the boundary
        # is not miscounted as \r + \n.
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
                "File %s mixes line separators (%s); hts-specs §1.3 requires a single consistent separator throughout the file.",
                self.filename,
                ", ".join(sorted(_SEPARATOR_NAMES[s] for s in separators)),
            )

        expected_columns: int | None = None
        with open(self.filename, "r", encoding="utf-8") as f:
            line_iter = enumerate(f, start=1)
            while True:
                try:
                    line_num, raw = next(line_iter)
                except StopIteration:
                    break
                except UnicodeDecodeError as e:
                    self.logger.error(
                        "File %s contains non-UTF-8 bytes near offset %d; BED files should be ASCII/UTF-8 per spec.",
                        self.filename, e.start,
                    )
                    return
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

                fields = line.split("\t")
                ncols = len(fields)

                if ncols < _MIN_COLUMNS:
                    self.logger.error(
                        "File %s line %d has %d tab-separated columns; BED requires at least 3.",
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
            if not (1 <= len(name) <= 255):
                self.logger.error(
                    "File %s line %d has an invalid name field length %d; must be 1-255 characters.",
                    self.filename, line_num, len(name),
                )

        if effective_n >= 5:
            score_str = fields[4]
            if not score_str:
                self.logger.error("File %s line %d has empty score field.", self.filename, line_num)
            elif self.spec == "hts":
                if not score_str.isdigit():
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

        for i, size in enumerate(sizes_i):
            if size == 0:
                self.logger.error(
                    "File %s line %d: block %d has size 0; block sizes must be positive.",
                    self.filename, line_num, i,
                )

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
