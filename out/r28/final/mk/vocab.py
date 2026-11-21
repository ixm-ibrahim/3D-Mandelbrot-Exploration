"""The final checker: every sentence the page showed in my runs (status sentences, help texts, tooltips: read from the
logs of small7.py, f1.py and words.py) against the words section 4 of docs/ROUND27.md forbids.
  python -B out/r28/final/mk/vocab.py   -> out/r28/final/logs/vocab.txt"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
BAD = ['page', 'sheet', 'hinge', 'door', 'cone copy', 'critical', 'covers', 'winding', 'jacobian', 'stretch ratio', 'latitude', 'cusp', 'parabolic', 'loxodromic', 'moebius', 'möbius', 'mobius', 'lattice', 'discrete',
       'limit set', 'pearl tree', 'skew pillow', 'twin_tri', 'kfix', 'maskit', 'picard', 'gaussian', 'eisenstein', 'fuchsian', 'schottky', 'generator', 'isometr', 'conformal', 'hyperbolic', 'subgroup', 'orbit space', 'fundamental domain', 'rho', 'hull', 'spindle']
texts = set()
for fn in glob.glob(os.path.join(FINAL, 'logs', 'small7-*.txt')) + glob.glob(os.path.join(FINAL, 'ui', 'logs', 'f1-*.txt')) + glob.glob(os.path.join(FINAL, 'ui', 'logs', 'words-*.txt')):
    for l in open(fn, encoding='utf-8', errors='replace'):
        for m in re.finditer(r'sentences? \(\d+ characters, \d+ px high\): (.*)$', l):
            texts.add(m.group(1).strip())
        for m in re.finditer(r'\| sentence: (.*?)(?:  -> |  NOTE|$)', l):
            texts.add(m.group(1).strip())
        for m in re.finditer(r'"([^"]{12,})"', l):
            texts.add(m.group(1).strip())
sent = set()
for t in texts:
    for s in re.split(r'(?<=[.!?])\s+', t):
        s = s.strip()
        if len(s) > 8 and not s.startswith(('out/', 'dist/')):
            sent.add(re.sub(r'\d+(\.\d+)?', 'N', s))
out = ['%d different sentences or labels read from the logs (numbers written as N)' % len(sent)]
hits = 0
for s in sorted(sent):
    low = ' ' + re.sub(r'[^a-zäöü_ ]', ' ', s.lower()) + ' '
    found = [b for b in BAD if (' ' + b + ' ' in low) or (b in ('isometr',) and b in low)]
    if found:
        hits += 1; out.append('FORBIDDEN WORD %s in: %s' % (found, s))
out.append('sentences with a forbidden word: %d' % hits)
out.append('')
out += sorted(sent)
open(os.path.join(FINAL, 'logs', 'vocab.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); print('\n'.join(out[:60]))
