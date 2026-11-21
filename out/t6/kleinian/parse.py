"""Summarise the logs of the entry runs and compare the lists. python out/t6/kleinian/parse.py"""
import json, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
H = 'out/t6/kleinian'
def results(name):
    out = []
    for line in open(os.path.join(H, name + '.log'), encoding='utf-8', errors='replace'):
        m = re.match(r'step (\d+) result: (.*)$', line.rstrip('\n'))
        if m:
            try: out.append((int(m.group(1)), json.loads(m.group(2))))
            except Exception as e: out.append((int(m.group(1)), m.group(2)))
    return out
def waits(name):
    return {int(m.group(1)): float(m.group(2)) for m in re.finditer(r'step (\d+) waited ([\d.]+) s', open(os.path.join(H, name + '.log'), encoding='utf-8', errors='replace').read())}
data = json.load(open('data/klein-presets.json', encoding='utf-8'))
v5 = json.loads(results('v5')[0][1])
a1 = results('a1')
v6 = json.loads(a1[1][1])
print('entries: data', len(data), 'v5 page', len(v5), 'v6 page', len(v6))
print('v6 page list == data file:', v6 == data)
print('first 19 of v6 == the 19 of v5 (every field):', v6[:19] == v5)
for i, (a, b) in enumerate(zip(v6, v5)):
    if a != b: print('  differs', i, a, b)
print('opening:', {k: v for k, v in a1[0][1].items() if k != 'opts'})
opts6 = a1[0][1]['opts']; opts5 = results('v5')[1][1]['opts']
print('first 20 options same text and heading as v5:', [o.replace(' (disabled)', '') for o in opts6[:20]] == opts5)
grids = {}
rows = []
for run in ('a1', 'a2', 'a3'):
    w = waits(run)
    for step, r in results(run):
        if isinstance(r, dict) and 'grid' in r: grids[r['i']] = r['grid']
        elif isinstance(r, dict) and 'text' in r: rows.append((r, w.get(step)))
names = [p['name'] for p in data]
for r, w in rows:
    i = r['i']; g = grids.get(i, [])
    hit = sum(row.count('1') for row in g); edge = (g[0] + g[-1]).count('1') + sum(row[0] == '1' or row[-1] == '1' for row in g) if g else -1
    cols = [c for row in g for c, ch in enumerate(row) if ch == '1']; rws = [j for j, row in enumerate(g) if '1' in row]
    flag = []
    if r['text'] != names[i]: flag.append('NAME ' + r['text'])
    if r['wrong']: flag.append('WRONG ' + str(r['wrong']))
    if not r['iterSame'] or r['iter'] != 150: flag.append('ITER ' + str(r['iter']))
    if not r['camSame']: flag.append('ENTRY MOVED CAMERA')
    if r['warn']: flag.append('WARN ' + r['warn'])
    print('%2d %-74s %-40s wait %4.1fs hits %3d/336 cols %2d-%2d rows %2d-%2d edge %d %s' % (i, r['text'][:74], r['group'], w or -1, hit, min(cols), max(cols), min(rws), max(rws), edge, ' '.join(flag)))
