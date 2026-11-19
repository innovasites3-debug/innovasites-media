# -*- coding: utf-8 -*-
"""Guion de voz del Reel "Black Friday: la tienda falsa" y línea de tiempo (timing.js).

Las palabras entre *asteriscos* salen resaltadas en rojo en los textos animados.
La duración real de cada frase (voz/duraciones.json) define cuándo pasa cada cosa.
Sin voz, se estiman duraciones para la versión solo texto.
"""
import json, pathlib, re, sys

V = pathlib.Path(__file__).resolve().parent

LINES = [
    ("L1",  "Compró unos tenis al *70%…* y nunca llegaron."),
    ("L2",  "*Rebobinando…* al día de la compra."),
    ("L3",  "Antes de seguir: una de estas tiendas es *falsa.* ¿La *A* o la *B?*"),
    ("L4",  "Le aparece un anuncio: tenis de marca a *$120.000.*"),
    ("L5",  "Primera señal: el precio es *demasiado bueno.*"),
    ("L6",  "Segunda señal: la dirección. Léela *letra por letra.*"),
    ("L7",  "Tercera señal: *solo transferencia* a una cuenta personal."),
    ("L8",  "Pagó… y la tienda *desapareció.*"),
    ("L9",  "*¿Cuál era la falsa?* Comenta A o B."),
    ("L10", "*La B.* Mira bien la dirección: termina en *.shop*"),
    ("L11", "Uno: escribe tú la dirección, *no entres por anuncios.*"),
    ("L12", "Dos: si el descuento es *demasiado bueno,* desconfía."),
    ("L13", "Tres: paga con tarjeta o pasarela conocida, *nunca a una cuenta personal.*"),
    ("L14", "Cada pixel cuenta… y tu *seguridad* también."),
]
# cómo lo dice la voz (para dividir la toma por sílabas)
SAY = {
    "L1": "Compró unos tenis al setenta por ciento… y nunca llegaron.",
    "L4": "Le aparece un anuncio: tenis de marca a ciento veinte mil.",
    "L10": "La B. Mira bien la dirección: termina en punto shop.",
}
TEXT = dict(LINES)
clean = lambda s: s.replace('*', '').replace('\u00a0', ' ')


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
    s = {}
    e = lambda k: s[k] + dur[k]
    T = {}
    s['L1'] = 0.25
    T['phoneIn'] = 0.05
    T['rw0'] = e('L1') + 0.1
    s['L2'] = T['rw0'] + 0.05
    T['rw1'] = max(e('L2') + 0.1, T['rw0'] + 1.4)
    T['ab0'] = T['rw1']                           # tiendas A y B
    s['L3'] = T['ab0'] + 0.2
    T['ab1'] = e('L3') + 1.4
    T['ad'] = T['ab1']                            # anuncio en el teléfono
    s['L4'] = T['ad'] + 0.15
    s['L5'] = e('L4') + 0.2; T['z1'] = s['L5']
    T['web'] = e('L5') + 0.45
    s['L6'] = T['web'] + 0.35; T['z2'] = s['L6']
    T['pay'] = e('L6') + 0.45
    s['L7'] = T['pay'] + 0.35; T['z3'] = s['L7']
    T['paid'] = e('L7') + 0.35
    s['L8'] = T['paid'] + 0.3
    T['gone'] = s['L8'] + dur['L8'] * .5
    T['phEnd'] = e('L8') + 0.35
    T['bankEnd'] = T['phEnd']
    T['q0'] = T['phEnd'] + 0.05
    s['L9'] = T['q0'] + 0.35
    T['p0'] = e('L9') + 0.1
    T['p1'] = T['p0'] + 4.0
    s['L10'] = T['p1'] + 0.2
    T['qe'] = e('L10') + 0.3
    T['ts'] = T['qe']
    s['L11'] = T['ts'] + 0.45
    T['t1'] = [T['ts'] + 0.3, max(e('L11') + 0.25, T['ts'] + 3.0)]
    s['L12'] = T['t1'][1] + 0.05
    T['t2'] = [T['t1'][1] - 0.35, max(e('L12') + 0.25, T['t1'][1] + 3.0)]
    s['L13'] = T['t2'][1] + 0.05
    T['t3'] = [T['t2'][1] - 0.35, max(e('L13') + 0.25, T['t2'][1] + 3.2)]
    T['end'] = T['t3'][1]
    s['L14'] = T['end'] + 0.65
    T['dur'] = round(max(T['end'] + 4.0, e('L14') + 0.45), 2)
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
