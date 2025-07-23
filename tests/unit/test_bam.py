"""Unified test suite for BAM, FASTA, and FASTQ file validation."""

from pathlib import Path
from typing import Callable, Sequence, Type

import pytest

from biovalid.validators import BamValidator, FastaValidator, FastqValidator
from biovalid.validators.base import BaseValidator

TEST_CASES: Sequence[tuple[str, Type[BaseValidator]]] = (
    ("bam", BamValidator),
    ("fasta", FastaValidator),
    ("fastq", FastqValidator),
)


def happy_files(filetype: str) -> list[Path]:
    return list(Path(f"tests/data/{filetype}").glob("*happy*.*"))


def unhappy_files(filetype: str) -> list[Path]:
    return [
        f for f in Path(f"tests/data/{filetype}").glob("*.*") if "happy" not in f.name
    ]


happy_params = [
    pytest.param(validator_class, file_path, id=f"{filetype}-{file_path.name}")
    for filetype, validator_class in TEST_CASES
    for file_path in happy_files(filetype)
]

unhappy_params = [
    pytest.param(validator_class, file_path, id=f"{filetype}-{file_path.name}")
    for filetype, validator_class in TEST_CASES
    for file_path in unhappy_files(filetype)
]


@pytest.mark.parametrize("validator_class,file_path", happy_params)
def test_happy(validator_class, file_path):
    validator = validator_class(file_path)
    validator.validate()


@pytest.mark.parametrize("validator_class,file_path", unhappy_params)
def test_unhappy(validator_class, file_path):
    with pytest.raises(ValueError):
        validator = validator_class(file_path)
        validator.validate()
