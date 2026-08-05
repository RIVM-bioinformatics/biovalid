"""
Validation function for FASTQ files.
See: https://en.wikipedia.org/wiki/FASTQ_format for the FASTQ file format specification.
This function checks if the FASTQ file has valid record structure, sequence, and quality lines.
It does not check the biological correctness of the sequences.
"""

from biovalid.validators.base import BaseValidator


class FastqValidator(BaseValidator):
    def _decode_for_log(self, line: bytes) -> str:
        return line.decode("utf-8", errors="replace")

    def _validate_record_is_complete(self, sequence: bytes, plus_line: bytes, quality: bytes, line_num: int) -> None:
        if not sequence or not quality or not plus_line:
            self.logger.error(
                "File %s contains an incomplete FASTQ record at line %d. Each record must consist of 4 lines: header, sequence, plus line, and quality.",
                self.filename,
                line_num,
            )

    def _validate_header(self, header: bytes, line_num: int) -> None:
        if not header.startswith(b"@"):
            self.logger.error(
                "File %s contains an invalid header line at line %d: %s. This must start with '@'.",
                self.filename,
                line_num + 1,
                self._decode_for_log(header),
            )

    def _validate_sequence(self, sequence: bytes, line_num: int, valid_sequence_chars: set[int]) -> None:
        if not all(c in valid_sequence_chars for c in sequence):
            self.logger.error(
                "File %s contains invalid characters in sequence line at line %d: %s. Valid characters are ACGTNacgtn-.*",
                self.filename,
                line_num + 2,
                self._decode_for_log(sequence),
            )

    def _validate_plus_line(self, plus_line: bytes, line_num: int) -> None:
        if plus_line != b"+":
            self.logger.error(
                "File %s contains an invalid plus line at line %d: %s. This must be a single '+' character.",
                self.filename,
                line_num + 3,
                self._decode_for_log(plus_line),
            )

    def _validate_quality(self, quality: bytes, sequence: bytes, line_num: int) -> None:
        if len(quality) != len(sequence):
            self.logger.error(
                "File %s contains an invalid quality line length at line %d: %s. The quality line must have the same length as the sequence line.",
                self.filename,
                line_num + 4,
                self._decode_for_log(quality),
            )

        if not all(33 <= c <= 126 for c in quality):
            self.logger.error(
                "File %s contains invalid characters in quality line at line %d: %s. Valid characters are ASCII 33 to 126.",
                self.filename,
                line_num + 4,
                self._decode_for_log(quality),
            )

    def _normalize_record(self, header: bytes, sequence: bytes, plus_line: bytes, quality: bytes) -> tuple[bytes, bytes, bytes, bytes]:
        # Strip line terminators and surrounding whitespace before validation checks.
        return header.strip(), sequence.strip(), plus_line.strip(), quality.strip()

    def validate(self) -> None:
        valid_sequence_chars = set(b"ACGTNacgtn-.*")

        with self.open_binary_stream() as f:
            line_num = 0

            while True:
                header = f.readline()
                if not header:
                    break
                sequence = f.readline()
                plus_line = f.readline()
                quality = f.readline()

                self._validate_record_is_complete(sequence, plus_line, quality, line_num)
                header, sequence, plus_line, quality = self._normalize_record(header, sequence, plus_line, quality)
                self._validate_header(header, line_num)
                self._validate_sequence(sequence, line_num, valid_sequence_chars)
                self._validate_plus_line(plus_line, line_num)
                self._validate_quality(quality, sequence, line_num)
                line_num += 4
