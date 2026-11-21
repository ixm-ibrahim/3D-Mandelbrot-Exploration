"""Round 22, entry: the page's smoke list (tools/smoke-v14.json, 62 steps), the 5 steps round 20 added for "Wind, then
square" (out/r20/entry/smoke.py; one line of them changed, see below), and steps for the two new entries, on
dist/r22-entry.html at 1400x950. Pictures go to out/r22/entry/smoke/.
  python out/r22/entry/smoke.py [part]   part: all (default) | base (the 67 old steps) | new (the new steps only)
-> smoke-<part>.log
The one changed line: round 20's step said "windsq stands at the END of the list". It now stands before the two new
entries, so the test asks that it stands right after turnalong, which is what it meant."""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

spec = importlib.util.spec_from_file_location('smoke20', os.path.join(run.ROOT, 'out', 'r20', 'entry', 'smoke.py'))
S20 = importlib.util.module_from_spec(spec); spec.loader.exec_module(S20)
OLD_LINE = "if (L.APPROACHES.indexOf(a) !== L.APPROACHES.length - 1 || L.APPROACHES[L.APPROACHES.length - 2].id !== 'turnalong') fail('the entry should stand at the end of the list, after turnalong');"
NEW_LINE = "if (L.APPROACHES[L.APPROACHES.indexOf(a) - 1].id !== 'turnalong') fail('the entry should stand right after turnalong');"

HEAD = run.HEAD + """
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
// what the picture is: the 165 probes and where they hit (the same state must give the same answer)
const sig = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = '', sum = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) { const p = L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11); s += p ? '1' : '0'; if (p) sum += p[0] + 2 * p[1] + 3 * p[2]; } return s + ' ' + sum.toFixed(3); };
const hits = s => (s.split(' ')[0].match(/1/g) || []).length;
"""
WORDS = {
    'alongonce': ['The first squaring of every orbit is done by Turning plane, along', 'two bodies of the rabbit float free', 'a count of its squarings and nothing else',
                  'show the first squaring of an orbit only', 'First squaring of an orbit: v² = Rot(ψ)', 'Where it falls short'],
    'pulledplane': ['Each orbit carries a plane through the x-axis', 'three numbers in the rule were set by hand', 'thin loose flakes hover over the skin',
                    'show the first squaring of an orbit only', 'v² = Rot(θ)·P(Rot(−θ)·v)', 'Where it falls short', 'the pages of a book whose spine is the x-axis'],
}
NAMES = {'alongonce': 'Along once, then one plane', 'pulledplane': 'Pulled plane'}


