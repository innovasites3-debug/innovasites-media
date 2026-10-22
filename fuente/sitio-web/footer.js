(function () {
  'use strict';
  var root = document.getElementById('is2f');
  if (!root) return;
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var year = document.getElementById('is2fYear');
  if (year) year.textContent = new Date().getFullYear();

  var top = document.getElementById('is2fTop');
  if (top) top.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: RM ? 'auto' : 'smooth' });
    var skip = document.querySelector('.is2h-skip, #inicio');
    if (skip) setTimeout(function () { try { (document.getElementById('inicio') || skip).focus({ preventScroll: true }); } catch (e) {} }, RM ? 0 : 800);
  });

  var clock = document.getElementById('is2fClock');
  if (clock) {
    var fmt = null;
    try { fmt = new Intl.DateTimeFormat('es-CO', { timeZone: 'America/Bogota', hour: '2-digit', minute: '2-digit', hour12: false }); } catch (e) {}
    var upd = function () { if (fmt) clock.textContent = fmt.format(new Date()); };
    upd();
    setInterval(upd, 20000);
  }

  var mark = document.getElementById('is2fMark');
  if (mark) {
    var spans = Array.prototype.slice.call(mark.querySelectorAll('span'));
    var fit = function () {
      mark.style.fontSize = '';
      var cs = getComputedStyle(mark);
      var avail = mark.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      var used = 0;
      spans.forEach(function (s) { used += s.getBoundingClientRect().width; });
      if (used > 0 && avail > 0) mark.style.fontSize = (parseFloat(cs.fontSize) * (avail / used) * 0.94).toFixed(2) + 'px';
    };
    fit();
    var t;
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(fit, 150); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    if (!RM && 'IntersectionObserver' in window) {
      root.classList.add('is2f-js');
      spans.forEach(function (s, i) { s.style.transitionDelay = (i * 0.045).toFixed(3) + 's'; });
      var io = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { mark.classList.add('is2f-in'); io.disconnect(); }
      }, { threshold: 0.35 });
      io.observe(mark);
    }
  }
})();
