import logging
from pathlib import Path

import pytest

from biovalid.validators import BamValidator

happy_bam_path = Path("tests/data/bam/happy.bam")
uncompressed_bam_path = Path("tests/data/bam/uncompressed.bam")


def _assert_validation_error_logged(validator: BamValidator, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR, logger="biovalid"):
        validator.validate()
    assert any(record.levelname == "ERROR" for record in caplog.records)


def test_happy_bam() -> None:
    validator = BamValidator(happy_bam_path)
    validator.validate()


def test_uncompressed_bam(caplog: pytest.LogCaptureFixture) -> None:
    validator = BamValidator(uncompressed_bam_path)
    _assert_validation_error_logged(validator, caplog)


def test_invalid_magic_number(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_bam = tmp_path / "invalid.bam"
    invalid_bam.write_bytes(b"INVALID_CONTENT_HERE")
    validator = BamValidator(invalid_bam)
    _assert_validation_error_logged(validator, caplog)


def test_empty_file(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    empty_bam = tmp_path / "empty.bam"
    empty_bam.touch()
    validator = BamValidator(empty_bam)
    _assert_validation_error_logged(validator, caplog)
