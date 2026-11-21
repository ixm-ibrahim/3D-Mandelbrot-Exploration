"""Does a snapshot keep the program that fits its own frozen state?

  python out/r5/speed/snap.py <page> [<page> ...]      then compares the first page's files with each other page's

For each page, twice (a trap solid on at the start and then switched off on the live page; and the other way round):
  1. a picture job (Save a picture, 512 x 512, as on screen) is started and the live page is switched at once;
     the saved PNG goes to out/r5/speed/snap/<page>-<case>-export.png, the live stage to ...-live.png
  2. a snapshot is taken, the live page is switched and drawn, and then one slice of the snapshot is sampled
     (sampleSlice, what the 3D model uses); its numbers are summed up in ...-slice.json
"""
import base64, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = ("const L = window.squaringLab, S = L.S, C = S.colour, $ = id => document.getElementById(id);"
       "const sleep = ms => new Promise(r => setTimeout(r, ms));"
       "if (L.R) L.R.warmOn = false;"
       "const go = () => { L.syncControls(); L.refresh(false); };"
       "const q = id => $(id).click();")
START = "L.resetAll(); q('qBal'); S.q.aa = 4; $('mode-j').click(); S.c = [-1, 0, 0]; C.solid = %d; go(); return 'start solid %d';"
JOB = r"""
window.snapBlob = null; window.squaringLabSaveHook = (name, blob) => { window.snapBlob = blob; };
const panel = $('exportPanel'), start = [...panel.querySelectorAll('button')].find(b => /^start/i.test(b.textContent.trim()));
const sel = [...panel.querySelectorAll('select')].find(s => [...s.options].some(o => /typed|own size|custom/i.test(o.text)));
const o = [...sel.options].find(x => /typed|own size|custom/i.test(x.text));
sel.value = o.value; sel.dispatchEvent(new Event('change', { bubbles: true })); await sleep(100);
const box = word => { const d = [...panel.querySelectorAll('.dial')].find(e => !e.hidden && e.querySelector('label') && new RegExp(word, 'i').test(e.querySelector('label').textContent)); return d && d.querySelector('input.num'); };
for (const e of [box('width'), box('height')]) { e.value = '512'; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }
const disc = [...panel.querySelectorAll('button')].find(b => /discard/i.test(b.textContent) && b.getBoundingClientRect().width > 0);
if (disc) { disc.click(); await sleep(200); }       // a finished picture has to be discarded before another can be made
const keyBefore = L.R.want.key;
start.click();
C.solid = %d; go();                      // the live page moves on while the job draws
await sleep(300);
return 'job started with program ' + keyBefore + '; live page now wants ' + L.R.want.key + '; export busy ' + L.exportBusy();
"""
SAVE = r"""
const panel = $('exportPanel'), save = [...panel.querySelectorAll('button')].find(b => /^save/i.test(b.textContent.trim()) && b.getBoundingClientRect().width > 0);
if (!save) throw new Error('the picture job did not end with a Save the file button');
save.click(); await sleep(800);
if (!window.snapBlob) throw new Error('no picture was handed over');
const buf = new Uint8Array(await window.snapBlob.arrayBuffer()); let s = '';
for (let i = 0; i < buf.length; i += 8192) s += String.fromCharCode.apply(null, buf.subarray(i, i + 8192));
return 'PNG:%s:' + btoa(s);
"""
SLICE = r"""
C.solid = %d; go();
for (let i = 0; i < 4000 && !L.idle(); i++) await sleep(16);
const snap = L.takeSnapshot(), keySnap = snap.want && snap.want.key;
C.solid = %d; go();
for (let i = 0; i < 4000 && !L.idle(); i++) await sleep(16);
const a = await L.sampleSlice(snap, 0, 0, 4, 0.05, 96);
L.releaseSnapshot(snap);
if (!a) return 'SLICE:%s:' + JSON.stringify({ failed: true });
let inside = 0, sumD = 0, sumC = 0, h = 2166136261; const u = new Uint32Array(a.buffer);
for (let i = 0; i < a.length; i += 4) { if (a[i + 3] <= 0) inside++; sumD += Math.abs(a[i + 3]); sumC += a[i] + a[i + 1] + a[i + 2]; }
for (let i = 0; i < u.length; i++) { h ^= u[i]; h = Math.imul(h, 16777619) >>> 0; }
return 'SLICE:%s:' + JSON.stringify({ snapKey: keySnap, liveKey: L.R.want.key, points: a.length / 4, inside, sumD: +sumD.toFixed(4), sumC: +sumC.toFixed(4), hash: h });
"""


