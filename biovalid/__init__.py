"""Biovalid: Lightweight bioinformatics file validation library.

Biovalid provides format validation for common bioinformatics file types
including FASTA, FASTQ, BAM, BAI, GFF, and VCF files. It features a
plugin-style validator architecture with no external dependencies.

Basic usage:
    >>> from biovalid import BioValidator
    >>> validator = BioValidator("data.fasta")
    >>> validator.validate_files()

    # For programmatic use with boolean return
    >>> validator = BioValidator("data.fasta", bool_mode=True)
    >>> is_valid = validator.validate_files()

Supported file types:
    - FASTA/FASTQ (including compressed .gz variants)
    - BAM/BAI (binary alignment formats)
    - GFF (with Sequence Ontology validation)
    - VCF (variant call format)
"""

from biovalid.biovalidator import BioValidator
from biovalid.version import __version__

__all__ = ["BioValidator", "__version__"]
