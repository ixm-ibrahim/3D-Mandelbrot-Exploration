"""Round 28, Track A, the final checker: the old lists on dist/r28-final.html against what was kept for Version 20.
Nothing is run here; it reads the logs.     python -B out/r28/final/mk/cmp_old.py   -> out/r28/final/logs/cmp-old.txt

Round 26 (use.js, spot.js, phone.js): the result line of every step against the lines round 26 kept for Version 20
(out/r26/final/v20-*.log) and against the dial checker's run on the page before the repairs (out/r28/ui/r26/*-new.log).
Round 27 (verd, shape, same6, flat, holes): every line of the script's own text against the dial checker's run on
the page before the repairs (out/r28/ui/r27-new/logs/*.txt), which that checker had held against Version 20's lines.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FINAL)))
out = []


def res(path):
    d = {}
    if not os.path.exists(path):
        return None
    for l in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'step (\d+) result: (.*)$', l.rstrip('\n'))
        if m:
            d[int(m.group(1))] = m.group(2)
    return d


def tail(path):
    t = open(path, encoding='utf-8', errors='replace').read() if os.path.exists(path) else ''
    return ('exit code 0' in t or 'exit 0' in t), ('no console errors' in t)


out.append('ROUND 26')
for name in ('use', 'spot', 'phone'):
    mine = os.path.join(FINAL, 'ui', 'r26', name + '-new.log')
    a = res(mine); b = res(os.path.join(ROOT, 'out', 'r26', 'final', 'v20-%s.log' % name)); c = res(os.path.join(ROOT, 'out', 'r28', 'ui', 'r26', name + '-new.log'))
    if a is None:
        out.append('%s.js: NOT RUN' % name); continue
    ex, cl = tail(mine)
    out.append('%s.js on the final page: %d result lines, exit 0: %s, "no console errors": %s' % (name, len(a), ex, cl))
    for label, o in (('the lines kept for Version 20', b), ('the dial checker\'s run before the repairs', c)):
        if o is None:
            out.append('   %s: no such log' % label); continue
        keys = sorted(set(a) | set(o)); diff = [k for k in keys if a.get(k) != o.get(k)]
        out.append('   against %s: %d of %d result lines the same word for word' % (label, len(keys) - len(diff), len(keys)))
        for k in diff:
            x, y = a.get(k, '(no line)'), o.get(k, '(no line)')
            # show only the place where the two differ
            i = 0
            while i < min(len(x), len(y)) and x[i] == y[i]:
                i += 1
            out.append('      step %d differs from character %d:\n         final page: ...%s\n         other:      ...%s' % (k, i, x[max(0, i - 60):i + 100], y[max(0, i - 60):i + 100]))
out.append('')
out.append('ROUND 27')
for name in ('verd', 'shape', 'same6', 'flat', 'holes'):
    mine = os.path.join(FINAL, 'ui', 'r27-new', 'logs', name + '.txt'); other = os.path.join(ROOT, 'out', 'r28', 'ui', 'r27-new', 'logs', name + '.txt')
    if not os.path.exists(mine):
        out.append('%s.py: NOT RUN (no %s)' % (name, mine)); continue
    A = [l.rstrip('\n') for l in open(mine, encoding='utf-8', errors='replace')]; B = [l.rstrip('\n') for l in open(other, encoding='utf-8', errors='replace')]
    norm = lambda l: l.replace('dist/r28-final.html', 'PAGE').replace('dist/r28-ui.html', 'PAGE').replace('dist/r28-base-final.html', 'BASE').replace('dist/r28-base-ui.html', 'BASE').replace('out/r28/final/ui', 'OUT').replace('out/r28/ui', 'OUT').replace('r28/final/ui', 'OUT').replace('r28/ui', 'OUT')
    An = [norm(l) for l in A]; Bn = [norm(l) for l in B]
    same = sum(1 for x, y in zip(An, Bn) if x == y)
    out.append('%s.py on the final page: %d lines; the dial checker\'s run before the repairs: %d lines; the same letter for letter (page names apart): %d; "no console errors" in mine: %s'
               % (name, len(A), len(B), same, any('no console errors' in l for l in A)))
    for i, (x, y) in enumerate(zip(An, Bn)):
        if x != y:
            j = 0
            while j < min(len(x), len(y)) and x[j] == y[j]:
                j += 1
            out.append('      line %d differs from character %d:\n         final page: ...%s\n         other:      ...%s' % (i + 1, j, x[max(0, j - 60):j + 120], y[max(0, j - 60):j + 120]))
text = '\n'.join(out) + '\n'
open(os.path.join(FINAL, 'logs', 'cmp-old.txt'), 'w', encoding='utf-8', newline='\n').write(text)
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); print(text)
