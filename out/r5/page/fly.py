"""Show Figure 4 and Back to one plane with the fly camera on, from a flown-away position, with extreme ranges
on and the mosaic ticked: python out/r5/page/fly.py   ->  out/r5/page/fly-*.png, fly.log"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERE = 'out/r5/page/'
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const probes = () => { let s = ''; const w = $('stage').clientWidth, h = $('stage').clientHeight; for (let i = 1; i < 8; i++) for (let j = 1; j < 8; j++) s += L.pick(w * i / 8, h * j / 8) ? '1' : '0'; return s; };
"""
steps = [
    {'js': PRE + "L.R.warmOn = false; L.S.q.aa = 4; L.touch(); return 1;", 'wait': 'done', 'timeout': 300},
    {'js': PRE + r"""
$('m-mosaic').click(); $('extreme').click(); $('camFly').click(); await sleep(400);
if (!L.S.view.fly) fail('the fly camera did not switch on');
const cv = $('view');
cv.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyS', key: 's', bubbles: true })); await sleep(900);
window.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyS', key: 's', bubbles: true })); await sleep(300);
$('fig4Show').click(); await sleep(600);
return { fly: L.S.view.fly, mode: L.S.mode, planes: L.S.param.mercator.planes, cutOn: L.S.cutOn, mosaic: L.S.mosaic, extreme: L.S.extreme, pos: L.basis().pos.map(x => +x.toFixed(2)) };
""", 'wait': 'done', 'timeout': 300, 'shot': HERE + 'fly-fig4.png', 'clip': '#stage'},
    {'js': PRE + r"""
const s = probes(), n = s.split('1').length - 1;
if (n < 5) fail('with the fly camera on, the Figure 4 picture is empty or out of frame: ' + n + ' of 49 probes hit');
$('fig4Back').click(); await sleep(400);
return 'fly camera: figure 4 hit by ' + n + ' of 49 probes; planes now ' + L.S.param.mercator.planes + ', fly still ' + L.S.view.fly;
""", 'wait': 'done', 'timeout': 300, 'shot': HERE + 'fly-oneplane.png', 'clip': '#stage'},
]
path = os.path.join(ROOT, HERE, 'fly.json')
json.dump(steps, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
with open(os.path.join(ROOT, HERE, 'fly.log'), 'w', encoding='utf-8') as f:
    code = subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/r5-page.html', '--actions', path], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
print('exit', code)
