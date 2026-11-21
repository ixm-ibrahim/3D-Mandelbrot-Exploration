"""Round 12, checker of the page: action files for tools/shot.py. Run from the project root.

  python out/r12/check-page/make_checks.py
  -> out/r12/check-page/list-1400.json, list-375.json, buttons.json, regress.json
"""
import io, json, os

OUT = 'out/r12/check-page/'
IDS = ['mercator', 'fold', 'lathe', 'tilt', 'bulb', 'classic', 'split', 'softfold', 'axisbulb', 'pillow']

PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id); if (!e) fail('no list ' + id); const o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const chosen = id => { const e = $(id); return e && e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : ''; };
const apId = () => L.APPROACHES[L.S.approach].id;
const camNow = () => [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => x.toFixed(4)).join();
const settle = async () => { await sleep(250); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 100000) throw new Error('the picture was not finished after 100 s'); await sleep(50); } };
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = ''; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) s += L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11) ? '1' : '0'; return s; };
const gs = s => { let n = 0, ring = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) if (s[i * 11 + j] === '1') { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } return n + ' of 165 probes hit, ' + ring + ' on the outer ring'; };
const where = () => 'approach ' + apId() + ' (radio ' + ((document.querySelector('#rules input[type=radio]:checked') || {}).id) + ', marked ' + [...document.querySelectorAll('#rules .rule.is-on')].map(e => e.dataset.ap).join('+') + '), mode ' + L.S.mode + ', n ' + L.S.n + ', c ' + L.S.c + ', flip ' + L.S.flip + ', 2D ' + L.S.flat + ', cut ' + L.S.cutOn + ', abs ' + L.S.abs + ', trap solid ' + L.S.colour.solid + ', iter ' + L.S.iter + ', dials ' + JSON.stringify(L.S.param[apId()]) + ', cam ' + camNow() + ', far limit ' + L.S.view.zmax + ', radius ' + L.S.view.bound + ', Julia list "' + chosen('juliaPreset') + '"';
const desc = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : '') + ' "' + (e.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40) + '"';
// layout of the Approach section: things outside the section, cut-off text, text boxes lying over one another
const layout = () => {
  const out = [], sec = $('secApproach').getBoundingClientRect();
  const vis = [...document.querySelectorAll('#secApproach *')].filter(e => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e); return r.width > 1 && r.height > 1 && cs.visibility !== 'hidden' && cs.opacity !== '0'; });
  for (const e of vis) {
    const r = e.getBoundingClientRect();
    if (r.right > sec.right + 1 || r.left < sec.left - 1) out.push('outside the section: ' + desc(e) + ' ' + Math.round(r.left) + '..' + Math.round(r.right) + ' against ' + Math.round(sec.left) + '..' + Math.round(sec.right));
    if (!['SELECT', 'INPUT'].includes(e.tagName) && e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflowX !== 'visible') out.push('cut off sideways: ' + desc(e) + ' ' + e.scrollWidth + ' in ' + e.clientWidth);
  }
  const leaf = vis.filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || ['SELECT', 'INPUT', 'BUTTON'].includes(e.tagName));
  for (let i = 0; i < leaf.length; i++) for (let j = i + 1; j < leaf.length; j++) {
    const a = leaf[i], b = leaf[j]; if (a.contains(b) || b.contains(a)) continue;
    const p = a.getBoundingClientRect(), q = b.getBoundingClientRect();
    const w = Math.min(p.right, q.right) - Math.max(p.left, q.left), h = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top);
    if (w > 2 && h > 2) out.push('over one another: ' + desc(a) + ' and ' + desc(b) + ' by ' + Math.round(w) + ' x ' + Math.round(h));
  }
  if (document.documentElement.scrollWidth > innerWidth + 1) out.push('the page is wider than the window: ' + document.documentElement.scrollWidth + ' of ' + innerWidth);
  return out;
};
"""


def writer(name):
    steps = []

    def step(js, shot=None, clip='#stage', wait=None, timeout=240):
        a = {'js': PRE + js.strip()}
        if wait:
            a['wait'] = wait
            a['timeout'] = timeout
        if shot:
            a['shot'] = OUT + shot + '.png'
            if clip:
                a['clip'] = clip
        steps.append(a)

    def done():
        with io.open(OUT + name + '.json', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(steps, f, indent=1, ensure_ascii=False)
        print('%d steps -> %s%s.json' % (len(steps), OUT, name))
    return step, done


# ------------------------------------------------------------------ the list
def build_list(tag):
    step, done = writer('list-' + tag)
    step(r"""
