"""
Validation function for GFF3 files.
See: https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md for the GFF3 file format specification.
This function checks if the GFF3 file has a valid header, column structure, and ontology terms.
It does not check the biological correctness of the annotation.
"""

import re
from enum import Enum

from biovalid.util.gff.legacy_so_mapping import deprecated_so_mapping
from biovalid.util.gff.obo_parser import get_valid_types
from biovalid.validators.base import BaseValidator


class GffColumns(Enum):
    """Standard GFF3 column indices."""

    SEQID = 0
    SOURCE = 1
    TYPE = 2
    START = 3
    END = 4
    SCORE = 5
    STRAND = 6
    PHASE = 7
    ATTRIBUTES = 8

    @classmethod
    def to_list(cls) -> list[str]:
        """Returns a list of column names."""
        return [member.name for member in cls]

    @classmethod
    def number_of_columns(cls) -> int:
        """Returns the number of GFF columns."""
        return len(cls)


class Attributes(Enum):
    """Standard GFF3 attribute keys."""

    ID = "ID"
    NAME = "Name"
    ALIAS = "Alias"
    PARENT = "Parent"
    TARGET = "Target"
    GAP = "Gap"
    DERIVED_FROM = "Derives_from"
    NOTE = "Note"
    DBXREF = "Dbxref"
    ONTOLOGY_TERM = "Ontology_term"
    IS_CIRCULAR = "Is_circular"


class GffValidator(BaseValidator):
    """
    Validator for GFF3 files.
    Validates header and data lines according to the GFF3 specification.
    """

    def validate(self) -> None:
        with self.filename.open("r") as gff_file:
            lines = gff_file.readlines()

        self._check_header_lines(lines)
        self._check_data_lines(lines)

    def _check_header_lines(self, lines: list[str]) -> None:
        first_data_idx = next((i for i, line in enumerate(lines) if not line.startswith("#")), len(lines))

        for i, line in enumerate(lines[first_data_idx:], start=first_data_idx):
            if line.startswith("#"):
                self.log(40, f"Header line found after data has started at line {i+1}")

        if not any("gff-version" in line for line in lines[:first_data_idx]):
            self.log(40, "Missing required GFF version declaration")

    def _check_data_lines(self, lines: list[str]) -> None:
        data_lines = [line for line in lines if not line.startswith("#")]

        for i, line in enumerate(data_lines):
            columns = line.strip().split("\t")
            if len(columns) < GffColumns.number_of_columns():
                columns += ["."] * (GffColumns.number_of_columns() - len(columns))
                self.log(
                    30,
                    f"File {self.filename} contains an invalid number of columns in line {i+1}. Padded the missing columns with placeholders.",
                )
            elif len(columns) > GffColumns.number_of_columns():
                self.log(
                    40,
                    f"File {self.filename} contains an invalid number of columns in line {i+1}:"
                    f" {line.strip()}, it should be 9: {GffColumns.to_list()}",
                )

            self.validate_columns(columns)

    def validate_columns(self, columns: list[str]) -> None:
        """Validates all columns for a single row in a GFF file"""
        self._check_seqid(columns[GffColumns.SEQID.value])
        valid_types = get_valid_types()

        self._check_type(columns[GffColumns.TYPE.value], valid_types)
        self._check_start_end(columns[GffColumns.START.value], columns[GffColumns.END.value])
        self._check_score(columns[GffColumns.SCORE.value])
        self._check_strand(columns[GffColumns.STRAND.value])
        self._check_phase(columns[GffColumns.PHASE.value], columns[GffColumns.TYPE.value])
        self._check_attributes(columns[GffColumns.ATTRIBUTES.value])

    def _check_seqid(self, seqid: str) -> None:
        """seqid must be in: [a-zA-Z0-9.:^*$@!+_?-|]"""
        pattern = r"^[a-zA-Z0-9.:^*$@!+_?-|]+$"
        if not re.match(pattern, seqid.strip()):
            self.log(
                40,
                f"File {self.filename} contains an invalid seqid: {seqid}. Seqid must match the pattern: {pattern}",
            )

    def _check_type(self, feature_type: str, valid_types: list[str]) -> None:
        """
        type must be a valid SO term.
        Exceptions:
        - If the type contains a single quote, try replacing it with "' " and check again.
        - If the valid type contains a ":", allow a match to either the part before or after the ":".
        """
        lwr_feature_type = feature_type.strip().lower()
        if lwr_feature_type in valid_types:
            return

        # Exception for single quote
        if "'" in lwr_feature_type:
            changed = lwr_feature_type.replace("'", "' ")
            if changed in valid_types:
                return

        # Exception for colon in valid_types
        for vt in valid_types:
            if ":" in vt:
                before, after = vt.split(":", 1)
                if lwr_feature_type in (before, after):
                    return

        # check legacy types
        if lwr_feature_type in deprecated_so_mapping:
            replacement = deprecated_so_mapping[lwr_feature_type]["replacement"]
            assert isinstance(replacement, dict)
            self.log(
                30,
                f"File {self.filename} contains a deprecated SO term: {feature_type}. "
                f"Consider replacing with '{replacement['so_name']}' ({replacement['so_id']}).",
            )
            return

        self.log(40, f"File {self.filename} contains an invalid type: {feature_type}")

    def _check_start_end(self, start: str, end: str) -> None:
        """
        start and end must be integers.
        start must be less than or equal to end.
        start and end cannot be negative.
        """
        start = start.strip()
        end = end.strip()
        if not start.isdigit():
            self.log(
                40,
                f"File {self.filename} contains an invalid start: {start}. Start must be a non-negative integer.",
            )
        if not end.isdigit():
            self.log(
                40,
                f"File {self.filename} contains an invalid end: {end}. End must be a non-negative integer.",
            )
        if int(start) > int(end):
            self.log(
                40,
                f"File {self.filename} contains an invalid start-end range: {start} > {end}. Start must be less than or equal to end.",
            )

    def _is_float(self, s: str) -> bool:
        parts = s.split(".")
        if len(parts) == 1:
            return parts[0].isdigit()
        if len(parts) == 2:
            return parts[0].isdigit() and parts[1].isdigit()
        return False

    def _check_score(self, score: str) -> None:
        """score must be a float or '.'"""
        if not self._is_float(score) and score.strip() != ".":
            self.log(
                40,
                f"File {self.filename} contains an invalid score: {score}. Score must be a float value or a .",
            )

    def _check_strand(self, strand: str) -> None:
        """strand must be one of: +, -, ., ?"""
        strand = strand.strip()
        if strand not in {"+", "-", ".", "?"}:
            self.log(
                40,
                f"File {self.filename} contains an invalid strand: {strand}. Strand must be one of: +, -, ., ?",
            )

    def _check_phase(self, phase: str, feature_type: str) -> None:
        """
        If phase is a CDS feature, it must be one of: 0, 1, 2.
        For the rest it is a free text field.
        It is optional for non CDS values.
        """
        if feature_type == "CDS":
            if not phase:
                self.log(
                    40,
                    f"File {self.filename} contains no phase in a CDS feature. This is required for CDS features.",
                )
            if phase not in {"0", "1", "2"}:
                self.log(
                    40,
                    f"File {self.filename} contains an invalid phase for CDS: {phase}. Phases must be one of: 0, 1, 2.",
                )

    def _check_attributes(self, attributes: str) -> None:
        """attributes must be a valid GFF attribute string."""
        if not attributes:
            self.log(
                40,
                f"File {self.filename} does not contain attributes. Attributes are required.",
            )
