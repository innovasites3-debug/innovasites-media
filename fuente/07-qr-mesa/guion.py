# -*- coding: utf-8 -*-
"""Guion de voz del Reel "El QR pegado en la mesa" y línea de tiempo (timing.js).

Las palabras entre *asteriscos* salen resaltadas en rojo en los textos animados.
La duración real de cada frase (voz/duraciones.json) define cuándo pasa cada cosa.
Sin voz, se estiman duraciones para la versión solo texto.
"""
import json, pathlib, re, sys

V = pathlib.Path(__file__).resolve().parent

LINES = [
    ("L1",  "Escaneaste el QR de la mesa… y le pagaste a un *estafador.*"),
    ("L2",  "Estás en un café. En la mesa hay un QR: *menú y pago.*"),
    ("L3",  "Lo escaneas, y se abre una página para *pagar la cuenta.*"),
    ("L4",  "Primera señal: el QR es una *calcomanía pegada encima* del original."),
    ("L5",  "Segunda señal: la dirección *no es la del café.* Es un *link acortado.*"),
    ("L6",  "Pero *pagas la cuenta…*"),
    ("L7",  "Y los datos de tu tarjeta le llegan *al estafador.*"),
    ("L8",  "*¿Cuál es el QR intruso?* Comenta uno, dos o tres antes de la respuesta."),
    ("L9",  "*El dos.* Tiene el borde levantado: está *pegado encima* del original."),
    ("L10", "Uno: antes de abrir el link, *mira la dirección.*"),
    ("L11", "Dos: si el QR está *pegado encima,* pregunta en caja."),
    ("L12", "Tres: paga en *caja* o en la *app oficial,* no desde un QR."),
    ("L13", "Cada pixel cuenta… y tu *seguridad* también."),
]
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
    s['L1'] = 0.3
    T['qr'] = 0.1
    T['phoneIn'] = max(1.15, s['L1'] + dur['L1'] * .35)
    T['hookEnd'] = max(3.0, e('L1') + 0.15)
    T['cam'] = T['hookEnd']
    s['L2'] = T['cam'] + 0.2
    T['det'] = s['L2'] + dur['L2'] * .55
    s['L3'] = e('L2') + 0.1
    T['tapBan'] = s['L3'] + dur['L3'] * .3
    T['web'] = T['tapBan'] + 0.3
    T['back'] = e('L3') + 0.1
    s['L4'] = T['back'] + 0.15
    T['z1'] = T['back'] + 0.35
    T['z1e'] = e('L4') + 0.3
    T['fwd'] = T['z1e'] - 0.1
    s['L5'] = T['fwd'] + 0.3
    T['z2'] = T['fwd'] + 0.35
    T['z2e'] = e('L5') + 0.2
    T['ty0'] = T['z2'] + (T['z2e'] - T['z2']) * .5; T['ty1'] = T['ty0'] + 1.5
    s['L6'] = T['z2e'] + 0.05
    T['pay'] = max(s['L6'] + dur['L6'] * .75, T['ty1'] + .2)
    T['bank'] = T['pay'] + 0.4
    s['L7'] = T['bank'] + 0.1
    T['n1'] = T['bank'] + 0.2; T['n2'] = T['bank'] + 0.75; T['n3'] = T['bank'] + 1.3; T['n4'] = T['bank'] + 1.85
    T['bankEnd'] = max(e('L7') + 0.4, T['n4'] + 1.0)
    T['q0'] = T['bankEnd'] + 0.05
    s['L8'] = T['q0'] + 0.35
    T['p0'] = e('L8') + 0.15
    T['p1'] = T['p0'] + 4.0
    s['L9'] = T['p1'] + 0.25
    T['qe'] = e('L9') + 0.35
    T['ts'] = T['qe']
    s['L10'] = T['ts'] + 0.45
    T['t1'] = [T['ts'] + 0.3, max(e('L10') + 0.35, T['ts'] + 3.4)]
    s['L11'] = T['t1'][1] + 0.05
    T['t2'] = [T['t1'][1] - 0.35, max(e('L11') + 0.35, T['t1'][1] + 3.2)]
    s['L12'] = T['t2'][1] + 0.05
    T['t3'] = [T['t2'][1] - 0.35, max(e('L12') + 0.35, T['t2'][1] + 3.4)]
    T['end'] = T['t3'][1]
    s['L13'] = T['end'] + 0.85
    T['dur'] = round(max(T['end'] + 4.5, e('L13') + 0.85), 2)
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
