"""Round 28, truth checker: the totals of my runs, and the page's ballsReach() against my formula for the chain's end.
  python out/r28/truth/mk/h_totals.py      -> out/r28/truth/logs/h_totals.txt      (reads logs/bc_<key>.json, logs/raw/, no browser)"""
import gzip, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T
import bc_page as B
lines = []; tw = [0, 0]; fl = [0, 0]; sp = [0, 0]; es = {}; sh = [0, 0, 0]; n = 0; nrho = 0; worst = 0.0
for key, (words, rho, t, gname, depth) in B.SETS.items():
    fn = os.path.join(TRUTH, 'logs', 'bc_%s.json' % key)
    if not os.path.exists(fn):
        continue
    r = json.load(open(fn, encoding='utf-8')); n += 1; top = 2 * float(t); p = 100 / (top - 1)
    nrho += int(rho < 1 and p > 100 * (1 + 1e-9))
    tw[0] += r['twin_diff']; tw[1] += r['twin_n']; fl[0] += r['sh_flat'][1]; fl[1] += r['sh_flat'][0]; sp[0] += r['sh_space'][1]; sp[1] += r['sh_space'][0]
    sh[0] += r['sh_over']; sh[1] += r.get('sh_over_any', 0); sh[2] += r['sh_n']
    for name, v in r['est'].items():
        a = es.setdefault(name, [0, 0]); a[0] += v['over']; a[1] += v['n']
    raw = json.load(gzip.open(os.path.join(TRUTH, 'logs', 'raw', 'bc_%s.json.gz' % key), 'rt', encoding='utf-8'))
    mine = T.hulls(top, float(rho))['reach']; page = raw['page']['reach']
    d = 0.0 if (page is None and not np.isfinite(mine)) else abs(page - mine) / mine if page is not None and np.isfinite(mine) else float('inf')
    worst = max(worst, d)
    lines.append('%s  rho %-8.5g p %-9.3f %-6s depth %-4d | the chain ends at x = %s by ballsReach(), %s by my formula | the sentence: "%s"' % (key, rho, p, gname, depth, 'no end' if page is None else '%.9f' % page, '%.9f' % mine if np.isfinite(mine) else 'no end', raw['page']['warn']))
lines.append('')
lines.append('%d settings, %d of them with a smaller second sphere and neighbours past 100.' % (n, nrho))
lines.append('b. twin against my recipe: %d of %d verdicts differ. Shader against my recipe: flat cut %d of %d, in space %d of %d.' % (tw[0], tw[1], fl[0], fl[1], sp[0], sp[1]))
lines.append('c. ballsEstimate longer than the true distance to the nearest listed ball: ' + ', '.join('%s %d of %d' % (k, v[0], v[1]) for k, v in es.items()) + '; all sets %d of %d.' % (sum(v[0] for v in es.values()), sum(v[1] for v in es.values())))
lines.append('c. the shader\'s own number at %d outside grid points: above the true distance at %d (it IS the true distance wherever "best" is the smaller number, and single precision puts it a hair above or below), by more than my first allowance at %d.' % (sh[2], sh[1], sh[0]))
lines.append('ballsReach() against my formula k^2 / 2 + k^2 HB / (1 - HB): largest relative difference %.1e' % worst)
out = '\n'.join(lines) + '\n'; open(os.path.join(TRUTH, 'logs', 'h_totals.txt'), 'w', encoding='utf-8', newline='\n').write(out); print(out)
