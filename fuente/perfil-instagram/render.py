import pathlib, sys
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent; out=D/'out'; out.mkdir(exist_ok=True)
only=sys.argv[1:]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto((D/'pieces.html').as_uri()); pg.evaluate('document.fonts.ready')
    for k in pg.evaluate('PIECES'):
        if only and not any(o in k for o in only): continue
        w,h=pg.evaluate(f'show("{k}")'); pg.evaluate('document.fonts.ready')
        pg.set_viewport_size({'width':w,'height':h})
        pg.screenshot(path=str(out/f'{k}.png'))
    print('errors',errs); b.close()
