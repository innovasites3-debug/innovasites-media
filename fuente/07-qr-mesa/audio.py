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
rng = np.random.default_rng(9)

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

# ---------- instruments ----------
def kick(g=1.0):
    d = .35; t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t * 30)) / SR) * np.exp(-t * 9) * g
HAT = hp(noise(.05), 7000) * env(int(.05 * SR), .001, .03, 3)
SNARE = (lp(noise(.2), 3000) * .8 + tone(190, .2) * .4) * env(int(.2 * SR), .001, .12, 4)
RIM = hp(noise(.03), 2000) * env(int(.03 * SR), .0005, .012, 3) + tone(1700, .03) * env(int(.03 * SR), .0005, .01, 3) * .4
def pluck(f, d=.3, g=.5, w='tri'): return lp(tone(f, d, w), 3500) * env(int(d * SR), .003, d * .6, 4) * g
def keys(f, d=.9, g=.3):  # suave tipo Rhodes
    x = tone(f, d) + .35 * tone(f * 2, d) * np.exp(-np.arange(int(d * SR)) / SR * 6) + .1 * tone(f * 3, d)
    return x * env(int(d * SR), .006, d * .7, 3) * g
def bass(f, d=.4, g=.55): return lp(tone(f, d, 'saw') * .5 + tone(f, d), 400) * env(int(d * SR), .004, d * .8, 3) * g
def pad(notes, d, g=.12):
    x = sum(tone(nf(n) * (1 + .002 * k), d, 'saw') for k, n in enumerate(notes))
    a = np.minimum(1, np.arange(len(x)) / (.6 * SR)); r = np.minimum(1, (len(x) - np.arange(len(x))) / (.6 * SR))
    return lp(x, 1200) * a * r * g

music = np.zeros(N); sfx = np.zeros(N)

# ---------- música: "Café QR" (ElevenLabs Music, licencia comercial del plan) ----------
trk, tsr = sf.read(V / 'musica' / 'cafe_qr.wav')
trk = trk.mean(1) if trk.ndim > 1 else trk
if tsr != SR: trk = resample_poly(trk, 147, 160) if tsr == 48000 else trk
music[:min(N, len(trk))] = trk[:N]
# suspenso en la cuenta regresiva: baja volumen y agudos
tt = np.arange(N) / SR
susp = np.clip((tt - T['p0'] + .3) / .3, 0, 1) * np.clip((T['p1'] + .15 - tt) / .15, 0, 1)
music = music * (1 - .55 * susp) + 0
music = music - susp * .5 * hp(music, 1800)
# pequeño corte de música justo antes del golpe del resultado
gap = np.clip((tt - (T['p1'] - .25)) / .05, 0, 1) * np.clip((T['p1'] - tt) / .05, 0, 1)
music *= 1 - .8 * gap
E = T['end']

# ---------- sfx ----------
def ding(f=1320, g=.5): return (tone(f, .5) + .5 * tone(f * 1.5, .5)) * env(int(.5 * SR), .002, .3, 4) * g
def notif(g=.6):
    x = np.zeros(int(.5 * SR)); a = ding(1047, 1); b2 = ding(1568, 1)
    x[:len(a)] += a; i = int(.11 * SR); x[i:] += b2[:len(x) - i]; return x * g
def pop(f=880, g=.5):  # burbuja de chat
    d = .09; tt = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 1.2 * np.exp(-tt * 60))) / SR) * env(int(d * SR), .001, .05, 3) * g
def sendsnd():
    d = .18; tt = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(500 + 1400 * tt / d) / SR) * np.sin(np.pi * tt / d) * .35
def buzz(d):
    tt = np.arange(int(d * SR)) / SR
    return lp(tone(160, d, 'square'), 300) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 7 * tt))) * .6
def whoosh(d=.45, up=True):
    n = noise(d); x = np.linspace(0, 1, len(n))
    out = lp(n, 900) if not up else hp(lp(n, 4000), 300)
    return out * np.sin(np.pi * x) ** 2 * 1.2
def click(): return hp(noise(.02), 3000) * env(int(.02 * SR), .0005, .006, 3) * .9
def impact(g=1.0):
    d = 1.0; tt = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-tt * 12)) / SR) * np.exp(-tt * 3.5) + lp(noise(d), 1500) * np.exp(-tt * 10) * .5) * g
def alert():
    a = tone(880, .09, 'square') * .25; z = np.zeros(int(.05 * SR)); b2 = tone(660, .12, 'square') * .25
    x = np.concatenate([a, z, b2]); return lp(x, 3000) * env(len(x), .002, .3, 1)
