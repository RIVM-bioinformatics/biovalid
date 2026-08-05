from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Type

from biovalid.arg_parser import PathStabilizer, cli_parser
from biovalid.domain.enum import CompressionType, FileType
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
        threads: int = 1,
        verbose: bool = False,
        log_file: Path | str | None = None,
        display_version: bool = False,
    ) -> None:
        """Initialize the BioValidator with arguments."""
        if display_version:
            print(f"BioValidator version {__version__}")
            return

        self.bool_mode = bool_mode
        self.threads = threads
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

    def _check_compression_support(self, file_path: Path, file_type: FileType) -> None:
        """Ensure compression is only used for supported file type combinations."""
        try:
            compression_type = CompressionType.from_path(file_path)
        except RuntimeError:
            return

        if compression_type != CompressionType.GZIP:
            self.logger.error(
                "File %s uses unsupported compression type '%s'. Only gzip compression is currently supported for FASTA and FASTQ.",
                file_path,
                compression_type.value,
            )

        if file_type not in (FileType.FASTA, FileType.FASTQ):
            self.logger.error(
                "File %s is a compressed %s file. Gzip compression is currently only supported for FASTA and FASTQ files.",
                file_path,
                file_type.name,
            )

    def validate_files(self, paths: list[str | Path] | str | Path, recursive: bool = False) -> bool:
        """Validate a list of file paths."""
        clean_paths = self.path_stabilizer.convert_file_paths_to_paths(paths, recursive=recursive)

        def _validate_path(path: Path) -> None:
            self.logger.debug("Validating file: %s", path)
            validator_class = self.pick_validator(path)
            file_type = FileType.from_path(path)
            self._check_compression_support(path, file_type)
            validator = validator_class(path, self.logger)
            validator.general_validation()
            if validator_class != BaseValidator:
                validator.validate()
            self.logger.info("File %s validated successfully.", path)

        def _threading_wrapper() -> None:
            worker_count = max(1, self.threads)
            self.logger.debug("Using %d threads for validation.", worker_count)

            if worker_count == 1 or len(clean_paths) < 2:
                for path in clean_paths:
                    _validate_path(path)
                self.logger.info("All files validated successfully.")
                return

            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                futures = [executor.submit(_validate_path, path) for path in clean_paths]
                for future in as_completed(futures):
                    future.result()

            self.logger.info("All files validated successfully.")

        try:
            _threading_wrapper()
        except RuntimeError as e:
            if self.bool_mode:
                return False
            raise e
        return True


def run_cli() -> None:
    """Main function to run the validation."""
    args = cli_parser()
    validator = BioValidator(bool_mode=args.bool_mode, threads=args.threads, verbose=args.verbose, log_file=args.log_file)
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
