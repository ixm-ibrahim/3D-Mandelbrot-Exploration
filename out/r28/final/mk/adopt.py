"""Round 28, Track A, the final checker: take the three checkers' OWN scripts (out/r28/{truth,eyes,ui}/mk, not the
fixer's copies) and point them at my page and my folder. Nothing else in them is changed.

  python -B out/r28/final/mk/adopt.py      -> out/r28/final/{truth,eyes,ui}/mk

  the page          dist/r28-<part>.html        -> dist/r28-final.html        (my build, command of out/r28/dials/BUILD.txt)
  the frozen page   dist/r28-base-<part>.html   -> dist/r28-base-final.html   (my build of base20a)
  the folder        out/r28/<part>              -> out/r28/final/<part>
  the project root  three folders up            -> four folders up
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE); R28 = os.path.dirname(FINAL)
PAGE = "'dist/r28-final.html'"; BASE = "'dist/r28-base-final.html'"

for part, folder in (('eyes', 'EYES'), ('ui', 'UI'), ('truth', 'TRUTH')):
    src = os.path.join(R28, part, 'mk'); dst = os.path.join(FINAL, part, 'mk'); os.makedirs(dst, exist_ok=True)
    for fn in sorted(os.listdir(src)):
        if not fn.endswith(('.py', '.js')):
            continue
        t = open(os.path.join(src, fn), encoding='utf-8').read(); t0 = t
        t = t.replace("'dist/r28-base-%s.html'" % part, BASE)
        t = t.replace("os.environ.get('UI_PAGE', 'dist/r28-ui.html')", PAGE)
        t = t.replace("'dist/r28-%s.html'" % part, PAGE)
        t = t.replace('out/r28/%s' % part, 'out/r28/final/%s' % part)
        t = t.replace("'../../r28/%s/" % part, "'../../r28/final/%s/" % part)
        t = t.replace("os.path.join('out', 'r28', '%s', 'mk', n)" % part, "os.path.join('out', 'r28', 'final', '%s', 'mk', n)" % part)
        t = t.replace("'r28-base-%s'" % part, "'r28-base-final'").replace("'r28-%s'" % part, "'r28-final'")
        t = t.replace('os.path.dirname(os.path.dirname(os.path.dirname(%s)))' % folder, 'os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(%s))))' % folder)
        open(os.path.join(dst, fn), 'w', encoding='utf-8', newline='\n').write(t)
        left = [l for l in t.splitlines() if re.search(r"r28-(%s|base-%s)\b" % (part, part), l)]
        print('%-6s %-18s %s%s' % (part, fn, 'pointed at my folder' if t != t0 else 'as it is', ('   STILL NAMES THE OLD PAGE: ' + ' | '.join(l.strip()[:90] for l in left)) if left else ''))
    for sub in ('logs', 'shots'):
        os.makedirs(os.path.join(FINAL, part, sub), exist_ok=True)
