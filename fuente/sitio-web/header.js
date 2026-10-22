(function () {
  'use strict';
  var root = document.getElementById('is2h');
  if (!root) return;
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var burger = document.getElementById('is2hBurger');
  var menu = document.getElementById('is2hMenu');
  var nav = document.getElementById('is2hNav');
  var pill = document.getElementById('is2hPill');
  var prog = document.getElementById('is2hProg');
  var links = nav ? Array.prototype.slice.call(nav.querySelectorAll('a')) : [];
  var open = false, lastY = window.pageYOffset, ticking = false;

  function onScroll() {
    var y = window.pageYOffset;
    root.classList.toggle('is2h-scrolled', y > 24);
    if (!open) {
      if (y > lastY + 6 && y > 520) root.classList.add('is2h-hidden');
      else if (y < lastY - 6 || y < 520) root.classList.remove('is2h-hidden');
    }
    var max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    if (prog) prog.style.transform = 'scaleX(' + Math.min(1, y / max).toFixed(4) + ')';
    lastY = y;
    ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* active section pill */
  function movePill(a) {
    if (!pill) return;
    if (!a) { pill.style.opacity = '0'; return; }
    pill.style.opacity = '1';
    pill.style.width = a.offsetWidth + 'px';
    pill.style.transform = 'translate3d(' + a.offsetLeft + 'px,0,0)';
  }
  var current = null;
  function setActive(id) {
    var a = null;
    links.forEach(function (l) { var on = l.getAttribute('href') === '#' + id; l.classList.toggle('is2h-active', on); if (on) a = l; });
    current = a;
    movePill(a);
  }
  if ('IntersectionObserver' in window) {
    var seen = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { seen[e.target.id] = e.isIntersecting; });
      var pick = null;
      links.forEach(function (l) { var id = l.getAttribute('href').slice(1); if (seen[id]) pick = id; });
      setActive(pick);
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach(function (l) { var t = document.getElementById(l.getAttribute('href').slice(1)); if (t) io.observe(t); });
  }
  window.addEventListener('resize', function () { movePill(current); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { movePill(current); });

  /* mobile menu */
  function setOpen(v) {
    open = v;
    root.classList.toggle('is2h-open', v);
    root.classList.remove('is2h-hidden');
    burger.setAttribute('aria-expanded', v ? 'true' : 'false');
    burger.setAttribute('aria-label', v ? 'Cerrar menú' : 'Abrir menú');
    menu.setAttribute('aria-hidden', v ? 'false' : 'true');
    document.documentElement.style.overflow = v ? 'hidden' : '';
    if (v) { var f = document.getElementById('is2hMenuNav'); if (f) setTimeout(function () { f.focus(); }, RM ? 0 : 350); }
    else burger.focus({ preventScroll: true });
  }
  if (burger && menu) {
    burger.addEventListener('click', function () { setOpen(!open); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a[href^="#"]')) { open = false; root.classList.remove('is2h-open'); burger.setAttribute('aria-expanded', 'false'); burger.setAttribute('aria-label', 'Abrir menú'); menu.setAttribute('aria-hidden', 'true'); document.documentElement.style.overflow = ''; } });
    document.addEventListener('keydown', function (e) {
      if (!open) return;
      if (e.key === 'Escape') { setOpen(false); return; }
      if (e.key === 'Tab') {
        var f = Array.prototype.slice.call(menu.querySelectorAll('a')).concat([burger]);
        var i = f.indexOf(document.activeElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
      }
    });
    window.addEventListener('resize', function () { if (open && window.innerWidth >= 1024) setOpen(false); });
  }
})();
