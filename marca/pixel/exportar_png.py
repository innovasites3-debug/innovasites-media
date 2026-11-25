# Saca un PNG transparente (fondo vacío) de cada pose de poses.html en png/.
# Uso: python3 exportar_png.py
import pathlib
from playwright.sync_api import sync_playwright
D = pathlib.Path(__file__).resolve().parent
(D / 'png').mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 400, 'height': 520}, device_scale_factor=2)
    pg.goto((D / 'poses.html').as_uri()); poses = pg.evaluate('window.POSES')
    for n in poses:
        pg.goto('about:blank'); pg.goto((D / 'poses.html').as_uri() + '?pose=' + n); pg.wait_for_timeout(150)
        pg.screenshot(path=str(D / 'png' / f'pixel-{n}.png'), omit_background=True)
    b.close()
print(len(poses), 'poses')
