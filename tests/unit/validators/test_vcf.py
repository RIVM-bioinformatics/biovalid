import logging
from pathlib import Path

import pytest

from biovalid.validators import VcfValidator

happy_vcf_path = Path("tests/data/vcf/happy.vcf")


def _assert_validation_error_logged(validator: VcfValidator, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR, logger="biovalid"):
        validator.validate()
    assert any(record.levelname == "ERROR" for record in caplog.records)


def test_happy_vcf() -> None:
    VcfValidator(happy_vcf_path).validate()


def test_empty_vcf_file(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/empty.vcf")), caplog)


def test_invalid_first_line(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/invalid_first_line.vcf")), caplog)


def test_missing_required_columns(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/missing_required_columns.vcf")), caplog)


def test_wrong_column_headers(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/wrong_column_headers.vcf")), caplog)


def test_chrom_with_whitespace(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/chrom_with_whitespace.vcf")), caplog)


def test_invalid_pos(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/invalid_pos.vcf")), caplog)


def test_id_with_whitespace(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/id_with_whitespace.vcf")), caplog)


def test_ambiguous_ref() -> None:
    VcfValidator(Path("tests/data/vcf/happy_ambiguous_ref.vcf")).validate()


def test_invalid_ref(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/invalid_ref.vcf")), caplog)


def test_ambiguous_alt() -> None:
    VcfValidator(Path("tests/data/vcf/happy_ambiguous_alt.vcf")).validate()


def test_invalid_alt(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/invalid_alt.vcf")), caplog)


def test_invalid_qual(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/invalid_qual.vcf")), caplog)


def test_undefined_filter(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/undefined_filter.vcf")), caplog)


def test_undefined_info(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/undefined_info.vcf")), caplog)


def test_undefined_format(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/undefined_format.vcf")), caplog)


def test_mismatched_columns(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/mismatched_columns.vcf")), caplog)


def test_empty_chrom(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/empty_chrom.vcf")), caplog)


def test_empty_pos(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/empty_pos.vcf")), caplog)


def test_empty_ref(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/empty_ref.vcf")), caplog)


def test_no_format_no_samples() -> None:
    VcfValidator(Path("tests/data/vcf/happy_no_format_no_samples.vcf")).validate()


def test_empty_alt_allele(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/empty_alt_allele.vcf")), caplog)


def test_negative_qual(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/negative_qual.vcf")), caplog)


def test_multiple_filters() -> None:
    VcfValidator(Path("tests/data/vcf/happy_multiple_filters.vcf")).validate()


def test_info_flag() -> None:
    VcfValidator(Path("tests/data/vcf/happy_info_flag.vcf")).validate()


def test_missing_qual_dot() -> None:
    VcfValidator(Path("tests/data/vcf/happy_missing_qual.vcf")).validate()


def test_missing_id_dot() -> None:
    VcfValidator(Path("tests/data/vcf/happy_missing_id.vcf")).validate()


def test_missing_ref_dot() -> None:
    VcfValidator(Path("tests/data/vcf/happy_missing_ref.vcf")).validate()


def test_missing_alt_dot() -> None:
    VcfValidator(Path("tests/data/vcf/happy_missing_alt.vcf")).validate()


def test_missing_filter_dot() -> None:
    VcfValidator(Path("tests/data/vcf/happy_missing_filter.vcf")).validate()


def test_missing_info_dot(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/missing_info.vcf")), caplog)


def test_empty_sample(caplog: pytest.LogCaptureFixture) -> None:
    _assert_validation_error_logged(VcfValidator(Path("tests/data/vcf/empty_sample_proper.vcf")), caplog)
