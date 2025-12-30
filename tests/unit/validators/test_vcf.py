from pathlib import Path

import pytest

from biovalid.validators import VcfValidator

happy_vcf_path = Path("tests/data/vcf/happy.vcf")


def test_happy_vcf() -> None:
    """Test that a valid VCF file passes validation."""
    validator = VcfValidator(happy_vcf_path)
    validator.validate()


def test_empty_vcf_file() -> None:
    """Test that an empty VCF file raises validation error."""
    empty_vcf_path = Path("tests/data/vcf/empty.vcf")
    validator = VcfValidator(empty_vcf_path)

    with pytest.raises(ValueError, match="VCF file is empty"):
        validator.validate()


def test_invalid_first_line() -> None:
    """Test that a file without proper VCF header raises validation error."""
    invalid_vcf_path = Path("tests/data/vcf/invalid_first_line.vcf")
    validator = VcfValidator(invalid_vcf_path)

    with pytest.raises(ValueError, match="File does not start with a valid VCF header line"):
        validator.validate()


def test_missing_required_columns() -> None:
    """Test that VCF with missing required columns raises validation error."""
    missing_cols_path = Path("tests/data/vcf/missing_required_columns.vcf")
    validator = VcfValidator(missing_cols_path)

    with pytest.raises(ValueError, match="VCF column header has fewer than 8 required columns"):
        validator.validate()


def test_wrong_column_headers() -> None:
    """Test that VCF with wrong column headers raises validation error."""
    wrong_headers_path = Path("tests/data/vcf/wrong_column_headers.vcf")
    validator = VcfValidator(wrong_headers_path)

    with pytest.raises(ValueError, match="VCF column header mismatch at position 1: expected 'CHROM', got '#CHR'"):
        validator.validate()


def test_chrom_with_whitespace() -> None:
    """Test that CHROM field with whitespace raises validation error."""
    chrom_whitespace_path = Path("tests/data/vcf/chrom_with_whitespace.vcf")
    validator = VcfValidator(chrom_whitespace_path)

    with pytest.raises(ValueError, match="CHROM contains whitespace characters"):
        validator.validate()


def test_invalid_pos() -> None:
    """Test that non-numeric POS field raises validation error."""
    invalid_pos_path = Path("tests/data/vcf/invalid_pos.vcf")
    validator = VcfValidator(invalid_pos_path)

    with pytest.raises(ValueError, match="POS must be an integer"):
        validator.validate()


def test_id_with_whitespace() -> None:
    """Test that ID field with whitespace raises validation error."""
    id_whitespace_path = Path("tests/data/vcf/id_with_whitespace.vcf")
    validator = VcfValidator(id_whitespace_path)

    with pytest.raises(ValueError, match="ID contains whitespace"):
        validator.validate()


def test_ambiguous_ref() -> None:
    """Test that REF field with invalid DNA bases raises validation warning."""
    ambiguous_ref_path = Path("tests/data/vcf/happy_ambiguous_ref.vcf")
    validator = VcfValidator(ambiguous_ref_path)

    # Feedback indicated that this should be allowed
    validator.validate()


def test_invalid_ref() -> None:
    """Test that REF field with invalid DNA bases raises validation error."""
    invalid_ref_path = Path("tests/data/vcf/invalid_ref.vcf")
    validator = VcfValidator(invalid_ref_path)

    with pytest.raises(ValueError, match="REF contains invalid"):
        validator.validate()


def test_ambiguous_alt() -> None:
    """Test that ALT field with ambiguous DNA bases raises validation warning."""
    ambiguous_alt_path = Path("tests/data/vcf/happy_ambiguous_alt.vcf")
    validator = VcfValidator(ambiguous_alt_path)

    # Feedback indicated that this should be allowed
    validator.validate()


def test_invalid_alt() -> None:
    """Test that ALT field with invalid DNA bases raises validation error."""
    invalid_alt_path = Path("tests/data/vcf/invalid_alt.vcf")
    validator = VcfValidator(invalid_alt_path)

    with pytest.raises(ValueError, match="ALT contains invalid"):
        validator.validate()


def test_invalid_qual() -> None:
    """Test that non-numeric QUAL field raises validation error."""
    invalid_qual_path = Path("tests/data/vcf/invalid_qual.vcf")
    validator = VcfValidator(invalid_qual_path)

    with pytest.raises(ValueError, match="QUAL must be a positive numeric value"):
        validator.validate()


def test_undefined_filter() -> None:
    """Test that undefined FILTER value raises validation error."""
    undefined_filter_path = Path("tests/data/vcf/undefined_filter.vcf")
    validator = VcfValidator(undefined_filter_path)

    with pytest.raises(ValueError, match="FILTER contains unknown filter"):
        validator.validate()


def test_undefined_info() -> None:
    """Test that undefined INFO key raises validation error."""
    undefined_info_path = Path("tests/data/vcf/undefined_info.vcf")
    validator = VcfValidator(undefined_info_path)

    with pytest.raises(ValueError, match="INFO contains unknown key"):
        validator.validate()


def test_undefined_format() -> None:
    """Test that undefined FORMAT key raises validation error."""
    undefined_format_path = Path("tests/data/vcf/undefined_format.vcf")
    validator = VcfValidator(undefined_format_path)

    with pytest.raises(ValueError, match="FORMAT contains unknown key"):
        validator.validate()


