"""End-to-end tests for the biovalid package."""

import subprocess
import sys
from pathlib import Path

from biovalid.main import BioValidator

DATAPATH = Path("tests/data")


class End2EndTests:
    def __init__(self, data_path: Path = DATAPATH):
        self.data_path = data_path

    def get_files_by_pattern(self, pattern: str) -> list[Path]:
        """Return a list of pattern file paths."""
        return list(self.data_path.glob(f"**/*{pattern}*.*"))

    def run_api(
        self, file_path: str, optional_args: list[str] | None = None
    ) -> bool | None:
        """Run the API for validation."""
        return validate_files(file_path, *optional_args if optional_args else [])

    def run_cli(
        self, file_path: str, optional_args: list[str] | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        """Run the CLI command for validation."""
        args = [sys.executable, "-m", "biovalid", file_path]
        if optional_args:
            args.extend(optional_args)
        return subprocess.run(args, check=True)
