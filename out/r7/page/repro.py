"""The testers' reproductions of the five page defects, as one step file per page.

  python out/r7/page/repro.py before   -> out/r7/page/repro-before.json  (pictures before-*.png), run on dist/v6.html
  python out/r7/page/repro.py after    -> out/r7/page/repro-after.json   (pictures after-*.png), run on dist/r7-page.html
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1] if len(sys.argv) > 1 else 'before'
PRE = r"""const L = squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const type = (id, v) => { const e = $(id); e.focus(); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
// 15 x 11 probes over the picture, as the words tester used: hits, and hits on the outer ring
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) if (L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11)) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } return n + ' of 165 probes hit, ' + ring + ' on the outer ring'; };
const view = () => 'camera dist ' + cam.dist.toFixed(3) + ', far limit ' + S.view.zmax + ', near limit ' + S.view.zmin + ', drawing radius ' + S.view.bound + ', field of view ' + (2 * Math.atan(S.view.fov) * 180 / Math.PI).toFixed(1);
"""
steps = []


def step(js, shot=None, wait='done'):
    a = {'js': PRE + js.strip()}
    if wait:
        a['wait'] = wait; a['timeout'] = 240
    if shot:
        a['shot'] = 'out/r7/page/%s-%s.png' % (tag, shot); a['clip'] = '#stage'
    steps.append(a)


# layout-4, at the opening scroll position
step(r"""
const r = $('reset').getBoundingClientRect(), s = $('stage').getBoundingClientRect();
return 'layout-4: stage ' + Math.round(s.top) + ' to ' + Math.round(s.bottom) + ', Reset view button ' + Math.round(r.top) + ' to ' + Math.round(r.bottom) + ', window ' + innerHeight + ', scrollY ' + scrollY;
""", wait=None)
# layout-2
step(r"""
$('mode-k').click();
const s = $('kleinPreset'), cs = getComputedStyle(s), c = document.createElement('canvas').getContext('2d');
c.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
const room = s.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 18;
const wide = [...s.options].filter(o => c.measureText(o.text).width > room).map(o => o.text + ' (' + Math.round(c.measureText(o.text).width) + ')');
return 'layout-2: room ' + room + ' px, font ' + cs.fontSize + '; ' + wide.length + ' of ' + s.options.length + ' names too wide: ' + wide.join(' | ');
""", wait=None)
# kleinian-2
step(r"""
type('kinvrNum', '10'); await sleep(300);
return 'kleinian-2, radius 10: warning hidden ' + $('kleinWarn').hidden + ' text [' + $('kleinWarn').textContent + ']';
""", 'klein-radius10')
step(r"""
const g = grid();
type('kinvrNum', '3'); await sleep(300);
return 'radius 10: ' + g + '. radius 3: warning hidden ' + $('kleinWarn').hidden + ' text [' + $('kleinWarn').textContent + ']';
""", 'klein-radius3')
step(r"""
const g = grid();
type('kinvrNum', '1.5'); await sleep(300);
return 'radius 3: ' + g + '. radius 1.5: warning hidden ' + $('kleinWarn').hidden + ' text [' + $('kleinWarn').textContent + ']';
""", 'klein-radius15')
# words-1
step(r"""
const g = grid();
L.resetAll(); $('mode-j').click(); $('flat').click(); S.cut = 0.156; L.syncControls(); L.touch();
const foot = [...document.querySelectorAll('footer.why p')].map(p => p.textContent).filter(t => /smooth piece|one piece|separate discs/.test(t));
return 'radius 1.5: ' + g + '. words-1, sentences: ' + foot.map(t => (t.match(/[^.]*(smooth piece|one piece|separate discs)[^.]*\./g) || []).join(' ')).join(' || ');
""", 'words1-slice-0156')
# words-3 (a): far zoom limit 3, 5 iterations
step(r"""
L.resetAll(); S.view.zmax = 3; S.iter = 5; L.syncControls(); L.viewChanged(); L.touch(); $('fig4Show').click(); await sleep(700);
return 'words-3a Figure 4: ' + view();
""", 'words3a-fig4')
step(r"""
const g = grid(); $('twinMerc').click(); await sleep(700);
return 'words-3a Figure 4: ' + g + '. Twin of Sphere inversions: ' + view();
""", 'words3a-twinMerc')
step(r"""
const g = grid(); $('twinBulb').click(); await sleep(700);
return 'words-3a twin of Sphere inversions: ' + g + '. Twin of the Mandelbulb: ' + view();
""", 'words3a-twinBulb')
# words-3 (a'): the zoom limit alone, at the usual 14 iterations
step(r"""
const g = grid();
L.resetAll(); S.view.zmax = 3; L.syncControls(); L.viewChanged(); L.touch(); $('fig4Show').click(); await sleep(700);
return 'words-3a twin of the Mandelbulb: ' + g + '. Zoom limit alone, Figure 4: ' + view();
""", 'words3a2-fig4')
# words-3 (b): fly camera, drawing radius 1.5, field of view 100
step(r"""
const g = grid();
L.resetAll(); L.setCamMode(true); S.view.bound = 1.5; S.view.fov = Math.tan(100 * Math.PI / 360); L.syncControls(); L.viewChanged(); L.touch(); $('fig4Show').click(); await sleep(700);
return 'zoom limit alone, Figure 4: ' + g + '. words-3b Figure 4: ' + view();
""", 'words3b-fig4')
# words-3 (b'): the field of view alone
step(r"""
const g = grid();
L.resetAll(); S.view.fov = Math.tan(100 * Math.PI / 360); L.syncControls(); L.viewChanged(); L.touch(); $('fig4Show').click(); await sleep(700);
return 'words-3b Figure 4: ' + g + '. Field of view 100 alone, Figure 4: ' + view();
""", 'words3b2-fig4')
step(r"""
const g = grid(); L.resetAll();
return 'field of view 100 alone, Figure 4: ' + g;
""")

path = os.path.join(HERE, 'repro-%s.json' % tag)
with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(steps, f, indent=1, ensure_ascii=False)
print('%d steps -> %s' % (len(steps), path))
