import base64, re, subprocess, pathlib, shutil

SRC = pathlib.Path(__file__).resolve().parent
DIST = pathlib.Path(__file__).resolve().parent / 'dist'
OUT = pathlib.Path('/mnt/user-data/outputs')
DIST.mkdir(exist_ok=True)

BOOT = ('<script>/*iv3boot*/(function(){var b64="%s";var bytes=Uint8Array.from(atob(b64),function(c){return c.charCodeAt(0);});'
        'var code=new TextDecoder("utf-8").decode(bytes);var s=document.createElement("script");s.textContent=code;'
        'document.currentScript.parentNode.insertBefore(s,document.currentScript.nextSibling);})();</script>')

parts = {}
for name, out in [('header', 'innovasites-v3-header.html'), ('page', 'innovasites-v3-pagina.html'), ('footer', 'innovasites-v3-footer.html')]:
    js_path = SRC / f'{name}.js'
    subprocess.run(['node', '--check', str(js_path)], check=True)
    js = js_path.read_text(encoding='utf-8')
    b64 = base64.b64encode(js.encode('utf-8')).decode('ascii')
    html = (SRC / f'{name}.html').read_text(encoding='utf-8')
    marker = f'<!--JS:{name}.js-->'
    assert marker in html, marker
    html = html.replace(marker, BOOT % b64)
    # WordPress safety: no & or apostrophe inside any script tag
    for m in re.finditer(r'<script>(.*?)</script>', html, re.S):
        body = m.group(1)
        assert '&' not in body and "'" not in body, f'unsafe char in script of {name}'
    # no & inside style blocks either
    for m in re.finditer(r'<style>(.*?)</style>', html, re.S):
        assert '&' not in m.group(1), f'& in style of {name}'
    (DIST / out).write_text(html, encoding='utf-8')
    parts[name] = html
    print(f'{out}: {len(html):,} bytes (js {len(js):,})')

combined = ('<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>InnovaSites — vista previa</title>\n<style>html,body{margin:0;background:#0A0C11;}</style>\n'
            '</head>\n<body>\n' + parts['header'] + '\n' + parts['page'] + '\n' + parts['footer'] + '\n</body>\n</html>\n')
(DIST / 'innovasites-v3-preview.html').write_text(combined, encoding='utf-8')
print('combined:', f'{len(combined):,} bytes')
