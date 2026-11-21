"""Targeted check of the interim page: the buttons and lists that used the Planes dial, and the new entries.

python out/me/v12b/check.py -> out/me/v12b/check.json   (run with tools/shot.py --url dist/v12b.html)
"""
import io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); e.dispatchEvent(new Event('blur')); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const apId = () => L.APPROACHES[L.S.approach].id;
const hits = () => { let n = 0; const w = $('stage').clientWidth, h = $('stage').clientHeight; for (let i = 1; i < 8; i++) for (let j = 1; j < 8; j++) if (L.pick(w * i / 8, h * j / 8)) n++; return n; };
"""
steps = []
def step(js, shot=None):
    s = {"js": PRE + js.strip(), "wait": "done", "timeout": 240}
    if shot:
        s["shot"] = "out/me/v12b/shots/c-" + shot + ".png"; s["clip"] = "#stage"
    steps.append(s)

step(r"""
L.R.warmOn = false; L.S.q.aa = 3; L.touch();
const names = L.APPROACHES.map(a => a.id + '=' + a.name).join(' | ');
for (const a of L.APPROACHES) if (!$('ap-' + a.id) || !$('f-' + a.id).textContent) fail('entry ' + a.id + ' is not in the list or has no formula');
return names;
""")
# Show Figure 4 from a messy state
step(r"""
$('mode-k').click(); $('flat').click(); await sleep(200);
$('fig4Show').click(); await sleep(500);
if (apId() !== 'fold' || !$('ap-fold').checked) fail('Show Figure 4 should land on the two-plane entry, it is on ' + apId());
if (L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0' || L.S.flat || L.S.param.fold.planes !== 2 || L.S.param.fold.lift !== 0) fail('Show Figure 4 state: ' + JSON.stringify([L.S.mode, L.S.c, L.S.flat, L.S.param.fold]));
return 'Show Figure 4 from the Kleinian 2D view: on ' + apId();
""")
step(r"""
const h = hits(); if (h < 8) fail('the Figure 4 picture is empty: ' + h);
$('fig4Back').click(); await sleep(400);
if (apId() !== 'mercator' || L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0') fail('Back to one plane: ' + apId() + ' ' + L.S.mode);
return 'Figure 4 picture ' + h + ' of 49 probes; Back to one plane goes to ' + apId();
""", 'fig4')
# As it was found
step(r"""
const h = hits(); if (h < 5) fail('one-plane Basilica empty: ' + h);
pick('juliaPreset', 'Cracked Basilica'); await sleep(300);
if (!shown('juliaFound')) fail('Cracked Basilica under one plane should offer As it was found');
const t = $('juliaFound').title;
if (!/two planes/.test(t)) fail('the button should say it goes to two planes: ' + t);
$('juliaFound').click(); await sleep(400);
if (apId() !== 'fold' || !$('ap-fold').checked || L.S.param.fold.planes !== 2) fail('As it was found should go to the two-plane entry: ' + apId());
if (shown('juliaFound')) fail('the button should go once it is as recorded');
return 'As it was found: "' + t + '" -> ' + apId() + ', note: ' + $('juliaNote').textContent.slice(0, 160);
""", 'onep-bas')
step(r"""
const h = hits(); if (h < 5) fail('Cracked Basilica with two planes empty: ' + h);
pick('juliaPreset', 'Douady rabbit'); await sleep(300);
const offered = shown('juliaFound'), t = offered ? $('juliaFound').title : '';
if (offered) { $('juliaFound').click(); await sleep(400); }
return 'Douady rabbit while on two planes: button ' + (offered ? 'offered ("' + t + '") -> ' + apId() + ', iterations ' + L.S.iter : 'not offered') + '; picture had ' + h + ' probes';
""", 'cracked')
# twins
step(r"""
$('mode-k').click(); $('flat').click(); await sleep(200);
$('twinMerc').click(); await sleep(500);
if (apId() !== 'mercator' || L.S.mode !== 'm' || L.S.flip.join() !== '0,1' || L.S.flat) fail('twin of Sphere inversions: ' + JSON.stringify([apId(), L.S.mode, L.S.flip, L.S.flat]));
return 'twinMerc ok';
""")
step(r"""
const h = hits(); if (h < 5) fail('twin of Sphere inversions empty: ' + h);
$('twinLathe').click(); await sleep(500);
if (apId() !== 'lathe' || L.S.flip.join() !== '0,1') fail('twin of the Lathe: ' + apId());
return 'twin of Sphere inversions ' + h + ' probes; twinLathe ok';
""", 'twin-merc')
step(r"""
const h = hits(); if (h < 5) fail('twin of the Lathe empty: ' + h);
$('twinBulb').click(); await sleep(500);
if (apId() !== 'bulb' || L.S.flip.join() !== '0,1') fail('twin of the Mandelbulb: ' + apId());
return 'twin of the Lathe ' + h + ' probes; twinBulb ok';
""", 'twin-lathe')
step(r"""
const h = hits(); if (h < 5) fail('twin of the Mandelbulb empty: ' + h);
$('twinOff').click(); await sleep(400);
if (L.S.flip.join() !== '0,0') fail('Back to the plain rule left flip at ' + L.S.flip);
return 'twin of the Mandelbulb ' + h + ' probes; plain rule back';
""", 'twin-bulb')
# the new entry and its dial
step(r"""
$('ap-tilt').click(); await sleep(400); L.resetCam(); L.touch();
if (apId() !== 'tilt' || L.S.param.tilt.tilt !== 40) fail('tilt entry: ' + apId() + ' ' + JSON.stringify(L.S.param.tilt));
return 'twisted square on show, formula: ' + $('f-tilt').textContent.slice(0, 140);
""")
step(r"""
const h = hits(); if (h < 5) fail('twisted square empty: ' + h);
type('par-tilt-tiltNum', '180'); await sleep(300);
if (L.S.param.tilt.tilt !== 180) fail('typing the tilt did not take: ' + L.S.param.tilt.tilt);
return 'twisted square ' + h + ' probes; tilt typed to 180';
""", 'tilt40')
step(r"""
const h = hits(); if (h < 5) fail('twisted square at 180 empty: ' + h);
$('mode-j').click(); await sleep(200); pick('juliaPreset', 'Douady rabbit'); type('par-tilt-tiltNum', '40'); L.resetCam(); L.touch(); await sleep(300);
return 'tilt 180 ' + h + ' probes; rabbit under the twisted square';
""", 'tilt180')
# the examples of trap solids, and Reset everything
step(r"""
const h = hits(); if (h < 5) fail('rabbit under the twisted square empty: ' + h);
const out = [];
for (const e of L.EXAMPLES) {
  pick('trapExamples', e.name); await sleep(250);
  out.push(e.name + ':' + L.S.mode + '/' + apId());
}
return 'rabbit ' + h + ' probes; examples picked: ' + out.join(', ');
""", 'tilt-rabbit')
step(r"""
const h = hits();
$('resetAll').click(); await sleep(600);
if (apId() !== 'mercator' || L.S.mode !== 'm' || L.S.colour.solid !== 0 || L.S.param.tilt.tilt !== 40 || L.S.param.fold.planes !== 2) fail('Reset everything: ' + JSON.stringify([apId(), L.S.mode, L.S.colour.solid, L.S.param.tilt, L.S.param.fold]));
return 'last example ' + h + ' probes; Reset everything brings the opening state back';
""", 'example-last')
step(r"""
const h = hits(); if (h < 5) fail('opening picture empty after reset: ' + h);
return 'opening picture ' + h + ' probes';
""", 'reset')

io.open(os.path.join(ROOT, 'out', 'me', 'v12b', 'check.json'), 'w', encoding='utf-8').write(json.dumps(steps, indent=1))
print(len(steps), 'steps')