await settle();
const groups = L.APPROACH_GROUPS, A = L.APPROACHES, bad = [];
const rows = [...document.querySelectorAll('#rules .rule-group-head, #rules .rule')].map(e => e.classList.contains('rule') ? e.dataset.ap + ' [' + e.querySelector('.name').textContent + ' | ' + e.querySelector('.tag').textContent + ']' : 'HEADING ' + e.textContent);
for (const r of document.querySelectorAll('#rules .rule')) { const a = A.find(x => x.id === r.dataset.ap), g = r.closest('.rule-group'), h = g && g.querySelector('.rule-group-head'), want = groups.find(x => x.id === a.group); if (!h || !want || h.textContent !== want.title) bad.push(a.id + ' stands under ' + (h ? h.textContent : 'no heading') + ', should be ' + (want ? want.title : a.group)); }
const heads = [...document.querySelectorAll('#rules .rule-group-head')].map(h => h.textContent).join(' | ');
const order = groups.filter(g => A.some(a => a.group === g.id)).map(g => g.title).join(' | ');
if (heads !== order) bad.push('headings read ' + heads + ', APPROACH_GROUPS gives ' + order);
const hs = [...document.querySelectorAll('#rules .rule-group-head')].map(h => { const cs = getComputedStyle(h), r = h.getBoundingClientRect(); return h.tagName + ' ' + cs.fontSize + ' ' + cs.fontWeight + ' ' + cs.textTransform + ' h' + Math.round(r.height); }).join('; ');
return { window: innerWidth + 'x' + innerHeight, sectionOpen: $('secApproach').open, rows, wrong: bad, headingStyle: hs, layout: layout(), sectionHeight: Math.round($('secApproach').getBoundingClientRect().height) };
""", 'list-%s-0-opening' % tag, clip='#secApproach')
    for i, id_ in enumerate(IDS):
        step(r"""
const id = '__ID__', a = L.APPROACHES.find(x => x.id === id);
window.chk = window.chk || {};
const lab = document.querySelector('.rule[data-ap="' + id + '"] .rule-head'); lab.scrollIntoView({ block: 'center' }); await sleep(100);
lab.click(); const t0 = performance.now(); await settle(); const took = ((performance.now() - t0) / 1000).toFixed(1);
const rule = document.querySelector('.rule[data-ap="' + id + '"]'), body = rule.querySelector('.rule-body');
const g = grid(); window.chk[id] = g;
const ctl = [...rule.querySelectorAll('#pd-' + id + ' label')].filter(e => e.getBoundingClientRect().height > 0).map(e => e.textContent.replace(/\s+/g, ' ').trim());
const missing = (a.params || []).filter(s => s.key !== undefined && !(($('par-' + id + '-' + s.key) || {}).getBoundingClientRect && $('par-' + id + '-' + s.key).getBoundingClientRect().height > 0)).map(s => s.label || s.key);
const open = [...document.querySelectorAll('#rules .rule')].filter(r => r.querySelector('.rule-body').getBoundingClientRect().height > 0).map(r => r.dataset.ap);
return { id, chosen: apId(), radio: $('ap-' + id).checked, marked: [...document.querySelectorAll('#rules .rule.is-on')].map(e => e.dataset.ap), bodiesOpen: open, seconds: took, picture: gs(g),
  formula: $('f-' + id).textContent.replace(/\s+/g, ' ').slice(0, 90), note: (body.querySelector('p.note') || {}).textContent ? body.querySelector('p.note').textContent.slice(0, 70) : '(none)',
  controls: ctl, dialsNotOnShow: missing, ruleHeight: Math.round(rule.getBoundingClientRect().height), layout: layout(), status: $('status').textContent.slice(0, 80) };
""".replace('__ID__', id_), 'list-%s-%d-%s' % (tag, i + 1, id_), clip='#secApproach')
        if tag == '1400':
            step("return 'picture of __ID__';".replace('__ID__', id_), 'stage-%d-%s' % (i + 1, id_), clip='#stage')
    step(r"""
