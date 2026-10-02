"""Build helpers shared by the status sites.

Installed by each site as a uv git dependency pinned in its uv.lock; rollout.sh
moves the pins. Standard library only, Python 3.11: the consumers' floor.

The one that matters is `assemble`: it inlines base.css and ui.js into a page
template at the <!--UI-CSS--> and <!--UI-JS--> markers. Inlined, not linked,
because every page is entered cold from a search result and a shared
stylesheet would cost each of those readers a second request.

A page that calls one or two of them takes a narrower marker instead, and gets
that piece alone rather than 15 KB of app it never calls: <!--UI-JS-CAPTION-->
for the day-cell listener, <!--UI-JS-FRESH--> for the data-age line. A page that
wants both takes both markers. <!--UI-WAIT--> in <head> holds back a page's
[data-wait] elements until its script has drawn what goes above them.

Every page leaves `assemble` with the comments stripped from its inline <style>
and <script> blocks: on an app page they were a third of the gzipped HTML.
"""

from __future__ import annotations

import functools
import html
import json
import math
import re
import unicodedata
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

HERE = Path(__file__).parent
UI_CSS, UI_JS = "<!--UI-CSS-->", "<!--UI-JS-->"
UI_JS_CAPTION, UI_JS_FRESH = "<!--UI-JS-CAPTION-->", "<!--UI-JS-FRESH-->"
UI_WAIT = "<!--UI-WAIT-->"

# Self-contained, because it runs in <head> before ui.js exists. The load event
# is the fallback for a script that throws before calling pending(false), and the
# timer for a data file that stalls rather than fails.
# Once the page has called pending() its own timer is the net, so neither fires.
WAIT_HEAD = (
    "<script>(function(){var h=document.documentElement;"
    'function go(){if(!(window.pending&&pending.owned))h.classList.remove("wait")}'
    'h.classList.add("wait");addEventListener("load",go);setTimeout(go,8000)})()</script>'
)

MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)

# Monday-first, to index date.weekday() directly; ui.js's D3 is Sunday-first
# for getUTCDay, and the mirror test holds the two to the same output.
DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

# Said on a day cell built from part of a day. Plain words on purpose: it is
# read by someone wondering why their place looks quiet. Mirrored in ui.js.
PARTIAL_NOTE = " - only part of this day was recorded"


def base_css():
    return (HERE / "base.css").read_text(encoding="utf-8")


def ui_js():
    # ui.js first: a "use strict" directive is only a directive while nothing
    # precedes it. The newlines are load-bearing too, or a trailing line comment
    # eats the next file's first line.
    app = (HERE / "ui.js").read_text(encoding="utf-8")
    return "\n".join((app, freshness_js(), caption_js()))


def caption_js():
    """The day-cell caption listener alone, for a page that calls nothing else."""
    return (HERE / "caption.js").read_text(encoding="utf-8")


def freshness_js():
    """The data-age line alone, and the two helpers only it calls."""
    return (HERE / "freshness.js").read_text(encoding="utf-8")


def js_globals():
    """Every name the inlined script declares, for a consumer's redeclaration test.

    No argument, on purpose: a site that could pass its own source could pass
    the part of the bundle it already reads, look migrated, and still miss what
    the rest of it declares. There is one right answer and this is it.

    Ask here rather than parsing ui.js: the bundle is three files, and a site
    reading one of them would pass a script that shadows a name from another.

    One name per declaration is the rule this reads by, and a test holds the
    bundle to it: `var a = 1, b = 2;` would publish `a` and leave `b` guarding
    nothing.
    """
    return _declared(ui_js())


def _declared(js):
    """The names one script declares. The tests drive this over source the real
    bundle does not contain; a consumer has no reason to reach past js_globals."""
    return set(re.findall(r"^(?:function|var)\s+(\w+)", js, re.M))


def assemble(template, markers=None):
    """Fill a page template: the shared CSS and JS, then each <!--NAME--> in `markers`.

    Comments come out of the inline CSS and JS on the way, so nothing a page needs
    may live in one. HTML comments stay: a site may fill its own markers later.
    """
    page = (
        template.replace(UI_WAIT, WAIT_HEAD)
        .replace(UI_CSS, base_css())
        .replace(UI_JS, ui_js())
        .replace(UI_JS_CAPTION, caption_js())
        .replace(UI_JS_FRESH, freshness_js())
    )
    for name, text in (markers or {}).items():
        page = page.replace(f"<!--{name}-->", text)
    return strip_comments(page)


