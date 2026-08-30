"""Guards on the shared files. Run with `python3 -m unittest discover -s tests -t .`."""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import statusui  # noqa: E402

CSS = (ROOT / "src" / "statusui" / "base.css").read_text(encoding="utf-8")
# What a page inlines at <!--UI-JS-->, which is both JS files: every rule below
# holds for the bundle, wherever a name lives in it.
JS = statusui.ui_js()
CAPTION = statusui.caption_js()

# Every global the bundle defines. A consumer's test checks its own script
# against statusui.js_globals(), so adding a name here is a deliberate act.
JS_GLOBALS = {
    "M3", "MFULL", "D3", "PARTIAL_NOTE",
    "esc", "slug", "monthLabel", "monthLabelLong", "num", "plural",
    "fmtDays", "fmtHours", "when", "fmtDay", "fmtDate", "monthTabs",
    "revealMonthTab", "dayCells", "bindDayCaption", "bindMonthReveal",
    "cacheBust", "loadShard", "freshness", "stampLine",
    "searchHits", "bindSearch",
}


def js_globals(text):
    return set(re.findall(r"^(?:function|var)\s+(\w+)", text, re.M))


def scheme_tokens():
    """The hex-valued tokens as resolved in each scheme: (light, dark)."""
    hexes = r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})"
    light = dict(re.findall(hexes, re.search(r":root\s*\{(.*?)\}", CSS, re.S).group(1)))
    dark = re.search(r"prefers-color-scheme: dark\)\s*\{\s*:root\s*\{(.*?)\}", CSS, re.S)
    return light, {**light, **dict(re.findall(hexes, dark.group(1)))}


def chip_rules():
    """Each .g-* chip as (letter, fill expression, text colour expression)."""
    rules = {}
    # anchored, so the .chead size override for .g-none is not read as a chip
    for sel, body in re.findall(r"(?m)^\.g-([A-Za-z]+)\s*\{([^}]*)\}", CSS):
        fill = re.search(r"background:\s*([^;]+)", body)
        text = re.search(r"color:\s*([^;!]+)", body)
        rules[sel] = (fill.group(1).strip(), text.group(1).strip() if text else "#fff")
    return rules


def resolve(expr, tokens):
    """A chip's colour expression as a hex string.

    Handles the three forms base.css uses: a literal, a var(), and the one
    color-mix() the B chip is built from.
    """
    expr = expr.strip()
    if expr.startswith("#"):
        return expr if len(expr) == 7 else "#" + "".join(c * 2 for c in expr[1:])
    mix = re.match(r"color-mix\(in srgb,\s*(.+?)\s+(\d+)%,\s*(.+?)\)$", expr)
    if mix:
        a = resolve(mix.group(1), tokens)
        b = resolve(mix.group(3), tokens)
        pct = int(mix.group(2)) / 100
        return "#" + "".join(
            f"{round(int(a[i:i + 2], 16) * pct + int(b[i:i + 2], 16) * (1 - pct)):02x}"
            for i in (1, 3, 5))
    var = re.match(r"var\((--[\w-]+)\)$", expr)
    if var:
        return tokens[var.group(1)]
    raise AssertionError(f"unhandled colour expression: {expr}")


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

    def test_the_drill_down_sub_line_is_shared(self):
        # All three sites put a link to the page's permanent URL on this line,
        # so the rule that styles it belongs here rather than in three copies.
        self.assertIn(".chead + .sub", CSS)

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

    def test_every_grade_chip_can_be_read(self):
        chips = chip_rules()
        for tokens in scheme_tokens():
            for letter, (fill, text) in chips.items():
                ratio = contrast(resolve(text, tokens), resolve(fill, tokens))
                self.assertGreaterEqual(ratio, 4.5, f"g-{letter} letter on its fill")

    def test_the_scale_runs_a_to_f_inclusive(self):
        # A scale that skips E is an American-ism, and these sites are Irish.
        # A site emits `gradechip g-<letter>` straight from its own band table,
        # so a letter with no fill here renders as white on nothing.
        self.assertEqual(set(chip_rules()), set("ABCDEF") | {"none"})


