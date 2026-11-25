"""Cierre grabado aparte: "InnovaSites… cada pixel cuenta." (toma A). Marca las palabras por las pausas medidas."""
import json, subprocess, pathlib, numpy as np, soundfile as sf
V = pathlib.Path(__file__).resolve().parent
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(V / 'voz/pruebas/r15_L9_a.mp3'), '-ac', '1', '-ar', '44100', '/tmp/_l9.wav'], check=True)
a, sr = sf.read('/tmp/_l9.wav'); seg = a[:int(2.78 * sr)].copy(); f = int(.012 * sr); seg[-f:] *= np.linspace(1, 0, f)
sf.write(V / 'voz' / 'L9.wav', seg, sr)
d = json.load(open(V / 'voz' / 'duraciones.json')); d['L9'] = round(len(seg) / sr, 3); json.dump(d, open(V / 'voz' / 'duraciones.json', 'w'))
p = json.load(open(V / 'voz' / 'palabras.json')); p['L9'] = [0.03, 1.35, 1.74, 2.28]; json.dump(p, open(V / 'voz' / 'palabras.json', 'w'))
print('L9', d['L9'])
