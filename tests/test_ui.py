"""Guards on the shared files. Run with `python3 -m unittest discover -s tests -t .`."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ui import statusui  # noqa: E402

CSS = (ROOT / "ui" / "base.css").read_text(encoding="utf-8")
JS = (ROOT / "ui" / "ui.js").read_text(encoding="utf-8")

# Every global ui.js defines. A consumer's test checks its own script against
# this list, so adding a name here is a deliberate act.
JS_GLOBALS = {
    "M3", "MFULL", "PARTIAL_NOTE",
    "esc", "slug", "monthLabel", "monthLabelLong", "num", "plural",
    "fmtDays", "fmtHours", "when", "monthTabs", "dayCells", "bindDayCaption",
    "cacheBust", "loadShard", "stampLine",
}


def js_globals(text):
    return set(re.findall(r"^(?:function|var)\s+(\w+)", text, re.M))


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

    def test_vendor_header_is_first(self):
        self.assertTrue(CSS.startswith("/* Vendored from baz8080/statusui"))
        self.assertTrue(JS.startswith("/* Vendored from baz8080/statusui"))


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
        sm = statusui.sitemap("https://x", ["c/a.html"], "2026-01-01")
        self.assertIn("<loc>https://x/c/a.html</loc>", sm)
        self.assertEqual(
            statusui.robots("https://x"),
            "User-agent: *\nAllow: /\nSitemap: https://x/sitemap.xml\n",
        )


if __name__ == "__main__":
    unittest.main()
