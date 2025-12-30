from pathlib import Path

import pytest

from biovalid.validators import GffValidator

happy_gff_path = Path("tests/data/gff/gff3_happy.gff3")
happy_gff2_path = Path("tests/data/gff/gff3_happy2.gff")
happy_gff3_path = Path("tests/data/gff/gff3_happy3.gff")
invalid_type_gff_path = Path("tests/data/gff/gff3_invalid_type.gff3")


def test_happy_gff() -> None:
    """Test that a valid GFF3 file passes validation."""
    validator = GffValidator(happy_gff_path)
    validator.validate()


def test_happy_gff2() -> None:
    """Test that another valid GFF file passes validation."""
    validator = GffValidator(happy_gff2_path)
    validator.validate()


def test_happy_gff3() -> None:
    """Test that another valid GFF file passes validation."""
    validator = GffValidator(happy_gff3_path)
    validator.validate()


def test_invalid_type() -> None:
    """Test that a GFF file with invalid type raises validation error."""
    validator = GffValidator(invalid_type_gff_path)

    with pytest.raises(ValueError, match="contains an invalid type"):
        validator.validate()


def test_missing_gff_version(tmp_path: Path) -> None:
    """Test that a GFF file without version declaration raises validation error."""
    missing_version_gff = tmp_path / "missing_version.gff"
    missing_version_gff.write_text(
        """##sequence-region chr1 1 100
chr1	test	gene	1	100	.	+	.	ID=gene1
"""
    )

    validator = GffValidator(missing_version_gff)

    with pytest.raises(ValueError, match="Missing required GFF version declaration"):
        validator.validate()


def test_header_after_data(tmp_path: Path) -> None:
    """Test that header lines after data lines raise validation error."""
    header_after_data_gff = tmp_path / "header_after_data.gff"
    header_after_data_gff.write_text(
        """##gff-version 3
chr1	test	gene	1	100	.	+	.	ID=gene1
##sequence-region chr1 1 100
"""
    )

    validator = GffValidator(header_after_data_gff)

    with pytest.raises(ValueError, match="Header line found after data has started"):
        validator.validate()


def test_too_many_columns(tmp_path: Path) -> None:
    """Test that a GFF line with too many columns raises validation error."""
    too_many_columns_gff = tmp_path / "too_many_columns.gff"
    too_many_columns_gff.write_text(
        """##gff-version 3
chr1	test	gene	1	100	.	+	.	ID=gene1	extra_column
"""
    )

    validator = GffValidator(too_many_columns_gff)

    with pytest.raises(ValueError, match="contains an invalid number of columns"):
        validator.validate()


def test_invalid_seqid(tmp_path: Path) -> None:
    """Test that invalid seqid raises validation error."""
    invalid_seqid_gff = tmp_path / "invalid_seqid.gff"
    invalid_seqid_gff.write_text(
        """##gff-version 3
chr 1 with spaces	test	gene	1	100	.	+	.	ID=gene1
"""
    )

    validator = GffValidator(invalid_seqid_gff)

    with pytest.raises(ValueError, match="contains an invalid seqid"):
        validator.validate()


def test_invalid_start_end(tmp_path: Path) -> None:
    """Test that invalid start/end coordinates raise validation error."""
    invalid_coords_gff = tmp_path / "invalid_coords.gff"
    invalid_coords_gff.write_text(
        """##gff-version 3
chr1	test	gene	abc	100	.	+	.	ID=gene1
"""
    )

    validator = GffValidator(invalid_coords_gff)

    with pytest.raises(ValueError, match="contains an invalid start"):
        validator.validate()


def test_start_greater_than_end(tmp_path: Path) -> None:
    """Test that start > end raises validation error."""
    start_gt_end_gff = tmp_path / "start_gt_end.gff"
    start_gt_end_gff.write_text(
        """##gff-version 3
chr1	test	gene	100	50	.	+	.	ID=gene1
"""
    )

    validator = GffValidator(start_gt_end_gff)

    with pytest.raises(ValueError, match="contains an invalid start-end range"):
        validator.validate()


def test_invalid_score(tmp_path: Path) -> None:
    """Test that invalid score raises validation error."""
    invalid_score_gff = tmp_path / "invalid_score.gff"
    invalid_score_gff.write_text(
        """##gff-version 3
chr1	test	gene	1	100	abc	+	.	ID=gene1
"""
    )

    validator = GffValidator(invalid_score_gff)

    with pytest.raises(ValueError, match="contains an invalid score"):
        validator.validate()


def test_invalid_strand(tmp_path: Path) -> None:
    """Test that invalid strand raises validation error."""
    invalid_strand_gff = tmp_path / "invalid_strand.gff"
    invalid_strand_gff.write_text(
        """##gff-version 3
chr1	test	gene	1	100	.	x	.	ID=gene1
"""
    )

    validator = GffValidator(invalid_strand_gff)

    with pytest.raises(ValueError, match="contains an invalid strand"):
        validator.validate()


def test_invalid_cds_phase(tmp_path: Path) -> None:
    """Test that invalid phase for CDS raises validation error."""
    invalid_phase_gff = tmp_path / "invalid_phase.gff"
    invalid_phase_gff.write_text(
        """##gff-version 3
chr1	test	CDS	1	100	.	+	5	ID=cds1
"""
    )

    validator = GffValidator(invalid_phase_gff)

    with pytest.raises(ValueError, match="contains an invalid phase for CDS"):
        validator.validate()


def test_few_columns_gets_padded(tmp_path: Path) -> None:
    """Test that a GFF line with fewer than 9 columns gets padded with placeholders."""
    few_columns_gff = tmp_path / "few_columns.gff"
    # Create line with only 8 columns (missing attributes column)
    few_columns_gff.write_text("##gff-version 3\nchr1\ttest\tgene\t1\t100\t.\t+\t.\n")

    validator = GffValidator(few_columns_gff)
    # This should pass with a warning, as the validator pads with "."
    validator.validate()


def test_empty_file(tmp_path: Path) -> None:
    """Test that an empty GFF file raises validation error due to missing version."""
    empty_gff = tmp_path / "empty.gff"
    empty_gff.touch()

    validator = GffValidator(empty_gff)

    with pytest.raises(ValueError, match="Missing required GFF version declaration"):
        validator.validate()
