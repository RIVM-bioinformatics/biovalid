from pathlib import Path

import pytest

from biovalid.validators import BamValidator

happy_bam_path = Path("tests/data/bam/happy.bam")
uncompressed_bam_path = Path("tests/data/bam/uncompressed.bam")


def test_happy_bam() -> None:
    """Test that a valid BAM file passes validation."""
    validator = BamValidator(happy_bam_path)
    validator.validate()


def test_uncompressed_bam() -> None:
    """Test that an uncompressed BAM file raises validation error."""
    validator = BamValidator(uncompressed_bam_path)

    with pytest.raises(ValueError, match="is not compressed with BGZF"):
        validator.validate()


def test_invalid_magic_number(tmp_path: Path) -> None:
    """Test that a file with invalid magic number raises validation error."""
    invalid_bam = tmp_path / "invalid.bam"
    # Write some invalid content that's not BGZF compressed
    invalid_bam.write_bytes(b"INVALID_CONTENT_HERE")

    validator = BamValidator(invalid_bam)

    with pytest.raises(ValueError, match="is not compressed with BGZF"):
        validator.validate()


def test_empty_file(tmp_path: Path) -> None:
    """Test that an empty BAM file raises validation error."""
    empty_bam = tmp_path / "empty.bam"
    empty_bam.touch()

    validator = BamValidator(empty_bam)

    with pytest.raises(ValueError, match="is not compressed with BGZF"):
        validator.validate()
