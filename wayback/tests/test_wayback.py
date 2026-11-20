"""Tests for wayback.py. Run: python3 -I tests/test_wayback.py"""

import gzip
import io
import os
import json
import ssl
import sys
import tempfile
import urllib.error
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import wayback as w  # noqa: E402

w.CACHE = Path(tempfile.mkdtemp(prefix="wbtest-cache-"))  # never touch the real cache


# ---------- transport


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


def test_429_gives_up_after_one_short_retry():
    """archive.org 429s this whole network for hours; the old ladder slept 75 s per call."""
    calls, sleeps = [], []

    def throttled(req, timeout=None):
        calls.append(req.full_url)
        raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {"Retry-After": "120"}, None)

    w.urllib.request.urlopen = throttled
    w.time.sleep = lambda s: sleeps.append(s)
    try:
        w.get("https://web.archive.org/cdx/search/cdx?url=example.com")
    except urllib.error.HTTPError as e:
        assert e.code == 429
    else:
        raise AssertionError("expected HTTPError")
    assert len(calls) == 2 and sum(sleeps) <= 5, (len(calls), sleeps)


def test_connection_cut_midread_is_retried_but_a_refused_handshake_is_not():
    """arquivo.pt drops SSL connections when history fetches overlap; that is transient."""
    assert w.tls_refused(urllib.error.URLError(ssl.SSLError(1, "tlsv1 alert access denied")))
    assert not w.tls_refused(urllib.error.URLError(ssl.SSLEOFError(8, "EOF occurred")))
    assert not w.tls_refused(urllib.error.URLError(ssl.SSLError(1, "UNEXPECTED_EOF_WHILE_READING")))


# ---------- keys and listing


def test_surt_matches_common_crawl_keys():
    cases = {
        "https://www.Example.com/a/": "com,example)/a",
        "example.com": "com,example)/",
        "http://x.com:8080/a?b=2&a=1": "com,x:8080)/a?a=1&b=2",
        "https://x.com//a/#frag": "com,x)//a",
    }
    for url, want in cases.items():
        assert w.surt(url) == want, (url, w.surt(url), want)


def test_captures_dedups_identical_payloads_across_archives():
    def fake(name, rows):
        return lambda url, frm=None, to=None, limit=None, domain=False: rows

    orig = dict(w.SOURCES)
    w.SOURCES.clear()
    w.SOURCES.update(
        ia=fake("ia", [("20200101000000", "20200101000000", "u", "text/html", "10", "DIGEST")]),
        cc=fake("cc", [("cc:20210101000000", "20210101000000", "u", "text/html", "10", "DIGEST"),
                       ("cc:20220101000000", "20220101000000", "u", "text/html", "11", "OTHER")]),
        pt=fake("pt", []),
    )
    try:
        rows = w.captures("u", sources=("ia", "cc", "pt"))
    finally:
        w.SOURCES.clear()
        w.SOURCES.update(orig)
    assert [r[0] for r in rows] == ["20200101000000", "cc:20220101000000"], rows


def test_pt_skips_wildcards_instead_of_returning_the_host_root():
    err = io.StringIO()
    with redirect_stderr(err):
        assert w.pt_captures("x.com/careers*") == []
    assert "exactly" in err.getvalue()


# ---------- discovery: full-text search and URL feeds


def test_arquivo_find_follows_pagination_and_dedups():
    pages = {
        "": {"response_items": [
            {"tstamp": "20200101000000", "originalURL": "https://x.com/a", "mimeType": "text/html"},
            {"tstamp": "20200101000000", "originalURL": "https://x.com/a", "mimeType": "text/html"},
            {"tstamp": "20210101000000", "originalURL": "https://x.com/b"},
        ], "next_page": "https://arquivo.pt/textsearch?q=x&offset=3"},
        "offset=3": {"response_items": [
            {"tstamp": "20220101000000", "originalURL": "https://x.com/c"},
        ]},
    }
    calls = []

    def fake_get(url, **kw):
        calls.append(url)
        key = "offset=3" if "offset=3" in url else ""
        return json.dumps(pages[key]).encode()

    orig = w.get
    w.get = fake_get
    try:
        rows = w.arquivo_find("x", limit=10)
    finally:
        w.get = orig
    assert [r[2] for r in rows] == ["https://x.com/a", "https://x.com/b", "https://x.com/c"], rows
    assert rows[0][3].startswith("https://arquivo.pt/wayback/20200101000000/")
    assert len(calls) == 2, calls


