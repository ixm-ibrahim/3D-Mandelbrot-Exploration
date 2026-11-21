"""Drawing time of the opening Kleinian picture (and Mandelbrot, Julia), pages in turn, several rounds, one Chrome each.

  python out/r5/speed/kdraw.py <rounds> <page> [<page> ...]

Each visit: least of 8 drawings of the finished picture for K, then M, then J (c = -1). Prints every visit and the least per page.
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
if (L.R) L.R.warmOn = false;
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const draw = async () => { const t0 = performance.now(); L.touch(); await new Promise(r => { const f = () => L.idle() ? r() : setTimeout(f, 3); setTimeout(f, 40); }); return performance.now() - t0; };
const least = async n => { let m = 1e9; for (let i = 0; i < n; i++) m = Math.min(m, await draw()); return Math.round(m); };
"""
EXTRA = os.environ.get('KDRAW_JS', '')     # optional: run before the Kleinian picture is drawn (for example a quality preset)
steps = [{'js': PRE + "$('mode-k').click(); " + EXTRA + " go(); return 'k';", 'wait': 'done', 'timeout': 600},
         {'js': PRE + "return 'DRAW K ' + await least(8);", 'timeout': 600},
         {'js': PRE + "$('mode-m').click(); go(); return 'm';", 'wait': 'done', 'timeout': 600},
         {'js': PRE + "return 'DRAW M ' + await least(8);", 'timeout': 600},
         {'js': PRE + "$('mode-j').click(); L.S.c = [-1, 0, 0]; go(); return 'j';", 'wait': 'done', 'timeout': 600},
         {'js': PRE + "return 'DRAW J ' + await least(8);", 'timeout': 600}]
if os.environ.get('KONLY'): steps = steps[:2]   # the Kleinian picture only
path = os.path.join(HERE, 'kdraw-steps.json')
json.dump(steps, open(path, 'w', encoding='utf-8'))
rounds, pages = int(sys.argv[1]), sys.argv[2:]
best = {}
for r in range(rounds):
    for page in pages:
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--size', '1100x760', '--actions', path],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=1800)
        got = {}
        for l in ((p.stdout or '') + (p.stderr or '')).splitlines():
            if 'DRAW' in l:
                _, k, v = json.loads(l.split('result:', 1)[1].strip()).split()
                got[k] = int(v); best.setdefault(page, {})[k] = min(best.get(page, {}).get(k, 10 ** 9), int(v))
        print(time.strftime('%H:%M:%S'), page, got, 'exit', p.returncode, flush=True)
for page in pages:
    print('least', page, best.get(page))
