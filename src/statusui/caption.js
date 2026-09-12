/* statusui - the day-cell caption listener, on its own so a static page can
   inline it without the rest of ui.js. A page of day bars and nothing else
   interactive needs this one function; taking the whole bundle for it costs
   15 KB on every such page, and those pages are per place, per site.
   ui_js() carries this file too, so the app keeps every name it had. */
"use strict";

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
