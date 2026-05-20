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

    def general_validation(self) -> None:
        """
        Checks the following conditions for a file:
        1. The file exists.
        2. The file is not empty.
        3. The file is readable.
        If any of these conditions are not met, an error message is logged indicating the specific issue with the file.
        """

        if not self.filename.exists():
            self.logger.error("File %s does not exist.", self.filename)
        if not self.filename.is_file():
            self.logger.error("Path %s is not a file.", self.filename)
        if self.filename.stat().st_size == 0:
            self.logger.error("File %s is empty.", self.filename)
        if not os.access(self.filename, os.R_OK):
            self.logger.error("File %s is not readable.", self.filename)

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
