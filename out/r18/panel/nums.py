"""Working aid: the raw numbers of every saved rule, one line per (set, rule). python out/r18/panel/nums.py [rules]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import panel as P


def f(x, fmt='%.2f'):
    return '-' if x is None else fmt % x


if __name__ == '__main__':
    names = sys.argv[1:] or P.saved_rules()
    for t in P.TAGS:
        print('---- ' + t)
        for n in names:
            r = P.load(n)
            if not r or t not in r['sets']:
                continue
            s = r['sets'][t]; s_ = s; d = s['d3']; pc = s['piece']; m = s.get('meet') or {}
            cl = s.get('close') or []
            hs = sorted([x for q in cl for x in q['hair'] if x is not None], reverse=True) if cl and 'pos' in cl[0] else []
            line = '%-9s vol %6.3f thick x%.2f | gap %7.3f loose %6.3f pcs %4d | cut %s | turn %5.1f off: %3d pieces %2d rings %3d off %3d round-off, round %s | ' % (
                n, s['volume'], s['thickest'] / s['flat']['thickest'], pc['gap_pct'], pc['loose_pct'], pc['pieces'], (s.get('cut') or {}).get('differ', '-'),
                d['turn_pct'], d['pieces'], d['rings'], d['off_plane'], d['round_off_plane'], f(d['roundness']))
            if m:
                line += 'meet ball %s up %s (flat %s) fill %.0f/%.0f | ' % (m['ball_that_parts'], f(m.get('up_run'), '%.3f'), f(m.get('flat_run'), '%.3f'), m['ball_fill_pct'], m['flat_disc_fill_pct'])
            if 'neck' in s:
                line += 'neck %.3f%% | ' % s['neck']['cut_fill_pct']
            if 'tree' in s:
                line += 'tree thick %s flat %s gap %s flatgap %s shadow/flat %s offshare %s | ' % (
                    ','.join('%.3f' % q['thickest'] for q in s['tree']), ','.join('%.3f' % q['flat_thickest'] for q in s['tree']),
                    ','.join('%.1f' % q['gap_pct'] for q in s['tree']), ','.join('%.1f' % q['flat_gap_pct'] for q in s['tree']),
                    ','.join('%.1f' % (q['biggest_shadow'] / max(q['flat_area'], 1e-9)) for q in s['tree']), f(d.get('share_off_plane_pct'), '%.0f'))
            line += 'strict %.2f roundoff %s | ' % (pc['strict_pct'], f(d.get('roundness_off')))
            if 'pits' in s_:
                line += 'pits %s | ' % s_['pits']
            if 'doubling' in s_:
                line += 'doubling %.2f | ' % s_['doubling']['factor']
            if hs:
                line += 'hair ' + ' '.join('%.2f' % x for x in hs)
            mr = s['mirror']; line += ' | mirror z %.2f y %.2f' % (mr['z_pct'], mr['y_pct'])
            if 'turned_copy_differs_pct' in s:
                line += ' | turned copy differs %.1f' % s['turned_copy_differs_pct']
            print(line)
