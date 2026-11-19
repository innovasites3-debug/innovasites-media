"""Comprueba los cortes de dividir.py alineando la narración con una referencia sintética (Kokoro) por DTW.
Uso: python3 verificar.py "<carpeta del modelo Kokoro>" """
import sys, json, numpy as np, librosa
from kokoro_onnx import Kokoro
from guion import LINES, clean
M = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Downloads/KOKORO VOS IA'
k = Kokoro(M + '/kokoro-v1.0.onnx', M + '/voices-v1.0.bin')
SR, H = 22050, 256; ref, bounds, t = [], [], 0
for key, txt in LINES:
    a, sr = k.create(clean(txt).replace('WhatsApp', 'wátsap'), voice='ef_dora', speed=1.0, lang='es-419')
    a = librosa.resample(np.asarray(a, float), orig_sr=sr, target_sr=SR); ref.append(a); t += len(a) / SR; bounds.append(t)
    ref.append(np.zeros(int(.35 * SR))); t += .35
ref = np.concatenate(ref); el, _ = librosa.load('voz/elevenlabs_full.wav', sr=SR)
f = lambda x: librosa.feature.mfcc(y=x, sr=SR, n_mfcc=20, hop_length=H)[1:]
A, B = f(ref), f(el); A = (A - A.mean(1, keepdims=True)) / (A.std(1, keepdims=True) + 1e-6); B = (B - B.mean(1, keepdims=True)) / (B.std(1, keepdims=True) + 1e-6)
_, wp = librosa.sequence.dtw(X=A, Y=B, metric='cosine'); wp = wp[::-1]
est = [wp[wp[:, 0] >= int((b + .17) * SR / H)][0, 1] * H / SR for b in bounds[:-1]]
d = json.load(open('voz/duraciones.json')); cuts, acc = [], 0
import soundfile as sf
print('alineación:', [round(x, 2) for x in est])
