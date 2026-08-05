import gzip
from pathlib import Path

import pytest

from biovalid.biovalidator import BioValidator


def test_gzip_vcf_is_rejected(tmp_path: Path) -> None:
    """Gzip compression is currently only supported for FASTA and FASTQ files."""
    source_vcf = Path("tests/data/vcf/happy.vcf")
    gzip_vcf = tmp_path / "happy.vcf.gz"

    with source_vcf.open("rb") as src, gzip.open(gzip_vcf, "wb") as dst:
        dst.write(src.read())

    validator = BioValidator()
    assert validator.validate_files(gzip_vcf) is False


def test_invalid_file_returns_false_by_default() -> None:
    """Validation should report failure without raising for bad content."""
    validator = BioValidator()
    assert validator.validate_files("tests/data/fasta/missing_header.fasta") is False


def test_invalid_file_raises_when_raise_errors_enabled() -> None:
    """Validation should raise when raise_errors is enabled."""
    validator = BioValidator(raise_errors=True)
    with pytest.raises(RuntimeError, match="Validation unsuccessful"):
        validator.validate_files("tests/data/fasta/missing_header.fasta")
