"""Round 28, Track A, the final checker: the same rays on the page as it was BEFORE the fixer (dist/r28-dials.html,
the builder's page), for the views where my walk counts rays that pass a stretch only the depth of the search calls
solid. To tell what the fixer's new room changed from what was there already.

  python -B out/r28/final/mk/rays_before.py <view> [view ...]   -> eyes/shots/bw-<view>.png, eyes/rays/bw-<view>.json
  then:  python -B out/r28/final/eyes/mk/walk.py bw <view> ...
REUSED: the eyes checker's rays.py, unchanged; only the page is another.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'eyes', 'mk'))
import eyerun as run
import rays

if __name__ == '__main__':
    names = sys.argv[1:]
    page = 'dist/r28-dials.html'
    t0 = time.time()
    code, text, vals = run.shot(page, rays.steps_for(names, 'bw'), 'rays-bw-%s' % names[0], '1400x950', 'dark')
    run.write('rays-bw-%s.log' % names[0], text + 'exit %d, %.0f s\n' % (code, time.time() - t0))
    got = 0
    for v in vals:
        if v.startswith('{"meta"'):
            d = json.loads(v)
            with open(os.path.join(run.EYES, 'rays', 'bw-%s.json' % d['meta']['name']), 'w', encoding='utf-8') as f:
                f.write(v)
            m = d['meta']; got += 1
            print('%s on %s: t %.6f rho %.6f grid %d depth %d | %s | drawn in %d ms | picks %d, stops %d' % (m['name'], page, m['k']['bt'], m['k']['brho'], m['k']['bgrid'], m['k']['bit'], m['status'], m['drawMs'], m['picks'], m['stops']))
    print('exit %d, %s, %d of %d views back, %.0f s' % (code, 'no console errors' if run.clean(text) else 'SEE THE LOG', got, len(names), time.time() - t0))
