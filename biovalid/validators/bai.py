"""
Validator for BAM Index files.
BAM Index files (BAI) are binary files that index the alignment of reads in a BAM file.
The file structure is specified in the SAM/BAM format specification. See https://samtools.github.io/hts-specs/SAMv1.pdf specifically section 5.2
"""

from biovalid.domain.enum import MagicBytes
from biovalid.validators.base import BaseValidator


class BaiValidator(BaseValidator):

    def get_first_bytes(self) -> bytes:
        """
        Reads the first 4 bytes of the file to check for the magic number.
        Returns:
            bytes: The first 4 bytes of the file.
        """
        with self.filename.open("rb") as bai_file:
            return bai_file.read(4)

    def validate(self) -> None:
        """
        Validates a BAI file in the same way as samtools quickcheck.
        This means that it checks the beginning of the file for a valid magic number.
        For now, it does not check the integrity of the BAI file itself.
        """
        file_magic_num = self.get_first_bytes()
        if file_magic_num != MagicBytes.BAI.value:
            self.logger.error("File %s is not a valid BAI file, the magic number is incorrect: %s", self.filename, file_magic_num)
