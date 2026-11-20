# -*- coding: utf-8 -*-
"""Guion de voz del Reel "La verificación en dos pasos" y línea de tiempo (timing.js).

Las palabras entre *asteriscos* salen resaltadas en rojo en los textos animados.
La duración real de cada frase (voz/duraciones.json) define cuándo pasa cada cosa.
Sin voz, se estiman duraciones para la versión solo texto.
"""
import json, pathlib, re, sys

V = pathlib.Path(__file__).resolve().parent

LINES = [
    ("L1",  "Le robaron la contraseña… y aun así *no pudieron entrar.*"),
    ("L2",  "*Rebobinando…* tres de la mañana."),
    ("L3",  "¿Por qué no pudieron? *¿A, B o C?*"),
    ("L4",  "El hacker escribe el correo y la clave… *correctos.*"),
    ("L5",  "Pero aparece esto: *“Escribe el código que enviamos a su celular.”*"),
    ("L6",  "Ese código *solo llega a su teléfono.*"),
    ("L7",  "Ella toca *“No fui yo”…* y el intento queda *bloqueado.*"),
    ("L8",  "*¿Ya sabes cuál es?* Comenta A, B o C."),
    ("L9",  "*La B.* La verificación en dos pasos *la salvó.*"),
    ("L10", "Uno: actívala hoy en tu *correo, WhatsApp y redes.*"),
    ("L11", "Dos: si puedes, usa una *app de códigos* en vez del SMS."),
    ("L12", "Tres: ese código *no se le da a nadie.*"),
    ("L13", "Actívala y comenta *LISTO.*"),
    ("L14", "Cada pixel cuenta… y tu *seguridad* también."),
]
TEXT = dict(LINES)
clean = lambda s: s.replace('*', '').replace(' ', ' ')


def estimate(txt):
    return len(clean(txt)) / 15.0 + 0.25 * len(re.findall(r'[.,:?…]', txt))


def tokens(txt):
    """[(palabra, resaltada)] respetando las marcas *...*"""
    res, key = [], False
    for tok in txt.split(' '):
        k = key or tok.startswith('*')
        if tok.startswith('*'): key = True
        if tok.rstrip('.,:?…').endswith('*') or tok.endswith('*'): key = False
        res.append((tok.replace('*', ''), k))
    return res


def chunks(txt, maxc=36):
    """Bloques cortos de palabras: corta en fin de frase y, si hace falta, en el punto más equilibrado."""
    ws = tokens(txt); L = lambda c: len(' '.join(w for w, _ in c))
    sents, cur = [], []
    for w in ws:
        cur.append(w)
        if w[0].rstrip('*')[-1] in '.:?…': sents.append(cur); cur = []
    if cur: sents.append(cur)
    def split(c):
        if L(c) <= maxc or len(c) < 2: return [c]
        STOP = {'la', 'el', 'los', 'las', 'de', 'o', 'y', 'a', 'que', 'tu', 'en', 'es', 'un', 'una', 'se', 'lo', 'le', 'te', 'no', 'para', 'si'}
        def cost(i):
            k = abs(L(c[:i]) - L(c[i:]))
            if c[i - 1][0].endswith(','): k -= 10
            if c[i - 1][0].lower() in STOP: k += 14
            if c[i - 1][1] and c[i][1]: k += 9
            return k
        best = min(range(1, len(c)), key=cost)
        return split(c[:best]) + split(c[best:])
    out = []
    for c in sents: out += split(c)
    merged, i = [], 0
    while i < len(out):
        c = out[i]
        if L(c) <= 15 and i + 1 < len(out) and L(c) + 1 + L(out[i + 1]) <= maxc + 4 and c[-1][0][-1] in ':,':
            c = c + out[i + 1]; i += 1
        merged.append(c); i += 1
    return merged


def syl(w):
    return max(1, len(re.findall(r'[aeiouáéíóúü]+', w.lower())))


def pauses(k):
    """Centros de silencios (>110 ms) dentro de la frase grabada."""
    f = V / 'voz' / f'{k}.wav'
    if not f.exists(): return []
    import numpy as np, soundfile as sf
    a, sr = sf.read(f)
    if a.ndim > 1: a = a.mean(1)
    hop = int(.01 * sr)
    e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    quiet = e < max(.006, e.max() * .05); out, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if (j - i) >= 11 and i > 5 and j < len(quiet) - 5: out.append((i + j) / 2 * .01)
            i = j
        else: i += 1
    return out


