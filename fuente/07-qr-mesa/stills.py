import os, sys, pathlib
from playwright.sync_api import sync_playwright
V = pathlib.Path(__file__).resolve().parent
args = sys.argv[1:]
voz = '--voz' in args
times = [float(x) for x in args if x != '--voz']
(V / 'frames').mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}))
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto((V / 'scene.html').as_uri() + ('#voz' if voz else '')); pg.evaluate('document.fonts.ready')
    for t in times:
        pg.evaluate(f'render({t})')
        pg.screenshot(path=str(V / 'frames' / f"{'v' if voz else 's'}{t:05.1f}.png"))
    print('errors', errs)
    b.close()