def steps_for(id_):
    P = 'out/r22/entry/smoke/r22-%s-' % id_
    st = [
        # 1. choose the entry in Julia mode from the menu's own radio; c = -1 at 40 iterations
        dict(js=HEAD + """
$('mode-j').click(); await sleep(150);
if (S.mode !== 'j') fail('not in Julia mode');
const r = $('ap-%(id)s'); if (!r) fail('the list has no entry %(id)s');
r.click(); await sleep(250);
if (apId() !== '%(id)s') fail('choosing the entry did not take: ' + apId());
const a = L.APPROACHES[S.approach], ids = L.APPROACHES.map(x => x.id);
if (a.name !== '%(name)s' || a.group !== 'inversions') fail('name or group wrong: ' + a.name + ', ' + a.group);
if (ids.slice(-3).join(' ') !== 'windsq alongonce pulledplane') fail('the two entries should stand at the end of the list, after windsq: ' + ids.slice(-3));
if (a.deMax !== 0) fail('the entry should cap the distance estimate at Rough');
const dials = (a.params || []).filter(p => p.type === 'dial').map(p => p.key).join(' ');
if (dials !== '%(dials)s') fail('dials: ' + dials);
S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 40; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; S.mosaic = false; L.resetCam(); go(); await sleep(200);
return '%(id)s chosen in Julia mode; menu reads ' + $('apMenuName').textContent;
""" % dict(id=id_, name=NAMES[id_], dials='hold ease cpull' if id_ == 'pulledplane' else ''), wait='done', timeout=600, shot=P + '1-basilica.png'),
        # 2. the picture is whole; the words are on the page; the cap at Rough holds; the same state draws the same picture
        dict(js=HEAD + """
if (apId() !== '%(id)s' || S.mode !== 'j') fail('lost the entry or the mode');
if ($('apMenuName').textContent !== '%(name)s') fail('the menu should name the entry, it reads ' + $('apMenuName').textContent);
const g = grid();
if (g[0] < 8) fail('the picture of c = -1 is empty: ' + g[0] + ' of 165 probes hit');
if (g[1] > 4) fail('c = -1 is not whole in the frame: ' + g[1] + ' probes on the outer ring');
const btn = $('apAboutBtn'), box = $('apAbout'), wasHidden = box.hidden;
if (wasHidden) { btn.click(); await sleep(150); }
if (box.hidden) fail('"About this approach" did not open the explanation');
const all = box.textContent + ' ' + document.body.innerText;
for (const t of %(words)s) if (!all.includes(t)) fail('missing on the page: ' + t);
if (/undefined|NaN|TEXT PENDING/.test(box.textContent)) fail('the explanation shows a stray mark');
if (wasHidden) { btn.click(); await sleep(150); }
for (const t of ['TEXT PENDING', 'undefined', 'NaN']) if ($('secApproach').innerText.includes(t)) fail('the Approach section shows ' + t);
if ($('card') && /undefined|NaN/.test($('card').innerText)) fail('the card shows a stray mark');
const s0 = sig(), was = S.q.de;
S.q.de = 0; go(); await settle(); const p0 = sig();
S.q.de = 3; go(); await settle(); const p3 = sig();
S.q.de = was; go(); await settle(); const s1 = sig();
if (p0 !== p3) fail('the picture changed with the Distance estimate setting: the cap at Rough does not hold');
if (s0 !== s1) fail('the same settings gave another picture the second time');
return 'c = -1 drawn (' + g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring); words on the page; same probes at Rough and at Exact, and twice over';
""" % dict(id=id_, name=NAMES[id_], words=json.dumps(WORDS[id_], ensure_ascii=False)), wait='done', timeout=600),
        # 3. the Mandelbrot view
        dict(js=HEAD + """
$('mode-m').click(); await sleep(200);
if (S.mode !== 'm' || apId() !== '%(id)s') fail('the Mandelbrot view did not come on');
S.iter = 30; L.resetCam(); go(); await settle();
const g = grid(); if (g[0] < 5) fail('the Mandelbrot solid is empty: ' + g[0] + ' probes hit');
return 'Mandelbrot solid: ' + g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring';
""" % dict(id=id_), wait='done', timeout=600, shot=P + '2-mandelbrot.png'),
        # 4. the flat cut of the Mandelbrot view, then of the Julia view
        dict(js=HEAD + """
$('flat').click(); await sleep(200);
if (!S.flat) fail('the 2D view did not come on');
const w = $('stage').clientWidth, h = $('stage').clientHeight; await settle();
const p = L.pick(w / 2, h / 2);
if (!p || Math.abs(p[2]) > 1e-9) fail('the 2D view is not the cut at z = 0');
return 'the 2D view of the Mandelbrot solid shows the cut at z = ' + p[2];
""", wait='done', timeout=600, shot=P + '3-mandelbrot-flat.png'),
        dict(js=HEAD + """
$('mode-j').click(); await sleep(200); S.c = [-0.122561, 0.744862, 0]; S.iter = 40; go(); await settle();
if (!S.flat || S.mode !== 'j') fail('the 2D view of the Julia set did not come on');
return 'the 2D view of the rabbit';
""", wait='done', timeout=600, shot=P + '4-rabbit-flat.png'),
        # 5. power 3; two powers in one step; a negative power from 0 and from c; the modifiers; the mosaic; inside-out
        dict(js=HEAD + """
$('flat').click(); await sleep(200);
if (S.flat) fail('the 3D view did not come back');
const out = [];
const tryIt = async (what, f, least) => {
  f(); L.resetCam(); go(); await settle();
  const g = grid(); if (g[0] < least) fail(what + ': the picture is empty (' + g[0] + ' probes hit)');
  const a = L.APPROACHES[S.approach], t = a.formula(S.param[a.id], S.n) + a.crush(S.param[a.id], S.n)[1] + a.smooth(S.param[a.id], S.n)[1] + a.slice(true, S.param[a.id], S.n) + a.roundNote(S.param[a.id], S.n);
  if (/undefined|NaN/.test(t)) fail(what + ': bad text');
  out.push(what + ': ' + g[0] + ' probes hit');
};
await tryIt('power 3, Julia c = 0.3', () => { S.mode = 'j'; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 3; S.c = [0.3, 0, 0]; S.iter = 30; }, 5);
await tryIt('power 3, Mandelbrot', () => { S.mode = 'm'; }, 5);
await tryIt('power 2.5, Julia c = 0.3', () => { S.mode = 'j'; S.n = 2.5; }, 0);
await tryIt('z^2 + z^3 + c, Julia c = -0.2', () => { S.eq = 'z^2 + z^3 + c'; S.n = 2; S.c = [-0.2, 0, 0]; }, 3);
await tryIt('z^2 + z^3 + c, Mandelbrot', () => { S.mode = 'm'; }, 3);
await tryIt('z^-n + c from 0, n = 2, Mandelbrot', () => { S.eq = 'z^-n + c'; S.z0 = '0'; S.n = 2; }, 0);
await tryIt('z^-n + c from c, n = 2, Mandelbrot', () => { S.z0 = 'c'; }, 0);
await tryIt('z^-n + c, Julia c = -1', () => { S.mode = 'j'; S.z0 = '0'; S.c = [-1, 0, 0]; }, 0);
await tryIt('|x| |y| |z| ticked, Julia c = -1', () => { S.eq = 'z^n + c'; S.n = 2; S.abs = [1, 1, 1]; }, 3);
await tryIt('flip y, flip z, Julia c = -1', () => { S.abs = [0, 0, 0]; S.flip = [1, 1]; }, 3);
await tryIt('mosaic', () => { S.flip = [0, 0]; S.mode = 'm'; S.mosaic = true; }, 1);
await tryIt('cut at z = 0, Julia rabbit', () => { S.mosaic = false; S.mode = 'j'; S.c = [-0.122561, 0.744862, 0]; S.cutOn = true; S.cut = 0; S.iter = 40; }, 5);
S.cutOn = false; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.c = [-1, 0, 0]; L.resetCam(); go(); await settle();
return out.join('; ');
""", wait='done', timeout=1500, shot=P + '5-after-variants.png'),
    ]
    if id_ == 'pulledplane':
        st.append(dict(js=HEAD + """
// the three sliders: they are on the page, each changes the picture, and the starting values bring the first picture back
for (const k of ['hold', 'ease', 'cpull']) if (![...document.querySelectorAll('[id^="par-pulledplane-' + k + '"]')].length) fail('no control for ' + k);
const P = S.param.pulledplane, def = { hold: 0.05, ease: 0.7, cpull: 16 };
if (JSON.stringify(P) !== JSON.stringify(def)) fail('the dials do not start at 0.05, 0.7, 16: ' + JSON.stringify(P));
S.mode = 'j'; S.c = [-0.6, 0.2, 0]; S.iter = 30; L.resetCam(); go(); await settle();
const first = sig(), out = ['start: ' + hits(first) + ' probes hit'];
for (const [k, v] of [['hold', 1], ['ease', 0], ['cpull', 0]]) {
  P[k] = v; go(); await settle(); const s = sig();
  if (s === first) fail('the dial ' + k + ' at ' + v + ' did not change the picture');
  const f = L.APPROACHES[S.approach].formula(P, 2); if (/undefined|NaN/.test(f)) fail('bad formula text');
  out.push(k + ' = ' + v + ': ' + hits(s) + ' probes hit');
  P[k] = def[k];
}
go(); await settle();
if (sig() !== first) fail('back at the starting values the picture is not the first picture');
S.c = [-1, 0, 0]; S.iter = 40; go(); await settle();
return out.join('; ') + '; starting values bring the first picture back';
""", wait='done', timeout=900))
    st += [
        # the Learn tab: the moves of the first squaring, Next step, and the line that says so
        dict(js=HEAD + """
$('mode-l').click(); await sleep(400);
if (!document.body.classList.contains('is-learn')) fail('Learn did not switch on');
$('learnSpace3').click(); await sleep(400);
const say = () => $('learnSay').textContent, note = () => document.body.innerText;
if (!note().includes('these moves show its first squaring only')) fail('Learn does not say that it shows the first squaring only');
$('learnFwd').click(); await sleep(200); $('learnFwd').click(); await sleep(300);
const K = L.learn.cache; if (!K || K.names.join(' ') !== 'Turn Stretch Add c') fail('the moves are not Turn, Stretch, Add c: ' + (K && K.names));
const s1 = K.say[1]; if (!/multiplied by itself, not doubled/.test(s1)) fail('the Stretch move does not say what it does: ' + s1);
if (!say() || /undefined|NaN/.test(say())) fail('the words under the picture: ' + say());
$('learnNext').click(); await sleep(400); $('learnFwd').click(); await sleep(300);
const s2 = L.learn.cache.say.join(' / '); if (!s2 || /undefined|NaN/.test(s2 + say())) fail('after Next step: ' + s2);
if (L.learn.k !== 1) fail('Next step did not go on to the second step');
if (L.learn.cache && L.learn.cache.fault) fail('Learn reports: ' + L.learn.cache.fault);
$('learnAgain').click(); await sleep(200);
$('mode-j').click(); await sleep(400);
if (document.body.classList.contains('is-learn') || apId() !== '%(id)s') fail('leaving Learn lost the entry');
return 'Learn: "' + s1 + '" / after Next step: "' + s2.slice(0, 90) + '"';
""" % dict(id=id_), wait='done', timeout=600),
        # a 3D model of the Julia set for c = -1 (48 cells)
        dict(js=HEAD + """
if (typeof L.meshBusy !== 'function' || !$('meshStart')) return 'model job skipped: no 3D model module';
window.squaringLabMeshTest = { cells: 48 };
S.mode = 'j'; S.c = [-1, 0, 0]; S.iter = 30; S.flat = false; go(); await settle();
$('meshStart').click(); await sleep(300);
return 'model job started for %(id)s';
""" % dict(id=id_), wait='!window.squaringLab.meshBusy || !window.squaringLab.meshBusy()', timeout=420),
        dict(js=HEAD + """
if (typeof L.meshBusy !== 'function' || !$('meshStart')) return 'model job skipped';
const msg = $('meshMsg') ? $('meshMsg').textContent : '';
if (!shown('meshSave')) fail('the model job did not end with a file to save: ' + msg);
delete window.squaringLabMeshTest;
return 'model job ended with a file to save. ' + msg.slice(0, 200);
""", wait='done', timeout=300),
    ]
    return st


