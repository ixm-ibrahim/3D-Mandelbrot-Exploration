"""Summarise the log of the entry run and compare the lists. python out/t9/kleinian/parse.py"""
import json, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
H = 'out/t9/kleinian'
def results(path):
    out = []
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'step (\d+) result: (.*)$', line.rstrip('\n'))
        if m:
            try: out.append((int(m.group(1)), json.loads(m.group(2))))
            except Exception as e: out.append((int(m.group(1)), m.group(2)))
    return out
def waits(path):
    return {int(m.group(1)): float(m.group(2)) for m in re.finditer(r'step (\d+) waited ([\d.]+) s', open(path, encoding='utf-8', errors='replace').read())}
data = json.load(open('data/klein-presets.json', encoding='utf-8'))
v5 = json.loads(results('out/t6/kleinian/v5.log')[0][1])
v6 = json.loads(results('out/t6/kleinian/a1.log')[1][1])
a = results(H + '/a.log')
v8 = json.loads(a[1][1])
print('entries: data', len(data), 'v5 page', len(v5), 'v6 page', len(v6), 'v8 page', len(v8))
print('v8 page list == data file:', v8 == data)
print('first 19 of v8 == the 19 of v5 (every field):', v8[:19] == v5)
strip = lambda L: [{k: v for k, v in p.items() if k != 'name'} for p in L]
print('v8 == v6 apart from names:', strip(v8) == strip(v6))
print('names changed since v6:', [(i, x['name'], '->', y['name']) for i, (x, y) in enumerate(zip(v6, v8)) if x['name'] != y['name']])
print('opening:', {k: v for k, v in a[0][1].items() if k != 'opts'})
opts8 = a[0][1]['opts']; opts5 = results('out/t6/kleinian/v5.log')[1][1]['opts']
print('options', len(opts8), '; first 20 same text and heading as v5:', [o.replace(' (disabled)', '') for o in opts8[:20]] == opts5)
grids = {}; rows = []
w = waits(H + '/a.log')
for step, r in a:
    if isinstance(r, dict) and 'grid' in r: grids[r['i']] = r['grid']
    elif isinstance(r, dict) and 'text' in r: rows.append((r, w.get(step)))
names = [p['name'] for p in data]
for r, wt in rows:
    i = r['i']; g = grids.get(i, [])
    hit = sum(row.count('1') for row in g); edge = (g[0] + g[-1]).count('1') + sum(row[0] == '1' or row[-1] == '1' for row in g) if g else -1
    cols = [c for row in g for c, ch in enumerate(row) if ch == '1'] or [-1]; rws = [j for j, row in enumerate(g) if '1' in row] or [-1]
    flag = []
    if r['text'] != names[i]: flag.append('NAME ' + r['text'])
    if r['closedText'] != names[i]: flag.append('CLOSED LIST READS ' + r['closedText'])
    if r['wrong']: flag.append('WRONG ' + str(r['wrong']))
    if not r['iterSame'] or r['iter'] != 150: flag.append('ITER ' + str(r['iter']))
    if not r['camSame']: flag.append('ENTRY MOVED CAMERA')
    if r['warn']: flag.append('WARN ' + r['warn'])
    print('%2d %-44s %-20s wait %4.1fs hits %3d/336 cols %2d-%2d rows %2d-%2d edge %d %s' % (i, r['text'][:44], r['group'], wt or -1, hit, min(cols), max(cols), min(rws), max(rws), edge, ' '.join(flag)))
