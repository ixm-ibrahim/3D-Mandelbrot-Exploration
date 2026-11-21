import re, sys, collections
p = sys.argv[1] if len(sys.argv) > 1 else 'out/r13/steps/results.txt'
L = open(p, encoding='utf-8').read().splitlines()
print(L[-1])
kinds = collections.Counter(); ex = {}
cur = None
for l in L[1:-1]:
    if l.startswith('      ! '):
        t = l[8:]
        k = t.split(':')[0]
        grp = cur.split()[0] if not cur.startswith('space') else ' '.join(cur.split()[:2])
        key = (grp, k)
        kinds[key] += 1
        ex.setdefault(key, (cur, t[:330]))
    else:
        cur = l[:74].strip()
        f = l[74:].split()
for k, v in sorted(kinds.items()):
    print('%-22s %-14s configs with it: %3d   e.g. %s || %s' % (k[0], k[1], v, ex[k][0], ex[k][1]))
# per approach table
agg = collections.OrderedDict()
for l in L[1:-1]:
    if l.startswith('      ! '): continue
    lab = l[:74].strip(); rest = l[74:]
    m = re.search(r'\s(\d+)\s+([\d.e+-]+|inf|nan)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)%\s+(\d+)\s+(\d+)', rest)
    if not m: print('??', l); continue
    grp = lab.split()[0] if not lab.startswith('space') else ' '.join(lab.split()[:2])
    a = agg.setdefault(grp, dict(cfg=0, pts=0, rel=0.0, cf=0, at0=0, jm=0, jf=0, sn=0, sf=0))
    a['cfg'] += 1; a['pts'] += int(m.group(1)); a['rel'] = max(a['rel'], float(m.group(2))); a['cf'] += int(m.group(3)); a['at0'] += int(m.group(4))
    a['jm'] += int(m.group(5)); a['jf'] += int(m.group(6)); a['sn'] += int(m.group(8)); a['sf'] += int(m.group(9))
    k = re.search(r'jump: origin (\d+), ratio (\d+), other (\d+) \| geom (\d+) fail (\d+) \| key (\d+)', rest)
    for i, nm in enumerate(['jo', 'jr', 'jx', 'gn', 'gf', 'kf']): a[nm] = a.get(nm, 0) + int(k.group(i + 1))
print('%-10s %4s %7s %9s %6s %4s %8s %5s %6s %6s %6s %7s %5s %4s %8s %5s' % ('group', 'cfg', 'points', 'worstrel', 'chkF', 'at0F', 'jumpMv', 'jF', 'origin', 'ratio', 'other', 'geomN', 'geoF', 'keyF', 'say', 'sayF'))
for g, a in agg.items():
    print('%-10s %4d %7d %9.1e %6d %4d %8d %5d %6d %6d %6d %7d %5d %4d %8d %5d' % (g, a['cfg'], a['pts'], a['rel'], a['cf'], a['at0'], a['jm'], a['jf'], a['jo'], a['jr'], a['jx'], a['gn'], a['gf'], a['kf'], a['sn'], a['sf']))
