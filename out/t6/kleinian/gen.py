"""Tester "kleinian": writes the step files for tools/shot.py. Run from the project root:
   python out/t6/kleinian/gen.py
"""
import json, os

HERE = 'out/t6/kleinian'
PRE = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.focus(); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const pickAt = (id, i) => { const e = $(id); e.value = String(i); e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const chosen = id => { const e = $(id); return e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : ''; };
const camNow = () => [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => x.toFixed(4)).join();
const KD = ['kmy', 'kmx', 'kmz', 'kL', 'kiter', 'kinvr', 'kcx', 'kcy', 'kcz'];
const ranges = () => KD.map(id => id + ' slider ' + $(id).min + '..' + $(id).max + ' step ' + $(id).step + ' box ' + $(id + 'Num').value + (shown(id) ? '' : ' (hidden)') + ($(id + 'Wide') && !$(id + 'Wide').hidden ? ' WIDE' : ''));
const kNow = () => JSON.stringify(L.S.k);
// hits of a grid of probes: rows of '1' (solid) and '0'
const grid = (nx, ny) => { const w = $('stage').clientWidth, h = $('stage').clientHeight, rows = []; for (let j = 0; j < ny; j++) { let s = ''; for (let i = 0; i < nx; i++) s += L.pick(w * (i + 0.5) / nx, h * (j + 0.5) / ny) ? '1' : '0'; rows.push(s); } return rows; };
"""


def js(code, **kw):
    a = {'js': PRE + code}
    a.update(kw)
    return a


def entry(i, folder, frame=True, extra=''):
    return js(r"""
const i = %d, sel = $('kleinPreset'), cam0 = camNow(), it0 = L.S.k.iter;
pickAt('kleinPreset', i + 1);
const opt = sel.options[sel.selectedIndex], p = L.KLEIN_PRESETS[i], bad = [];
for (const key of ['mx', 'my', 'mz', 'three', 'L', 'cx', 'cy', 'cz', 'invR']) if (p.k[key] !== undefined && L.S.k[key] !== p.k[key] && !(key === 'L' && !p.k.three)) bad.push(key + '=' + L.S.k[key]);
const camSame = camNow() === cam0, iterSame = L.S.k.iter === it0;
%s
%s
return { i, text: opt ? opt.text : '(none)', group: opt ? opt.parentNode.label || '' : '', wrong: bad, iter: L.S.k.iter, iterSame, camSame, warn: $('kleinWarn').hidden ? '' : $('kleinWarn').textContent, cam: camNow(), note: $('kleinNote').textContent };
""" % (i, "$('kleinFrame').click();" if frame else '', extra))


def shot(path, timeout=400):
    return {'wait': 'done', 'timeout': timeout, 'shot': '%s/%s' % (HERE, path), 'clip': '#stage'}


def with_shot(a, path, timeout=400):
    a = dict(a); a.update(shot(path, timeout)); return a


def write(name, steps):
    with open(os.path.join(HERE, name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(steps, f, ensure_ascii=False, indent=1)
    print(name, len(steps), 'steps')


OPEN = js(r"""
const k = L.S.k, d = $('kiter');
const out = { iter: k.iter, slider: d.min + '..' + d.max, box: $('kiterNum').value, extreme: !!L.S.extreme,
  quality: ['qUltra', 'qFast', 'qBal', 'qFine'].filter(id => $(id).classList.contains('is-on')).join(),
  colour: JSON.stringify(L.S.colour), k: kNow(),
  opts: [...$('kleinPreset').options].map(o => (o.parentNode.label || '-') + ' | ' + o.text + (o.disabled ? ' (disabled)' : '')) };
window.__presets = JSON.stringify(L.KLEIN_PRESETS);
return out;
""")
DUMP = js("return JSON.stringify(L.KLEIN_PRESETS);")
TOK = js("$('mode-k').click(); await sleep(100); return { panel: !$('kleinPanel').hidden, chosen: chosen('kleinPreset'), note: $('kleinNote').textContent, cam: camNow() };", wait='done', timeout=400)

# ---- A: all 34 entries through the drop-down, Frame it, Balanced
for name, ids in (('a1', range(0, 12)), ('a2', range(12, 23)), ('a3', range(23, 34))):
    steps = [OPEN, DUMP] if name == 'a1' else []
    steps.append(with_shot(TOK, 'a/%s-open.png' % name))
    for i in ids:
        steps.append(with_shot(entry(i, 'a'), 'a/e%02d.png' % i))
        steps.append(js("return { i: %d, grid: grid(24, 14) };" % i))
    write(name, steps)

# ---- v5: the list the user has now
write('v5', [js("return JSON.stringify(L.KLEIN_PRESETS);"),
             js("return { iter: L.S.k.iter, slider: $('kiter').min + '..' + $('kiter').max, opts: [...$('kleinPreset').options].map(o => (o.parentNode.label || '-') + ' | ' + o.text) };")])

# ---- D: every Kleinian control once, Extreme ranges on
D = []
D.append(with_shot(js(r"""
$('mode-k').click(); document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); await sleep(150);
const out = { before: ranges(), k3: $('k3').checked };
type('kiterNum', '151'); out.typed151 = L.S.k.iter + ' box ' + $('kiterNum').value;
type('kiterNum', '400'); out.typed400 = L.S.k.iter + ' box ' + $('kiterNum').value;
type('kiterNum', '999'); out.typed999 = L.S.k.iter + ' box ' + $('kiterNum').value;
type('kiterNum', '150'); out.back = L.S.k.iter;
type('kmyNum', '5'); out.my5_normal = L.S.k.my + ' box ' + $('kmyNum').value; type('kmyNum', '2');
out.extremeLabel = $('extreme').parentNode.textContent.trim(); out.extremeNote = $('extremeNote').textContent;
return out;"""), 'd/00-open.png'))
D.append(js(r"""
$('extreme').click(); await sleep(200);
return { extreme: L.S.extreme, checked: $('extreme').checked, after: ranges(), note: $('extremeNote').textContent, k: kNow(),
  wide: [...document.querySelectorAll('.dial-wide')].filter(e => !e.hidden).map(e => e.id.replace(/Wide$/, '')).join(' ') };"""))


def ctl(code, path, timeout=400):
    D.append(with_shot(js(code + "\nreturn { k: kNow(), warn: $('kleinWarn').hidden ? '' : $('kleinWarn').textContent, list: chosen('kleinPreset'), note: $('kleinNote').textContent.slice(0, 80), boxes: KD.map(id => id + '=' + $(id + 'Num').value).join(' ') };"), path, timeout))


ctl("type('kmyNum', '1.8');", 'd/01-my1.8.png')
ctl("type('kmyNum', '5');", 'd/02-my5-beyond.png')
ctl("type('kmyNum', '2'); const s = $('kmx'); s.value = '0.3'; s.dispatchEvent(new Event('input', { bubbles: true })); s.dispatchEvent(new Event('change', { bubbles: true }));", 'd/03-mx0.3-slider.png')
ctl("type('kmxNum', '3');", 'd/04-mx3-beyond.png')
ctl("type('kmxNum', '0'); type('kmzNum', '0.4');", 'd/05-mz0.4.png')
ctl("type('kmzNum', '0'); $('k3').click(); await sleep(100); window.__LshownOff = shown('kL');", 'd/06-third-off.png')
D.append(js("const off = window.__LshownOff; $('k3').click(); await sleep(100); return { L_shown_while_off: off, L_shown_now: shown('kL'), three: L.S.k.three };"))
ctl("type('kLNum', '1.5');", 'd/07-L1.5.png')
ctl("type('kLNum', '10');", 'd/08-L10-beyond.png')
ctl("type('kLNum', '1'); type('kiterNum', '800');", 'd/09-depth800-beyond.png', 600)
ctl("type('kiterNum', '20');", 'd/10-depth20.png')
ctl("type('kiterNum', '5');", 'd/11-depth5.png')
ctl("type('kiterNum', '150'); type('kinvrNum', '0.6');", 'd/12-radius0.6.png')
ctl("type('kinvrNum', '12');", 'd/13-radius12-beyond.png')
ctl("type('kinvrNum', '1.2'); type('kcxNum', '0.3');", 'd/14-cx0.3.png')
ctl("type('kcxNum', '1'); type('kcyNum', '0.5');", 'd/15-cy0.5.png')
ctl("type('kcyNum', '1'); type('kczNum', '0.6');", 'd/16-cz0.6.png')
ctl("type('kczNum', '0'); type('kcxNum', '8');", 'd/17-cx8-beyond.png')
ctl("type('kcxNum', '1'); type('kcyNum', '2.5');", 'd/18-cy2.5-inside-wall.png')
D.append(js(r"""
type('kcyNum', '1');
const up = $('kczNum').parentNode.querySelector('.dial-up'), dn = $('kczNum').parentNode.querySelector('.dial-down');
const z0 = L.S.k.cz; up.click(); const z1 = L.S.k.cz; dn.click(); dn.click(); const z2 = L.S.k.cz; up.click();
const n = $('kiterNum'); n.focus(); const i0 = L.S.k.iter; n.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true })); const i1 = L.S.k.iter; n.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
type('kiterNum', 'abc'); const junk = L.S.k.iter + ' box ' + $('kiterNum').value; type('kiterNum', '12.7'); const frac = L.S.k.iter + ' box ' + $('kiterNum').value; type('kiterNum', '-3'); const neg = L.S.k.iter + ' box ' + $('kiterNum').value;
type('kiterNum', '800'); type('kmyNum', '5'); type('kinvrNum', '12');
return { cz: [z0, z1, z2], iterArrow: [i0, i1], junk, frac, neg, k: kNow() };"""))
D.append(js(r"""
$('extreme').click(); await sleep(200);
return { extreme: L.S.extreme, after_off: ranges(), k: kNow(), warn: $('kleinWarn').hidden ? '' : $('kleinWarn').textContent };"""))
D.append(with_shot(js(r"""
const b = $('kleinReset').querySelector('button'); const label = b.textContent; b.click(); await sleep(150);
return { label, k: kNow(), list: chosen('kleinPreset'), ranges: ranges(), cam: camNow() };"""), 'd/19-after-reset.png'))
write('d', D)

# ---- E: Ultra fast and Fine
EU = [0, 2, 5, 8, 14, 20, 25, 27, 29, 33]
EF = [8, 14, 2, 27, 33, 21]
E1 = [TOK, js("$('qUltra').click(); await sleep(50); return { q: JSON.stringify(L.S.q), marked: $('qUltra').classList.contains('is-on') };")]
for i in EU:
    E1.append(with_shot(entry(i, 'e'), 'e/ultra-e%02d.png' % i))
write('e1', E1)
E2 = [TOK, js("$('qFine').click(); await sleep(50); return { q: JSON.stringify(L.S.q), marked: $('qFine').classList.contains('is-on') };")]
for i in EF:
    E2.append(with_shot(entry(i, 'e'), 'e/fine-e%02d.png' % i, 900))
write('e2', E2)

# ---- F: the 2D view of entries
F = [TOK]
for i in (2, 8, 21, 29, 0):
    F.append(with_shot(entry(i, 'f'), 'f/e%02d-3d.png' % i))
    F.append(with_shot(js("$('flat').click(); await sleep(150); return { flat: L.S.flat, label: $('flat').parentNode.textContent.trim(), v2: JSON.stringify(L.S.v2), cut: L.S.cut };"), 'f/e%02d-2d.png' % i))
    F.append(js("$('flat').click(); await sleep(100); return { flat: L.S.flat };"))
write('f', F)

# ---- G: trap solids on entries
G = [TOK, js("document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); await sleep(100); return { solidOpts: [...$('col-solid').options].map(o => o.text), trap: chosen('col-trap'), by: chosen('col-by'), colour: JSON.stringify(L.S.colour) };")]
for i in (0, 3, 24, 21):
    G.append(with_shot(entry(i, 'g', extra="pick('col-solid', 'Colours the surface');"), 'g/e%02d-0-colours.png' % i))
    G.append(with_shot(js("pick('col-solid', 'Is the solid'); await sleep(100); return { solid: L.S.colour.solid, thick: L.S.colour.thick, skip: L.S.colour.skip, thickShown: shown('col-thick'), skipShown: shown('col-skip') };"), 'g/e%02d-1-is.png' % i, 600))
    G.append(js("return { i: %d, grid: grid(24, 14) };" % i))
    G.append(with_shot(js("pick('col-solid', 'Is added to the solid'); await sleep(100); return { solid: L.S.colour.solid };"), 'g/e%02d-2-added.png' % i, 600))
write('g', G)
