/* statusui — shared browser helpers, inlined into each page by statusui.assemble().
   Plain globals, ES5, and nothing runs at load: the page calls what it needs.
   A site's own script must not redeclare any name defined here. */
"use strict";

var M3 = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
var MFULL = ["January","February","March","April","May","June",
             "July","August","September","October","November","December"];
var D3 = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
var PARTIAL_NOTE = " - only part of this day was recorded";

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}
function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, "-"); }
function monthLabel(ym) { return M3[+ym.slice(5, 7) - 1] + " " + ym.slice(0, 4); }
function monthLabelLong(ym) { return MFULL[+ym.slice(5, 7) - 1] + " " + ym.slice(0, 4); }
function num(n) { return n.toLocaleString("en-IE"); }
function plural(n, word) { return num(n) + " " + word + (n === 1 ? "" : "s"); }
function fmtDays(n) {
  if (n < 2) return "1 day";
  if (n < 60) return n + " days";
  return (n / 30.44).toFixed(1) + " months";
}
// `days` formats the whole-days branch; the default keeps days as days
function fmtHours(h, days) {
  if (h < 1) return Math.round(h * 60) + " min";
  if (h < 48) return h.toFixed(h < 10 ? 1 : 0) + " h";
  var n = Math.round(h / 24);
  return days ? days(n) : n + (n === 1 ? " day" : " days");
}
// "2026-08-16T20:21" -> "16 Aug, 20:21", or "16 Aug 2026, 20:21" with the year
function when(ts, withYear) {
  return +ts.slice(8, 10) + " " + M3[+ts.slice(5, 7) - 1] +
    (withYear ? " " + ts.slice(0, 4) : "") + ", " + ts.slice(11, 16);
}
// "2026-08-01" -> "Sat 1 Aug": a date the way a reader says one. The ISO
// string stays behind the scenes for sorting and comparisons.
function fmtDay(iso) {
  var d = new Date(iso.slice(0, 10) + "T00:00:00Z");
  return D3[d.getUTCDay()] + " " + d.getUTCDate() + " " + M3[d.getUTCMonth()];
}
// fmtDay plus the year, only when it isn't the year of `today` — the caller's
// clock as an ISO string, so a page rebuilt later renders the same.
function fmtDate(iso, today) {
  return fmtDay(iso) + (iso.slice(0, 4) === String(today).slice(0, 4) ? "" : " " + iso.slice(0, 4));
}

/* --- month tabs and day bars ------------------------------------------- */
// aria-pressed carries the .on state to screen readers, which otherwise hear
// five identical buttons with no way to tell which month is showing
function monthTabs(months, current, fn) {
  return months.map(function (m) {
    var on = m === current;
    return '<button class="' + (on ? "on" : "") + '" aria-pressed="' + on + '" onclick="' +
      fn + "('" + m + "')\">" + monthLabel(m) + "</button>";
  }).join("");
}

// scrollLeft rather than scrollIntoView(), which can scroll the page too.
function revealMonthTab(strip) {
  var on = strip && strip.querySelector("button.on");
  if (!on) return;
  var s = strip.getBoundingClientRect();
  var b = on.getBoundingClientRect();
  var pad = 16;
  if (b.left < s.left + pad) strip.scrollLeft += b.left - s.left - pad;
  else if (b.right > s.right - pad) strip.scrollLeft += b.right - s.right + pad;
}

// A rotate or window resize narrows the strip without re-rendering it, which
// leaves the selected tab stranded off the end. Hidden views measure zero, and
// re-render before they are shown anyway.
function bindMonthReveal() {
  window.addEventListener("resize", function () {
    var strips = document.querySelectorAll(".months");
    for (var i = 0; i < strips.length; i++) {
      if (strips[i].clientWidth) revealMonthTab(strips[i]);
    }
  });
}

