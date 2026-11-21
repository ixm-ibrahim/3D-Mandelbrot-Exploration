"""Round 28, Track A, builder: two things measured apart.

  python out/r28/dials/mk/extras.py   -> out/r28/dials/logs/extras.txt

1. The background warming: with the page as a user gets it (warming on), does the other program of Balls on balls
   get prepared while the default picture stands, so that the first step past 100 does not have to build it?
2. The deepest search the dial now allows (typed 1000), where the search is longest: the spheres touching
   (100 with two equal spheres; 200 with the second at 50). Does the picture finish, and how long does it take?
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run28 as run

CLOCK = """
const clock = async act => { await sleep(200); const built0 = L.R.compiles, t0 = performance.now(); await act();
  for (;;) { await new Promise(r => setTimeout(r, 5)); const now = performance.now() - t0;
    if (now > 250 && L.idle()) return { done: Math.round(now), built: L.R.compiles - built0, status: $('status').textContent };
    if (now > 110000) return { done: -1, built: L.R.compiles - built0, status: 'NOT FINISHED in 110 s: ' + $('status').textContent }; } };
"""
WARM = run.HEAD + CLOCK + """
$('ap-balls').click(); await settle();
const c0 = L.R.compiles; let waited = 0;
for (; waited < 20000 && L.R.compiles === c0; waited += 100) await sleep(100);
await sleep(1500);
const v = await clock(async () => { S.k.brho = 1 / 3; S.k.bt = 0.5 * (100 / 150 + 1); L.ballsFrame(); go(); });
return JSON.stringify({ warmOn: L.R.warmOn, waitedForAProgramToBeStarted: waited, startedMeanwhile: L.R.compiles - c0, sig: String(L.R.sig).replace(/\\n/g, '/'), first150: v });
"""
DEEP = run.HEAD + CLOCK + """
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
S.k.brho = %r; S.k.bt = %r; S.k.bgrid = 0; S.k.bit = %d; S.flat = %s; L.ballsFrame();
const v = await clock(async () => { go(); });
v.what = '%s'; v.depth = S.k.bit; v.warn = warn().slice(0, 60);
return JSON.stringify(v);
"""

if __name__ == '__main__':
    lines = []
    # 1. warming on: no UP step (that one switches the warming off)
    code, text, vals = run.shot(run.PAGE, [{'js': "return 'page as it comes';", 'wait': 'done', 'timeout': 900}, {'js': WARM, 'timeout': 300}], 'extras-warm', '1400x950', 'dark')
    run.write('extras-warm.log', text + 'exit %d\n' % code)
    try:
        d = json.loads(vals[-1])
        lines.append('1. warming on (the page as it comes): after the default picture of Balls on balls, programs started in the background within %.1f s: %d; then the size set to 150: programs that had to be built then %d, picture finished after %d ms (program %s); %s'
                     % (d['waitedForAProgramToBeStarted'] / 1000 + 1.5, d['startedMeanwhile'], d['first150']['built'], d['first150']['done'], d['sig'], 'no console errors' if run.clean(text) else 'CONSOLE ERRORS'))
    except Exception as e:
        lines.append('1. NO RESULT: %s' % text[-600:])
    # 2. the deepest search
    steps = [run.UP]
    for what, rho, t, depth, flat in (('two equal spheres at 100, depth 16', 1.0, 1.0, 16, 'false'), ('two equal spheres at 100, depth 200 (the old end of typed values)', 1.0, 1.0, 200, 'false'),
                                      ('two equal spheres at 100, depth 1000', 1.0, 1.0, 1000, 'false'), ('second sphere 50, size 200, depth 1000', 0.5, 0.75, 1000, 'false'),
                                      ('second sphere 50, size 200, depth 1000, 2D view', 0.5, 0.75, 1000, 'true'), ('size 150 (second sphere 33.33), depth 1000', 1 / 3.0, 0.5 * (100 / 150.0 + 1), 1000, 'false'),
                                      ('the default, depth 1000', 1.0, 1.4, 1000, 'false')):
        steps.append({'js': DEEP % (rho, t, depth, flat, what), 'timeout': 300})
    code, text, vals = run.shot(run.PAGE, steps, 'extras-deep', '1400x950', 'dark')
    run.write('extras-deep.log', text + 'exit %d\n' % code)
    for v in vals[1:]:
        try:
            d = json.loads(v)
            lines.append('2. %s: finished after %s ms; %s' % (d['what'], d['done'], d['status']))
        except Exception:
            lines.append('2. ' + str(v)[:300])
    lines.append('   ' + ('no console errors' if run.clean(text) else 'CONSOLE ERRORS: see logs/extras-deep.log'))
    out = '\n'.join(lines) + '\n'
    run.write('extras.txt', out); print(out)
