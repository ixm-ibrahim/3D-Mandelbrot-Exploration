"""Round 28, Track A, the final checker: sections 1.4 b and c (first half) once more, on dist/r28-final.html.

  python -B out/r28/final/mk/bc5.py [keys ...]    -> out/r28/final/truth/logs/bc_<key>.txt, bc_summary.txt

REUSED: the truth checker's bc_page.py (three voices at the same points; ballsEstimate against a list of balls made
by its tkit.py, which it tested against brute force and against round 25's tree.py). I read it and found it sound.
MINE: the settings. None of them is one the truth checker or the fixer ran, except A (the page as it opens).
The three with a smaller second sphere all stand where the fixer's new room (the side spindle) is at work: second
sphere at 50 on the square grid (the setting of defect E1) and on the honeycomb grid, and 45 with a line only.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'truth', 'mk'))
import bc_page as B

tp = B.tp
MINE = {
    'A': B.SETS['A'],
    'V': ('two equal spheres, neighbours 80, honeycomb', 1.0, tp(80.0), 'hex', 16),
    'W': ('neighbours 150, second sphere 50 (the setting of defect E1), square', 0.5, tp(150.0), 'square', 16),
    'X': ('neighbours 120, second sphere 50, honeycomb, depth 24', 0.5, tp(120.0), 'hex', 24),
    'Y': ('neighbours 210, second sphere 45, a line only', 0.45, tp(210.0), 'line', 16),
    'Z': ('neighbours 480, second sphere 20 (all but touching), square, depth 30', 0.2, tp(480.0), 'square', 30),
}
B.SETS.clear(); B.SETS.update(MINE)

if __name__ == '__main__':
    import json
    keys = sys.argv[1:] or list(MINE)
    for k in keys:
        try:
            B.one(k)
        except Exception as err:
            import traceback
            print('SETTING %s STOPPED: %s' % (k, err)); traceback.print_exc()
    rows = []
    for k in MINE:
        fn = os.path.join(B.R.LOGS, 'bc_%s.json' % k)
        if os.path.exists(fn):
            rows.append(json.load(open(fn, encoding='utf-8')))
    s = ['Round 28, final check, 1.4 b and c (first half): %d settings run on %s. Details: truth/logs/bc_<key>.txt' % (len(rows), B.R.PAGE), '']
    for r in rows:
        w = MINE[r['key']]
        s.append('%s  %-70s | console %s | twin against the plain recipe: %d of %d differ (twin with nothing passed the same: %s) | shader against the plain recipe: flat %d of %d, in space %d of %d | shader number > true beyond single precision: %d of %d | ballsEstimate > true: %s'
                 % (r['key'], w[0], 'clean' if r['clean'] else 'ERRORS', r['twin_diff'], r['twin_n'], r['same'], r['sh_flat'][1], r['sh_flat'][0], r['sh_space'][1], r['sh_space'][0], r['sh_over'], r['sh_n'],
                    ', '.join('%s %d of %d' % (n, v['over'], v['n']) for n, v in r['est'].items())))
    open(os.path.join(B.R.LOGS, 'bc_summary.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(s) + '\n')
    print('\n'.join(s))