const ids = Object.keys(window.chk), same = [];
for (let i = 0; i < ids.length; i++) for (let j = i + 1; j < ids.length; j++) if (window.chk[ids[i]] === window.chk[ids[j]]) same.push(ids[i] + ' = ' + ids[j]);
const diff = (a, b) => { let n = 0; for (let k = 0; k < a.length; k++) if (a[k] !== b[k]) n++; return n; };
const steps = ids.slice(1).map((id, k) => ids[k] + '>' + id + ' ' + diff(window.chk[ids[k]], window.chk[id]));
return { entriesDrawn: ids.length, samePictureByProbes: same, probesThatChangedFromOneEntryToTheNext: steps };
""")
    done()


# ------------------------------------------------------------------ the buttons
def build_buttons():
    step, done = writer('buttons')
    FIG = r"""
const fig = async from => { const before = where(); $('fig4Show').click(); await settle(); const g = grid(); window.figGrid = g; const S = L.S, bad = [];
  if (apId() !== 'fold' || !$('ap-fold').checked) bad.push('approach ' + apId()); if (S.mode !== 'j') bad.push('mode ' + S.mode); if (S.c.join() !== '-1,0,0') bad.push('c ' + S.c);
  if (S.param.fold.planes !== 2 || S.param.fold.lift !== 0 || $('par-fold-planesNum').value !== '2') bad.push('dials ' + JSON.stringify(S.param.fold)); if (S.n !== 2) bad.push('power ' + S.n);
  if (S.flat || S.cutOn || S.colour.solid !== 0 || S.abs.join() !== '0,0,0') bad.push('2D view, cut, trap solid or modifier still on');
  if (S.flip.join() !== '0,0') bad.push('flip ' + S.flip);
  if ($('juliaPanel').hidden || $('secApproach').hidden) bad.push('a panel is put away');
  const r = $('stage').getBoundingClientRect(); if (r.bottom <= 0 || r.top >= innerHeight) bad.push('picture out of view');
  return { from, before, after: where(), picture: gs(g), wrong: bad }; };
"""
    step("await settle(); window.open0 = JSON.stringify(L.S); window.cam0 = camNow(); return 'opening state: ' + where();")
    # 1 Mandelbrot under another entry
    step(FIG + "$('ap-bulb').click(); await settle(); return await fig('the Mandelbrot solid of the Mandelbulb');", 'fig4-1-from-mandel-bulb')
    step(r"""
const view = camNow(), dials = JSON.stringify(L.S.param), fg = window.figGrid; $('fig4Back').click(); await settle(); const g = grid(); let d = 0; for (let k = 0; k < g.length; k++) if (g[k] !== fg[k]) d++;
return { after: where(), cameraKept: camNow() === view, dialsKept: JSON.stringify(L.S.param) === dials, picture: gs(g), probesDifferentFromFigure4: d };
""", 'back-1-after-fig4')
    # 2 the Kleinian view
    step(FIG + "$('mode-k').click(); await settle(); return await fig('the Kleinian view');", 'fig4-2-from-kleinian')
    # 3 the 2D view (Mandelbrot under the quaternion square)
    step(FIG + "$('resetAll').click(); await sleep(200); $('ap-lathe').click(); $('flat').click(); await settle(); const was = where(); const r = await fig('the 2D view of the Mandelbrot set under the quaternion square'); return r;", 'fig4-3-from-2d')
    # 4 a trap solid on show
    step(FIG + "$('resetAll').click(); await sleep(200); pick('col-solid', 'Is the solid'); await settle(); return await fig('a trap solid on show (Mandelbrot, one plane)');", 'fig4-4-from-trap-solid')
    # 5 a tried entry, Julia rabbit, the two-planes dials moved, flip z ticked
    step(FIG + "$('resetAll').click(); await sleep(200); $('ap-fold').click(); type('par-fold-planesNum', '5'); type('par-fold-liftNum', '0.4'); $('ap-pillow').click(); $('mode-j').click(); pick('juliaPreset', 'Douady rabbit'); $('flipz').click(); await settle(); return await fig('the Julia rabbit under Pillow with flip z ticked and Planes at 5');", 'fig4-5-from-pillow-rabbit')
    step(r"""
