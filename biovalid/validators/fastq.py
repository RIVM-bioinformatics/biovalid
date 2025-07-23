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
                        f"Incomplete FASTQ record at line {line_num} in {self.filename}",
                    )

                # dont strip at once because it might throw an error if a line is empty (e.g. last line)
                header = header.strip()
                sequence = sequence.strip()
                plus_line = plus_line.strip()
                quality = quality.strip()

                if not header.startswith("@"):
                    self.log(
                        40,
                        f"Invalid header line at line {line_num + 1} in {self.filename}: {header}",
                    )

                if not all(c in "ACGTNacgtn-.*" for c in sequence):
                    self.log(
                        40,
                        f"Invalid characters in sequence line at line {line_num + 2} in {self.filename}: {sequence}",
                    )

                if plus_line != "+":
                    self.log(
                        40,
                        f"Invalid plus line at line {line_num + 3} in {self.filename}: {plus_line}",
                    )

                if len(quality) != len(sequence):
                    self.log(
                        40,
                        f"Quality line length does not match sequence length at line {line_num + 4} in {self.filename}: {quality}",
                    )

                if not all(33 <= ord(c) <= 126 for c in quality):
                    self.log(
                        40,
                        f"Invalid characters in quality line at line {line_num + 4} in {self.filename}: {quality}",
                    )
                line_num += 4
