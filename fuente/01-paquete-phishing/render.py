import os, sys, subprocess, pathlib
from multiprocessing import Process
from playwright.sync_api import sync_playwright

V = pathlib.Path(__file__).resolve().parent
FPS, DUR, WORKERS = 30, 56.0, 4
TOTAL = int(FPS * DUR)

def work(k):
    a, b = k * TOTAL // WORKERS, (k + 1) * TOTAL // WORKERS
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', str(V / f'part{k}.mp4')], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        br = p.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}))
        pg = br.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto((V / 'scene.html').as_uri()); pg.evaluate('document.fonts.ready')
        for f in range(a, b):
            pg.evaluate(f'render({f / FPS})')
            ff.stdin.write(pg.screenshot(type='jpeg', quality=95))
        br.close()
    ff.stdin.close(); ff.wait()

if __name__ == '__main__':
    ps = [Process(target=work, args=(k,)) for k in range(WORKERS)]
    [p.start() for p in ps]; [p.join() for p in ps]
    (V / 'parts.txt').write_text(''.join(f"file 'part{k}.mp4'\n" for k in range(WORKERS)))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(V / 'parts.txt'), '-i', str(V / 'audio.wav'),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-r', str(FPS), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                    '-movflags', '+faststart', '-shortest', str(V / 'innovasites-paquete-phishing.mp4')], check=True)
    print('done')
