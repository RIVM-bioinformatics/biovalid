"""Enumerations for file types and compression types used in bioinformatics."""

from enum import Enum
from pathlib import Path


class CompressionType(Enum):
    """Enumeration for different compression types based on file extensions."""

    GZIP = ".gz"
    BZIP2 = ".bz2"
    ZIP = ".zip"
    XZ = ".xz"
    BGZF = ".bgzf"

    @classmethod
    def from_path(cls, path: Path) -> "CompressionType":
        """Determine the compression type based on the file extension."""
        ext = path.suffix.lower()
        for compression_type in cls:
            if ext == compression_type.value:
                return compression_type
        raise ValueError(f"Unknown compression type for extension: {ext}")


class FileType(Enum):
    """Enumeration for different file types used in bioinformatics, based on extensions."""

    FASTA = [".fasta", ".fa", ".fna", ".faa", ".frn"]
    FASTQ = [".fastq", ".fq"]
    GFF = [".gff", ".gff3"]
    BED = [".bed"]
    VCF = [".vcf"]
    SAM = [".sam"]
    BAM = [".bam"]
    BAI = [".bai"]
    BCF = [".bcf"]
    GENBANK = [".gb", ".gbk", ".genbank"]
    PDB = [".pdb"]
    UNKNOWN = ["UNKNOWN"]
    # normally you dont add annotations to enums, but mypy complains otherwise

    @classmethod
    def is_compressed(cls, path: Path) -> bool:
        """Check if the file is compressed based on its extension."""
        ext = path.suffix.lower()
        return any(ext == comp_type.value for comp_type in CompressionType)

    @classmethod
    def from_path(cls, path: Path) -> "FileType":
        """Determine the file type based on the file extension."""
        if cls.is_compressed(path):
            ext = path.suffixes[-2].lower()
        else:
            ext = path.suffix.lower()
        for file_type in cls:
            if ext in file_type.value:
                return file_type
        return FileType.UNKNOWN


class MagicBytes(Enum):
    """
    Enum for the magic bytes of BAM and BGZF files.
    """

    BAM = b"BAM\x01"
    BGZF = b"\x1f\x8b\x08\x04"
    BGZF_EOF = b"\x1f\x8b\x08\x04\x00\x00\x00\x00\x00\xff\x06\x00\x42\x43\x02\x00\x1b\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    BAI = b"BAI\x01"
