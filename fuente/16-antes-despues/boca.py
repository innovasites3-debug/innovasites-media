"""Calcula la apertura de la boca de Pixel (0..1, 30 por segundo) a partir de la voz y la agrega a timing.js."""
import json, re, pathlib, numpy as np, soundfile as sf
V = pathlib.Path(__file__).resolve().parent
js = (V / 'timing.js').read_text(encoding='utf-8')
T = json.loads(re.search(r'window\.T = (.*?);\n', js).group(1)); VO = json.loads(re.search(r'window\.VOICE = (.*?);\n', js).group(1))
FPS = 30; n = int(T['dur'] * FPS) + 2; m = np.zeros(n)
for k, (st, d) in VO.items():
    a, sr = sf.read(V / 'voz' / f'{k}.wav'); a = a.mean(1) if a.ndim > 1 else a
    hop = sr // FPS
    for i in range(0, len(a) - hop, hop):
        f = int(round(st * FPS)) + i // hop
        if f < n: m[f] = max(m[f], np.sqrt(np.mean(a[i:i + hop] ** 2)))
m = m / (np.percentile(m[m > 0], 90) + 1e-9); m = np.clip(m, 0, 1)
m = np.convolve(m, [.25, .5, .25], 'same')
js = re.sub(r'window\.MOUTH = .*?;\n', '', js) + 'window.MOUTH = ' + json.dumps([round(float(x), 2) for x in m]) + ';\n'
(V / 'timing.js').write_text(js, encoding='utf-8'); print('boca', n)
