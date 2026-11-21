"""A few extra pictures for the notes: python out/r5/page/extra.py

- the notes under the planes dial, with one plane and with two (extra-notes-1.png, extra-notes-2.png)
- the trap as the solid at the opening settings and with Trap radius 0.7, Mandelbrot and Julia (extra-solid-*.png)
- the opening picture with Glow width 1 and 2.5 (extra-glow-*.png)
- the closing text at phone width from "What does a list entry change?" to the end (extra-foot-*.png)
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERE = 'out/r5/page/'
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
"""


def S(js, shot=None, clip=None, wait='done'):
    a = {'js': PRE + js.strip()}
    if wait:
        a['wait'] = wait; a['timeout'] = 300
    if shot:
        a['shot'] = HERE + shot
        if clip:
            a['clip'] = clip
    return a


desk = [
    S("L.R.warmOn = false; L.S.q.aa = 4; L.touch(); document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); return 1;", 'extra-glow-1.png', '#stage'),
    S("type('col-glowNum', '2.5'); return 'glow width 2.5';", 'extra-glow-2.png', '#stage'),
    S("type('col-glowNum', '1'); pick('col-solid', 'Is the solid'); type('col-radiusNum', '0.7'); return 'trap solid, radius 0.7, Mandelbrot';", 'extra-solid-m-r07.png', '#stage'),
    S("$('mode-j').click(); return 'trap solid, radius 0.7, Julia c = -1';", 'extra-solid-j-r07.png', '#stage'),
    S("type('col-radiusNum', '1'); return 'trap solid, radius 1, Julia c = -1';", 'extra-solid-j-r1.png', '#stage'),
    S("pick('col-solid', 'Colours the surface'); $('par-mercator-planes').scrollIntoView({ block: 'center' }); await sleep(200); return $('par-mercator-note1').textContent;", 'extra-notes-1.png', '#pd-mercator', wait=None),
    S("type('par-mercator-planesNum', '2'); await sleep(200); $('par-mercator-planes').scrollIntoView({ block: 'center' }); await sleep(200); return $('par-mercator-note2').textContent;", 'extra-notes-2.png', '#pd-mercator'),
]
phone = [
    S("L.R.warmOn = false; L.S.q.aa = 2; L.touch(); const h = [...document.querySelectorAll('footer.why h3')].find(e => e.textContent.startsWith('What does a list entry')); window.scrollTo(0, h.getBoundingClientRect().top + window.scrollY - 10); await sleep(250); return 1;", 'extra-foot-1.png'),
    S("window.scrollBy(0, window.innerHeight - 110); await sleep(250); return 1;", 'extra-foot-2.png', wait=None),
    S("window.scrollBy(0, window.innerHeight - 110); await sleep(250); return 1;", 'extra-foot-3.png', wait=None),
]
env = dict(os.environ, PYTHONIOENCODING='utf-8')
for name, steps, size in (('extra-desk', desk, '1400x950'), ('extra-phone', phone, '375x812')):
    path = os.path.join(ROOT, HERE, name + '.json')
    json.dump(steps, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    with open(os.path.join(ROOT, HERE, name + '.log'), 'w', encoding='utf-8') as f:
        code = subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/r5-page.html', '--size', size, '--actions', path], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
    print(name, 'exit', code)
