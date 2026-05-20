from pathlib import Path

import pytest

from biovalid.validators import FastaValidator

MISSING_HEADER_PATH = Path("tests/data/fasta/missing_header.fasta")


def test_missing_header() -> None:
    """Test that a FASTA file without a header raises a RuntimeError."""
    with pytest.raises(RuntimeError):
        FastaValidator(MISSING_HEADER_PATH).validate()
