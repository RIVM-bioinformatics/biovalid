"""
Validation function for VCF files.
See: https://github.com/samtools/hts-specs for the VCF file format specification.
This function checks if the VCF file has valid header lines, column structure, and field values.
It does not check the biological correctness of the variants.
"""

import re
from string import ascii_letters

from biovalid.util.vcf.vcf_models import (
    AltField,
    AltTypes,
    FilterField,
    FormatField,
    InfoField,
    VCFHeaders,
)
from biovalid.validators.base import BaseValidator


class VcfValidator(BaseValidator):
    """Validator for VCF files."""

    def _check_first_line(self, line: str) -> bool:
        return line.startswith("##fileformat=VCFv")

    def validate(self) -> None:
        with self.filename.open("r") as vcf_file:
            # Read and process file sequentially
            first_line = vcf_file.readline()
            if not first_line:
                self.log(40, "VCF file is empty")
                return

            if not self._check_first_line(first_line):
                self.log(
                    40, f"File does not start with a valid VCF header line: {first_line.strip()}. It should start with '##fileformat=VCFv[VERSION]'"
                )
                return

            # Parse headers sequentially
            # The readline above removes the first line from the file iterator, so we manually add it back and start counting lines from 1
            top_headers: list[str] = [first_line.strip()]
            normal_header: list[str] = []
            data_lines: list[list[str]] = []
            line_number = 1

            # Read meta-information lines (##)
            for line in vcf_file:
                line_number += 1
                line = line.strip()
                if not line:
                    continue
                if line.startswith("##"):
                    top_headers.append(line)
                elif line.startswith("#"):
                    # This is the column header line
                    normal_header = line.split("\t")
                else:
                    data_lines.append(line.split("\t"))

            self.validate_top_headers(top_headers)
            info_tuple = self._extract_fields(top_headers)
            self.validate_normal_header(normal_header)
            headers = self._get_headers(normal_header)
            format_header_present = "FORMAT" in headers
            self.validate_data_lines(data_lines, len(normal_header), line_number - len(data_lines), info_tuple, include_format=format_header_present)

    def _parse_key_value_pairs(self, content: str) -> dict[str, str]:
        """Helper method to parse key=value pairs from a VCF header content string."""
        res: dict[str, str] = {}
        regex_pattern = r"""(?:[^,'"]|"(?:\\.|[^"])*"|'(?:\\.|[^'])*')+"""  # Handles commas inside quotes
        for part in re.findall(regex_pattern, content):
            key, value = part.split("=", 1)
            res[key.strip()] = value.strip().replace('"', "").replace("'", "")
        return res

    def _extract_fields(self, headers: list[str]) -> tuple[dict[str, InfoField], dict[str, FilterField], dict[str, FormatField], dict[str, AltField]]:
        info_fields: dict[str, InfoField] = {}
        filter_fields: dict[str, FilterField] = {}
        format_fields: dict[str, FormatField] = {}
        alt_info: dict[str, AltField] = {}

        for line in headers:
            if line.startswith("##INFO="):
                # Extract INFO field details
                content = line[len("##INFO=") :].strip("<>")
                parts = self._parse_key_value_pairs(content)
                info_field = InfoField(
                    id=parts.get("ID", ""),
                    number=parts.get("Number", ""),
                    type=parts.get("Type", ""),
                    description=parts.get("Description", "").strip('"'),
                )
                info_fields[info_field.id] = info_field
            elif line.startswith("##FILTER="):
                # Extract FILTER field details
                content = line[len("##FILTER=") :].strip("<>")
                parts = self._parse_key_value_pairs(content)
                filter_field = FilterField(
                    id=parts.get("ID", ""),
                    description=parts.get("Description", "").strip('"'),
                )
                filter_fields[filter_field.id] = filter_field
            elif line.startswith("##FORMAT="):
                # Extract FORMAT field details
                content = line[len("##FORMAT=") :].strip("<>")
                parts = self._parse_key_value_pairs(content)
                format_field = FormatField(
                    id=parts.get("ID", ""),
                    number=parts.get("Number", ""),
                    type=parts.get("Type", ""),
                    description=parts.get("Description", "").strip('"'),
                )
                format_fields[format_field.id] = format_field
            elif line.startswith("##ALT="):
                # Extract ALT field details
                content = line[len("##ALT=") :].strip("<>")
                parts = self._parse_key_value_pairs(content)
                alt_field = AltField(
                    id=AltTypes(parts.get("ID", "")),
                    description=parts.get("Description", "").strip('"'),
                )
                alt_info[alt_field.id.value] = alt_field

        return info_fields, filter_fields, format_fields, alt_info

    def validate_top_headers(self, headers: list[str]) -> None:
        """Validate top-level VCF headers (##)."""
        for line in headers:
            if not line.startswith("##"):
                self.log(40, f"Invalid top-level header line: {line}")

    def validate_normal_header(self, normal_header: list[str]) -> None:
        """Validate the normal column header line (#CHROM ...)."""
        if not normal_header:
            self.log(40, "VCF file missing required column header line (should start with single #)")

        if len(normal_header) < 8:
            self.log(40, f"VCF column header has fewer than 8 required columns: {normal_header}")

        required_headers = [header.value for header in VCFHeaders][:8]
        for i, required_header in enumerate(required_headers):
            if normal_header[i].replace("#", "") != required_header:  # Remove leading # from #CHROM
                self.log(40, f"VCF column header mismatch at position {i+1}: expected '{required_header}', got '{normal_header[i]}'")

    def _get_headers(self, normal_header: list[str]) -> list[str]:
        """Helper method to get the list of standard VCF headers."""
        return [header.replace("#", "") for header in normal_header]  # Remove leading # from #CHROM

    def validate_data_lines(
        self,
        data_matrix: list[list[str]],
        column_count: int,
        line_number: int,
        info: tuple[dict[str, InfoField], dict[str, FilterField], dict[str, FormatField], dict[str, AltField]],
        include_format: bool = True,
    ) -> None:
        """Validate VCF data lines."""
        info_fields, filter_fields, format_fields, _alt_info = info

        # Process data lines
        for data_row in data_matrix:
            line_number += 1
            if not data_row:
                continue

            if data_row[0].startswith("#"):
                self.log(40, f"Unexpected header line found at line {line_number}: {data_row}, outside of the header section.")

            if len(data_row) != column_count:
                self.log(40, f"VCF data line {line_number} does not have the required {column_count} columns: {data_row}")

            clean_data_row = [col.strip() for col in data_row]

            if include_format and len(clean_data_row) < 9:
                self.log(40, f"VCF data line {line_number} missing required columns: {data_row}")
            elif not include_format and len(clean_data_row) < 8:
                self.log(40, f"VCF data line {line_number} missing required columns: {data_row}")

            # Validate each required column by index
            self.validate_chrom(clean_data_row[0], line_number)
            self.validate_pos(clean_data_row[1], line_number)
            self.validate_id(clean_data_row[2], line_number)
            self.validate_ref(clean_data_row[3], line_number)
            self.validate_alt(clean_data_row[4], line_number)
            self.validate_qual(clean_data_row[5], line_number)
            self.validate_filter(clean_data_row[6], line_number, filter_fields)
            self.validate_info(clean_data_row[7], line_number, info_fields)
            if include_format:
                self.validate_format(clean_data_row[8], line_number, format_fields)
                self.validate_sample_columns(clean_data_row[9:], line_number)
            else:
                self.validate_sample_columns(clean_data_row[8:], line_number)

    def validate_chrom(self, value: str, line_number: int) -> None:
        """
        Validate chromosome column.
        From the VCF specification: (String, no whitespace permitted, Required).
        """
        if not value:
            self.log(40, f"VCF line {line_number}: CHROM column is empty")

        if re.search(r"\s", value):  # "\s" matches any whitespace character
            self.log(40, f"VCF line {line_number}: CHROM contains whitespace characters: '{value}'")

    def validate_pos(self, value: str, line_number: int) -> None:
        """
        Validate position column.
        From the VCF specification: (Integer, Required).
        """
        if not value:
            self.log(40, f"VCF line {line_number}: POS column is empty")

        if not value.isdigit():
            self.log(40, f"VCF line {line_number}: POS must be an integer, got '{value}' which is type {type(value)}")

    def validate_id(self, value: str, line_number: int) -> None:
        """
        Validate ID column.
        From the VCF specification: (String, no whitespace or semicolons permitted, Required).
        ID can be '.' for missing, or semicolon-separated list of identifiers
        """
        if not value:
            self.log(40, f"VCF line {line_number}: ID column is empty")

        # Semicolon is not allowed within the values of the ID because it is used as the separator
        # We only check for whitespace here
        if re.search(r"\s", value):
            self.log(40, f"VCF line {line_number}: ID contains whitespace: '{value}'")

    def validate_ref(self, value: str, line_number: int) -> None:
        """
        Validate reference allele column.
        From the VCF specification: (String, no whitespace permitted, Required).
        Can be '.' for no reference allele, or else should contain valid DNA bases (A, C, G, T, N).
        Not U, also no other IUPAC codes.
        """
        if not value:
            self.log(40, f"VCF line {line_number}: REF column is empty")
        if value == ".":
            return

        # all ACGTN are fine
        # rest of the IUPAC codes are valid but should raise a warning
        # rest should raise an error

        invalid_chars = [c for c in value if c.upper() not in "ACGTN" and c not in ascii_letters + "-" + "*"]
        ambiguous_chars = [c for c in value if c in ascii_letters + "-" + "*" and c.upper() not in "ACGTN"]

        if not invalid_chars and not ambiguous_chars:
            return
        if not [c for c in invalid_chars if c not in ascii_letters + "-" + "*"]:
            # Only ambiguous bases present
            self.log(30, f"VCF line {line_number}: REF contains ambiguous bases: '{''.join(ambiguous_chars)}' in '{value}'")
        else:
            self.log(40, f"VCF line {line_number}: REF contains invalid base(s): '{''.join(invalid_chars)}' in '{value}'")

    def validate_alt(self, value: str, line_number: int) -> None:
        """
        Validate alternative allele column.
        From the VCF specification: (String; no whitespace, commas, or angle-brackets are permitted in the ID String itself)
        Can be '.' for no alternate, or comma-separated alleles
        """
        if not value:
            self.log(40, f"VCF line {line_number}: ALT column is empty")
        if value == ".":
            return
        alt_alleles = value.split(",")
        if len(alt_alleles) == 0:
            self.log(40, f"VCF line {line_number}: ALT column has no alleles specified. It should be '.' or contain at least one allele.")

        if any(not allele for allele in alt_alleles):
            self.log(40, f"VCF line {line_number}: ALT column contains empty alleles.")

        invalid_chars: list[str] = []
        ambiguous_chars: list[str] = []
        for allele in alt_alleles:
            allele = allele.strip()
            if allele == ".":
                continue

            invalid_chars.extend([c for c in allele if c.upper() not in "ACGTN" and c not in ascii_letters + "-" + "*"])
            ambiguous_chars.extend([c for c in allele if c in ascii_letters + "-" + "*" and c.upper() not in "ACGTN"])

        if not invalid_chars and not ambiguous_chars:
            return
        if not [c for c in invalid_chars if c not in ascii_letters + "-" + "*"]:
            # Only ambiguous bases present
            self.log(30, f"VCF line {line_number}: ALT contains ambiguous bases: '{''.join(ambiguous_chars)}' in '{value}'")
        else:
            self.log(40, f"VCF line {line_number}: ALT contains invalid base(s): '{''.join(invalid_chars)}' in '{value}'")

    def validate_qual(self, value: str, line_number: int) -> None:
        """
        Validate quality score column.
        From the VCF specification: (Numeric).
        Phred-scaled quality score or '.' if unknown
        """
        if not value:
            self.log(40, f"VCF line {line_number}: QUAL column is empty")
        if value == ".":
            return

        # I really dont like using exceptions for control flow but float() is the only way that is this complete
        # think about nan, inf, -inf, 1e10, 1.5 etc.
        try:
            float(value)
            if float(value) < 0:
                self.log(40, f"VCF line {line_number}: QUAL must be a positive numeric value, got '{value}'")
        except ValueError:
            self.log(40, f"VCF line {line_number}: QUAL must be a positive numeric value, got '{value}'")

    def validate_filter(self, value: str, line_number: int, filter_fields: dict[str, FilterField]) -> None:
        """
        Validate filter column.
        From the VCF specification: (String; no whitespace or semicolons permitted in the ID String itself).
        """
        if not value:
            self.log(40, f"VCF line {line_number}: FILTER column is empty")

        valid_filters = set(filter_fields.keys()).union({"PASS", "."})
        filters = value.split(";")
        for filt in filters:
            filt = filt.strip()
            if filt not in valid_filters:
                self.log(
                    40,
                    f"VCF line {line_number}: FILTER contains unknown filter '{filt}'. All filters must be defined in the header or be 'PASS' or '.'",
                )

    def validate_info(self, value: str, line_number: int, info_fields: dict[str, InfoField]) -> None:
        """
        Validate info column.
        From the VCF specification: (String, no whitespace, semicolons, or equals-signs permitted;
        commas are permitted only as delimiters for lists of values).
        """

        if not value:
            self.log(40, f"VCF line {line_number}: INFO column is empty")
        if value == "." and info_fields:
            self.log(40, f"VCF line {line_number}: INFO column is '.' but INFO fields are defined in the header")
        valid_info_keys = set(info_fields.keys()).union({"."})
        items = value.split(";")
        for item in items:
            item = item.strip()
            if item == ".":
                continue
            if "=" in item:
                key, _ = item.split("=", 1)
                key = key.strip()
                if key not in valid_info_keys:
                    self.log(40, f"VCF line {line_number}: INFO contains unknown key '{key}'. All INFO keys must be defined in the header or be '.'")
            else:
                key = item.strip()
                if key not in valid_info_keys:
                    self.log(40, f"VCF line {line_number}: INFO contains unknown flag '{key}'. All INFO keys must be defined in the header or be '.'")

    def validate_format(self, value: str, line_number: int, format_fields: dict[str, FormatField]) -> None:
        """
        Validate format column.
        From the VCF specification: (colon-separated alphanumeric String).
        """
        if not value:
            self.log(40, f"VCF line {line_number}: FORMAT column is empty")
        valid_format_keys = set(format_fields.keys())
        format_keys = value.split(":")
        for key in format_keys:
            key = key.strip()
            if key not in valid_format_keys:
                self.log(40, f"VCF line {line_number}: FORMAT contains unknown key '{key}'. All FORMAT keys must be defined in the header.")

    def validate_sample_columns(self, values: list[str], line_number: int) -> None:
        """Validate sample data columns."""
        for i, value in enumerate(values):
            if not value:
                self.log(40, f"VCF line {line_number}: Sample column {i+1} is empty")