def test_discover_drops_tracking_urls_and_collapses_shapes():
    def fake_otx(host, limit):
        return [
            "https://info.x.com/unsubscribeConfirm/1/abcdefabcdefabcdef123456",
            "https://info.x.com/unsubscribeConfirm/2/zzzzzzzzzzzzzzzzzzzz999999",
            "https://x.com/track?utm_source=a",
            "https://x.com/pixel.gif",
            "https://x.com/careers/risk",
            "https://x.com/careers/risk2",
        ]

    orig = w.otx_urls
    w.CACHE = Path(w.tempfile.mkdtemp(prefix="wbdc-"))
    w.otx_urls = fake_otx
    try:
        rows = w.discover("x.com", ["otx"], 20)
    finally:
        w.otx_urls = orig
    urls = [u for u, _ in rows]
    assert "https://x.com/careers/risk" in urls
    assert not any("unsubscribe" in u or "pixel" in u or "utm_source" in u for u in urls), urls
    assert urls[0].endswith("/careers/risk"), urls  # shallow, query-free first


def test_discover_survives_one_dead_source():
    def dead(host, limit):
        raise urllib.error.URLError("boom")

    orig_otx, orig_us = w.otx_urls, w.urlscan_urls
    w.CACHE = Path(w.tempfile.mkdtemp(prefix="wbdc-"))
    w.otx_urls, w.urlscan_urls = dead, lambda h, n: ["https://x.com/ok"]
    err = io.StringIO()
    try:
        with redirect_stderr(err):
            rows = w.discover("x.com", ["otx", "urlscan"], 10)
    finally:
        w.otx_urls, w.urlscan_urls = orig_otx, orig_us
    assert rows == [("https://x.com/ok", "urlscan")], rows
    assert "otx: failed" in err.getvalue()


# ---------- HTML -> text


def test_charset_is_honoured_so_accents_survive():
    raw = '<meta charset="windows-1252"><p>Caf\xe9 Cr\xe8me \xa350k</p>'.encode("latin-1")
    full, _, _ = w._as_text(raw, "https://x.com/")
    assert "Café Crème £50k" in full, full


def test_charset_from_the_http_header_is_used_without_a_meta_tag():
    """Common Crawl hands the charset over from the WARC's Content-Type, Wayback and
    Arquivo.pt from the replay headers: same code path, no <meta> needed."""
    raw = "<p>Café Crème £50k</p>".encode("cp1252")
    full, _, _ = w._as_text(raw, "https://x.com/", "text/html; charset=windows-1252")
    assert "Café Crème" in full and "£50k" in full, full


def test_table_cells_and_links_are_kept_apart():
    raw = (b'<html><body><table><tr><td>Title</td><td>Salary</td></tr></table>'
           b'<p>See <a href="/apply?id=7">this ad</a></p></body></html>')
    text, _, links = w._as_text(raw, "https://x.com/jobs/1")
    assert "Title" in text and "Salary" in text
    assert "TitleSalary" not in text  # cells must not merge
    assert links and links[0].startswith("https://x.com/apply?id=7\t"), links


def test_base_href_is_used_to_resolve_links():
    raw = b'<head><base href="https://cdn.x.com/jobs/"></head><body><a href="a/1">ad</a></body>'
    _, _, links = w._as_text(raw, "https://x.com/careers/")
    assert links[0].startswith("https://cdn.x.com/jobs/a/1"), links


