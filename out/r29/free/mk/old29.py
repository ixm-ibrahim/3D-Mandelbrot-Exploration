"""Round 29, Track A, builder, section 4 point 8: round 27's and round 28's own checks on the new page, UNCHANGED IN
WHAT THEY DO, with everything they write kept in out/r29/free/old/<name>/ (nothing is written under out/r27 or
out/r28).

  python -B out/r29/free/mk/old29.py <verd|shape|same28|same28e>

verd, shape: out/r27/final/mk/<name>.py. They read R27_PAGE, R27_BASE and R27_OUT from the environment (run.py);
             R27_OUT is a folder under out/r27/final/, so "../../r29/free/old/<name>" lands here.
same28:      out/r28/dials/mk/same.py (the builder's nine states, the picture of the new page against the frozen page).
same28e:     out/r28/eyes/mk/same.py (the eyes' seventeen states and the whole window).
             Their helper modules (run28, eyerun) are imported and pointed at this folder and at the two pages of
             this round before the script runs: dist/r29-free.html against dist/r29-free-base.html (base21a alone).
"""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); FREE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FREE)))
name = sys.argv[1]
assert name in ('verd', 'shape', 'same28', 'same28e'), name
PAGE, BASE = 'dist/r29-free.html', 'dist/r29-free-base.html'
out_rel = 'out/r29/free/old/' + name; out_dir = os.path.join(ROOT, out_rel)
for sub in ('logs', 'shots', 'same'):
    os.makedirs(os.path.join(out_dir, sub), exist_ok=True)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'; os.environ['PYTHONIOENCODING'] = 'utf-8'
os.chdir(ROOT)
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass
if name in ('verd', 'shape'):
    mk = os.path.join(ROOT, 'out', 'r27', 'final', 'mk')
    os.environ['R27_PAGE'] = PAGE; os.environ['R27_BASE'] = BASE; os.environ['R27_OUT'] = '../../r29/free/old/' + name
    sys.path.insert(0, mk)
    import run as _run
    assert os.path.normpath(_run.ENTRY) == os.path.normpath(out_dir), (_run.ENTRY, out_dir)
    src = os.path.join(mk, name + '.py')
else:
    mk = os.path.join(ROOT, 'out', 'r28', 'dials' if name == 'same28' else 'eyes', 'mk')
    sys.path.insert(0, mk)
    if name == 'same28':
        import run28 as _run
        _run.DIALS = out_dir
    else:
        import eyerun as _run
        _run.EYES = out_dir
    _run.OUT = out_rel; _run.LOGS = os.path.join(out_dir, 'logs'); _run.PAGE = PAGE; _run.BASE = BASE
    src = os.path.join(mk, 'same.py')
text = open(src, encoding='utf-8').read()
sys.argv = [src] + sys.argv[2:]
exec(compile(text, src, 'exec'), {'__name__': '__main__', '__file__': src})
