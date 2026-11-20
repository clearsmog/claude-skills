"""Tests for image_search.py. Run: python3 -I scripts/test_image_search.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import image_search as s  # noqa: E402


def fake_fetch(bad, dupes=()):
    def fetch(url, path, **kwargs):
        if url in bad:
            return None
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(b"x")
        return path

    return fetch


def _base(tmp):
    return str(Path(tmp) / "x.png")


def test_failed_candidate_falls_through_to_the_next(tmp):
    s.fetch_raster = fake_fetch({"u1"})
    s._dhash = lambda path, size=8: None
    assert s.download_first(["u1", "u2", "u3"], 1, _base(tmp)) == [_base(tmp)]


def test_numbered_files_have_no_gaps_and_stop_at_num(tmp):
    s.fetch_raster = fake_fetch({"u2"})
    s._dhash = lambda path, size=8: None
    saved = s.download_first(["u1", "u2", "u3", "u4"], 2, _base(tmp))
    assert [Path(p).name for p in saved] == ["x_1.png", "x_2.png"]


def test_all_candidates_failing_returns_nothing(tmp):
    s.fetch_raster = fake_fetch({"u1", "u2"})
    assert s.download_first(["u1", "u2"], 1, _base(tmp)) == []


def test_near_duplicates_are_dropped_and_replaced(tmp_path):
    s.fetch_raster = fake_fetch(set())
    s._dhash = lambda path, size=8: 0b1010
    saved = s.download_first(["u1", "u2"], 2, str(tmp_path / "x.png"))
    assert len(saved) == 1  # second hit hashes the same, so only one survives


def test_candidate_coerces_string_metadata():
    c = s.Candidate(url="u", engine="ddgs", width="1600", height="")
    assert c.width == 1600 and c.height is None and c.area == 0


def test_slugify_and_output_resolution():
    assert s.slugify("Golden Gate Bridge!") == "golden-gate-bridge"
    assert s.resolve_output(None, "images", "Golden Gate Bridge!") == \
        s.auto_filename("Golden Gate Bridge!", "images")
    assert s.resolve_output("pic", "images", "q") == "images/pic.png"
    assert s.resolve_output("a/b/pic.jpg", "images", "q") == "a/b/pic.jpg"


def test_brand_domain_prefers_wikidata(monkeypatch):
    monkeypatch.setattr(s, "wikidata_website", lambda name: "abc.xyz")
    assert s.resolve_domain("Alphabet Inc") == "abc.xyz"


def test_brand_domain_heuristic_when_wikidata_is_silent(monkeypatch):
    monkeypatch.setattr(s, "wikidata_website", lambda name: None)
    assert s.resolve_domain("Goldman Sachs") == "goldmansachs.com"


class _MP:
    """Minimal monkeypatch stand-in so the file runs without pytest."""

    def setattr(self, obj, attr, value):
        setattr(obj, attr, value)


if __name__ == "__main__":
    import inspect
    import tempfile

    for name, fn in list(globals().items()):
        if not name.startswith("test_"):
            continue
        kwargs = {}
        for param in inspect.signature(fn).parameters:
            if param in ("tmp", "tmp_path"):
                kwargs[param] = Path(tempfile.mkdtemp())
            elif param == "monkeypatch":
                kwargs[param] = _MP()
        fn(**kwargs)
        print("ok", name)