def test_script_and_style_text_stays_out():
    raw = b"<style>p{color:red}</style><script>var a=1</script><p>real</p>"
    full, _, _ = w._as_text(raw, "https://x.com/")
    assert full.strip() == "real", full


def test_crop_reports_which_regex_missed():
    text, warn = w.crop("a\nJob title: x\nb\n", r"^Job title:", r"^Apply")
    assert text.startswith("Job title:") and "--end not found" in warn


# ---------- main-content extraction


def nav_heavy_html(paragraph="Risk analyst wanted for the London desk."):
    nav = "".join(f'<li><a href="/{w}">{" ".join([w.title()] * 2)}</a></li>' for w in
                  ("services", "company", "insights", "careers", "contact"))
    return (f'<html><body><nav><ul>{nav}</ul></nav>'
            f'<p>{paragraph} We need someone who can run margin analytics and '
            'explain XVA to traders from a spreadsheet.</p>'
            '<p>Cookie policy and terms of use apply to this website.</p>'
            '<footer><p>Cookie policy and terms of use apply to this website.</p></footer>'
            '</body></html>').encode()


def test_lite_main_drops_menus_and_repeated_footer_blocks():
    full, main, _ = w._as_text(nav_heavy_html(), "https://x.com/", "", "builtin")
    assert "Services Services" in full, full          # the menu is in the raw text
    assert "Services Services" not in main, main      # ...and gone from the body
    assert "Risk analyst wanted" in main
    assert main.count("Cookie policy") == 1, main      # duplicate dropped, one kept
    assert len(main) < len(full)


def run_cli(argv):
    """Run the CLI in-process and return (stdout, stderr); no network is expected."""
    out, err = io.StringIO(), io.StringIO()
    w._ENGINE_NOTED = None  # the engine line prints once per process
    orig_argv, orig_out, orig_err = sys.argv, sys.stdout, sys.stderr
    sys.argv, sys.stdout, sys.stderr = ["wayback.py"] + argv, out, err
    try:
        w.main()
    finally:
        sys.argv, sys.stdout, sys.stderr = orig_argv, orig_out, orig_err
    return out.getvalue(), err.getvalue()


def test_diff_main_flag_drops_nav_and_caches_both_texts():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbdiff-"))
    a, b = d / "a.html", d / "b.html"
    a.write_bytes(nav_heavy_html("Risk analyst wanted for the London desk."))
    b.write_bytes(nav_heavy_html("Risk analyst wanted for the New York desk."))
    printed, err = run_cli(["diff", "https://x.com/j", str(a), str(b), "--main", "-o", str(d / "out")])
    assert "New York" in printed, printed
    assert "Company Company" not in printed, printed     # nav never reaches the diff
    assert list((d / "out").glob("a.main-*.txt")) and (d / "out" / "a.full.txt").exists()
    assert "main: " in err and "extraction" in err, err  # says which engine ran


def test_diff_without_main_keeps_the_raw_text():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbdiff-"))
    a, b = d / "a.html", d / "b.html"
    a.write_bytes(nav_heavy_html("Risk analyst wanted for the London desk."))
    b.write_bytes(nav_heavy_html("Risk analyst wanted for the New York desk."))
    printed, _ = run_cli(["diff", "https://x.com/j", str(a), str(b), "-o", str(d / "out")])
    assert "Company Company" in printed or "London" in printed


def test_engine_flag_forces_the_builtin_cut():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbeng-"))
    a, b = d / "a.html", d / "b.html"
    a.write_bytes(nav_heavy_html("Risk analyst wanted for the London desk."))
    b.write_bytes(nav_heavy_html("Risk analyst wanted for the New York desk."))
    printed, err = run_cli(["diff", "https://x.com/j", str(a), str(b), "--main",
                            "--engine", "builtin", "-o", str(d / "out")])
    assert "main: builtin extraction" in err, err
    assert "Company Company" not in printed, printed


