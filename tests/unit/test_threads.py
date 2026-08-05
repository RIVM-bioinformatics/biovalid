from argparse import Namespace
from pathlib import Path
from typing import Any, Literal

import biovalid.biovalidator as biovalidator


class _DummyHandler:
    def flush(self) -> None:
        return

    def close(self) -> None:
        return


class _DummyLogger:
    def __init__(self) -> None:
        self.handlers = [_DummyHandler()]


def test_run_cli_passes_threads_to_biovalidator(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_cli_parser() -> Namespace:
        return Namespace(
            file_paths=["tests/data/fastq/happy.fastq"],
            recursive=False,
            bool_mode=True,
            threads=4,
            verbose=False,
            log_file=None,
        )

    class DummyValidator:
        def __init__(self, **kwargs: Any) -> None:
            captured["init_kwargs"] = kwargs
            self.logger = _DummyLogger()

        def validate_files(self, paths: list[str], recursive: bool = False) -> bool:
            captured["paths"] = paths
            captured["recursive"] = recursive
            return True

    monkeypatch.setattr(biovalidator, "cli_parser", fake_cli_parser)
    monkeypatch.setattr(biovalidator, "BioValidator", DummyValidator)

    biovalidator.run_cli()

    assert captured["init_kwargs"]["threads"] == 4


class _ImmediateFuture:
    def __init__(self, fn: Any, args: tuple[Any, ...]) -> None:
        self._exception: Exception | None = None
        try:
            fn(*args)
        except RuntimeError as exc:  # pragma: no cover - exercised on failure paths
            self._exception = exc

    def result(self) -> None:
        if self._exception:
            raise self._exception


class _RecordingExecutor:
    created_with: int | None = None
    submit_calls = 0

    def __init__(self, max_workers: int) -> None:
        _RecordingExecutor.created_with = max_workers

    def __enter__(self) -> "_RecordingExecutor":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Literal[False]:
        return False

    def submit(self, fn: Any, *args: Any) -> _ImmediateFuture:
        _RecordingExecutor.submit_calls += 1
        return _ImmediateFuture(fn, args)


def test_validate_files_uses_thread_pool_when_threads_gt_one(monkeypatch: Any) -> None:
    validator = biovalidator.BioValidator(bool_mode=True, threads=3)

    file_paths = [Path("tests/data/fasta/happy.fasta"), Path("tests/data/fastq/happy.fastq")]

    monkeypatch.setattr(
        validator.path_stabilizer,
        "convert_file_paths_to_paths",
        lambda _paths, recursive=False: file_paths,
    )
    monkeypatch.setattr(biovalidator, "ThreadPoolExecutor", _RecordingExecutor)
    monkeypatch.setattr(biovalidator, "as_completed", lambda futures: futures)

    assert validator.validate_files(["ignored"], recursive=False) is True
    assert _RecordingExecutor.created_with == 3
    assert _RecordingExecutor.submit_calls == len(file_paths)
