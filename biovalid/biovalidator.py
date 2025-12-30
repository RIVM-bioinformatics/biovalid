from pathlib import Path
from typing import Type

from biovalid.arg_parser import cli_parser
from biovalid.enum import FileType
from biovalid.logger import log_function, setup_logging
from biovalid.validators import (
    BaiValidator,
    BamValidator,
    FastaValidator,
    FastqValidator,
    GffValidator,
    VcfValidator,
)
from biovalid.validators.base import BaseValidator
from biovalid.version import __version__


class BioValidator:
    """Validator class to encapsulate validation logic."""

    def convert_file_paths_to_paths(self, file_paths: list[str | Path] | str | Path, recursive: bool) -> list[Path]:
        """Convert input file paths to a list of Path objects."""

        # The ignores are because this is user input and I want to make sure it's validated properly
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]
        elif not isinstance(file_paths, list):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("file_paths must be a string, Path, or list of strings/Paths")
        elif any(not isinstance(fp, (str, Path)) for fp in file_paths):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("All elements in file_paths list must be strings or Path objects")
        files: list[Path] = []
        dirs: list[Path] = []
        for fp in file_paths:
            p = Path(fp)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                dirs.append(p)
            else:
                raise ValueError(f"Path {p} is neither a file nor a directory.")
        # now handle directories
        for d in dirs:
            if recursive:
                for path in d.rglob("*"):
                    if path.is_file() and FileType.from_path(path) != FileType.UNKNOWN:
                        files.append(path)
            else:
                for path in d.iterdir():
                    if path.is_file() and FileType.from_path(path) != FileType.UNKNOWN:
                        files.append(path)
        return files

    def __init__(
        self,
        bool_mode: bool = False,
        verbose: bool = False,
        log_file: Path | str | None = None,
        version: bool = False,
    ) -> None:
        """Initialize the BioValidator with file paths and optional arguments."""
        if version:
            print(f"BioValidator version {__version__}")
            return

        self.bool_mode = bool_mode
        self.verbose = verbose
        self.log_file = log_file
        self.logger = setup_logging(self.verbose, self.log_file)

    def log(self, level: int, message: str) -> None:
        """Log a message with the specified severity level."""
        log_function(self.logger, level, message)

    def pick_validator(self, file_path: Path) -> Type[BaseValidator]:
        """Pick the appropriate validator based on the file extension."""
        file_type = FileType.from_path(file_path)

        file_type_dict: dict[FileType, Type[BaseValidator]] = {
            FileType.FASTA: FastaValidator,
            FileType.FASTQ: FastqValidator,
            FileType.BAM: BamValidator,
            FileType.BAI: BaiValidator,
            FileType.GFF: GffValidator,
            FileType.VCF: VcfValidator,
        }
        if file_type in file_type_dict:
            return file_type_dict[file_type]

        return BaseValidator

    def validate_files(self, paths: list[str | Path] | str | Path, recursive: bool = False) -> bool:
        """Validate a list of file paths."""
        clean_paths = self.convert_file_paths_to_paths(paths, recursive=recursive)

        if not self.bool_mode:
            try:
                for path in clean_paths:
                    validator_class = self.pick_validator(path)
                    validator = validator_class(path, self.logger)
                    validator.general_validation()
                    if validator_class != BaseValidator:
                        validator.validate()
                self.log(20, "All files validated successfully.")
            except ValueError as e:
                self.log(20, f"Validation failed: {e}")
                raise e

        try:
            for path in clean_paths:
                validator_class = self.pick_validator(path)
                validator = validator_class(path, self.logger)
                validator.general_validation()
                if validator_class != BaseValidator:
                    validator.validate()
            self.log(20, "All files validated successfully.")
        except ValueError:
            self.log(20, "Validation failed.")
            return False
        return True


def run_cli() -> None:
    """Main function to run the validation."""
    args = cli_parser()
    validator = BioValidator(bool_mode=args.bool_mode, verbose=args.verbose, log_file=args.log_file)
    try:
        validator.validate_files(args.file_paths, recursive=args.recursive)
    except Exception as e:
        # Flush and close all handlers to ensure logs are written
        for handler in validator.logger.handlers:
            handler.flush()
            handler.close()
        raise e
    finally:
        # Always flush and close handlers to ensure logs are written
        for handler in validator.logger.handlers:
            handler.flush()
            handler.close()


if __name__ == "__main__":
    run_cli()