def test_explicit_trafilatura_engine_fails_loudly_when_missing():
    orig_mod, orig_py = w._TRAFILATURA, w.TRAFILATURA_PY
    w._TRAFILATURA, w.TRAFILATURA_PY = None, "/nonexistent/python3"
    os.environ.pop("WAYBACK_TRAFILATURA_PATH", None)
    try:
        try:
            w.resolve_engine("trafilatura")
        except SystemExit as e:
            assert "trafilatura" in str(e.code) and "venv" in str(e.code), e.code
        else:
            raise AssertionError("expected a clean exit")
    finally:
        w._TRAFILATURA, w.TRAFILATURA_PY = orig_mod, orig_py


# ---------- word-level summary


def tmp_pair(a_text, b_text):
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbstat-"))
    (a := d / "a.txt").write_text(a_text)
    (b := d / "b.txt").write_text(b_text)
    return a, b


def test_word_stat_counts_content_words_and_skips_stopwords():
    a, b = tmp_pair("We need margin and margin for the desk.", "We need capital and margin for the desk.")
    stat = w.word_stat(a, b)
    assert "-1 margin" in stat and "+1 capital" in stat, stat
    assert "the" not in stat.split() and "and" not in stat.split(), stat


def test_word_stat_ignores_moved_words():
    """Same bag of words, different order: nothing was said differently."""
    a, b = tmp_pair("margin margin trade\n", "trade margin margin\n")
    assert w.word_stat(a, b) == ""


def test_word_stat_returns_empty_for_identical_texts():
    a, b = tmp_pair("one same paragraph\n", "one same paragraph\n")
    assert w.word_stat(a, b) == ""


def test_diff_stat_prints_both_diff_and_summary():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbstat-"))
    a, b = d / "a.html", d / "b.html"
    a.write_bytes(nav_heavy_html("Risk analyst wanted for the London desk."))
    b.write_bytes(nav_heavy_html("Risk analyst wanted for the New York desk."))
    printed, _ = run_cli(["diff", "https://x.com/j", str(a), str(b), "--main", "--stat", "-o", str(d / "o")])
    assert "diff --git" in printed and "-- word change --" in printed, printed
    assert "+1 york" in printed, printed


def test_diff_stat_only_drops_the_diff():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbstat-"))
    a, b = d / "a.html", d / "b.html"
    a.write_bytes(nav_heavy_html("Risk analyst wanted for the London desk."))
    b.write_bytes(nav_heavy_html("Risk analyst wanted for the New York desk."))
    printed, _ = run_cli(["diff", "https://x.com/j", str(a), str(b), "--main", "--stat-only", "-o", str(d / "o")])
    assert "diff --git" not in printed and "+1 york" in printed, printed


def test_history_stat_adds_a_net_summary():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbnet-"))
    nav = "Menu Home\nFooter legal"
    bodies = [f"{nav}\nWe need an analyst for margin work.",
              f"{nav}\nWe need an analyst for capital work.",
              f"{nav}\nWe need an analyst for xva work."]
    refs = [(f"r{i}", f"2020010{i}000000", "u", "text/html", "1", f"D{i}") for i in range(3)]
    orig_c, orig_l = w.captures, w.load
    texts = dict(zip([r[0] for r in refs], bodies))
    w.captures = lambda *a, **k: refs
    w.load = lambda url, ref, engine=None: (ref, b"x", texts[ref], None, [])
    try:
        printed, _ = run_cli(["history", "https://x.com/j", "--stat-only",
                              "--min-chars", "5", "-o", str(d)])
    finally:
        w.captures, w.load = orig_c, orig_l
    assert "===== net r0 -> r2 (3 versions) =====" in printed, printed
    assert "+1 xva" in printed and "-1 margin" in printed, printed


# ---------- cross-capture template filter