def test_mismatched_columns() -> None:
    """Test that data line with wrong number of columns raises validation error."""
    mismatched_cols_path = Path("tests/data/vcf/mismatched_columns.vcf")
    validator = VcfValidator(mismatched_cols_path)

    with pytest.raises(ValueError, match="VCF data line .* does not have the required .* columns"):
        validator.validate()


def test_empty_chrom() -> None:
    """Test that empty CHROM field raises validation error."""
    empty_chrom_path = Path("tests/data/vcf/empty_chrom.vcf")
    validator = VcfValidator(empty_chrom_path)

    with pytest.raises(ValueError, match="VCF data line .* does not have the required .* columns"):
        validator.validate()


def test_empty_pos() -> None:
    """Test that empty POS field raises validation error."""
    empty_pos_path = Path("tests/data/vcf/empty_pos.vcf")
    validator = VcfValidator(empty_pos_path)

    with pytest.raises(ValueError, match="POS column is empty"):
        validator.validate()


def test_empty_ref() -> None:
    """Test that empty REF field raises validation error."""
    empty_ref_path = Path("tests/data/vcf/empty_ref.vcf")
    validator = VcfValidator(empty_ref_path)

    with pytest.raises(ValueError, match="REF column is empty"):
        validator.validate()


def test_no_format_no_samples() -> None:
    """Test that VCF without FORMAT and sample columns validates correctly."""
    no_format_path = Path("tests/data/vcf/happy_no_format_no_samples.vcf")
    validator = VcfValidator(no_format_path)

    # This should pass validation as FORMAT and sample columns are optional
    validator.validate()


def test_empty_alt_allele() -> None:
    """Test that empty ALT allele in comma-separated list raises validation error."""
    empty_alt_path = Path("tests/data/vcf/empty_alt_allele.vcf")
    validator = VcfValidator(empty_alt_path)

    with pytest.raises(ValueError, match="ALT column contains empty alleles"):
        validator.validate()


def test_negative_qual() -> None:
    """Test that negative QUAL values raise validation error (current implementation)."""
    negative_qual_path = Path("tests/data/vcf/negative_qual.vcf")
    validator = VcfValidator(negative_qual_path)

    # Current implementation rejects negative QUAL values
    with pytest.raises(ValueError, match="QUAL must be a positive numeric value"):
        validator.validate()


def test_multiple_filters() -> None:
    """Test that multiple semicolon-separated filters validate correctly."""
    multi_filter_path = Path("tests/data/vcf/happy_multiple_filters.vcf")
    validator = VcfValidator(multi_filter_path)

    # Multiple filters should be valid when all are defined
    validator.validate()


def test_info_flag() -> None:
    """Test that INFO flags (keys without values) validate correctly."""
    info_flag_path = Path("tests/data/vcf/happy_info_flag.vcf")
    validator = VcfValidator(info_flag_path)

    # INFO flags should be valid when defined in header
    validator.validate()


def test_missing_qual_dot() -> None:
    """Test that missing QUAL (dot) validates correctly."""
    missing_qual_path = Path("tests/data/vcf/happy_missing_qual.vcf")
    validator = VcfValidator(missing_qual_path)

    # QUAL can be . for unknown/missing quality
    validator.validate()


def test_missing_id_dot() -> None:
    """Test that missing ID (dot) validates correctly."""
    missing_id_path = Path("tests/data/vcf/happy_missing_id.vcf")
    validator = VcfValidator(missing_id_path)

    # ID can be . for missing identifier
    validator.validate()


def test_missing_ref_dot() -> None:
    """Test that missing REF (dot) validates correctly."""
    missing_ref_path = Path("tests/data/vcf/happy_missing_ref.vcf")
    validator = VcfValidator(missing_ref_path)

    # REF can be . for no reference allele
    validator.validate()


def test_missing_alt_dot() -> None:
    """Test that missing ALT (dot) validates correctly."""
    missing_alt_path = Path("tests/data/vcf/happy_missing_alt.vcf")
    validator = VcfValidator(missing_alt_path)

    # ALT can be . for no alternate allele
    validator.validate()


def test_missing_filter_dot() -> None:
    """Test that missing FILTER (dot) validates correctly."""
    missing_filter_path = Path("tests/data/vcf/happy_missing_filter.vcf")
    validator = VcfValidator(missing_filter_path)

    # FILTER can be . for missing/unknown filter status
    validator.validate()


def test_missing_info_dot() -> None:
    """Test that missing INFO (dot) validates correctly."""
    empty_info_with_fields_path = Path("tests/data/vcf/missing_info.vcf")
    validator = VcfValidator(empty_info_with_fields_path)

    with pytest.raises(ValueError, match="INFO column is '.' but INFO fields are defined in the header"):
        validator.validate()


def test_empty_sample() -> None:
    """Test that missing sample column raises validation error."""
    empty_sample_path = Path("tests/data/vcf/empty_sample_proper.vcf")
    validator = VcfValidator(empty_sample_path)

    with pytest.raises(ValueError, match="VCF data line .* does not have the required .* columns"):
        validator.validate()
