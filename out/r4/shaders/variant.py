"""Build a test page from a private copy of my shader file with text replaced.
  python out/r4/shaders/variant.py <name> "old=>new" ["old=>new" ...]   -> dist/r4-shaders-<name>.html"""
import io, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
name = sys.argv[1]
s = io.open(os.path.join(ROOT, 'src/js/30-shaders.js'), encoding='utf-8').read().replace('\r\n', '\n')
for r in sys.argv[2:]:
    a, b = r.split('=>', 1)
    if a not in s: sys.exit('missing: ' + a)
    s = s.replace(a, b)
os.makedirs(os.path.join(ROOT, 'out/r4/shaders/var'), exist_ok=True)
p = 'out/r4/shaders/var/30-shaders.%s.js' % name
io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
col = os.environ.get('COLOUR', 'out/r4/shaders/25-colour.js')
subprocess.check_call([sys.executable, 'build.py', '--name', 'r4-shaders-' + name, '--base', 'base4', '--swap', 'js/30-shaders.js=' + p, 'js/25-colour.js=' + col], cwd=ROOT)
