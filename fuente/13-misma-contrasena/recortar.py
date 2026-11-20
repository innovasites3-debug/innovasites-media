"""Vuelve a cortar la toma de ElevenLabs con cortes fijos (corrige los que dividir.py eligió mal).
Uso: python recortar.py voz/elevenlabs_lina.mp3"""
import sys, json, subprocess, pathlib
import numpy as np, soundfile as sf
from guion import LINES
V = pathlib.Path(__file__).resolve().parent
# Cortes en las pausas entre frases, tomados de una transcripción con tiempos por palabra (Whisper).
CUTS = [4.44, 8.07, 10.24, 15.43, 18.38, 19.48, 22.16, 26.46, 28.86, 32.18, 36.58, 40.59, 43.66]
wav = V / 'voz' / 'elevenlabs_full.wav'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', '44100', str(wav)], check=True)
a, sr = sf.read(wav)
hop = int(.01 * sr)
e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
thr = max(.003, np.percentile(e, 95) * .04)
bounds = [0] + [int(c * sr) for c in CUTS] + [len(a)]
dur = {}
for (k, _), b0, b1 in zip(LINES, bounds[:-1], bounds[1:]):
    seg = a[b0:b1]; idx = np.where(np.abs(seg) > thr)[0]
    seg = seg[max(0, idx[0] - int(.08 * sr)):min(len(seg), idx[-1] + int(.12 * sr))]
    n = int(.01 * sr); seg[:n] *= np.linspace(0, 1, n); seg[-n:] *= np.linspace(1, 0, n)
    sf.write(V / 'voz' / f'{k}.wav', seg, sr); dur[k] = round(len(seg) / sr, 3)
wav.unlink()
print(dur)
(V / 'voz' / 'duraciones.json').write_text(json.dumps(dur, indent=1))
