(function () {
  'use strict';
  var root = document.getElementById('is2');
  if (!root) return;
  root.classList.add('is2-js');

  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FINE = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (id) { return document.getElementById(id); };
  var qa = function (sel, el) { return Array.prototype.slice.call((el || root).querySelectorAll(sel)); };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var safe = function (fn) { try { fn(); } catch (e) { if (window.console) console.error('[is2]', e); } };

  /* ======================= pixel bitmaps ======================= */
  var PX = {
    web: ['###########', '#.........#', '#.**.###..#', '#.........#', '#.####.**.#', '#.........#', '###########', '....###....', '..#######..'],
    social: ['###########', '#.........#', '#..*.*.*..#', '#.........#', '#.#####...#', '#.........#', '###.#######', '..##.......', '..#........'],
    photo: ['..###......', '###########', '#.........#', '#...###.*.#', '#..#...#..#', '#..#.*.#..#', '#..#...#..#', '#...###...#', '###########'],
    video: ['###########', '#.........#', '#...*.....#', '#...**....#', '#...***...#', '#...**....#', '#...*.....#', '#.........#', '###########'],
    apps: ['..#######..', '..#.....#..', '..#.**..#..', '..#.....#..', '..#.*.*.#..', '..#.....#..', '..#.###.#..', '..#..*..#..', '..#######..'],
    brand: ['.....*.....', '....***....', '###########', '.#########.', '..#######..', '...#####...', '..###.###..', '.##.....##.', '#.........#'],
    doc: ['#######..', '#.....##.', '#.***..##', '#.......#', '#.#####.#', '#.......#', '#.####..#', '#.......#', '#########'],
    build: ['#########', '#...#...#', '#.*.#.*.#', '#########', '#.......#', '#.#####.#', '#.......#', '#.***...#', '#########'],
    rocket: ['....#....', '...###...', '...#*#...', '...###...', '..#####..', '.##.#.##.', '.#..#..#.', '...*.*...', '..*...*..'],
    cup: ['...*.*.....', '..*.*......', '...........', '########...', '#......###.', '#......#.#.', '#......###.', '.#....#....', '..####.....']
  };
  PX.chat = PX.social;

  function pxSVG(name, opts) {
    var map = PX[name];
    if (!map) return '';
    opts = opts || {};
    var w = map[0].length, h = map.length, out = [];
    var base = opts.base || 'currentColor', acc = opts.accent || '#FF5A45';
    var n = 0;
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) {
        var c = map[y].charAt(x);
        if (c === '.') continue;
        var d = opts.anim ? ' style="--d:' + (((x + y) * 0.028) + ((n * 7) % 5) * 0.01).toFixed(3) + 's"' : '';
        out.push('<rect x="' + (x + 0.06) + '" y="' + (y + 0.06) + '" width=".88" height=".88" fill="' + (c === '*' ? acc : base) + '"' + d + '/>');
        n++;
      }
    }
    return '<svg class="is2-pxi" viewBox="0 0 ' + w + ' ' + h + '" aria-hidden="true" focusable="false">' + out.join('') + '</svg>';
  }

  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function artSVG(glyph, seed, num) {
    var r = rng(seed), W = 400, H = 300, g = 20, out = [];
    out.push('<rect width="' + W + '" height="' + H + '" fill="#11141B"/>');
    for (var y = 0; y < H; y += g) {
      for (var x = 0; x < W; x += g) {
        var v = r();
        if (v < 0.11) out.push('<rect x="' + (x + 2) + '" y="' + (y + 2) + '" width="' + (g - 4) + '" height="' + (g - 4) + '" fill="#E5342A" opacity="' + (0.07 + r() * 0.3).toFixed(2) + '"/>');
        else if (v < 0.135) out.push('<rect x="' + (x + 2) + '" y="' + (y + 2) + '" width="' + (g - 4) + '" height="' + (g - 4) + '" fill="#FFFFFF" opacity="' + (0.05 + r() * 0.08).toFixed(2) + '"/>');
      }
    }
    var map = PX[glyph] || PX.web, mw = map[0].length, mh = map.length, cell = 18;
    var ox = Math.round((W - mw * cell) / 2), oy = Math.round((H - mh * cell) / 2);
    var shadow = [], front = [];
    for (var yy = 0; yy < mh; yy++) {
      for (var xx = 0; xx < mw; xx++) {
        var c = map[yy].charAt(xx);
        if (c === '.') continue;
        var px = ox + xx * cell, py = oy + yy * cell;
        shadow.push('<rect x="' + (px + 7) + '" y="' + (py + 7) + '" width="' + (cell - 2) + '" height="' + (cell - 2) + '" fill="#7A1712"/>');
        front.push('<rect x="' + px + '" y="' + py + '" width="' + (cell - 2) + '" height="' + (cell - 2) + '" fill="' + (c === '*' ? '#FF5A45' : '#FFFFFF') + '"/>');
      }
    }
    out.push(shadow.join(''), front.join(''));
    if (num) out.push('<text x="22" y="' + (H - 22) + '" fill="#6B7180" font-family="Space Mono, monospace" font-size="13" letter-spacing="2">' + num + '</text>');
    return '<svg viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">' + out.join('') + '</svg>';
  }

  qa('[data-px]').forEach(function (el) { el.innerHTML = pxSVG(el.getAttribute('data-px'), { anim: true }); });

  /* ======================= start gate (after preloader) ======================= */
  var started = false, startFns = [];
  function onStart(fn) { if (started) safe(fn); else startFns.push(fn); }
  function start() {
    if (started) return;
    started = true;
    document.documentElement.style.overflow = '';
    startFns.forEach(safe);
  }

  /* ======================= preloader ======================= */
  safe(function () {
    var pre = $('is2Pre');
    if (!pre) { start(); return; }
    var num = $('is2PreNum'), pxBox = $('is2PrePx'), word = $('is2PreWord');
    var N = 24, cells = [];
    for (var i = 0; i < N; i++) { var b = document.createElement('b'); pxBox.appendChild(b); cells.push(b); }
    var order = cells.map(function (c, i) { return i; });
    var rr = rng(7);
    for (var k = order.length - 1; k > 0; k--) { var j = Math.floor(rr() * (k + 1)); var t = order[k]; order[k] = order[j]; order[j] = t; }
    var words = ['Diseño web', 'Branding', 'Redes sociales', 'Fotografía', 'Video', 'Apps a medida'];
    var seen = false;
    try { seen = sessionStorage.getItem('is2Seen') === '1'; sessionStorage.setItem('is2Seen', '1'); } catch (e) {}
    var minT = RM ? 150 : (seen ? 450 : 1500), maxT = 4500;
    var loaded = document.readyState === 'complete';
    window.addEventListener('load', function () { loaded = true; });
    document.documentElement.style.overflow = 'hidden';
    var t0 = performance.now(), shown = 0, lit = 0, wi = 0, lastWord = t0, done = false;

    function finish() {
      if (done) return;
      done = true;
      num.textContent = '100';
      cells.forEach(function (c) { c.classList.add('on'); });
      pre.classList.add('is2-pre-line');
      setTimeout(function () { pre.classList.add('is2-pre-out'); }, RM ? 0 : 260);
      setTimeout(start, RM ? 0 : 520);
      setTimeout(function () { pre.classList.add('is2-pre-gone'); }, RM ? 50 : 1500);
    }
    function tick(now) {
      if (done) return;
      var el = now - t0;
      var target = loaded ? 100 : Math.min(90, (el / minT) * 90);
      if (el > maxT) target = 100;
      shown = Math.min(target, shown + Math.max(0.5, (target - shown) * 0.09));
      var v = Math.floor(shown);
      num.textContent = String(v);
      var want = Math.floor((v / 100) * N);
      while (lit < want) { cells[order[lit]].classList.add('on'); lit++; }
      if (now - lastWord > 420) { wi = (wi + 1) % words.length; word.textContent = words[wi]; lastWord = now; }
      if (shown >= 99.5 && el >= minT) { finish(); return; }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    setTimeout(finish, maxT + 1200);
  });

  /* ======================= grain ======================= */
  safe(function () {
    var g = $('is2Grain');
    if (!g || RM) return;
    var c = document.createElement('canvas');
    c.width = c.height = 160;
    var x = c.getContext('2d');
    if (!x) return;
    var d = x.createImageData(160, 160);
    for (var i = 0; i < d.data.length; i += 4) {
      var v = Math.random() * 255;
      d.data[i] = d.data[i + 1] = d.data[i + 2] = v;
      d.data[i + 3] = 255;
    }
    x.putImageData(d, 0, 0);
    g.style.backgroundImage = 'url(' + c.toDataURL('image/png') + ')';
  });

  /* ======================= cursor ======================= */
  var cur = $('is2Cur'), dot = $('is2CurDot'), curLabel = $('is2CurLabel');
  var mouse = { x: -100, y: -100, rx: -100, ry: -100, seen: false };
  if (FINE && cur) {
    document.addEventListener('mousemove', function (e) {
      mouse.x = e.clientX; mouse.y = e.clientY;
      if (!mouse.seen) { mouse.seen = true; mouse.rx = e.clientX; mouse.ry = e.clientY; cur.classList.add('is2-cur-on'); dot.classList.add('is2-cur-on'); }
      dot.style.transform = 'translate3d(' + e.clientX + 'px,' + e.clientY + 'px,0)';
    }, { passive: true });
    document.addEventListener('mouseover', function (e) {
      var t = e.target;
      if (!t || !t.closest) return;
      var lab = t.closest('[data-cursor]');
      var hov = t.closest('a, button, label, select, [role="button"], .is2-pick');
      var labelText = lab ? lab.getAttribute('data-cursor') : '';
      if (hov && lab && hov !== lab && lab.contains(hov)) labelText = '';
      if (hov && hov.tagName === 'BUTTON' && !lab) labelText = '';
      cur.classList.toggle('is2-cur-inv', !!(labelText && lab.hasAttribute('data-cursor-inv')));
      if (labelText) {
        curLabel.textContent = labelText;
        cur.classList.add('is2-cur-text'); cur.classList.remove('is2-cur-hover');
      } else {
        cur.classList.remove('is2-cur-text');
        cur.classList.toggle('is2-cur-hover', !!hov);
      }
    });
    document.addEventListener('mousedown', function () { cur.classList.add('is2-cur-down'); });
    document.addEventListener('mouseup', function () { cur.classList.remove('is2-cur-down'); });
    document.documentElement.addEventListener('mouseleave', function () { cur.classList.remove('is2-cur-on'); dot.classList.remove('is2-cur-on'); mouse.seen = false; });
  }

  /* ======================= magnetic ======================= */
  if (FINE && !RM) {
    var magEl = null;
    document.addEventListener('mousemove', function (e) {
      var el = e.target && e.target.closest ? e.target.closest('[data-magnetic]') : null;
      if (magEl && magEl !== el) { magEl.style.transform = ''; magEl = null; }
      if (!el) return;
      magEl = el;
      var r = el.getBoundingClientRect();
      var dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
      el.style.transform = 'translate3d(' + (dx * 0.22).toFixed(1) + 'px,' + (dy * 0.32).toFixed(1) + 'px,0)';
    }, { passive: true });
  }

  /* ======================= smooth anchors ======================= */
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a || e.defaultPrevented) return;
    var id = a.getAttribute('href').slice(1);
    if (!id) return;
    var target = document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    var top = target.getBoundingClientRect().top + window.pageYOffset - (id === 'inicio' || id === 'main-content' ? 90 : 64);
    window.scrollTo({ top: Math.max(0, top), behavior: RM ? 'auto' : 'smooth' });
    if (!target.hasAttribute('tabindex') && !/^(A|BUTTON|INPUT|TEXTAREA)$/.test(target.tagName)) target.setAttribute('tabindex', '-1');
    setTimeout(function () { try { target.focus({ preventScroll: true }); } catch (err) {} }, RM ? 0 : 700);
  });

  /* ======================= reveal ======================= */
  var revealIO = null;
  function reveal(el) { el.classList.add('is2-in'); }
  onStart(function () {
    var els = qa('.is2-rv, .is2-split');
    els.forEach(function (el) { var d = el.getAttribute('data-d'); if (d) el.style.transitionDelay = d + 'ms'; });
    if (!('IntersectionObserver' in window)) { els.forEach(reveal); return; }
    revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { reveal(en.target); revealIO.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    els.forEach(function (el) { revealIO.observe(el); });
  });

  /* ======================= hero title scramble ======================= */
  var GLYPHS = 'ABCDEFGHIJKLNOPRSTUVXYZ0123456789';
  function scramble(el, dur) {
    if (RM || el.is2Busy) return;
    var final = el.getAttribute('data-final') || el.textContent;
    el.setAttribute('data-final', final);
    el.is2Busy = true;
    var w = el.getBoundingClientRect().width;
    el.style.width = w + 'px';
    el.style.whiteSpace = 'nowrap';
    var t0 = performance.now();
    (function step(now) {
      var p = clamp((now - t0) / dur, 0, 1), s = '';
      for (var i = 0; i < final.length; i++) {
        s += (p * final.length * 1.15 > i + Math.random() * 2) ? final.charAt(i) : GLYPHS.charAt(Math.floor(Math.random() * GLYPHS.length));
      }
      el.textContent = s;
      if (p < 1) { requestAnimationFrame(step); return; }
      el.textContent = final;
      el.style.width = '';
      el.style.whiteSpace = '';
      el.is2Busy = false;
    })(t0);
  }
  onStart(function () {
    var words = qa('[data-scramble]');
    words.forEach(function (w, i) {
      setTimeout(function () { scramble(w, 1000); }, 350 + i * 220);
      if (FINE) w.addEventListener('mouseenter', function () { scramble(w, 600); });
    });
  });

  /* ======================= counters ======================= */
  onStart(function () {
    var nums = qa('[data-count]');
    function run(el) {
      var to = +el.getAttribute('data-count');
      if (RM) { el.textContent = to; return; }
      var t0 = performance.now(), dur = 1700;
      (function step(now) {
        var p = clamp((now - t0) / dur, 0, 1), e = 1 - Math.pow(1 - p, 4);
        el.textContent = Math.round(to * e);
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    }
    if (!('IntersectionObserver' in window)) { nums.forEach(run); return; }
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) { setTimeout(function () { run(x.target); }, 450); io.unobserve(x.target); } });
    }, { threshold: 0.5 });
    nums.forEach(function (n) { io.observe(n); });
  });

  /* ======================= clocks ======================= */
  safe(function () {
    var els = qa('[data-clock]');
    if (!els.length) return;
    var fmt;
    try { fmt = new Intl.DateTimeFormat('es-CO', { timeZone: 'America/Bogota', hour: '2-digit', minute: '2-digit', hour12: false }); } catch (e) { fmt = null; }
    function upd() { var s = fmt ? fmt.format(new Date()) : ''; els.forEach(function (el) { el.textContent = s; }); }
    upd();
    setInterval(upd, 20000);
  });

  /* ======================= hero pixel field ======================= */
  var hero = $('inicio'), heroIn = $('is2HeroIn');
  var field = (function () {
    var cv = $('is2HeroPx');
    if (!cv || !cv.getContext) return null;
    var ctx = cv.getContext('2d');
    if (!ctx) return null;
    var W = 0, H = 0, S = 28, cols = 0, rows = 0, en = null, ph = null, sp = null, tw = null, dpr = 1;
    var m = { x: -999, y: -999, on: false }, visible = true, last = 0, burstAt = 0;
    function size() {
      var r = cv.getBoundingClientRect();
      W = r.width; H = r.height;
      dpr = Math.min(1.5, window.devicePixelRatio || 1);
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      S = W < 700 ? 22 : 28;
      cols = Math.ceil(W / S) + 1; rows = Math.ceil(H / S) + 1;
      var n = cols * rows, r2 = rng(99);
      en = new Float32Array(n); ph = new Float32Array(n); sp = new Float32Array(n); tw = new Uint8Array(n);
      for (var i = 0; i < n; i++) { ph[i] = r2() * 6.283; sp[i] = 0.6 + r2() * 1.8; tw[i] = r2() < 0.22 ? 1 : 0; }
      if (RM) draw(0);
    }
    function draw(t) {
      ctx.clearRect(0, 0, W, H);
      var R = W < 700 ? 120 : 190, tsec = t / 1000;
      var mx = m.x, my = m.y, mon = m.on;
      if (!FINE && !RM) {
        mon = true;
        mx = W * (0.62 + 0.3 * Math.sin(tsec * 0.35));
        my = H * (0.42 + 0.3 * Math.sin(tsec * 0.52 + 1.3));
      }
      if (!RM && t - burstAt > 140) {
        burstAt = t;
        var bi = Math.floor(Math.random() * cols * rows);
        if (en) en[bi] = Math.max(en[bi], 0.55 + Math.random() * 0.4);
      }
      var half = S / 2;
      for (var y = 0; y < rows; y++) {
        for (var x = 0; x < cols; x++) {
          var i = y * cols + x, cx = x * S + half, cy = y * S + half;
          if (mon) {
            var dx = cx - mx, dy = cy - my, d = Math.sqrt(dx * dx + dy * dy);
            if (d < R) { var f = 1 - d / R; f = f * f; if (f > en[i]) en[i] = f; }
          }
          var e = en[i];
          if (!RM) en[i] = e * 0.955;
          var base = tw[i] ? 0.06 + 0.07 * (0.5 + 0.5 * Math.sin(tsec * sp[i] + ph[i])) : 0.045;
          if (e > 0.03) {
            var s = 2 + e * (S * 0.62);
            ctx.globalAlpha = Math.min(1, 0.18 + e * 0.95);
            ctx.fillStyle = e > 0.72 ? '#FF5A45' : '#E5342A';
            ctx.fillRect(cx - s / 2, cy - s / 2, s, s);
          } else {
            ctx.globalAlpha = base;
            ctx.fillStyle = '#FFFFFF';
            ctx.fillRect(cx - 1, cy - 1, 2, 2);
          }
        }
      }
      ctx.globalAlpha = 1;
    }
    size();
    var rt;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(size, 150); });
    if (FINE && hero) {
      hero.addEventListener('mousemove', function (e) { var r = cv.getBoundingClientRect(); m.x = e.clientX - r.left; m.y = e.clientY - r.top; m.on = true; }, { passive: true });
      hero.addEventListener('mouseleave', function () { m.on = false; });
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (e) { visible = e[0].isIntersecting; }).observe(cv);
    }
    return { tick: function (t) { if (RM || !visible) return; if (t - last < 16) return; last = t; draw(t); } };
  })();

  /* ======================= marquee ======================= */
  var bands = [];
  safe(function () {
    var A = ['Diseño web', 'Branding', 'Redes sociales', 'Fotografía', 'Apps a medida', 'Producción audiovisual'];
    var B = ['Sin plantillas', 'Hecho a tu medida', 'Rápido y responsivo', 'Soporte real', 'Desde Cali para Latinoamérica', 'Cada pixel cuenta'];
    function setup(el, items, speed, dir) {
      if (!el) return;
      var band = { el: el, items: items, speed: speed, dir: dir, w: 0, x: 0 };
      function build() {
        var one = items.map(function (t) { return '<span class="is2-bi">' + t + '<i></i></span>'; }).join('');
        el.innerHTML = one;
        var w = el.scrollWidth || 900;
        var reps = Math.max(3, Math.min(30, Math.ceil((window.innerWidth * 2) / w) + 1));
        var html = '';
        for (var r = 0; r < reps; r++) html += one;
        el.innerHTML = html;
        band.w = w;
        band.x = dir < 0 ? 0 : -w;
      }
      build();
      band.build = build;
      bands.push(band);
    }
    setup($('is2BandA'), A, 70, -1);
    setup($('is2BandB'), B, 42, 1);
    var t;
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(function () { bands.forEach(function (b) { b.build(); }); }, 200); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { bands.forEach(function (b) { b.build(); }); });
  });

  /* ======================= services ======================= */
  safe(function () {
    var list = $('is2SvcList');
    if (!list) return;
    qa('.is2-svc-row', list).forEach(function (row) {
      function side(e) { var r = row.getBoundingClientRect(); row.style.setProperty('--o', e.clientY < r.top + r.height / 2 ? 'top' : 'bottom'); }
      row.addEventListener('mouseenter', function (e) { side(e); row.classList.add('is2-hot'); });
      row.addEventListener('mouseleave', function (e) { side(e); row.classList.remove('is2-hot'); });
      row.addEventListener('focus', function () { row.classList.add('is2-hot'); });
      row.addEventListener('blur', function () { row.classList.remove('is2-hot'); });
    });
  });

  /* ======================= process ======================= */
  var proc = { pinned: false, dist: 0, broken: false, active: 0 };
  safe(function () {
    var sec = $('proceso'), pin = $('is2ProcPin'), track = $('is2ProcTrack');
    if (!sec || !track) return;
    var steps = qa('.is2-pstep', track), real = steps.filter(function (s) { return !s.classList.contains('is2-pstep-cta'); });
    var now = $('is2ProcNow'), bar = $('is2ProcBar');
    proc.setActive = function (i) {
      i = clamp(i, 0, real.length - 1);
      if (i === proc.active) return;
      proc.active = i;
      real.forEach(function (s, k) { s.classList.toggle('is2-act', k === i); });
      if (now) now.textContent = '0' + (i + 1);
    };
    proc.layout = function () {
      var want = window.innerWidth >= 1024 && !RM && !proc.broken;
      sec.classList.toggle('is2-pinned', want);
      proc.pinned = want;
      track.style.transform = '';
      if (want) {
        var lastEl = steps[steps.length - 1];
        var edge = parseFloat(getComputedStyle(track).paddingRight) || 48;
        proc.dist = Math.max(0, lastEl.offsetLeft + lastEl.offsetWidth + edge - window.innerWidth);
        sec.style.height = (window.innerHeight + proc.dist) + 'px';
      } else {
        sec.style.height = '';
      }
    };
    proc.tick = function () {
      var r = sec.getBoundingClientRect(), vh = window.innerHeight;
      if (proc.pinned) {
        var span = r.height - vh, p = span > 0 ? clamp(-r.top / span, 0, 1) : 0;
        track.style.transform = 'translate3d(' + (-p * proc.dist).toFixed(1) + 'px,0,0)';
        if (bar) bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
        proc.setActive(Math.floor(p * real.length * 0.999 + 0.0001));
        if (r.top < -80 && r.bottom > vh + 80) {
          var pt = pin.getBoundingClientRect().top;
          if (Math.abs(pt) > 40) { proc.broken = true; proc.layout(); }
        }
      } else if (r.top < vh && r.bottom > 0) {
        var best = 0, bd = 1e9;
        real.forEach(function (s, k) { var b = s.getBoundingClientRect(); var d = Math.abs(b.top + b.height / 2 - vh / 2); if (d < bd) { bd = d; best = k; } });
        proc.setActive(best);
        var p2 = clamp((vh * 0.6 - r.top) / (r.height), 0, 1);
        if (bar) bar.style.transform = 'scaleX(' + p2.toFixed(4) + ')';
      }
    };
    proc.layout();
    var t;
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(proc.layout, 200); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(proc.layout);
    window.addEventListener('load', proc.layout);
  });

  /* ======================= manifesto ======================= */
  var mani = null;
  safe(function () {
    var el = $('is2ManiText');
    if (!el) return;
    var keys = (el.getAttribute('data-key') || '').split(',');
    var words = el.textContent.trim().split(/\s+/);
    el.setAttribute('aria-label', el.textContent.trim());
    el.innerHTML = words.map(function (w) {
      var k = keys.indexOf(w) > -1 ? ' is2-k' : '';
      return '<span class="is2-w' + k + '" aria-hidden="true">' + w + '</span>';
    }).join(' ');
    var ws = qa('.is2-w', el), lit = -1;
    if (RM) { ws.forEach(function (w) { w.classList.add('on'); }); return; }
    mani = function () {
      var r = el.getBoundingClientRect(), vh = window.innerHeight;
      if (r.bottom < -200 || r.top > vh + 200) return;
      var p = clamp((vh * 0.82 - r.top) / (r.height + vh * 0.32), 0, 1);
      var n = Math.round(p * ws.length);
      if (n === lit) return;
      lit = n;
      ws.forEach(function (w, i) { w.classList.toggle('on', i < n); });
    };
  });

  /* ======================= portfolio ======================= */
  var gal = { tick: null };
  safe(function () {
    var track = $('is2Track'), galEl = $('is2Gal');
    if (!track) return;
    var projects = [
      { tag: 'Sitio web', name: 'Tienda de moda: landing y catálogo', desc: 'Rediseño completo de landing y catálogo para una tienda de ropa, pensado para convertir el tráfico que llega desde redes sociales.', glyph: 'web', seed: 11, list: ['Diseño UX/UI', 'WordPress', 'Catálogo', 'SEO base'] },
      { tag: 'Branding', name: 'Identidad visual para un café de especialidad', desc: 'Logo, paleta y sistema visual completo, aplicado a empaques, menú y redes sociales.', glyph: 'cup', seed: 23, list: ['Logo', 'Paleta', 'Empaques', 'Menú'] },
      { tag: 'Apps', name: 'App de reservas para un estudio de yoga', desc: 'Una app sencilla para reservar clases y gestionar cupos, que el equipo del estudio maneja sin ayuda técnica.', glyph: 'apps', seed: 37, list: ['App móvil', 'Reservas', 'Panel admin'] },
      { tag: 'Redes sociales', name: 'Lanzamiento para una clínica estética', desc: 'Estrategia y piezas para el lanzamiento de una nueva línea de servicios, con calendario de contenido a 60 días.', glyph: 'social', seed: 41, list: ['Estrategia', 'Piezas', 'Calendario 60 días'] },
      { tag: 'Audiovisual', name: 'Video institucional para una constructora', desc: 'Guion, rodaje y edición de un video institucional usado en ferias y presentaciones comerciales.', glyph: 'video', seed: 53, list: ['Guion', 'Rodaje', 'Edición'] }
    ];
    var total = projects.length;
    track.innerHTML = projects.map(function (p, i) {
      var n = '0' + (i + 1);
      return '<button type="button" class="is2-card" data-i="' + i + '" data-cursor="Ver" aria-label="Ver detalle: ' + p.name + '">' +
        '<span class="is2-card-thumb" style="display:block">' + artSVG(p.glyph, p.seed, n + ' / 0' + total) + '<span class="is2-card-tag">' + p.tag + '</span></span>' +
        '<span class="is2-card-meta"><span class="is2-card-name">' + p.name + '</span><span class="is2-card-idx">' + n + '</span></span></button>';
    }).join('');
    var cards = qa('.is2-card', track);
    var count = $('is2Count'), prog = $('is2GalProg');
    var idx = 0, stops = [0], maxX = 0, x = 0;

    function measure() {
      var padL = parseFloat(getComputedStyle(galEl).paddingLeft) || 0;
      var padR = parseFloat(getComputedStyle(galEl).paddingRight) || 0;
      var view = galEl.clientWidth - padL - padR;
      maxX = Math.max(0, track.scrollWidth - view);
      stops = [];
      for (var i = 0; i < cards.length; i++) {
        var s = Math.min(cards[i].offsetLeft, maxX);
        if (!stops.length || s > stops[stops.length - 1] + 2) stops.push(s);
        if (s >= maxX) break;
      }
      if (!stops.length) stops = [0];
      idx = Math.min(idx, stops.length - 1);
      go(idx, true);
    }
    function go(i, quiet) {
      var n = stops.length;
      idx = ((i % n) + n) % n;
      x = stops[idx];
      track.style.transform = 'translate3d(' + (-x) + 'px,0,0)';
      var shown = Math.min(total, idx + 1);
      if (count) count.innerHTML = '<b>0' + shown + '</b> / 0' + total;
      if (prog) prog.style.transform = 'scaleX(' + ((idx + 1) / n).toFixed(3) + ')';
    }
    measure();
    var mt;
    window.addEventListener('resize', function () { clearTimeout(mt); mt = setTimeout(measure, 200); });
    window.addEventListener('load', measure);

    var paused = false, hovering = false, inView = false, lastAuto = performance.now();
    $('is2Prev').addEventListener('click', function () { go(idx - 1); lastAuto = performance.now(); });
    $('is2Next').addEventListener('click', function () { go(idx + 1); lastAuto = performance.now(); });
    galEl.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(idx + 1); lastAuto = performance.now(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(idx - 1); lastAuto = performance.now(); }
    });
    galEl.addEventListener('mouseenter', function () { hovering = true; });
    galEl.addEventListener('mouseleave', function () { hovering = false; });
    galEl.addEventListener('focusin', function () { paused = true; });
    galEl.addEventListener('focusout', function () { paused = false; });
    if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { inView = e[0].isIntersecting; }, { threshold: 0.3 }).observe(galEl);

    var drag = { on: false, sx: 0, dx: 0, moved: false, id: null };
    track.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      drag.on = true; drag.sx = e.clientX; drag.dx = 0; drag.moved = false; drag.id = e.pointerId;
    });
    window.addEventListener('pointermove', function (e) {
      if (!drag.on || e.pointerId !== drag.id) return;
      drag.dx = e.clientX - drag.sx;
      if (!drag.moved && Math.abs(drag.dx) > 8) { drag.moved = true; track.classList.add('is2-drag'); try { track.setPointerCapture(e.pointerId); } catch (err) {} }
      if (drag.moved) {
        var nx = x - drag.dx;
        if (nx < 0) nx = nx * 0.35;
        if (nx > maxX) nx = maxX + (nx - maxX) * 0.35;
        track.style.transform = 'translate3d(' + (-nx) + 'px,0,0)';
      }
    }, { passive: true });
    function endDrag() {
      if (!drag.on) return;
      drag.on = false;
      track.classList.remove('is2-drag');
      if (drag.moved) {
        if (drag.dx < -60) go(Math.min(idx + 1, stops.length - 1));
        else if (drag.dx > 60) go(Math.max(idx - 1, 0));
        else go(idx);
        lastAuto = performance.now();
        setTimeout(function () { drag.moved = false; }, 0);
      }
    }
    window.addEventListener('pointerup', endDrag);
    window.addEventListener('pointercancel', endDrag);

    gal.tick = function (now) {
      if (RM || paused || hovering || drag.on || !inView || modalOpen) { lastAuto = now; return; }
      if (now - lastAuto > 4200) { go(idx + 1); lastAuto = now; }
    };

    /* modal */
    var modal = $('is2Modal'), box = modal.querySelector('.is2-modal-box'), lastFocus = null, modalOpen = false;
    function openModal(i) {
      var p = projects[i];
      $('is2ModalArt').innerHTML = artSVG(p.glyph, p.seed);
      $('is2ModalTag').textContent = p.tag;
      $('is2ModalT').textContent = p.name;
      $('is2ModalD').textContent = p.desc;
      $('is2ModalL').innerHTML = p.list.map(function (l) { return '<li>' + l + '</li>'; }).join('');
      lastFocus = document.activeElement;
      modal.classList.add('is2-open');
      modal.setAttribute('aria-hidden', 'false');
      root.classList.add('is2-modal-open');
      document.documentElement.style.overflow = 'hidden';
      modalOpen = true;
      setTimeout(function () { $('is2ModalX').focus(); }, 60);
    }
    function closeModal() {
      if (!modalOpen) return;
      modal.classList.remove('is2-open');
      modal.setAttribute('aria-hidden', 'true');
      root.classList.remove('is2-modal-open');
      document.documentElement.style.overflow = '';
      modalOpen = false;
      if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    }
    track.addEventListener('click', function (e) {
      var c = e.target.closest('.is2-card');
      if (!c || drag.moved) { e.preventDefault(); return; }
      openModal(+c.getAttribute('data-i'));
    });
    $('is2ModalX').addEventListener('click', closeModal);
    $('is2ModalBg').addEventListener('click', closeModal);
    $('is2ModalCta').addEventListener('click', closeModal);
    document.addEventListener('keydown', function (e) {
      if (!modalOpen) return;
      if (e.key === 'Escape') { closeModal(); return; }
      if (e.key === 'Tab') {
        var f = qa('a[href], button:not([disabled])', box);
        if (!f.length) return;
        var first = f[0], lastF = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastF.focus(); }
        else if (!e.shiftKey && document.activeElement === lastF) { e.preventDefault(); first.focus(); }
      }
    });
    gal.isModal = function () { return modalOpen; };
  });

  /* ======================= before / after ======================= */
  safe(function () {
    var cmp = $('is2Cmp'), range = $('is2CmpRange');
    if (!cmp || !range) return;
    var touched = false;
    function set(v) { cmp.style.setProperty('--p', v + '%'); }
    range.addEventListener('input', function () { touched = true; set(range.value); });
    set(range.value);
    if (RM || !('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return;
      io.disconnect();
      var keys = [[0, 50], [900, 18], [1900, 82], [2700, 50]], t0 = performance.now();
      (function step(now) {
        if (touched) return;
        var t = now - t0, v = 50;
        for (var k = 1; k < keys.length; k++) {
          if (t <= keys[k][0]) {
            var a = keys[k - 1], b = keys[k], p = (t - a[0]) / (b[0] - a[0]);
            p = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
            v = a[1] + (b[1] - a[1]) * p;
            break;
          }
        }
        range.value = v; set(v);
        if (t < keys[keys.length - 1][0]) requestAnimationFrame(step);
      })(t0);
    }, { threshold: 0.6 });
    io.observe(cmp);
  });

  /* ======================= contact form (Contact Form 7 REST) ======================= */
  safe(function () {
    var form = $('is2Form');
    if (!form) return;
    var status = $('is2Status'), btn = $('is2Send'), btnT = $('is2SendT');
    var endpoint = window.location.origin + '/wp-json/contact-form-7/v1/contact-forms/1969/feedback';
    var ICON_OK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>';
    var ICON_BAD = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 7v6M12 17h.01"/><circle cx="12" cy="12" r="10"/></svg>';
    function show(kind, msg) {
      status.className = 'is2-status ' + (kind === 'ok' ? 'is2-ok' : 'is2-bad');
      status.innerHTML = (kind === 'ok' ? ICON_OK : ICON_BAD) + '<span></span>';
      status.querySelector('span').textContent = msg;
    }
    function fieldOf(name) { return form.querySelector('[name="' + name + '"]'); }
    function mark(name, bad) { var f = fieldOf(name); if (f) f.closest('.is2-field').classList.toggle('is2-bad', bad); }
    form.addEventListener('input', function (e) { var lab = e.target.closest('.is2-field'); if (lab) lab.classList.remove('is2-bad'); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = fieldOf('your-name').value.trim(), email = fieldOf('your-email').value.trim();
      var badName = !name, badMail = !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
      mark('your-name', badName); mark('your-email', badMail);
      if (badName || badMail) { (badName ? fieldOf('your-name') : fieldOf('your-email')).focus(); return; }
      var fd = new FormData(form);
      var picks = qa('.is2-pick input:checked', form).map(function (c) { return c.value; });
      var msg = fieldOf('your-message').value.trim();
      if (picks.length) msg = (msg ? msg + '\n\n' : '') + 'Servicios de interés: ' + picks.join(', ');
      fd.set('your-message', msg || '(Sin mensaje)');
      if (!fd.get('your-subject')) fd.set('your-subject', 'Nuevo mensaje desde innovasites.co');
      btn.classList.add('is2-busy'); btn.setAttribute('aria-busy', 'true'); btnT.textContent = 'Enviando';
      status.className = 'is2-status'; status.innerHTML = '';
      fetch(endpoint, { method: 'POST', body: fd, credentials: 'same-origin' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && (d.status === 'mail_sent' || d.status === 'sent')) {
            form.reset();
            show('ok', '¡Mensaje enviado! Te respondemos en menos de 24 horas.');
          } else if (d && d.status === 'validation_failed' && d.invalid_fields) {
            d.invalid_fields.forEach(function (f) { var n = (f.field || '').replace(/^.*?(your-[a-z]+).*$/, '$1'); mark(n, true); });
            show('bad', d.message || 'Revisa los campos marcados.');
          } else {
            show('bad', (d && d.message) || 'No pudimos enviar tu mensaje. Escríbenos por WhatsApp mientras lo revisamos.');
          }
        })
        .catch(function () { show('bad', 'No pudimos conectar con el servidor. Escríbenos por WhatsApp o a info@innovasites.co.'); })
        .then(function () { btn.classList.remove('is2-busy'); btn.removeAttribute('aria-busy'); btnT.textContent = 'Enviar mensaje'; });
    });
  });

  /* ======================= main loop ======================= */
  var mcta = $('is2Mcta'), contact = $('contacto');
  var lastY = window.pageYOffset, vel = 0, lastT = performance.now();
  function loop(now) {
    var dt = Math.min(64, now - lastT) / 1000;
    lastT = now;
    var y = window.pageYOffset;
    vel = lerp(vel, (y - lastY) / Math.max(dt, 0.001), 0.15);
    lastY = y;

    if (FINE && cur && mouse.seen) {
      var k = RM ? 1 : 0.2;
      mouse.rx = lerp(mouse.rx, mouse.x, k); mouse.ry = lerp(mouse.ry, mouse.y, k);
      cur.style.transform = 'translate3d(' + mouse.rx.toFixed(1) + 'px,' + mouse.ry.toFixed(1) + 'px,0)';
    }
    if (field) field.tick(now);
    if (!RM && hero && heroIn && started) {
      var hh = hero.offsetHeight || 1, p = clamp(y / hh, 0, 1);
      if (p < 1) { heroIn.style.transform = 'translate3d(0,' + (p * 110).toFixed(1) + 'px,0)'; heroIn.style.opacity = (1 - p * 0.95).toFixed(3); }
    }
    if (!RM) {
      var boost = 1 + Math.min(Math.abs(vel) / 260, 5);
      bands.forEach(function (b) {
        if (!b.w) return;
        b.x += b.dir * b.speed * boost * dt;
        if (b.x <= -b.w) b.x += b.w;
        if (b.x > 0) b.x -= b.w;
        b.el.style.transform = 'translate3d(' + b.x.toFixed(2) + 'px,0,0)';
      });
    }
    if (proc.tick) proc.tick();
    if (mani) mani();
    if (gal.tick) gal.tick(now);
    if (mcta) {
      var showIt = y > window.innerHeight * 0.7 && !(gal.isModal && gal.isModal());
      if (showIt && contact) { var cr = contact.getBoundingClientRect(); if (cr.top < window.innerHeight * 0.9) showIt = false; }
      mcta.classList.toggle('is2-on', showIt);
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
