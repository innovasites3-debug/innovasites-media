"""Re-renderiza un tramo [a, b) en segundos y lo reemplaza dentro del video final.
Uso: python3 tramo.py 24.4 27.8"""
import sys, subprocess, pathlib
from playwright.sync_api import sync_playwright
V = pathlib.Path(__file__).resolve().parent; FPS = 30
OUT = V / 'innovasites-qr-mesa.mp4'
fa, fb = int(float(sys.argv[1]) * FPS), int(float(sys.argv[2]) * FPS)
mid = V / 'tramo.mp4'
ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', str(mid)], stdin=subprocess.PIPE)
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto((V / 'scene.html').as_uri() + '#voz'); pg.evaluate('document.fonts.ready')
    for f in range(fa, fb):
        pg.evaluate(f'render({f / FPS})'); ff.stdin.write(pg.screenshot(type='jpeg', quality=94))
    br.close()
ff.stdin.close(); assert ff.wait() == 0
tmp = OUT.with_suffix('.tmp.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(OUT), '-i', str(mid), '-filter_complex',
                f'[0:v]trim=end_frame={fa},setpts=PTS-STARTPTS[a];[0:v]trim=start_frame={fb},setpts=PTS-STARTPTS[c];[a][1:v][c]concat=n=3:v=1:a=0[v]',
                '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                '-r', str(FPS), '-c:a', 'copy', '-movflags', '+faststart', str(tmp)], check=True)
tmp.rename(OUT); mid.unlink(); print('ok')
