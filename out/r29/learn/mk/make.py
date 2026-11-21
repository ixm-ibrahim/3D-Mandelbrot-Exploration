# Round 29, track "learn": make the overlay from base21a and the pieces in this folder, then build dist/<name>.html.
#   PYTHONIOENCODING=utf-8 python -B -W ignore out/r29/learn/mk/make.py [name]      (name: r29-learn unless said)
# The overlay files are written afresh every time, so the frozen copy plus this folder is all there is to them.
import io, os, runpy, subprocess, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from patchlib import ROOT, BASE, OVER, read, frag

for script in ('patch65.py', 'patch66.py', 'patch67.py', 'patch68.py'):
    runpy.run_path(os.path.join(HERE, script), run_name='__main__')

# the style sheets: the frozen ones with this round's rules added at their ends
for rel, piece in (('css/65-learn.css', '65-css.css'), ('css/67-learn-shape.css', '67-css.css')):
    text = read(os.path.join(BASE, rel)).rstrip('\n') + '\n' + frag(piece)
    io.open(os.path.join(OVER, rel), 'w', encoding='utf-8', newline='\n').write(text)
    print('%s: rules added' % rel)

name = sys.argv[1] if len(sys.argv) > 1 else 'r29-learn'
files = ['js/65-learn-steps.js', 'js/66-learn-view.js', 'js/67-learn-shape.js', 'js/68-learn-shape3d.js', 'css/65-learn.css', 'css/67-learn-shape.css']
swap = ['%s=out/r29/learn/overlay/%s' % (f, f) for f in files]
line = 'PYTHONIOENCODING=utf-8 python -W ignore build.py --name r29-learn --base base21a --swap ' + ' '.join(swap)
io.open(os.path.join(ROOT, 'out', 'r29', 'learn', 'BUILD.txt'), 'w', encoding='utf-8', newline='\n').write(line + '\n')
r = subprocess.run([sys.executable, '-B', '-W', 'ignore', 'build.py', '--name', name, '--base', 'base21a', '--swap'] + swap, cwd=ROOT)
sys.exit(r.returncode)