const view = camNow(), dials = JSON.stringify(L.S.param); $('fig4Back').click(); await settle();
const a = { after: where(), cameraKept: camNow() === view, dialsKept: JSON.stringify(L.S.param) === dials };
$('mode-k').click(); $('ap-softfold') && 0; await settle(); $('fig4Back').click(); await settle(); a.fromKleinian = where(); return a;
""", 'back-2')
    # the two new buttons
    step(r"""
$('ap-fold').click(); $('flat').click(); $('flipz').click(); type('par-tilt-tiltNum', '-100'); type('powNum', '3'); await settle(); const before = where();
$('tiltShow').click(); await settle(); const g = grid();
return { button: $('tiltShow').textContent, before, after: where(), tilt: L.S.param.tilt, tiltBox: $('par-tilt-tiltNum').value, picture: gs(g) };
""", 'new-1-twisted-from-2d-fold')
    step(r"""
$('mode-k').click(); pick('col-solid', 'Is the solid'); type('par-lathe-spinNum', '3'); await settle(); const before = where();
$('quatShow').click(); await settle(); const g = grid();
return { button: $('quatShow').textContent, before, after: where(), spin: L.S.param.lathe, spinBox: $('par-lathe-spinNum').value, picture: gs(g) };
""", 'new-2-quaternion-from-kleinian-trap')
    step(r"""
$('mode-j').click(); $('ap-axisbulb').click(); $('cutOn').click(); await settle(); const before = where();
$('tiltShow').click(); await settle(); const g = grid();
return { before, after: where(), picture: gs(g) };
""", 'new-3-twisted-from-julia-tried-cut')
    # the twin buttons and Back to the plain rule
    TW = r"""
const twin = async (btn, id) => { const before = where(); $(btn).click(); await settle(); const g = grid(), S = L.S, bad = [];
  if (apId() !== id || !$('ap-' + id).checked) bad.push('approach ' + apId()); if (S.mode !== 'm') bad.push('mode ' + S.mode); if (S.flip.join() !== '0,1' || !$('flipz').checked) bad.push('flip ' + S.flip);
  if (S.n !== 2 || S.flat || S.cutOn || S.colour.solid !== 0 || S.abs.join() !== '0,0,0') bad.push('power, 2D view, cut, trap solid or modifier');
  for (const s of L.APPROACHES.find(x => x.id === id).params || []) if (s.key !== undefined && s.def !== undefined && S.param[id][s.key] !== s.def) bad.push(s.label + ' at ' + S.param[id][s.key]);
  return { button: $(btn).textContent, before, after: where(), picture: gs(g), wrong: bad }; };
"""
    step(TW + "$('mode-j').click(); $('ap-tilt').click(); type('par-mercator-turnNum', '25'); $('flat').click(); await settle(); return await twin('twinMerc', 'mercator');", 'twin-1-inversions')
    step(TW + "$('mode-k').click(); type('par-lathe-spinNum', '3'); await settle(); return await twin('twinLathe', 'lathe');", 'twin-2-lathe')
    step(TW + "$('ap-softfold').click(); pick('col-solid', 'Is the solid'); type('powNum', '4'); await settle(); return await twin('twinBulb', 'bulb');", 'twin-3-mandelbulb')
    step(r"""
const view = camNow(), ap = apId(), dials = JSON.stringify(L.S.param); $('twinOff').click(); await settle();
return { button: $('twinOff').textContent, after: where(), flipzBox: $('flipz').checked, approachKept: apId() === ap, cameraKept: camNow() === view, dialsKept: JSON.stringify(L.S.param) === dials, picture: gs(grid()) };
""", 'twin-4-back-to-plain')
    # the twin of the Lathe against the twisted square at tilt 180 (the closing text says they are the same)
    step(r"""
$('twinLathe').click(); await settle(); const a = grid(); const view = { yaw: L.cam.yaw, pitch: L.cam.pitch, dist: L.cam.dist };
$('twinOff').click(); $('ap-tilt').click(); type('par-tilt-tiltNum', '180'); await settle(); const b = grid(); let d = 0; for (let k = 0; k < a.length; k++) if (a[k] !== b[k]) d++;
return { twinOfLathe: gs(a), twistedAt180: gs(b), probesThatDiffer: d, sameCamera: camNow() };
""", 'twin-5-twisted-at-180')
    # As it was found
    step(r"""
