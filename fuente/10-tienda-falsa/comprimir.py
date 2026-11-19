"""Acorta los silencios largos de la toma de voz (deja máx. 0,28 s) y opcionalmente acelera (atempo).
Uso: python3 comprimir.py entrada.mp3 salida.wav [tempo]"""
import sys, subprocess, numpy as np, soundfile as sf
src, dst = sys.argv[1], sys.argv[2]; tempo = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-ac', '1', '-ar', '44100', '/tmp/_v.wav'], check=True)
a, sr = sf.read('/tmp/_v.wav'); hop = int(.01 * sr)
e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
q = e < max(.003, np.percentile(e, 95) * .04)
keep = np.ones(len(a), bool); i = 0; cut = 0
while i < len(q):
    if q[i]:
        j = i
        while j < len(q) and q[j]: j += 1
        if j - i > 28 and i > 0 and j < len(q):
            m = (i + j) // 2; half = 14
            keep[(i + half) * hop:(m) * hop] = False; keep[m * hop:(j - half) * hop] = False; cut += (j - i - 28) * .01
        i = j
    else: i += 1
b = a[keep]
sf.write('/tmp/_c.wav', b, sr)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', '/tmp/_c.wav', '-af', f'atempo={tempo}', dst], check=True)
print('recortado', round(cut, 2), 's; duración', round(len(b) / sr / tempo, 2))
