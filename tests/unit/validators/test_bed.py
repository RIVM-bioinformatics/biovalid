"""
BED validator tests.

Constraints cited below refer to the hts-specs BED specification:
https://samtools.github.io/hts-specs/BEDv1.pdf
and the UCSC FAQ:
https://genome.ucsc.edu/FAQ/FAQformat.html#format1
"""

from pathlib import Path

import pytest

from biovalid.validators import BedValidator

happy_bed_path = Path("tests/data/bed/happy_track_headers.bed")


def test_happy_bed() -> None:
    BedValidator(happy_bed_path).validate()


def test_empty_bed_file(tmp_path: Path) -> None:
    bed = tmp_path / "empty.bed"
    bed.touch()
    BedValidator(bed).validate()


def test_bed3_minimal(tmp_path: Path) -> None:
    bed = tmp_path / "bed3.bed"
    bed.write_text("chr1\t100\t200\nchr1\t300\t400\n")
    BedValidator(bed).validate()


def test_zero_length_feature_allowed(tmp_path: Path) -> None:
    # hts-specs §1.6: chromStart == chromEnd denotes a feature between chromStart
    # and the preceding base (e.g. an insertion).
    bed = tmp_path / "zerolen.bed"
    bed.write_text("chr1\t100\t100\n")
    BedValidator(bed).validate()


def test_too_few_columns(tmp_path: Path) -> None:
    # hts-specs §1.5: BED requires at least 3 columns (chrom, chromStart, chromEnd).
    bed = tmp_path / "bad.bed"
    bed.write_text("chr1\t100\n")
    with pytest.raises(RuntimeError, match="BED requires at least 3"):
        BedValidator(bed).validate()


def test_bed9_plus_custom_fields_accepted(tmp_path: Path) -> None:
    # hts-specs §1.5: BED N+M files where N is in {3-9, 12} and M is the number of
    # custom trailing fields are valid. A 10- or 11-column file is BED9+1 / BED9+2.
    bed = tmp_path / "bed9_plus_1.bed"
    bed.write_text("chr1\t100\t200\tname\t500\t+\t100\t200\t0,0,0\tcustomA\n")
    BedValidator(bed).validate()


def test_bed12_plus_custom_fields_accepted(tmp_path: Path) -> None:
    bed = tmp_path / "bed12_plus_2.bed"
    bed.write_text("chr1\t100\t200\tname\t500\t+\t100\t200\t0,0,0\t1\t100\t0\tcustomA\tcustomB\n")
    BedValidator(bed).validate()


def test_mismatched_column_counts(tmp_path: Path) -> None:
    # hts-specs §1.5: each data line must have the same number of fields.
    bed = tmp_path / "mismatch.bed"
    bed.write_text("chr1\t100\t200\nchr1\t300\t400\tname\n")
    with pytest.raises(RuntimeError, match="column count must be uniform"):
        BedValidator(bed).validate()


def test_chrom_end_before_start(tmp_path: Path) -> None:
    bed = tmp_path / "reversed.bed"
    bed.write_text("chr1\t200\t100\n")
    with pytest.raises(RuntimeError, match="chromEnd .* < chromStart"):
        BedValidator(bed).validate()


def test_non_integer_coord(tmp_path: Path) -> None:
    bed = tmp_path / "bad_coord.bed"
    bed.write_text("chr1\t100\tabc\n")
    with pytest.raises(RuntimeError, match="non-integer chromEnd"):
        BedValidator(bed).validate()


def test_negative_coord_rejected(tmp_path: Path) -> None:
    bed = tmp_path / "neg.bed"
    bed.write_text("chr1\t-1\t100\n")
    with pytest.raises(RuntimeError, match="negative chromStart"):
        BedValidator(bed).validate()


@pytest.mark.parametrize(
    "chrom",
    [
        pytest.param("chr 1", id="space"),
        pytest.param("chr-1", id="hyphen"),
        pytest.param("chr.1", id="dot"),
        pytest.param("a" * 256, id="length_over_255"),
        pytest.param("", id="empty"),
    ],
)
def test_chrom_rejects_non_word_or_too_long(tmp_path: Path, chrom: str) -> None:
    # hts-specs §1.6 Table 2: chrom matches [[:alnum:]_]{1,255}.
    # UCSC is silent on chrom character class; this is a --spec hts-only rule.
    bed = tmp_path / "chrom.bed"
    bed.write_text(f"{chrom}\t100\t200\n")
    with pytest.raises(RuntimeError, match="does not match the hts-specs character class"):
        BedValidator(bed, spec="hts").validate()