class TestJs(unittest.TestCase):
    def test_declares_exactly_the_documented_globals(self):
        self.assertEqual(js_globals(JS), JS_GLOBALS)

    def test_the_published_set_is_the_whole_bundles(self):
        """What consumers assert against. Parsing ui.js instead - which all three
        did before the split - would drop bindDayCaption and let a site redeclare
        it unnoticed."""
        self.assertEqual(statusui.js_globals(), JS_GLOBALS)
        self.assertIn("bindDayCaption", statusui.js_globals())

    def test_the_caption_bundle_is_the_listener_and_nothing_else(self):
        """A static page takes this instead of the whole file, so anything that
        drifts into it is inlined on every place page of every site."""
        self.assertEqual(js_globals(CAPTION), {"bindDayCaption"})
        self.assertLess(len(CAPTION), 2000, "the caption bundle has grown a body")

    def test_the_bundle_is_the_app_and_the_caption(self):
        self.assertTrue(JS.endswith(CAPTION))
        # a directive is only a directive while nothing precedes it
        self.assertEqual(JS.splitlines()[3], '"use strict";')

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
        # A class declaration as much as let and const: not ES5, and a binding
        # neither js_globals() nor a vm context records, so a consumer
        # redeclaring the name would take the whole inlined script down. Matched
        # as a declaration, because `class` is also an HTML attribute the bar
        # builders write into strings all day.
        self.assertIsNone(re.search(r"\bclass\s+[A-Za-z_$]", bare))

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

    def test_a_page_can_take_the_caption_without_the_app(self):
        page = statusui.assemble("<script><!--UI-JS-CAPTION--></script>")
        self.assertIn("function bindDayCaption", page)
        self.assertNotIn("function loadShard", page)
        self.assertNotIn("<!--UI-JS", page)

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
        self.assertIn('class="b0" data-cap="Sat 1 Aug: a &amp; b - only part', out)
        self.assertIn('class="b9" data-cap="Sun 2 Aug: to come"', out)

    def test_fmt_day(self):
        self.assertEqual(statusui.fmt_day("2026-08-01"), "Sat 1 Aug")
        self.assertEqual(statusui.fmt_day("2026-08-16T20:21"), "Sun 16 Aug")
        self.assertEqual(statusui.fmt_date("2026-08-01", "2026-08-25"), "Sat 1 Aug")
        self.assertEqual(statusui.fmt_date("2025-12-31", "2026-08-25"), "Wed 31 Dec 2025")
        self.assertEqual(statusui.fmt_date("2025-12-31", date(2025, 12, 31)), "Wed 31 Dec")

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


