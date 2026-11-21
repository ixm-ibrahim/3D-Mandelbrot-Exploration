"""Round 22, entrycheck second pass: five entries that carry nothing (mercator, lathe, turnalong, windsq, bulb) on the
repaired page against base17a (dist/r22-entrycheck2-base.html, built by me from base17a with nothing swapped in).
  pictures: four scenes of my own per entry, the stage as the page shows it, compared pixel for pixel
  words:    the card (Julia and Mandelbrot view) and the Learn tab (orbit after three "Next step", notes, sentences)
  python out/r22/entrycheck2/e2_untouched.py new|base     -> untouched-<which>.log / .json, untouched/<which>-*.png
  python out/r22/entrycheck2/e2_untouched.py compare      -> untouched.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drv

IDS = ['mercator', 'lathe', 'turnalong', 'windsq', 'bulb']
SCENES = [
    ('siegel', "S.mode = 'j'; S.c = [-0.390541, -0.586788, 0]; S.iter = 24; S.n = 2; L.resetCam(); L.cam.yaw = 1.1; L.cam.pitch = 0.35;"),
    ('mandel-cut', "S.mode = 'm'; S.iter = 18; S.n = 2; S.cutOn = true; L.resetCam();"),
    ('flat-offc', "S.mode = 'j'; S.c = [-0.75, 0.1, 0.2]; S.iter = 30; S.n = 2; S.flat = true; L.resetCam();"),
    ('absx', "S.mode = 'j'; S.c = [-1, 0, 0]; S.iter = 20; S.n = 2; S.abs = [1, 0, 0]; L.resetCam(); L.cam.yaw = -0.6; L.cam.pitch = 0.5;"),
]
H = drv.HEAD + """
const cardDone = async () => { await sleep(350); for (let i = 0; i < 800 && !L.cardIdle(); i++) await sleep(25); await sleep(150); };
const W = window.__w || (window.__w = { card: {}, learn: {}, ms: {} });
"""


def steps(which):
    st = [drv.UP]
    for id_ in IDS:
        for tag, js in SCENES:
            st.append(dict(js=H + """
$('mode-j').click(); await sleep(120); $('ap-%s').click(); await sleep(200); if (apId() !== '%s') fail('could not choose %s');
S.eq = 'z^n + c'; S.z0 = '0'; S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0];
%s
const t0 = performance.now(); go(); await settle(); W.ms['%s %s'] = Math.round(performance.now() - t0);
return '%s %s: ' + (S.flat ? 'flat' : grid()[0] + ' probes') + ', ' + W.ms['%s %s'] + ' ms';""" % (id_, id_, id_, js, id_, tag, id_, tag, id_, tag),
                           wait='done', timeout=300, shot='out/r22/entrycheck2/untouched/%s-%s-%s.png' % (which, id_, tag), clip='#stage'))
        # the words: the card in both views, the Learn tab
        st.append(dict(js=H + """