_JS_TOKEN = re.compile(r"""
  (?P<ws>[ \t\r\n]+)
| (?P<line>//[^\n]*)
| (?P<block>/\*.*?\*/)
| (?P<str>'(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*")
| (?P<tick>`)
| (?P<word>[A-Za-z_$][\w$]*|\d[\w.]*)
| (?P<slash>/)
| (?P<open>\{)
| (?P<close>\})
| (?P<punct>.)
""", re.X | re.S)
_TEMPLATE_TEXT = re.compile(r"(?:[^`\\$]|\\.|\$(?!\{))*", re.S)
_REGEX = re.compile(r"/(?:[^/\\\[\n]|\\.|\[(?:[^\]\\\n]|\\.)*\])+/[A-Za-z]*")
# A / after one of these opens a regex literal; after anything else it divides,
# except after the ) of `if (...)` and its kin, which is tracked separately.
_PAREN_STATEMENTS = {"if", "while", "for", "with"}
_BEFORE_REGEX = {
    "return", "typeof", "instanceof", "in", "of", "new", "delete", "void", "throw",
    "case", "do", "else", "yield", "await", *"(,=:[!&|?{};+-*%<>~^",
}
_CSS_TOKEN = re.compile(r"""
  (?P<ws>[ \t\r\n]+)
| (?P<block>/\*.*?\*/)
| (?P<str>'(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*")
| (?P<other>[^\s'"/]+|/)
""", re.X | re.S)
_REST_OF_LINE = re.compile(r"[ \t]*(?:\r?\n|$)")
_BLOCK = re.compile(r"(<(style|script)\b([^>]*)>)(.*?)(</\2>)", re.S | re.I)


def _drop_comment(out, src, start, end, css=False):
    """Drop src[start:end] from the output; returns where to carry on reading.

    A comment on a line of its own takes the line with it. One after code takes
    the spaces before it, and a block comment between two tokens leaves a space,
    or a newline if it spanned one, because to ASI that comment was a line break.
    """
    gap = ""
    while out and not out[-1].strip(" \t\r\n"):
        chunk = out.pop()
        if "\n" in chunk:
            cut = chunk.rindex("\n") + 1
            out.append(chunk[:cut])
            gap = chunk[cut:] + gap
            break
        gap = chunk + gap
    rest = _REST_OF_LINE.match(src, end)
    if (not out or out[-1].endswith("\n")) and rest:
        return rest.end()
    if "\n" in src[start:end]:
        out.append("\n")
    elif out and not rest and src[end:end + 1] not in (" ", "\t"):
        # JS reads a comment as a space (`a + /**/ +b` is not `a ++b`). CSS reads it as
        # nothing yet still ends a token (`.x/**/.y` is `.x.y`, `1px/**/-2px` is two),
        # which only an empty comment keeps
        out.append(gap or ("/**/" if css else " "))
    return end


def strip_js(src):
    """`src` without its comments, token for token the same script otherwise."""
    out, pos, prev, before = [], 0, None, None
    frames = [0]  # brace depth of each code frame; "`" marks a template literal
    parens = []  # whether each open ( heads a statement like `if (`
    while pos < len(src):
        if frames[-1] == "`":
            text = _TEMPLATE_TEXT.match(src, pos).group()
            out.append(text)
            pos += len(text)
            if src.startswith("${", pos):
                frames.append(0)
                out.append("${")
                pos += 2
            elif pos < len(src):
                frames.pop()
                out.append("`")
                pos, before, prev = pos + 1, prev, "`"
            continue
        m = _JS_TOKEN.match(src, pos)
        kind, text = m.lastgroup, m.group()
        if kind in ("line", "block"):
            pos = _drop_comment(out, src, pos, m.end())
            continue
        if kind == "slash" and (prev is None or prev in _BEFORE_REGEX):
            regex = _REGEX.match(src, pos)
            if regex:
                out.append(regex.group())
                pos, before, prev = regex.end(), prev, "/re/"
                continue
        out.append(text)
        pos = m.end()
        if kind == "ws":
            continue
        if text == "(":
            # not `arr.with(`, which is a call; `for await (` is a loop
            parens.append(prev in _PAREN_STATEMENTS and before != "."
                          or (prev, before) == ("await", "for"))
        elif text == ")" and parens and parens.pop():
            before, prev = prev, "("  # `if (x) /re/` is a statement then a regex
            continue
        if kind == "tick":
            frames.append("`")
        elif kind == "open":
            frames[-1] += 1
        elif kind == "close":
            if frames[-1] == 0 and len(frames) > 1:
                frames.pop()  # the } that closes a ${
                continue
            frames[-1] -= 1
        before, prev = prev, text
    return "".join(out)


def strip_css(src):
    out, pos = [], 0
    while pos < len(src):
        m = _CSS_TOKEN.match(src, pos)
        if m.lastgroup == "block":
            pos = _drop_comment(out, src, pos, m.end(), css=True)
            continue
        out.append(m.group())
        pos = m.end()
    return "".join(out)


@functools.lru_cache(maxsize=64)
def _strip_block(tag, body):
    return strip_css(body) if tag == "style" else strip_js(body)


def strip_comments(page):
    """Strip the comments from every inline <style> and classic <script> in `page`."""
    def one(m):
        tag, attrs = m.group(2).lower(), m.group(3)
        typed = re.search(r"\btype\s*=\s*['\"]?([\w/+.-]+)", attrs)
        data = tag == "script" and typed and typed.group(1) not in ("module", "text/javascript")
        if re.search(r"\bsrc\s*=", attrs) or data:
            return m.group()
        return m.group(1) + _strip_block(tag, m.group(4)) + m.group(5)
    return _BLOCK.sub(one, page)


def slug(name):
    """URL-safe, lowercase, fadas folded to ASCII rather than dropped."""
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "-" for c in folded.lower()).strip("-")


