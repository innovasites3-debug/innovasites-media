import numpy as np, wave

SR = 44100
DUR = 56.0
N = int(SR * DUR)
music = np.zeros(N)
sfx = np.zeros(N)
rng = np.random.default_rng(7)

def add(buf, t, sig, gain=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i] * gain

def env(n, a=0.005, r=None, curve=4.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    if r is None: r = n / SR
    e *= np.exp(-curve * t / r)
    return e

def tone(f, d, wave_='sine'):
    t = np.arange(int(d * SR)) / SR
    ph = 2 * np.pi * np.cumsum(np.full(len(t), f) if np.isscalar(f) else f) / SR
    if wave_ == 'sine': return np.sin(ph)
    if wave_ == 'square': return np.sign(np.sin(ph))
    if wave_ == 'saw': return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if wave_ == 'tri': return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1

def noise(d): return rng.uniform(-1, 1, int(d * SR))

def lp(x, a):  # simple one-pole lowpass, a in (0,1): higher = brighter
    y = np.empty_like(x); s = 0.0
    aa = np.broadcast_to(np.asarray(a, dtype=float), x.shape)
    for i in range(len(x)):
        s += aa[i] * (x[i] - s); y[i] = s
    return y

def hp(x, a): return x - lp(x, a)

# ---------------- instruments ----------------
def kick(g=1.0):
    d = .35; t = np.arange(int(d * SR)) / SR
    f = 50 + 120 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * g

HAT = hp(noise(.05), .6) * env(int(.05 * SR), .001, .03, 3)
SNARE = (lp(noise(.2), .35) * .8 + tone(190, .2) * .4) * env(int(.2 * SR), .001, .12, 4)
def clap():
    x = np.zeros(int(.25 * SR))
    for k, o in enumerate([0, .012, .024]):
        n = hp(noise(.2), .3) * env(int(.2 * SR), .001, .09 if k == 2 else .02, 4)
        i = int(o * SR); x[i:i + len(n)] += n[:len(x) - i]
    return x * .7

def pluck(f, d=.28, g=.5, w='tri'):
    return tone(f, d, w) * env(int(d * SR), .003, d * .6, 4) * g

def bass(f, d=.24, g=.55):
    x = tone(f, d, 'saw') * .6 + tone(f, d, 'sine')
    return lp(x, .12) * env(int(d * SR), .004, d * .8, 3) * g

def nf(n): return 440 * 2 ** ((n - 69) / 12)

BEAT = .5  # 120 bpm

# section A: playful bounce 0 - 22
progA = [45, 45, 41, 43]  # A, A, F, G (bass midi)
for b in range(44):
    t = b * BEAT
    add(music, t, kick(.9))
    add(music, t + .25, HAT, .25); add(music, t, HAT, .12)
    if b % 2 == 1: add(music, t, clap(), .45)
    root = progA[(b // 4) % 4]
    add(music, t + .25, bass(nf(root - 12)), .8)
    if b % 4 in (0, 2):
        for k, iv in enumerate([12, 16, 19]):
            add(music, t + k * .125, pluck(nf(root + iv + 12), .22, .18))

# section B: chaos 22 - 29.5 (faster, rising)
t = 22.0
while t < 29.4:
    k = (t - 22) / 7.4
    add(music, t, kick(1.0))
    step = .25 if t > 25 else .5
    add(music, t + step / 2, HAT, .3)
    t += step
dr = np.arange(int(7.4 * SR)) / SR
drone = (tone(55 + 30 * dr / 7.4, 7.4, 'saw') * .5 + tone(110 + 60 * dr / 7.4, 7.4, 'square') * .15)
add(music, 22.0, lp(drone, .05) * np.minimum(1, dr / 1.0), .5)
riser = hp(noise(5.2), .5) * np.linspace(0, 1, int(5.2 * SR)) ** 2
add(music, 22.2, riser, .25)

# section C: calm groove 30.7 - 50.4
progC = [48, 43, 45, 41]  # C G Am F
for b in range(int((50.4 - 30.7) / BEAT)):
    t = 30.7 + b * BEAT
    add(music, t, kick(.7))
    add(music, t + .25, HAT, .18)
    if b % 2 == 1: add(music, t, SNARE, .25)
    root = progC[(b // 4) % 4]
    add(music, t, bass(nf(root - 12), .4), .6)
    arp = [0, 7, 12, 16]
    for k in range(4):
        add(music, t + k * .125, pluck(nf(root + 12 + arp[(b * 4 + k) % 4]), .2, .12, 'sine'))

# section D: brand sting
add(music, 50.0, hp(noise(1.0), .5) * np.linspace(0, 1, SR) ** 3, .35)
chord = sum(tone(nf(n), 4.5, 'saw') for n in [48, 55, 60, 64, 67])
chord = lp(chord, .06) * env(len(chord), .01, 3.5, 2.2)
add(music, 51.0, chord, .22)
add(music, 51.0, kick(1.4)); add(music, 51.0, clap(), .6)
for k, n in enumerate([72, 76, 79, 84]):
    add(music, 53.2 + k * .09, pluck(nf(n), .5, .22, 'sine'))

# ---------------- sfx ----------------
def ding(f=1320, g=.5):
    return (tone(f, .5) + .5 * tone(f * 1.5, .5)) * env(int(.5 * SR), .002, .3, 4) * g
def notif(g=.6):
    x = np.zeros(int(.5 * SR)); a = ding(1047, 1); b = ding(1568, 1)
    x[:len(a)] += a; i = int(.11 * SR); x[i:] += b[:len(x) - i]
    return x * g
def buzz(d):
    t = np.arange(int(d * SR)) / SR
    return lp(tone(160, d, 'square'), .08) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 7 * t))) * .7
def whoosh(d=.45, up=True):
    n = noise(d); t = np.linspace(0, 1, len(n))
    sweep = lp(n, .03) * 0 + n
    out = np.zeros_like(n); s = 0.0
    for i in range(len(n)):
        a = .02 + .35 * (t[i] if up else 1 - t[i]); s += a * (n[i] - s); out[i] = s
    return out * np.sin(np.pi * t) ** 2 * 1.4
def click(): return hp(noise(.02), .5) * env(int(.02 * SR), .0005, .006, 3) * .9 + tone(2400, .02) * env(int(.02 * SR), .0005, .01, 3) * .3
def impact(g=1.0):
    d = 1.0; t = np.arange(int(d * SR)) / SR
    boom = np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-t * 12)) / SR) * np.exp(-t * 3.5)
    return (boom + lp(noise(d), .2) * np.exp(-t * 10) * .6) * g
