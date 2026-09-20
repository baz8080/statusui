/* statusui - how old the data is, on its own so a static page can inline it
   without the 15 KB of app it would otherwise cost. `num` and `plural` come
   with it because freshness is their only caller; ui_js() carries this file
   too, so the app keeps every name it had. */
"use strict";

function num(n) { return n.toLocaleString("en-IE"); }
function plural(n, word) { return num(n) + " " + word + (n === 1 ? "" : "s"); }

// A stamp asks the reader to do timezone arithmetic to answer the only
// question they had: is this current? Past `staleHours` the warning, not the
// wording, carries "something is wrong", and it hedges because the page cannot
// tell a stalled build from a stalled collector.
function freshness(iso, staleHours) {
  var mins = Math.round((Date.now() - Date.parse(iso)) / 60000);
  // a wrong clock or a stale cache must never render as "in 20 minutes"
  if (mins < 2) return "Updated just now";
  // rounded, not floored, so the page never understates its own age
  var age;
  if (mins < 60) age = mins + " minutes ago";
  else if (mins < 1440) age = plural(Math.round(mins / 60), "hour") + " ago";
  else age = plural(Math.round(mins / 1440), "day") + " ago";
  // on the exact minutes, not the rounded age, or the warning fires early
  if (mins < staleHours * 60) return "Updated " + age;
  return '<span class="stale">Updated ' + age +
    " - the last data build may have failed</span>";
}