$('resetAll').click(); await sleep(300); $('mode-j').click(); await settle();
const f = $('juliaFound'), out = [], say = t => out.push(t + ' -> ' + (shown('juliaFound') ? 'button "' + f.textContent + '" (title: ' + f.title + ')' : 'button not on show'));
out.push('start: ' + where());
pick('juliaPreset', 'Cracked Basilica'); await settle(); say('one plane, Cracked Basilica'); out.push('note: ' + $('juliaNote').textContent);
const v = camNow(), c = L.S.c.join(); f.click(); await settle(); out.push('after click: ' + where() + '; camera kept ' + (camNow() === v) + ', c kept ' + (L.S.c.join() === c)); say('then');
window.found1 = grid();
return out;
""", 'found-1-cracked-from-one-plane')
    step(r"""
const f = $('juliaFound'), out = [], say = t => out.push(t + ' -> ' + (shown('juliaFound') ? 'button "' + f.textContent + '" (title: ' + f.title + ')' : 'button not on show'));
pick('juliaPreset', 'Basilica'); await sleep(200); pick('juliaPreset', 'Cracked Basilica'); await settle(); say('two planes (Planes 2), Cracked Basilica picked again');
type('par-fold-planesNum', '4'); await settle(); say('two planes with Planes at 4, Cracked Basilica');
f.click(); await settle(); out.push('after click: ' + where()); say('then');
return out;
""", 'found-2-cracked-from-two-planes')
    step(r"""
const f = $('juliaFound'), out = [], say = t => out.push(t + ' -> ' + (shown('juliaFound') ? 'button "' + f.textContent + '" (title: ' + f.title + ')' : 'button not on show'));
$('ap-mercator').click(); pick('juliaPreset', 'Douady rabbit'); await settle(); say('one plane, Douady rabbit, iterations ' + L.S.iter); out.push('note: ' + $('juliaNote').textContent);
if (shown('juliaFound')) { f.click(); await settle(); out.push('after click: ' + where()); say('then'); }
return out;
""", 'found-3-rabbit-from-one-plane')
    step(r"""
const f = $('juliaFound'), out = [], say = t => out.push(t + ' -> ' + (shown('juliaFound') ? 'button "' + f.textContent + '" (title: ' + f.title + ')' : 'button not on show'));
$('ap-fold').click(); await settle(); say('two planes, Douady rabbit, iterations ' + L.S.iter);
type('iterNum', '14'); await settle(); say('two planes, Douady rabbit, iterations ' + L.S.iter);
const v = camNow(); f.click(); await settle(); out.push('after click: ' + where() + '; camera kept ' + (camNow() === v)); say('then');
const row = f.closest('.pick-row'); out.push('row of the Julia list: ' + [...row.children].filter(e => e.getBoundingClientRect().width > 0).map(e => e.tagName + ' ' + Math.round(e.getBoundingClientRect().left) + '..' + Math.round(e.getBoundingClientRect().right)).join(', '));
return out;
""", 'found-4-rabbit-from-two-planes')
    # Approach reset and Reset everything
    step(r"""
