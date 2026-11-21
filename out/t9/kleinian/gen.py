"""Tester "kleinian", second check: writes the step files for tools/shot.py (page dist/v8.html).
   python out/t9/kleinian/gen.py      (from the project root)
Adapted from out/t6/kleinian/gen.py."""
import json, os

HERE = 'out/t9/kleinian'
PRE = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.focus(); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id); if (!e) fail('no control ' + id); const o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const pickAt = (id, i) => { const e = $(id); e.value = String(i); e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const chosen = id => { const e = $(id); return e && e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : ''; };
const camNow = () => [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => x.toFixed(4)).join();
const kNow = () => JSON.stringify(L.S.k);
const openAll = () => document.querySelectorAll('details.sec').forEach(d => { d.open = true; });
const notes = () => [...document.querySelectorAll('p.note')].filter(p => p.id.startsWith('col-') && !p.hidden && p.getBoundingClientRect().width > 0).map(p => p.textContent.slice(0, 46));
const cutNote = () => { const p = [...document.querySelectorAll('p.note')].find(p => p.textContent.startsWith('With this group or this trap centre')); return p ? (!p.hidden && p.getBoundingClientRect().width > 0 ? 'SHOWN' : 'hidden') : 'ABSENT'; };
const warn = () => $('kleinWarn').hidden ? '' : $('kleinWarn').textContent;
const grid = (nx, ny) => { const w = $('stage').clientWidth, h = $('stage').clientHeight, rows = []; for (let j = 0; j < ny; j++) { let s = ''; for (let i = 0; i < nx; i++) s += L.pick(w * (i + 0.5) / nx, h * (j + 0.5) / ny) ? '1' : '0'; rows.push(s); } return rows; };
const hits = () => { const g = grid(15, 11); let n = 0, ring = 0; g.forEach((r, j) => [...r].forEach((ch, i) => { if (ch === '1') { n++; if (j === 0 || j === 10 || i === 0 || i === 14) ring++; } })); return n + ' of 165, ' + ring + ' on the ring'; };
const frame = async () => { $('kleinFrame').click(); await sleep(80); };
"""


def js(code, **kw):
    a = {'js': PRE + code}
    a.update(kw)
    return a


def shot(path, timeout=600):
    return {'wait': 'done', 'timeout': timeout, 'shot': '%s/%s' % (HERE, path), 'clip': '#stage'}


def st(code, path, timeout=600):
    a = js(code); a.update(shot(path, timeout)); return a


def write(name, steps):
    with open(os.path.join(HERE, name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(steps, f, ensure_ascii=False, indent=1)
    print(name, len(steps), 'steps')


TOK = js("$('mode-k').click(); openAll(); await sleep(150); return { chosen: chosen('kleinPreset'), cam: camNow(), q: ['qUltra', 'qFast', 'qBal', 'qFine'].filter(id => $(id).classList.contains('is-on')).join(), colour: JSON.stringify(L.S.colour), k: kNow() };", wait='done', timeout=600)
STATE = "return { k: kNow(), entry: chosen('kleinPreset'), solid: chosen('col-solid'), trap: chosen('col-trap'), tc: [L.S.colour.tx, L.S.colour.ty, L.S.colour.tz].join(), thick: L.S.colour.thick, skip: L.S.colour.skip, cutNote: cutNote(), warn: warn(), notes: notes() };"
HITS = js("return { hits: hits(), cutNote: cutNote() };")

# ---------------- r1: kleinian-1 with the first check's own steps, and the note beside the choice
R1 = [TOK]
# the reproduction, word for word (entry 3 is option value '4')
R1.append(st("pickAt('kleinPreset', 4); await frame(); pick('col-solid', 'Is the solid'); await sleep(100);" + STATE, 'r1/e03-1-is.png'))
R1.append(HITS)
R1.append(st("$('qFine').click(); await sleep(50);" + STATE, 'r1/e03-2-is-fine.png', 900))
R1.append(st("L.cam.dist = 20; L.touch(); return { cam: camNow() };", 'r1/e03-3-is-fine-far.png', 900))
R1.append(st("$('qBal').click(); await frame(); pick('col-solid', 'Is added to the solid'); await sleep(100);" + STATE, 'r1/e03-4-added.png'))
R1.append(st("pickAt('kleinPreset', 25); await frame(); pick('col-solid', 'Is the solid'); await sleep(100);" + STATE, 'r1/e24-1-is.png'))
R1.append(st("pick('col-solid', 'Is added to the solid'); await sleep(100);" + STATE, 'r1/e24-2-added.png'))
# the clean ones of the first check
R1.append(st("pickAt('kleinPreset', 1); await frame(); pick('col-solid', 'Is the solid'); await sleep(100);" + STATE, 'r1/e00-1-is.png'))
R1.append(HITS)
R1.append(st("pickAt('kleinPreset', 22); await frame(); await sleep(100);" + STATE, 'r1/e21-1-is.png'))
write('r1', R1)

# ---------------- n1: is the note true, and shown exactly when the fault shows
N1 = [TOK]
N1.append(st("pick('col-solid', 'Is the solid'); await sleep(100);" + STATE, 'n1/00-e00-is.png'))
# the note follows the list without a colour control being touched
N1.append(js("const out = {}; out.e00 = cutNote(); pickAt('kleinPreset', 4); await sleep(400); out.e03 = cutNote(); pickAt('kleinPreset', 1); await sleep(400); out.back00 = cutNote();"
             " type('kmxNum', '0.3'); await sleep(400); out.mx03 = cutNote(); type('kmxNum', '0'); await sleep(400); out.mx0 = cutNote(); type('kmzNum', '0.4'); await sleep(400); out.mz04 = cutNote(); type('kmzNum', '0'); await sleep(400); out.mz0 = cutNote();"
             " pick('col-solid', 'Colours the surface'); await sleep(300); out.colours_e00 = cutNote(); pickAt('kleinPreset', 4); await sleep(400); out.colours_e03 = cutNote(); pick('col-solid', 'Is the solid'); await sleep(300); out.is_e03 = cutNote();"
             " $('flat').click(); await sleep(400); out.flat_e03 = cutNote(); $('flat').click(); await sleep(400); out.unflat_e03 = cutNote(); pickAt('kleinPreset', 1); await sleep(300); out.end = cutNote(); return out;", wait='done', timeout=600))
# trap centre moved on the starting group
N1.append(st("pickAt('kleinPreset', 1); await frame(); type('col-txNum', '0.6'); await sleep(100);" + STATE, 'n1/01-e00-tx06.png'))
N1.append(st("type('col-txNum', '0'); type('col-tzNum', '0.4'); await sleep(100);" + STATE, 'n1/02-e00-tz04.png'))
N1.append(st("type('col-tzNum', '0'); type('col-tyNum', '0.5'); await sleep(100);" + STATE, 'n1/03-e00-ty05.png'))
N1.append(HITS)
N1.append(st("type('col-tyNum', '0.25'); await sleep(100);" + STATE, 'n1/04-e00-ty025.png'))
N1.append(st("type('col-tyNum', '1'); await sleep(100);" + STATE, 'n1/05-e00-ty1.png'))
# groups that do not lean, note hidden: are the pieces whole?
N1.append(st("type('col-tyNum', '0'); pickAt('kleinPreset', 2); await frame(); await sleep(100);" + STATE, 'n1/06-e01-is.png'))
N1.append(st("pickAt('kleinPreset', 19); await frame(); await sleep(100);" + STATE, 'n1/07-e18-is.png'))
N1.append(st("pickAt('kleinPreset', 20); await frame(); await sleep(100);" + STATE, 'n1/08-e19-is.png'))
N1.append(st("pickAt('kleinPreset', 23); await frame(); await sleep(100);" + STATE, 'n1/09-e22-is.png'))
# groups that lean, note shown: is there a fault to see?
N1.append(st("pickAt('kleinPreset', 3); await frame(); await sleep(100);" + STATE, 'n1/10-e02-is.png'))
N1.append(st("pickAt('kleinPreset', 16); await frame(); await sleep(100);" + STATE, 'n1/11-e15-is.png'))
N1.append(st("pickAt('kleinPreset', 5); await frame(); await sleep(100);" + STATE, 'n1/12-e04-is.png'))
N1.append(st("pickAt('kleinPreset', 34); await frame(); await sleep(100);" + STATE, 'n1/13-e33-is.png'))
# every trap shape on the starting group, note hidden: whole?
N1.append(st("pickAt('kleinPreset', 1); await frame(); pick('col-trap', 'Cross'); await sleep(100);" + STATE, 'n1/20-e00-cross.png'))
N1.append(st("pick('col-trap', 'Planes'); await sleep(100);" + STATE, 'n1/21-e00-planes.png'))
N1.append(st("pick('col-trap', 'Ring'); await sleep(100);" + STATE, 'n1/22-e00-ring.png'))
N1.append(st("pick('col-trap', 'Point'); type('col-thickNum', '0.2'); await sleep(100);" + STATE, 'n1/23-e00-point-t02.png'))
N1.append(st("pick('col-trap', 'Line'); pick('col-axis', 'The x-axis'); await sleep(100);" + STATE, 'n1/24-e00-linex-t02.png'))
N1.append(st("pick('col-trap', 'Ray'); pick('col-ray', '+x'); await sleep(100);" + STATE, 'n1/25-e00-ray+x-t02.png'))
N1.append(st("pick('col-ray', '+y'); await sleep(100);" + STATE, 'n1/26-e00-ray+y-t02.png'))
N1.append(st("pick('col-ray', '+z'); await sleep(100);" + STATE, 'n1/27-e00-ray+z-t02.png'))
N1.append(st("pick('col-ray', '−x'); await sleep(100);" + STATE, 'n1/28-e00-ray-x-t02.png'))
write('n1', N1)

# ---------------- r2: kleinian-2
R2 = [js("$('mode-k').click(); await sleep(150); return { k: kNow(), warn: warn(), bound: L.S.view.bound, cam: camNow() };", wait='done', timeout=600)]
R2.append(st("const e = $('kinvrNum'); e.focus(); e.value = '10'; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); await sleep(300); return { k: kNow(), warn: warn(), shownWarn: shown('kleinWarn'), reach: L.kleinReach(), entry: chosen('kleinPreset') };", 'r2/radius10-typed.png'))
R2.append(js("return { hits: hits() };"))
R2.append(st("type('kinvrNum', '3'); await sleep(300); return { k: kNow(), warn: warn(), reach: L.kleinReach() };", 'r2/radius3.png'))
R2.append(js("return { hits: hits() };"))
# the advice of the sentence: zoom out
R2.append(st("L.cam.dist = 16; L.touch(); await sleep(400); return { cam: camNow(), warn: warn(), bound: L.S.view.bound };", 'r2/radius3-dist16.png'))
R2.append(js("return { hits: hits() };"))
R2.append(st("type('kinvrNum', '2.1'); L.cam.dist = 7; L.touch(); await sleep(400); return { warn: warn(), cam: camNow() };", 'r2/radius2.1.png'))
R2.append(st("type('kinvrNum', '2'); await sleep(400); return { warn: warn() };", 'r2/radius2.0.png'))
R2.append(js("return { hits: hits() };"))
R2.append(st("type('kinvrNum', '1.5'); await sleep(400); return { warn: warn() };", 'r2/radius1.5.png'))
R2.append(js("const out = { hits: hits() }; $('extreme').click(); await sleep(200); type('kinvrNum', '12'); await sleep(400); out.r12 = L.S.k.invR; out.warn12 = warn(); $('extreme').click(); await sleep(300); out.afterOff = L.S.k.invR; out.warnOff = warn();"
              " type('kinvrNum', '3'); await sleep(300); out.warn3 = warn().slice(0, 40); pickAt('kleinPreset', 4); await sleep(400); out.entry = chosen('kleinPreset'); out.warnEntry = warn(); out.r = L.S.k.invR; return out;", wait='done', timeout=600))
# real use: the slider's top, then the zoom control the user has
R2.append(js("pickAt('kleinPreset', 1); await sleep(200); const s = $('kinvr'); s.value = s.max; s.dispatchEvent(new Event('input', { bubbles: true })); s.dispatchEvent(new Event('change', { bubbles: true })); await sleep(400);"
              " const out = { r: L.S.k.invR, warn: warn().slice(0, 60), zoomIds: [...document.querySelectorAll('[id*=zoom], [id*=Zoom]')].map(e => e.id + ':' + e.tagName + (e.min !== undefined ? ' ' + e.min + '..' + e.max + ' v ' + e.value : '')).slice(0, 20), view: JSON.stringify(L.S.view) }; return out;", wait='done', timeout=600))
write('r2', R2)

# ---------------- r3: layout-2 (run at three sizes)
MEASURE = ("$('mode-k').click(); await sleep(200); openAll(); await sleep(100); const s = $('kleinPreset'), cs = getComputedStyle(s), c = document.createElement('canvas').getContext('2d');"
           " c.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily; const room = s.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 18;"
           " const w = [...s.options].map(o => [Math.round(c.measureText(o.text).width), o.text]); w.sort((a, b) => b[0] - a[0]);"
           " return { win: innerWidth + 'x' + innerHeight, options: s.options.length, room, clientWidth: s.clientWidth, font: c.font, tooWide: w.filter(x => x[0] > room), widest: w.slice(0, 4), sideways: document.documentElement.scrollWidth > innerWidth };")
R3 = [js(MEASURE, wait='done', timeout=600)]
R3.append({'js': PRE + "const s = $('kleinPreset'); const w = [...s.options].map(o => [o.text.length, o.value, o.text]); w.sort((a, b) => b[0] - a[0]); pickAt('kleinPreset', w[0][1]); await sleep(300); s.scrollIntoView({ block: 'center' }); return { picked: chosen('kleinPreset') };",
           'wait': 'done', 'timeout': 600, 'shot': HERE + '/r3/closed-list-SIZE.png', 'clip': '#kleinPreset'})
for size in ('1400x950', '1024x768', '375x812'):
    steps = json.loads(json.dumps(R3).replace('SIZE', size))
    write('r3-' + size, steps)

# ---------------- q: the colours of the Kleinian view across the four quality presets
QS = [('qUltra', 'ultra'), ('qFast', 'fast'), ('qBal', 'bal'), ('qFine', 'fine')]
Q = [TOK]


def qrow(tag, setup):
    first = True
    for qid, qn in QS:
        Q.append(st((setup if first else '') + "$('%s').click(); await sleep(60); return { tag: '%s', q: '%s', marked: $('%s').classList.contains('is-on'), qs: JSON.stringify(L.S.q), colour: [chosen('col-mode'), chosen('col-trap'), chosen('col-by')].join(' | '), entry: chosen('kleinPreset') };" % (qid, tag, qn, qid), 'q/%s-%s.png' % (tag, qn), 900))
        first = False


qrow('e00-shell', "pickAt('kleinPreset', 1); await frame();")
qrow('e00-planes', "pick('col-trap', 'Planes'); pick('col-by', 'How near the orbit came, in bands');")
qrow('e00-planes-glow', "pick('col-by', 'How near it came, as a glow');")
qrow('e00-cross-step', "pick('col-trap', 'Cross'); pick('col-by', 'The step at which');")
qrow('e25-planes', "pick('col-trap', 'Planes'); pick('col-by', 'How near the orbit came, in bands'); pickAt('kleinPreset', 26); await frame();")
qrow('e25-shell', "pick('col-trap', 'Sphere shell'); pick('col-by', 'How near it came, as a glow');")
qrow('e08-shell', "pickAt('kleinPreset', 9); await frame();")
qrow('e02-shell', "pickAt('kleinPreset', 3); await frame();")
qrow('e21-shell', "pickAt('kleinPreset', 22); await frame();")
qrow('e16-where', "pickAt('kleinPreset', 17); await frame(); pick('col-by', 'Where on the trap');")
write('q', Q)


# ---------------- a: all 34 entries through the list, Frame it, Balanced
def entry(i):
    return js(r"""
const i = %d, sel = $('kleinPreset'), cam0 = camNow(), it0 = L.S.k.iter;
pickAt('kleinPreset', i + 1);
const opt = sel.options[sel.selectedIndex], p = L.KLEIN_PRESETS[i], bad = [];
for (const key of ['mx', 'my', 'mz', 'three', 'L', 'cx', 'cy', 'cz', 'invR']) if (p.k[key] !== undefined && L.S.k[key] !== p.k[key] && !(key === 'L' && !p.k.three)) bad.push(key + '=' + L.S.k[key]);
const camSame = camNow() === cam0, iterSame = L.S.k.iter === it0;
$('kleinFrame').click(); await sleep(60);
return { i, text: opt ? opt.text : '(none)', group: opt ? opt.parentNode.label || '' : '', wrong: bad, iter: L.S.k.iter, iterSame, camSame, warn: warn(), cam: camNow(), note: $('kleinNote').textContent, closedText: chosen('kleinPreset') };
""" % i)


OPEN = js(r"""
const k = L.S.k, d = $('kiter');
return { iter: k.iter, slider: d.min + '..' + d.max, box: $('kiterNum').value, extreme: !!L.S.extreme,
  quality: ['qUltra', 'qFast', 'qBal', 'qFine'].filter(id => $(id).classList.contains('is-on')).join(),
  colour: JSON.stringify(L.S.colour), k: kNow(),
  opts: [...$('kleinPreset').options].map(o => (o.parentNode.label || '-') + ' | ' + o.text + (o.disabled ? ' (disabled)' : '')) };
""")
DUMP = js("return JSON.stringify(L.KLEIN_PRESETS);")
A = [OPEN, DUMP, TOK]
for i in range(34):
    a = entry(i); a.update(shot('a/e%02d.png' % i)); A.append(a)
    A.append(js("return { i: %d, grid: grid(24, 14) };" % i))
write('a', A)

# ---------------- f: the 2D view of five entries
F = [TOK]
for i in (0, 2, 8, 21, 29):
    F.append(st("pickAt('kleinPreset', %d); await frame(); return { entry: chosen('kleinPreset') };" % (i + 1), 'f/e%02d-3d.png' % i))
    F.append(st("$('flat').click(); await sleep(200); return { flat: L.S.flat, label: $('flat').parentNode.textContent.trim(), v2: JSON.stringify(L.S.v2), cut: L.S.cut, inMode: chosen('col-inMode'), notes: notes() };", 'f/e%02d-2d.png' % i))
    F.append(js("$('flat').click(); await sleep(150); return { flat: L.S.flat };", wait='done', timeout=600))
write('f', F)

# ---------------- i: the inside colourings of the Kleinian view (flat-2)
I = []
# flat-2, the first check's own steps
I.append(st("document.getElementById('flat').click(); document.getElementById('mode-k').click(); const e = document.getElementById('col-inMode'); e.value = [...e.options].find(o => o.text.startsWith('How quickly')).value; e.dispatchEvent(new Event('change', {bubbles: true})); await sleep(300); openAll(); await sleep(100);"
            " return { inMode: chosen('col-inMode'), opts: [...$('col-inMode').options].map(o => o.text), notes: [...document.querySelectorAll('p.note')].filter(p => p.id.startsWith('col-') && !p.hidden && p.getBoundingClientRect().width > 0).map(p => p.textContent) };", 'i/flat2-repro.png'))
for n, name in enumerate(['Plain', 'Orbit trap', 'Where the orbit ends up', 'How deep inside', 'How quickly']):
    I.append(st("pick('col-inMode', '%s'); await sleep(200); return { inMode: chosen('col-inMode'), inPal: chosen('col-inPal'), notes: notes() };" % name, 'i/e00-in%d.png' % n))
# another palette inside, reversed
I.append(st("pick('col-inMode', 'How deep inside'); pick('col-inPal', 'Viridis'); await sleep(200); return { inPal: chosen('col-inPal') };", 'i/e00-in3-viridis.png'))
I.append(st("$('col-inRev').click(); await sleep(200); return { inRev: L.S.colour.inRev };", 'i/e00-in3-viridis-rev.png'))
I.append(st("pick('col-inMode', 'How quickly'); await sleep(200); return { inMode: chosen('col-inMode') };", 'i/e00-in4-viridis-rev.png'))
I.append(st("pick('col-inMode', 'Where the orbit ends up'); pick('col-inPal', 'Fire'); await sleep(200); return { inMode: chosen('col-inMode') };", 'i/e00-in2-fire-rev.png'))
I.append(st("pick('col-inMode', 'Orbit trap'); await sleep(200); return { inMode: chosen('col-inMode') };", 'i/e00-in1-fire-rev.png'))
# other entries
for i in (8, 2, 15):
    I.append(st("pickAt('kleinPreset', %d); await frame(); pick('col-inPal', 'Same as outside'); pick('col-inMode', 'How deep inside'); await sleep(200); return { entry: chosen('kleinPreset'), flat: L.S.flat };" % (i + 1), 'i/e%02d-in3.png' % i))
    I.append(st("pick('col-inMode', 'How quickly'); await sleep(200); return { notes: notes() };", 'i/e%02d-in4.png' % i))
    I.append(st("pick('col-inMode', 'Where the orbit ends up'); await sleep(200); return {};", 'i/e%02d-in2.png' % i))
    I.append(st("pick('col-inMode', 'Orbit trap'); await sleep(200); return {};", 'i/e%02d-in1.png' % i))
# the cut face in the 3D Kleinian view, coloured like the inside
I.append(st("$('flat').click(); await sleep(200); pickAt('kleinPreset', 1); await frame(); const c = $('cutOn'); const out = { cutOnExists: !!c }; if (c && !c.checked) c.click(); await sleep(300); out.cutOn = L.S.cutOn; out.cut = L.S.cut; out.faceShown = shown('col-cutFace'); return out;", 'i/cut-e00-plain.png'))
I.append(st("const f = $('col-cutFace'); if (f && !f.checked) f.click(); await sleep(200); pick('col-inMode', 'How deep inside'); await sleep(200); return { cutFace: L.S.colour.cutFace, inMode: chosen('col-inMode'), notes: notes() };", 'i/cut-e00-in3.png'))
I.append(st("pick('col-inMode', 'How quickly'); await sleep(200); return { notes: notes() };", 'i/cut-e00-in4.png'))
I.append(st("pick('col-inMode', 'Where the orbit ends up'); await sleep(200); return {};", 'i/cut-e00-in2.png'))
I.append(st("pick('col-inMode', 'Orbit trap'); await sleep(200); return {};", 'i/cut-e00-in1.png'))
write('i', I)