def test_template_lines_needs_every_capture():
    a = "Menu Home\nStanding copy here\nRisk analyst London."
    b = "Menu Home\nStanding copy here\nRisk analyst New York."
    c = "Menu Home\nStanding copy here\nRisk analyst Paris."
    tpl = w.template_lines([a, b, c])
    assert "menu home" in tpl and "standing copy here" in tpl
    assert not any("risk analyst" in k for k in tpl), tpl
    assert tpl["menu home"][1] == "Menu Home"  # original spelling kept for the report


def test_template_lines_is_off_below_three_captures():
    assert w.template_lines(["same", "same"]) == {}


def test_a_line_that_changed_once_is_not_template():
    """35 of 36 captures sharing a line must NOT make it template: that erases the change."""
    texts = ["old copy"] + ["new copy"] * 35
    tpl = w.template_lines(texts)
    assert "new copy" not in tpl and "old copy" not in tpl, tpl


def test_drop_template_counts_lines():
    tpl = {"menu": (3, "Menu")}
    text, dropped, seen = w.drop_template("Menu\nbody one\nbody two\n", tpl)
    assert text.strip() == "body one\nbody two" and dropped == 1 and seen == 3


def fake_history(tmp, bodies):
    """Run `history` with captures/load mocked out; bodies are the per-capture texts."""
    refs = [(f"r{i}", f"2020010{i}000000", "u", "text/html", "1", f"D{i}") for i in range(len(bodies))]
    orig_c, orig_l = w.captures, w.load
    texts = dict(zip([r[0] for r in refs], bodies))
    w.captures = lambda *a, **k: refs
    w.load = lambda url, ref, engine=None: (ref, b"<html></html>", texts[ref], None, [])
    try:
        return run_cli(["history", "https://x.com/j", "--min-chars", "5", "-o", str(tmp)])
    finally:
        w.captures, w.load = orig_c, orig_l


def test_history_drops_shared_lines_and_reports_them():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbtpl-"))
    nav = "Menu Home\nCookie settings\nFooter legal"
    bodies = [f"{nav}\nRisk analyst London desk."] * 2 + [f"{nav}\nRisk analyst New York desk."]
    printed, err = fake_history(d, bodies)
    assert "New York" in printed and "London" in printed, printed
    assert "Menu Home" not in printed, printed            # template never reaches the diff
    assert "template: dropped" in err, err
    assert (d / "template.txt").read_text().startswith("3\t"), (d / "template.txt").read_text()
    assert "Menu Home" not in (d / "r0.txt").read_text()


def test_history_refuses_to_filter_when_every_capture_is_identical():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbtpl-"))
    same = "Menu Home\nOne standing paragraph."
    printed, err = fake_history(d, [same] * 3)
    assert "nothing changed between them" in err, err
    assert (d / "r0.txt").read_text().strip(), "the text must stay on disk"


def test_history_keeps_template_lines_with_no_template():
    import tempfile as tf

    d = Path(tf.mkdtemp(prefix="wbtpl-"))
    nav = "Menu Home\nFooter legal"
    bodies = [f"{nav}\nOne."] * 2 + [f"{nav}\nTwo."]
    refs = [(f"r{i}", f"2020010{i}000000", "u", "text/html", "1", f"D{i}") for i in range(3)]
    orig_c, orig_l = w.captures, w.load
    texts = dict(zip([r[0] for r in refs], bodies))
    w.captures = lambda *a, **k: refs
    w.load = lambda url, ref, engine=None: (ref, b"x", texts[ref], None, [])
    try:
        printed, err = run_cli(["history", "https://x.com/j", "--no-template",
                            "--min-chars", "5", "-o", str(d)])
    finally:
        w.captures, w.load = orig_c, orig_l
    assert "Menu Home" in printed, printed
    assert "template" not in err.lower(), err


# ---------- Common Crawl ZipNum binary search, against a synthetic index


