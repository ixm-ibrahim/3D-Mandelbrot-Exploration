"""Round 23, design: battery.json -> table.md (one table per shape).   python out/r23/design/table.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R

m = json.load(open(os.path.join(HERE, 'battery.json')))
names = [n for n in R.REF + R.SIX + ['cones2'] if '%s|flat' % n in m]
out = ['# Round 23, design: the numbers (made by table.py from battery.json; all measured)', '',
       'Blocks of side 0.02, orbit of each block centre. Columns are explained in battery.py.', '',
       '## Flat check (verdicts that differ from the flat orbit, of 20,000 each)', '',
       '| rule | Mandelbrot | c = -1 | rabbit | Siegel | a flat point is thrown off the plane by |', '|---|---|---|---|---|---|']
for n in names:
    f = m['%s|flat' % n]; out.append('| %s | %d | %d | %d | %d | %.1e |' % (n, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page']))
for s in ['basilica', 'sanmarco', 'rabbit', 'siegel', 'dendrite']:
    out += ['', '## %s' % R.SETNAME[s], '',
            '| rule | volume at 30 / 80 steps | kept from 30 to 80 | pieces of 8+ blocks | loose share | thin share | bodies after peeling (biggest holds) | bodies off the flat plane (joined, loose) | their long : thick, median (max) | over empty flat picture | above : below | meeting point | lift test |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for n in names:
        d = m.get('%s|%s' % (n, s))
        if not d:
            continue
        mt = d.get('meet')
        out.append('| %s | %.3f / %.3f | %s | %d | %.1f %% | %.1f %% | %d (%.2f) | %d (%d, %d) | %s | %.0f %% | %s | %s | %s |' % (
            n, d['vol30'], d['vol80'], ('%.1f %%' % (100 * d['vol80'] / d['vol30'])) if d['vol30'] > 0 else '-', d['pieces8'], 100 * d['loose'], 100 * d['thin'], d['bodies'], d['big'],
            d['off'], d['off_joined'], d['off_loose'], ('%.2f (%.2f)' % (d['off_ratio_median'], d['off_ratio_max'])) if d.get('off') else '-',
            100 * d['over'], ('%.2f' % d['up_down']) if d.get('up_down') else '-', ('%d patches, %.0f %%' % (mt['patches'], 100 * mt['share'])) if mt else '-',
            ('%.3f of %d' % (d['lift'], d['lift_n'])) if d['lift'] is not None else 'no flat inside'))
open(os.path.join(HERE, 'table.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
