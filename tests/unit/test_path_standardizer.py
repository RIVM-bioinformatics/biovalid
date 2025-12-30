import tempfile
from pathlib import Path

import pytest

from biovalid.biovalidator import BioValidator


def test_convert_file_paths_to_paths() -> None:
    """
    Test the _convert_file_paths_to_paths method of the BioValidator class.
    Method should only return files that are either specifically passed as input or,
    if a directory is passed, all files in that directory which are recognized as bionformatic file types
    (and subdirectories if recursive=True). (fastq, fasta, bam, bai, gff)
    Test cases:
    - Single string path
    - Single Path object
    - List of string paths
    - List of Path objects
    - Mixed list
    - Directory input with recursive True/False (should handle appropriately)
    """

    def create_test_cases() -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path, Path, Path, Path]:

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
        return temp_dir, file1, file2, file3, sub_dir, file4, file5

    temp_dir, file1, _file2, file3, _sub_dir, file4, _file5 = create_test_cases()
    validator = BioValidator()

    result = validator.convert_file_paths_to_paths(file1.as_posix(), recursive=False)
    assert result == [file1]
    result = validator.convert_file_paths_to_paths(file1, recursive=False)
    assert result == [file1]
    result = validator.convert_file_paths_to_paths([file1.as_posix(), file3.as_posix()], recursive=False)
    assert result == [file1, file3]
    result = validator.convert_file_paths_to_paths([file1, file3], recursive=False)
    assert result == [file1, file3]

    result = validator.convert_file_paths_to_paths([file1.as_posix(), file3], recursive=False)
    assert result == [file1, file3]

    result = validator.convert_file_paths_to_paths(temp_dir.name, recursive=False)
    assert set(result) == {file3, file1}  # file2 is not a recognized type
    assert len(result) == 2
    result = validator.convert_file_paths_to_paths(temp_dir.name, recursive=True)
    assert set(result) == {file3, file1, file4}  # file4 is in subdir
    assert len(result) == 3

    # bad input
    # type errors are ignored because we are testing invalid input
    with pytest.raises(ValueError):
        validator.convert_file_paths_to_paths([file1.as_posix(), file3, 123], recursive=False)  # type: ignore

    with pytest.raises(ValueError):
        validator.convert_file_paths_to_paths(123, recursive=False)  # type: ignore

    with pytest.raises(ValueError):
        validator.convert_file_paths_to_paths([123, 456], recursive=False)  # type: ignore

    with pytest.raises(ValueError):
        validator.convert_file_paths_to_paths([file1.as_posix(), "bad_path"], recursive=False)

    temp_dir.cleanup()