def tick(): return tone(1800, .04) * env(int(.04 * SR), .001, .02, 3) * .6
def sparkle():
    x = np.zeros(int(.7 * SR))
    for k, f in enumerate([2093, 2637, 3136, 4186]):
        a = tone(f, .3) * env(int(.3 * SR), .001, .15, 4) * .22; i = int(k * .07 * SR); x[i:i + len(a)] += a
    return x
def wah():
    out = []
    for i, n in enumerate([62, 61, 60, 59]):
        d = .3 if i < 3 else .9; tt = np.arange(int(d * SR)) / SR
        out.append(lp(tone(nf(n), d, 'saw'), 900) * np.minimum(1, tt / .03) * np.exp(-tt * (1.4 if i == 3 else 4)))
    return np.concatenate(out) * .7

def beep():  # lectura del QR
    return (tone(1975, .07) + .4 * tone(3950, .07)) * env(int(.07 * SR), .001, .05, 2) * .5
add(sfx, 0.04, impact(.7)); add(sfx, T['qr'] + .35, sparkle(), .9); add(sfx, T['qr'] + .4, pop(1300, .5))
add(sfx, T['phoneIn'] - .15, whoosh(.45), .5)
add(sfx, T['cam'] - .2, whoosh(.4), .4)
add(sfx, T['det'], beep(), 1.0); add(sfx, T['det'] + .2, pop(1100, .45))
add(sfx, T['tapBan'], click(), .9); add(sfx, T['web'], whoosh(.4), .4)
add(sfx, T['back'], whoosh(.3, False), .35)
add(sfx, T['z1'], whoosh(.5), .4); add(sfx, T['z1'] + .45, alert(), .85)
add(sfx, T['z1'] + (T['z1e'] - T['z1']) * .5, alert(), .7)
add(sfx, T['fwd'], whoosh(.35), .35)
add(sfx, T['z2'], whoosh(.5), .4); add(sfx, T['z2'] + .45, alert(), .85)
n = int((T['ty1'] - T['ty0']) / .1)
for i in range(n): add(sfx, T['ty0'] + i * (T['ty1'] - T['ty0']) / n + rng.uniform(0, .02), click(), .35)
add(sfx, T['pay'], click(), 1.0)
add(sfx, T['bank'] - .05, impact(.9))
for i, k in enumerate(['n1', 'n2', 'n3', 'n4']): add(sfx, T[k], notif(.45 + i * .05)); add(sfx, T[k] + .04, buzz(.35), .25)
add(sfx, T['n4'], impact(1.0)); add(sfx, T['n4'] + .1, wah(), .45)
add(sfx, T['bankEnd'] - .45, whoosh(.5), .5)
add(sfx, T['q0'] + .2, whoosh(.35), .3)
for i in range(3): add(sfx, T['q0'] + .35 + i * .15, whoosh(.3), .3)
for i in range(4): add(sfx, T['p0'] + i, tick(), 1.0)
add(sfx, T['p1'], impact(.9)); add(sfx, T['p1'] + .05, sparkle(), .55)
for w in [T['t1'][0], T['t2'][0], T['t3'][0]]:
    add(sfx, w - .05, whoosh(.45), .5); add(sfx, w + .35, ding(1568, .28))

# ---------- voz ----------
voice = np.zeros(N)
for k, (st, d) in VOICE.items():
    a, sr = sf.read(V / 'voz' / f'{k}.wav')
    a = resample_poly(a, 147, 80) if sr == 24000 else a
    add(voice, st, a)
voice = hp(voice, 85)
# compresión suave y brillo leve para que suene cercana y natural
lvl = np.sqrt(np.maximum(lp(voice ** 2, 8), 1e-9)); g = np.where(lvl > .12, (.12 / lvl) ** .45, 1.0); voice *= g
voice = voice + .18 * hp(voice, 3500)
voice /= np.max(np.abs(voice)) + 1e-9

# envolvente de voz para bajar la música (ducking)
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

# control: relación voz / fondo mientras habla
m = venv > .5
bgd = (music * .29 * duck + sfx * .5 * (1 - .4 * (duck < .7)))[m]
print('voz/fondo dB', round(20 * np.log10(np.sqrt(np.mean((voice[m] * .95) ** 2)) / np.sqrt(np.mean(bgd ** 2))), 1), 'nan', np.isnan(voice).sum())
