"""
Validator for BAM Index files.
BAM Index files (BAI) are binary files that index the alignment of reads in a BAM file.
The file structure is specified in the SAM/BAM format specification. See https://samtools.github.io/hts-specs/SAMv1.pdf specifically section 5.2
"""

from biovalid.enum import MagicBytes
from biovalid.validators.base import BaseValidator


class BaiValidator(BaseValidator):
    def validate(self) -> None:
        """
        Validates a BAM file in the same way as samtools quickcheck.
        This means that it checks the beginning of the file for a valid BGZF compression and BAM header,
        then checks if the EOF marker is present and intact.
        For now, it does not check the integrity of the BAM file itself.
        """
        with self.filename.open("rb") as bam_file:
            file_magic_num = bam_file.read(4)
        if file_magic_num != MagicBytes.BAI.value:
            self.log(
                40,
                f"File {self.filename} is not a valid BAI file, " f"the magic number is incorrect: {file_magic_num!r}",
            )
