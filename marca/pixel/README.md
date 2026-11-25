# Pixel — avatar de InnovaSites

Mascota de la marca (versión 4 voxel, aprobada nov 2026). Primer uso: reel 15 "La web sin candado" (`fuente/15-web-sin-candado/`).

| Archivo | Qué es |
| --- | --- |
| `pixel.js` | El dibujo de Pixel: paleta, `sprite()` (cuadrícula 27x32), caras, `pixelHead/Body/Limb` (partes en SVG voxel) y `pixelSVG` (figura completa antigua, con halo: no usar en reels). |
| `pixel-figura.js` | Arma a Pixel por partes en un `div` y da `cara()` y `pose()` para animarlo. |
| `caras.html` | Hoja con las 21 caras (abrir en el navegador). Imagen: `img/pixel-caras.png`. |
| `poses.html` + `exportar_png.py` | 12 poses listas; el script saca PNG transparentes a `png/`. |
| `png/` | PNG transparentes (2x) para miniaturas, portadas, historias y web. |
| `img/` | Diseño aprobado v4 y propuestas descartadas v1–v3 (solo referencia). |
| `fonts/` | Oswald, Space Mono e Inter usadas en los reels. |

Animación completa (teletransporte, caminar, tecleo, boca con la voz): ver `drawPixel`, `MOVES`, `FACES`, `ARMS`, `tpFx` en `fuente/15-web-sin-candado/scene.html`, y `boca.py` para la boca.

Caras: `{ eyes, mouth, icon, dx, dy }`
- eyes: open, blink, wide, wink, happy, angry, sad, sus, heart, x, star, think
- mouth: smile, mid, talk, o, wide, flat, frown, smirk, grin, zig, ee
- icon (reemplaza la cara): lock, warn, check, q
