import logging
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


def test_missing_header(caplog: pytest.LogCaptureFixture) -> None:
    """Test that a FASTA file without a header logs validation errors."""
    validator = FastaValidator(MISSING_HEADER_PATH)
    with caplog.at_level(logging.ERROR, logger="biovalid"):
        validator.validate()
    assert any(record.levelname == "ERROR" for record in caplog.records)


def test_missing_header_gzip_fasta(caplog: pytest.LogCaptureFixture) -> None:
    """Test that an invalid gzipped FASTA file logs validation errors."""
    validator = FastaValidator(MISSING_HEADER_GZ_FASTA_PATH)
    with caplog.at_level(logging.ERROR, logger="biovalid"):
        validator.validate()
    assert any(record.levelname == "ERROR" for record in caplog.records)
