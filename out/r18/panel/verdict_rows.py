"""Working aid: one short line per (rule, set): the verdict with the number of the first failing test.
python out/r18/panel/verdict_rows.py [rules]   -> prints json"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import panel as P


def why(k, r):
    d = r['d3']; fl = r['flat']; ratio = r['thickest'] / max(fl['thickest'], 1e-9)
    yv = (P.YARD().get('rabbit' if r['group'] == 'C' else r['tag']) or {}).get('volume')
    if k == 'cut':
        return 'exact cut, %d points differ' % r['cut']['differ']
    if k == 'piece':
        if r['volume'] <= 0:
            return 'one piece, the solid is empty (0 of 17 million points inside)'
        if 'tree' in r:
            return 'one piece, biggest piece down to %.1f %% (flat tree 100)' % min(q['gap_pct'] for q in r['tree'])
        return 'one piece, biggest piece %.2f %% gap allowed, %.1f %% strict, %d pieces' % (r['piece']['gap_pct'], r['piece']['strict_pct'], r['piece']['pieces'])
    if k == 'bodies':
        if 'tree' in r:
            return 'tree stays a tree, doubling factor %.1f (thread 2, sheet 4; allowed 3), thickest at 12 steps %.3f against flat %.3f' % (r['doubling']['factor'], r['tree'][-1]['thickest'], r['tree'][-1]['flat_thickest'])
        if ratio < P.T_THIN:
            return 'bodies, thickest place only %.2f x the flat set\'s (no solid body)' % ratio
        m = r.get('meet')
        if m and m['ball_that_parts'] is None and yv:
            return 'bodies meet at points, no ball up to 0.32 parts them, volume %.2f x the yardstick\'s' % (r['volume'] / yv)
        return 'bodies (lump), volume %.2f x the yardstick\'s' % (r['volume'] / yv) if yv else 'bodies'
    if k == 'd3':
        if 'tree' in r:
            return 'truly 3D, %.0f %% of the tree off the flat plane, a turn changes %.1f %%' % (d['share_off_plane_pct'] or 0, d['turn_pct'])
        if r['tag'] == 'airplane':
            return 'truly 3D, %d rings, %d spikes off the flat plane (2 needed)' % (d['rings'], d['off_plane'])
        if 'pits' in r:
            return 'truly 3D, %d dimples off the flat plane (2 needed), %d grooves round the axis, a turn changes %.1f %%' % (r['pits']['off_plane'], r['pits']['rings'], d['turn_pct'])
        return 'truly 3D, %d rings, %d round pieces off the plane (2 needed), roundness off the plane %s, a turn changes %.1f %%' % (
            d['rings'], d['round_off_plane'], 'none' if d.get('roundness_off') is None else '%.2f' % d['roundness_off'], d['turn_pct'])
    if k == 'clean':
        hs = sorted([x for q in r['close'] for x in q['hair'] if x is not None], reverse=True)
        rb = P.load_ribs(r['rule']).get(r['tag']) if r['tag'] == 'basilica' else None
        return 'clean close up, worst tile %.2f (line 0.3)' % hs[0] + (', ribs %.2f (line 0.45)' % rb['ripple_pct'] if rb else '')
    if k == 'mirror':
        return 'mirror, %.2f %% changes' % max(r['mirror']['z_pct'], r['mirror']['y_pct'])


if __name__ == '__main__':
    rows = []
    for n in sys.argv[1:] or P.saved_rules():
        R_ = P.load(n)
        for t in P.TAGS:
            if t not in R_['sets']:
                rows.append(dict(rule=n, set=t, verdict='not run (build stopped first)')); continue
            r = R_['sets'][t]; v = P.verdicts(r); bad = [k for k in P.ORDER if v[k][0] is False]
            if not bad:
                hs = sorted([x for q in (r.get('close') or []) for x in q['hair'] if x is not None], reverse=True)
                rows.append(dict(rule=n, set=t, verdict='pass' + (' (worst close-cut tile %.2f, line 0.3)' % hs[0] if hs else '')))
            else:
                rows.append(dict(rule=n, set=t, verdict='fail: ' + why(bad[0], r) + ('; also fails: ' + ', '.join(P.TITLE[k] for k in bad[1:]) if len(bad) > 1 else '')))
    print(json.dumps(rows, indent=0))