def alert():
    return np.concatenate([tone(880, .09, 'square') * .3, np.zeros(int(.05 * SR)), tone(660, .12, 'square') * .3]) * env(int(.26 * SR) + 1, .002, .3, 1)[:int(.09 * SR) + int(.05 * SR) + int(.12 * SR)]
def sparkle():
    x = np.zeros(int(.7 * SR))
    for k, f in enumerate([2093, 2637, 3136, 4186]):
        a = tone(f, .3) * env(int(.3 * SR), .001, .15, 4) * .25; i = int(k * .07 * SR); x[i:i + len(a)] += a
    return x
def scratch():
    d = .7; t = np.arange(int(d * SR)) / SR
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 2.2 * t))
    s = tone(f, d, 'saw') * .4 + hp(noise(d), .3) * .5
    return lp(s, .25) * np.sin(np.pi * t / d) * 1.2
def rewind():
    d = 1.1; t = np.arange(int(d * SR)) / SR
    f = 200 + 1800 * (t / d) ** 2
    return (tone(f, d, 'saw') * .25 + hp(noise(d), .4) * .3) * np.sin(np.pi * t / d) * .9
def wahwah():
    out = []
    for i, n in enumerate([62, 61, 60, 59]):
        d = .32 if i < 3 else 1.0; t = np.arange(int(d * SR)) / SR
        vib = 1 + (.03 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0)
        x = lp(tone(nf(n) * vib, d, 'saw'), .08 + .06 * np.sin(np.pi * t / d)) * np.minimum(1, t / .03) * np.exp(-t * (1.2 if i == 3 else 4))
        out.append(x)
    return np.concatenate(out) * .9
def typing(t0, t1, n):
    for k in range(n):
        add(sfx, t0 + (t1 - t0) * k / n + rng.uniform(0, .02), click(), .35)

add(sfx, 0.08, impact(.7)); add(sfx, 0.12, whoosh(.35), .5)
add(sfx, 0.3, notif(.55))
add(sfx, 0.35, buzz(.7), .35); add(sfx, 1.6, buzz(.6), .3)
add(sfx, 2.12, whoosh(.3), .45); add(sfx, 2.15, impact(.4))
add(sfx, 3.35, whoosh(.4), .5)
add(sfx, 3.5, ding(1760, .35)); add(sfx, 4.6, ding(1760, .3))
add(sfx, 4.2, sparkle(), .9)
add(sfx, 7.5, click(), .9)
add(sfx, 8.35, whoosh(.45), .55)
add(sfx, 10.4, alert(), .9); add(sfx, 10.9, sparkle(), .4)
add(sfx, 15.45, whoosh(.3), .4); add(sfx, 15.6, alert(), .9)
typing(17.0, 19.0, 16)
add(sfx, 20.6, click(), 1.0)
add(sfx, 22.0, whoosh(.5, False), .5)
for i in range(7):
    add(sfx, 23.2 + i * .62, notif(.5 + i * .04))
add(sfx, 27.4, impact(1.2)); add(sfx, 27.45, wahwah(), .7)
add(sfx, 29.5, scratch(), .9); add(sfx, 29.6, rewind(), .7)
add(sfx, 30.7, impact(.6)); add(sfx, 30.7, whoosh(.3), .4)
for w in [34.5, 38.0, 41.8]:
    add(sfx, w - .05, whoosh(.45), .55); add(sfx, w + .35, ding(1568, .3))
add(sfx, 45.9, whoosh(.45), .5)
add(sfx, 46.4, notif(.5)); add(sfx, 46.5, buzz(.6), .3)
add(sfx, 47.7, whoosh(.4, False), .6)
add(sfx, 48.25, impact(1.0)); add(sfx, 48.3, sparkle(), .5)

# ---------------- mix ----------------
mix = music * .55 + sfx * .9
# duck music under big hits
mix = np.tanh(mix * 1.1) * .9
fade = np.ones(N); fl = int(1.2 * SR); fade[-fl:] = np.linspace(1, 0, fl)
fi = int(.03 * SR); fade[:fi] = np.linspace(0, 1, fi)
mix *= fade
peak = np.max(np.abs(mix)); mix = mix / peak * .89
st = np.stack([mix, mix], axis=1)
with wave.open(str(__import__('pathlib').Path(__file__).resolve().parent / 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print('ok', DUR)
