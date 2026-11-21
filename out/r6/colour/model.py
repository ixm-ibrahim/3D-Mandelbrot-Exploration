"""A 3D model's colours against the picture's: python out/r6/colour/model.py <page> <label>

Julia set for c = -1, shell of radius 1, glow (the opening colours), seen from straight above.
  1. the 3D picture of the page, camera above the solid looking down the z-axis (Balanced, no shadows);
  2. the same scene as a model would be sampled: sampleSlice() on a stack of level slices (the call the 3D model
     uses), and for every (x, y) column the colour of the highest sample that is inside the solid or within one
     sample spacing of it. That is the colour a model's top surface gets. Written as a picture, unlit.
Both are written to out/r6/colour/<label>/ and put side by side in out/r6/colour/model-<label>.png.
"""
import base64, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
page, label = sys.argv[1], sys.argv[2]
folder = os.path.join(HERE, label)
os.makedirs(folder, exist_ok=True)
PRE = ("const L = window.squaringLab, S = L.S, C = S.colour, $ = id => document.getElementById(id);"
       "if (L.R) L.R.warmOn = false;"
       "const go = () => { L.syncControls(); L.refresh(false); };")
SETUP = ("L.resetAll(); $('qBal').click(); S.q.shadow = false; S.q.ao = false; S.q.aa = 2; $('mode-j').click(); S.c = [-1, 0, 0];"
         "L.cam.target = [0, 0, 0]; L.cam.yaw = -Math.PI / 2; L.cam.pitch = Math.PI / 2 - 0.001; L.cam.dist = 6; go(); return 'top view ' + JSON.stringify([L.cam.yaw, L.cam.pitch, L.cam.dist]);")
SAMPLE = r"""
const N = 160, Z = 72, side = 3.6, z0 = 1.05, z1 = -0.05, sp = side / N;
const snap = L.takeSnapshot();
const top = new Float32Array(3 * N * N), got = new Uint8Array(N * N);
for (let k = 0; k < Z; k++) {
  const z = z0 + (z1 - z0) * k / (Z - 1);
  const a = await L.sampleSlice(snap, 0, 0, side, z, N);
  if (!a) return 'sampling failed';
  for (let i = 0; i < N * N; i++) if (!got[i] && a[4 * i + 3] < sp) { got[i] = 1; top[3 * i] = a[4 * i]; top[3 * i + 1] = a[4 * i + 1]; top[3 * i + 2] = a[4 * i + 2]; }
}
L.releaseSnapshot(snap);
const cv = document.createElement('canvas'); cv.width = cv.height = N;
const ctx = cv.getContext('2d'), im = ctx.createImageData(N, N);
for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
  const i = (N - 1 - y) * N + x, o = 4 * (y * N + x);
  for (let j = 0; j < 3; j++) im.data[o + j] = got[i] ? 255 * Math.pow(Math.min(1, Math.max(0, top[3 * i + j])), 0.4545) : 8;
  im.data[o + 3] = 255;
}
ctx.putImageData(im, 0, 0);
return cv.toDataURL('image/png');
"""
acts = [{'wait': 'done', 'timeout': 600},
        {'js': PRE + SETUP}, {'sleep': 0.2},
        {'wait': 'done', 'timeout': 600, 'shot': 'out/r6/colour/%s/model-picture.png' % label, 'clip': '#view'},
        {'js': PRE + SAMPLE, 'timeout': 900}]
path = os.path.join(folder, '_actions-model.json')
json.dump(acts, open(path, 'w', encoding='utf-8'))
r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--actions', path, '--size', '1000x700'],
                   cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8'), capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3000)
out = (r.stdout or '') + (r.stderr or '')
open(os.path.join(folder, '_log-model.txt'), 'w', encoding='utf-8').write(out[:200000])
url = None
for l in out.splitlines():
    if 'data:image/png;base64,' in l:
        url = l.split('data:image/png;base64,')[1].strip().strip('"')
    elif 'result' in l or 'PROBLEMS' in l or 'console.' in l or 'EXCEPTION' in l or 'no console' in l:
        print(l[:200])
print('exit', r.returncode)
if url:
    from PIL import Image, ImageDraw
    open(os.path.join(folder, 'model-top.png'), 'wb').write(base64.b64decode(url))
    a = Image.open(os.path.join(folder, 'model-picture.png')).convert('RGB')
    b = Image.open(os.path.join(folder, 'model-top.png')).convert('RGB').resize((a.height, a.height), Image.LANCZOS)
    sheet = Image.new('RGB', (a.width + b.width, a.height), (20, 20, 24))
    sheet.paste(a, (0, 0)); sheet.paste(b, (a.width, 0))
    d = ImageDraw.Draw(sheet)
    d.text((6, 4), label + ': the 3D picture from above', fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((a.width + 6, 4), label + ': the colours a model gets (volume samples, unlit)', fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    sheet.save(os.path.join(HERE, 'model-%s.png' % label)); print('wrote out/r6/colour/model-%s.png' % label)
