# TRASPASO DE LOS REELS — InnovaSites (formato con Pixel)

> Documento para que otro chat continúe la producción de los Reels de InnovaSites sin perder nada.
> Úsalo junto con:
> - **APRENDIZAJES-REELS.md** (en el proyecto Innova: `claude/aprendizajes-reels.md`): qué funciona en los primeros 3 segundos y la fórmula del gancho.
> - **Documento de Pixel** (Claude Docs): https://claude.ai/artifact/4VoEpFhrQtWJVvEFV4RZ8z, con el avatar, las caras, los parámetros y cómo crear caras y animaciones nuevas.
>
> Última actualización: 25 de noviembre de 2026.

---

## 1. Qué es y en qué va

- **Cuenta:** InnovaSites (innovasites.co), agencia de diseño web y contenido en Colombia. Instagram @innova_sites, TikTok @innova.sites.
- **Series:** seguridad digital y estafas (la principal) y diseño web.
- **Formato nuevo (desde el reel 15):**
  - Video vertical 1080×1920, de 30 a 60 s como máximo.
  - Escena "espacio neón": monitor grande, teclado neón, cuadrícula en el piso y cubos flotando.
  - **Pixel**, la mascota (un monitor rojo voxel), actúa, habla con la boca sincronizada, se teletransporta, teclea y reacciona.
  - Voz de Lina (ElevenLabs), música instrumental y **un solo subtítulo arriba**, palabra por palabra, con las palabras clave en rojo.
  - Cierre siempre con la voz: **"InnovaSites… cada pixel cuenta"**.
- **Por qué se cambió:** los reels del formato viejo (pantalla de celular) no pasaban de ~35% de retención a los 3 s. El usuario pidió reels "llamativos y didácticos", como un video viral de referencia con monitor y escenas rápidas.

### Calendario (lunes, miércoles y sábado a las 9:45 a. m., hora Bogotá)

| Fecha | Tema | Estado |
|---|---|---|
| Mié 25 nov | Checklist Black Friday | Publicado (formato viejo) |
| Vie 27 nov | El paquete que regresa | Programado (formato viejo) |
| Lun 30 nov | La misma contraseña en todo | Programado (formato viejo) |
| Mié 2 dic | La verificación en dos pasos | Programado (formato viejo) |
| **Sáb 5 dic** | **Antes y después: así se transforma una web** (reel 16) | **Programado, formato Pixel** |
| **Lun 7 dic** | **La web sin candado** (reel 15) | **Programado, formato Pixel** |
| Mié 9 dic | El trabajo desde casa "fácil" | **Sin hacer (el siguiente)** |
| Sáb 12 dic | ¿Tu marca está lista para 2027? | Sin hacer |
| Lun 14 dic | La tarjeta de regalo navideña | Sin hacer |
| Mié 16 dic | La app falsa | Sin hacer |
| Sáb 19 dic | Regalos digitales seguros | Sin hacer |
| Lun 21 dic | Quiz de fin de año: 5 estafas en 30 s | Sin hacer |

Del 22 al 31 de diciembre no hay nada planeado. El calendario completo está en `calendario/Calendario_InnovaSites.xlsx`, hoja "Calendario". **Antes de proponer una fecha, revisar el calendario y lo que ya está programado en Metricool.**

**Pendiente de medir:** cuando salgan los reels 15 y 16, comparar en Metricool su retención a 3 s y su tiempo promedio visto contra los del formato viejo (ver APRENDIZAJES-REELS.md).

---

## 2. Repositorio

- GitHub: **innovasites3-debug/innovasites-media** (rama `main`).
- Commits como **Xolven.Si <innovasites3@gmail.com>**.
- Siempre hacer `git pull --rebase` antes del push, porque otras personas del equipo también suben cambios.

