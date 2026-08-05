import logging
from pathlib import Path

import pytest

from biovalid.validators import GffValidator

happy_gff_path = Path("tests/data/gff/gff3_happy.gff3")
happy_gff2_path = Path("tests/data/gff/gff3_happy2.gff")
happy_gff3_path = Path("tests/data/gff/gff3_happy3.gff")
invalid_type_gff_path = Path("tests/data/gff/gff3_invalid_type.gff3")


def _assert_validation_error_logged(validator: GffValidator, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR, logger="biovalid"):
        validator.validate()
    assert any(record.levelname == "ERROR" for record in caplog.records)


def test_happy_gff() -> None:
    GffValidator(happy_gff_path).validate()


def test_happy_gff2() -> None:
    GffValidator(happy_gff2_path).validate()


def test_happy_gff3() -> None:
    GffValidator(happy_gff3_path).validate()


def test_invalid_type(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(GffValidator(invalid_type_gff_path), caplog)


def test_missing_gff_version(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    missing_version_gff = tmp_path / "missing_version.gff"
    missing_version_gff.write_text("""##sequence-region chr1 1 100
chr1\ttest\tgene\t1\t100\t.\t+\t.\tID=gene1
""")
    _assert_validation_error_logged(GffValidator(missing_version_gff), caplog)


def test_header_after_data(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    header_after_data_gff = tmp_path / "header_after_data.gff"
    header_after_data_gff.write_text("""##gff-version 3
chr1\ttest\tgene\t1\t100\t.\t+\t.\tID=gene1
##sequence-region chr1 1 100
""")
    _assert_validation_error_logged(GffValidator(header_after_data_gff), caplog)


def test_too_many_columns(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    too_many_columns_gff = tmp_path / "too_many_columns.gff"
    too_many_columns_gff.write_text("""##gff-version 3
chr1\ttest\tgene\t1\t100\t.\t+\t.\tID=gene1\textra_column
""")
    _assert_validation_error_logged(GffValidator(too_many_columns_gff), caplog)


def test_invalid_seqid(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_seqid_gff = tmp_path / "invalid_seqid.gff"
    invalid_seqid_gff.write_text("""##gff-version 3
chr 1 with spaces\ttest\tgene\t1\t100\t.\t+\t.\tID=gene1
""")
    _assert_validation_error_logged(GffValidator(invalid_seqid_gff), caplog)


def test_invalid_start_end(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_coords_gff = tmp_path / "invalid_coords.gff"
    invalid_coords_gff.write_text("""##gff-version 3
chr1\ttest\tgene\tabc\t100\t.\t+\t.\tID=gene1
""")
    _assert_validation_error_logged(GffValidator(invalid_coords_gff), caplog)


def test_start_greater_than_end(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    start_gt_end_gff = tmp_path / "start_gt_end.gff"
    start_gt_end_gff.write_text("""##gff-version 3
chr1\ttest\tgene\t100\t50\t.\t+\t.\tID=gene1
""")
    _assert_validation_error_logged(GffValidator(start_gt_end_gff), caplog)


def test_invalid_score(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_score_gff = tmp_path / "invalid_score.gff"
    invalid_score_gff.write_text("""##gff-version 3
chr1\ttest\tgene\t1\t100\tabc\t+\t.\tID=gene1
""")
    _assert_validation_error_logged(GffValidator(invalid_score_gff), caplog)


def test_invalid_strand(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_strand_gff = tmp_path / "invalid_strand.gff"
    invalid_strand_gff.write_text("""##gff-version 3
chr1\ttest\tgene\t1\t100\t.\tx\t.\tID=gene1
""")
    _assert_validation_error_logged(GffValidator(invalid_strand_gff), caplog)


def test_invalid_cds_phase(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    invalid_phase_gff = tmp_path / "invalid_phase.gff"
    invalid_phase_gff.write_text("""##gff-version 3
chr1\ttest\tCDS\t1\t100\t.\t+\t5\tID=cds1
""")
    _assert_validation_error_logged(GffValidator(invalid_phase_gff), caplog)


def test_few_columns_gets_padded(tmp_path: Path) -> None:
    few_columns_gff = tmp_path / "few_columns.gff"
    few_columns_gff.write_text("##gff-version 3\nchr1\ttest\tgene\t1\t100\t.\t+\t.\n")
    GffValidator(few_columns_gff).validate()


def test_empty_file(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    empty_gff = tmp_path / "empty.gff"
    empty_gff.touch()
    _assert_validation_error_logged(GffValidator(empty_gff), caplog)