@unittest.skipUnless(shutil.which("node"), "node not available")
class TestPublishedGlobals(unittest.TestCase):
    """Hold js_globals() to what a JavaScript engine actually declares.

    Consumers get their redeclaration guard from that function, and it reads
    the bundle with a regex - one name per declaration, column zero. Every
    cheaper check of that assumption was itself a regex over JavaScript, and
    the first one shipped here was fooled by the quotes inside esc()'s
    /[&<>"']/g. So the assumption is checked against an engine instead: run the
    bundle in a bare context and ask which names it left behind.

    A context records `var` and `function` bindings, which is the same shape
    js_globals() reads for; lexical declarations would be invisible to both,
    and test_es5_syntax_only is what keeps them out of the file.
    """

    @staticmethod
    def declared(js):
        harness = f"""
const vm = require("vm");
const ctx = {{}};
vm.createContext(ctx);
vm.runInContext({json.dumps(js)}, ctx);
console.log(JSON.stringify(Object.keys(ctx)));
"""
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        return set(json.loads(run.stdout))

    def test_the_regex_agrees_with_an_engine(self):
        self.assertEqual(statusui.js_globals(), self.declared(statusui.ui_js()))

    def test_a_second_name_on_one_line_is_caught_rather_than_dropped(self):
        """The failure this exists for: js_globals() would publish `zqA` and
        say nothing about `zqB`, leaving a consumer free to shadow it."""
        doctored = statusui.ui_js() + "\nvar zqA = 1, zqB = 2;\n"
        engine = self.declared(doctored)
        self.assertIn("zqB", engine)
        # the shipped parser, not a copy of its regex: a copy would agree with
        # whatever this test was written against rather than with the function
        self.assertEqual(statusui._declared(doctored), engine - {"zqB"})


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
  fmtDay: whenIn.map(fmtDay),
  fmtDate: whenIn.map(function (t) {{ return fmtDate(t, "2026-08-25"); }}),
  months: whenIn.map(function (t) {{ return monthLabelLong(t.slice(0, 7)); }}),
  cells: dayCells("09", "2026-08", function (ch, date) {{
    return ["b" + ch, fmtDay(date) + ": " + ({{0: "quiet day", 9: "to come"}})[ch], ch !== "9"];
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

    def test_fmt_day(self):
        self.assertEqual(self.js["fmtDay"], [statusui.fmt_day(t) for t in self.WHEN])
        self.assertEqual(
            self.js["fmtDate"], [statusui.fmt_date(t, "2026-08-25") for t in self.WHEN])

    def test_month_label(self):
        self.assertEqual(self.js["months"], [statusui.month_label(t[:7]) for t in self.WHEN])

    def test_day_cells(self):
        py = statusui.day_cells(
            "09", "2026-08", {"2026-08-01", "2026-08-02"},
            {"0": "quiet day", "9": "to come"}, qualify=lambda ch: ch != "9")
        self.assertEqual(self.js["cells"], py)


@unittest.skipUnless(shutil.which("node"), "node not available")
class TestSearchHits(unittest.TestCase):
    """searchHits is the pure half of the search box; bindSearch is DOM-only."""

    COUNTIES = ["Carlow", "Cork", "Dublin"]
    INDEX = {
        "Cork": ["Ballincollig", "Carrigaline", "Cobh"],
        "Dublin": ["Balbriggan", "Dún Laoghaire", "Swords"],
        "Carlow": ["Tullow"],
    }

    def hits(self, q):
        harness = JS + f"""
console.log(JSON.stringify(searchHits({json.dumps(q)},
  {json.dumps(self.COUNTIES)}, {json.dumps(self.INDEX)})));
"""
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_a_county_prefix_outranks_the_towns_inside_it(self):
        self.assertEqual(
            self.hits("co"),
            [["Cork", "Cork"], ["Cobh", "Cork"], ["Ballincollig", "Cork"]])

    def test_earlier_matches_rank_higher_and_ties_go_alphabetical(self):
        self.assertEqual(
            self.hits("ba"),
            [["Balbriggan", "Dublin"], ["Ballincollig", "Cork"]])

    def test_the_query_is_lowercased_inside(self):
        self.assertEqual(self.hits("DÚN"), [["Dún Laoghaire", "Dublin"]])

    def test_a_place_indexed_under_itself_renders_once(self):
        # lifts keys each station under its own name, so a prefix hit and a
        # substring hit are the same place
        harness = JS + """
console.log(JSON.stringify(searchHits("co", ["Cork"], {"Cork": ["Cork", "Cobh"]})));
"""
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout), [["Cork", "Cork"], ["Cobh", "Cork"]])

    def test_a_pair_yields_a_triple_and_a_string_yields_a_pair(self):
        # the mixed index is the real one: a site indexes names it has a page
        # for beside names it does not
        harness = JS + """
console.log(JSON.stringify(searchHits("na", ["Kildare"],
  {"Kildare": [["Naas", "naas"], "Nass Road"]})));
"""
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(
            json.loads(run.stdout),
            [["Naas", "Kildare", "naas"], ["Nass Road", "Kildare"]])

    def test_a_targeted_name_that_is_also_a_county_still_dedups(self):
        harness = JS + """
console.log(JSON.stringify(searchHits("co", ["Cork"],
  {"Cork": [["Cork", "cork"], "Cobh"]})));
"""
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        # the county hit wins the key, so the county's own row stays targetless
        self.assertEqual(json.loads(run.stdout), [["Cork", "Cork"], ["Cobh", "Cork"]])

    def test_hits_are_capped_at_forty(self):
        harness = JS + """
var index = {"Cork": []};
for (var i = 0; i < 60; i++) index.Cork.push("Place " + String(i).padStart(2, "0"));
console.log(JSON.stringify(searchHits("place", ["Cork"], index).length));
"""
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout), 40)


