"""Round 27, fixer: what the fixer changed in the overlay. The overlay as the builder left it was copied to
out/r27/fix/before/overlay/ before the first edit; this writes the difference to out/r27/fix/fix.diff and prints how
many lines each file gained and lost.
  python out/r27/fix/mk/mkdiff.py
"""
import difflib, io, os
HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FIX)))
OLD = os.path.join(FIX, 'before', 'overlay'); NEW = os.path.join(ROOT, 'out', 'r27', 'entry', 'overlay')
out, summary = [], []
names = set()
for base in (OLD, NEW):
    for d, _, files in os.walk(base):
        for f in files:
            names.add(os.path.relpath(os.path.join(d, f), base).replace('\\', '/'))
for rel in sorted(names):
    a = io.open(os.path.join(OLD, rel), encoding='utf-8').read().replace('\r\n', '\n').splitlines() if os.path.exists(os.path.join(OLD, rel)) else []
    b = io.open(os.path.join(NEW, rel), encoding='utf-8').read().replace('\r\n', '\n').splitlines() if os.path.exists(os.path.join(NEW, rel)) else []
    if a == b:
        summary.append('%-22s unchanged' % rel); continue
    d = list(difflib.unified_diff(a, b, 'before/' + rel, 'after/' + rel, lineterm='', n=2))
    plus = sum(1 for l in d if l.startswith('+') and not l.startswith('+++')); minus = sum(1 for l in d if l.startswith('-') and not l.startswith('---'))
    summary.append('%-22s +%d -%d lines' % (rel, plus, minus))
    out += d + ['']
with io.open(os.path.join(FIX, 'fix.diff'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(out) + '\n')
print('\n'.join(summary))
