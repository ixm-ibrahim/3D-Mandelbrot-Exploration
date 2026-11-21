"""Round 28, Track A, builder: is the program text for two equal spheres the frozen one, to the byte?

  python out/r28/fix/mk/frozen.py   -> out/r28/fix/logs/frozen.txt  (the builder's script, writing into the fixer's folder)

Compares, between base20a/js/32-balls.js and the overlay's copy: the text of GL_BALLS (from "const GL_BALLS = `" to
its closing "`;") and the long comment above it; and says which lines of the overlay's five files differ from the
frozen ones (counts only: out/r28/dials/changes.diff has the lines).
"""
import difflib, os
HERE = os.path.dirname(os.path.abspath(__file__)); FIXD = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FIXD))); D = os.path.join(ROOT, "out", "r28", "dials")


def read(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def gl(s):
    a = s.index('const GL_BALLS = `'); b = s.index('`;', a)
    return s[a:b + 2]


lines = []
base = read(os.path.join(ROOT, 'base20a', 'js', '32-balls.js')); new = read(os.path.join(D, 'overlay', 'js', '32-balls.js'))
lines.append('GL_BALLS, the program text for two equal spheres (%d characters): the same to the byte: %s' % (len(gl(base)), gl(base) == gl(new)))
ca = base[base.index('// The scene program of this group.'):base.index('const GL_BALLS = `')]
cb = new[new.index('// The scene program of this group.'):new.index('const GL_BALLS = `')]
lines.append('the comment above it: the same to the byte: %s' % (ca == cb))
lines.append('GL_BALLS_RHO, the new program text: %d characters, after GL_BALLS: %s' % (len(new[new.index('const GL_BALLS_RHO = `'):]), new.index('const GL_BALLS_RHO = `') > new.index('const GL_BALLS = `')))
for f in ('00-core.js', '32-balls.js', '40-render.js', '46-mesh.js', '80-ui.js'):
    a = read(os.path.join(ROOT, 'base20a', 'js', f)).split('\n'); b = read(os.path.join(D, 'overlay', 'js', f)).split('\n')
    plus = minus = 0
    for l in difflib.unified_diff(a, b, lineterm='', n=0):
        if l.startswith('+') and not l.startswith('+++'):
            plus += 1
        elif l.startswith('-') and not l.startswith('---'):
            minus += 1
    lines.append('%-13s %5d lines frozen, %5d in the overlay: %d taken out, %d put in' % (f, len(a), len(b), minus, plus))
text = '\n'.join(lines) + '\n'
open(os.path.join(FIXD, "logs", "frozen.txt"), 'w', encoding='utf-8', newline='\n').write(text)
print(text)
