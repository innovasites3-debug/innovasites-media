"""Corta la voz por frases usando las marcas de tiempo por palabra de la transcripción (ElevenLabs Scribe)
y guarda la hora exacta de cada palabra para los subtítulos.
Entrada: voz/pruebas/<toma>.mp3 (original), voz/palabras_scribe.json ([[palabra, inicio, fin], ...] sobre el original).
Aplica el mismo acortado de silencios + tempo que comprimir.py, para que todo quede sincronizado.
Uso: python3 alinear.py voz/pruebas/r10_vozB.mp3 [tempo]"""
import sys, json, re, subprocess, difflib, pathlib
import numpy as np, soundfile as sf
from guion import LINES, SAY
V = pathlib.Path(__file__).resolve().parent
src = sys.argv[1]; tempo = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
SR = 44100
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '/tmp/_v.wav'], check=True)
a, _ = sf.read('/tmp/_v.wav'); hop = int(.01 * SR)
e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
q = e < max(.003, np.percentile(e, 95) * .04)
keep = np.ones(len(a), bool); i = 0
while i < len(q):
    if q[i]:
        j = i
        while j < len(q) and q[j]: j += 1
        if j - i > 28 and i > 0 and j < len(q):
            keep[(i + 14) * hop:(j - 14) * hop] = False
        i = j
    else: i += 1
cum = np.concatenate([[0], np.cumsum(keep)])
def nt(t):  # tiempo original -> tiempo en la voz procesada
    k = int(min(len(a), max(0, round(t * SR)))); return cum[k] / SR / tempo
sf.write('/tmp/_c.wav', a[keep], SR)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', '/tmp/_c.wav', '-af', f'atempo={tempo}', '-ar', str(SR), str(V / 'voz' / 'procesada.wav')], check=True)
proc, _ = sf.read(V / 'voz' / 'procesada.wav')

W = json.load(open(V / 'voz' / 'palabras_scribe.json', encoding='utf-8'))
norm = lambda w: re.sub(r'[^a-z0-9áéíóúüñ%$]', '', w.lower().replace('*', ''))
EXT = {'L9'}   # frases grabadas aparte (ver l9.py)
NEXT_AFTER = 99   # en la toma original, ahí empezaba la frase vieja de L9 ("Cada…")
pos = 0; dur = {}; pal = {}; spans = []
for k, txt in LINES:
    if k in EXT: continue
    said = SAY.get(k, txt).replace('*', '').split()
    ws = W[pos:pos + len(said)]; pos += len(said)
    bad = [(x, y[0]) for x, y in zip(said, ws) if norm(x) != norm(y[0])]
    if bad: print('AVISO', k, bad)
    spans.append((k, txt, said, ws))
assert pos == len(W), ('sobran/faltan palabras', pos, len(W))
for n, (k, txt, said, ws) in enumerate(spans):
    a0 = nt(ws[0][1]) - .04
    b0 = nt(ws[-1][2]) + .08
    if n + 1 < len(spans): b0 = min(b0, nt(spans[n + 1][3][0][1]) - .04)
    else: b0 = min(b0, nt(NEXT_AFTER) - .14)   # no meter el inicio de la frase que se grabó aparte
    a0 = max(0, a0); seg = proc[int(a0 * SR):int(b0 * SR)].copy()
    f = int(.012 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    sf.write(V / 'voz' / f'{k}.wav', seg, SR); dur[k] = round(len(seg) / SR, 3)
    # hora de cada palabra mostrada (relativa al inicio del corte)
    disp = txt.split(' ')
    sm = difflib.SequenceMatcher(a=[norm(x) for x in disp], b=[norm(x) for x in said], autojunk=False)
    tt = [None] * len(disp)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        for d in range(i1, i2):
            j = j1 + (d - i1) if op == 'equal' else min(j1, len(ws) - 1)
            tt[d] = round(nt(ws[j][1]) - a0, 3)
    pal[k] = tt
old = json.load(open(V / 'voz' / 'duraciones.json')) if (V / 'voz' / 'duraciones.json').exists() else {}
old_p = json.load(open(V / 'voz' / 'palabras.json')) if (V / 'voz' / 'palabras.json').exists() else {}
for k in EXT:
    if k in old: dur[k] = old[k]
    if k in old_p: pal[k] = old_p[k]
json.dump(dur, open(V / 'voz' / 'duraciones.json', 'w'))
json.dump(pal, open(V / 'voz' / 'palabras.json', 'w'))
print(dur)
