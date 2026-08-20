"""Guards on the shared files. Run with `python3 -m unittest discover -s tests -t .`."""

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import statusui  # noqa: E402

CSS = (ROOT / "src" / "statusui" / "base.css").read_text(encoding="utf-8")
JS = (ROOT / "src" / "statusui" / "ui.js").read_text(encoding="utf-8")

# Every global ui.js defines. A consumer's test checks its own script against
# this list, so adding a name here is a deliberate act.
JS_GLOBALS = {
    "M3", "MFULL", "PARTIAL_NOTE",
    "esc", "slug", "monthLabel", "monthLabelLong", "num", "plural",
    "fmtDays", "fmtHours", "when", "monthTabs", "revealMonthTab", "dayCells",
    "bindDayCaption", "bindMonthReveal",
    "cacheBust", "loadShard", "stampLine",
}


def js_globals(text):
    return set(re.findall(r"^(?:function|var)\s+(\w+)", text, re.M))


def scheme_tokens():
    """The hex-valued tokens as resolved in each scheme: (light, dark)."""
    hexes = r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})"
    light = dict(re.findall(hexes, re.search(r":root\s*\{(.*?)\}", CSS, re.S).group(1)))
    dark = re.search(r"prefers-color-scheme: dark\)\s*\{\s*:root\s*\{(.*?)\}", CSS, re.S)
    return light, {**light, **dict(re.findall(hexes, dark.group(1)))}


def contrast(fg, bg):
    def lum(hx):
        def chan(c):
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (chan(int(hx[i:i + 2], 16) / 255) for i in (1, 3, 5))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    a, b = lum(fg), lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


class TestCss(unittest.TestCase):
    def test_hidden_always_wins(self):
        # The one !important display rule is [hidden]; any other would be able
        # to beat it and un-hide a view container.
        bare = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
        important = re.findall(r"([^{}]+)\{[^{}]*display\s*:[^;{}]*!important", bare)
        self.assertEqual([s.strip() for s in important], ["[hidden]"])

    def test_tokens_are_declared_for_both_schemes(self):
        light = re.search(r":root\s*\{(.*?)\}", CSS, re.S).group(1)
        for tok in ("--page", "--surface", "--ink", "--muted", "--good", "--critical",
                    "--good-text", "--critical-text", "--row-cols", "--stats-cols"):
            self.assertIn(tok + ":", light)
        dark = re.search(r"prefers-color-scheme: dark\)\s*\{\s*:root\s*\{(.*?)\}", CSS, re.S)
        self.assertIsNotNone(dark)
        self.assertIn("--page:", dark.group(1))

    def test_header_names_the_source(self):
        # both files land inlined in consumer pages; the header is the only
        # pointer back to where an edit belongs
        self.assertTrue(CSS.startswith("/* statusui"))
        self.assertTrue(JS.startswith("/* statusui"))

    def test_text_tokens_pass_aa_contrast(self):
        # the header comment's claim, held to: every *-text hue reads as 4.5:1
        # text on both page and surface, in both schemes
        for tokens in scheme_tokens():
            for txt in ("--good-text", "--warning-text", "--serious-text", "--critical-text"):
                for bg in ("--page", "--surface"):
                    self.assertGreaterEqual(
                        contrast(tokens[txt], tokens[bg]), 4.5, f"{txt} on {bg}")

    def test_fills_that_carry_white_text_can(self):
        # .gradechip and the banner set white on these; B/C/D fills can't and
        # take dark lettering instead, which base.css hard-codes
        for tokens in scheme_tokens():
            for fill in ("--good", "--critical", "--severe", "--serious-deep"):
                self.assertGreaterEqual(contrast("#ffffff", tokens[fill]), 4.5, fill)


class TestJs(unittest.TestCase):
    def test_declares_exactly_the_documented_globals(self):
        self.assertEqual(js_globals(JS), JS_GLOBALS)

    def test_nothing_runs_at_load(self):
        # Top-level statements are declarations only: the page decides what to
        # call. A stray call here would run on every page that inlines the file.
        stripped = re.sub(r"/\*.*?\*/|//[^\n]*", "", JS, flags=re.S)
        depth, top, cont = 0, [], False
        for line in stripped.splitlines():
            if depth == 0 and line.strip() and not cont:
                top.append(line.strip())
            depth += line.count("{") - line.count("}")
            # a var initialiser may run on: it is over at the first semicolon
            cont = depth == 0 and bool(line.strip()) and not line.rstrip().endswith((";", "}"))
        for line in top:
            self.assertTrue(
                line.startswith(("function ", "var ", '"use strict"', "}")),
                f"top-level statement in ui.js: {line}",
            )

    def test_es5_syntax_only(self):
        bare = re.sub(r"/\*.*?\*/|//[^\n]*", "", JS, flags=re.S)
        self.assertNotIn("`", bare)
        self.assertNotIn("=>", bare)
        self.assertIsNone(re.search(r"\b(?:let|const)\b", bare))

    def test_month_names_mirror_python(self):
        mfull = re.search(r"var MFULL = \[(.*?)\];", JS, re.S).group(1)
        self.assertEqual(re.findall(r'"([^"]+)"', mfull), list(statusui.MONTH_NAMES))
        m3 = re.search(r"var M3 = \[(.*?)\];", JS).group(1)
        self.assertEqual(re.findall(r'"([^"]+)"', m3), [m[:3] for m in statusui.MONTH_NAMES])

    def test_partial_note_mirrors_python(self):
        note = re.search(r'var PARTIAL_NOTE = "(.*?)";', JS).group(1)
        self.assertEqual(note, statusui.PARTIAL_NOTE)


