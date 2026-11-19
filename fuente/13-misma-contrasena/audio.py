# -*- coding: utf-8 -*-
"""Música y efectos sintetizados + voz. Genera audio_sin.wav (sin voz) y audio_voz.wav (con voz)."""
import json, re, pathlib, wave
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt

V = pathlib.Path(__file__).resolve().parent
js = (V / 'timing.js').read_text(encoding='utf-8')
T = json.loads(re.search(r'window\.T = (.*?);\n', js).group(1))
VOICE = json.loads(re.search(r'window\.VOICE = (.*?);\n', js).group(1))
SR = 44100
DUR = T['dur']
N = int(SR * DUR)
rng = np.random.default_rng(13)

def add(buf, t, sig, gain=1.0):
    i = int(t * SR)
    if i >= len(buf) or i < 0: return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i] * gain

def env(n, a=0.005, r=None, curve=4.0):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4))
    if r is None: r = n / SR
    return e * np.exp(-curve * t / r)

def tone(f, d, w='sine'):
    t = np.arange(int(d * SR)) / SR
    ph = 2 * np.pi * np.cumsum(np.full(len(t), f) if np.isscalar(f) else f) / SR
    if w == 'sine': return np.sin(ph)
    if w == 'square': return np.sign(np.sin(ph))
    if w == 'saw': return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if w == 'tri': return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1

def noise(d): return rng.uniform(-1, 1, int(d * SR))
def lp(x, fc, order=2): return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)
def nf(n): return 440 * 2 ** ((n - 69) / 12)

music = np.zeros(N); sfx = np.zeros(N)

# ---------- música: "Domino Voltage" (ElevenLabs Music, licencia comercial del plan) ----------
trk, tsr = sf.read(V / 'musica' / 'domino_voltage.wav')
trk = trk.mean(1) if trk.ndim > 1 else trk
if tsr != SR: trk = resample_poly(trk, 147, 160) if tsr == 48000 else trk
music[:min(N, len(trk))] = trk[:N]
tt = np.arange(N) / SR
susp = np.clip((tt - T['p0'] + .3) / .3, 0, 1) * np.clip((T['p1'] + .15 - tt) / .15, 0, 1)
music = music * (1 - .55 * susp)
music = music - susp * .5 * hp(music, 1800)
gap = np.clip((tt - (T['p1'] - .25)) / .05, 0, 1) * np.clip((T['p1'] - tt) / .05, 0, 1)
music *= 1 - .8 * gap
E = T['end']

# ---------- sfx ----------
def ding(f=1320, g=.5): return (tone(f, .5) + .5 * tone(f * 1.5, .5)) * env(int(.5 * SR), .002, .3, 4) * g
def pop(f=880, g=.5):
    d = .09; tt2 = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 1.2 * np.exp(-tt2 * 60))) / SR) * env(int(d * SR), .001, .05, 3) * g
def whoosh(d=.45, up=True):
    n = noise(d); x = np.linspace(0, 1, len(n))
    out = lp(n, 900) if not up else hp(lp(n, 4000), 300)
    return out * np.sin(np.pi * x) ** 2 * 1.2
def click(): return hp(noise(.02), 3000) * env(int(.02 * SR), .0005, .006, 3) * .9
def impact(g=1.0):
    d = 1.0; tt2 = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-tt2 * 12)) / SR) * np.exp(-tt2 * 3.5) + lp(noise(d), 1500) * np.exp(-tt2 * 10) * .5) * g
def tick(): return tone(1800, .04) * env(int(.04 * SR), .001, .02, 3) * .6
def sparkle():
    x = np.zeros(int(.7 * SR))
    for k, f in enumerate([2093, 2637, 3136, 4186]):
        a = tone(f, .3) * env(int(.3 * SR), .001, .15, 4) * .22; i = int(k * .07 * SR); x[i:i + len(a)] += a
    return x
def domino_thud(g=1.0):
    """Golpe seco y corto: la ficha cae y choca contra la siguiente."""
    d = .35; tt2 = np.arange(int(d * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(95 + 60 * np.exp(-tt2 * 20)) / SR) * np.exp(-tt2 * 14)
    crack = np.zeros(len(body)); c = hp(noise(.05), 2500) * env(int(.05 * SR), .0005, .02, 3); crack[:len(c)] = c
    return (body * .8 + crack * .9) * g
def keytype(g=.35): return hp(noise(.03), 2200) * env(int(.03 * SR), .0005, .015, 3) * g

add(sfx, 0.04, impact(.6))
add(sfx, T['rewind'] - .1, whoosh(.4), .5)
for i in range(5):
    tpos = T['formIn'] + i * .22
    if tpos < T['rewindEnd'] - .2: add(sfx, tpos, keytype(.4))
add(sfx, T['rowIn'] - .15, whoosh(.5), .5)
FALLS = [T['fall1'], T['fall2'], T['fall3'], T['fall4'], T['fall5'], T['fall6'], T['fall7']]
for i, f in enumerate(FALLS):
    add(sfx, f, domino_thud(.85 + i * .02))
    add(sfx, f + .03, tick(), .7)
add(sfx, T['q0'] + .2, whoosh(.35), .3)
for i in range(5): add(sfx, T['p0'] + i, tick(), 1.0)
add(sfx, T['explode'] - .03, impact(1.0)); add(sfx, T['explode'] + .02, sparkle(), .6)
for w in [T['t1'][0], T['t2'][0], T['t3'][0]]:
    add(sfx, w - .05, whoosh(.45), .5); add(sfx, w + .35, ding(1568, .28))

# ---------- voz ----------
voice = np.zeros(N)
for k, (st, d) in VOICE.items():
    a, sr = sf.read(V / 'voz' / f'{k}.wav')
    a = resample_poly(a, 147, 80) if sr == 24000 else a
    add(voice, st, a)
voice = hp(voice, 85)
lvl = np.sqrt(np.maximum(lp(voice ** 2, 8), 1e-9)); g = np.where(lvl > .12, (.12 / lvl) ** .45, 1.0); voice *= g
voice = voice + .18 * hp(voice, 3500)
voice /= np.max(np.abs(voice)) + 1e-9

venv = lp(np.abs(voice), 3, 1); venv = np.minimum(1, venv / (venv.max() * .25 + 1e-9))
duck = 1 - .72 * lp(venv, 2, 1)

def finish(mix, name):
    mix = np.tanh(mix * 1.05) * .92
    fade = np.ones(N); fl = int(.8 * SR); fade[-fl:] = np.linspace(1, 0, fl); fi = int(.03 * SR); fade[:fi] = np.linspace(0, 1, fi)
    mix = mix * fade; mix = mix / np.max(np.abs(mix)) * .89
    st = np.stack([mix, mix], axis=1)
    with wave.open(str(V / name), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

finish(music * .55 + sfx * .85, 'audio_sin.wav')
finish(music * .29 * duck + sfx * .5 * (1 - .4 * (duck < .7)) + voice * .95, 'audio_voz.wav')
print('ok', DUR)

m = venv > .5
bgd = (music * .29 * duck + sfx * .5 * (1 - .4 * (duck < .7)))[m]
print('voz/fondo dB', round(20 * np.log10(np.sqrt(np.mean((voice[m] * .95) ** 2)) / np.sqrt(np.mean(bgd ** 2))), 1), 'nan', np.isnan(voice).sum())
