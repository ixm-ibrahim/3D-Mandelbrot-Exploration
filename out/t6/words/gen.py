"""Step files of tester "words". python out/t6/words/gen.py  writes out/t6/words/steps-*.json
Run each with:  PYTHONIOENCODING=utf-8 python tools/shot.py --url dist/v6.html --actions out/t6/words/steps-<name>.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
D = 'out/t6/words/'
PRE = r"""
const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const sel = id => { const e = $(id); return e && e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : null; };
const vis = e => !!e && e.getBoundingClientRect().width > 0;
const pickOpt = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) throw new Error('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const type = (id, v) => { const e = $(id); if (!e) throw new Error('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
const st = () => ({ mode: S.mode, flat: S.flat, ap: L.APPROACHES[S.approach].id, par: JSON.parse(JSON.stringify(S.param[L.APPROACHES[S.approach].id])), planes: S.param.mercator.planes, n: S.n, iter: S.iter, eq: S.eq, z0: S.z0, c: S.c.slice(), abs: S.abs.slice(), flip: S.flip.slice(), cutOn: S.cutOn, cut: S.cut, mosaic: S.mosaic, solid: S.colour.solid, colMode: S.colour.mode, trap: S.colour.trap, pal: S.colour.pal, rev: S.colour.rev, q: JSON.stringify(S.q), fly: S.view.fly, extreme: !!S.extreme, cam: [cam.yaw, cam.pitch, cam.dist].map(x => +x.toFixed(4)), target: cam.target.map(x => +x.toFixed(4)), kiter: S.k.iter });
// what the controls show (not the state): for "every control shows the new state"
const shown = () => ({ modeRadio: ['m', 'j', 'k'].find(m => $('mode-' + m).checked), apRadio: L.APPROACHES.find(a => $('ap-' + a.id).checked).id, planesNum: $('par-mercator-planesNum') && $('par-mercator-planesNum').value, powNum: $('powNum').value, flat: $('flat').checked, flipz: $('flipz').checked, cutOn: $('cutOn').checked, eq: $('eq').value, julia: sel('juliaPreset'), cx: $('cxNum').value, cy: $('cyNum').value, cz: $('czNum').value, solid: sel('col-solid'), mosaic: $('m-mosaic') && $('m-mosaic').checked, stageTop: Math.round($('stage').getBoundingClientRect().top), stageBottom: Math.round($('stage').getBoundingClientRect().bottom), winH: innerHeight });
// 15 x 11 probes over the picture: which hit the solid
const probes = () => { let s = ''; const w = $('stage').clientWidth, h = $('stage').clientHeight; for (let j = 1; j < 12; j++) { for (let i = 1; i < 16; i++) s += L.pick(w * i / 16, h * j / 12) ? '#' : '.'; s += '|'; } return s; };
"""


def step(js=None, wait='done', timeout=300, shot=None, clip='#stage', sleep=None):
    a = {}
    if js is not None:
        a['js'] = PRE + js
    if sleep is not None:
        a['sleep'] = sleep
    if wait:
        a['wait'] = wait
        a['timeout'] = timeout
    if shot:
        a['shot'] = D + shot
        if clip:
            a['clip'] = clip
    return a


def write(name, steps):
    p = os.path.join(HERE, 'steps-%s.json' % name)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(steps, f, ensure_ascii=False, indent=1)
    print('wrote', p, len(steps), 'steps')


# ---------------------------------------------------------------- texts + N2: the opening state, the closing texts, every label
texts = [
    step("return 'opened';", shot='open-fresh.png'),
    step(r"""
const pressed = ['qUltra', 'qFast', 'qBal', 'qFine'].filter(id => $(id).getAttribute('aria-pressed') === 'true').map(id => $(id).textContent);
const k = $('kiter');
let stored = null; try { stored = Object.keys(localStorage); } catch (e) { stored = 'blocked'; }
return JSON.stringify({ storageKeys: stored, qualityMarked: pressed, q: S.q, colourBy: sel('col-mode'), trapShape: sel('col-trap'), trapColoursBy: sel('col-by'), palette: sel('col-pal'), reverse: $('col-rev').checked,
  trapIn3D: sel('col-solid'), glow: S.colour.glow, radius: S.colour.radius, kIter: S.k.iter, kiterSlider: [k.min, k.max, k.value], kiterNum: $('kiterNum').value, kiterTitle: $('kiterNum').title,
  mode: S.mode, approach: L.APPROACHES[S.approach].name, planes: S.param.mercator.planes, n: S.n, iter: S.iter, flat: S.flat, extreme: !!S.extreme, colour: S.colour, title: document.title });
""", wait=None),
    step(r"""
// the closing section, paragraph by paragraph, as the page under test has it
const f = document.querySelector('footer.why'); const out = []; let on = false;
for (const e of f.children) { if (e.tagName === 'H2') on = e.textContent.startsWith('Questions from testing'); if (on) out.push(e.tagName + ': ' + (e.classList.contains('row-btns') ? [...e.querySelectorAll('button')].map(b => '[' + b.textContent + ']').join(' ') : e.textContent)); }
return out.join('\n');
""", wait=None),
    step(r"""
// every label, button, option, heading of a section, as written (with whether it is on show now)
const out = [];
document.querySelectorAll('label, button, option, summary, legend, optgroup').forEach(e => { const t = (e.tagName === 'OPTGROUP' ? e.label : e.textContent).replace(/\s+/g, ' ').trim(); if (t) out.push(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.htmlFor ? '>' + e.htmlFor : '') + (e.tagName === 'OPTION' ? '@' + (e.parentElement.id || e.parentElement.parentElement.id) : '') + ' | ' + t); });
return out.join('\n');
""", wait=None),
    # the Kleinian view at the opening settings, and its depth dial
    step(r"""
$('mode-k').click(); await sleep(50);
const k = $('kiter');
return JSON.stringify({ kIter: S.k.iter, slider: [k.min, k.max, k.value], num: $('kiterNum').value, title: $('kiterNum').title, klein: sel('kleinPreset') });
""", shot='open-klein.png'),
    step(r"""
$('mode-j').click(); await sleep(50);
return JSON.stringify({ julia: sel('juliaPreset'), c: S.c, note: $('juliaNote').textContent });
""", shot='open-julia.png'),
]
write('texts', texts)
