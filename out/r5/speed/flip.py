"""Flip every setting a program is specialised on, both ways, through the page's own controls.

  python out/r5/speed/flip.py <page> [set of fresh-start pictures: ref (the default, from dist/v6a.html) or one drawn from the same page]

After each flip: how many new programs were started, whether "Preparing the formula" showed, how long the finished
picture took, and a picture (out/r5/speed/flip/). Each picture is then compared with the one it must equal: a
reference picture of the same state drawn from a fresh start (out/r5/speed/ref/, from dist/v6a.html), or the
picture of the same state earlier in this run.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = r"""
const L = window.squaringLab, S = L.S, C = S.colour, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
if (L.R) L.R.warmOn = false;
const go = () => { L.syncControls(); L.refresh(false); };
const q = id => $(id).click();
const pick = (id, text) => { const e = $(id); if (!e) throw new Error('no control ' + id); const o = [...e.options].find(x => x.text.startsWith(text)); if (!o) throw new Error('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const watch = async label => {
  const c0 = L.R.compiles, t0 = performance.now(); let busy = '', tBusy = 0;
  for (let i = 0; i < 8000; i++) {
    await sleep(16);
    const b = $('busy');
    if (b && !b.hidden && /Preparing/.test(b.textContent)) { busy = b.textContent.trim(); tBusy = performance.now() - t0; }
    if (i > 5 && L.idle()) break;
  }
  return 'FLIP ' + label + ' | new programs ' + (L.R.compiles - c0) + ' | label ' + JSON.stringify(busy) + (busy ? ' for ' + Math.round(tBusy) + ' ms' : '') + ' | finished after ' + Math.round(performance.now() - t0) + ' ms | program ' + L.R.want.key.replace(/\|.*\|/, '|...|');
};
"""
B4 = "q('qBal'); S.q.aa = 4;"
# (picture name, what is done, the picture it must equal)
STEPS = [
    ('f01-m', "L.resetAll(); " + B4 + " go();", None),
    ('f02-m-solid1', "pick('col-solid', 'Is the solid');", 'ref/04-m-solid1-shell'),
    ('f03-m-solid0', "pick('col-solid', 'Colours the surface');", 'flip/f01-m'),
    ('f04-m-solid2', "pick('col-solid', 'Is added');", None),
    ('f05-m-solid2-tones', "pick('col-trap', 'Three tones');", 'ref/11-m-tones'),
    ('f06-m-solid2-shell', "pick('col-trap', 'Sphere shell');", 'flip/f04-m-solid2'),
    ('f07-flat', "L.resetAll(); q('flat');", 'ref/17-flat-m-open'),
    ('f08-flat-inside', "pick('col-inMode', 'Orbit trap');", 'ref/18-flat-m-in-trap'),
    ('f09-3d-inside-kept', "q('flat');", 'ref/01-m-open'),
    ('f10-flat-inside-again', "q('flat');", 'ref/18-flat-m-in-trap'),
    ('f11-flat-plain', "pick('col-inMode', 'Plain');", 'ref/17-flat-m-open'),
    ('f12-cut', "L.resetAll(); " + B4 + " S.cutOn = true; S.cut = 0; C.inMode = 4; go();", 'ref/23-cut-m-hatch'),
    ('f13-cut-face', "q('col-cutFace');", 'ref/24-cut-m-face-settle'),
    ('f14-cut-plain', "q('col-cutFace');", 'ref/23-cut-m-hatch'),
    ('f15-k', "L.resetAll(); " + B4 + " $('mode-k').click(); go();", None),
    ('f16-k-solid1', "pick('col-solid', 'Is the solid');", 'ref/07-k-solid1-shell'),
    ('f17-k-solid0', "pick('col-solid', 'Colours the surface');", 'flip/f15-k'),
]


def main():
    page = sys.argv[1]
    fresh = sys.argv[2] if len(sys.argv) > 2 else 'ref'   # the set of fresh-start pictures to compare with
    os.makedirs(os.path.join(HERE, 'flip'), exist_ok=True)
    steps = [{'wait': 'done', 'timeout': 600}]
    for name, js, _ in STEPS:
        steps.append({'js': PRE + js + " return await watch('" + name + "');", 'wait': 'done', 'timeout': 600,
                      'shot': 'out/r5/speed/flip/%s.png' % name, 'clip': '#view'})
    path = os.path.join(HERE, 'flip', '_steps.json')
    json.dump(steps, open(path, 'w', encoding='utf-8'), indent=1)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--size', '1000x700', '--actions', path],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3600)
    out = (r.stdout or '') + (r.stderr or '')
    open(os.path.join(HERE, 'flip', '_log.txt'), 'w', encoding='utf-8').write(out)
    for l in out.splitlines():
        if 'FLIP' in l: print(json.loads(l.split('result:', 1)[1].strip()))
        elif 'TIMED OUT' in l or 'PROBLEMS' in l or 'console.' in l or 'EXCEPTION' in l or 'no console errors' in l or 'failed' in l: print(l.strip()[:500])
    print('exit', r.returncode)
    import numpy as np
    from PIL import Image
    for name, _, want in STEPS:
        if not want: continue
        want = want.replace('ref/', fresh + '/')
        pa, pb = os.path.join(HERE, 'flip', name + '.png'), os.path.join(HERE, want + '.png')
        if not (os.path.exists(pa) and os.path.exists(pb)):
            print('%-24s missing' % name); continue
        x = np.asarray(Image.open(pa).convert('RGB')).astype(int); y = np.asarray(Image.open(pb).convert('RGB')).astype(int)
        if x.shape != y.shape:
            print('%-24s sizes differ' % name); continue
        d = np.abs(x - y).max(axis=2)
        print('%-24s against %-26s largest channel difference %3d, pixels over 2 of 255: %.4f %%' % (name, want, int(d.max()), 100 * float((d > 2).mean())))


if __name__ == '__main__':
    main()
