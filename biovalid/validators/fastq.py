"""
Validation function for FASTQ files.
See: https://en.wikipedia.org/wiki/FASTQ_format for the FASTQ file format specification.
This function checks if the FASTQ file has valid record structure, sequence, and quality lines.
It does not check the biological correctness of the sequences.
"""

from biovalid.validators.base import BaseValidator


class FastqValidator(BaseValidator):
    def validate(self) -> None:
        with open(self.filename, "r", encoding="utf-8") as f:
            line_num = 0

            while True:
                header = f.readline()
                if not header:
                    break
                sequence = f.readline()
                plus_line = f.readline()
                quality = f.readline()

                if not sequence or not quality or not plus_line:
                    self.log(
                        40,
                        f"File {self.filename} contains an incomplete FASTQ record at line {line_num}",
                    )

                # dont strip at once because it might throw an error if a line is empty (e.g. last line)
                header = header.strip()
                sequence = sequence.strip()
                plus_line = plus_line.strip()
                quality = quality.strip()

                if not header.startswith("@"):
                    self.log(
                        40,
                        f"File {self.filename} contains an invalid header line at line {line_num + 1}: {header}",
                    )

                if not all(c in "ACGTNacgtn-.*" for c in sequence):
                    self.log(
                        40,
                        f"File {self.filename} contains invalid characters in sequence line at line {line_num + 2}: {sequence}",
                    )

                if plus_line != "+":
                    self.log(
                        40,
                        f"File {self.filename} contains an invalid plus line at line {line_num + 3}: {plus_line}",
                    )

                if len(quality) != len(sequence):
                    self.log(
                        40,
                        f"File {self.filename} contains an invalid quality line length at line {line_num + 4}: {quality}",
                    )

                if not all(33 <= ord(c) <= 126 for c in quality):
                    self.log(
                        40,
                        f"File {self.filename} contains invalid characters in quality line at line {line_num + 4}: {quality}",
                    )
                line_num += 4
