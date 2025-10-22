"""
Logger setup module for the biovalid project.

This module provides a function to configure logging for both console and file outputs.
It is intended to be used by both CLI and library users to ensure consistent logging behavior.
"""

import logging
from pathlib import Path

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


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
    logger = logging.getLogger("biovalid")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

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
        ValueError: If the log file path is not valid.
    """
    if log_file is not None:
        log_path = Path(log_file)
        if not log_path.parent.exists():
            raise ValueError(f"Log file directory {log_path.parent} does not exist.")
        if not log_path.parent.is_dir():
            raise ValueError(f"Log file path {log_path.parent} is not a directory.")
        return log_file
    return None


def log_function(logger: logging.Logger, level: int, message: str) -> None:
    """
    Log a message at the specified logging level.
    Will raise a ValueError if the level is ERROR.

    Parameters
    ----------
    level : int
        The logging level.
        (10 for DEBUG, 20 for INFO, 30 for WARNING, 40 for ERROR)
    message : str
        The message to log.
    """
    if level == 10:
        logger.debug(message)
    elif level == 20:
        logger.info(message)
    elif level == 30:
        logger.warning(message)
    elif level == 40:
        logger.error(message)
        raise ValueError(message)
    else:
        logger.info(message)