def month_label(ym):
    return f"{MONTH_NAMES[int(ym[5:7]) - 1]} {ym[:4]}"


def dumps(obj):
    # Default separators spend a byte on every comma and colon in the payload.
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def stamp(dt):
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def when(ts, year=False):
    """'2026-08-16T20:21' -> '16 Aug, 20:21', or with the year before the comma."""
    if not ts:
        return ""
    mon = MONTH_NAMES[int(ts[5:7]) - 1][:3]
    return f"{int(ts[8:10])} {mon}{' ' + ts[:4] if year else ''}, {ts[11:16]}"


def fmt_day(iso):
    """'2026-08-01' -> 'Sat 1 Aug': a date the way a reader says one; mirrors ui.js fmtDay."""
    d = date.fromisoformat(iso[:10])
    return f"{DAY_NAMES[d.weekday()]} {d.day} {MONTH_NAMES[d.month - 1][:3]}"


def fmt_date(iso, today):
    """fmt_day plus the year when it isn't `today`'s; mirrors ui.js fmtDate.

    `today` is the caller's clock (a date or ISO string), not the wall clock,
    so a page rebuilt later renders the same.
    """
    return fmt_day(iso) + ("" if iso[:4] == str(today)[:4] else f" {iso[:4]}")


def half_up(x):
    # JS Math.round rounds a .5 up; Python's round() goes to even. The pages
    # format the same figure on both sides, so they have to agree.
    return math.floor(x + 0.5)


def tenth(x):
    # JS toFixed rounds a tie up, "%.1f" goes to even, and x * 10 can cross a tie
    # that neither side sees; Decimal(float) is the double both are looking at.
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def days(n):
    if n < 2:
        return "1 day"
    if n < 60:
        return f"{n} days"
    return f"{tenth(n / 30.44)} months"


def hours(h, days_fmt=None):
    """Mirrors ui.js fmtHours; `days_fmt` formats the whole-days branch."""
    if h < 1:
        return f"{half_up(h * 60)} min"
    if h < 48:
        return f"{tenth(h)} h" if h < 10 else f"{half_up(h)} h"
    n = half_up(h / 24)
    if days_fmt:
        return days_fmt(n)
    return "1 day" if n == 1 else f"{n} days"


def day_cells(cells, ym, partial, labels, qualify=lambda ch: True):
    """The day bar for a static page: one <i> per cell, class b<ch>, caption in data-cap.

    `labels` maps a cell character to its caption text; `qualify` says whether a
    part-day suffix applies to that cell (no data and not-yet days take none).
    """
    out = []
    for i, ch in enumerate(cells):
        day = f"{ym}-{i + 1:02d}"
        cap = f"{fmt_day(day)}: {labels[ch]}"
        if qualify(ch) and day in partial:
            cap += PARTIAL_NOTE
        out.append(f'<i class="b{ch}" data-cap="{html.escape(cap)}"></i>')
    return "".join(out)


def sitemap(base_url, paths, lastmod):
    urls = "".join(
        f"<url><loc>{html.escape(f'{base_url}/{p}')}</loc><lastmod>{lastmod}</lastmod></url>"
        for p in paths
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>"
    )


def robots(base_url):
    return f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"


def size_report(site_dir, budget, pages_dir, pages_label, extra=()):
    """What a reader downloads before they touch anything, as (bytes, text).

    Printed on every build: the payload is the constraint these sites keep
    having to defend, and a regression belongs in the build log. `extra` is
    [(filename, note)] for on-demand files worth listing after the initial load.
    """
    site_dir = Path(site_dir)
    # A site that inlines its payload writes no data.js; one whose page still
    # names it, by src or as a lazily loaded script, must have written it.
    loads_data = '"data.js' in (site_dir / "index.html").read_text(encoding="utf-8")
    initial = {
        p: (site_dir / p).stat().st_size
        for p in ("index.html", "data.js")
        if p == "index.html" or loads_data or (site_dir / p).exists()
    }
    shards = sorted((site_dir / "h").glob("*.js"), key=lambda p: -p.stat().st_size)
    pages = list((site_dir / pages_dir).glob("*.html"))
    lines = [f"  {p:<16}{size / 1024:8.1f} KB" for p, size in initial.items()]
    lines.append(
        f"  {'initial load':<16}{sum(initial.values()) / 1024:8.1f} KB"
        f"   (budget {budget / 1024:.1f} KB)"
    )
    for name, note in extra:
        lines.append(f"  {name:<16}{(site_dir / name).stat().st_size / 1024:8.1f} KB   ({note})")
    lines.append(
        f"  {pages_label:<16}{sum(p.stat().st_size for p in pages) / 1024:8.1f} KB"
        f"   ({len(pages)} files)"
    )
    if shards:
        lines.append(
            f"  {'shards':<16}{sum(p.stat().st_size for p in shards) / 1024:8.1f} KB"
            f"   ({len(shards)} files, largest {shards[0].name} at"
            f" {shards[0].stat().st_size / 1024:.1f} KB)"
        )
    return sum(initial.values()), "\n".join(lines)
