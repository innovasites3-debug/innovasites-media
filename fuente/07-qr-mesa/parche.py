"""Vuelve a renderizar los primeros N segundos y los empalma en el video final (sin re-renderizar todo).
Uso: python3 parche.py voz|sin 3.0"""
import os, sys, subprocess, pathlib
from playwright.sync_api import sync_playwright
V = pathlib.Path(__file__).resolve().parent
MODE, SECS = sys.argv[1], float(sys.argv[2]); FPS = 30; N = int(SECS * FPS)
OUT = V / 'innovasites-qr-mesa.mp4'
head = V / f'head_{MODE}.mp4'
ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', str(head)], stdin=subprocess.PIPE)
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto((V / 'scene.html').as_uri() + ('#voz' if MODE == 'voz' else '')); pg.evaluate('document.fonts.ready')
    for f in range(N):
        pg.evaluate(f'render({f / FPS})'); ff.stdin.write(pg.screenshot(type='jpeg', quality=94))
    br.close()
ff.stdin.close(); assert ff.wait() == 0
tmp = OUT.with_suffix('.tmp.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(head), '-i', str(OUT), '-filter_complex',
                f'[1:v]trim=start_frame={N},setpts=PTS-STARTPTS[b];[0:v][b]concat=n=2:v=1:a=0[v]',
                '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                '-r', str(FPS), '-c:a', 'copy', '-movflags', '+faststart', str(tmp)], check=True)
tmp.rename(OUT); head.unlink(); print('ok', OUT.name)
