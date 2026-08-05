from pathlib import Path

import pytest

from biovalid.validators import FastaValidator

MISSING_HEADER_PATH = Path("tests/data/fasta/missing_header.fasta")
HAPPY_GZ_FASTA_PATH = Path("tests/data/fasta/happy_gz.fasta.gz")
MISSING_HEADER_GZ_FASTA_PATH = Path("tests/data/fasta/missing_header_gz.fasta.gz")


def test_happy_gzip_fasta() -> None:
    """Test that a valid gzipped FASTA file passes validation."""
    validator = FastaValidator(HAPPY_GZ_FASTA_PATH)
    validator.validate()


def test_missing_header() -> None:
    """Test that a FASTA file without a header raises a RuntimeError."""
    validator = FastaValidator(MISSING_HEADER_PATH)
    with pytest.raises(RuntimeError):
        validator.validate()


def test_missing_header_gzip_fasta() -> None:
    """Test that an invalid gzipped FASTA file raises a RuntimeError."""
    validator = FastaValidator(MISSING_HEADER_GZ_FASTA_PATH)
    with pytest.raises(RuntimeError):
        validator.validate()
