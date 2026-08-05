import logging
from pathlib import Path

import pytest

from biovalid.validators import FastqValidator

happy_fastq_path = Path("tests/data/fastq/happy.fastq")
happy_gz_fastq_path = Path("tests/data/fastq/happy_gz.fastq.gz")
invalid_header_gz_fastq_path = Path("tests/data/fastq/invalid_header_gz.fastq.gz")


def _assert_validation_error_logged(validator: FastqValidator, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR, logger="biovalid"):
        validator.validate()
    assert any(record.levelname == "ERROR" for record in caplog.records)


def test_happy_fastq() -> None:
    validator = FastqValidator(happy_fastq_path)
    validator.validate()


def test_happy_gzip_fastq() -> None:
    validator = FastqValidator(happy_gz_fastq_path)
    validator.validate()


def test_invalid_header_gzip_fastq(caplog: pytest.LogCaptureFixture) -> None:
    validator = FastqValidator(invalid_header_gz_fastq_path)
    _assert_validation_error_logged(validator, caplog)


def test_empty_fastq_file(tmp_path: Path) -> None:
    empty_fastq = tmp_path / "empty.fastq"
    empty_fastq.touch()
    validator = FastqValidator(empty_fastq)
    validator.validate()


def test_incomplete_record(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    incomplete_fastq = tmp_path / "incomplete.fastq"
    incomplete_fastq.write_text("@header1\nACGT\n")
    validator = FastqValidator(incomplete_fastq)
    _assert_validation_error_logged(validator, caplog)


def test_invalid_header(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_header_fastq = tmp_path / "invalid_header.fastq"
    invalid_header_fastq.write_text("header1\nACGT\n+\nIIII\n")
    validator = FastqValidator(invalid_header_fastq)
    _assert_validation_error_logged(validator, caplog)


def test_invalid_sequence_characters(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_seq_fastq = tmp_path / "invalid_seq.fastq"
    invalid_seq_fastq.write_text("@header1\nACGTXYZ\n+\nIIIIIII\n")
    validator = FastqValidator(invalid_seq_fastq)
    _assert_validation_error_logged(validator, caplog)


def test_invalid_plus_line(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_plus_fastq = tmp_path / "invalid_plus.fastq"
    invalid_plus_fastq.write_text("@header1\nACGT\n++\nIIII\n")
    validator = FastqValidator(invalid_plus_fastq)
    _assert_validation_error_logged(validator, caplog)


def test_quality_length_mismatch(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    quality_mismatch_fastq = tmp_path / "quality_mismatch.fastq"
    quality_mismatch_fastq.write_text("@header1\nACGT\n+\nII\n")
    validator = FastqValidator(quality_mismatch_fastq)
    _assert_validation_error_logged(validator, caplog)


def test_invalid_quality_characters(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_qual_fastq = tmp_path / "invalid_qual.fastq"
    invalid_qual_fastq.write_text("@header1\nACGT\n+\nII\x1fI\n")
    validator = FastqValidator(invalid_qual_fastq)
    _assert_validation_error_logged(validator, caplog)
