"""Round 28, truth checker: a page that did not finish its first picture.

  python out/r28/truth/mk/g_open.py [n]      -> out/r28/truth/logs/g_open.txt

In one of my runs (logs/bc_Q.log, first try) the page stood at "Preparing the formula" for the whole 900 s that the
first step waits for the picture as the page opens, before anything of mine had run; once my script clicked on, it
worked. Is that the new page, or the machine (other people's browsers were running)? Here the two pages are opened in
turn, n times each (default 25), the same way (tools/shot.py, the first step of all my runs: warming switched off,
then wait for the finished picture, at most 90 s), and the waits are written down.
"""
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import pagerun as R

n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
steps = [{'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up';", 'wait': 'done', 'timeout': 90},
         {'js': "const L = window.squaringLab; return JSON.stringify({ idle: L.idle(), status: document.getElementById('status').textContent, sig: String(L.R.sig || ''), failed: L.R.failed || '' });"}]
sj = os.path.join(R.LOGS, 'g_open-steps.json'); json.dump(steps, open(sj, 'w', encoding='utf-8'))
rows = {R.PAGE: [], R.BASE: []}; lines = []
for i in range(n):
    for page in (R.PAGE, R.BASE):
        t0 = time.time()
        p = subprocess.run([sys.executable, '-W', 'ignore', os.path.join(R.ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj, '--size', '1400x950'],
                           capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'), cwd=R.ROOT)
        text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
        m = re.search(r'step 1 waited ([\d.]+) s', text); to = 'TIMED OUT' in text
        st = re.search(r'step 2 result: (.*)', text)
        rows[page].append((float(m.group(1)) if m else None, to, p.returncode))
        lines.append('%2d %-26s wait %s%s exit %d, whole launch %.0f s | %s' % (i + 1, page, m.group(1) + ' s' if m else '-', ' TIMED OUT (90 s)' if to else '', p.returncode, time.time() - t0, st.group(1)[:200] if st else text[-200:].replace('\n', ' / ')))
        print(lines[-1], flush=True)
        open(os.path.join(R.LOGS, 'g_open.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
for page, r in rows.items():
    w = sorted(x[0] for x in r if x[0] is not None)
    lines.append('%s: %d launches, %d did not finish the first picture in 90 s; waits of the others: least %.1f s, middle %.1f s, most %.1f s'
                 % (page, len(r), sum(1 for x in r if x[1]), w[0] if w else 0, w[len(w) // 2] if w else 0, w[-1] if w else 0))
    print(lines[-1])
open(os.path.join(R.LOGS, 'g_open.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
