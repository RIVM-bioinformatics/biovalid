from pathlib import Path

import pytest

from biovalid.validators import BaiValidator

happy_bai_path = Path("tests/data/bai/happy.bam.bai")
wrong_magic_bai_path = Path("tests/data/bai/wrong_magic_num.bai")


def test_happy_bai() -> None:
    """Test that a valid BAI file passes validation."""
    validator = BaiValidator(happy_bai_path)
    validator.validate()


def test_wrong_magic_number() -> None:
    """Test that a BAI file with wrong magic number raises validation error."""
    validator = BaiValidator(wrong_magic_bai_path)

    with pytest.raises(ValueError, match="is not a valid BAI file, the magic number is incorrect"):
        validator.validate()


def test_empty_file(tmp_path: Path) -> None:
    """Test that an empty BAI file raises validation error."""
    empty_bai = tmp_path / "empty.bai"
    empty_bai.touch()

    validator = BaiValidator(empty_bai)

    with pytest.raises(ValueError, match="is not a valid BAI file, the magic number is incorrect"):
        validator.validate()


def test_invalid_file_content(tmp_path: Path) -> None:
    """Test that invalid file content raises validation error."""
    invalid_bai = tmp_path / "invalid.bai"
    invalid_bai.write_text("This is not a valid BAI file")

    validator = BaiValidator(invalid_bai)

    with pytest.raises(ValueError, match="is not a valid BAI file, the magic number is incorrect"):
        validator.validate()
