"""Checks of the Colour section through the real controls: which controls show in which state, that the new ones
drive the picture, the wide ranges, and that the defaults are what the contract names. Writes panel.json and runs it.

  python out/r4/colour/panel.py [page] [size] [theme]     default: r4-colour 1400x950 dark
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
page = sys.argv[1] if len(sys.argv) > 1 else 'r4-colour'
size = sys.argv[2] if len(sys.argv) > 2 else '1400x950'
theme = sys.argv[3] if len(sys.argv) > 3 else 'dark'
tag = '%s-%s' % (size.split('x')[0], theme)

PRE = r"""
const L = window.squaringLab, S = L.S, C = S.colour, $ = id => document.getElementById(id);
const fail = m => { throw new Error(m); };
const shown = id => { const e = $(id); if (!e) fail('no control ' + id); return !!(e.offsetParent || e.getClientRects().length) && e.checkVisibility(); };
const pick = (id, text) => { const e = $(id); if (!e) fail('no control ' + id); const o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no choice ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const tick = (id, on) => { const e = $(id); if (!e) fail('no control ' + id); if (e.checked !== on) e.click(); };
const type = (id, v) => { const e = $(id + 'Num'); if (!e) fail('no box ' + id); e.focus(); e.value = String(v); e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); e.blur(); };
const frame = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
const want = (id, on, why) => { if (shown(id) !== on) fail(id + ' should be ' + (on ? 'shown' : 'hidden') + ': ' + why); };
$('secColour').open = true;
"""

steps = [
    ("defaults", """
L.resetAll(); await frame();
const d = { solid: 0, thick: 0.05, skip: 1, inMode: 0, inPal: -1, inRev: false, edge: 1, edgeGlow: 0, cutFace: false };
for (const k in d) if (C[k] !== d[k]) fail('default of ' + k + ' is ' + C[k]);
want('col-solid', true, '3D, orbit trap with a shape'); want('col-thick', false, 'no solid yet'); want('col-skip', false, 'no solid yet');
for (const id of ['col-edge', 'col-edgeGlow', 'col-inMode', 'col-inPal', 'col-inRev', 'col-cutFace']) want(id, false, '3D view, no cut');
return 'defaults ok';
"""),
    ("solid controls", """
pick('col-solid', 'Is the solid'); await frame();
if (C.solid !== 1) fail('solid not set: ' + C.solid);
want('col-thick', true, 'solid on'); want('col-skip', true, 'solid on'); want('col-radius', true, 'shell');
type('col-thick', 0.08); type('col-skip', 2);
if (C.thick !== 0.08 || C.skip !== 2) fail('thick or skip not taken: ' + C.thick + ' ' + C.skip);
pick('col-trap', 'Cross'); await frame(); want('col-radius', true, 'a cross is cut to the trap radius as a solid');
pick('col-trap', 'Three tones'); await frame(); want('col-thick', false, 'three tones has no shape'); want('col-solid', true, 'so that it can be switched off');
pick('col-trap', 'Sphere shell'); pick('col-mode', 'Plain clay'); await frame();
want('col-solid', true, 'the solid stays under another colouring'); want('col-trap', true, 'its shape too'); want('col-by', false, 'nothing is coloured by the trap');
pick('col-mode', 'Orbit trap'); await frame(); want('col-by', true, 'orbit trap again');
return 'solid controls ok';
"""),
    ("2D view", """
L.resetAll(); await frame();
tick('flat', true); await frame(); await frame();
for (const id of ['col-edge', 'col-edgeGlow', 'col-inMode']) want(id, true, '2D view');
for (const id of ['col-solid', 'col-thick', 'col-skip', 'col-cutFace', 'col-inPal', 'col-inRev']) want(id, false, '2D view at its defaults');
pick('col-inMode', 'How quickly'); await frame(); want('col-inPal', true, 'an inside colouring is on'); want('col-inRev', false, 'same palette as outside');
pick('col-inPal', 'Ocean'); await frame(); want('col-inRev', true, 'the inside has its own palette');
pick('col-mode', 'Plain clay'); await frame(); want('col-pal', true, 'the inside still reads the outside palette choice... or its own'); want('col-trap', false, 'no trap in use');
pick('col-inMode', 'Orbit trap'); await frame(); want('col-trap', true, 'the inside is coloured by the trap'); want('col-by', true, 'and by its choice');
type('col-edge', 3); type('col-edgeGlow', 12);
if (C.edge !== 3 || C.edgeGlow !== 12) fail('edge or glow not taken');
return '2D controls ok';
"""),
    ("cut face", """
L.resetAll(); await frame();
tick('cutOn', true); await frame(); await frame(); await frame();
want('col-cutFace', true, 'the solid is cut open'); want('col-inMode', false, 'not asked for yet');
tick('col-cutFace', true); await frame(); want('col-inMode', true, 'cut face coloured like the inside');
pick('col-inMode', 'Where the orbit'); await frame();
tick('cutOn', false); await frame(); await frame(); await frame();
want('col-cutFace', false, 'no cut'); want('col-inMode', false, 'no cut');
return 'cut face controls ok';
"""),
    ("wide ranges", """
L.resetAll(); await frame();
if (!L.setExtreme) return 'no setExtreme on this page';
pick('col-solid', 'Is the solid'); await frame();
L.setExtreme(true); await frame();
const wide = ['col-thick', 'col-skip', 'col-glow', 'col-radius', 'col-tx', 'col-bands'].filter(id => { const w = $(id + 'Wide'); return w && !w.hidden; });
type('col-skip', 300); type('col-radius', 120);
const got = [C.skip, C.radius];
L.setExtreme(false); await frame();
const back = [C.skip, C.radius];
L.resetAll();
if (wide.length !== 6) fail('wide tags: ' + wide);
if (got[0] !== 300 || got[1] !== 120) fail('wide values not taken: ' + got);
if (back[0] !== 100 || back[1] !== 50) fail('values not pulled back: ' + back);
return 'wide ranges ok: ' + wide.join(' ');
"""),
]
acts = [{'wait': 'done', 'timeout': 240}]
for name, js in steps:
    acts.append({'js': PRE + js})
# pictures of the section
acts += [
    {'js': PRE + "L.resetAll(); pick('col-solid', 'Is the solid'); pick('col-trap', 'Cross'); $('secColour').scrollIntoView();"},
    {'sleep': 0.4}, {'wait': 'done', 'timeout': 300, 'shot': 'out/r4/colour/panel-solid-%s.png' % tag},
    {'js': PRE + "L.resetAll(); tick('flat', true); pick('col-inMode', 'How quickly'); pick('col-inPal', 'Ocean'); type('col-edge', 2); $('secColour').scrollIntoView();"},
    {'sleep': 0.4}, {'wait': 'done', 'timeout': 300, 'shot': 'out/r4/colour/panel-2d-%s.png' % tag},
    {'js': PRE + "L.resetAll(); tick('cutOn', true); await frame(); await frame(); tick('col-cutFace', true); pick('col-inMode', 'Where the orbit'); $('secColour').scrollIntoView();"},
    {'sleep': 0.4}, {'wait': 'done', 'timeout': 300, 'shot': 'out/r4/colour/panel-cut-%s.png' % tag},
    {'js': PRE + "L.resetAll();"},
]
path = os.path.join(HERE, 'panel.json')
json.dump(acts, open(path, 'w'))
r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--actions', path, '--size', size, '--theme', theme],
                   cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8'), capture_output=True, text=True, encoding='utf-8')
print((r.stdout + r.stderr).strip())
print('exit', r.returncode)
