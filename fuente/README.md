# Código fuente de los videos y del sitio

Cada carpeta de video tiene:

- `scene.html`: la animación completa. `window.render(t)` dibuja el segundo `t`. Ábrela en Chrome y llama `render(10)` en la consola para ver el segundo 10.
- `audio.py`: música y efectos sintetizados con numpy. Genera `audio.wav`.
- `render.py`: captura cada fotograma con Playwright (1080x1920, 30 fps, 4 procesos), lo codifica con ffmpeg y mezcla el audio. Genera el `.mp4` final.
- `stills.py`: capturas sueltas para revisar sin renderizar todo.
- `fonts/`: Oswald, Inter y Space Mono (licencia OFL).

## Requisitos

```
pip install playwright numpy scipy soundfile
playwright install chromium   # o define CHROME=/ruta/a/chrome
# ffmpeg instalado en el sistema
```

## Renderizar

```
cd fuente/03-hola-mama
python3 audio.py
python3 render.py
```

## sitio-web

Bloques de WordPress (HTML personalizado) del homepage de innovasites.co: header, página y footer. `python3 build.py` genera `dist/`. El JS va en Base64 porque WordPress cambia los `&` en scripts en línea.