| Carpeta | Qué tiene |
|---|---|
| `fuente/NN-tema/` | Todo lo de cada reel: guion, escena, voz, música, scripts y portada |
| `fuente/15-web-sin-candado/` | Reel 15, la plantilla original del formato Pixel |
| `fuente/16-antes-despues/` | Reel 16, **la plantilla más reciente: copiar esta para el siguiente** |
| `fuente/sonidos/` | Biblioteca de 16 efectos modernos (whoosh, impacto, pixel, alerta, exito, candado, datos, tecleo; versiones `_a` y `_b`) |
| `marca/pixel/` | El avatar: `pixel.js`, `pixel-figura.js`, hoja de caras, 12 poses en PNG transparente, `README.md` |
| `videos/` | Videos finales comprimidos que se publican |
| `perfil-instagram/portadas-reels/` | Miniaturas de cada reel |
| `calendario/` | Calendario de contenido |

---

## 3. Cómo se hace un reel nuevo (paso a paso)

### 3.1 Guion
1. Copiar `fuente/16-antes-despues/` a `fuente/NN-tema/` (sin `frames/` ni los mp4).
2. En `guion.py`, escribir `LINES` con frases cortas, una por escena (8 frases más el cierre L9). Las palabras entre `*asteriscos*` salen en rojo en el subtítulo. `INTRO = 1.3` s es el tiempo en que Pixel aparece y hace algo antes de que hable la voz.
3. Gancho: seguir la fórmula de APRENDIZAJES-REELS.md (consecuencia en pasado, escena reconocible, juego o pregunta antes del segundo 5).
4. Para la escena del monitor, pensar qué se ve en cada frase y qué hace Pixel.

### 3.2 Voz (ElevenLabs)
- Voz **Lina** `yfUfwZTRubVrsUZWqzwp`, modelo **eleven_v4**.
- Primero `creative_create_flow`, y luego `creative_generate_speech` con **todas las frases menos el cierre**, en un solo texto y con `generations_count: 1` (unos 300 créditos).
- **El cierre no se vuelve a grabar:** se reutiliza `voz/pruebas/r15_L9_a.mp3` con `l9.py`.
- **Transcripción con palabras y tiempos (gratis):** `creative_add_flow_asset_node` con el `generation_id`, y después `creative_transcribe_audio` con `connect_from` apuntando a ese nodo. Las palabras con tiempos se pegan en `voz/palabras_scribe.json` como `[["palabra", inicio, fin], …]`. Hay que quitar etiquetas tipo `[curious]`.
- **Descargar el mp3:**
  1. En el navegador integrado, con elevenlabs.io abierto, se usa `javascript_tool` para hacer `fetch` de la URL, crear un blob y descargarlo con `a.download`.
  2. Cae en `C:\Users\Master\Downloads`, a veces como un `.tmp` del mismo tamaño.
  3. Se trae con `device_stage_files` y se copia a `voz/pruebas/`.
- **Música:** `eleven_music_v2_5` (unos 900 créditos). Para ahorrar se puede reutilizar una toma no usada. El reel 16 usó la toma B del reel 15.

### 3.3 Sincronizar
```
python3 alinear.py voz/pruebas/rNN_voz.mp3   # corta la voz por frases con los tiempos de Scribe
python3 l9.py                                 # agrega el cierre "InnovaSites… cada pixel cuenta"
python3 guion.py                              # escribe timing.js (T, VOICE, SUBS)
python3 boca.py                               # apertura de la boca de Pixel por fotograma
```
- `alinear.py` ya corrige que Scribe marque tarde la primera palabra de una frase ("Uno:", "Dos:"…). Antes eso cortaba el inicio de la palabra. Si se oye un corte, revisar esto primero.
- Las frases van separadas 0,3 s para que el texto se alcance a leer. Ya hubo quejas de transiciones muy rápidas.
- Las palabras con `…`, `?` o `¿` se buscan sin esos signos: `W_('a', 1)` es la segunda "a", no `W_('a…')`.

### 3.4 Escena (`scene.html`)
- `window.render(t)` tiene que ser **una función pura del tiempo `t`**, porque se renderiza en paralelo.
- Lo que se cambia en cada reel:
  - el contenido del monitor (HTML y CSS);
  - `KW[0]`, el gancho que sale arriba antes de la voz;
  - `MOVES`, `FACES` y `ARMS`;
  - `TYPE` y `STRIKES`, si Pixel teclea;
  - el bloque de render de las escenas.
