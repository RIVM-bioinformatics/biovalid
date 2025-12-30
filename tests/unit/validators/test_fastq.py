from pathlib import Path

import pytest

from biovalid.validators import FastqValidator

happy_fastq_path = Path("tests/data/fastq/happy.fastq")


def test_happy_fastq() -> None:
    """Test that a valid FASTQ file passes validation."""
    validator = FastqValidator(happy_fastq_path)
    validator.validate()


def test_empty_fastq_file(tmp_path: Path) -> None:
    """Test that an empty FASTQ file passes validation (empty files are valid)."""
    empty_fastq = tmp_path / "empty.fastq"
    empty_fastq.touch()

    validator = FastqValidator(empty_fastq)
    validator.validate()


def test_incomplete_record(tmp_path: Path) -> None:
    """Test that an incomplete FASTQ record raises validation error."""
    incomplete_fastq = tmp_path / "incomplete.fastq"
    incomplete_fastq.write_text("@header1\nACGT\n")

    validator = FastqValidator(incomplete_fastq)

    with pytest.raises(ValueError, match="contains an incomplete FASTQ record"):
        validator.validate()


def test_invalid_header(tmp_path: Path) -> None:
    """Test that a FASTQ record without @ header raises validation error."""
    invalid_header_fastq = tmp_path / "invalid_header.fastq"
    invalid_header_fastq.write_text("header1\nACGT\n+\nIIII\n")

    validator = FastqValidator(invalid_header_fastq)

    with pytest.raises(ValueError, match="contains an invalid header line"):
        validator.validate()


def test_invalid_sequence_characters(tmp_path: Path) -> None:
    """Test that invalid characters in sequence raise validation error."""
    invalid_seq_fastq = tmp_path / "invalid_seq.fastq"
    invalid_seq_fastq.write_text("@header1\nACGTXYZ\n+\nIIIIIII\n")

    validator = FastqValidator(invalid_seq_fastq)

    with pytest.raises(ValueError, match="contains invalid characters in sequence line"):
        validator.validate()


def test_invalid_plus_line(tmp_path: Path) -> None:
    """Test that invalid plus line raises validation error."""
    invalid_plus_fastq = tmp_path / "invalid_plus.fastq"
    invalid_plus_fastq.write_text("@header1\nACGT\n++\nIIII\n")

    validator = FastqValidator(invalid_plus_fastq)

    with pytest.raises(ValueError, match="contains an invalid plus line"):
        validator.validate()


def test_quality_length_mismatch(tmp_path: Path) -> None:
    """Test that quality line length mismatch raises validation error."""
    quality_mismatch_fastq = tmp_path / "quality_mismatch.fastq"
    quality_mismatch_fastq.write_text("@header1\nACGT\n+\nII\n")

    validator = FastqValidator(quality_mismatch_fastq)

    with pytest.raises(ValueError, match="contains an invalid quality line length"):
        validator.validate()


def test_invalid_quality_characters(tmp_path: Path) -> None:
    """Test that invalid characters in quality line raise validation error."""
    invalid_qual_fastq = tmp_path / "invalid_qual.fastq"
    # Using character with ASCII value < 33 or > 126
    invalid_qual_fastq.write_text("@header1\nACGT\n+\nII\x1fI\n")

    validator = FastqValidator(invalid_qual_fastq)

    with pytest.raises(ValueError, match="contains invalid characters in quality line"):
        validator.validate()
