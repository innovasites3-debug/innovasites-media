(function () {
  var root = document.getElementById('iv3h');
  if (!root) return;
  var bar = document.getElementById('iv3hBar');
  var prog = document.getElementById('iv3hProg');
  var burger = document.getElementById('iv3hBurger');
  var menu = document.getElementById('iv3hMenu');
  var links = Array.prototype.slice.call(document.querySelectorAll('#iv3hNav a'));
  var open = false, lastY = 0, ticking = false;

  function scrollToHash(hash) {
    var el = document.querySelector(hash);
    if (!el) return false;
    if (window.iv3Lenis) window.iv3Lenis.scrollTo(el, { offset: 0, duration: 1.4 });
    else el.scrollIntoView({ behavior: 'smooth' });
    if (history.replaceState) history.replaceState(null, '', hash);
    return true;
  }

  function setOpen(v) {
    open = v;
    root.classList.toggle('iv3h-open', v);
    bar.classList.remove('iv3h-hide');
    burger.setAttribute('aria-expanded', v ? 'true' : 'false');
    burger.setAttribute('aria-label', v ? 'Cerrar menú' : 'Abrir menú');
    menu.setAttribute('aria-hidden', v ? 'false' : 'true');
    if (window.iv3Lenis) { if (v) window.iv3Lenis.stop(); else window.iv3Lenis.start(); }
    document.documentElement.style.overflow = v ? 'hidden' : '';
  }

  burger.addEventListener('click', function () { setOpen(!open); });
  document.addEventListener('keydown', function (e) { if (open && e.key === 'Escape') { setOpen(false); burger.focus(); } });

  root.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var hash = a.getAttribute('href');
    if (hash.length < 2) return;
    if (open) setOpen(false);
    if (scrollToHash(hash)) e.preventDefault();
  });

  function update() {
    ticking = false;
    var y = window.pageYOffset || document.documentElement.scrollTop;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    prog.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
    bar.classList.toggle('iv3h-solid', y > 40);
    var canHide = window.innerWidth > 900;
    if (!canHide) bar.classList.remove('iv3h-hide');
    else {
      if (!open) bar.classList.toggle('iv3h-hide', y > lastY + 4 && y > 400);
      if (y < lastY - 4) bar.classList.remove('iv3h-hide');
    }
    lastY = y;
    var mid = window.innerHeight * 0.4, on = null;
    links.forEach(function (a) {
      var s = document.querySelector(a.getAttribute('href'));
      if (!s) return;
      var r = s.getBoundingClientRect();
      if (r.top <= mid && r.bottom > mid) on = a;
    });
    links.forEach(function (a) { a.classList.toggle('iv3h-on', a === on); });
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  window.addEventListener('resize', update);
  update();
})();
