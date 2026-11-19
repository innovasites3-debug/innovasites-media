"""Divide la narración de ElevenLabs (una sola toma) en las frases del guion.
Busca los silencios y elige, para cada fin de frase, la pausa que mejor coincide con
dónde debería terminar según la longitud del texto (programación dinámica).
Uso: python3 dividir.py voz/elevenlabs_lina.mp3"""
import sys, json, subprocess, pathlib
import numpy as np, soundfile as sf
from guion import LINES, clean
V = pathlib.Path(__file__).resolve().parent
src = pathlib.Path(sys.argv[1]); wav = V / 'voz' / 'elevenlabs_full.wav'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(src), '-ac', '1', '-ar', '44100', str(wav)], check=True)
a, sr = sf.read(wav); hop = int(.01 * sr)
e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
thr = max(.003, np.percentile(e, 95) * .04); quiet = e < thr
gaps, i = [], 0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]: j += 1
        if i > 0 and j < len(quiet) and j - i >= 8: gaps.append(((i + j) / 2 * .01, (j - i) * .01))
        i = j
    else: i += 1
voiced = np.where(~quiet)[0]; t0, t1 = voiced[0] * .01, voiced[-1] * .01
# duración esperada de cada frase por sílabas y pausas de puntuación
import re
def units(t):
    t = clean(t).lower()
    return len(re.findall(r'[aeiouáéíóúü]+', t)) + 1.6 * len(re.findall(r'[.?:]', t)) + 2.2 * t.count('…') + .8 * t.count(',')
U = [units(t) for _, t in LINES]
rate = (t1 - t0) / sum(U)                     # segundos por unidad
B, G = len(LINES) - 1, len(gaps)
starts = [t0] + [gaps[g][0] for g in range(G)]
def segcost(prev_t, g, b):                   # frase b va de prev_t hasta el corte g
    d = gaps[g][0] - prev_t
    return abs(d - U[b] * rate) / (U[b] * rate) * 3 - .9 * gaps[g][1]
INF = 1e9; dp = np.full((B, G), INF); prv = np.full((B, G), -1)
for g in range(G): dp[0, g] = segcost(t0, g, 0)
for b in range(1, B):
    for g in range(b, G):
        best = INF; arg = -1
        for h in range(b - 1, g):
            if dp[b - 1, h] >= INF: continue
            c = dp[b - 1, h] + segcost(gaps[h][0], g, b)
            if c < best: best, arg = c, h
        dp[b, g] = best; prv[b, g] = arg
# última frase hasta el final
fin = [dp[B - 1, g] + abs((t1 - gaps[g][0]) - U[B] * rate) / (U[B] * rate) * 3 if dp[B - 1, g] < INF else INF for g in range(G)]
g = int(np.argmin(fin)); sel = [g]
for b in range(B - 1, 0, -1): g = int(prv[b, g]); sel.append(g)
sel = sel[::-1]
exp = np.cumsum([t0] + [U[b] * rate for b in range(B)])[1:]
cuts = [gaps[g][0] for g in sel]
print('cortes (s):', [round(c, 2) for c in cuts])
print('pausa en cada corte (s):', [round(gaps[g][1], 2) for g in sel])
print('desvío vs esperado (s):', [round(gaps[g][0] - x, 2) for g, x in zip(sel, exp)])
bounds = [0] + [int(c * sr) for c in cuts] + [len(a)]
dur = {}
for (k, _), b0, b1 in zip(LINES, bounds[:-1], bounds[1:]):
    seg = a[b0:b1]; idx = np.where(np.abs(seg) > thr * 1.5)[0]
    seg = seg[max(0, idx[0] - int(.03 * sr)):min(len(seg), idx[-1] + int(.08 * sr))]
    sf.write(V / 'voz' / f'{k}.wav', seg, sr); dur[k] = round(len(seg) / sr, 3)
print(dur)
(V / 'voz' / 'duraciones.json').write_text(json.dumps(dur, indent=1))
