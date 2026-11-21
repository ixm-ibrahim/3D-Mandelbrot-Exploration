"""Round 29, track "learn": run one of round 27's scripts (out/r27/final/mk/<name>.py) UNCHANGED IN WHAT IT DOES on the
page of this track, the way out/r28/final/ui/mk/old27.py does it, with everything it writes kept in out/r29/learn/r27/.

  python -B out/r29/learn/mk/old27b.py <name> [arguments of the script ...]
      name: verd | shape | same6 | holes | flat
The new page is dist/r29-learn.html, the frozen one dist/r29-learn-b0.html (built from base21a alone).
"""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
MK27 = os.path.join(ROOT, 'out', 'r27', 'final', 'mk')
name = sys.argv[1]
assert name in ('verd', 'shape', 'same6', 'holes', 'flat'), name
os.environ['R27_PAGE'] = os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')
os.environ['R27_BASE'] = 'dist/r29-learn-b0.html'
os.environ['R27_OUT'] = '../../r29/learn/r27'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
src_path = os.path.join(MK27, name + '.py')
text = open(src_path, encoding='utf-8').read()
text = text.replace("'out/r27/final/shots/", "run.OUT + '/shots/")
out_dir = os.path.join(ROOT, 'out', 'r29', 'learn', 'r27')
os.makedirs(os.path.join(out_dir, 'logs'), exist_ok=True); os.makedirs(os.path.join(out_dir, 'shots'), exist_ok=True)
os.chdir(ROOT)
sys.argv = [src_path] + sys.argv[2:]
sys.path.insert(0, MK27)
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass
import run as _run
assert os.path.normpath(_run.ENTRY) == os.path.normpath(out_dir), (_run.ENTRY, out_dir)
exec(compile(text, src_path, 'exec'), {'__name__': '__main__', '__file__': src_path})
