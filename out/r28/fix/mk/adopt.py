"""Round 28, Track A, the fixer: take the three checkers' scripts as they are and point them at my folder and my page.

  python out/r28/fix/mk/adopt.py      -> out/r28/fix/eyes/mk, out/r28/fix/ui/mk, out/r28/fix/truth/mk

The copies differ from the checkers' own files only in where they read the page from and where they write:
  the page          dist/r28-<part>.html       -> the environment's FIX_PAGE, or dist/r28-fix.html
  the frozen page   dist/r28-base-<part>.html  -> dist/r28-base.html (the builder's own build of base20a)
  the folder        out/r28/<part>             -> out/r28/fix/<part>
  the project root  three folders up           -> four folders up
So "the script that showed the defect" runs unchanged in what it does, before and after a repair, and nothing of
the checkers' own logs and pictures is written over. (The truth checker's lists of balls, tkit.py, are used as they are.)
"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE); R28 = os.path.dirname(FIX)
PAGE = "os.environ.get('FIX_PAGE', 'dist/r28-fix.html')"

for part, folder in (('eyes', 'EYES'), ('ui', 'UI'), ('truth', 'TRUTH')):
    src = os.path.join(R28, part, 'mk'); dst = os.path.join(FIX, part, 'mk'); os.makedirs(dst, exist_ok=True)
    n = 0
    for fn in sorted(os.listdir(src)):
        if not fn.endswith(('.py', '.js', '.sh')):
            continue
        t = open(os.path.join(src, fn), encoding='utf-8').read(); t0 = t
        t = t.replace("'dist/r28-base-%s.html'" % part, "'dist/r28-base.html'")
        t = t.replace("os.environ.get('UI_PAGE', 'dist/r28-ui.html')", PAGE)
        t = t.replace("'dist/r28-%s.html'" % part, PAGE)
        t = t.replace('out/r28/%s' % part, 'out/r28/fix/%s' % part)
        t = t.replace('os.path.dirname(os.path.dirname(os.path.dirname(%s)))' % folder, 'os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(%s))))' % folder)
        if PAGE in t and not re.search(r'^import .*\bos\b', t, re.M):
            t = 'import os\n' + t
        open(os.path.join(dst, fn), 'w', encoding='utf-8', newline='\n').write(t)
        n += 1 if t != t0 else 0
        print('%-6s %-18s %s' % (part, fn, 'pointed at my folder' if t != t0 else 'as it is'))
    for sub in ('logs', 'shots'):
        os.makedirs(os.path.join(FIX, part, sub), exist_ok=True)
