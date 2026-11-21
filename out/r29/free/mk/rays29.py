"""Round 29, Track A, builder, section 4 point 5: the 3D view against a reference made from the recipe alone.

  python -B out/r29/free/mk/rays29.py [page|here] [names...]   -> out/r29/free/logs/rays.txt, shots/rays-<name>-<view>.png
  (page: the browser's part, kept in logs/rays-data-*.json; here: the reference and the report, no browser)

For each state of the new panel and two views (the start view that Frame it gives; a second one from another side,
six tenths as far away): the page is asked, with pick(), where the ray of every 8th pixel of every 8th row stops.
Here the same rays are walked with my own writing of the recipe (kit29.recipe, the page's depth) in steps of half a
pixel, from where the ray enters the Drawing radius to where it leaves it; the first inside point is the reference.
  hole:       the reference meets the solid, the page's ray stops nowhere or more than 3 pixels (at that depth)
              behind that place, and the solid is more than 2 pixels thick along the ray there (a ray that went
              through something);
  in the air: the page's ray stops, and neither that place nor any of 78 points within 2.5 pixels round it is inside
              (a stop where nothing is).
Also: how far the page's stop lies from the reference along the ray (the page stops on a level a little above the
skin, so on a skin seen at a slant this is more than a pixel without anything being wrong).
A view whose eye stands inside the solid is said so and not counted.
"""
import base64, json, os, sys, time
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run29 as run
import kit29 as K

STEP = 8
PRE = run.HEAD + """
window.__V = {};
window.__V.b64 = f => { const u = new Uint8Array(f.buffer, f.byteOffset, f.byteLength); let s = ''; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return btoa(s); };
$('ap-balls').click(); await settle();
return 'Balls on balls on show';
"""
ONE = run.HEAD + """
const STEP = %d, second = %s;
S.k.brho = %r; S.k.bt = %r; S.k.bgrid = %d; S.k.bit = %d; S.flat = false; S.cutOn = false; go(); await sleep(80); $('ballsFrame').click(); await settle();
if (second) { L.cam.yaw = 0.9; L.cam.pitch = 0.28; L.cam.dist = 0.6 * L.cam.dist; L.cam.target = [0.3, 0.05, 0.1]; go(); await settle(); }
const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), ro = b.pos;
const nx = Math.floor((w - 3) / STEP) + 1, ny = Math.floor((h - 3) / STEP) + 1, dep = new Float32Array(nx * ny);
let k = 0, t0 = performance.now();
for (let j = 0; j < ny; j++) { for (let i = 0; i < nx; i++) {
  const p = L.pick(3 + i * STEP + 0.5, 3 + j * STEP + 0.5);
  dep[k++] = p ? Math.hypot(p[0] - ro[0], p[1] - ro[1], p[2] - ro[2]) : -1;
} if (j %% 8 === 7) await sleep(1); }
return JSON.stringify({ name: '%s', second, w, h, nx, ny, fov: S.view.fov, bound: S.view.bound, pos: ro, right: b.right, up: b.up, f: b.f, dist: L.cam.dist, ms: Math.round(performance.now() - t0),
  eyeInside: L.ballsInside(ro[0], ro[1], ro[2]), status: $('status').textContent, sig: String(L.R.sig).split('\\n')[0], dep: window.__V.b64(dep) });
"""
HIDE = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = 'hidden'; }); await new Promise(r => setTimeout(r, 150)); return 'hidden';"
SHOW = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = ''; }); return 'shown';"


def rays_of(d, pxy):
    w, h, fov = d['w'], d['h'], d['fov']
    ro = np.array(d['pos']); R = np.array(d['right']); U = np.array(d['up']); F = np.array(d['f'])
    ux = (2 * pxy[:, 0] - w) / h * fov; uy = (2 * (h - pxy[:, 1]) - h) / h * fov
    rd = ux[:, None] * R + uy[:, None] * U + F
    rd /= np.sqrt((rd * rd).sum(1))[:, None]
    return ro, rd, 2 * fov / h


def walk(d, t, rho, grid, depth, pxy):
    """Along each ray, in steps of half a pixel: where the first inside point lies (distance from the eye, -1 when
    none before the ray leaves the Drawing radius) and how long the solid is there along the ray, in pixels (up to 12)."""
    ro, rd, pix = rays_of(d, pxy)
    bound = d['bound']
    bb = rd @ ro; hh = bb * bb - (ro @ ro) + bound * bound
    ok = hh > 0
    s = np.where(ok, np.maximum(-bb - np.sqrt(np.maximum(hh, 0)), 1e-4), 0.0); s_out = np.where(ok, -bb + np.sqrt(np.maximum(hh, 0)), 0.0)
    first = np.full(len(rd), -1.0); thick = np.zeros(len(rd)); live = ok.copy()
    while live.any():
        idx = np.nonzero(live)[0]
        ins = K.recipe(ro + rd[idx] * s[idx][:, None], t, rho, grid, depth)
        new = ins & (first[idx] < 0)
        first[idx[new]] = s[idx[new]]
        thick[idx[ins]] += 0.5
        done = (first[idx] > 0) & (~ins | (thick[idx] >= 12))
        live[idx[done]] = False
        s[idx] *= 1 + 0.5 * pix
        live &= s < s_out
    return first, thick, pix, ro, rd


DIRS = np.array([[a, b, c] for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1) if a or b or c], float)
DIRS /= np.sqrt((DIRS * DIRS).sum(1))[:, None]


