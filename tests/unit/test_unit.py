"""
Unit tests for bioinformatics file validators.

This module contains generic unit tests for the BAM, FASTA, FASTQ and GFF file validators
in the biovalid package. It checks that files matching the "happy" pattern are validated
successfully, and that files not matching the pattern raise a ValueError.

The tests are parametrized to run for each validator type using test data in
the corresponding subdirectories of tests/data/.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Type

import pytest

from biovalid.validators import (
    BaiValidator,
    BamValidator,
    FastaValidator,
    FastqValidator,
    GffValidator,
    VcfValidator,
)
from biovalid.validators.base import BaseValidator


@dataclass
class ValidatorInfo:
    """
    Container for validator class and associated test files.

    Parameters
    ----------
    validator_class : Type[BaseValidator]
        The validator class to be tested (e.g., FastaValidator).
    happy_files : list[Path]
        List of file paths expected to pass validation.
    unhappy_files : list[Path]
        List of file paths expected to fail validation.
    """

    validator_class: Type[BaseValidator]
    happy_files: list[Path]
    unhappy_files: list[Path]

    def __init__(self, validator_class: Type[BaseValidator], filetype: str):
        self.validator_class = validator_class
        self.happy_files = list(Path(f"tests/data/{filetype}").glob("*happy*.*"))
        self.unhappy_files = [f for f in Path(f"tests/data/{filetype}").glob("*.*") if "happy" not in f.name]


list_of_validators = [
    ValidatorInfo(FastaValidator, "fasta"),
    ValidatorInfo(FastqValidator, "fastq"),
    ValidatorInfo(BamValidator, "bam"),
    ValidatorInfo(GffValidator, "gff"),
    ValidatorInfo(BaiValidator, "bai"),
    ValidatorInfo(VcfValidator, "vcf"),
]


@pytest.mark.parametrize("validator_info", list_of_validators, ids=lambda v: v.validator_class.__name__)
def test_happy(validator_info: ValidatorInfo) -> None:
    """Test that happy BAM, FASTA, and FASTQ files validate without error."""
    for file_path in validator_info.happy_files:
        validator_info.validator_class(file_path).validate()


@pytest.mark.parametrize(
    "validator_info",
    list_of_validators,
    ids=lambda v: v.validator_class.__name__,
)
def test_unhappy(validator_info: ValidatorInfo) -> None:
    """Test that unhappy BAM, FASTA, and FASTQ files raise a ValueError."""
    for file_path in validator_info.unhappy_files:
        with pytest.raises(ValueError):
            validator_info.validator_class(file_path).validate()
