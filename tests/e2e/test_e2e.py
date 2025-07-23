import subprocess
import sys
from pathlib import Path

import pytest

from biovalid.main import BioValidator

DATAPATH = Path("tests/data")


class End2EndTests:
    def __init__(self, data_path: Path = DATAPATH):
        self.data_path = data_path

    def get_files_by_pattern(self, pattern: str) -> list[Path]:
        """Return a list of pattern file paths."""
        return list(self.data_path.glob(f"**/*{pattern}*.*"))

    def run_api(self, file_path: str, optional_args: list[str] | None = None) -> None:
        """Run the API for validation."""
        validator = BioValidator(file_paths=file_path, bool_mode=True)
        return validator.validate_files()

    def run_cli(self, file_path: str, optional_args: list[str] | None = None) -> None:
        """Run the CLI command for validation."""
        args = [sys.executable, "-m", "biovalid", file_path]
        if optional_args:
            args.extend(optional_args)
        return subprocess.run(args, check=True)


DATAPATH = Path("tests/data")


def get_files_by_pattern(pattern: str) -> list[Path]:
    """Return a list of pattern file paths."""
    return list(DATAPATH.glob(f"**/*{pattern}*.*"))


@pytest.mark.parametrize(
    "file_path", get_files_by_pattern("happy"), ids=lambda x: x.name
)
def test_validate_files_happy(file_path: Path):
    """Test validation of happy files."""
    validator = BioValidator(file_paths=file_path, bool_mode=False)
    assert validator.validate_files() is None, f"Validation failed for {file_path}"


@pytest.mark.parametrize(
    "file_path", [get_files_by_pattern("happy")[0]], ids=lambda x: x.name
)  # only check 1
def test_validate_files_cli(file_path: Path):
    process_res = subprocess.run(
        args=[
            sys.executable,
            "-m",
            "biovalid",
            str(file_path),
            "--bool-mode",
        ],
        check=True,
    )
    assert (
        process_res.returncode == 0
    ), f"Validation failed for {file_path} with return code {process_res.returncode}"
