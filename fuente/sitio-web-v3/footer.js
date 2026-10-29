(function () {
  var root = document.getElementById('iv3f');
  if (!root) return;
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var y = document.getElementById('iv3fYear');
  if (y) y.textContent = new Date().getFullYear();

  function go(target) {
    if (window.iv3Lenis) window.iv3Lenis.scrollTo(target, { duration: 1.6 });
    else if (typeof target === 'number') window.scrollTo({ top: target, behavior: 'smooth' });
    else target.scrollIntoView({ behavior: 'smooth' });
  }
  var top = document.getElementById('iv3fTop');
  if (top) top.addEventListener('click', function () { go(0); });
  root.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var h = a.getAttribute('href');
    if (h.length < 2) return;
    var el = document.querySelector(h);
    if (!el) return;
    e.preventDefault(); go(el);
    if (history.replaceState) history.replaceState(null, '', h);
  });

  var word = document.getElementById('iv3fWord');
  if (word) {
    var txt = word.textContent, html = '';
    for (var i = 0; i < txt.length; i++) html += '<span class="' + (i >= 6 ? 'r' : '') + '" style="transition-delay:' + (i * 0.04).toFixed(2) + 's">' + txt.charAt(i) + '</span>';
    word.innerHTML = html;
    if (!RM && 'IntersectionObserver' in window) {
      root.classList.add('iv3f-js');
      new IntersectionObserver(function (es) { es.forEach(function (e) { word.classList.toggle('iv3f-in', e.isIntersecting); }); }, { threshold: 0.3 }).observe(word);
    }
  }
})();