def make_index(entries, per_block=50):
    """entries: [(surt_key, ts, json_str)] -> (cluster.idx bytes, {filename: gz bytes}).
    Like the real index: one block holds many lines, and cluster.idx has one line per
    block, keyed by the block's first key."""
    idx, files = [], {}
    for b in range(0, len(entries), per_block):
        chunk = entries[b : b + per_block]
        fname = f"cdx-{b // per_block:05d}.gz"
        files[fname] = gzip.compress("".join(f"{k} {ts} {js}\n" for k, ts, js in chunk).encode())
        idx.append(f"{chunk[0][0]} {chunk[0][1]}\t{fname}\t0\t{len(files[fname])}\t1\n")
    return "".join(idx).encode(), files


def run_zipnum(entries, query):
    idx, files = make_index(entries)
    orig_range, orig_open = w._range, w.urllib.request.urlopen

    def fake_range(url, start, end):
        if url.endswith("cluster.idx"):
            return idx[start : end + 1]
        return files[url.rsplit("/", 1)[-1]][start : end + 1]

    class Head:
        headers = {"Content-Length": str(len(idx))}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    w._range = fake_range
    w.urllib.request.urlopen = lambda *a, **k: Head()
    try:
        return w.zipnum_rows("CC-MAIN-TEST", query)
    finally:
        w._range, w.urllib.request.urlopen = orig_range, orig_open


def test_zipnum_finds_an_exact_key_and_its_neighbours():
    entries = [(f"com,ex)/page{i:03d}", f"20250101{i:06d}", json.dumps({"url": f"https://ex.com/page{i:03d}", "status": "200"}))
               for i in range(400)]
    rows = run_zipnum(entries, "ex.com/page200")
    assert [r["url"] for r in rows] == ["https://ex.com/page200"], rows


def test_zipnum_prefix_sweep_returns_only_the_prefix():
    entries = [(f"com,ex)/job{i:03d}", f"20250101{i:06d}", json.dumps({"url": f"https://ex.com/job{i:03d}", "status": "200"}))
               for i in range(60)]
    entries += [(f"com,ex)/news{i:03d}", f"20250102{i:06d}", json.dumps({"url": f"https://ex.com/news{i:03d}", "status": "200"}))
                for i in range(60)]
    entries.sort()
    rows = run_zipnum(entries, "ex.com/job*")
    assert len(rows) == 60, len(rows)
    assert all("/job" in r["url"] for r in rows)
    assert run_zipnum(entries, "ex.com/job007") and len(run_zipnum(entries, "ex.com/job007")) == 1


def test_zipnum_missing_key_returns_nothing():
    entries = [(f"com,ex)/a{i:03d}", "20250101000000", json.dumps({"url": "u", "status": "200"})) for i in range(50)]
    assert run_zipnum(entries, "ex.com/zzz") == []


# ---------- listing cache


def test_listing_cache_answers_the_second_call_without_the_network():
    w.CACHE = Path(w.tempfile.mkdtemp(prefix="wbcache-"))
    calls = []

    def boom(*a, **k):
        calls.append(a)
        raise AssertionError("cache miss")

    key = ("test", "u", None, None, None, False)
    w.cached(key, lambda: [("ref", "ts", "u", "text/html", "1", "d")])
    assert w.cached(key, boom) == [("ref", "ts", "u", "text/html", "1", "d")]
    assert not calls


# ---------- audit 2026-11-19


def _http_error(code, retry_after):
    import email.message
    h = email.message.Message()
    h["Retry-After"] = retry_after
    return lambda req, timeout=None: (_ for _ in ()).throw(
        urllib.error.HTTPError(req.full_url, code, "x", h, io.BytesIO()))


def test_5xx_retry_after_is_capped():
    """A 503 with Retry-After: 3600 used to sleep for an hour."""
    sleeps = []
    w.urllib.request.urlopen, w.time.sleep = _http_error(503, "3600"), sleeps.append
    try:
        w.get("https://x/", tries=3)
    except urllib.error.HTTPError:
        pass
    assert sleeps and max(sleeps) <= w.MAX_WAIT, sleeps