def test_chrom_with_refseq_accession_passes_in_ucsc_mode(tmp_path: Path) -> None:
    # RefSeq accessions like NC_000001.11 or MN908947.3 are spec-valid per UCSC
    # (silent on char class) but reject under hts-specs Table 2.
    bed = tmp_path / "refseq.bed"
    bed.write_text("NC_000001.11\t100\t200\n")
    BedValidator(bed).validate()  # default --spec ucsc


def test_name_too_long(tmp_path: Path) -> None:
    # hts-specs §1.7: name is 1 to 255 non-tab characters.
    bed = tmp_path / "name.bed"
    bed.write_text(f"chr1\t100\t200\t{'x' * 256}\n")
    with pytest.raises(RuntimeError, match="invalid name field length"):
        BedValidator(bed).validate()


def test_blank_lines_ignored(tmp_path: Path) -> None:
    # hts-specs §1.4.2: blank lines (entirely horizontal whitespace) are valid anywhere.
    bed = tmp_path / "blanks.bed"
    bed.write_text("chr1\t100\t200\n\n   \t  \nchr1\t300\t400\n")
    BedValidator(bed).validate()


def test_score_out_of_range_hts_only(tmp_path: Path) -> None:
    # Score range 0-1000 is per hts-specs §1.7; UCSC is silent on integer-ness and
    # treats the range as descriptive. Real-world peak callers emit out-of-range scores.
    bed = tmp_path / "score.bed"
    bed.write_text("chr1\t100\t200\tname\t1001\n")
    with pytest.raises(RuntimeError, match="outside the spec range 0-1000"):
        BedValidator(bed, spec="hts").validate()


def test_score_out_of_range_passes_in_ucsc_mode(tmp_path: Path) -> None:
    bed = tmp_path / "score.bed"
    bed.write_text("chr1\t100\t200\tname\t1500\n")
    BedValidator(bed).validate()  # default --spec ucsc


@pytest.mark.parametrize("strand", ["+", "-", "."])
def test_valid_strands(tmp_path: Path, strand: str) -> None:
    bed = tmp_path / "strand.bed"
    bed.write_text(f"chr1\t100\t200\tname\t0\t{strand}\n")
    BedValidator(bed).validate()


def test_invalid_strand(tmp_path: Path) -> None:
    bed = tmp_path / "strand.bed"
    bed.write_text("chr1\t100\t200\tname\t0\t*\n")
    with pytest.raises(RuntimeError, match="invalid strand"):
        BedValidator(bed).validate()


def test_thick_outside_chrom_range(tmp_path: Path) -> None:
    # hts-specs §1.8: thickStart must be between chromStart and chromEnd inclusive.
    bed = tmp_path / "thick.bed"
    bed.write_text("chr1\t100\t200\tname\t0\t+\t50\t150\n")
    with pytest.raises(RuntimeError, match="thick range"):
        BedValidator(bed).validate()


def test_item_rgb_zero_shorthand(tmp_path: Path) -> None:
    # hts-specs §1.8: a single 0 is a special-cased shorthand for itemRgb.
    bed = tmp_path / "rgb0.bed"
    bed.write_text("chr1\t100\t200\tname\t0\t+\t100\t200\t0\n")
    BedValidator(bed).validate()


@pytest.mark.parametrize(
    "rgb",
    [
        pytest.param("255,0,300", id="component_over_255"),
        pytest.param("256,0,0", id="first_component_overflow"),
        pytest.param("255,0", id="only_two_components"),
        pytest.param("1", id="non_zero_single_value"),
    ],
)
def test_item_rgb_invalid(tmp_path: Path, rgb: str) -> None:
    bed = tmp_path / "rgb.bed"
    bed.write_text(f"chr1\t100\t200\tname\t0\t+\t100\t200\t{rgb}\n")
    with pytest.raises(RuntimeError, match="invalid itemRgb"):
        BedValidator(bed).validate()


def test_space_separated_file_rejected(tmp_path: Path) -> None:
    # Deviation from hts-specs §1.3 (which allows [ \t]+): validator requires tab.
    # Locking this in so it fails loudly rather than silently misparsing.
    bed = tmp_path / "spaces.bed"
    bed.write_text("chr1 100 200\n")
    with pytest.raises(RuntimeError, match="BED requires at least 3"):
        BedValidator(bed).validate()


def test_chrom_named_track_not_skipped(tmp_path: Path) -> None:
    # browser/track header detection must respect a whitespace boundary, otherwise
    # a chrom literally named "track1" silently disappears as a header line.
    bed = tmp_path / "track_chrom.bed"
    bed.write_text("track1\t100\t200\n")
    BedValidator(bed).validate()


def test_block_count_mismatch(tmp_path: Path) -> None:
    bed = tmp_path / "blocks.bed"
    bed.write_text("chr1\t0\t100\tname\t0\t+\t0\t100\t0\t2\t50,\t0,\n")
    with pytest.raises(RuntimeError, match="blockSizes has 1 entries"):
        BedValidator(bed).validate()