@unittest.skipUnless(shutil.which("node"), "node not available")
class TestBindSearch(unittest.TestCase):
    """The dropdown, against a DOM shim carrying only what bindSearch touches.

    What is worth guarding is the contract the sites lean on: a hit with a
    target is a real link, and pick() returning true is how a site keeps one in
    the app anyway.
    """

    SHIM = """
function El(tag) {
  this.tag = tag; this.dataset = {}; this.listeners = {};
  this.innerHTML = ""; this.hidden = false; this.value = "";
}
El.prototype.addEventListener = function (t, fn) {
  (this.listeners[t] = this.listeners[t] || []).push(fn);
};
El.prototype.contains = function (el) { return el && el.inBox !== false; };
global.document = {
  head: { appendChild: function () {} },
  createElement: function (t) { return new El(t); },
  activeElement: null,
  addEventListener: function () {}
};
global.setTimeout = function () { return 0; };
global.clearTimeout = function () {};
"""

    BIND = """
var input = new El("input"), results = new El("div"), picked = null;
document.activeElement = input;
bindSearch({
  input: input, results: results, counties: ["Kildare"], src: "",
  loaded: function () { return {Kildare: [["Naas", "naas"], "Sallins Road"]}; },
  href: function (c, t) {
    return t ? "a/" + slug(c) + "/" + t + ".html" : "c/" + slug(c) + ".html";
  },
  pick: function (c, t) { picked = [c, t || null]; return !t; }
});
function click(c, t, ev) {
  var el = new El("a"); el.dataset = {c: c, t: t}; var prevented = false;
  var e = {target: {closest: function () { return el; }},
           preventDefault: function () { prevented = true; }};
  for (var k in (ev || {})) e[k] = ev[k];
  if (ev && ev.outside) el.inBox = false;
  results.listeners.click[0](e);
  return prevented;
}
"""

    def run_js(self, body):
        harness = JS + self.SHIM + self.BIND + body
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_a_hit_with_a_target_is_a_real_link(self):
        html = self.run_js("""
input.value = "na"; input.listeners.input[0]();
console.log(JSON.stringify(results.innerHTML));
""")
        self.assertIn('<a href="a/kildare/naas.html"', html)
        self.assertIn('data-t="naas"', html)

    def test_no_href_option_leaves_the_hits_as_buttons(self):
        html = self.run_js("""
var i2 = new El("input"), r2 = new El("div");
document.activeElement = i2;
bindSearch({
  input: i2, results: r2, counties: ["Kildare"], src: "",
  loaded: function () { return {Kildare: ["Sallins Road"]}; },
  pick: function () {}
});
i2.value = "sallins"; i2.listeners.input[0]();
console.log(JSON.stringify(r2.innerHTML));
""")
        # lifts supplies no href, and must keep exactly the markup it had
        self.assertIn("<button", html)
        self.assertNotIn("<a href", html)

    def test_a_modified_click_on_a_link_is_left_to_the_browser(self):
        out = self.run_js("""
picked = null;
var prevented = click("Kildare", "naas", {metaKey: true});
console.log(JSON.stringify([prevented, picked]));
""")
        # a new-tab click must not clear the box or route the current one
        self.assertEqual(out, [False, None])

    def test_a_modified_click_still_picks_where_there_is_no_link(self):
        """lifts supplies no href, so its hits are buttons: there is nothing for
        the browser to follow and swallowing the click would just break it."""
        out = self.run_js("""
var i2 = new El("input"), r2 = new El("div"), got = null;
document.activeElement = i2;
bindSearch({
  input: i2, results: r2, counties: ["Kildare"], src: "",
  loaded: function () { return {Kildare: ["Sallins Road"]}; },
  pick: function (c) { got = c; }
});
var el = new El("button"); el.dataset = {c: "Kildare"};
r2.listeners.click[0]({
  target: {closest: function () { return el; }},
  ctrlKey: true, preventDefault: function () {}
});
console.log(JSON.stringify(got));
""")
        self.assertEqual(out, "Kildare")

    def test_a_click_resolving_outside_the_dropdown_is_ignored(self):
        """closest() lost its `button` qualifier when hits became links, so an
        unmatched click could otherwise climb out of the box entirely."""
        out = self.run_js("""
picked = null;
click("Kildare", "naas", {outside: true});
console.log(JSON.stringify(picked));
""")
        self.assertIsNone(out)

    def test_pick_returning_true_suppresses_the_link(self):
        out = self.run_js("""
var countyHit = click("Kildare", undefined);
var areaHit = click("Kildare", "naas");
console.log(JSON.stringify([countyHit, areaHit, picked]));
""")
        # the county hit stays in the app; the area hit is allowed to navigate
        self.assertEqual(out, [True, False, ["Kildare", "naas"]])


@unittest.skipUnless(shutil.which("node"), "node not available")
class TestFreshness(unittest.TestCase):
    """freshness() has no Python twin, so it is exercised under node directly."""

    NOTE = "collection has stopped"
    STALE = '<span class="stale">Updated %s - ' + NOTE + "</span>"
    # (minutes before "now", staleHours, expected)
    CASES = [
        (-20, 16, "Updated just now"),          # a reader's clock running fast
        (0, 16, "Updated just now"),
        (1, 16, "Updated just now"),
        (2, 16, "Updated 2 minutes ago"),
        (59, 16, "Updated 59 minutes ago"),
        (60, 16, "Updated 1 hour ago"),
        (719, 16, "Updated 12 hours ago"),      # 11h59m rounds up, never down
        (959, 16, "Updated 16 hours ago"),      # the age rounds to 16h ...
        (960, 16, STALE % "16 hours ago"),          # ... but only 16h exactly is overdue
        (1439, 24, "Updated 24 hours ago"),     # one unit all the way up
        (1440, 24, STALE % "1 day ago"),
        (4320, 24, STALE % "3 days ago"),
    ]

    def test_cases(self):
        cases = json.dumps([[m, h] for m, h, _ in self.CASES])
        harness = JS + f"""
Date.now = function () {{ return Date.parse("2026-08-26T12:00:00Z"); }};
console.log(JSON.stringify({cases}.map(function (c) {{
  return freshness(new Date(Date.now() - c[0] * 60000).toISOString(), c[1],
                   {json.dumps(self.NOTE)});
}})));
"""
        run = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout), [want for _, _, want in self.CASES])


if __name__ == "__main__":
    unittest.main()
