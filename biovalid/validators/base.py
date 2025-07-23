"""
Base class for bioinformatics file validators.

This module defines the abstract base class for all file type validators
in the biovalid package. Subclasses should implement the `validate` method
to provide file type-specific validation logic.
"""

import os
from logging import Logger
from pathlib import Path

from biovalid.logger import setup_logging


class BaseValidator:
    """
    Abstract base class for file validators.

    All specific file type validators should inherit from this class and
    implement the `validate` method.

    Parameters
    ----------
    logger : Logger
        Logger instance for recording validation events and errors.
    """

    def __init__(self, filename: Path, logger: Logger | None = None) -> None:
        self.filename = filename
        if not logger:
            self.logger = setup_logging()
        else:
            self.logger = logger

    def log(self, level: int, message: str) -> None:
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
            self.logger.debug(message)
        elif level == 20:
            self.logger.info(message)
        elif level == 30:
            self.logger.warning(message)
        elif level == 40:
            self.logger.error(message)
            raise ValueError(message)

    def general_validation(self) -> None:
        """
        Checks the following conditions for a file:
        1. The file exists.
        2. The file is not empty.
        3. The file is readable.
        Args:
            file_path (Path): Path to the file to validate.
        Raises:
            ValueError: If the file does not exist, is empty, or is not readable.
        """

        if not self.filename.exists():
            self.log(40, f"File {self.filename} does not exist.")
        if not self.filename.is_file():
            self.log(40, f"Path {self.filename} is not a file.")
        if self.filename.stat().st_size == 0:
            self.log(40, f"File {self.filename} is empty.")
        if not os.access(self.filename, os.R_OK):
            self.log(40, f"File {self.filename} is not readable.")

    def validate(self) -> None:
        """
        Validate the given file.

        Subclasses must implement this method to provide file type-specific
        validation logic.

        Parameters
        ----------
        path : Path
            Path to the file to be validated.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement validate()")
