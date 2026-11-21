"""Writes the step files of the tester "solids" (N3: trap solids). Run from the project root:
   python out/t6/solids/gen.py
then: python tools/shot.py --url dist/v6.html --actions out/t6/solids/<name>.json
"""
import json, os
D = 'out/t6/solids/'
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const sel = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = String(v); if (e.value !== String(v)) fail('no option ' + v + ' in ' + id); e.dispatchEvent(new Event('change', { bubbles: true })); };
const st = () => { const c = L.S.colour; return [L.S.mode, 'c', L.S.c.join(','), 'trap', c.trap, 'solid', c.solid, 'thick', c.thick, 'skip', c.skip, 'r', c.radius, 't', [c.tx, c.ty, c.tz].join(','), 'iter', L.S.iter, 'kiter', L.S.k.iter, 'cut', L.S.cutOn, L.S.cut, 'flat', L.S.flat, 'mosaic', L.S.mosaic, 'q', JSON.stringify(L.S.q), 'cam', L.cam.dist.toFixed(2)].join(' '); };
"""
SHAPES = [(0, 'point'), (1, 'cross'), (2, 'line'), (3, 'ray'), (4, 'planes'), (5, 'shell'), (6, 'ring')]


def step(js, shot=None, clip='#stage', timeout=420):
    d = {'js': PRE + js + "\nawait sleep(80); return st();", 'wait': 'done', 'timeout': timeout}
    if shot:
        d['shot'] = D + shot
        d['clip'] = clip
    return d


def write(name, steps):
    json.dump(steps, open(D + name + '.json', 'w', encoding='utf-8'), indent=1)
    print(name, len(steps), 'steps')


def shapes(prefix, first, extra_skip=None):
    out = []
    for i, (s, name) in enumerate(SHAPES):
        for solid in (1, 2):
            js = (first if (i == 0 and solid == 1) else '') + "sel('col-trap', %d); sel('col-solid', %d); type('col-skipNum', '1');" % (s, solid)
            out.append(step(js, '%s-%s-s%d.png' % (prefix, name, solid)))
        if extra_skip is not None:
            out.append(step("sel('col-solid', 1); type('col-skipNum', '%d');" % extra_skip, '%s-%s-s1-skip%d.png' % (prefix, name, extra_skip)))
    return out


def J(c):
    return "$('mode-j').click(); type('cxNum', '%s'); type('cyNum', '%s'); type('czNum', '%s'); await sleep(200); " % c


C1, C2, C3 = ('-1', '0', '0'), ('-0.123', '0.745', '0'), ('0', '1', '0')

# every shape, both choices, in each mode
TONES = ("sel('col-trap', 7); await sleep(100); window.__tones = 'tones: solid control shown ' + ($('col-solid').getBoundingClientRect().width > 0) + ', thickness shown ' + ($('col-thick').getBoundingClientRect().width > 0) + ', notes: ' + [...document.querySelectorAll('[id^=col-note]')].filter(e => e.getBoundingClientRect().width > 0).map(e => e.textContent).join(' || ');")
write('m', shapes('m', '', 2) + [step(TONES, 'm-tones-s1.png'), {'js': "return window.__tones;"}])
write('j1', shapes('j1', J(C1)))
write('j2', shapes('j2', J(C2)))
write('j3', shapes('j3', J(C3)))
write('k', shapes('k', "$('mode-k').click(); await sleep(200); "))

# the dials, one at a time
p = [step(J(C1) + "sel('col-trap', 5); sel('col-solid', 1); type('col-radiusNum', '0.7');", 'p-j-base.png')]
for v in ('0.005', '0.02', '0.15', '0.5'):
    p.append(step("type('col-thickNum', '%s');" % v, 'p-j-thick%s.png' % v))
p.append(step("type('col-thickNum', '0.05'); type('col-skipNum', '0');", 'p-j-skip0.png'))
for v in ('2', '3', '6'):
    p.append(step("type('col-skipNum', '%s');" % v, 'p-j-skip%s.png' % v))
p.append(step("type('col-skipNum', '1'); type('col-radiusNum', '0.2');", 'p-j-radius0.2.png'))
for v in ('0.5', '1', '1.5', '2'):
    p.append(step("type('col-radiusNum', '%s');" % v, 'p-j-radius%s.png' % v))
p.append(step("type('col-radiusNum', '0.7'); type('col-txNum', '0.5');", 'p-j-tx0.5.png'))
p.append(step("type('col-txNum', '0'); type('col-tyNum', '0.5');", 'p-j-ty0.5.png'))
p.append(step("type('col-tyNum', '0'); type('col-tzNum', '0.5');", 'p-j-tz0.5.png'))
p.append(step("type('col-tzNum', '0'); type('iterNum', '3');", 'p-j-iter3.png'))
for v in ('6', '30', '80'):
    p.append(step("type('iterNum', '%s');" % v, 'p-j-iter%s.png' % v))
write('pj', p)

p = [step("sel('col-trap', 1); sel('col-solid', 1); type('col-skipNum', '0');", 'p-m-skip0.png')]
for v in ('1', '2', '3', '5'):
    p.append(step("type('col-skipNum', '%s');" % v, 'p-m-skip%s.png' % v))
p.append(step("type('col-skipNum', '2'); type('iterNum', '4');", 'p-m-iter4.png'))
for v in ('8', '30', '80'):
    p.append(step("type('iterNum', '%s');" % v, 'p-m-iter%s.png' % v))
p.append(step("type('iterNum', '14'); type('col-thickNum', '0.01');", 'p-m-thick0.01.png'))
p.append(step("type('col-thickNum', '0.2');", 'p-m-thick0.2.png'))
p.append(step("type('col-thickNum', '0.05'); type('col-radiusNum', '0.4');", 'p-m-radius0.4.png'))
p.append(step("type('col-radiusNum', '1.6');", 'p-m-radius1.6.png'))
p.append(step("type('col-radiusNum', '1'); type('col-txNum', '-0.5');", 'p-m-tx-0.5.png'))
p.append(step("type('col-txNum', '0'); type('col-tzNum', '0.4');", 'p-m-tz0.4.png'))
write('pm', p)

p = [step("$('mode-k').click(); await sleep(200); sel('col-trap', 6); sel('col-solid', 1);", 'p-k-base.png')]
for v in ('0.01', '0.2'):
    p.append(step("type('col-thickNum', '%s');" % v, 'p-k-thick%s.png' % v))
p.append(step("type('col-thickNum', '0.05'); type('col-radiusNum', '0.4');", 'p-k-radius0.4.png'))
p.append(step("type('col-radiusNum', '1.6');", 'p-k-radius1.6.png'))
p.append(step("type('col-radiusNum', '1'); type('col-skipNum', '0');", 'p-k-skip0.png'))
p.append(step("type('col-skipNum', '4');", 'p-k-skip4.png'))
p.append(step("type('col-skipNum', '1'); type('kiterNum', '12');", 'p-k-kiter12.png'))
p.append(step("type('kiterNum', '40');", 'p-k-kiter40.png'))
p.append(step("type('kiterNum', '150'); type('col-txNum', '0.6');", 'p-k-tx0.6.png'))
p.append(step("type('col-txNum', '0'); type('col-tzNum', '0.6');", 'p-k-tz0.6.png'))
write('pk', p)

# quality presets
q = []
scenes = [('qm', "sel('col-trap', 1); sel('col-solid', 1); type('col-skipNum', '2');"),
          ('qj', J(C1) + "sel('col-trap', 5); sel('col-solid', 1); type('col-skipNum', '1'); type('col-radiusNum', '0.7');"),
          ('qr', J(C2) + "type('col-radiusNum', '1'); sel('col-trap', 6); sel('col-solid', 2);"),
          ('qk', "$('mode-k').click(); await sleep(200); sel('col-trap', 6); sel('col-solid', 1);")]
for name, js in scenes:
    for i, b in enumerate(('qUltra', 'qFast', 'qBal', 'qFine')):
        q.append(step((js if i == 0 else '') + "$('%s').click();" % b, '%s-%s.png' % (name, b), timeout=900))
write('q', q)

# the cut, the 2D view, the mosaic
x = [step("sel('col-trap', 1); sel('col-solid', 1); type('col-skipNum', '2'); $('cutOn').click();", 'x-m-cut0.png'),
     step("type('cutNum', '0.3');", 'x-m-cut0.3.png'),
     step("$('col-cutFace').click();", 'x-m-cut0.3-face.png'),
     step("$('col-cutFace').click(); type('cutNum', '0'); sel('col-solid', 2);", 'x-m-cut0-s2.png'),
     step("$('cutOn').click(); " + J(C1) + "sel('col-trap', 5); sel('col-solid', 1); type('col-skipNum', '1'); type('col-radiusNum', '0.7'); $('cutOn').click();", 'x-j-cut0.png'),
     step("sel('col-solid', 2);", 'x-j-cut0-s2.png'),
     step("$('cutOn').click(); $('mode-k').click(); await sleep(200); type('col-radiusNum', '1'); sel('col-trap', 6); sel('col-solid', 1); $('cutOn').click();", 'x-k-cut0.png'),
     step("$('cutOn').click(); sel('col-solid', 0);", None)]
# the 2D view with the trap as colour (0), as the solid (1), added (2): the three pictures must be equal
for mode, js in (('m', "$('mode-m').click(); await sleep(200); sel('col-trap', 1);"), ('j', "$('mode-j').click(); await sleep(200); sel('col-trap', 5);"), ('k', "$('mode-k').click(); await sleep(200); sel('col-trap', 6);")):
    for solid in (0, 1, 2):
        x.append(step((js if solid == 0 else "$('flat').click(); await sleep(150); ") + "sel('col-solid', %d); await sleep(150); $('flat').click(); await sleep(150); if (!L.S.flat) fail('2D view not on');" % solid, 'x-2d-%s-s%d.png' % (mode, solid)))
    x.append(step("$('flat').click(); await sleep(150); sel('col-solid', 0);", None))
# the mosaic, 3D and 2D
x.append(step("$('mode-m').click(); await sleep(200); sel('col-trap', 5); sel('col-solid', 0); $('m-mosaic').click();", 'x-mosaic-s0.png'))
x.append(step("sel('col-solid', 1);", 'x-mosaic-s1.png'))
x.append(step("sel('col-solid', 2);", 'x-mosaic-s2.png'))
x.append(step("sel('col-trap', 1); sel('col-solid', 1);", 'x-mosaic-cross-s1.png'))
x.append(step("$('flat').click(); await sleep(150);", 'x-mosaic2d-cross-s1.png'))
x.append(step("$('flat').click(); await sleep(150); sel('col-solid', 0); await sleep(100); $('flat').click(); await sleep(150);", 'x-mosaic2d-cross-s0.png'))
write('x', x)