def run(page):
    steps = []
    for case, a, b in (('on-then-off', 1, 0), ('off-then-on', 0, 1)):
        steps.append({'js': PRE + START % (a, a), 'wait': 'done', 'timeout': 600})
        steps.append({'js': PRE + JOB % b, 'wait': "window.squaringLab.idle() && !window.squaringLab.exportBusy()", 'timeout': 900})
        steps.append({'js': PRE + SAVE % case, 'shot': 'out/r5/speed/snap/%s-%s-live.png' % (page, case), 'clip': '#view'})
        steps.append({'js': PRE + SLICE % (a, b, case, case), 'timeout': 900})
    os.makedirs(os.path.join(HERE, 'snap'), exist_ok=True)
    path = os.path.join(HERE, 'snap', '_steps.json')
    json.dump(steps, open(path, 'w', encoding='utf-8'), indent=1)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--size', '1000x700', '--actions', path],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3600)
    out = (r.stdout or '') + (r.stderr or '')
    for l in out.splitlines():
        if 'result:' in l:
            v = json.loads(l.split('result:', 1)[1].strip())
            if v.startswith('PNG:'):
                _, case, b64 = v.split(':', 2)
                open(os.path.join(HERE, 'snap', '%s-%s-export.png' % (page, case)), 'wb').write(base64.b64decode(b64))
                print(page, case, 'export saved,', len(b64) * 3 // 4, 'bytes')
            elif v.startswith('SLICE:'):
                _, case, js = v.split(':', 2)
                open(os.path.join(HERE, 'snap', '%s-%s-slice.json' % (page, case)), 'w').write(js)
                print(page, case, 'slice', js)
            else:
                print(page, v)
        elif 'TIMED OUT' in l or 'PROBLEMS' in l or 'console.' in l or 'EXCEPTION' in l or 'no console errors' in l or 'failed' in l:
            print(page, l.strip()[:500])
    print(page, 'exit', r.returncode)


def compare(a, b):
    import numpy as np
    from PIL import Image
    for case in ('on-then-off', 'off-then-on'):
        for kind in ('export', 'live'):
            pa, pb = (os.path.join(HERE, 'snap', '%s-%s-%s.png' % (p, case, kind)) for p in (a, b))
            if not (os.path.exists(pa) and os.path.exists(pb)):
                print(case, kind, 'missing'); continue
            x = np.asarray(Image.open(pa).convert('RGB')).astype(int); y = np.asarray(Image.open(pb).convert('RGB')).astype(int)
            if x.shape != y.shape:
                print(case, kind, 'sizes differ', x.shape, y.shape); continue
            d = np.abs(x - y).max(axis=2)
            print('%s %s: %s against %s: largest channel difference %d, pixels over 2 of 255: %.4f %%' % (case, kind, a, b, int(d.max()), 100 * float((d > 2).mean())))
        sa, sb = (open(os.path.join(HERE, 'snap', '%s-%s-slice.json' % (p, case))).read() for p in (a, b))
        ja, jb = json.loads(sa), json.loads(sb)
        same = all(ja.get(k) == jb.get(k) for k in ('points', 'inside', 'sumD', 'sumC', 'hash'))
        print('%s slice: %s' % (case, 'the same numbers on both pages' if same else 'DIFFERENT: %s | %s' % (sa, sb)))


if __name__ == '__main__':
    pages = sys.argv[1:]
    for p in pages:
        run(p)
    for p in pages[1:]:
        compare(pages[0], p)