class TestPython(unittest.TestCase):
    def test_assemble_fills_every_marker(self):
        page = statusui.assemble(
            "<style><!--UI-CSS--></style><script><!--UI-JS--></script><!--X-->",
            {"X": "filled"},
        )
        self.assertIn(":root", page)
        self.assertIn("function bindDayCaption", page)
        self.assertTrue(page.endswith("filled"))
        self.assertNotIn("<!--", page.replace("<!--UI", ""))

    def test_hours_mirrors_the_js(self):
        self.assertEqual(statusui.hours(0.5), "30 min")
        self.assertEqual(statusui.hours(2.5), "2.5 h")
        self.assertEqual(statusui.hours(12.5), "13 h")  # half up, like Math.round
        self.assertEqual(statusui.hours(72), "3 days")
        self.assertEqual(statusui.hours(72, statusui.days), "3 days")
        self.assertEqual(statusui.hours(24 * 90, statusui.days), "3.0 months")

    def test_when(self):
        self.assertEqual(statusui.when("2026-08-16T20:21"), "16 Aug, 20:21")
        self.assertEqual(statusui.when("2026-08-06T09:05", year=True), "6 Aug 2026, 09:05")
        self.assertEqual(statusui.when(None), "")

    def test_day_cells_qualify_and_escape(self):
        out = statusui.day_cells(
            "09", "2026-08", {"2026-08-01", "2026-08-02"},
            {"0": "a & b", "9": "to come"}, qualify=lambda ch: ch not in "89",
        )
        self.assertIn('class="b0" data-cap="2026-08-01: a &amp; b — only part', out)
        self.assertIn('class="b9" data-cap="2026-08-02: to come"', out)

    def test_slug_folds_fadas(self):
        self.assertEqual(statusui.slug("Dún Laoghaire"), "dun-laoghaire")
        # per-character, as the live URLs were built; a run of punctuation keeps its dashes
        self.assertEqual(statusui.slug("Rush and Lusk"), "rush-and-lusk")
        self.assertEqual(statusui.slug("-Laois-"), "laois")

    def test_sitemap_and_robots(self):
        sm = statusui.sitemap("https://x", ["c/a.html", "d&n.html"], "2026-01-01")
        self.assertIn("<loc>https://x/c/a.html</loc>", sm)
        self.assertIn("<loc>https://x/d&amp;n.html</loc>", sm)
        self.assertEqual(
            statusui.robots("https://x"),
            "User-agent: *\nAllow: /\nSitemap: https://x/sitemap.xml\n",
        )

    def test_hours_boundaries(self):
        self.assertEqual(statusui.hours(0.02), "1 min")
        self.assertEqual(statusui.hours(0.99), "59 min")
        self.assertEqual(statusui.hours(1), "1.0 h")
        self.assertEqual(statusui.hours(2.25), "2.3 h")  # toFixed rounds a tie up
        self.assertEqual(statusui.hours(1.15), "1.1 h")  # ... but 1.15 is a hair under one
        self.assertEqual(statusui.hours(9.96), "10.0 h")
        self.assertEqual(statusui.hours(10), "10 h")
        self.assertEqual(statusui.hours(47.9), "48 h")
        self.assertEqual(statusui.hours(48), "2 days")
        self.assertEqual(statusui.hours(60), "3 days")  # 2.5 days, half up

    def test_days_boundaries(self):
        self.assertEqual(statusui.days(0), "1 day")
        self.assertEqual(statusui.days(1), "1 day")
        self.assertEqual(statusui.days(2), "2 days")
        self.assertEqual(statusui.days(59), "59 days")
        self.assertEqual(statusui.days(60), "2.0 months")

    def test_half_up_mirrors_math_round(self):
        self.assertEqual(statusui.half_up(2.5), 3)  # round() would give 2
        self.assertEqual(statusui.half_up(-0.5), 0)
        self.assertEqual(statusui.half_up(-1.5), -1)

    def test_month_label(self):
        self.assertEqual(statusui.month_label("2026-01"), "January 2026")
        self.assertEqual(statusui.month_label("2025-12"), "December 2025")

    def test_dumps_is_compact_and_keeps_fadas(self):
        self.assertEqual(statusui.dumps({"a": ["é", 1]}), '{"a":["é",1]}')

    def test_stamp(self):
        self.assertEqual(statusui.stamp(datetime(2026, 8, 16, 20, 21)), "2026-08-16 20:21 UTC")

    def test_size_report(self):
        with tempfile.TemporaryDirectory() as td:
            site = Path(td)
            (site / "index.html").write_bytes(b"x" * 1024)
            (site / "data.js").write_bytes(b"y" * 2048)
            (site / "h").mkdir()
            (site / "h" / "big.js").write_bytes(b"z" * 512)
            (site / "h" / "small.js").write_bytes(b"z" * 256)
            (site / "pages").mkdir()
            (site / "pages" / "a.html").write_bytes(b"p" * 100)
            (site / "notes.txt").write_bytes(b"n" * 300)
            total, text = statusui.size_report(
                site, 4096, "pages", "pages", extra=[("notes.txt", "on demand")])
        self.assertEqual(total, 3072)
        self.assertIn("(budget 4.0 KB)", text)
        self.assertIn("largest big.js", text)
        self.assertIn("(1 files)", text)
        self.assertIn("on demand", text)

    def test_size_report_without_shards(self):
        with tempfile.TemporaryDirectory() as td:
            site = Path(td)
            (site / "index.html").write_bytes(b"x")
            (site / "data.js").write_bytes(b"y")
            (site / "pages").mkdir()
            total, text = statusui.size_report(site, 4096, "pages", "pages")
        self.assertEqual(total, 2)
        self.assertNotIn("shards", text)

    def test_python_39_floor(self):
        # best-effort: the parser rejects syntax the consumers' 3.9 can't read
        src = (ROOT / "src" / "statusui" / "__init__.py").read_text(encoding="utf-8")
        ast.parse(src, feature_version=(3, 9))