LAST = [dict(js=HEAD + """
// back and forth between the entries: the same picture each time
S.mode = 'j'; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; L.resetCam();
const seen = {}, order = ['alongonce', 'pulledplane', 'turnalong', 'mercator', 'pulledplane', 'alongonce', 'mercator', 'turnalong'];
for (const id of order) {
  $('ap-' + id).click(); await sleep(250); go(); await settle();
  const s = sig();
  if (seen[id] !== undefined && seen[id] !== s) fail(id + ' drew another picture the second time it was chosen');
  seen[id] = s;
}
if (seen.alongonce === seen.turnalong || seen.alongonce === seen.mercator || seen.pulledplane === seen.mercator) fail('two different entries drew the same picture');
$('resetAll').click(); await sleep(400);
if (apId() !== 'mercator' || S.approach !== 0 || S.flat) fail('Reset everything did not bring the opening state back: ' + apId());
return 'each entry draws the same picture each time it is chosen; reset: ' + apId() + ', mode ' + S.mode;
""", wait='done', timeout=900)]

if __name__ == '__main__':
    part = sys.argv[1] if len(sys.argv) > 1 else 'all'
    base = json.load(open(os.path.join(run.ROOT, 'tools', 'smoke-v14.json'), encoding='utf-8'))
    os.makedirs(os.path.join(HERE, 'smoke'), exist_ok=True)
    old = base + [dict(s) for s in S20.NEW]
    n_changed = 0
    for s in old:
        if 'shot' in s:
            s['shot'] = 'out/r22/entry/smoke/' + os.path.basename(s['shot'])
        if OLD_LINE in s.get('js', ''):
            s['js'] = s['js'].replace(OLD_LINE, NEW_LINE); n_changed += 1
    assert n_changed == 1, n_changed
    new = steps_for('alongonce') + steps_for('pulledplane') + LAST
    steps = {'all': old + new, 'base': old, 'new': [run.UP] + new}[part]
    code, text, vals = run.shot(run.PAGE, steps, 'smoke-%s-steps' % part, '1400x950')
    text += 'exit %d\n' % code
    run.write('smoke-%s.log' % part, text)
    lines = text.splitlines()
    print('\n'.join(lines[-(len(new) + 14):]))
    print('steps: %d old + %d new; ran %d' % (len(old), len(new), len(steps)))
    sys.exit(code)
