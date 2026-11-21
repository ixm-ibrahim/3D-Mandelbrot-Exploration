"""Round 28, dial checker (ui): run one of round 27's scripts (out/r27/final/mk/<name>.py) UNCHANGED IN WHAT IT DOES,
on a page of round 28, with everything it writes kept in out/r28/fix/ui/r27-<tag>/.

  python -B out/r28/fix/ui/mk/old27.py <name> <tag> [arguments of the script ...]
      name: verd | shape | same6 | holes | flat          tag: new (dist/r28-ui.html) | old (dist/r28-base-ui.html)

How: the scripts read R27_PAGE, R27_BASE and R27_OUT from the environment (run.py). R27_OUT is a folder under
out/r27/final/, so "../../r28/ui/r27-<tag>" lands in my folder. Two of the scripts (holes.py, flat.py) also name a
picture with the fixed text 'out/r27/final/shots/...': that text alone is changed to run.OUT + '/shots/...' in the
copy that is run (the copy is kept beside the logs as <name>-as-run.py). Nothing is written under out/r27.
"""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(UI))))
MK27 = os.path.join(ROOT, 'out', 'r27', 'final', 'mk')
name, tag = sys.argv[1], sys.argv[2]
assert name in ('verd', 'shape', 'same6', 'holes', 'flat'), name
assert tag in ('new', 'old'), tag
os.environ['R27_PAGE'] = os.environ.get('FIX_PAGE', 'dist/r28-fix.html') if tag == 'new' else 'dist/r28-base.html'
os.environ['R27_BASE'] = 'dist/r28-base.html'
os.environ['R27_OUT'] = '../../r28/ui/r27-' + tag
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
src_path = os.path.join(MK27, name + '.py')
text = open(src_path, encoding='utf-8').read()
n_fixed = text.count("'out/r27/final/shots/")
text = text.replace("'out/r27/final/shots/", "run.OUT + '/shots/")
out_dir = os.path.join(UI, 'r27-' + tag)
os.makedirs(os.path.join(out_dir, 'logs'), exist_ok=True); os.makedirs(os.path.join(out_dir, 'shots'), exist_ok=True)
with open(os.path.join(out_dir, 'logs', name + '-as-run.py'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# copy of out/r27/final/mk/%s.py as run by out/r28/fix/ui/mk/old27.py: %d fixed picture path(s) changed, nothing else\n' % (name, n_fixed) + text)
os.chdir(ROOT)
sys.argv = [src_path] + sys.argv[3:]
sys.path.insert(0, MK27)
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass
import run as _run
assert os.path.normpath(_run.ENTRY) == os.path.normpath(out_dir), (_run.ENTRY, out_dir)
exec(compile(text, src_path, 'exec'), {'__name__': '__main__', '__file__': src_path})
