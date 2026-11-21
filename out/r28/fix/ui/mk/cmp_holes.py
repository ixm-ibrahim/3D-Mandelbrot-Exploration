"""Round 28, dial checker (ui): the lines of my run of round 27's holes.py on the new page, each set beside the
lines round 27 kept for the same view (out/r27/final/logs/holes*.txt, read only), and beside my own run on the frozen
page when there is one.   python -B out/r28/fix/ui/mk/cmp_holes.py   -> out/r28/fix/ui/logs/cmp-holes.txt
The numbers of a line are compared (every number in it, in order); the wording of the line changed between round
27's passes, so the text is not compared."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(UI))))
num = lambda l: re.findall(r'-?\d+(?:\.\d+)?(?:e-?\d+)?', l.split('| At ')[0].split('| The chain')[0])


def read(p):
    out = {}
    if not os.path.exists(p):
        return out
    for l in open(p, encoding='utf-8'):
        if l.strip() and not l.startswith('page'):
            out[l.split()[0]] = l.strip()
    return out


new = read(os.path.join(UI, 'r27-new', 'logs', 'holes.txt'))
old = read(os.path.join(UI, 'r27-old', 'logs', 'holes.txt'))
rec = {}
for p in sorted(glob.glob(os.path.join(ROOT, 'out', 'r27', 'final', 'logs', 'holes*.txt'))):
    for k, l in read(p).items():
        rec.setdefault(k, []).append((os.path.basename(p), l))
lines = []
for k, l in new.items():
    same_rec = [n for n, r in rec.get(k, []) if r == l]
    same_num = [n for n, r in rec.get(k, []) if num(r) == num(l)]
    s = '%-20s' % k
    if same_rec: s += ' the same line, letter for letter, as round 27 kept in ' + ', '.join(same_rec)
    elif same_num: s += ' the same numbers as round 27 kept in ' + ', '.join(same_num)
    else: s += ' no line of round 27 with the same numbers (kept in: %s)' % (', '.join(n for n, _ in rec.get(k, [])) or 'nowhere')
    if old:
        s += '; my run on the frozen page: ' + ('the same line, letter for letter' if old.get(k) == l else 'DIFFERS' if k in old else 'not run')
    lines.append(s)
    m = re.search(r'HOLES \(through a ball for more than 2 px\) (\d+)', l)
    lines.append('      holes %s | %s' % (m.group(1) if m else '?', l.split('| stops')[1][:330] if '| stops' in l else ''))
text = '\n'.join(lines) + '\n'
open(os.path.join(UI, 'logs', 'cmp-holes.txt'), 'w', encoding='utf-8', newline='\n').write(text)
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); print(text)
