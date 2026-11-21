"""Is the 2D view pixel-identical? Renders the same 2D pictures on several pages and compares the PNGs."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab
from PIL import Image, ImageChops
SC = {
  'm': "$('mode-m').click(); $('flat').click();",
  'j': "$('mode-j').click(); $('flat').click();",
  'jcut': "$('mode-j').click(); $('flat').click(); L.S.cut = 0.3;",
  'mplanes': "$('mode-m').click(); $('flat').click(); Object.assign(L.S.colour, {trap: 4, by: 0});",
  'mesc': "$('mode-m').click(); $('flat').click(); L.S.colour.mode = 2;",
  'k': "$('mode-k').click(); $('flat').click();",
  'mosaic': "$('mode-m').click(); $('m-mosaic').click(); $('flat').click();",
  'neg': "$('mode-m').click(); $('flat').click(); L.S.n = -2;",
}
pages = sys.argv[1].split(',')
names = sys.argv[2].split(',') if len(sys.argv) > 2 else list(SC)
out = {}
for pg in pages:
    steps = []
    for n in names:
        p = '%s/flat/%s-%s.png' % (lab.HERE, pg, n)
        os.makedirs(os.path.dirname(os.path.join(lab.ROOT, p)), exist_ok=True)
        steps.append({'js': lab.PRE + "if (L.S.flat) $('flat').click(); if (L.S.mosaic) $('m-mosaic').click(); L.S.n = 2; L.S.cut = 0; Object.assign(L.S.colour, {mode: 0, trap: 5, by: 4}); " + SC[n] + " L.S.q.aa = 4; go(); return '%s';" % n,
                      'wait': 'done', 'timeout': 400, 'shot': p, 'clip': '#view'})
        out.setdefault(n, []).append(p)
    code, log = lab.shot('dist/%s.html' % pg, steps, 'flat-' + pg, size='1000x700')
    print(pg, 'exit', code, log.strip().splitlines()[-1])
for n in names:
    a = Image.open(os.path.join(lab.ROOT, out[n][0])).convert('RGB')
    for p in out[n][1:]:
        b = Image.open(os.path.join(lab.ROOT, p)).convert('RGB')
        diff = ImageChops.difference(a, b)
        bbox = diff.getbbox()
        mx = max(v for band in diff.split() for v in [band.getextrema()[1]])
        cnt = sum(1 for px in diff.getdata() if px != (0, 0, 0)) if bbox else 0
        print('%-8s %s vs %s: %s (largest channel difference %d, %d pixels differ)' % (n, os.path.basename(out[n][0]), os.path.basename(p), 'IDENTICAL' if not bbox else 'DIFFERENT', mx, cnt))
