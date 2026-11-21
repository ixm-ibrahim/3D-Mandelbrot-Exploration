"""Build a test page from a private copy of the live shader file with text replaced (to measure what a piece costs).

  python out/r5/speed/variant.py <name> "old=>new" ["old=>new" ...]     -> dist/r5-speed-<name>.html

The copy goes to out/r5/speed/var/30-shaders.<name>.js; src/ is not touched. The colour file and the renderer are
the live ones.
"""
import io, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
name = sys.argv[1]
s = io.open(os.path.join(ROOT, 'src/js/30-shaders.js'), encoding='utf-8').read().replace('\r\n', '\n')
for r in sys.argv[2:]:
    a, b = r.split('=>', 1)
    if a not in s:
        sys.exit('missing: ' + a)
    s = s.replace(a, b)
os.makedirs(os.path.join(ROOT, 'out/r5/speed/var'), exist_ok=True)
p = 'out/r5/speed/var/30-shaders.%s.js' % name
io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
subprocess.check_call([sys.executable, 'build.py', '--name', 'r5-speed-' + name, '--base', 'base5',
                       '--use', 'src/js/25-colour.js', 'src/js/40-render.js', '--swap', 'js/30-shaders.js=' + p], cwd=ROOT)
