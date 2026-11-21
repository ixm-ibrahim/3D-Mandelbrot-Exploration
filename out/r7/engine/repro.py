"""The testers' own reproductions, through the page's real controls, on one page.

  python out/r7/engine/repro.py <page> <label>     pictures and log in out/r7/engine/<label>/ (names repro-*.png)

Covers solids-1, solids-2, the new notes and hints, flat-2, flat-3, flat-5 and walk-2 (the lost graphics context).
Prints the share of bright pixels of each picture (the solids tester's measure) and what each step returned.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
page, label = sys.argv[1], sys.argv[2]
PRE = r"""
const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const sel = (id, v) => { const e = $(id); e.value = String(v); e.dispatchEvent(new Event('change', { bubbles: true })); };
const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) throw new Error('no option ' + text); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const said = re => [...document.querySelectorAll('#secColour *')].filter(e => e.children.length === 0 && e.getBoundingClientRect().width > 0 && re.test(e.textContent)).map(e => e.textContent.slice(0, 90));
document.querySelectorAll('details.sec').forEach(d => { d.open = true; });
"""
STEPS = [
    ('solids-1-m-cross-skip0', "L.resetAll(); sel('col-trap', 1); sel('col-solid', 1); type('col-skipNum', '0'); await sleep(100); return 'skip ' + S.colour.skip + ' | ' + said(/hardly change/).join(' | ');"),
    ('solids-2-j-thick005', "L.resetAll(); $('mode-j').click(); type('cxNum', '-1'); type('cyNum', '0'); type('czNum', '0'); await sleep(200); sel('col-trap', 5); sel('col-solid', 1); type('col-radiusNum', '0.7'); await sleep(100); return 'thick ' + S.colour.thick;"),
    ('solids-2-j-thick0005', "type('col-thickNum', '0.005'); await sleep(100); return 'thick ' + S.colour.thick;"),
    ('solids-2-j-thick002', "type('col-thickNum', '0.02'); await sleep(100); return 'thick ' + S.colour.thick;"),
    ('solids-2-m-thick001', "L.resetAll(); sel('col-trap', 1); sel('col-solid', 1); type('col-skipNum', '1'); type('col-thickNum', '0.01'); await sleep(100); return 'thick ' + S.colour.thick + ' skip ' + S.colour.skip;"),
    ('notes-j-point', "L.resetAll(); $('mode-j').click(); await sleep(200); sel('col-solid', 1); sel('col-trap', 0); await sleep(150); return said(/thin shapes|cut open|same fine lace/).join(' | ');"),
    ('notes-k-e03', "L.resetAll(); $('mode-k').click(); await sleep(200); sel('kleinPreset', 4); $('kleinFrame').click(); sel('col-solid', 1); await sleep(200); const a = said(/cut open/).length; sel('col-trap', 0); await sleep(150); const b = said(/same fine lace/).length; sel('col-trap', 5); sel('kleinPreset', 1); $('kleinFrame').click(); await sleep(300); return 'entry 3: cut hint shown ' + a + ', lace note for Point ' + b + '; entry 0: cut hint shown ' + said(/cut open/).length;"),
    ('flat-2-k-settles', "L.resetAll(); $('flat').click(); $('mode-k').click(); await sleep(200); pick('col-inMode', 'How quickly'); await sleep(150); return said(/no orbit that settles/).join(' | ');"),
    ('flat-5-m-trap', "L.resetAll(); $('flat').click(); await sleep(200); pick('col-inMode', 'Orbit trap'); await sleep(150); return said(/half-way round/).join(' | ') + ' || outline help: ' + said(/web of such threads/).length;"),
    ('flat-3-cut-deep', "L.resetAll(); $('cutOn').click(); await sleep(200); $('col-cutFace').click(); pick('col-inMode', 'How deep inside'); cam.pitch = 1.1; L.touch(); await sleep(150); return 'cutFace ' + S.colour.cutFace + ' inMode ' + S.colour.inMode;"),
    ('flat-3-flat-deep', "L.resetAll(); $('flat').click(); await sleep(200); pick('col-inMode', 'How deep inside'); await sleep(150); return 'inMode ' + S.colour.inMode;"),
]
LOST = ("L.resetAll(); await sleep(200); await new Promise(r => { const f = () => L.idle() ? r() : setTimeout(f, 50); f(); });"
        "const before = $('status').textContent; const gl = $('view').getContext('webgl2'); window.__ext = gl.getExtension('WEBGL_lose_context'); window.__ext.loseContext();"
        "await sleep(400); const lost1 = $('status').textContent; $('mode-j').click(); await sleep(600); const lost2 = $('status').textContent;"
        "window.__ext.restoreContext(); return JSON.stringify({ before, lost1, lost2 });")
acts = [{'wait': 'done', 'timeout': 600}]
for name, js in STEPS:
    acts.append({'js': PRE + js})
    acts.append({'sleep': 0.2})
    acts.append({'wait': 'done', 'timeout': 900, 'shot': 'out/r7/engine/%s/repro-%s.png' % (label, name), 'clip': '#view'})
acts.append({'js': PRE + LOST})
acts.append({'sleep': 1.0})
acts.append({'wait': 'done', 'timeout': 900})
acts.append({'js': PRE + "return 'after the context came back: ' + $('status').textContent;"})
os.makedirs(os.path.join(HERE, label), exist_ok=True)
path = os.path.join(HERE, label, '_repro.json')
json.dump(acts, open(path, 'w', encoding='utf-8'))
r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--actions', path],
                   cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8'), capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3600)
out = (r.stdout or '') + (r.stderr or '')
open(os.path.join(HERE, label, '_repro-log.txt'), 'w', encoding='utf-8').write(out)
for l in out.splitlines():
    if 'result:' in l or 'TIMED OUT' in l or 'console.' in l or 'EXCEPTION' in l or 'PROBLEMS' in l or 'no console errors' in l:
        print(l[:420])
print('exit', r.returncode)
import numpy as np
from PIL import Image
for name, _ in STEPS:
    p = os.path.join(HERE, label, 'repro-%s.png' % name)
    if os.path.exists(p):
        a = np.asarray(Image.open(p).convert('RGB')).astype(int)
        print('%-28s bright pixels %5.2f %%   mean colour %s' % (name, 100 * float((a.max(axis=2) > 60).mean()), np.round(a.reshape(-1, 3).mean(axis=0), 1)))
