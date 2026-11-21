"""Round 28, dial checker (ui): "Frame it" in windows the builder did not look at, and two near-touching cases.

  python -B out/r28/fix/ui/mk/sizes.py      -> out/r28/fix/ui/logs/sizes.txt, pictures out/r28/fix/ui/shots/sizes-*.png

For each window (1920x1080, 1024x768, 820x1180 upright, 360x640 small phone, 900x420 low and wide) and each size
(55.56, 150, 400, 2000): the size is typed (real keys), Frame it is pressed (real click), and the picture is asked at
29 x 21 points whether the object is there (the lab's own pick). Whole chain in the picture = no hit on the rim of
the picture, and the Drawing radius holds the chain. The same in the 2D view with the twin at 240 x 240 points.
Then, in the 1400x950 window: second sphere 33.33 typed with size 300 (300 x 0.3333 = 99.99: touching "within
rounding"), and on the frozen page size 99 in the 2D view (to see what Version 20 says when a chain is not whole).
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hand import Hand, ROOT, UI

LOG = os.path.join(UI, 'logs', 'sizes.txt'); SHOTS = 'out/r28/fix/ui/shots'
lines, wrong = [], []
PROBE = """const w = $('stage').clientWidth, hh = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 29; i++) for (let j = 0; j < 21; j++) { const hit = !!L.pick(w * (i + 0.5) / 29, hh * (j + 0.5) / 21); if (hit) { n++; if (i === 0 || j === 0 || i === 28 || j === 20) ring++; } }
  return { hits: n, rim: ring, reach: L.ballsReach(), bound: S.view.bound, dist: L.cam.dist, stage: [w, hh], warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', size: $('ballsSizeNum').value, rho: $('ballsRhoNum').value };"""
FLAT = """const N = 240, side = S.v2.h, asp = $('stage').clientWidth / $('stage').clientHeight; let rim = 0, inside = 0;
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) { const x = S.v2.x + side * asp * ((i + 0.5) / N - 0.5), y = S.v2.y + side * ((j + 0.5) / N - 0.5); if (L.ballsInside(x, y, +S.cut || 0)) { inside++; if (i === 0 || j === 0 || i === N - 1 || j === N - 1) rim++; } }
  return { inside, rim, h: side, reach: L.ballsReach(), halfw: side * asp / 2, halfh: side / 2, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '' };"""


def say(t):
    lines.append(t); print(t)
    open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def to_balls(h):
    h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
    return h.js("return S.mode === 'k' && S.k.group === 1;")


def main():
    say('started %s' % time.strftime('%H:%M:%S'))
    for size in ('1920x1080', '1024x768', '820x1180', '360x640', '900x420'):
        with Hand(os.environ.get('FIX_PAGE', 'dist/r28-fix.html'), size, 'dark') as h:
            if not to_balls(h):
                say('window %s: THE ROW DID NOT SHOW BALLS ON BALLS' % size); wrong.append('row in ' + size); continue
            for p in ('55.56', '150', '400', '2000'):
                h.click('#ballsReset button'); h.done()
                h.type('#ballsSizeNum', p); h.done()
                h.click('#ballsFrame'); h.done(); a = h.js(PROBE)
                h.shot('%s/sizes-%s-size-%s-3d.png' % (SHOTS, size, p), '#stage')
                ok = a['rim'] == 0 and a['hits'] > 0 and a['bound'] >= a['reach'] and abs(float(a['size']) - float(p)) < 0.006
                h.click('#flat'); h.done(); h.click('#ballsFrame'); h.done(); c = h.js(FLAT)
                h.shot('%s/sizes-%s-size-%s-2d.png' % (SHOTS, size, p), '#stage')
                h.click('#flat'); h.done()
                # how much of the picture the object takes: the chain's length against the width of the picture
                ok2 = c['rim'] == 0 and c['inside'] > 0 and c['halfw'] >= c['reach']
                say('window %s (picture %d x %d), size %s (second sphere %s): 3D %d of 609 probes hit, %d on the rim, reach %.2f, Drawing radius %.2f, camera distance %.2f -> %s | 2D view %.2f high, half width %.2f: %d of 57600 points inside, %d on the rim -> %s' % (
                    size, a['stage'][0], a['stage'][1], p, a['rho'], a['hits'], a['rim'], a['reach'], a['bound'], a['dist'], 'OK' if ok else 'WRONG', c['h'], c['halfw'], c['inside'], c['rim'], 'OK' if ok2 else 'WRONG'))
                if not ok: wrong.append('3D, window %s, size %s' % (size, p))
                if not ok2: wrong.append('2D, window %s, size %s' % (size, p))
                if a['hits'] < 25:
                    say('   NOTE: the object takes only %d of 609 probes: small in the picture' % a['hits'])
            probs = h.problems()
            if probs:
                say('   console in window %s: %s' % (size, ' || '.join(p[:300] for p in probs[:6]))); wrong.append('console in ' + size)
    with Hand(os.environ.get('FIX_PAGE', 'dist/r28-fix.html'), '1400x950', 'dark') as h:
        to_balls(h)
        say('--- touching "within rounding": second sphere 33.33 typed, then size 300 (300 x 0.3333 = 99.99)')
        h.type('#ballsRhoNum', '33.33'); h.done(); h.type('#ballsSizeNum', '300'); h.done()
        a = h.js(PROBE); say('typed, no Frame it: size %s, second sphere %s; reach %.1f, Drawing radius %.2f; sentence "%s"' % (a['size'], a['rho'], a['reach'], a['bound'], a['warn']))
        h.click('#ballsFrame'); h.done(); a = h.js(PROBE)
        h.shot('%s/sizes-near-touch-rho33.33-size300-3d.png' % SHOTS, '#stage')
        say('Frame it: %d probes hit, %d on the rim; reach %.1f, Drawing radius %.2f; sentence "%s"' % (a['hits'], a['rim'], a['reach'], a['bound'], a['warn']))
        h.click('#flat'); h.done(); h.click('#ballsFrame'); h.done(); c = h.js(FLAT)
        h.shot('%s/sizes-near-touch-rho33.33-size300-2d.png' % SHOTS, '#stage')
        say('2D view, Frame it: view %.2f high, half width %.2f, reach %.1f; %d on the rim; sentence "%s"' % (c['h'], c['halfw'], c['reach'], c['rim'], c['warn']))
        h.click('#flat'); h.done()
        probs = h.problems(); say('console: %s' % ('no console errors or warnings' if not probs else ' || '.join(p[:300] for p in probs[:6])))
    with Hand('dist/r28-base.html', '1400x950', 'dark') as h:
        to_balls(h)
        say('--- the frozen page (Version 20), size 99: what it says when the chain is not whole')
        h.type('#ballsSizeNum', '99'); h.done(); h.click('#ballsFrame'); h.done()
        a = h.js("return { reach: L.ballsReach(), bound: S.view.bound, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', tip: $('ballsFrame').title };")
        say('3D, Frame it: reach %.2f, Drawing radius %.2f; sentence "%s"; tooltip of Frame it "%s"' % (a['reach'], a['bound'], a['warn'], a['tip']))
        h.click('#flat'); h.done(); h.click('#ballsFrame'); h.done(); c = h.js(FLAT)
        say('2D view, Frame it: view %.2f high, half width %.2f, reach %.2f; %d on the rim; sentence "%s"' % (c['h'], c['halfw'], c['reach'], c['rim'], c['warn']))
    say('=== %d thing(s) marked WRONG%s' % (len(wrong), ': ' + ' | '.join(wrong) if wrong else ''))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        say('THE SCRIPT STOPPED: ' + repr(e)); say(traceback.format_exc()); sys.exit(1)
