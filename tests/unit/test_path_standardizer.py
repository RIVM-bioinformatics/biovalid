import tempfile
from pathlib import Path
from typing import Generator, TypeAlias

import pytest

from biovalid.arg_parser import PathStabilizer

# I want to test the protected methods, and I dont agree that using a fixture is redefining an outer name.
# pylint: disable=protected-access,redefined-outer-name
# pyright: reportPrivateUsage=false

TestCases: TypeAlias = tuple[tempfile.TemporaryDirectory[str], Path, Path, Path, Path, Path, Path]


@pytest.fixture(scope="class")
def cases() -> Generator[TestCases, None, None]:
    """
    Create test cases for the PathStabilizer class.
    """
    temp_dir = tempfile.TemporaryDirectory()
    file1 = Path(temp_dir.name) / "file1.fastq"
    file2 = Path(temp_dir.name) / "file2.txt"
    file3 = Path(temp_dir.name) / "file3.fastq"
    file1.touch()
    file2.touch()
    file3.touch()
    sub_dir = Path(temp_dir.name) / "subdir"
    sub_dir.mkdir()
    file4 = sub_dir / "file4.fastq"
    file5 = sub_dir / "file5.txt"
    file4.touch()
    file5.touch()
    yield temp_dir, file1, file2, file3, sub_dir, file4, file5
    temp_dir.cleanup()


@pytest.fixture(scope="class")
def stabilizer() -> PathStabilizer:
    """
    Create a PathStabilizer instance for testing.
    """
    return PathStabilizer()


class TestPathStabilizer:
    """
    Test the PathStabilizer class.
    """

    def test_make_file_list(self, stabilizer: PathStabilizer, cases: TestCases) -> None:
        _, file1, file2, file3, _, _, _ = cases
        file_list = stabilizer._make_file_list([file1, file2, file3])
        assert set(file_list) == {file1, file2, file3}

    def test_separate_files_and_dirs(self, stabilizer: PathStabilizer, cases: TestCases) -> None:
        _, file1, file2, _, sub_dir, _, _ = cases
        files, dirs = stabilizer._separate_files_and_dirs([file1, file2, sub_dir])
        assert set(files) == {file1, file2}
        assert set(dirs) == {sub_dir}

    def test_iter_directory_paths(self, stabilizer: PathStabilizer, cases: TestCases) -> None:
        temp_dir, file1, file2, file3, sub_dir, file4, file5 = cases
        temp_path = Path(temp_dir.name)

        stabilizer.recursive = False
        paths = list(stabilizer._iter_directory_paths(temp_path))
        assert set(paths) == {file1, file2, file3, sub_dir}

        stabilizer.recursive = True
        paths = list(stabilizer._iter_directory_paths(temp_path))
        assert set(paths) == {file1, file2, file3, sub_dir, file4, file5}

    def test_is_supported_file(self, stabilizer: PathStabilizer, cases: TestCases) -> None:
        _, file1, file2, _, sub_dir, _, _ = cases
        assert stabilizer._is_supported_file(file1) is True
        assert stabilizer._is_supported_file(file2) is False
        assert stabilizer._is_supported_file(sub_dir) is False

    def test_populate_files_from_directories(self, stabilizer: PathStabilizer, cases: TestCases) -> None:
        temp_dir, file1, _, file3, _, file4, _ = cases
        temp_path = Path(temp_dir.name)

        stabilizer.recursive = False
        files = stabilizer._populate_files_from_directories([file1], [temp_path])
        assert set(files) == {file1, file3}

        stabilizer.recursive = True
        files = stabilizer._populate_files_from_directories([file1], [temp_path])
        assert set(files) == {file1, file3, file4}

    def test_convert_file_paths_to_paths(self, stabilizer: PathStabilizer, cases: TestCases) -> None:
        temp_dir, file1, _, file3, _, file4, _ = cases
        result = stabilizer.convert_file_paths_to_paths(file1.as_posix(), recursive=False)
        assert result == [file1]
        result = stabilizer.convert_file_paths_to_paths(file1, recursive=False)
        assert result == [file1]
        result = stabilizer.convert_file_paths_to_paths([file1.as_posix(), file3.as_posix()], recursive=False)
        assert result == [file1, file3]
        result = stabilizer.convert_file_paths_to_paths([file1, file3], recursive=False)
        assert result == [file1, file3]

        result = stabilizer.convert_file_paths_to_paths([file1.as_posix(), file3], recursive=False)
        assert result == [file1, file3]

        result = stabilizer.convert_file_paths_to_paths(temp_dir.name, recursive=False)
        assert set(result) == {file3, file1}  # file2 is not a recognized type
        assert len(result) == 2
        result = stabilizer.convert_file_paths_to_paths(temp_dir.name, recursive=True)
        assert set(result) == {file3, file1, file4}  # file4 is in subdir
        assert len(result) == 3

    def test_convert_file_paths_to_paths_invalid_input(self, stabilizer: PathStabilizer, cases: TestCases) -> None:
        _, file1, _, file3, _, _, _ = cases
        bad_file_list = [file1.as_posix(), file3, 123]
        with pytest.raises(RuntimeError):
            stabilizer.convert_file_paths_to_paths(bad_file_list, recursive=False)  # type: ignore

    def test_convert_file_paths_to_paths_invalid_input_types(self, stabilizer: PathStabilizer) -> None:
        bad_input = 123
        with pytest.raises(RuntimeError):
            stabilizer.convert_file_paths_to_paths(bad_input, recursive=False)  # type: ignore

    def test_convert_file_paths_to_paths_invalid_paths(self, stabilizer: PathStabilizer) -> None:
        invalid_paths = [123, 456]
        with pytest.raises(RuntimeError):
            stabilizer.convert_file_paths_to_paths(invalid_paths, recursive=False)  # type: ignore

    def test_convert_file_paths_to_paths_nonexistent_path(self, stabilizer: PathStabilizer, cases: TestCases) -> None:
        _, file1, _, _, _, _, _ = cases
        with pytest.raises(RuntimeError):
            stabilizer.convert_file_paths_to_paths([file1.as_posix(), "bad_path"], recursive=False)