@unittest.skipUnless(shutil.which("node"), "node not available")
class TestMirror(unittest.TestCase):
    """Run ui.js under node and hold each paired formatter to identical output.

    slug is deliberately unpaired: the Python one folds fadas and trims edge
    dashes for the static URLs; the JS one does neither.
    """

    HOURS = [0.02, 0.5, 0.99, 1, 1.15, 1.25, 1.45, 2.25, 2.5, 8.95, 9.94, 9.96, 10,
             12.5, 23.5, 36, 47.9, 48, 60, 72, 24 * 90, 24 * 365]
    DAYS = [0, 1, 2, 59, 60, 61, 365]
    WHEN = ["2026-08-16T20:21", "2026-01-06T09:05", "2025-12-31T23:59"]

    @classmethod
    def setUpClass(cls):
        harness = JS + f"""
var hoursIn = {json.dumps(cls.HOURS)}, daysIn = {json.dumps(cls.DAYS)};
var whenIn = {json.dumps(cls.WHEN)};
console.log(JSON.stringify({{
  hours: hoursIn.map(function (h) {{ return fmtHours(h); }}),
  hoursAsDays: hoursIn.map(function (h) {{ return fmtHours(h, fmtDays); }}),
  days: daysIn.map(fmtDays),
  when: whenIn.map(function (t) {{ return when(t); }}),
  whenYear: whenIn.map(function (t) {{ return when(t, true); }}),
  months: whenIn.map(function (t) {{ return monthLabelLong(t.slice(0, 7)); }}),
  cells: dayCells("09", "2026-08", function (ch, date) {{
    return ["b" + ch, date + ": " + ({{0: "quiet day", 9: "to come"}})[ch], ch !== "9"];
  }}, ["2026-08-01", "2026-08-02"]),
}}));
"""
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        cls.js = json.loads(run.stdout)

    def test_hours(self):
        self.assertEqual(self.js["hours"], [statusui.hours(h) for h in self.HOURS])
        self.assertEqual(
            self.js["hoursAsDays"], [statusui.hours(h, statusui.days) for h in self.HOURS])

    def test_days(self):
        self.assertEqual(self.js["days"], [statusui.days(n) for n in self.DAYS])

    def test_when(self):
        self.assertEqual(self.js["when"], [statusui.when(t) for t in self.WHEN])
        self.assertEqual(self.js["whenYear"], [statusui.when(t, year=True) for t in self.WHEN])

    def test_month_label(self):
        self.assertEqual(self.js["months"], [statusui.month_label(t[:7]) for t in self.WHEN])

    def test_day_cells(self):
        py = statusui.day_cells(
            "09", "2026-08", {"2026-08-01", "2026-08-02"},
            {"0": "quiet day", "9": "to come"}, qualify=lambda ch: ch != "9")
        self.assertEqual(self.js["cells"], py)


if __name__ == "__main__":
    unittest.main()
