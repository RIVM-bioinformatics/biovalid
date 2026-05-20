"""
Validation function for BAM files.
See: https://samtools.github.io/hts-specs/SAMv1.pdf for the BAM file format specification.
This function checks if the BAM file has a valid header and an intact EOF marker.
It does not check the integrity of the BAM file itself.
It is similar to the `samtools quickcheck` command.
"""

import gzip
import struct
from pathlib import Path

from biovalid.domain.enum import MagicBytes
from biovalid.validators.base import BaseValidator


class BamValidator(BaseValidator):
    """Validator for BAM files.
    Validates the BAM file by checking the magic number and EOF marker.
    Similar to `samtools quickcheck`.
    """

    def _first_and_last_uncompressed_bgzf_bytes(self, filename: Path) -> tuple[bytes, bytes]:
        """
        Returns the first four uncompressed bytes of a BGZF compressed file.
        This is used to check the magic number of a BAM file after decompressing the BGZF block.
        """
        with open(filename, "rb") as f:
            header = f.read(18)
            block_size = struct.unpack("<H", header[16:18])[0] + 1
            f.seek(0)
            block = f.read(block_size)
            magic_num = gzip.decompress(block)[:4]
            f.seek(-28, 2)  # 2 means from end of file
            eof_marker = f.read(28)
        return magic_num, eof_marker

    def validate(self) -> None:
        """
        Validates a BAM file in the same way as samtools quickcheck.
        This means that it checks the beginning of the file for a valid BGZF compression and BAM header,
        then checks if the EOF marker is present and intact.
        For now, it does not check the integrity of the BAM file itself.
        """
        with self.filename.open("rb") as bam_file:
            file_magic_num = bam_file.read(4)
        is_compressed = file_magic_num == MagicBytes.BGZF.value
        if not is_compressed:
            self.logger.error("File %s is not compressed with BGZF, it may still be a valid BAM file, but it is probably truncated.", self.filename)

        # gzip.decompress needs the entire BGZF block,
        # but we only know if it is compressed after reading the first 4 bytes
        # so we have to open it twice if we want to accept non-compressed BAM files
        magic_num, eof_marker = self._first_and_last_uncompressed_bgzf_bytes(self.filename)
        if magic_num != MagicBytes.BAM.value:
            self.logger.error("File %s is not a valid BAM file, the magic number is incorrect: %s", self.filename, magic_num)
        if eof_marker != MagicBytes.BGZF_EOF.value:
            self.logger.error("File %s is not a valid BAM file, the EOF marker is incorrect: %s", self.filename, eof_marker)
