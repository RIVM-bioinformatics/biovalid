import gzip
from pathlib import Path

from biovalid.biovalidator import BioValidator


def test_gzip_vcf_is_rejected(tmp_path: Path) -> None:
    """Gzip compression is currently only supported for FASTA and FASTQ files."""
    source_vcf = Path("tests/data/vcf/happy.vcf")
    gzip_vcf = tmp_path / "happy.vcf.gz"

    with source_vcf.open("rb") as src, gzip.open(gzip_vcf, "wb") as dst:
        dst.write(src.read())

    validator = BioValidator(bool_mode=True)
    assert validator.validate_files(gzip_vcf) is False
