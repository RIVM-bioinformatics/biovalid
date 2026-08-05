from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Type

from biovalid.arg_parser import PathStabilizer, cli_parser
from biovalid.domain.enum import CompressionType, FileType
from biovalid.logger import ValidationLogger, setup_logging
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
        raise_errors: bool = False,
        threads: int = 1,
        verbose: bool = False,
        log_file: Path | str | None = None,
        display_version: bool = False,
    ) -> None:
        """Initialize the BioValidator with arguments."""
        if display_version:
            print(f"BioValidator version {__version__}")
            return

        self.raise_errors = raise_errors
        self.threads = threads
        self.verbose = verbose
        self.log_file = log_file
        self.path_stabilizer = PathStabilizer()
        logger = setup_logging(self.verbose, self.log_file)
        if not isinstance(logger, ValidationLogger):
            raise RuntimeError("BioValidator requires a ValidationLogger instance")
        self.logger = logger

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

    def _validate_path(self, path: Path) -> None:
        self.logger.debug("Validating file: %s", path)
        validator_class = self.pick_validator(path)
        file_type = FileType.from_path(path)
        self._check_compression_support(path, file_type)
        validator = validator_class(path, self.logger)
        validator.general_validation()
        if validator_class != BaseValidator:
            validator.validate()
        self.logger.debug("Finished validating file: %s", path)

    def _validate_paths_sequential(self, clean_paths: list[Path]) -> list[Path]:
        failed_files: list[Path] = []
        for path in clean_paths:
            try:
                self._validate_path(path)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.logger.error("Unexpected error while validating %s: %s", path, str(exc))
                failed_files.append(path)
        return failed_files

    def _validate_paths_parallel(self, clean_paths: list[Path], worker_count: int) -> list[Path]:
        failed_files: list[Path] = []
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_to_path = {executor.submit(self._validate_path, path): path for path in clean_paths}
            for future in as_completed(future_to_path):
                try:
                    future.result()
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    self.logger.error("Unexpected error while validating %s: %s", future_to_path[future], str(exc))
                    failed_files.append(future_to_path[future])
        return failed_files

    def _finalize_validation_result(self, failed_files: list[Path], baseline_error_count: int) -> bool:
        total_new_errors = self.logger.get_error_count() - baseline_error_count

        if failed_files:
            self.logger.warning("Validation encountered unexpected failures in %d file(s).", len(failed_files))

        if total_new_errors > 0:
            self.logger.warning("Validation finished with %d error log message(s).", total_new_errors)
            return False

        self.logger.info("All files validated successfully.")
        return True

    def validate_files(self, paths: list[str | Path] | str | Path, recursive: bool = False) -> bool:
        """Validate a list of file paths."""
        baseline_error_count = self.logger.get_error_count()
        clean_paths = self.path_stabilizer.convert_file_paths_to_paths(paths, recursive=recursive)

        worker_count = max(1, self.threads)
        self.logger.debug("Using %d threads for validation.", worker_count)

        if worker_count == 1 or len(clean_paths) < 2:
            failed_files = self._validate_paths_sequential(clean_paths)
        else:
            failed_files = self._validate_paths_parallel(clean_paths, worker_count)

        is_valid = self._finalize_validation_result(failed_files, baseline_error_count)
        if not is_valid and self.raise_errors:
            raise RuntimeError("Validation unsuccessful")
        return is_valid


def run_cli() -> None:
    """Main function to run the validation."""
    args = cli_parser()
    validator = BioValidator(raise_errors=args.raise_errors, threads=args.threads, verbose=args.verbose, log_file=args.log_file)
    try:
        is_valid = validator.validate_files(args.file_paths, recursive=args.recursive)
        if not is_valid:
            raise SystemExit(1)
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
