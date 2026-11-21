"""The final checker: one short line a view from the eyes checker's walk log.   python -B out/r28/final/mk/sumwalk.py <walk log> [...]  -> logs/walk-summary.txt"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
out = []; tot = dict(views=0, rays=0, holes=0, thru=0, thru_ball=0, open=0)
for fn in sys.argv[1:]:
    out.append('from ' + fn)
    for l in open(fn, encoding='utf-8'):
        if ' 3D ' not in l:
            continue
        name = l.split()[0]
        g = lambda pat: (re.search(pat, l).group(1) if re.search(pat, l) else '?')
        rays = g(r'rays (\d+):'); holes = g(r'HOLES \(the page stops nowhere on such a ray\) (\d+)'); thru = g(r'SEEN THROUGH \(stop more than 2 px behind such a stretch\) (\d+)')
        tb = g(r'SEEN THROUGH \(stop more than 2 px behind such a stretch\) \d+ \(through a ball: (\d+)'); op = g(r'\(IN THE OPEN\): (\d+)')
        out.append('  %-28s rays %s, stops %s | HOLES %s | SEEN THROUGH %s (through a ball: %s) | IN THE OPEN %s | stops on what only the depth calls solid %s | picture against pick: %s painted as background where rays stop, %s painted where none stops'
                   % (name, rays, g(r'rays \d+: stop (\d+)'), holes, thru, tb, op, g(r'reaches a wall in 300 rounds\): (\d+)'), g(r'where rays stop all round (\d+ of \d+)'), g(r'where no ray stops all round (\d+ of \d+)')))
        tot['views'] += 1
        for k, v in (('rays', rays), ('holes', holes), ('thru', thru), ('thru_ball', tb), ('open', op)):
            tot[k] += int(v) if v.isdigit() else 0
out.append('TOTAL: %(views)d views, %(rays)d rays: HOLES %(holes)d, SEEN THROUGH %(thru)d (through a ball: %(thru_ball)d), IN THE OPEN %(open)d' % tot)
text = '\n'.join(out) + '\n'
open(os.path.join(FINAL, 'logs', 'walk-summary.txt'), 'w', encoding='utf-8', newline='\n').write(text); print(text)