def build(dur):
    """Linea de tiempo: monitor del hacker + telefono en la mesa de noche + juego A/B/C."""
    s = {}
    e = lambda k: s[k] + dur[k]
    T = {}
    s['L1'] = 0.3
    T['hookEnd'] = max(3.0, e('L1') + 0.15)
    T['rewind'] = T['hookEnd']
    s['L2'] = T['rewind'] + 0.2
    T['rewindEnd'] = e('L2') + 0.25
    s['L3'] = T['rewindEnd'] + 0.1
    T['optsIn'] = s['L3'] + 0.1
    T['optsOut'] = e('L3') + 0.3
    T['login'] = T['optsOut'] - 0.2
    s['L4'] = T['optsOut'] + 0.1
    T['typeA'] = s['L4'] + 0.3
    T['typeB'] = s['L4'] + dur['L4'] * .7
    T['check'] = e('L4') - 0.25
    s['L5'] = e('L4') + 0.15
    T['tfa'] = s['L5'] + dur['L5'] * .35
    s['L6'] = e('L5') + 0.2
    T['phone'] = s['L6'] - 0.1
    T['notif'] = s['L6'] + 0.5
    s['L7'] = e('L6') + 0.15
    T['tap'] = s['L7'] + dur['L7'] * .3
    T['denied'] = s['L7'] + dur['L7'] * .65
    T['storyEnd'] = e('L7') + 0.4
    T['q0'] = T['storyEnd']
    s['L8'] = T['q0'] + 0.35
    T['p0'] = e('L8') + 0.15
    T['p1'] = T['p0'] + 4.5
    s['L9'] = T['p1'] + 0.25
    T['qe'] = e('L9') + 0.35
    T['ts'] = T['qe']
    s['L10'] = T['ts'] + 0.3
    T['t1'] = [T['ts'] + 0.2, max(e('L10') + 0.35, T['ts'] + 3.4)]
    s['L11'] = T['t1'][1] + 0.05
    T['t2'] = [T['t1'][1] - 0.35, max(e('L11') + 0.35, T['t1'][1] + 3.2)]
    s['L12'] = T['t2'][1] + 0.05
    T['t3'] = [T['t2'][1] - 0.35, max(e('L12') + 0.35, T['t2'][1] + 3.2)]
    s['L13'] = T['t3'][1] + 0.1
    T['listo'] = [s['L13'] - 0.15, e('L13') + 0.5]
    T['end'] = T['listo'][1]
    s['L14'] = T['end'] + 0.85
    T['dur'] = round(max(T['end'] + 4.3, e('L14') + 0.85), 2)
    # bloques de texto animado con tiempo por palabra
    subs = []
    for k, _ in LINES:
        cs = chunks(TEXT[k]); txt = lambda c: ' '.join(w for w, _ in c); tot = sum(len(txt(c)) for c in cs)
        cuts = pauses(k); bounds, acc = [0.0], 0
        for c in cs[:-1]:
            acc += len(txt(c)); guess = dur[k] * acc / tot
            near = [x for x in cuts if abs(x - guess) < .6]
            bounds.append(min(near, key=lambda x: abs(x - guess)) if near else guess)
        bounds.append(dur[k])
        for i, c in enumerate(cs):
            a, b = s[k] + bounds[i], s[k] + bounds[i + 1]
            ws = c; w8 = [syl(w) for w, _ in ws]; tw = sum(w8); acc2 = 0; out = []
            for (w, key), n in zip(ws, w8):
                out.append([w, round(a + (b - a) * acc2 / tw - .04, 3), int(key)]); acc2 += n
            subs.append([round(a, 3), round(b, 3), out, k])
    return T, s, subs


def write(dur, path):
    T, s, subs = build(dur)
    js = 'window.T = ' + json.dumps(T) + ';\nwindow.VOICE = ' + json.dumps({k: [round(s[k], 3), round(dur[k], 3)] for k in s}) + \
         ';\nwindow.SUBS = ' + json.dumps(subs, ensure_ascii=False) + ';\n'
    beats = V / 'voz' / 'beats.json'
    js += 'window.BEATS = ' + (beats.read_text() if beats.exists() else '[]') + ';\n'
    pathlib.Path(path).write_text(js, encoding='utf-8')
    return T, s


if __name__ == '__main__':
    dfile = V / 'voz' / 'duraciones.json'
    dur = json.loads(dfile.read_text()) if dfile.exists() and '--estimar' not in sys.argv else {k: estimate(t) for k, t in LINES}
    T, s = write(dur, V / 'timing.js')
    print('duración total', T['dur'])
