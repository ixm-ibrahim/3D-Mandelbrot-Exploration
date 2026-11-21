"""Step files of the tester "solids" in the second check (page: dist/v8.html). Run from the project root:
   python out/t9/solids/gen.py
then, one at a time: PYTHONIOENCODING=utf-8 python tools/shot.py --url dist/v8.html --actions out/t9/solids/<name>.json
The helpers and the typed values are those of the first check (out/t6/solids/gen.py)."""
import json
D = 'out/t9/solids/'
PRE = r"""const L = window.squaringLab, S = L.S, C = S.colour, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const sel = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = String(v); if (e.value !== String(v)) fail('no option ' + v + ' in ' + id); e.dispatchEvent(new Event('change', { bubbles: true })); };
const notes = () => [...document.querySelectorAll('#colDials p.note, #camNote, #stageNote')].filter(e => !e.hidden && e.getBoundingClientRect().width > 0).map(e => (e.id || 'note') + ': ' + e.textContent).join(' || ');
const st = () => { const c = L.S.colour; return [L.S.mode, 'c', L.S.c.join(','), 'trap', c.trap, 'solid', c.solid, 'thick', c.thick, 'skip', c.skip, 'r', c.radius, 't', [c.tx, c.ty, c.tz].join(','), 'reach', c.reach, 'iter', L.S.iter, 'kiter', L.S.k.iter, 'q', JSON.stringify(L.S.q), 'cam', L.cam.dist.toFixed(3), 'fov', L.S.view.fov].join(' '); };
"""


def step(js, shot=None, clip='#stage', timeout=900, ret='st()'):
    d = {'js': PRE + js + "\nawait sleep(80); return " + ret + ";", 'wait': 'done', 'timeout': timeout}
    if shot:
        d['shot'] = D + shot
        d['clip'] = clip
    return d


def write(name, steps):
    json.dump(steps, open(D + name + '.json', 'w', encoding='utf-8'), indent=1)
    print(name, len(steps), 'steps')


def J(c):
    return "$('mode-j').click(); type('cxNum', '%s'); type('cyNum', '%s'); type('czNum', '%s'); await sleep(200); " % c


C1, C2, C3 = ('-1', '0', '0'), ('-0.123', '0.745', '0'), ('0', '1', '0')
N = "st() + ' NOTES ' + notes()"

# ---- run a: the reproductions of solids-1 to solids-7, typed values as in the first check
a = [
 step("sel('col-trap', 1); sel('col-solid', 1); type('col-skipNum', '0');", 'a-m-skip0.png'),                      # solids-1
 step("type('col-skipNum', '1');", 'a-m-skip1.png'),
 step("type('col-skipNum', '2'); type('iterNum', '4');", 'a-m-iter4.png'),                                         # solids-6
 step("type('iterNum', '80');", 'a-m-iter80.png'),
 step("type('iterNum', '14'); type('col-thickNum', '0.01');", 'a-m-thick0.01.png'),                                # solids-2
 step("type('col-thickNum', '0.05'); type('col-skipNum', '0'); sel('col-trap', 5);", 'a-m-shell-skip0.png'),       # solids-1, other shapes
 step("sel('col-trap', 4);", 'a-m-planes-skip0.png'),
 step("sel('col-trap', 6);", 'a-m-ring-skip0.png'),
 step("sel('col-trap', 0);", 'a-m-point-skip0.png'),
 step("type('col-skipNum', '1'); sel('col-trap', 0);", 'a-m-point.png', ret=N),                                    # solids-3
 step("type('col-thickNum', '0.3');", 'a-m-point-thick0.3.png'),
 step("type('col-thickNum', '0.05'); sel('col-trap', 3);", 'a-m-ray.png', ret=N),
 step("type('col-thickNum', '0.2');", 'a-m-ray-thick0.2.png'),
 step("type('col-thickNum', '0.05'); " + J(C1) + "sel('col-trap', 5); sel('col-solid', 1); type('col-radiusNum', '0.7');", 'a-j-base.png', ret=N),
 step("type('col-thickNum', '0.005');", 'a-j-thick0.005.png'),                                                     # solids-2
 step("type('col-thickNum', '0.02');", 'a-j-thick0.02.png'),
 step("type('col-thickNum', '0.05'); type('col-skipNum', '3');", 'a-j-skip3.png'),                                 # solids-5
 step("type('col-skipNum', '6');", 'a-j-skip6.png'),
 step("type('col-skipNum', '1'); type('col-radiusNum', '0.2');", 'a-j-radius0.2.png'),
 step("type('col-radiusNum', '0.7'); type('col-txNum', '0.5');", 'a-j-tx0.5.png'),
 step("type('col-txNum', '0'); type('col-tyNum', '0.5');", 'a-j-ty0.5.png'),
 step("type('col-tyNum', '0'); type('iterNum', '3');", 'a-j-iter3.png'),                                           # solids-6
 step("type('iterNum', '80');", 'a-j-iter80.png'),
 step("type('iterNum', '14'); type('col-radiusNum', '1.5');", 'a-j-radius1.5.png', ret=N),                         # solids-7
 step("type('col-radiusNum', '2');", 'a-j-radius2.png', ret=N),
 step("$('reset').click(); await sleep(400);", 'a-j-radius2-resetview.png', ret=N),
 step("type('col-radiusNum', '1'); sel('col-trap', 0);", 'a-j1-point.png', ret=N),                                 # solids-4
 step(J(C3) + "sel('col-trap', 0); sel('col-solid', 1);", 'a-j3-point.png', ret=N),                                # solids-3
 step("sel('col-trap', 3);", 'a-j3-ray.png'),
 step("$('mode-k').click(); await sleep(200); sel('col-trap', 6); sel('col-solid', 1);", 'a-k-base.png', ret=N),   # solids-7
 step("type('col-thickNum', '0.2');", 'a-k-thick0.2.png', ret=N),
 step("$('reset').click(); await sleep(400);", 'a-k-thick0.2-resetview.png', ret=N),
 step("type('col-thickNum', '0.05'); type('col-radiusNum', '1.6');", 'a-k-radius1.6.png', ret=N),
 step("type('col-radiusNum', '1'); type('col-txNum', '0.6');", 'a-k-tx0.6.png', ret=N),
 step("type('col-txNum', '0'); $('reset').click(); await sleep(300); sel('col-trap', 0);", 'a-k-point.png', ret=N), # solids-4
 step("sel('col-trap', 2);", 'a-k-line.png'),
 step("sel('col-trap', 3);", 'a-k-ray.png'),
]
write('a', a)
