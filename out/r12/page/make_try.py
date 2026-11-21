"""Round 12, page: the buttons tried by hand from several starting states.

  python out/r12/page/make_try.py  ->  out/r12/page/try-1400.json, out/r12/page/try-375.json
  then: python tools/shot.py --url dist/r12-page.html --size 1400x950 --actions out/r12/page/try-1400.json
        python tools/shot.py --url dist/r12-page.html --size 375x800  --actions out/r12/page/try-375.json
"""
import io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const camNow = () => [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => x.toFixed(4)).join();
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) if (L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11)) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } return [n, ring]; };
const where = () => 'approach ' + L.APPROACHES[L.S.approach].id + ', mode ' + L.S.mode + ', n ' + L.S.n + ', c ' + L.S.c + ', flip ' + L.S.flip + ', flat ' + L.S.flat + ', cut ' + L.S.cutOn + ', solid ' + L.S.colour.solid + ', params ' + JSON.stringify(L.S.param[L.APPROACHES[L.S.approach].id]) + ', cam ' + camNow() + ', zmax ' + L.S.view.zmax + ', bound ' + L.S.view.bound;
// as far from every button's target as the page can be: Kleinian, 2D view, a cut, modifiers, a trap solid, power 3, tight limits
const far = async () => { $('mode-k').click(); if (!L.S.flat) $('flat').click(); if (!L.S.cutOn) $('cutOn').click(); if (!$('absx').checked) $('absx').click(); if (!$('flipy').checked) $('flipy').click(); pick('col-solid', 'Is the solid'); type('powNum', '3'); L.S.view.zmax = 3; L.S.view.bound = 1.5; L.syncControls(); L.viewChanged(); await sleep(200); };
"""


def build(tag):
    steps = []

    def step(js, shot=None, wait='done'):
        a = {'js': PRE + js.strip()}
        if wait:
            a['wait'] = wait
            a['timeout'] = 240
        if shot:
            a['shot'] = 'out/r12/page/try-%s-%s.png' % (tag, shot)
            a['clip'] = '#stage'
        steps.append(a)

    step("L.R.warmOn = false; L.S.q.aa = 3; L.touch(); return 'opening state: ' + where();")
    # --- the two new buttons, each from the opening state and from the far state
    step("$('tiltShow').click(); await sleep(400); return 'Show the twisted quaternion square, from the opening state: ' + where();", 'tilt-from-opening')
    step("const g = grid(); await far(); $('quatShow').click(); await sleep(400); return 'twisted solid: ' + g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring. Show the quaternion square, from the far state: ' + where();", 'quat-from-far')
    step("const g = grid(); type('par-lathe-spinNum', '3'); type('par-tilt-tiltNum', '-120'); $('ap-bulb').click(); $('mode-j').click(); await sleep(200); $('quatShow').click(); await sleep(400); return 'quaternion solid: ' + g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring. Show the quaternion square, from Julia + Mandelbulb with spin 3: ' + where();", 'quat-from-julia')
    step("const g = grid(); await far(); $('tiltShow').click(); await sleep(400); return 'quaternion solid again: ' + g[0] + ' / ' + g[1] + '. Show the twisted quaternion square, from the far state with tilt -120: ' + where();", 'tilt-from-far')
    # --- Show Figure 4: from the twisted Mandelbrot solid, and from the far state with the two-planes dials moved
    step("const g = grid(); $('fig4Show').click(); await sleep(400); return 'twisted solid again: ' + g[0] + ' / ' + g[1] + '. Show Figure 4, from the twisted Mandelbrot solid: ' + where();", 'fig4-from-tilt')
    step("const g = grid(); type('par-fold-planesNum', '5'); type('par-fold-liftNum', '0.4'); type('par-mercator-turnNum', '30'); $('ap-classic').click(); await far(); $('fig4Show').click(); await sleep(400); return 'Figure 4: ' + g[0] + ' / ' + g[1] + '. Show Figure 4, from the far state with Planes 5, Lift 0.4: ' + where() + ', one-plane dials ' + JSON.stringify(L.S.param.mercator);", 'fig4-from-far')
    # --- Back to one plane: from Figure 4, and from the Kleinian view with another approach
    step("const g = grid(), view = camNow(); $('fig4Back').click(); await sleep(400); return 'Figure 4 again: ' + g[0] + ' / ' + g[1] + '. Back to one plane, from Figure 4: ' + where() + ', camera kept: ' + (camNow() === view) + ', two-planes dials ' + JSON.stringify(L.S.param.fold);", 'oneplane-from-fig4')
    step("$('ap-tilt').click(); $('mode-k').click(); await sleep(200); $('fig4Back').click(); await sleep(400); return 'Back to one plane, from the Kleinian view with the twisted square chosen: ' + where();", 'oneplane-from-klein')
    # --- As it was found, from three states
    step(r"""
const out = [], f = $('juliaFound'), say = t => out.push(t + ': button ' + (shown('juliaFound') ? '"' + f.textContent + '" (' + f.title + ')' : 'not on show'));
type('par-mercator-turnNum', '0'); pick('juliaPreset', 'Cracked Basilica'); await sleep(200);
say('one plane in use, Cracked Basilica (found with two planes)');
const view = camNow(); f.click(); await sleep(300);
out.push('after the click: ' + where() + ', camera kept: ' + (camNow() === view));
say('then');
type('par-fold-planesNum', '4'); await sleep(200);
say('two planes in use with Planes at 4');
f.click(); await sleep(300);
out.push('after the click: ' + JSON.stringify(L.S.param.fold));
pick('juliaPreset', 'Dendrite'); await sleep(200);
say('two planes in use, Dendrite (found with one plane)');
f.click(); await sleep(300);
out.push('after the click: ' + where());
say('then');
pick('juliaPreset', 'Douady rabbit'); $('ap-fold').click(); await sleep(200);
say('two planes in use, Douady rabbit (one plane, 24 iterations)');
f.click(); await sleep(300);
out.push('after the click: iterations ' + L.S.iter + ', ' + where());
$('ap-lathe').click(); pick('juliaPreset', 'Cracked Basilica'); await sleep(200);
say('Quaternion square in use, Cracked Basilica');
type('iterNum', '14'); pick('juliaPreset', 'Douady rabbit'); await sleep(200);
say('Quaternion square in use, Douady rabbit, 14 iterations');
return out.join(' || ');
""", 'found')
    step("$('ap-mercator').click(); pick('juliaPreset', 'Cracked Basilica'); await sleep(200); const r = $('juliaFound').closest('.pick-row').getBoundingClientRect(), b = $('juliaFound').getBoundingClientRect(); $('juliaPanel').scrollIntoView({ block: 'start' }); window.scrollBy(0, -100); await sleep(300); return 'button ' + Math.round(b.width) + ' wide in a row ' + Math.round(r.width) + ' wide, page width ' + document.documentElement.scrollWidth + ' of ' + innerWidth;", None)
    steps.append({'js': "return 'the Julia panel';", 'shot': 'out/r12/page/try-%s-julia-panel.png' % tag, 'clip': '#juliaPanel'})
    path = os.path.join(ROOT, 'out', 'r12', 'page', 'try-%s.json' % tag)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(steps, f, indent=1, ensure_ascii=False)
    print('%d steps -> %s' % (len(steps), os.path.relpath(path, ROOT)))


build('1400')
build('375')