const A = L.APPROACHES, out = [];
$('ap-fold').click(); type('par-fold-planesNum', '5'); type('par-fold-liftNum', '0.3'); type('par-tilt-tiltNum', '-100'); type('par-lathe-spinNum', '3'); type('par-mercator-turnNum', '33');
const set = (id, v) => { const e = $(id); if (!e) { out.push('no control ' + id); return; } e.value = v; e.dispatchEvent(new Event(e.tagName === 'SELECT' ? 'change' : 'input', { bubbles: true })); if (e.tagName !== 'SELECT') e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
$('ap-softfold').click(); await sleep(100); set('par-softfold-planesNum', '3'); set('par-softfold-blendNum', '0.4'); set('par-softfold-curve', $('par-softfold-curve').options[1].value); set('par-softfold-mix', $('par-softfold-mix').options[2].value);
$('ap-axisbulb').click(); await sleep(100); set('par-axisbulb-kNum', '5'); set('par-axisbulb-wobNum', '0.5');
$('ap-pillow').click(); await sleep(100); set('par-pillow-layout', $('par-pillow-layout').options[1].value); await settle();
out.push('before the Approach reset: ' + apId() + ' ' + JSON.stringify(L.S.param));
const view = camNow(), mode = L.S.mode, c = L.S.c.join(), it = L.S.iter;
document.querySelector('#approachReset .dial-reset').click(); await settle();
out.push('after: ' + apId() + ' ' + JSON.stringify(L.S.param));
const bad = [];
if (L.S.approach !== 0 || !$('ap-mercator').checked) bad.push('approach ' + apId());
for (const a of A) for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined) { if (L.S.param[a.id][s.key] !== s.def) bad.push(a.id + '.' + s.key + ' = ' + L.S.param[a.id][s.key] + ', should be ' + s.def); const e = $('par-' + a.id + '-' + s.key + 'Num') || $('par-' + a.id + '-' + s.key); if (e && e.type !== 'checkbox' && String(e.value) !== String(s.def)) bad.push('control of ' + a.id + '.' + s.key + ' shows ' + e.value + ', should show ' + s.def); }
out.push('camera kept ' + (camNow() === view) + ', mode kept ' + (L.S.mode === mode) + ', c kept ' + (L.S.c.join() === c) + ', iterations kept ' + (L.S.iter === it));
out.push(bad.length ? 'WRONG after the Approach reset: ' + bad.join('; ') : 'every approach dial and its control are back at the start');
return out;
""", 'reset-1-approach')
    step(r"""
const A = L.APPROACHES, out = [];
const set = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event(e.tagName === 'SELECT' ? 'change' : 'input', { bubbles: true })); if (e.tagName !== 'SELECT') e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
type('par-fold-planesNum', '6'); type('par-tilt-tiltNum', '77'); $('ap-softfold').click(); await sleep(100); set('par-softfold-mix', $('par-softfold-mix').options[1].value); $('ap-pillow').click(); await sleep(100); set('par-pillow-layout', $('par-pillow-layout').options[1].value);
$('mode-k').click(); $('flat').click(); $('flipz').click(); pick('col-solid', 'Is the solid'); type('powNum', '5'); type('iterNum', '30'); L.cam.yaw += 1; L.touch(); await settle();
out.push('before Reset everything: ' + where());
$('resetAll').click(); await settle();
out.push('after: ' + where());
const now = JSON.stringify(L.S); out.push('state equals the opening state: ' + (now === window.open0) + ', camera equals the opening camera: ' + (camNow() === window.cam0));
if (now !== window.open0) { const a = JSON.parse(window.open0), b = JSON.parse(now), d = []; const walk = (x, y, p) => { if (x && y && typeof x === 'object' && typeof y === 'object') { for (const k of new Set([...Object.keys(x), ...Object.keys(y)])) walk(x[k], y[k], p + '.' + k); } else if (JSON.stringify(x) !== JSON.stringify(y)) d.push(p + ': ' + JSON.stringify(x) + ' -> ' + JSON.stringify(y)); }; walk(a, b, 'S'); out.push('differences: ' + d.slice(0, 20).join('; ')); }
const bad = []; for (const a of A) for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined) { const e = $('par-' + a.id + '-' + s.key + 'Num') || $('par-' + a.id + '-' + s.key); if (e && e.type !== 'checkbox' && String(e.value) !== String(s.def)) bad.push('control of ' + a.id + '.' + s.key + ' shows ' + e.value); }
out.push(bad.length ? 'WRONG controls: ' + bad.join('; ') : 'every approach control shows its starting value');
return out;
""", 'reset-2-everything')
    done()


# ------------------------------------------------------------------ regressions and the words on the page
def build_regress():
    step, done = writer('regress')
    step("await settle(); return 'opening: ' + where();")
    step(r"""
const out = []; const ex = $('trapExamples'); out.push('Examples list: ' + [...ex.querySelectorAll('optgroup')].map(g => g.label + ' (' + g.children.length + ')').join(', '));
const e = L.EXAMPLES[0]; pick('trapExamples', e.name); await settle(); const g = grid(); out.push(e.name + ': ' + where() + '; ' + gs(g)); return out;
""", 'reg-1-trap-example-mandelbrot')
    step(r"""
