"""Round 29, Track A, builder: are the two old program texts the frozen ones, to the byte? And what did the overlay
change, file by file?

  python -B out/r29/free/mk/frozen29.py   -> out/r29/free/logs/frozen.txt, out/r29/free/changes.diff

Compares, between base21a/js/32-balls.js and the overlay's copy: the text of GL_BALLS and of GL_BALLS_RHO (from
"const GL_... = `" to the closing "`;") and the comments above them; counts the lines of each overlay file that differ
from the frozen one; and writes the full difference to changes.diff (difflib, no git).
"""
import difflib, os
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(D)))


def read(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def gl(s, name):
    a = s.index('const %s = `' % name); b = s.index('`;', a)
    return s[a:b + 2]


lines = []
base = read(os.path.join(ROOT, 'base21a', 'js', '32-balls.js')); new = read(os.path.join(D, 'overlay', 'js', '32-balls.js'))
for name in ('GL_BALLS', 'GL_BALLS_RHO'):
    lines.append('%s (%d characters): the same to the byte: %s' % (name, len(gl(base, name)), gl(base, name) == gl(new, name)))
ca = base[base.index('// The scene program of this group.'):]
cb = new[new.index('// The scene program of this group.'):new.index('// The same program for every pair of numbers the two programs above were not written for')]
lines.append('everything from "// The scene program of this group." to the end of GL_BALLS_RHO (both texts and the two long comments, %d characters): the same to the byte: %s'
             % (len(ca), ca.rstrip('\n') == cb.rstrip('\n')))
lines.append('GL_BALLS_FREE, the new program text: %d characters, after the two old ones: %s' % (len(gl(new, 'GL_BALLS_FREE')), new.index('const GL_BALLS_FREE = `') > new.index('const GL_BALLS_RHO = `')))
diff = []
for f in ('32-balls.js', '40-render.js', '80-ui.js'):
    a = read(os.path.join(ROOT, 'base21a', 'js', f)).split('\n'); b = read(os.path.join(D, 'overlay', 'js', f)).split('\n')
    plus = minus = 0
    for l in difflib.unified_diff(a, b, 'base21a/js/' + f, 'out/r29/free/overlay/js/' + f, lineterm='', n=2):
        diff.append(l)
        if l.startswith('+') and not l.startswith('+++'):
            plus += 1
        elif l.startswith('-') and not l.startswith('---'):
            minus += 1
    lines.append('%-13s %5d lines frozen, %5d in the overlay: %d taken out, %d put in' % (f, len(a), len(b), minus, plus))
for f in sorted(os.listdir(os.path.join(ROOT, 'base21a', 'js'))):
    if f not in ('32-balls.js', '40-render.js', '80-ui.js') and os.path.exists(os.path.join(D, 'overlay', 'js', f)):
        lines.append('UNEXPECTED overlay file ' + f)
open(os.path.join(D, 'changes.diff'), 'w', encoding='utf-8', newline='\n').write('\n'.join(diff) + '\n')
text = '\n'.join(lines) + '\n'
open(os.path.join(D, 'logs', 'frozen.txt'), 'w', encoding='utf-8', newline='\n').write(text)
print(text)
