"""
Logger setup module for the biovalid project.

This module provides a function to configure logging for both console and file outputs.
It is intended to be used by both CLI and library users to ensure consistent logging behavior.
"""

import logging
from pathlib import Path
from threading import Lock
from typing import Any

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


class ValidationLogger(logging.Logger):
    """Logger that tracks error count without raising exceptions."""

    def __init__(self, name: str, level: int = logging.NOTSET) -> None:
        super().__init__(name, level)
        self._error_count = 0
        self._error_count_lock = Lock()

    def error(self, msg: Any, *args: object, **kwargs: Any) -> None:
        with self._error_count_lock:
            self._error_count += 1
        super().error(msg, *args, **kwargs)

    def get_error_count(self) -> int:
        with self._error_count_lock:
            return self._error_count

    def reset_error_count(self) -> None:
        with self._error_count_lock:
            self._error_count = 0


def setup_logging(verbose: bool = False, log_file: Path | str | None = None) -> logging.Logger:
    """
    Set up logging for the biovalid project.

    Configures a logger named 'biovalid' with handlers for console output and, optionally, file output.
    The log level for the console can be set to DEBUG or INFO based on the verbose flag.
    If a log file is provided, logs will also be written to that file.

    Parameters
    ----------
    verbose : bool, optional
        If True, set console and possible file log level to DEBUG. Otherwise, set to INFO. Default is False.
    log_file : str or None, optional
        Path to a log file. If provided, logs will also be written to this file. Default is None.

    Returns
    -------
    logging.Logger
        Configured logger instance for the biovalid project.
    """
    logging.setLoggerClass(ValidationLogger)
    logger = logging.getLogger("biovalid")
    if not isinstance(logger, ValidationLogger):
        raise RuntimeError("Logger 'biovalid' is not configured as ValidationLogger")

    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.reset_error_count()

    console_handler = logging.StreamHandler()
    if verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFMT))
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        if verbose:
            file_handler.setLevel(logging.DEBUG)
        else:
            file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFMT))
        logger.addHandler(file_handler)

    logger.debug("Logging setup complete.")
    return logger


def validate_log_file(log_file: str | None) -> str | None:
    """
    Validates the log file path.
    Args:
        log_file (str | None): Path to the log file.
    Returns:
        str | None: The validated log file path.
    Raises:
        RuntimeError: If the log file path is not valid.
    """
    if log_file is not None:
        log_path = Path(log_file)
        if not log_path.parent.exists():
            raise RuntimeError(f"Log file directory {log_path.parent} does not exist.")
        if not log_path.parent.is_dir():
            raise RuntimeError(f"Log file path {log_path.parent} is not a directory.")
        return log_file
    return None
