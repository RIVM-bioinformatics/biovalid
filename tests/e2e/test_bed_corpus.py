"""
End-to-end validation of the BED corpus (tests/corpus/bed/).

The corpus is a collection of 100 BED-file fixtures synthesized from real-world
pathology reports across public bug trackers (bedtools, pybedtools, htslib,
deepTools, bedops) and the Niu, Denisko, Hoffman 2022 survey of BED-handling
tools. Each fixture cites its source inline and is bucketed by validator
behavior under the two --spec modes:

  universal_bad/  validator rejects in both --spec ucsc and --spec hts
  hts_only_bad/   passes in --spec ucsc, rejects in --spec hts
  good/           passes in both modes

See tests/corpus/bed/README.md for the bucket structure.

Validator is invoked via the BioValidator Python API in --bed auto mode
(the default); a handful of fixtures (notably narrowPeak-shaped BED6+4
files) deliberately land in universal_bad because they need an explicit
--bed 6 to validate cleanly, which the corpus' design exercises rather
than masks.
"""

from pathlib import Path

import pytest

from biovalid.biovalidator import BioValidator

CORPUS = Path(__file__).parent.parent / "corpus" / "bed"


def _corpus_files(bucket: str) -> list[Path]:
    return sorted((CORPUS / bucket).glob("*.bed"))


def _validate(path: Path, spec: str) -> bool:
    return BioValidator(bool_mode=True, spec=spec).validate_files(str(path))


@pytest.mark.parametrize("path", _corpus_files("universal_bad"), ids=lambda p: p.name)
@pytest.mark.parametrize("spec", ["ucsc", "hts"])
def test_universal_bad_rejected_in_both_modes(path: Path, spec: str) -> None:
    assert _validate(path, spec) is False


@pytest.mark.parametrize("path", _corpus_files("hts_only_bad"), ids=lambda p: p.name)
def test_hts_only_bad_passes_in_ucsc(path: Path) -> None:
    assert _validate(path, "ucsc") is True


@pytest.mark.parametrize("path", _corpus_files("hts_only_bad"), ids=lambda p: p.name)
def test_hts_only_bad_rejected_in_hts(path: Path) -> None:
    assert _validate(path, "hts") is False


@pytest.mark.parametrize("path", _corpus_files("good"), ids=lambda p: p.name)
@pytest.mark.parametrize("spec", ["ucsc", "hts"])
def test_good_accepted_in_both_modes(path: Path, spec: str) -> None:
    assert _validate(path, spec) is True
