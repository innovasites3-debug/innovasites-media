"""Renderiza el Reel. Uso: python3 render.py sin|voz"""
import os, sys, re, json, subprocess, pathlib
from multiprocessing import Process
from playwright.sync_api import sync_playwright

V = pathlib.Path(__file__).resolve().parent
MODE = sys.argv[1] if len(sys.argv) > 1 else 'sin'
T = json.loads(re.search(r'window\.T = (.*?);\n', (V / 'timing.js').read_text(encoding='utf-8')).group(1))
FPS, WORKERS = 30, 3
TOTAL = int(round(FPS * T['dur']))
OUT = V / 'innovasites-qr-mesa.mp4'

def work(k):
    a, b = k * TOTAL // WORKERS, (k + 1) * TOTAL // WORKERS
    tmp, fin = V / f'part{MODE}{k}.tmp.mp4', V / f'part{MODE}{k}.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', str(FPS), str(tmp)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        br = p.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}))
        pg = br.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto((V / 'scene.html').as_uri() + ('#voz' if MODE == 'voz' else '')); pg.evaluate('document.fonts.ready')
        for f in range(a, b):
            pg.evaluate(f'render({f / FPS})')
            ff.stdin.write(pg.screenshot(type='jpeg', quality=94))
        br.close()
    ff.stdin.close()
    if ff.wait() == 0: tmp.rename(fin)

if __name__ == '__main__':
    ps = [Process(target=work, args=(k,)) for k in range(WORKERS)]
    [p.start() for p in ps]; [p.join() for p in ps]
    parts = [V / f'part{MODE}{k}.mp4' for k in range(WORKERS)]
    assert all(p.exists() for p in parts), 'falta una parte'
    lst = V / f'parts{MODE}.txt'; lst.write_text(''.join(f"file '{p.name}'\n" for p in parts))
    vid = V / f'video{MODE}.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', str(vid)], check=True)
    aud = V / f'audio_{MODE}.wav'
    # loudnorm en dos pasadas para quedar en -14 LUFS exactos
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(aud), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    ln = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    tmp = OUT.with_suffix('.tmp.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(vid), '-i', str(aud), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', ln, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-shortest', str(tmp)], check=True)
    tmp.rename(OUT)
    for p in parts + [lst, vid]: p.unlink()
    print('done', OUT.name)
