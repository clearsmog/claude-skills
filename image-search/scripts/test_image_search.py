"""Tests for image_search.py. Run: python3 -I scripts/test_image_search.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import image_search as s  # noqa: E402


def fake_download(bad):
    def download(url, path):
        return None if url in bad else path

    return download


def test_failed_candidate_falls_through_to_the_next():
    s.download_image = fake_download({"u1"})
    assert s.download_first(["u1", "u2", "u3"], 1, "images/x.png") == ["images/x.png"]


def test_numbered_files_have_no_gaps_and_stop_at_num():
    s.download_image = fake_download({"u2"})
    saved = s.download_first(["u1", "u2", "u3", "u4"], 2, "images/x.png")
    assert saved == ["images/x_1.png", "images/x_2.png"]


def test_all_candidates_failing_returns_nothing():
    s.download_image = fake_download({"u1", "u2"})
    assert s.download_first(["u1", "u2"], 1, "images/x.png") == []


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
