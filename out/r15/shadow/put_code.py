"""Shadow, round 15B: make the private copy out/r15/shadow/10-approaches.js from base14b/js/10-approaches.js plus
block.js (code) and texts.js (the words), and build dist/r15-shadow.html. Run from the project root:
    python out/r15/shadow/put_code.py [--nobuild]
Three insertions, each between // R15B-BEGIN and // R15B-END: the block (before APPROACHES), the group, the entry."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
src = open(os.path.join(ROOT, 'base14b', 'js', '10-approaches.js'), encoding='utf-8').read()
block = open(os.path.join(HERE, 'block.js'), encoding='utf-8').read()
texts = open(os.path.join(HERE, 'texts.js'), encoding='utf-8').read().rstrip('\n')
assert '//__P4_TEXTS__' in block
block = block.replace('//__P4_TEXTS__', texts)

a = "\nconst APPROACHES = [\n"
assert src.count(a) == 1
src = src.replace(a, "\n" + block + a)

g = "  { id: 'angles', title: 'Angle rules' },\n"
assert src.count(g) == 1
src = src.replace(g, "  // R15B-BEGIN\n  { id: 'pillow', title: 'Doubling on a pillow grid' },\n  // R15B-END\n" + g)

assert src.rstrip().endswith('];')
src = src.rstrip()[:-2] + "  // R15B-BEGIN\n  P4_ENTRY,\n  // R15B-END\n];\n"
out = os.path.join(HERE, '10-approaches.js')
open(out, 'w', encoding='utf-8', newline='\n').write(src)
print('wrote', out, len(src), 'characters')
if '--nobuild' not in sys.argv:
    cmd = [sys.executable, 'build.py', '--name', 'r15-shadow', '--base', 'base14b', '--swap', 'js/10-approaches.js=out/r15/shadow/10-approaches.js']
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    print(p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace'))
    sys.exit(p.returncode)
