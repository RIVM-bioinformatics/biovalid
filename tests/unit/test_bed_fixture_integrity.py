"""
Byte-level integrity checks for BED test fixtures whose bytes are the test
subject. CRLF endings, trailing tabs, and mixed line separators are easy
for editors, copy-paste, and git to silently normalize; these assertions
fail loudly when that happens.

Companion to tests/data/bed/.gitattributes which marks *.bed as binary.
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "bed"


def _read(rel: str) -> bytes:
    return (DATA_DIR / rel).read_bytes()


def test_happy_crlf_is_pure_crlf() -> None:
    data = _read("happy_crlf.bed")
    assert b"\r\n" in data, "happy_crlf.bed lost its CRLF endings"
    bare_lf = data.replace(b"\r\n", b"").count(b"\n")
    bare_cr = data.replace(b"\r\n", b"").count(b"\r")
    assert bare_lf == 0 and bare_cr == 0, "happy_crlf.bed must use CRLF only, not a mix"


def test_mixed_separators_fixture_actually_mixes() -> None:
    data = _read("mixed_line_separators.bed")
    assert b"\r\n" in data, "mixed-separator fixture lost its CRLF half"
    bare_lf = data.replace(b"\r\n", b"").count(b"\n")
    assert bare_lf >= 1, "mixed-separator fixture lost its bare-LF half"


def test_trailing_tab_fixture_has_tab_before_newline() -> None:
    data = _read("trailing_tab.bed")
    assert b"\t\n" in data, "trailing-tab fixture lost its \\t before \\n"
    assert data.count(b"\t\n") >= 2, "expected trailing tab on every data line"
    assert b"\r" not in data, "fixture should be LF-only; CRLF would mask the trailing-tab pathology"
