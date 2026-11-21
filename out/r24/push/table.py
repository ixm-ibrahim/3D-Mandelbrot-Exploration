"""Round 24, section "push": the push law against what happens.   python out/r24/push/table.py [rule,...]  -> table.md

Reads cache/law.json (predictions; made again here for rules that are missing) and cache/necks-<rule>-*.json (measured).
What happened, per bud:   apart   the widest ball that passes from body to body is at most 1.5 blocks, nothing stands above the meeting point
                          FUSED   that ball is at least half the ball that fits in the bodies themselves
                          thread  between the two: a thin bridge, or thin stuff straight above the meeting point
"""
import os, sys, json, glob
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import plib as P
import extra as E
CACHE = os.path.join(HERE, 'cache')


def measured(name):
    out = {}
    for fn in sorted(glob.glob(os.path.join(CACHE, 'necks-%s-*.json' % name.replace(':', '_')))):
        if fn.endswith('-test.json'):
            continue
        out.update(json.load(open(fn)))
    return out


def verdict(res):
    blk = res['block']; nk = [(a, b) for a, b in res['neck'] if a is not None and b]
    nmax = max(a for a, b in nk); rmax = max(a / b for a, b in nk)
    above = max(res['disc'][0], res['column'][0])
    if rmax >= 0.5:
        return 'FUSED', nmax, rmax, above
    if nmax <= 1.5 * blk and above < 0.05 and res['column'][1] < 0.1:
        return 'apart', nmax, rmax, above
    return 'thread', nmax, rmax, above


def predictions(name):
    if name.startswith('face:'):
        base = P.DIRS[name[5:]]; out = {}
        for key, cs in P.CASES.items():
            out[key] = P.law(P.turned(base, np.angle(cs['a'])), cs)
        return out
    return {key: P.law(P.DIRS[name], cs) for key, cs in P.CASES.items()}


def main(names):
    lines = []; tally = {'A': [0, 0], 'A95': [0, 0], 'A15': [0, 0]}; fails = []
    keys = P.BUDS + ['1/2root']
    lines.append('| rule | c | law A: push x d at lifts 8 / 15 / 25 | says | measured | neck / body | stands above |')
    lines.append('|---|---|---|---|---|---|---|')
    for nm in names:
        m = measured(nm); pr = predictions(nm)
        for key in keys:
            if key not in m or 'neck' not in m[key]:
                continue
            A = pr[key]['A']; v, nmax, rmax, above = verdict(m[key])
            says = 'apart' if min(A) > 1 else 'FUSED'; says95 = 'apart' if min(A) > 0.95 else 'FUSED'; says15 = 'apart' if A[1] > 0.95 else 'FUSED'
            if key != '1/2root':
                for tag, s in (('A', says), ('A95', says95), ('A15', says15)):
                    ok = (s == v) or (v == 'thread' and s == 'FUSED'); tally[tag][0] += ok; tally[tag][1] += 1
                if not ((says95 == v) or (v == 'thread' and says95 == 'FUSED')):
                    fails.append((nm, key, A, v))
            lines.append('| %s | %s | %.2f / %.2f / %.2f | %s | %s | %.3f / %.2f | %.2f |' % (nm, key, A[0], A[1], A[2], says, v, nmax, rmax, above))
    lines.append('')
    lines.append('Right calls on the buds (the joining point c = -0.75 left out; "thread" counted as fused): law A with the line at 1: %d of %d; with the line at 0.95: %d of %d; lift 15 alone with the line at 0.95: %d of %d.'
                 % (tally['A'][0], tally['A'][1], tally['A95'][0], tally['A95'][1], tally['A15'][0], tally['A15'][1]))
    lines.append('Wrong calls with the line at 0.95: ' + '; '.join('%s at %s (%.2f / %.2f / %.2f, measured %s)' % (a, b, c[0], c[1], c[2], d) for a, b, c, d in fails))
    lines.append('')
    lines.append('| rule | c | pull 2d | law A at 8 / 15 / 25 | height of the solid straight above the fixed point | total inside length of the column (to 0.9) |')
    lines.append('|---|---|---|---|---|---|')
    for nm in names:
        m = measured(nm); pr = predictions(nm)
        for key in ('in120', 'in180', 'siegel', 'airplane'):
            if key in m:
                A = pr[key]['A']; lines.append('| %s | %s | %.3f | %.2f / %.2f / %.2f | %.3f | %.3f |' % (nm, key, 2 * P.CASES[key]['d'], A[0], A[1], A[2], m[key]['column'][0], m[key]['column'][1]))
    return lines


if __name__ == '__main__':
    names = sys.argv[1].split(',') if len(sys.argv) > 1 else P.MAIN + ['m4b']
    out = sys.argv[2] if len(sys.argv) > 2 else 'table.md'
    L = main(names); open(os.path.join(HERE, out), 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('\n'.join(L))