// describe(cell, date) -> [cls, caption, qualify]; a day in `partial` gets the
// part-day suffix unless qualify is false. data-cap feeds the .daycap readout;
// no title — it would repeat that, late, and never on a phone.
function dayCells(cells, ym, describe, partial) {
  var out = "";
  for (var i = 0; i < cells.length; i++) {
    var date = ym + "-" + String(i + 1).padStart(2, "0");
    var d = describe(cells[i], date), cap = d[1];
    if (d[2] !== false && partial && partial.indexOf(date) !== -1) cap += PARTIAL_NOTE;
    out += '<i class="' + d[0] + '" data-cap="' + esc(cap) + '"></i>';
  }
  return out;
}

// One delegated listener at the document, because the bars re-render on every
// route and month change. pointerover covers a mouse; click covers touch.
// Touch pointerover is dropped: it fires on scroll-starts and on taps,
// filling the strip that (hover: none) hides while empty.
function bindDayCaption() {
  var show = function (e) {
    if (e.type === "pointerover" && e.pointerType === "touch") return;
    var cell = e.target.closest(".bar i[data-cap]");
    if (!cell) return;
    var host = cell.closest(".row, .card");
    var cap = host && host.querySelector(".daycap");
    if (cap) cap.textContent = cell.dataset.cap;
  };
  document.addEventListener("click", show);
  document.addEventListener("pointerover", show);
}

/* --- loading a per-place shard ------------------------------------------ */
// A query string on a file:// URL is part of the path, so cache-busting there
// would 404 the shard this mechanism exists to keep loadable.
function cacheBust(D) {
  return location.protocol === "file:" ? "" : "?v=" + encodeURIComponent(D.generated);
}

// Injected <script>, not fetch: the site has to work opened straight off disk,
// and fetch cannot read a file:// URL. state[key] goes "loading" -> "ok" |
// "error"; isLoaded() is the truth, because onload alone is not success — a
// file served but blocked, or truncated, loads without assigning anything.
function loadShard(state, key, src, isLoaded, done) {
  if (isLoaded() || state[key] === "loading") return done();
  state[key] = "loading";
  var s = document.createElement("script");
  s.src = src;
  var settled = false;
  var timer = setTimeout(finish, 10000);
  function finish() {
    if (settled) return;
    settled = true;
    clearTimeout(timer);
    state[key] = isLoaded() ? "ok" : "error";
    done();
  }
  s.onload = finish;
  s.onerror = finish;
  document.head.appendChild(s);
}

/* --- the place search ---------------------------------------------------- */
// Ranked hits for a place query against {county: [names]}: counties whose own
// name starts with q come first, then indexed names by how early they match,
// alphabetical within a rank, capped at 40 so one keystroke cannot render a
// thousand buttons. Pure, and lowercases q itself, so it is safe standalone.
function searchHits(q, counties, index) {
  q = q.toLowerCase();
  var hits = [];
  // Counties first, so typing a county name never buries it under the places
  // inside it.
  counties.forEach(function (c) {
    if (c.toLowerCase().indexOf(q) === 0) hits.push([c, c, 0]);
  });
  counties.forEach(function (c) {
    (index[c] || []).forEach(function (name) {
      var at = name.toLowerCase().indexOf(q);
      if (at !== -1) hits.push([name, c, at + 1]);
    });
  });
  hits.sort(function (a, b) { return a[2] - b[2] || a[0].localeCompare(b[0]); });
  // one button per place: a name that is also a prefix-ranked county (lifts
  // indexes each station under itself) would otherwise render twice
  var seen = {}, out = [];
  for (var i = 0; i < hits.length && out.length < 40; i++) {
    var key = hits[i][0] + "|" + hits[i][1];
    if (!seen[key]) {
      seen[key] = true;
      out.push([hits[i][0], hits[i][1]]);
    }
  }
  return out;
}

