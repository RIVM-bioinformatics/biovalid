from pathlib import Path
from typing import Type

from biovalid.arg_parser import PathStabilizer, cli_parser
from biovalid.domain.enum import FileType
from biovalid.logger import setup_logging
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

    def __init__(
        self,
        bool_mode: bool = False,
        verbose: bool = False,
        log_file: Path | str | None = None,
        display_version: bool = False,
    ) -> None:
        """Initialize the BioValidator with arguments."""
        if display_version:
            print(f"BioValidator version {__version__}")
            return

        self.bool_mode = bool_mode
        self.verbose = verbose
        self.log_file = log_file
        self.path_stabilizer = PathStabilizer()
        self.logger = setup_logging(self.verbose, self.log_file)

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
        clean_paths = self.path_stabilizer.convert_file_paths_to_paths(paths, recursive=recursive)

        if not self.bool_mode:
            try:
                for path in clean_paths:
                    validator_class = self.pick_validator(path)
                    validator = validator_class(path, self.logger)
                    validator.general_validation()
                    if validator_class != BaseValidator:
                        validator.validate()
                self.logger.info("All files validated successfully.")
            except RuntimeError as e:
                self.logger.error("Validation failed: %s", e)
                raise e

        try:
            for path in clean_paths:
                validator_class = self.pick_validator(path)
                validator = validator_class(path, self.logger)
                validator.general_validation()
                if validator_class != BaseValidator:
                    validator.validate()
            self.logger.info("All files validated successfully.")
        except RuntimeError:
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