def test_http_date_retry_after_does_not_crash():
    sleeps = []
    w.urllib.request.urlopen, w.time.sleep = _http_error(503, "Wed, 21 Oct 2026 07:28:00 GMT"), sleeps.append
    try:
        w.get("https://x/", tries=2)
    except urllib.error.HTTPError:
        pass
    assert len(sleeps) == 1 and 0 <= sleeps[0] <= w.MAX_WAIT, sleeps


def test_local_txt_keeps_its_lines_and_angle_brackets():
    d = Path(tempfile.mkdtemp())
    f = d / "today.txt"
    f.write_text("line one\nline two <b>\nline three\n")
    name, raw, full, main, links = w.load("x.com", str(f), "builtin")
    assert name == "today"
    assert full == "line one\nline two <b>\nline three\n", full
    assert main == full and links == []


def test_main_text_cache_is_per_engine():
    """A .main.txt left by the builtin cut must not answer a trafilatura run."""
    assert w.main_cache_name("20200101000000", "builtin") != w.main_cache_name("20200101000000", "trafilatura")


def test_tls_refusal_from_archive_org_marks_ia_blocked():
    w.CACHE = Path(tempfile.mkdtemp(prefix="wbblock-"))
    w.FRESH = True
    w.urllib.request.urlopen, w.time.sleep = refuse_tls([]), no_sleep
    orig = dict(w.SOURCES)
    w.SOURCES["pt"] = lambda *a, **k: []
    err = io.StringIO()
    try:
        with redirect_stderr(err):
            w.captures("example.com", sources=("ia", "pt"))
    finally:
        w.SOURCES.clear()
        w.SOURCES.update(orig)
        w.FRESH = False
    assert w.ia_blocked_until() > w.time.time(), err.getvalue()


def test_finished_cc_crawls_are_cached_for_good():
    w.CACHE = Path(tempfile.mkdtemp(prefix="wbcc-"))
    key = ("cc", "CC-MAIN-2020-05", "x.com")
    w.cached(key, lambda: [{"timestamp": "1"}], ttl=None)
    p = w.cache_path(*key)
    old = w.time.time() - 365 * 86400
    os.utime(p, (old, old))
    assert w.cached(key, lambda: (_ for _ in ()).throw(AssertionError("refetched")), ttl=None) == [{"timestamp": "1"}]
    assert w.cc_ttl({"id": "CC-MAIN-2020-05", "to": "2020-01-29"}) is None
    today = w.datetime.date.today().isoformat()
    assert w.cc_ttl({"id": "CC-MAIN-now", "to": today}) == w.CACHE_TTL


def test_live_ref_fetches_the_current_page():
    seen = []

    class R:
        headers = {"Content-Type": "text/html; charset=utf-8"}
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return b"<p>hello now</p>"

    def ok(req, timeout=None):
        seen.append(req.full_url)
        return R()

    w.urllib.request.urlopen = ok
    name, raw, full, main, links = w.load("x.com/a", "live", None)
    assert seen == ["https://x.com/a"], seen
    assert name.startswith("live-") and full == "hello now\n", (name, full)


def test_live_ref_points_at_the_cloudflare_skill_on_a_challenge():
    class R:
        headers = {"Content-Type": "text/html"}
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return b"<title>Just a moment...</title><script>_cf_chl_opt={}</script>"

    w.urllib.request.urlopen = lambda req, timeout=None: R()
    try:
        w.load("https://x.com/a", "live", None)
    except SystemExit as e:
        assert "cf text" in str(e.code), e.code
    else:
        raise AssertionError("expected a challenge exit")


# ---------- extra sources: ghostarchive, Megalodon, UK Web Archive