def page_part(names):
    panel = [s for s in K.PANEL_NEW if not names or s[0] in names]
    steps = [run.UP, {'js': PRE, 'wait': 'done', 'timeout': 900}]
    for (name, p, rs, grid, depth) in panel:
        t = float(K.t_of(p)); rho = float(rs / 100.0)
        for second in (False, True):
            steps.append({'js': ONE % (STEP, 'true' if second else 'false', rho, t, grid, depth, name), 'wait': 'done', 'timeout': 2400})
            steps.append({'js': HIDE, 'shot': '%s/shots/rays-%s-%s.png' % (run.OUT, name, 'second' if second else 'start'), 'clip': '#view'})
            steps.append({'js': SHOW})
    tag = 'rays-page' + ('-' + '-'.join(names) if names else '')
    code, text, vals = run.shot(run.PAGE, steps, tag, '1400x950', 'light')
    run.write(tag + '.log', text + 'exit %d\n' % code)
    n = 0
    for v in vals:
        try:
            d = json.loads(v)
        except ValueError:
            continue
        if isinstance(d, dict) and 'dep' in d:
            json.dump(d, open(os.path.join(run.LOGS, 'rays-data-%s-%s.json' % (d['name'], 'second' if d['second'] else 'start')), 'w'))
            n += 1
    print('page %s: exit %d, %s; %d views kept' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE logs/%s.log' % tag, n))


def here_part(names):
    lines = []
    tag = 'rays' + ('-' + '-'.join(names) if names else '')
    for (name, p, rs, grid, depth) in K.PANEL_NEW:
        if names and name not in names:
            continue
        t = float(K.t_of(p)); rho = float(rs / 100.0)
        for view in ('start', 'second'):
            f = os.path.join(run.LOGS, 'rays-data-%s-%s.json' % (name, view))
            if not os.path.exists(f):
                continue
            d = json.load(open(f))
            t0 = time.time()
            head = '%-4s %-6s size %7.2f second %6.2f grid %d depth %3d | %s, eye %.2f from the middle, Drawing radius %.2f' % (name, view, p, rs, grid, depth, d['sig'], d['dist'], d['bound'])
            if d.get('eyeInside') and float(np.sqrt(sum(v * v for v in d['pos']))) < d['bound']:      # (beyond the Drawing radius nothing is solid for the picture)
                lines.append(head + ' | the eye stands inside the solid: not counted'); print(lines[-1], flush=True)
                run.write(tag + '.txt', '\n'.join(lines) + '\n'); continue
            page = np.frombuffer(base64.b64decode(d['dep']), dtype=np.float32).astype(float)
            nx, ny = d['nx'], d['ny']
            PX, PY = np.meshgrid(3 + np.arange(nx) * STEP + 0.5, 3 + np.arange(ny) * STEP + 0.5)
            pxy = np.stack([PX.ravel(), PY.ravel()], 1)
            ref, thick, pix, ro, rd = walk(d, t, rho, grid, depth, pxy)
            one = pix * np.where(ref > 0, ref, np.where(page > 0, page, 1.0))
            both = (page > 0) & (ref > 0)
            behind = ((page <= 0) & (ref > 0)) | (both & (page - ref > 3 * one))
            hole = behind & (thick > 2)
            # in the air: the page stops, and nothing inside within 2.5 pixels of the stop
            stop = page > 0
            idx = np.nonzero(stop)[0]
            hit = ro + rd[idx] * page[idx][:, None]; r1 = pix * page[idx]
            near = K.recipe(hit, t, rho, grid, depth)
            for rad in (0.8, 1.6, 2.5):
                for u in DIRS:
                    todo = ~near
                    if not todo.any():
                        break
                    near[todo] |= K.recipe(hit[todo] + u * (rad * r1[todo])[:, None], t, rho, grid, depth)
            air = np.zeros(len(page), bool); air[idx[~near]] = True
            diff = (page - ref)[both] / one[both]
            lines.append(head + ' | %d rays (%d s in the page, %d s here)' % (len(ref), d['ms'] / 1000, time.time() - t0))
            lines.append('            stops: reference %d, page %d | page against reference along the ray, in pixels: median %+.2f, within 3 of each other %d of %d | holes %d | stops in the air %d'
                         % ((ref > 0).sum(), stop.sum(), float(np.median(diff)) if both.any() else 0.0, int((np.abs(diff) <= 3).sum()), int(both.sum()), hole.sum(), air.sum()))
            print(lines[-2]); print(lines[-1], flush=True)
            try:
                im = np.asarray(Image.open(os.path.join(run.FREE, 'shots', 'rays-%s-%s.png' % (name, view))).convert('RGB')).copy()
                for k in np.nonzero(hole | air)[0]:
                    j, i = divmod(int(k), nx); x = 3 + i * STEP; y = 3 + j * STEP
                    im[max(y - 2, 0):y + 3, max(x - 2, 0):x + 3] = (255, 0, 0) if hole[k] else (0, 60, 255)
                Image.fromarray(im).save(os.path.join(run.FREE, 'shots', 'rays-%s-%s-marked.png' % (name, view)))
            except Exception as e:
                lines.append('            (no marked picture: %s)' % e)
            run.write(tag + '.txt', '\n'.join(lines) + '\n')


if __name__ == '__main__':
    a = sys.argv[1:]
    part = a[0] if a and a[0] in ('page', 'here') else 'both'
    names = [x for x in a if x not in ('page', 'here')]
    if part in ('page', 'both'):
        page_part(names)
    if part in ('here', 'both'):
        here_part(names)
