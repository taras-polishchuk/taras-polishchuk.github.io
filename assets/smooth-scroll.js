/* Inertial smooth scroll (Apple-like). Desktop pointer only. Keyboard, scrollbar
   and touch stay native. Skips nested scrollers (chat panel). Off under
   prefers-reduced-motion. No dependencies. */
(function () {
  if (!window.matchMedia('(pointer: fine)').matches) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var target = window.scrollY, current = target, raf = null, ease = 0.11;
  var max = function () { return document.documentElement.scrollHeight - window.innerHeight; };
  function clamp(v) { return Math.max(0, Math.min(max(), v)); }
  function tick() {
    current += (target - current) * ease;
    if (Math.abs(target - current) < 0.5) { current = target; window.scrollTo(0, current); raf = null; return; }
    window.scrollTo(0, current);
    raf = requestAnimationFrame(tick);
  }
  function start() { if (!raf) raf = requestAnimationFrame(tick); }
  function nestedScroller(el, dy) {
    while (el && el !== document.body && el !== document.documentElement) {
      var s = getComputedStyle(el);
      if (/(auto|scroll)/.test(s.overflowY) && el.scrollHeight > el.clientHeight + 1) {
        var atTop = el.scrollTop <= 0 && dy < 0, atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 1 && dy > 0;
        if (!atTop && !atBottom) return true;
      }
      el = el.parentElement;
    }
    return false;
  }
  window.addEventListener('wheel', function (e) {
    if (e.ctrlKey || e.defaultPrevented) return;
    if (e.target.closest && e.target.closest('#ai-assistant-root')) return;
    if (nestedScroller(e.target, e.deltaY)) return;
    var dy = e.deltaY;
    if (e.deltaMode === 1) dy *= 16; else if (e.deltaMode === 2) dy *= window.innerHeight;
    e.preventDefault();
    if (!raf) { current = window.scrollY; target = current; }
    target = clamp(target + dy);
    start();
  }, { passive: false });
  // Keep in sync when something else scrolls (keyboard, anchors, scrollbar).
  window.addEventListener('scroll', function () { if (!raf) { current = target = window.scrollY; } }, { passive: true });
  // Smooth anchors through the same engine.
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1); if (!id) return;
    var el = document.getElementById(id); if (!el) return;
    e.preventDefault();
    if (!raf) { current = window.scrollY; }
    target = clamp(el.getBoundingClientRect().top + window.scrollY - 16);
    start();
    history.pushState(null, '', '#' + id);
  });
  window.addEventListener('resize', function () { target = clamp(target); });
})();