GH_PAGE = """<p>Page 1 out of 2</p><a href="/search?term=x&amp;page=1">Next Page</a><table>
<tr><td><img src="/img2/AAAAA.png"></td><td><a href="/archive/AAAAA">https://www.ex.com/news</a></td><td>Fri, 06 Nov 2026 10:26:45 GMT
</td><td>Archived webpage</td></tr>
<tr><td><img src="/img2/BBBBB.png"></td><td><a href="/archive/BBBBB">https://www.ex.com/news/story-1</a></td><td>Sun, 04 Oct 2026 15:43:44 GMT
</td><td>Archived webpage</td></tr></table>"""
GH_PAGE2 = """<p>Page 2 out of 2</p><table>
<tr><td></td><td><a href="/archive/CCCCC">http://ex.com/news/</a></td><td>Mon, 05 Jan 2015 08:00:00 GMT
</td><td>Archived webpage</td></tr></table>"""


def _pages(mapping):
    def fake_get(url, *a, **k):
        for key, body in mapping.items():
            if key in url:
                return body.encode()
        raise AssertionError(f"unexpected {url}")
    return fake_get


def test_ghostarchive_exact_url_filters_the_substring_search_and_follows_pages():
    orig = w.get
    w.get = _pages({"page=1": GH_PAGE2, "search?": GH_PAGE})
    try:
        rows = w.gh_captures("ex.com/news")
    finally:
        w.get = orig
    assert [r[0] for r in rows] == ["gh:CCCCC", "gh:AAAAA"], rows   # oldest first, story-1 dropped
    assert rows[1][1] == "20261106102645"


def test_ghostarchive_prefix_and_dates():
    orig = w.get
    w.get = _pages({"page=1": GH_PAGE2, "search?": GH_PAGE})
    try:
        rows = w.gh_captures("ex.com/news*", frm="2016")
    finally:
        w.get = orig
    assert [r[0] for r in rows] == ["gh:BBBBB", "gh:AAAAA"], rows


MG_PAGE = """<a href="https://megalodon.jp/2014-0518-1047-24/www.ex.com/" target="_top" id="fish1">x</a>
<a href="https://megalodon.jp/2008-0426-1214-51/www.ex.com/" target="_top" id="fish2">y</a>
<a href="https://megalodon.jp/2009-0101-0000-00/www.ex.com/other" target="_top">z</a>"""


def test_megalodon_lists_captures_of_the_exact_url():
    orig = w.get
    w.get = _pages({"megalodon.jp/?url=": MG_PAGE})
    try:
        rows = w.mg_captures("https://ex.com/")
    finally:
        w.get = orig
    assert [r[0] for r in rows] == ["mg:20080426121451", "mg:20140518104724"], rows
    assert rows[0][2] == "https://megalodon.jp/2008-0426-1214-51/www.ex.com/"


def test_list_only_refs_explain_instead_of_fetching():
    w.urllib.request.urlopen, w.time.sleep = _http_error(451, "0"), lambda s: None
    for ref, word in (("mg:20080426121451", "megalodon.jp"), ("uk:20100719142319", "reading room")):
        try:
            w.load("http://www.ex.com/", ref, None)
        except SystemExit as e:
            assert word in str(e.code), e.code
        else:
            raise AssertionError(ref)


def test_ghostarchive_warc_yields_the_page_record():
    body = b"<html><p>ghost copy</p></html>"
    http = b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n" + body

    def rec(kind, uri, payload):
        head = (f"WARC/1.0\r\nWARC-Type: {kind}\r\nWARC-Target-URI: {uri}\r\n"
                f"Content-Length: {len(payload)}\r\n\r\n").encode()
        return head + payload + b"\r\n\r\n"

    css = b"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\nbody{}"
    warc = rec("warcinfo", "", b"x: y") + rec("response", "https://ex.com/a.css", css) + rec("response", "https://ex.com/news", http)
    raw, ctype = w.warc_page(warc, "ex.com/news")
    assert raw == body and "text/html" in ctype


def test_history_drops_list_only_sources():
    assert w.fetchable(["ia", "gh", "mg", "uk"]) == ["ia", "gh"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