- Los parámetros de Pixel, y cómo crear caras y animaciones nuevas, están en el documento de Pixel.
- **Regla:** las animaciones se ajustan siempre al guion. Si hace falta una nueva, se crea sin borrar las que existen y se anota en el documento.

### 3.5 Sonido, render y video final
```
python3 audio.py                 # efectos con smp('sfx_nombre', volumen) atados a palabras con wt('palabra')
python3 stills.py --voz 2.0 8.5  # fotogramas sueltos para revisar (en frames/)
python3 render.py voz            # video completo, 3 procesos, volumen a -14 LUFS
ffmpeg -i fuente/NN-tema/innovasites-tema.mp4 -c:v libx264 -crf 23 -preset slow -c:a copy -movflags +faststart videos/innovasites-tema.mp4
```
- **Revisar siempre los fotogramas antes de renderizar:** textos cortados, Pixel fuera de cuadro, cosas encimadas.

### 3.6 Miniatura
- Se diseña aparte en `fuente/NN-tema/portada/portada.html` (1080×1920) y se toma una captura con Playwright.
- Lleva el mismo fondo neón, un gancho grande en 2 líneas (blanco y rojo) y una franja roja con la frase corta. Debajo, la escena clave y Pixel grande con una expresión fuerte.
- Lo importante tiene que caber en el centro (y entre 285 y 1635), que es lo que se ve en la cuadrícula del perfil.
- Se copia a `perfil-instagram/portadas-reels/portada-tema.png`.
- **Al usuario no le gustó usar un fotograma del video como miniatura.** Siempre diseñarla.

### 3.7 Publicar (Metricool)
- Marca `7588298`, zona `America/Bogota`, a las **9:45** en Instagram (REEL), Facebook (REEL) y TikTok.
- `media` y `videoThumbnailUrl` son URLs raw de GitHub **fijadas a un commit**: `https://raw.githubusercontent.com/innovasites3-debug/innovasites-media/<hash>/videos/…`.
- Texto con este orden: la consecuencia en la primera línea, la explicación, las reglas con 1️⃣ 2️⃣ 3️⃣, la pregunta y 5 hashtags. Aparte, el primer comentario (la pregunta) y el título de TikTok.
- Se guarda en `fuente/NN-tema/publicacion.md`.
- **Programar solo cuando el usuario lo apruebe en el chat.**

---

## 4. Lo que el usuario ya corrigió (no repetir)

- Pixel **sin halo ni plataforma**: solo una sombra oscura debajo.
- **Nada de movimientos en bucle de lado a lado.** Pixel se mueve libre, con brazos y piernas, y cada gesto va con lo que dice la voz.
- **Teletransporte con píxeles, no volar.**
- Pixel se sienta en la esquina del monitor mientras explica.
- Teclado centrado y soporte del monitor visible.
- **Un solo subtítulo**, arriba.
- Pixel entra antes de que hable la voz: aparece, saluda o teclea.
- Tecleo realista: una pulsación por letra, la tecla se enciende bajo la mano y las piernas quedan ocultas detrás del teclado.
- Sonidos modernos (la biblioteca de `fuente/sonidos/`), no de los de antes.
- Las palabras no se pueden cortar: revisar el inicio de cada frase.
- Nada que parezca falso. Se usan marcas genéricas o inventadas, y si es un ejemplo, se dice en el texto ("Ejemplo con una marca ficticia").

---

## 5. Cómo trabajar con el usuario (Juan)

- Español, directo, con acción. Pocas explicaciones largas.
- **No usar tarjetas interactivas de opciones.** Preguntar en texto normal.
- Para tareas en el navegador del usuario, usar Google Chrome cuando sea en su computador.
- Mostrar el video y la miniatura antes de programar, y programar cuando lo apruebe.
- Nunca escribir contraseñas ni datos de acceso.
- Al terminar cada cambio: commit, push, mandar el video y decir en pocas líneas qué cambió.
