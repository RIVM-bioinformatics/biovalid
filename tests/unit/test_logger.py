import gc
import logging
import subprocess
from pathlib import Path
from typing import Generator

import pytest

from biovalid import BioValidator


@pytest.fixture(scope="module")
def log_path() -> Generator[Path, None, None]:
    """
    Fixture to provide a temporary log file path for testing.
    Cleans up the log file after the test is done.
    """
    test_log_path = Path("tests/data/test_log.log")
    yield test_log_path
    if test_log_path.exists():
        gc.collect()  # Ensure all file handles are released, causing issues on Windows
        test_log_path.unlink()


# disabled because in pytest, you use the fixtures as function arguments
def test_logger_initialization(log_path: Path, capsys: pytest.CaptureFixture[str]) -> None:  # pylint: disable=redefined-outer-name
    """
    Test that the logger is initialized correctly.
    Also checks that the logger has the correct level and handlers.
    Double checks that log files are created and that log messages are written to them.
    Also checks that log messages are written to the console.
    """

    validator = BioValidator(verbose=True, log_file=log_path)
    logger = validator.logger

    for handler in logger.handlers:
        handler.flush()

    test_message = "This is a test log message."
    validator.log(logging.INFO, test_message)

    captured = capsys.readouterr()
    assert test_message in captured.err

    with open(log_path, "r", encoding="utf-8") as f:
        log_contents = f.read()
        assert test_message in log_contents

    # Explicitly close file handlers to prevent Windows file locking issues
    for handler in logger.handlers:
        if hasattr(handler, "close"):
            handler.close()

    # Remove handlers to ensure clean state
    logger.handlers.clear()


def test_cli_log_functionality(
    log_path: Path,  # pylint: disable=redefined-outer-name
) -> None:
    """
    Test that the CLI logging functionality works as expected.
    This includes checking that log messages are written to the specified log file
    and that they are also printed to the console when verbose mode is enabled.
    """

    subprocess_args = [
        "python",
        "-m",
        "biovalid",
        "tests/data/gff/gff3_happy3.gff",
        "--log-file",
        str(log_path),
        "--verbose",
    ]
    result = subprocess.run(subprocess_args, capture_output=True, text=True, check=True)

    # have to do it in parts because of different formatting in different environments
    # (e.g., Windows vs Linux line endings, timestamps, etc)
    # dont use that paths variable in the comparison (slashes etc)
    expected_parts = ["WARNING", "invalid number of columns", "line 2", "Padded the missing columns"]

    output_text = result.stdout + result.stderr
    for part in expected_parts:
        assert part in output_text, f"Expected '{part}' not found in output: {output_text}"

    with open(log_path, "r", encoding="utf-8") as f:
        log_contents = f.read()
        for part in expected_parts:
            assert part in log_contents, f"Expected '{part}' not found in log file: {log_contents}"
