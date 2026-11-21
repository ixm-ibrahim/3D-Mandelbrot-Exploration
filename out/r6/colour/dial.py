"""The new dial on the page: python out/r6/colour/dial.py  (writes out/r6/colour/dial-page.png, prints what it found)"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = ("const L = window.squaringLab, S = L.S, C = S.colour, $ = id => document.getElementById(id);"
       "const sleep = ms => new Promise(r => setTimeout(r, ms));"
       "const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };"
       "const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };")
acts = [
    {'wait': 'done', 'timeout': 600},
    {'js': PRE + "L.resetAll(); document.querySelectorAll('#sections > details.sec').forEach(d => d.open = d.id === 'secColour'); await sleep(300);"
           "const out = { shown3d: shown('col-reach'), value: C.reach, label: ($('col-reach') && ($('col-reach').closest('.dial, .ctl, div') || {}).textContent || '').slice(0, 60) };"
           "const before = L.R.compiles; type('col-reach', 9); await sleep(400); out.after = C.reach; out.compiles = L.R.compiles - before;"
           "type('col-reach', 2.6); await sleep(300); out.whole = C.reach;"
           "L.setExtreme && L.setExtreme(true); await sleep(200); type('col-reach', 400); await sleep(300); out.extreme = C.reach; L.setExtreme && L.setExtreme(false); await sleep(200); out.backFromExtreme = C.reach;"
           "type('col-reach', 4); await sleep(200);"
           "S.flat = true; L.syncControls(); L.refresh(false); await sleep(300); out.shown2d = shown('col-reach'); S.flat = false; L.syncControls(); L.refresh(false); await sleep(200);"
           "$('mode-k').click(); await sleep(400); out.shownKlein = shown('col-reach'); $('mode-m').click(); await sleep(300);"
           "C.mode = 2; L.syncControls(); L.refresh(false); await sleep(300); out.shownEscape = shown('col-reach'); C.mode = 0; L.syncControls(); L.refresh(false); await sleep(300);"
           "out.shownAgain = shown('col-reach'); return JSON.stringify(out);", 'timeout': 120},
    {'wait': 'done', 'timeout': 600, 'shot': 'out/r6/colour/dial-page.png'},
]
path = os.path.join(HERE, '_dial-actions.json')
json.dump(acts, open(path, 'w', encoding='utf-8'))
r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/r6-colour.html', '--actions', path, '--size', '1400x950'],
                   cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8'), capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
out = (r.stdout or '') + (r.stderr or '')
open(os.path.join(HERE, 'dial.log'), 'w', encoding='utf-8').write(out)
print(out[-1500:]); print('exit', r.returncode)