$('mode-j').click(); await sleep(120); $('ap-%(id)s').click(); await sleep(200);
S.eq = 'z^n + c'; S.z0 = '0'; S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; S.n = 2; S.c = [-0.4, 0.3, 0.2]; S.iter = 20; L.resetCam(); go(); await settle(); await cardDone();
const cj = txt('card'), fj = $('f-%(id)s') ? $('f-%(id)s').textContent : '';
S.c = [-1, 0, 0]; L.touch(); await settle(); await cardDone(); const cj2 = txt('card');
$('mode-m').click(); await sleep(250); await settle(); await cardDone(); const cm = txt('card');
S.n = 3; go(); await settle(); await cardDone(); const c3 = txt('card'); S.n = 2;
$('mode-j').click(); await sleep(200); go(); await settle(); await cardDone();
W.card['%(id)s'] = { julia: cj, juliaOtherC: cj2, mandel: cm, power3: c3, formula: fj, cacheKeys: [...L.cardRun.cache.keys()].filter(k => k.startsWith('%(id)s ')) };
$('mode-l').click(); await sleep(400); $('learnSpace3').click(); await sleep(250);
L.learn.set({ z: [0.5, -0.4, 0.3], c: [-0.8, 0.1, 0.2] });
const say0 = L.learn.cache.say.slice(), names = L.learn.cache.names.slice();
for (let k = 0; k < 3; k++) { $('learnNext').click(); await sleep(110); }
const s = L.learn.state();
W.learn['%(id)s'] = { names, say0, say3: L.learn.cache.say.slice(), orbit: s.orbit, end: s.end, note: s.note };
$('learnAgain').click(); await sleep(150); $('mode-j').click(); await sleep(300); await settle();
return '%(id)s words taken';""" % dict(id=id_), timeout=300))
    st.append({'js': "return JSON.stringify(window.__w);"})
    return st


if __name__ == '__main__':
    which = sys.argv[1]
    if which in ('new', 'base'):
        os.makedirs(os.path.join(HERE, 'untouched'), exist_ok=True)
        code, text, vals = drv.shot(drv.PAGE if which == 'new' else drv.BASE, steps(which), 'untouched-%s-steps' % which, '1400x950')
        drv.write('untouched-%s.log' % which, text + 'exit %d\n' % code)
        if vals:
            v = vals[-1]; drv.write('untouched-%s.json' % which, v if isinstance(v, str) else json.dumps(v))
        print(text[-2500:]); print('exit', code); sys.exit(code)
    import numpy as np
    from PIL import Image
    rep = []
    def say(t):
        rep.append(t); print(t)
    say('Pictures: the stage as the page shows it, repaired page against base17a, pixel for pixel.')
    tot = 0; bad = 0
    for id_ in IDS:
        for tag, _ in SCENES:
            a = np.asarray(Image.open(os.path.join(HERE, 'untouched', 'new-%s-%s.png' % (id_, tag))).convert('RGB')).astype(int)
            b = np.asarray(Image.open(os.path.join(HERE, 'untouched', 'base-%s-%s.png' % (id_, tag))).convert('RGB')).astype(int)
            if a.shape != b.shape:
                say('   %-10s %-10s: SIZES DIFFER %s %s' % (id_, tag, a.shape, b.shape)); bad += 1; continue
            d = np.abs(a - b).max(-1); tot += d.size; bad += int((d > 0).sum())
            lit = int((a.max(-1) > 40).sum())
            say('   %-10s %-10s: %d x %d, pixels that differ %d (largest difference %d of 255); pixels brighter than 40: %d' % (id_, tag, a.shape[1], a.shape[0], (d > 0).sum(), d.max(), lit))
    say('   in all: %d of %d pixels differ' % (bad, tot))
    n = json.load(open(os.path.join(HERE, 'untouched-new.json'), encoding='utf-8')); b = json.load(open(os.path.join(HERE, 'untouched-base.json'), encoding='utf-8'))
    say('')
    say('Words: the card (Julia c = (-0.4, 0.3, 0.2), then c = -1 by touch only, Mandelbrot view, power 3) and the formula line.')
    for id_ in IDS:
        cn, cb = n['card'][id_], b['card'][id_]
        say('   %-10s: ' % id_ + ', '.join('%s %s' % (k, 'same' if cn[k] == cb[k] else 'DIFFERENT') for k in ('julia', 'juliaOtherC', 'mandel', 'power3', 'formula', 'cacheKeys'))
            + '; card unchanged when only c moved: new %s, base %s' % (cn['julia'] == cn['juliaOtherC'], cb['julia'] == cb['juliaOtherC']))
    say('')
    say('Words: the Learn tab, start (0.5, -0.4, 0.3), c = (-0.8, 0.1, 0.2), three times "Next step".')
    for id_ in IDS:
        ln, lb = n['learn'][id_], b['learn'][id_]
        far = max(max(abs(x - y) for x, y in zip(p, q)) for p, q in zip(ln['orbit'], lb['orbit'])) if len(ln['orbit']) == len(lb['orbit']) else float('nan')
        ds = [(x, y) for x, y in zip(ln['say0'] + ln['say3'], lb['say0'] + lb['say3']) if x != y]
        say('   %-10s: orbit points %d / %d, largest difference %.1e; names %s; note %s; sentences that differ: %d of %d' % (id_, len(ln['orbit']), len(lb['orbit']), far, 'same' if ln['names'] == lb['names'] else 'DIFFERENT', 'same' if ln['note'] == lb['note'] else 'DIFFERENT', len(ds), len(ln['say0']) + len(ln['say3'])))
        for x, y in ds:
            say('        new : ' + x); say('        base: ' + y)
    say('')
    say('Time to draw (ms, one run each, new / base): ' + '; '.join('%s %d / %d' % (k, n['ms'][k], b['ms'].get(k, -1)) for k in n['ms']))
    say('   sum: new %d ms, base %d ms' % (sum(n['ms'].values()), sum(b['ms'].values())))
    open(os.path.join(HERE, 'untouched.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')
