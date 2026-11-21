"""A look at the new features of the joined page, as the user would meet them. Writes out/me/look6/*.png.

  python out/me/look6.py [page]        page is a name in dist/ without .html (default v6a)
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
page = sys.argv[1] if len(sys.argv) > 1 else 'v6a'
tag = sys.argv[2] if len(sys.argv) > 2 else 'look6'
os.makedirs(os.path.join(ROOT, 'out', 'me', tag), exist_ok=True)

PRE = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const col = o => Object.assign(L.S.colour, o);
"""
steps = []
def step(js, name=None, wait='done', clip='#stage'):
    a = {'js': PRE + js, 'timeout': 600}
    if wait: a['wait'] = wait
    if name:
        a['shot'] = 'out/me/%s/%s.png' % (tag, name)
        if clip: a['clip'] = clip
    steps.append(a)

# 1 the opening picture, and the same with a wider glow
step("return 'open: ' + JSON.stringify(L.S.colour);", '01-open')
step("col({glow: 2}); go(); return 'glow 2';", '02-glow2')
step("col({glow: 3}); go(); return 'glow 3';", '03-glow3')
step("col({glow: 1, radius: 0.7}); go(); return 'radius 0.7';", '04-radius07')
step("col({radius: 1.4}); go(); return 'radius 1.4';", '05-radius14')
# 2 trap solids on the Julia set for c = -1
step("col({radius: 1, glow: 1}); $('mode-j').click(); L.S.c = [-1, 0, 0]; L.resetCam(); col({solid: 1}); go(); return 'julia shell solid: ' + JSON.stringify(L.S.colour);", '06-j-shell-solid')
step("col({solid: 2}); go(); return 'julia shell added';", '07-j-shell-added')
step("col({solid: 1, trap: 1}); go(); return 'julia cross solid';", '08-j-cross-solid')
step("col({solid: 1, trap: 6}); go(); return 'julia ring solid';", '09-j-ring-solid')
# 3 trap solid on the Mandelbrot
step("$('mode-m').click(); L.resetCam(); col({solid: 1, trap: 5}); go(); return 'mandelbrot shell solid';", '10-m-shell-solid')
step("col({solid: 2, trap: 1}); go(); return 'mandelbrot cross added';", '11-m-cross-added')
# 4 the 2D view with the inside coloured
step("col({solid: 0, trap: 5}); L.S.flat = true; go(); return '2D plain';", '12-flat-plain')
step("col({inMode: 4}); go(); return '2D inside: how quickly it settles';", '13-flat-settles')
step("col({inMode: 1}); go(); return '2D inside: orbit trap';", '14-flat-intrap')
step("col({inMode: 2, edge: 2, edgeGlow: 6}); go(); return '2D inside: where it ends up, outline 2, glow 6';", '15-flat-ends')
# 5 the cut face coloured like the inside
step("col({inMode: 4, edge: 1, edgeGlow: 0, cutFace: true}); L.S.flat = false; L.S.cutOn = true; L.S.cut = 0; go(); return 'cut open at 0, face coloured: cutOn ' + L.S.cutOn;", '16-cut-face')
# 6 Kleinian: a new entry, framed; then a trap solid
step("col({inMode: 0, cutFace: false}); L.S.cutOn = false; $('mode-k').click(); await sleep(200); const s = $('kleinPreset'); const names = [...s.options].map(o => o.text); s.selectedIndex = Math.min(s.options.length - 1, 26); s.dispatchEvent(new Event('change', { bubbles: true })); await sleep(200); $('kleinFrame').click(); await sleep(200); return 'klein entry: ' + s.options[s.selectedIndex].text + ' of ' + names.length;", '17-k-entry')
step("const s = $('kleinPreset'); s.selectedIndex = Math.min(s.options.length - 1, 31); s.dispatchEvent(new Event('change', { bubbles: true })); await sleep(200); $('kleinFrame').click(); await sleep(200); return 'klein entry: ' + s.options[s.selectedIndex].text;", '18-k-entry2')
step("L.resetAll ? L.resetAll() : 0; $('mode-k').click(); await sleep(200); col({solid: 1}); go(); return 'klein shell solid';", '19-k-shell-solid')
step("col({solid: 2}); go(); return 'klein shell added';", '20-k-shell-added')
# 7 the whole page with the colour section open, for the new controls
step("col({solid: 1}); $('mode-m').click(); document.querySelectorAll('#sections > details.sec').forEach(d => d.open = d.id === 'secColour'); go(); await sleep(300); return 'colour section';", '21-page-colour', clip=None)
step("L.S.flat = true; go(); await sleep(300); return 'colour section, 2D';", '22-page-colour-2d', clip=None)

path = os.path.join(ROOT, 'out', 'me', tag + '.json')
json.dump(steps, open(path, 'w', encoding='utf-8'), indent=1)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--size', '1400x950', '--actions', path],
                   cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3000)
out = (r.stdout or '') + (r.stderr or '')
open(os.path.join(ROOT, 'out', 'me', tag + '.log'), 'w', encoding='utf-8').write(out)
for l in out.splitlines():
    if 'result' in l or 'rror' in l or 'exit' in l:
        print(l[:300])
print('exit', r.returncode)
