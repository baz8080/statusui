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

/* --- the build stamp ----------------------------------------------------- */
// How far the data behind this page reaches. The build clock (D.generated)
// stays out of it: a reader cares where the record stops, not when the site
// was assembled. When the gap between the two grows, the stale flag says the
// collector has stopped rather than leaving the bars to read as a quiet week.
function stampLine(D) {
  return "Data to " + (D.stale ? '<span class="stale">' : "<span>") + esc(D.observed) +
    (D.stale ? " - collection has stopped" : "") + "</span>.";
}
