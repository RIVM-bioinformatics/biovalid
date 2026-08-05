from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Iterable

from biovalid.domain.enum import FileType
from biovalid.logger import validate_log_file
from biovalid.version import __version__


def cli_parser() -> Namespace:
    parser = ArgumentParser(
        prog="biovalid",
        description="A tool for validating bioinformatics files.",
        epilog="For more information, visit https://github.com/RIVM-bioinformatics/biovalid",
    )
    parser.add_argument(
        "file_paths",
        nargs="+",
        type=str,
        help="One or more file paths to validate. Can be compressed files. Can also be a directory containing files.",
    )

    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        default=False,
        help="Recursively validate all files in a directory tree.",
    )

    parser.add_argument(
        "--bool-mode",
        "-b",
        action="store_true",
        default=False,
        help="Return True if all files are valid, False if any file is invalid.",
    )

    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=1,
        help="Number of threads to use for validation. Default is 1.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose output.",
    )

    parser.add_argument(
        "--log-file",
        "-l",
        type=validate_log_file,
        default=None,
        help="Path to a log file.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version of biovalid.",
    )

    return parser.parse_args()


class PathStabilizer:
    """
    This class does nothing but take input and return only a list of Path objects.
    It is used to ensure that the input is valid and to convert it to a list of Path objects.
    """

    def __init__(self) -> None:
        self.recursive: bool = False

    def convert_file_paths_to_paths(self, file_paths: list[str | Path] | str | Path, recursive: bool = False) -> list[Path]:
        """Convert input file paths to a list of Path objects."""
        self.recursive = recursive
        file_list = self._make_file_list(file_paths)
        files, dirs = self._separate_files_and_dirs(file_list)
        # now handle directories
        return self._populate_files_from_directories(files, dirs)

    def _populate_files_from_directories(self, files: list[Path], dirs: list[Path]) -> list[Path]:
        for directory in dirs:
            for path in self._iter_directory_paths(directory):
                if self._is_supported_file(path):
                    files.append(path)
        return files

    def _iter_directory_paths(self, directory: Path) -> Iterable[Path]:
        if self.recursive:
            return directory.rglob("*")
        return directory.iterdir()

    def _is_supported_file(self, path: Path) -> bool:
        return path.is_file() and FileType.from_path(path) != FileType.UNKNOWN

    def _separate_files_and_dirs(self, file_paths: list[str | Path]) -> tuple[list[Path], list[Path]]:
        files: list[Path] = []
        dirs: list[Path] = []
        for fp in file_paths:
            p = Path(fp)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                dirs.append(p)
            else:
                raise RuntimeError(f"Path {p} is neither a file nor a directory.")
        return files, dirs

    def _make_file_list(self, file_paths: list[str | Path] | str | Path) -> list[str | Path]:
        # The ignores are because this is user input and I want to make sure it's validated properly
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]
        elif not isinstance(file_paths, list):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise RuntimeError("file_paths must be a string, Path, or list of strings/Paths")
        elif any(not isinstance(fp, (str, Path)) for fp in file_paths):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise RuntimeError("All elements in file_paths list must be strings or Path objects")
        return file_paths
