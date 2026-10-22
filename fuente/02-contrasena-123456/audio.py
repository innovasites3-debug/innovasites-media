import numpy as np, wave

SR = 44100
DUR = 55.5
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


def groove(a, b, prog, kickg=.8, arpg=.14, clapg=.4, bassg=.7):
    n = int((b - a) / BEAT)
    for k in range(n):
        t = a + k * BEAT
        add(music, t, kick(kickg)); add(music, t + .25, HAT, .22)
        if k % 2 == 1: add(music, t, clap(), clapg)
        root = prog[(k // 4) % len(prog)]
        add(music, t + .25, bass(nf(root - 12)), bassg)
        if k % 4 in (0, 2):
            for j, iv in enumerate([12, 16, 19]): add(music, t + j * .125, pluck(nf(root + iv + 12), .22, arpg))

groove(0.0, 8.5, [45, 45, 41, 43])                     # playful setup
# quiz: tension with clock ticks
qd = np.arange(int(8.0 * SR)) / SR
pad = lp(tone(110, 8.0, 'saw') * .5 + tone(164.8, 8.0, 'saw') * .3, .03) * np.minimum(1, qd / .8)
add(music, 8.6, pad, .35)
t = 9.0
while t < 16.5:
    add(music, t, kick(.55)); t += .5
for k in range(10):
    add(sfx, 11.6 + k * .5, click(), .55); add(sfx, 11.85 + k * .5, click(), .3)
# terminal: fast and tense
t = 18.6
while t < 23.9:
    add(music, t, kick(1.0)); add(music, t + .125, HAT, .3); t += .25
add(music, 18.6, hp(noise(2.2), .5) * np.linspace(0, 1, int(2.2 * SR)) ** 2, .22)
groove(24.0, 29.9, [45, 45, 41, 43], .7, .12, .35, .6)   # why
# calm groove for tips + meters
progC = [48, 43, 45, 41]
for b in range(int((49.5 - 30.7) / BEAT)):
    t = 30.7 + b * BEAT
    add(music, t, kick(.7)); add(music, t + .25, HAT, .18)
    if b % 2 == 1: add(music, t, SNARE, .25)
    root = progC[(b // 4) % 4]
    add(music, t, bass(nf(root - 12), .4), .6)
    for k in range(4): add(music, t + k * .125, pluck(nf(root + 12 + [0, 7, 12, 16][(b * 4 + k) % 4]), .2, .12, 'sine'))
# sting
add(music, 49.4, hp(noise(1.0), .5) * np.linspace(0, 1, SR) ** 3, .35)
chord = sum(tone(nf(n), 5.0, 'saw') for n in [48, 55, 60, 64, 67])
add(music, 50.0, lp(chord, .06) * env(len(chord), .01, 4.0, 2.2), .22)
add(music, 50.0, kick(1.4)); add(music, 50.0, clap(), .6)
for k, n in enumerate([72, 76, 79, 84]): add(music, 52.2 + k * .09, pluck(nf(n), .5, .22, 'sine'))

add(sfx, 0.08, impact(.7)); add(sfx, 0.12, whoosh(.35), .5)
typing(0.5, 1.5, 6)
add(sfx, 1.6, buzz(.7), .3); add(sfx, 1.62, alert(), .7)
add(sfx, 3.4, whoosh(.4), .5); add(sfx, 3.6, sparkle(), .8)
add(sfx, 5.7, click(), .9); add(sfx, 6.2, impact(.6)); add(sfx, 6.25, wahwah(), .55)
add(sfx, 8.6, whoosh(.45), .55)
for i in range(3): add(sfx, 9.6 + i * .35, whoosh(.3), .4); add(sfx, 9.75 + i * .35, ding(1320 + i * 200, .25))
add(sfx, 16.6, impact(1.1)); add(sfx, 16.65, notif(.6))
add(sfx, 16.8, sparkle(), .7)
add(sfx, 18.3, whoosh(.5), .5)
for i in range(7): add(sfx, 19.0 + i * (1.6 / 7), click(), .7); add(sfx, 19.05 + i * (1.6 / 7), ding(500 + i * 40, .12))
add(sfx, 20.6, impact(1.2)); add(sfx, 20.62, alert(), 1.0)
add(sfx, 24.0, whoosh(.45), .5)
for i in range(8): add(sfx, 24.5 + i * .12, ding(900 + i * 90, .18))
add(sfx, 29.95, scratch(), .9); add(sfx, 30.0, rewind(), .7)
add(sfx, 30.7, impact(.6)); add(sfx, 30.7, whoosh(.3), .4)
for w in [33.7, 37.2, 41.0]: add(sfx, w - .05, whoosh(.45), .55); add(sfx, w + .35, ding(1568, .3))
add(sfx, 45.2, whoosh(.45), .5)
for k in range(1): add(sfx, 46.2, ding(330, .4))
for k in range(10): add(sfx, 47.2 + k * .06, ding(700 + k * 80, .14))
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