const out = []; const e = L.EXAMPLES.find(x => x.mode === 'j') || L.EXAMPLES[3]; pick('trapExamples', e.name); await settle(); const g = grid(); out.push(e.name + ': ' + where() + '; ' + gs(g)); return out;
""", 'reg-2-trap-example-julia')
    step(r"""
const out = []; const e = L.EXAMPLES.find(x => x.mode === 'k') || L.EXAMPLES[6]; pick('trapExamples', e.name); await settle(); const g = grid(); out.push(e.name + ': ' + where() + '; Kleinian list "' + chosen('kleinPreset') + '"; ' + gs(g)); return out;
""", 'reg-3-trap-example-kleinian')
    step(r"""
$('resetAll').click(); await sleep(300); $('mode-j').click(); await settle(); const a = grid();
pick('juliaPreset', 'Douady rabbit'); await settle(); const b = grid(); let d = 0; for (let k = 0; k < a.length; k++) if (a[k] !== b[k]) d++;
return 'Julia list, Douady rabbit: c ' + L.S.c + ', note "' + $('juliaNote').textContent.slice(0, 120) + '"; ' + gs(b) + '; ' + d + ' probes differ from the Basilica';
""", 'reg-4-julia-entry')
    step(r"""
$('mode-k').click(); await settle(); const a = grid(); const names = [...$('kleinPreset').options].map(o => o.text);
pick('kleinPreset', names[5]); await settle(); const b = grid(); let d = 0; for (let k = 0; k < a.length; k++) if (a[k] !== b[k]) d++;
return 'Kleinian list (' + names.length + ' entries), entry "' + names[5] + '": note "' + $('kleinNote').textContent.slice(0, 120) + '"; Approach section put away: ' + $('secApproach').hidden + '; ' + gs(b) + '; ' + d + ' probes differ from the first entry';
""", 'reg-5-kleinian-entry')
    step(r"""
$('mode-m').click(); $('flat').click(); await settle();
return '2D view of the Mandelbrot set: 2D ' + L.S.flat + ', ' + gs(grid()) + ', status "' + $('status').textContent.slice(0, 80) + '"';
""", 'reg-6-2d-view')
    step(r"""
$('ap-pillow').click(); await settle(); const a = gs(grid()); return '2D view under Pillow (a tried entry): ' + a;
""", 'reg-7-2d-view-pillow')
    step(r"""
$('flat').click(); $('ap-mercator').click(); await settle();
window.chkFiles = []; window.squaringLabSaveHook = (name, blob) => { window.chkFiles.push({ name, size: blob.size, type: blob.type }); };
const panel = $('exportPanel'), start = [...panel.querySelectorAll('button')].find(b => /^start/i.test(b.textContent.trim()));
if (!start) fail('the picture panel has no Start button');
const sel = [...panel.querySelectorAll('select')].find(s => [...s.options].some(o => /typed|own size|custom/i.test(o.text)));
if (sel) { const o = [...sel.options].find(x => /typed|own size|custom/i.test(x.text)); sel.value = o.value; sel.dispatchEvent(new Event('change', { bubbles: true })); await sleep(100);
  const box = word => { const d = [...panel.querySelectorAll('.dial')].find(e => !e.hidden && e.querySelector('label') && new RegExp(word, 'i').test(e.querySelector('label').textContent)); return d && d.querySelector('input.num'); };
  const w = box('width'), h = box('height'); if (w && h) for (const e of [w, h]) { e.value = '256'; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); } }
start.click(); await sleep(400);
return 'picture job started with "' + start.textContent.trim() + '": busy ' + L.exportBusy() + ', step line "' + ($('exportStep') ? $('exportStep').textContent : '') + '"';
""", wait='!window.squaringLab.exportBusy()', timeout=300)
    step(r"""
const panel = $('exportPanel'), save = [...panel.querySelectorAll('button')].find(b => /^save the file/i.test(b.textContent.trim()) && b.getBoundingClientRect().width > 0);
const msg = $('exportMsg') ? $('exportMsg').textContent : '';
if (save) { save.click(); await sleep(600); }
return 'picture job ended: message "' + msg + '", facts "' + ($('exportFacts') ? $('exportFacts').textContent.replace(/\s+/g, ' ').slice(0, 160) : '') + '", Save the file on show: ' + !!save + ', file handed over: ' + JSON.stringify(window.chkFiles);
""", 'reg-8-export-panel', clip='#secExport')
    # the words: every title, label, note and help text, in every state of the lists
    step(r"""
