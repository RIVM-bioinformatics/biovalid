"""
Validation function for FASTA files.
See: https://en.wikipedia.org/wiki/FASTA_format for the FASTA file format specification.
This function checks if the FASTA file has valid header and sequence lines, and character usage.
It does not check the biological correctness of the sequences.
"""

from pathlib import Path

from biovalid.validators.base import BaseValidator


class FastaValidator(BaseValidator):
    def _check_first_char(self, byte: int, filename: Path) -> None:
        if byte != ord(">"):
            self.logger.error("File %s contains an invalid first character: %s. This must be '>'.", filename, chr(byte))

    def _handle_newline(
        self,
        is_header: bool,
        is_header_text: bool,
        is_prev_line_header: bool,
        is_line_empty: bool,
        line_num: int,
        filename: Path,
    ) -> bool:
        if is_line_empty:
            self.logger.error("File %s contains an empty line at line %d", filename, line_num)

        if is_header and not is_header_text:
            self.logger.error("File %s contains an empty header line at line %d", filename, line_num)
        if is_header and is_prev_line_header:
            self.logger.error("File %s contains consecutive header lines at line %d and %d", filename, line_num - 1, line_num)
        return is_header

    def _validate_header_byte(self, byte: int, filename: Path, line_num: int, pos_in_line: int) -> None:
        if not 32 <= byte <= 126:
            self.logger.error("File %s contains invalid character %s at line %d, position %d in header", filename, chr(byte), line_num, pos_in_line)

    def _validate_sequence_byte(self, byte: int, filename: Path, line_num: int, pos_in_line: int) -> None:
        if not (ord("a") <= byte <= ord("z") or ord("A") <= byte <= ord("Z") or byte == ord("-") or byte == ord("*")):
            self.logger.error("File %s contains invalid character %s in sequence at line %d, position %d", filename, chr(byte), line_num, pos_in_line)

    def validate(self) -> None:
        """
        Validate a FASTA file for correct formatting and character usage.
        Currently checks for:
        - The first character must be '>'.
        - Each header line must start with '>'.
        - Header lines must not be empty.
        - No consecutive header lines.
        - Valid characters in header lines (ASCII 32-126).
        - Valid characters in sequence lines (a-z, A-Z, '-', '*').

        Args:
            filename (Path | str): Path to the FASTA file to validate.

        Raises:
            RuntimeError: If any validation check fails, an error message will indicate the issue and its location in the file.

        Example:
            >>> validate_fasta("example.fasta")
            This will raise a RuntimeError if the file does not conform to FASTA format.
        """
        with self.open_binary_stream() as f:

            line_num = 1
            pos_in_line = 0
            is_header = False
            is_header_text_present = False
            is_last_line_header = False
            is_line_empty = True

            while True:
                buffer = f.read(8192)
                if not buffer:
                    break

                for byte in buffer:
                    pos_in_line += 1

                    if line_num == 1 and pos_in_line == 1:
                        self._check_first_char(byte, self.filename)

                    if byte == ord("\n"):
                        is_last_line_header = self._handle_newline(
                            is_header,
                            is_header_text_present,
                            is_last_line_header,
                            is_line_empty,
                            line_num,
                            self.filename,
                        )
                        line_num += 1
                        pos_in_line = 0
                        is_header = False
                        is_header_text_present = False
                        is_line_empty = True
                        continue

                    # Skip carriage return characters (Windows line endings)
                    if byte == ord("\r"):
                        pos_in_line -= 1  # Don't count CR in position
                        continue

                    if byte == ord(">"):
                        is_header = True
                        is_header_text_present = False
                        is_line_empty = False
                        continue

                    if is_header:
                        self._validate_header_byte(byte, self.filename, line_num, pos_in_line)
                        is_header_text_present = True
                        continue

                    self._validate_sequence_byte(byte, self.filename, line_num, pos_in_line)
                    is_line_empty = False
