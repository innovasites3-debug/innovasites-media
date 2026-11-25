// Pixel armado por partes (cabeza, cuerpo, 2 brazos, 2 piernas) para animarlo.
// Requiere pixel.js. Uso:
//   const fig = pixelFigura(document.getElementById('donde'), 12.5);
//   fig.cara({ eyes: 'happy', mouth: 'grin' });
//   fig.pose({ brazoI: 12, brazoD: -150, cabeza: 4, piernaI: 0, piernaD: 0 });   // grados
// El contenedor mide 21*px de ancho y 31*px de alto; los pies quedan abajo al centro.
function pixelFigura(el, px = 12.5) {
  el.style.position = el.style.position || 'relative';
  el.style.width = 21 * px + 'px'; el.style.height = 31 * px + 'px';
  const parte = (id, x, y, ox, oy, html) => {
    const d = document.createElement('div'); d.className = 'pp-' + id;
    Object.assign(d.style, { position: 'absolute', left: x * px + 'px', top: y * px + 'px', transformOrigin: `${ox * px}px ${oy * px}px` });
    d.innerHTML = html; return d;
  };
  const P = {
    piernaI: parte('piernaI', 5.6, 27.6, 1.5, 0, pixelLimb('leg', px)),
    piernaD: parte('piernaD', 11.4, 27.6, 1.5, 0, pixelLimb('leg', px)),
    brazoI: parte('brazoI', 1.2, 21.6, 1.5, .5, pixelLimb('arm', px)),
    cuerpo: parte('cuerpo', 4, 21, 6, 7, pixelBody(px)),
    cabeza: parte('cabeza', 0, 0, 10.5, 20.5, pixelHead({}, px)),
    brazoD: parte('brazoD', 16.8, 21.6, 1.5, .5, pixelLimb('arm', px)),
  };
  Object.values(P).forEach(d => el.appendChild(d));          // orden = capas (brazo derecho delante)
  return {
    partes: P,
    cara(o) { P.cabeza.innerHTML = pixelHead(o || {}, px); },
    pose({ brazoI = 12, brazoD = -12, cabeza = 0, piernaI = 0, piernaD = 0, cuerpo = 0 } = {}) {
      P.brazoI.style.transform = `rotate(${brazoI}deg)`; P.brazoD.style.transform = `rotate(${brazoD}deg)`;
      P.cabeza.style.transform = `rotate(${cabeza}deg)`; P.cuerpo.style.transform = `rotate(${cuerpo}deg)`;
      P.piernaI.style.transform = `rotate(${piernaI}deg)`; P.piernaD.style.transform = `rotate(${piernaD}deg)`;
    },
  };
}