$('resetAll').click(); await sleep(300);
document.querySelectorAll('details').forEach(d => { d.open = true; });
const texts = new Map(); const add = (wh, t) => { t = (t || '').replace(/\s+/g, ' ').trim(); if (t && !texts.has(t)) texts.set(t, wh); };
const sweep = tag => { document.querySelectorAll('[title]').forEach(e => add(tag + ' title of ' + desc(e).slice(0, 50), e.title)); document.querySelectorAll('[aria-label]').forEach(e => add(tag + ' aria-label of ' + (e.id || e.tagName), e.getAttribute('aria-label')));
  document.querySelectorAll('p, li, label, button, option, optgroup, summary, h1, h2, h3, code, dt, dd, legend, figcaption, td, th').forEach(e => add(tag + ' ' + desc(e).slice(0, 40), e.tagName === 'OPTGROUP' ? e.label : e.textContent)); };
for (const mode of ['m', 'j', 'k']) { $('mode-' + mode).click(); await sleep(150); sweep('mode ' + mode); }
$('mode-j').click(); await sleep(100);
for (const a of L.APPROACHES) { $('ap-' + a.id).click(); await sleep(120); sweep('approach ' + a.id); for (const s of a.params || []) { const e = s.key !== undefined && $('par-' + a.id + '-' + s.key); if (e && e.tagName === 'SELECT') for (const o of e.options) { e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); await sleep(120); sweep('approach ' + a.id + ' ' + s.key + '=' + o.text.slice(0, 20)); } } }
$('resetAll').click(); await sleep(200); $('mode-j').click(); await sleep(100);
for (const ap of ['mercator', 'fold', 'lathe']) { $('ap-' + ap).click(); for (const o of $('juliaPreset').options) { $('juliaPreset').value = o.value; $('juliaPreset').dispatchEvent(new Event('change', { bubbles: true })); await sleep(60); add('Julia note of ' + o.text + ' under ' + ap, $('juliaNote').textContent); if (shown('juliaFound')) { add('As it was found, ' + o.text + ' under ' + ap, $('juliaFound').textContent); add('As it was found title, ' + o.text + ' under ' + ap, $('juliaFound').title); } } }
$('mode-k').click(); await sleep(100);
for (const o of $('kleinPreset').options) { $('kleinPreset').value = o.value; $('kleinPreset').dispatchEvent(new Event('change', { bubbles: true })); await sleep(40); add('Kleinian note of ' + o.text, $('kleinNote').textContent); }
$('resetAll').click(); await sleep(300);
const tests = [['Planes with a setting of 1', /Planes?\s*(dial\s*)?(at|to|=|is|of|set to)?\s*1\b(?!\s*(and|,)\s*2)/], ['Planes at 1', /Planes at 1\b/i], ['one-plane setting of a dial', /Planes dial[^.]*\b(1|one)\b/i], ['Lathe not as Quaternion square (Lathe)', /(?<!Quaternion square \()Lathe/], ['em dash', /—/], ['internal name', /\b(mercator|softfold|axisbulb|pillowboth|pillowsmooth|uA|S\.param|GL_[A-Z]+|par-[a-z]+)\b/], ['Mercator as a name', /Mercator approach|the Mercator\b(?! map)/]];
const hits = []; for (const [t, wh] of texts) for (const [name, re] of tests) if (re.test(t)) { const m = t.match(re); hits.push(name + ' | ' + wh + ' | ...' + t.slice(Math.max(0, m.index - 70), m.index + 90) + '...'); }
window.allTexts = [...texts].map(([t, wh]) => wh + ' :: ' + t);
return { texts: texts.size, hits };
""")
    step(r"""
const T = window.allTexts; const pickOut = re => T.filter(x => re.test(x)).map(x => x.slice(0, 420));
return { approachTitles: pickOut(/title of .*(ap-|par-|rule|fig4|twin|quat|tilt|juliaFound)/).slice(0, 40), triedNote: $('triedNote').textContent, lede: document.querySelector('.lede').textContent.replace(/\s+/g, ' ') };
""")
    done()


build_list('1400')
build_list('375')
build_buttons()
build_regress()
