def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (s.count(a), a[:70])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

sub('src/js/65-learn-steps.js', [
 ("""    const w = [v[0], (1 - 2 * t) * v[1], v[2]], lw = len(w);
    return lw > 0 ? scl(w, Math.pow(L, 1 - 2 * t) / lw) : scl(v, (t < 0.5 ? 1 : -1) * Math.pow(L, -2 * t));   // on the y-axis the mirror is a jump at half way
""", """    return scl([v[0], (1 - 2 * t) * v[1], v[2]], Math.pow(L, -2 * t));   // y straight through 0, while everything is scaled by L^(-2t)
"""),
 (" A point exactly on the y-axis makes that last move with a jump half way.` : '');", " In that move y goes straight through 0 to its mirror value, so a point on the y-axis passes through the origin.` : '');"),
])
s = open('out/r13/steps/summ.py', encoding='utf-8').read()
s = s.replace("    a['jm'] += int(m.group(5)); a['jf'] += int(m.group(6)); a['sn'] += int(m.group(8)); a['sf'] += int(m.group(9))",
"""    a['jm'] += int(m.group(5)); a['jf'] += int(m.group(6)); a['sn'] += int(m.group(8)); a['sf'] += int(m.group(9))
    k = re.search(r'jump: origin (\d+), ratio (\d+), other (\d+) \| geom (\d+) fail (\d+) \| key (\d+)', rest)
    for i, nm in enumerate(['jo', 'jr', 'jx', 'gn', 'gf', 'kf']): a[nm] = a.get(nm, 0) + int(k.group(i + 1))""")
s = s.replace("print('%-10s %4s %7s %9s %6s %4s %8s %5s %8s %5s' % ('group', 'cfg', 'points', 'worstrel', 'chkF', 'at0', 'jumpMv', 'jF', 'say', 'sayF'))",
 "print('%-10s %4s %7s %9s %6s %4s %8s %5s %6s %6s %6s %7s %5s %4s %8s %5s' % ('group', 'cfg', 'points', 'worstrel', 'chkF', 'at0F', 'jumpMv', 'jF', 'origin', 'ratio', 'other', 'geomN', 'geoF', 'keyF', 'say', 'sayF'))")
s = s.replace("    print('%-10s %4d %7d %9.1e %6d %4d %8d %5d %8d %5d' % (g, a['cfg'], a['pts'], a['rel'], a['cf'], a['at0'], a['jm'], a['jf'], a['sn'], a['sf']))",
 "    print('%-10s %4d %7d %9.1e %6d %4d %8d %5d %6d %6d %6d %7d %5d %4d %8d %5d' % (g, a['cfg'], a['pts'], a['rel'], a['cf'], a['at0'], a['jm'], a['jf'], a['jo'], a['jr'], a['jx'], a['gn'], a['gf'], a['kf'], a['sn'], a['sf']))")
open('out/r13/steps/summ.py', 'w', encoding='utf-8', newline='\n').write(s)
