from pathlib import Path
from typing import Type

from biovalid.arg_parser import cli_parser
from biovalid.enum import FileType
from biovalid.logger import setup_logging
from biovalid.validators import BamValidator, FastaValidator, FastqValidator
from biovalid.validators.base import BaseValidator
from biovalid.version import __version__


class BioValidator:
    """Validator class to encapsulate validation logic."""

    def _convert_file_paths_to_paths(
        self, file_paths: list[str | Path] | str | Path
    ) -> list[Path]:
        """Convert file paths to Path objects."""
        if isinstance(file_paths, list):
            return [Path(p) for p in file_paths]
        return [Path(file_paths)]


    def __init__(
        self,
        file_paths: list[str | Path] | str | Path,
        bool_mode: bool = False,
        verbose: bool = False,
        log_file: str | None = None,
        version: bool = False,
    ) -> None:
        """Initialize the BioValidator with file paths and optional arguments."""
        if version:
            print(f"BioValidator version {__version__}")
            return

        self.file_paths = self._convert_file_paths_to_paths(file_paths)
        self.bool_mode = bool_mode
        self.verbose = verbose
        self.log_file = log_file
        self.logger = setup_logging(self.verbose, self.log_file)

    def pick_validator(self, file_path: Path) -> Type[BaseValidator]:
        """Pick the appropriate validator based on the file extension."""
        file_type = FileType.from_path(file_path)

        file_type_dict: dict[FileType, Type[BaseValidator]] = {
            FileType.FASTA: FastaValidator,
            FileType.FASTQ: FastqValidator,
            FileType.BAM: BamValidator,
        }
        if file_type in file_type_dict:
            return file_type_dict[file_type]

        return BaseValidator

    def validate_files(self) -> None | bool:
        """Validate a list of file paths."""
        if not self.bool_mode:
            for path in self.file_paths:
                validator_class = self.pick_validator(path)
                validator = validator_class(path, self.logger)
                validator.general_validation()
                if validator_class != BaseValidator:
                    validator.validate()
            return None

        try:
            for path in self.file_paths:
                validator_class = self.pick_validator(path)
                validator = validator_class(path, self.logger)
                validator.general_validation()
                if validator_class != BaseValidator:
                    validator.validate()
        except ValueError:
            return False
        return True


def run_cli() -> None:
    """Main function to run the validation."""
    args = cli_parser()
    validator = BioValidator(**args.__dict__)
    validator.validate_files()


if __name__ == "__main__":
    run_cli()