def test_first_block_start_must_be_zero(tmp_path: Path) -> None:
    # hts-specs §1.9: the first block must start at chromStart, so blockStarts[0] == 0.
    bed = tmp_path / "blocks.bed"
    bed.write_text("chr1\t0\t100\tname\t0\t+\t0\t100\t0\t1\t100,\t10,\n")
    with pytest.raises(RuntimeError, match="first blockStart must be 0"):
        BedValidator(bed).validate()


def test_last_block_must_reach_chrom_end(tmp_path: Path) -> None:
    # hts-specs §1.9: the last block must end at chromEnd.
    bed = tmp_path / "blocks.bed"
    bed.write_text("chr1\t0\t100\tname\t0\t+\t0\t100\t0\t1\t50,\t0,\n")
    with pytest.raises(RuntimeError, match="must equal chromEnd - chromStart"):
        BedValidator(bed).validate()


def test_blocks_overlap(tmp_path: Path) -> None:
    # hts-specs §1.9: blocks must not overlap and must be sorted ascending.
    bed = tmp_path / "blocks.bed"
    bed.write_text("chr1\t0\t100\tname\t0\t+\t0\t100\t0\t2\t60,50\t0,50\n")
    with pytest.raises(RuntimeError, match="overlapping previous block"):
        BedValidator(bed).validate()


@pytest.mark.parametrize(
    "block_field, sizes, starts",
    [
        pytest.param("blockSizes", "60,,40", "0,60", id="double_comma"),
        pytest.param("blockSizes", ",60,40", "0,60", id="leading_comma"),
    ],
)
def test_malformed_block_list(tmp_path: Path, block_field: str, sizes: str, starts: str) -> None:
    # hts-specs §1.9 Table 2: blockSizes/blockStarts match ([[:digit:]]+,){n-1}[[:digit:]]+,?
    bed = tmp_path / "blocks.bed"
    bed.write_text(f"chr1\t0\t100\tname\t0\t+\t0\t100\t0\t2\t{sizes}\t{starts}\n")
    with pytest.raises(RuntimeError, match=f"malformed {block_field}"):
        BedValidator(bed).validate()


def test_comment_and_track_lines_skipped(tmp_path: Path) -> None:
    # browser/track lines: tolerated per UCSC convention.
    # hts-specs §5 treats them as making the file a track file, not a BED file.
    bed = tmp_path / "headers.bed"
    bed.write_text(
        "browser position chr1:1-1000\n"
        'track name="x" description="y"\n'
        "# a comment\n"
        "chr1\t100\t200\n"
    )
    BedValidator(bed).validate()


# --bed tier explicit-N mode tests

def test_bed6_narrowpeak_shape_passes_with_explicit_bed6(tmp_path: Path) -> None:
    # narrowPeak (BED6+4) has float signalValue at col 7 that would fail greedy
    # BED9+1 parse as thickStart. Explicit --bed 6 treats cols 7-10 as opaque custom.
    bed = tmp_path / "narrowpeak.bed"
    bed.write_text("chr1\t100\t200\tpeak1\t500\t+\t5.30862\t12.749\t8.65\t67\n")
    BedValidator(bed, bed_tier="6").validate()


def test_bed9_explicit_validates_through_col_9_ignores_extras(tmp_path: Path) -> None:
    bed = tmp_path / "bed9_plus_2.bed"
    bed.write_text("chr1\t100\t200\tname\t500\t+\t100\t200\t0,0,0\tcustomA\tcustomB\n")
    BedValidator(bed, bed_tier="9").validate()


def test_explicit_bed_n_errors_on_too_few_columns(tmp_path: Path) -> None:
    bed = tmp_path / "bed3.bed"
    bed.write_text("chr1\t100\t200\n")
    with pytest.raises(RuntimeError, match="--bed 9 requires at least 9"):
        BedValidator(bed, bed_tier="9").validate()


def test_explicit_bed_3_skips_per_field_checks(tmp_path: Path) -> None:
    # With --bed 3, only chrom/start/end are validated. A junk score in col 5
    # passes because col 5 is treated as opaque custom.
    bed = tmp_path / "bed3_with_junk.bed"
    bed.write_text("chr1\t100\t200\tname\tnot-a-score\t+\n")
    BedValidator(bed, bed_tier="3").validate()


def test_explicit_bed_6_on_bed12_file_skips_block_validation(tmp_path: Path) -> None:
    # With --bed 6, cols 7-12 are opaque. Block invariant violations go unchecked.
    bed = tmp_path / "bed12_with_bad_blocks.bed"
    bed.write_text("chr1\t100\t200\tname\t500\t+\t100\t200\t0,0,0\t99\tbroken\tnope\n")
    BedValidator(bed, bed_tier="6").validate()
