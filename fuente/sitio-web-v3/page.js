(function () {
function iv3main() {
  var root = document.getElementById('iv3');
  if (!root) return;
  var $ = function (id) { return document.getElementById(id); };
  var qa = function (sel, ctx) { return Array.prototype.slice.call((ctx || root).querySelectorAll(sel)); };
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FINE = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var G = window.gsap, ST = window.ScrollTrigger;
  var ANIM = !!(G && ST) && !RM;
  function safe(fn) { try { fn(); } catch (e) { if (window.console) console.warn('[iv3]', e); } }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  if (ANIM) G.registerPlugin(ST);

  /* ---------------- pixel icons ---------------- */
  var ICONS = {
    web: ['#########', '#r#r#...#', '#########', '#.......#', '#.rrr...#', '#.......#', '#.##.##.#', '#.......#', '#########'],
    heart: ['.rr...rr.', 'rrrr.rrrr', 'rrrrrrrrr', 'rrrrrrrrr', '.rrrrrrr.', '..rrrrr..', '...rrr...', '....r....', '.........'],
    camera: ['..###....', '#########', '#.....r.#', '#..###..#', '#.#rrr#.#', '#.#rrr#.#', '#..###..#', '#.......#', '#########'],
    play: ['#########', '#.......#', '#..r....#', '#..rr...#', '#..rrr..#', '#..rr...#', '#..r....#', '#.......#', '#########'],
    phone: ['..#####..', '..#...#..', '..#rrr#..', '..#...#..', '..#r.r#..', '..#...#..', '..#rrr#..', '..#.#.#..', '..#####..'],
    brand: ['....r....', '...rrr...', '..rr#rr..', '.rr...rr.', 'rr#...#rr', '.rr...rr.', '..rr#rr..', '...rrr...', '....r....']
  };
  safe(function () {
    qa('.iv3-px').forEach(function (el) {
      var map = ICONS[el.getAttribute('data-icon')] || ICONS.web, html = '';
      map.join('').split('').forEach(function (c) { html += '<i class="' + (c === '#' ? 'w' : c === 'r' ? 'r' : '') + '" style="--d:' + (Math.random() * 0.5).toFixed(2) + 's"></i>'; });
      el.innerHTML = html;
    });
  });

  /* ---------------- portfolio art (cards are in the HTML) ---------------- */
  function drawArt(cv) {
    var r = cv.getBoundingClientRect();
    if (!r.width) return;
    var dpr = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(r.width * dpr); cv.height = Math.round(r.height * dpr);
    var c = cv.getContext('2d'); c.setTransform(dpr, 0, 0, dpr, 0, 0);
    var alt = cv.getAttribute('data-alt') === '1';
    var ink = '#0A0C11', acc = alt ? '#E5342A' : '#FFFFFF';
    var map = ICONS[cv.getAttribute('data-icon')] || ICONS.web;
    var cell = Math.max(10, Math.round(Math.min(r.width, r.height) / 15));
    var gx = Math.floor(r.width / cell), gy = Math.floor(r.height / cell);
    var seed = map.join('').length * 7 + (alt ? 3 : 1);
    function rnd() { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; }
    c.clearRect(0, 0, r.width, r.height);
    c.fillStyle = alt ? 'rgba(10,12,17,.08)' : 'rgba(10,12,17,.12)';
    for (var y = 0; y < gy; y++) for (var x = 0; x < gx; x++) if (rnd() < 0.16) c.fillRect(x * cell + 1, y * cell + 1, cell - 2, cell - 2);
    var s = Math.floor(Math.min(gx, gy) * 0.62 / 9) || 1, ox = Math.floor((gx - 9 * s) / 2) + Math.floor(gx * 0.12), oy = Math.floor((gy - 9 * s) / 2) - Math.floor(gy * 0.08);
    map.forEach(function (row, yy) {
      row.split('').forEach(function (ch, xx) {
        if (ch === '.') return;
        c.fillStyle = ch === 'r' ? acc : ink;
        c.fillRect((ox + xx * s) * cell, (oy + yy * s) * cell, s * cell - 2, s * cell - 2);
      });
    });
  }
  var artIO = null;
  function drawAllArt() {
    qa('.iv3-proj-art canvas').forEach(function (cv) {
      if (cv.iv3drawn || !('IntersectionObserver' in window)) { safe(function () { drawArt(cv); }); return; }
      if (!artIO) artIO = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { artIO.unobserve(e.target); e.target.iv3drawn = true; safe(function () { drawArt(e.target); }); } });
      }, { rootMargin: '400px 0px' });
      artIO.observe(cv);
    });
  }

  /* ---------------- marquee bands ---------------- */
  var BAND = ['Sitios web', 'Apps', 'Redes sociales', 'Branding', 'Fotografía', 'Video'];
  var bands = [];
  safe(function () {
    qa('.iv3-band-in').forEach(function (el) {
      var unit = BAND.map(function (w) { return '<span>' + w + '<i></i></span>'; }).join('');
      el.innerHTML = unit + unit + unit + unit;
      bands.push({ el: el, dir: +el.getAttribute('data-dir') || 1, x: 0, w: 0 });
    });
  });
  function measureBands() { bands.forEach(function (b) { b.w = b.el.scrollWidth / 4; }); }

  var chars = [];

  /* ---------------- problem words ---------------- */
  var words = [];
  safe(function () {
    var p = $('iv3ProbTxt');
    if (!p) return;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(' ')); return; }
            var s = document.createElement('span'); s.className = 'iv3-w'; s.textContent = w; frag.appendChild(s); words.push(s);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1 && !n.classList.contains('iv3-br')) walk(n);
      });
    })(p);
  });

  /* ---------------- hero pixel field (dots are CSS, canvas only draws near the pointer) ---------------- */
  var field = (function () {
    var cv = $('iv3Field');
    if (!cv) return null;
    var c = cv.getContext('2d');
    var W = 0, H = 0, cell = 26, cols = 0, rows = 0, visible = true, last = 0, step = 1000 / 30;
    var mouse = { x: -999, y: -999, tx: 0, ty: 0, seen: false }, sparks = [], t0 = performance.now();
    function size() {
      var r = cv.getBoundingClientRect();
      W = Math.round(r.width); H = Math.round(r.height);
      cv.width = W; cv.height = H;
      cell = W < 700 ? 22 : 26;
      cols = Math.ceil(W / cell) + 1; rows = Math.ceil(H / cell) + 1;
    }
    if (FINE) {
      cv.parentNode.addEventListener('pointermove', function (e) {
        var r = cv.getBoundingClientRect();
        mouse.tx = e.clientX - r.left; mouse.ty = e.clientY - r.top; mouse.seen = true;
      }, { passive: true });
      cv.parentNode.addEventListener('pointerleave', function () { mouse.seen = false; });
    }
    var REDS = [], WHITES = [];
    for (var i = 0; i <= 20; i++) { REDS.push('rgba(229,52,42,' + (i / 20).toFixed(2) + ')'); WHITES.push('rgba(255,255,255,' + (i / 20).toFixed(2) + ')'); }
    function draw(now) {
      var t = (now - t0) / 1000;
      if (!mouse.seen) {
        if (W < 700) { mouse.tx = W * (0.86 + 0.08 * Math.cos(t * 0.5)); mouse.ty = H * (0.62 + 0.12 * Math.sin(t * 0.4)); }
        else { mouse.tx = W * (0.64 + 0.2 * Math.cos(t * 0.35)); mouse.ty = H * (0.5 + 0.22 * Math.sin(t * 0.5)); }
      }
      if (mouse.x < -900) { mouse.x = mouse.tx; mouse.y = mouse.ty; }
      mouse.x += (mouse.tx - mouse.x) * 0.2; mouse.y += (mouse.ty - mouse.y) * 0.2;
      c.clearRect(0, 0, W, H);
      var R = W < 700 ? 95 : Math.max(150, W * 0.15), R2 = R * R;
      var x0 = Math.max(0, Math.floor((mouse.x - R) / cell)), x1 = Math.min(cols, Math.ceil((mouse.x + R) / cell));
      var y0 = Math.max(0, Math.floor((mouse.y - R) / cell)), y1 = Math.min(rows, Math.ceil((mouse.y + R) / cell));
      for (var y = y0; y < y1; y++) {
        for (var x = x0; x < x1; x++) {
          var px = x * cell, py = y * cell, dx = px - mouse.x, dy = py - mouse.y, d2 = dx * dx + dy * dy;
          if (d2 >= R2) continue;
          var k = 1 - d2 / R2; k *= k;
          var q = ((x * 7 + y * 13) % 5) / 5, s;
          if (k > 0.25 + q * 0.5) { c.fillStyle = REDS[Math.round((0.25 + k * 0.75) * 20)]; s = cell * (0.3 + k * 0.62); }
          else { c.fillStyle = WHITES[Math.round(Math.min(1, 0.07 + k * 0.4) * 20)]; s = 2 + k * 5; }
          c.fillRect(px - s / 2, py - s / 2, s, s);
        }
      }
      if (Math.random() < 0.25 && sparks.length < 14) sparks.push({ x: Math.floor(Math.random() * cols), y: Math.floor(Math.random() * rows), l: 0, red: Math.random() < 0.6 });
      var ss = cell * 0.55;
      for (var n = sparks.length - 1; n >= 0; n--) {
        var sp = sparks[n]; sp.l += 0.05;
        if (sp.l >= 1) { sparks.splice(n, 1); continue; }
        var al = Math.round(Math.sin(sp.l * Math.PI) * 20);
        c.fillStyle = sp.red ? REDS[al] : WHITES[Math.round(al * 0.8)];
        c.fillRect(sp.x * cell - ss / 2, sp.y * cell - ss / 2, ss, ss);
      }
    }
    size();
    if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { visible = e[0].isIntersecting; }).observe(cv);
    return {
      size: size,
      tick: function (now) { if (!visible || document.hidden || now - last < step - 2) return; last = now; draw(now); },
      still: function () { draw(performance.now()); }
    };
  })();

  /* ---------------- compare slider ---------------- */
  safe(function () {
    var cmp = $('iv3Cmp'), r = $('iv3CmpR');
    if (!cmp || !r) return;
    function set() { cmp.style.setProperty('--pos', r.value + '%'); }
    r.addEventListener('input', set); set();
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { cmp.classList.add('iv3-in'); io.disconnect(); } }, { rootMargin: '600px 0px' });
      io.observe(cmp);
    } else cmp.classList.add('iv3-in');
  });

  /* ---------------- contact form (CF7 REST) ---------------- */
  safe(function () {
    var form = $('iv3Form');
    if (!form) return;
    var status = $('iv3FormStatus'), btn = $('iv3Send'), btnT = $('iv3SendT');
    var endpoint = window.location.origin + '/wp-json/contact-form-7/v1/contact-forms/1969/feedback';
    var OK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M20 6L9 17l-5-5"/></svg>';
    var BAD = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 7v6M12 17h.01"/><circle cx="12" cy="12" r="10"/></svg>';
    function show(kind, msg) {
      status.className = 'iv3-fstatus ' + (kind === 'ok' ? 'iv3-ok' : 'iv3-err');
      status.innerHTML = (kind === 'ok' ? OK : BAD) + '<span></span>';
      status.querySelector('span').textContent = msg;
    }
    function f(name) { return form.querySelector('[name="' + name + '"]'); }
    function mark(name, bad) { var el = f(name); if (el) el.closest('.iv3-field').classList.toggle('iv3-bad', bad); }
    form.addEventListener('input', function (e) { var l = e.target.closest('.iv3-field'); if (l) l.classList.remove('iv3-bad'); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = f('your-name').value.trim(), email = f('your-email').value.trim();
      var badN = !name, badM = !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
      mark('your-name', badN); mark('your-email', badM);
      if (badN || badM) { (badN ? f('your-name') : f('your-email')).focus(); show('bad', 'Revisa tu nombre y tu correo.'); return; }
      var fd = new FormData(form);
      var picks = qa('.iv3-pick input:checked', form).map(function (c) { return c.value; });
      var msg = f('your-message').value.trim();
      if (picks.length) msg = (msg ? msg + '\n\n' : '') + 'Servicios de interés: ' + picks.join(', ');
      fd.set('your-message', msg || '(Sin mensaje)');
      if (!fd.get('your-subject')) fd.set('your-subject', 'Nuevo mensaje desde innovasites.co');
      btn.classList.add('iv3-busy'); btn.setAttribute('aria-busy', 'true'); btnT.textContent = 'Enviando';
      status.className = 'iv3-fstatus'; status.innerHTML = '';
      fetch(endpoint, { method: 'POST', body: fd, credentials: 'same-origin' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && (d.status === 'mail_sent' || d.status === 'sent')) { form.reset(); show('ok', '¡Mensaje enviado! Te respondemos en menos de 24 horas.'); }
          else if (d && d.status === 'validation_failed' && d.invalid_fields) {
            d.invalid_fields.forEach(function (x) { mark((x.field || '').replace(/^.*?(your-[a-z]+).*$/, '$1'), true); });
            show('bad', d.message || 'Revisa los campos marcados.');
          } else show('bad', (d && d.message) || 'No pudimos enviar tu mensaje. Escríbenos por WhatsApp mientras lo revisamos.');
        })
        .catch(function () { show('bad', 'No pudimos conectar con el servidor. Escríbenos por WhatsApp o a info@innovasites.co.'); })
        .then(function () { btn.classList.remove('iv3-busy'); btn.removeAttribute('aria-busy'); btnT.textContent = 'Enviar mensaje'; });
    });
  });

  /* ---------------- mobile CTA ---------------- */
  safe(function () {
    var m = $('iv3Mcta'), hero = $('inicio'), contact = $('contacto');
    if (!m || !hero || !contact) return;
    var tk = false;
    function upd() {
      tk = false;
      var vh = window.innerHeight, h = hero.getBoundingClientRect(), c = contact.getBoundingClientRect();
      m.classList.toggle('iv3-show', h.bottom < vh * 0.3 && c.top > vh * 0.75);
    }
    window.addEventListener('scroll', function () { if (!tk) { tk = true; requestAnimationFrame(upd); } }, { passive: true });
    upd();
  });

  /* ---------------- cursor + magnetic ---------------- */
  var cur = null, lastMg = null, mp = { x: 0, y: 0, rx: 0, ry: 0, on: false };
  if (FINE && !RM) safe(function () {
    cur = document.createElement('div'); cur.className = 'iv3-cur'; cur.setAttribute('aria-hidden', 'true'); root.appendChild(cur);
    document.addEventListener('pointermove', function (e) {
      mp.x = e.clientX; mp.y = e.clientY;
      if (!mp.on) { mp.rx = mp.x; mp.ry = mp.y; mp.on = true; }
      var hot = e.target.closest && e.target.closest('a, button, input, textarea, label, .iv3-card, .iv3-cmp');
      cur.classList.toggle('iv3-big', !!hot);
      var mg = e.target.closest && e.target.closest('[data-magnetic]');
      if (lastMg && lastMg !== mg) { lastMg.style.transform = ''; lastMg = null; }
      if (mg) {
        lastMg = mg;
        var r = mg.getBoundingClientRect();
        var dx = (e.clientX - (r.left + r.width / 2)) * 0.22, dy = (e.clientY - (r.top + r.height / 2)) * 0.32;
        mg.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px)'; mg.style.transition = 'transform .25s cubic-bezier(.2,.8,.2,1)';
      }
    }, { passive: true });
    document.addEventListener('pointerleave', function () { mp.on = false; cur.style.opacity = '0'; });
    document.addEventListener('pointerenter', function () { cur.style.opacity = '1'; });
  });

  /* ---------------- process helpers ---------------- */
  var STATUS = ['Idea recibida', 'Propuesta aprobada', 'Diseño en construcción', 'Sitio en línea'];
  var steps = qa('.iv3-step'), stepsOl = $('iv3Steps'), statusT = $('iv3StatusT'), curStep = -1;
  function setStep(i, p) {
    if (stepsOl) stepsOl.style.setProperty('--p', p.toFixed(3));
    if (i === curStep) return;
    curStep = i;
    steps.forEach(function (s, k) { s.classList.toggle('iv3-on', k === i); });
    if (statusT) statusT.textContent = STATUS[i];
  }

  /* ---------------- counters ---------------- */
  function runCount(el) {
    var to = +el.getAttribute('data-count'), t0 = null;
    function step(t) { if (!t0) t0 = t; var k = clamp((t - t0) / 1600, 0, 1); k = 1 - Math.pow(1 - k, 4); el.textContent = Math.round(to * k); if (k < 1) requestAnimationFrame(step); }
    el.textContent = '0'; requestAnimationFrame(step);
  }

  /* ================== STATIC MODE ================== */
  if (!ANIM) {
    root.classList.add('iv3-static');
    safe(function () { if (field) field.still(); });
    setStep(3, 1);
    steps.forEach(function (s) { s.classList.add('iv3-on'); });
    drawAllArt();
    measureBands();
    if (!RM) {
      (function bandLoop() { bands.forEach(function (b) { b.x -= 0.6 * b.dir; if (b.x <= -b.w) b.x += b.w; if (b.x > 0) b.x -= b.w; b.el.style.transform = 'translate3d(' + b.x + 'px,0,0)'; }); requestAnimationFrame(bandLoop); })();
      if (field) (function fl(now) { field.tick(now); requestAnimationFrame(fl); })(performance.now());
    }
    return;
  }

  /* ================== ANIMATED MODE ================== */
  /* heavy setup runs in small chunks so the page stays responsive while it loads */
  var Q = [];
  function later(fn) { Q.push(fn); }
  function runQ() { var fn = Q.shift(); if (!fn) { ST.refresh(); safe(restoreScroll); return; } safe(fn); setTimeout(runQ, 0); }
  document.documentElement.classList.add('iv3-js');
  root.classList.add('iv3-anim');
  /* restore the scroll position ourselves, after pinned sections exist (avoids jumps and slow catch-up) */
  var savedY = 0;
  try {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    var sv = (sessionStorage.getItem('iv3y') || '').split('|');
    if (sv[1] === location.pathname) savedY = +sv[0] || 0;
    sessionStorage.removeItem('iv3y');
  } catch (e) {}
  window.addEventListener('pagehide', function () { try { sessionStorage.setItem('iv3y', Math.round(window.pageYOffset) + '|' + location.pathname); } catch (e) {} });
  function restoreScroll() {
    var target = null;
    if (location.hash && location.hash.length > 1) { try { target = document.querySelector(location.hash); } catch (e) {} }
    if (!target && savedY > 0) target = savedY;
    if (target === null) return;
    if (lenis) lenis.scrollTo(target, { immediate: true, force: true });
    else if (typeof target === 'number') window.scrollTo(0, target); else target.scrollIntoView();
    ST.update();
    ST.getAll().forEach(function (t) { var tw = t.getTween && t.getTween(); if (tw) tw.progress(1); });
  }
  var lenis = null;
  later(function () {
    if (!window.Lenis) return;
    lenis = new window.Lenis({ lerp: 0.14, smoothWheel: true, wheelMultiplier: 1.1 });
    window.iv3Lenis = lenis;
    lenis.on('scroll', ST.update);
    G.ticker.add(function (t) { lenis.raf(t * 1000); });
    G.ticker.lagSmoothing(0);
  });

  /* hero scroll-out */
  later(function () {
    var tl = G.timeline({ scrollTrigger: { trigger: '#inicio', start: 'top top', end: 'bottom top', scrub: true } });
    tl.to('.iv3-ln1', { xPercent: -14, ease: 'none' }, 0)
      .to('.iv3-ln2', { xPercent: 18, ease: 'none' }, 0)
      .to('#iv3HeroIn', { y: -120, autoAlpha: 0.1, ease: 'none' }, 0)
      .to('#iv3Field', { scale: 1.25, ease: 'none' }, 0);
  });

  /* problem: words light up */
  later(function () {
    if (!words.length) return;
    G.set(words, { opacity: 0.12 });
    G.set('#iv3ProbEnd', { scale: 0.6, autoAlpha: 0, rotate: -4 });
    var tl = G.timeline({ scrollTrigger: { trigger: '#iv3Prob', start: 'top top', end: '+=170%', pin: true, scrub: true } });
    tl.to(words, { opacity: 1, stagger: 0.12, duration: 0.3, ease: 'none' })
      .to('#iv3ProbEnd', { scale: 1, autoAlpha: 1, rotate: 0, duration: 1.2, ease: 'back.out(2)' }, '+=0.2')
      .to({}, { duration: 0.6 });
  });

  /* services: horizontal */
  later(function () {
  var mm = G.matchMedia();
  mm.add('(min-width: 901px)', function () {
    var track = $('iv3ServTrack'), pin = $('iv3ServPin');
    if (!track) return;
    function dist() { return Math.max(0, track.scrollWidth - window.innerWidth); }
    var tween = G.to(track, {
      x: function () { return -dist(); }, ease: 'none',
      scrollTrigger: { trigger: pin, start: 'center center', end: function () { return '+=' + dist(); }, pin: true, scrub: true, invalidateOnRefresh: true, anticipatePin: 1,
        onUpdate: function (s) { var b = $('iv3ServBar'); if (b) b.style.transform = 'scaleX(' + s.progress.toFixed(3) + ')'; } }
    });
    qa('.iv3-card').forEach(function (card) {
      var pxEl = card.querySelector('.iv3-px');
      ST.create({ trigger: card, containerAnimation: tween, start: 'left 80%', onEnter: function () { pxEl.classList.add('iv3-on'); }, onLeaveBack: function () { pxEl.classList.remove('iv3-on'); } });
    });
  });
  mm.add('(max-width: 900px)', function () {
    qa('.iv3-card').forEach(function (card) {
      card.classList.add('iv3-rv');
      if ('IntersectionObserver' in window) {
        var o = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { card.classList.add('iv3-in'); card.querySelector('.iv3-px').classList.add('iv3-on'); o.disconnect(); } }, { rootMargin: '0px 0px -12% 0px' });
        o.observe(card);
      } else { card.classList.add('iv3-in'); card.querySelector('.iv3-px').classList.add('iv3-on'); }
    });
  });

  });

  /* process scene */
  later(function () {
    var S = qa('.iv3-stage');
    G.set(S, { autoAlpha: 0 }); G.set(S[0], { autoAlpha: 1 });
    var msgs = qa('.iv3-s1 .iv3-msg, .iv3-s1 .iv3-typing');
    var rows = qa('.iv3-doc-row b');
    var path = $('iv3GraphPath'), len = 0;
    if (path && path.getTotalLength) { len = path.getTotalLength(); path.style.strokeDasharray = len; path.style.strokeDashoffset = len; }
    G.set(msgs, { autoAlpha: 0, y: 24, scale: 0.96 });
    G.set(rows, { scale: 0 });
    G.set('.iv3-stamp', { scale: 2.4, autoAlpha: 0, rotate: 8 });
    G.set('.iv3-doc', { y: 60, autoAlpha: 0 });
    G.set(qa('#iv3Chips span'), { x: -30, autoAlpha: 0 });
    G.set('#iv3Graph', { y: 30, autoAlpha: 0 });
    G.set(qa('.iv3-s4 .iv3-site-art i'), { scale: 0 });
    var tl = G.timeline({ scrollTrigger: { trigger: '#iv3ProcPin', start: 'top top', end: '+=330%', pin: true, scrub: true },
      onUpdate: function () { var t = this.time(), L = this.labels; setStep(t >= L.p4 ? 3 : t >= L.p3 ? 2 : t >= L.p2 ? 1 : 0, this.progress()); } });
    tl.to(msgs, { autoAlpha: 1, y: 0, scale: 1, stagger: 0.5, duration: 0.6, ease: 'power2.out' })
      .to({}, { duration: 0.4 })
      .addLabel('p2')
      .to(S[0], { autoAlpha: 0, y: -30, duration: 0.5 })
      .to(S[1], { autoAlpha: 1, duration: 0.3 }, '<0.2')
      .to('.iv3-doc', { y: 0, autoAlpha: 1, duration: 0.6, ease: 'power3.out' }, '<')
      .to(rows, { scale: 1, stagger: 0.3, duration: 0.3, ease: 'back.out(3)' })
      .to('.iv3-stamp', { scale: 1, autoAlpha: 1, rotate: -10, duration: 0.4, ease: 'power4.in' })
      .to({}, { duration: 0.4 })
      .addLabel('p3')
      .to(S[1], { autoAlpha: 0, duration: 0.4 })
      .to(S[2], { autoAlpha: 1, duration: 0.3 }, '<0.1')
      .from(qa('.iv3-s3 .iv3-site-nav, .iv3-s3 .iv3-site-hero > *, .iv3-s3 .iv3-site-cards i'), { y: 10, stagger: 0.08, duration: 0.3 }, '<')
      .to({}, { duration: 0.3 })
      .addLabel('p4')
      .to(S[3], { autoAlpha: 1, duration: 0.6 })
      .to(qa('.iv3-s4 .iv3-site-art i'), { scale: 1, stagger: { amount: 0.6, from: 'random' }, duration: 0.3, ease: 'back.out(3)' }, '<0.2')
      .to(S[2], { autoAlpha: 0, duration: 0.2 })
      .to(qa('#iv3Chips span'), { x: 0, autoAlpha: 1, stagger: 0.25, duration: 0.4, ease: 'power3.out' })
      .to('#iv3Graph', { y: 0, autoAlpha: 1, duration: 0.4 }, '<')
      .to(path || {}, { strokeDashoffset: 0, duration: 0.9, ease: 'none' }, '<0.2')
      .to({}, { duration: 0.5 });
  });

  /* counters */
  later(function () {
    qa('[data-count]').forEach(function (el) {
      el.textContent = '0';
      ST.create({ trigger: el, start: 'top 85%', once: true, onEnter: function () { runCount(el); } });
    });
  });

  /* bands: speed reacts to scroll */
  later(function () {
    measureBands();
    var dir = 1, bandsOn = true, bandsEl = root.querySelector('.iv3-bands');
    if (bandsEl && 'IntersectionObserver' in window) new IntersectionObserver(function (e) { bandsOn = e[0].isIntersecting; }).observe(bandsEl);
    G.ticker.add(function () {
      if (!bandsOn) return;
      var v = lenis ? lenis.velocity : 0;
      if (v > 0.5) dir = 1; else if (v < -0.5) dir = -1;
      var sp = (0.7 + Math.min(14, Math.abs(v) * 0.5)) * dir;
      bands.forEach(function (b) {
        b.x -= sp * b.dir;
        if (b.w) { while (b.x <= -b.w) b.x += b.w; while (b.x > 0) b.x -= b.w; }
        b.el.style.transform = 'translate3d(' + b.x.toFixed(1) + 'px,0,0)';
      });
    });
    G.from('.iv3-band-a', { rotate: -12, scrollTrigger: { trigger: '.iv3-bands', start: 'top bottom', end: 'bottom top', scrub: true } });
    G.from('.iv3-band-b', { rotate: 10, scrollTrigger: { trigger: '.iv3-bands', start: 'top bottom', end: 'bottom top', scrub: true } });
  });

  /* portfolio stack */
  later(function () {
    var cards = qa('.iv3-proj');
    cards.forEach(function (card, i) {
      var inner = card.querySelector('.iv3-proj-in');
      G.from(inner, { y: 80, rotateX: -8, transformPerspective: 1200, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: card, start: 'top 92%' } });
      if (window.innerWidth > 900) G.from(card.querySelector('.iv3-proj-big'), { yPercent: 60, ease: 'none', scrollTrigger: { trigger: card, start: 'top bottom', end: 'top top', scrub: true } });
      if (i < cards.length - 1 && window.innerWidth > 900) {
        var st = { trigger: cards[i + 1], start: 'top 75%', end: 'top ' + (90 + (i + 1) * 14) + 'px', scrub: true };
        G.to(inner, { scale: 0.92, ease: 'none', scrollTrigger: st });
        G.to(card.querySelector('.iv3-proj-shade'), { opacity: 0.55, ease: 'none', scrollTrigger: st });
      }
    });
  });

  /* comparison */
  later(function () {
    var left = qa('.iv3-vs-col:first-child li'), right = qa('.iv3-vs-col + .iv3-vs-col li');
    left.forEach(function (li) { li.querySelector('s').style.setProperty('--strike', '0%'); });
    var tl = G.timeline({ scrollTrigger: { trigger: '#iv3Vs', start: 'top 75%', end: 'bottom 60%', scrub: true } });
    tl.from(left, { x: -30, autoAlpha: 0, stagger: 0.15, duration: 0.4 }, 0)
      .from(right, { x: 30, autoAlpha: 0, stagger: 0.15, duration: 0.4 }, 0.1);
    left.forEach(function (li, k) { tl.to(li.querySelector('s'), { '--strike': '100%', duration: 0.4, ease: 'none' }, 0.3 + k * 0.15); });
  });

  /* contact giant text */
  later(function () {
    var mob = window.innerWidth <= 900;
    G.fromTo('#iv3Giant', { xPercent: mob ? 0 : 4 }, { xPercent: mob ? -18 : -38, ease: 'none', scrollTrigger: { trigger: '#contacto', start: 'top bottom', end: 'bottom top', scrub: true } });
  });

  /* generic reveals: CSS classes + one IntersectionObserver (no per-element tweens) */
  later(function () {
    var els = qa('.iv3-label, .iv3-h2, .iv3-work-head p, .iv3-ba > div:first-child > *, .iv3-cmp, .iv3-contact-info p, .iv3-way, .iv3-form, .iv3-num, .iv3-vs-head')
      .filter(function (el) { return !el.closest('#iv3ServTrack') && !el.closest('#inicio') && !el.closest('#iv3Prob') && !el.closest('.iv3-vs-head .iv3-h2'); });
    if (!('IntersectionObserver' in window)) return;
    els.forEach(function (el) { el.classList.add('iv3-rv'); });
    var io = new IntersectionObserver(function (es) {
      var k = 0;
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.style.transitionDelay = (k++ * 0.08).toFixed(2) + 's';
        e.target.classList.add('iv3-in'); io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  });

  requestAnimationFrame(function () { setTimeout(runQ, 0); });

  /* main ticker (pixel field waits until the page has settled) */
  var fieldOn = false;
  function startField() { fieldOn = true; }
  if (document.readyState === 'complete') setTimeout(startField, 1200); else window.addEventListener('load', function () { setTimeout(startField, 1200); });
  G.ticker.add(function (t) {
    if (field && fieldOn) field.tick(performance.now());
    if (cur && mp.on) {
      mp.rx = lerp(mp.rx, mp.x, 0.22); mp.ry = lerp(mp.ry, mp.y, 0.22);
      cur.style.transform = 'translate3d(' + mp.rx.toFixed(1) + 'px,' + mp.ry.toFixed(1) + 'px,0)';
    }
  });

  /* sizing: ScrollTrigger already refreshes on load; refresh again only if late fonts change layout */
  var rT, lastW = window.innerWidth;
  function onResize() { if (field) field.size(); qa('.iv3-proj-art canvas').forEach(function (cv) { if (cv.iv3drawn) safe(function () { drawArt(cv); }); }); measureBands(); }
  window.addEventListener('resize', function () {
    if (Math.abs(window.innerWidth - lastW) < 2) return;
    lastW = window.innerWidth; clearTimeout(rT); rT = setTimeout(onResize, 200);
  });
  if (document.fonts && document.fonts.status !== 'loaded') document.fonts.ready.then(function () { measureBands(); ST.refresh(); });
  drawAllArt();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iv3main); else iv3main();
})();
