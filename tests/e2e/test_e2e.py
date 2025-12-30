import subprocess
import sys
from pathlib import Path

from biovalid.biovalidator import BioValidator

DATAPATH = Path("tests/data")

BOOLEAN_FLAGS = ["--bool-mode", "--verbose", "--version"]


class End2EndTester:
    def __init__(self, data_path: Path = DATAPATH):
        self.data_path = data_path

    def get_files_by_pattern(self, pattern: str) -> list[Path]:
        """Return a list of pattern file paths."""
        return list(self.data_path.glob(f"**/*{pattern}*.*"))

    def get_files_except_pattern(self, pattern: str) -> list[Path]:
        """Return a list of file paths that do not match the given pattern."""
        return [file for file in self.data_path.glob("**/*.*") if pattern not in file.as_posix()]

    def run_api(self, file_path: str, optional_args: list[str] | None = None) -> bool | None:
        """Run the API for validation."""
        args_dict: dict[str, bool | str] = {}
        if optional_args:
            for i, arg in enumerate(optional_args):
                if i % 2 == 0:
                    key = arg.lstrip("--").replace("-", "_")
                    value = True if arg in BOOLEAN_FLAGS else optional_args[i + 1]
                    args_dict[key] = value

        # Ignore this type check because args can be a mix of str and bool and we don't know here
        # which type they will be.
        validator = BioValidator(**args_dict)  # type: ignore
        return validator.validate_files(file_path, recursive=False)

    def run_cli(self, file_path: str, optional_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        """Run the CLI command for validation."""
        args = [sys.executable, "-m", "biovalid", file_path]
        if optional_args:
            args.extend(optional_args)
        return subprocess.run(args, check=False, capture_output=True, text=True)


tester = End2EndTester()


def test_end2end() -> None:
    """Test end-to-end validation for happy and unhappy files."""
    happy_file_paths = tester.get_files_by_pattern("happy")
    unhappy_file_paths = tester.get_files_except_pattern("happy")

    for file_path in happy_file_paths:
        api_result = tester.run_api(file_path.as_posix(), ["--bool-mode"])
        assert api_result is True, f"API validation failed for {file_path}"

    for file_path in unhappy_file_paths:
        api_result = tester.run_api(file_path.as_posix(), ["--bool-mode"])
        assert api_result is False, f"API validation failed for {file_path}"


def test_end2end_cli() -> None:
    """Test end-to-end validation for happy and unhappy files using the CLI interface."""
    happy_file_paths = tester.get_files_by_pattern("happy")
    unhappy_file_paths = tester.get_files_except_pattern("happy")

    for file_path in happy_file_paths:
        result = tester.run_cli(file_path.as_posix())
        assert result.returncode == 0, f"CLI validation failed for {file_path}: {result.stderr}"

    for file_path in unhappy_file_paths:
        result = tester.run_cli(file_path.as_posix())
        assert result.returncode != 0, f"CLI validation should fail for {file_path}, but it passed: {result.stdout}"