// The search box. The name index is the one payload that grows with the number
// of distinct places rather than with time, so it is fetched on the first
// keystroke instead of loading for every reader who never searches.
// opts: input and results are elements, counties an array of county names,
// src the index URL (already cache-busted), loaded() returns the
// {county: [names]} index or falsy, pick(county) navigates.
function bindSearch(opts) {
  var state = null, waiting = [];
  function ensure(then) {
    // an index already in place (preloaded, or from a prior bind) needs no fetch
    if (state !== "ok" && opts.loaded()) state = "ok";
    if (state === "ok") return then();
    // Queue rather than call straight back: a second keystroke arriving while
    // the index is still in flight would otherwise run the callback against
    // an index that has not landed and report the search as permanently
    // broken. loaded() is the truth, not onload — a file served but blocked,
    // or truncated, loads without assigning anything.
    waiting.push(then);
    if (state === "loading") return;
    state = "loading";
    var s = document.createElement("script");
    s.src = opts.src;
    var timer = setTimeout(finish, 10000);
    function finish() {
      clearTimeout(timer);
      state = opts.loaded() ? "ok" : "error";
      var q = waiting;
      waiting = [];
      q.forEach(function (fn) { fn(); });
    }
    s.onload = finish;
    s.onerror = finish;
    document.head.appendChild(s);
  }
  function show() {
    // The query is re-read rather than captured: a callback queued behind the
    // index load fires after the reader has typed more, and the newest query
    // is the one they are waiting on.
    var q = opts.input.value.trim();
    if (q.length < 2) { opts.results.hidden = true; return; }
    var idx = opts.loaded();
    opts.results.hidden = false;
    if (!idx) {
      opts.results.innerHTML = '<div class="none">Search is unavailable - try reloading.</div>';
      return;
    }
    var hits = searchHits(q, opts.counties, idx);
    opts.results.innerHTML = hits.length
      ? hits.map(function (h) {
          return '<button data-c="' + esc(h[1]) + '">' + esc(h[0]) +
            (h[0] === h[1] ? "" : ' <span class="rc">' + esc(h[1]) + "</span>") + "</button>";
        }).join("")
      : '<div class="none">Nothing matching “' + esc(q) + '”</div>';
  }
  opts.input.addEventListener("input", function () {
    if (opts.input.value.trim().length < 2) { opts.results.hidden = true; return; }
    if (state !== "ok") {
      opts.results.hidden = false;
      opts.results.innerHTML = '<div class="none">Searching…</div>';
    }
    ensure(show);
  });
  // data-c rather than an inline onclick: a name with an apostrophe would need
  // escaping twice over, and one delegated listener survives every re-render.
  opts.results.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-c]");
    if (!b) return;
    opts.input.value = "";
    opts.results.hidden = true;
    opts.pick(b.dataset.c);
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".search")) opts.results.hidden = true;
  });
}

/* --- how old the data is -------------------------------------------------- */
// "Data to 26 Aug, 06:04 UTC" asks the reader to do timezone arithmetic to
// answer the only question they had: is this current? An age answers it.
//
// A healthy overnight gap is a big number, and no wording makes a big number
// read as fine, so the warning past `staleHours` — not the wording — carries
// "something is wrong". Its absence is the reassurance, and it costs no words
// on a normal render. `note` is what having gone stale means on this site.
//
// Measured against the reader's clock, so a page served from cache says so.
function freshness(iso, staleHours, note) {
  var mins = Math.round((Date.now() - Date.parse(iso)) / 60000);
  // a wrong clock or a stale cache must never render as "in 20 minutes"
  if (mins < 2) return "Updated just now";
  // one unit all the way up, as every relative-time library does; rounded, not
  // floored, so the page never understates its own age
  var age;
  if (mins < 60) age = mins + " minutes ago";
  else if (mins < 1440) age = plural(Math.round(mins / 60), "hour") + " ago";
  else age = plural(Math.round(mins / 1440), "day") + " ago";
  // on the exact minutes, not the rounded age, or the warning fires early
  if (mins < staleHours * 60) return "Updated " + age;
  return '<span class="stale">Updated ' + age + " - " + esc(note) + "</span>";
}

/* --- the build stamp ----------------------------------------------------- */
// How far the data behind this page reaches. The build clock (D.generated)
// stays out of it: a reader cares where the record stops, not when the site
// was assembled. When the gap between the two grows, the stale flag says the
// collector has stopped rather than leaving the bars to read as a quiet week.
function stampLine(D) {
  return "Data to " + (D.stale ? '<span class="stale">' : "<span>") + esc(D.observed) +
    (D.stale ? " - collection has stopped" : "") + "</span>.";
}
