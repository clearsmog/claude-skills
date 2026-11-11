"""Tests for wayback.py. Run: python3 -I tests/test_wayback.py"""

import ssl
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import wayback as w  # noqa: E402


def refuse_tls(calls):
    def urlopen(req, timeout=None):
        calls.append(req.full_url)
        raise urllib.error.URLError(ssl.SSLError(1, "tlsv1 alert access denied"))

    return urlopen


def no_sleep(seconds):
    raise AssertionError(f"slept {seconds}s on a refused TLS handshake")


def test_refused_tls_fails_at_once_without_retrying():
    calls = []
    w.urllib.request.urlopen, w.time.sleep = refuse_tls(calls), no_sleep
    try:
        w.get("https://web.archive.org/cdx/search/cdx?url=example.com")
    except urllib.error.URLError:
        pass
    else:
        raise AssertionError("expected URLError")
    assert len(calls) == 1


def test_save_reports_an_unreachable_archive_instead_of_a_traceback():
    w.urllib.request.urlopen, w.time.sleep = refuse_tls([]), no_sleep
    try:
        w.save("https://example.com/")
    except SystemExit as e:
        assert "archive.org" in str(e.code) and "archive.ph" in str(e.code)
    else:
        raise AssertionError("expected a clean exit")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
