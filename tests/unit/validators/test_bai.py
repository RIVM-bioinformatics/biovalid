import logging
from pathlib import Path

import pytest

from biovalid.validators import BaiValidator

happy_bai_path = Path("tests/data/bai/happy.bam.bai")
wrong_magic_bai_path = Path("tests/data/bai/wrong_magic_num.bai")


def _assert_validation_error_logged(validator: BaiValidator, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR, logger="biovalid"):
        validator.validate()
    assert any(record.levelname == "ERROR" for record in caplog.records)


def test_happy_bai() -> None:
    validator = BaiValidator(happy_bai_path)
    validator.validate()


def test_wrong_magic_number(caplog: pytest.LogCaptureFixture) -> None:
    validator = BaiValidator(wrong_magic_bai_path)
    _assert_validation_error_logged(validator, caplog)


def test_empty_file(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    empty_bai = tmp_path / "empty.bai"
    empty_bai.touch()
    validator = BaiValidator(empty_bai)
    _assert_validation_error_logged(validator, caplog)


def test_invalid_file_content(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_bai = tmp_path / "invalid.bai"
    invalid_bai.write_text("This is not a valid BAI file")
    validator = BaiValidator(invalid_bai)
    _assert_validation_error_logged(validator, caplog)
