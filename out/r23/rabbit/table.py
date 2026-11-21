"""Markdown tables from numbers.json (measure.py) and nsweep.json.   python out/r23/rabbit/table.py > out/r23/rabbit/table.md"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import doors as D
m = json.load(open(os.path.join(HERE, 'numbers.json')))


def f(v, fmt='%.2f'):
    return '-' if v is None else fmt % v


def row(key, s, name=None):
    q = m.get('%s|%s' % (key, s))
    if q is None:
        return None
    mt = q.get('meet0.03'); off = q.get('off', 0)
    return '| %s | %.3f / %.3f | %d | %.1f %% | %.1f %% | %d (%.2f) | %s | %s | %s | %.2f | %.2f | %s |' % (
        name or key, q['vol30'], q['vol80'], q.get('pieces8', 0), 100 * q['loose'], 100 * q['thin'], q['bodies'], q['big'],
        ('%d patches, %.2f' % (mt['patches'], mt['share'])) if mt and s == 'rabbit' else '-',
        ('%d (%d joined, %d loose)' % (off, q['off_joined'], q['off_loose'])) if off else '0',
        ('%.2f (%.2f to %.2f)' % (q['off_ratio_median'], q['off_ratio_min'], q['off_ratio_max'])) if off else '-',
        q['over'], q['zmax'], f(q.get('lift'), '%.3f'))


HEAD = ('| rule | volume at 30 / 80 steps | pieces of 8+ blocks | loose share | thin share | bodies after peeling (biggest holds) | meeting point | bodies off the flat plane | their long : thick, median (range) | share standing over empty flat picture | highest point | lift test |\n'
        '|---|---|---|---|---|---|---|---|---|---|---|---|')
for s in ('rabbit', 'siegel', 'tilt', 'dendrite'):
    print('\n**%s** (c = %s)\n' % (D.SETNAME[s], ', '.join('%.4f' % t for t in D.SETS[s]))); print(HEAD)
    for k in D.ORDER:
        r = row(k, s)
        if r:
            print(r)
tr = [k for k in ('pilJA', 'pilT45', 'alongC') if ('%s|rabbit' % k) in m]
if tr:
    print('\n**The tries, rabbit**\n'); print(HEAD)
    for k in tr:
        print(row(k, 'rabbit'))
