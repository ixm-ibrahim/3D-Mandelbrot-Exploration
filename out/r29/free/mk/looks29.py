"""Round 29, Track A, builder, section 4 point 4 and the pictures to look at.

  python -B out/r29/free/mk/looks29.py [new|old] [size] [theme] [names...]
     -> out/r29/free/shots/look-<name>-{3d,2d}.png (the page), look-<name>-recipe.png (the recipe alone, same view),
        look-<name>-sheet.png (page 2D | recipe alone | page 3D), logs/looks-<panel>-<size>-<theme>.txt

For each state: the numbers are written into the state, Frame it, the 3D picture; then the 2D view, Frame it, the 2D
picture, and the distance the program hands out on the pixels of the middle square of that picture (sampleSlice, one
sample a pixel). Here: my own writing of the recipe on the same pixels, four times as fine, and at the pixels' centres.
  stray: pixels the 2D view inks as outline (distance above 0 and under one and a half pixels) that lie more than two
         pixels from every place where the recipe changes its verdict.
"""
import base64, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run29 as run
import kit29 as K

PRE = run.HEAD + """
window.__V = {};
window.__V.b64 = f => { const u = new Uint8Array(f.buffer, f.byteOffset, f.byteLength); let s = ''; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return btoa(s); };
$('ap-balls').click(); await settle();
return 'Balls on balls on show';
"""
SET3 = run.HEAD + """
S.k.brho = %r; S.k.bt = %r; S.k.bgrid = %d; S.k.bit = %d; S.flat = false; S.cutOn = false; go(); await sleep(80); $('ballsFrame').click(); await settle();
return JSON.stringify({ name: '%s', view: '3d', sig: String(L.R.sig).split('\\n')[0], status: $('status').textContent, warn: warn(), cam: [L.cam.yaw, L.cam.pitch, L.cam.dist], bound: S.view.bound,
  size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, depth: $('ballsDepthNum').value });
"""
SET2 = run.HEAD + """
S.flat = true; go(); await sleep(80); $('ballsFrame').click(); await settle();
const cv = $('view'), H = cv.height, Wd = cv.width, n = Math.min(H, 720);
const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, S.v2.x, S.v2.y, S.v2.h * n / H, S.cut, n); L.releaseSnapshot(snap);
const d = new Float32Array(n * n); for (let i = 0; i < n * n; i++) d[i] = arr[4 * i + 3];
return JSON.stringify({ name: '%s', view: '2d', status: $('status').textContent, warn: warn(), v2: [S.v2.x, S.v2.y, S.v2.h], canvas: [Wd, H], n, cut: S.cut, d: window.__V.b64(d) });
"""
HIDE = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = 'hidden'; }); await new Promise(r => setTimeout(r, 150)); return 'hidden';"
SHOW = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = ''; }); return 'shown';"


def recipe_view(t, rho, grid, depth, v2, canvas, sub=1):
    W, H = canvas; x0, y0, h = v2
    px = h / H
    xs = x0 + ((np.arange(W * sub) + 0.5) / sub - W / 2) * px
    ys = y0 + (H / 2 - (np.arange(H * sub) + 0.5) / sub) * px
    X, Y = np.meshgrid(xs, ys)
    P = np.stack([X.ravel(), Y.ravel(), np.zeros(X.size)], 1)
    return K.recipe(P, t, rho, grid, depth).reshape(X.shape)


if __name__ == '__main__':
    args = sys.argv[1:]
    which = args[0] if args and args[0] in ('new', 'old') else 'new'
    rest = args[1:] if args and args[0] in ('new', 'old') else args
    size = rest[0] if rest and 'x' in rest[0] else '1400x950'
    theme = rest[1] if len(rest) > 1 and rest[1] in ('light', 'dark') else 'light'
    names = [a for a in rest if a not in (size, theme)]
    panel = [s for s in (K.PANEL_NEW if which == 'new' else K.PANEL_OLD) if not names or s[0] in names]
    steps = [run.UP, {'js': PRE, 'wait': 'done', 'timeout': 900}]
    meta = {}
    for (name, p, rs, grid, depth) in panel:
        t = float(K.t_of(p)); rho = float(rs / 100.0)
        if which == 'old' and abs(rs - 33.33) < 0.01:
            rho = 0.3333
        if which == 'old' and abs(rs - 16.67) < 0.01:
            rho = 0.1667
        meta[name] = (p, rs, grid, depth, t, rho)
        steps.append({'js': SET3 % (rho, t, grid, depth, name), 'wait': 'done', 'timeout': 1800})
        steps.append({'js': HIDE, 'shot': '%s/shots/look-%s-3d.png' % (run.OUT, name), 'clip': '#view'})
        steps.append({'js': SHOW})
        steps.append({'js': SET2 % name, 'wait': 'done', 'timeout': 1800})
        steps.append({'js': HIDE, 'shot': '%s/shots/look-%s-2d.png' % (run.OUT, name), 'clip': '#view'})
        steps.append({'js': SHOW})
    tag = 'looks-%s-%s-%s' % (which, size, theme) + ('-' + '-'.join(names) if names else '')
    code, text, vals = run.shot(run.PAGE, steps, tag, size, theme)
    run.write(tag + '.log', text + 'exit %d\n' % code)
    lines = ['page %s, %s, %s: exit %d, %s' % (run.PAGE, size, theme, code, 'no console errors' if run.clean(text) else 'SEE logs/%s.log' % tag)]
    SH = os.path.join(run.FREE, 'shots')
    for v in vals:
        try:
            d = json.loads(v)
        except ValueError:
            continue
        if not isinstance(d, dict) or 'name' not in d:
            continue
        name = d['name']; p, rs, grid, depth, t, rho = meta[name]
        if d['view'] == '3d':
            lines.append('%-4s size %s second %s depth %s (t %.6f) | program %s | 3D: camera distance %.3f, Drawing radius %s | %s' % (name, d['size'], d['second'], d['depth'], t, d['sig'], d['cam'][2], d['bound'], d['status']))
            lines.append('     3D sentence: %s' % (d['warn'] or '(none)'))
            continue
        W, H = d['canvas']; n = d['n']; x0, y0, h = d['v2']; px = h / H
        dist = np.frombuffer(base64.b64decode(d['d']), dtype=np.float32).astype(float).reshape(n, n)[::-1]     # row 0 at the top
        # the same pixels by the recipe alone, four times as fine, and at the pixels' own centres
        sub = 4
        xs = x0 + ((np.arange(n * sub) + 0.5) / sub - n / 2) * px
        ys = y0 + (n / 2 - (np.arange(n * sub) + 0.5) / sub) * px
        X, Y = np.meshgrid(xs, ys)
        ins = K.recipe(np.stack([X.ravel(), Y.ravel(), np.full(X.size, d['cut'])], 1), t, rho, grid, depth).reshape(X.shape)
        edge = np.zeros_like(ins)
        edge[:, 1:] |= ins[:, 1:] != ins[:, :-1]; edge[1:, :] |= ins[1:, :] != ins[:-1, :]
        far = ndimage.distance_transform_edt(~edge) / sub if edge.any() else np.full(ins.shape, 1e9)
        far = far.reshape(n, sub, n, sub).min(axis=(1, 3))                      # in pixels, per pixel
        pix_in = ins.reshape(n, sub, n, sub).mean(axis=(1, 3))
        xc = x0 + (np.arange(n) + 0.5 - n / 2) * px; yc = y0 + (n / 2 - (np.arange(n) + 0.5)) * px
        XC, YC = np.meshgrid(xc, yc)
        ins_c = K.recipe(np.stack([XC.ravel(), YC.ravel(), np.full(XC.size, d['cut'])], 1), t, rho, grid, depth).reshape(XC.shape)
        # (a pixel whose centre and whose sixteen finer points do not all agree holds an edge)
        hold = (pix_in > 0) & (pix_in < 1) | (ins_c != (pix_in > 0.5)) | (far < 0.71)      # pixels that hold an edge
        far = np.minimum(far, ndimage.distance_transform_edt(~hold) if hold.any() else 1e9)
        ink = (dist > 0) & (dist < 1.5 * px); ink2 = (dist > 0) & (dist < 2 * px)
        stray = ink & (far > 2.75); stray2 = ink2 & (far > 2.75)
        wrong = ((dist <= 0) != ins_c) & (far > 1.5)
        if wrong.any():
            # a picture of where: the recipe (dark inside), red where the shader says inside and the recipe outside, blue the other way
            g = np.where(pix_in > 0.5, 60, 235).astype(np.uint8); wimg = np.stack([g, g, g], 2)
            wimg[wrong & (dist <= 0)] = (230, 30, 30); wimg[wrong & (dist > 0)] = (30, 60, 230)
            Image.fromarray(wimg).save(os.path.join(SH, 'look-%s-2d-wrong.png' % name))
        lines.append('     2D: view %.3f high, %d x %d pixels, the middle %d x %d measured | inside share %.3f | outline pixels %d, stray %d (to two pixels of ink: %d, stray %d) | verdict of the shader against the recipe, away from every edge: %d differ'
                     % (h, W, H, n, n, pix_in.mean(), ink.sum(), stray.sum(), ink2.sum(), stray2.sum(), wrong.sum()))
        lines.append('     2D sentence: %s' % (d['warn'] or '(none)'))
        # the recipe alone, as a picture of the whole view, and the sheet
        ref = recipe_view(t, rho, grid, depth, d['v2'], d['canvas'])
        bg = (245, 242, 235) if theme == 'light' else (24, 24, 28); fg = (60, 60, 66) if theme == 'light' else (200, 196, 186)
        img = np.zeros(ref.shape + (3,), np.uint8); img[:] = bg; img[ref] = fg
        Image.fromarray(img).save(os.path.join(SH, 'look-%s-recipe.png' % name))
        a = Image.open(os.path.join(SH, 'look-%s-2d.png' % name)).convert('RGB'); b = Image.fromarray(img); c = Image.open(os.path.join(SH, 'look-%s-3d.png' % name)).convert('RGB')
        # mark the stray pixels on a copy of the page's 2D picture
        if stray.any():
            m = np.asarray(a).copy(); ox = (W - n) // 2
            yy, xx = np.nonzero(stray)
            for y_, x_ in zip(yy, xx):
                m[max(y_ - 2, 0):y_ + 3, max(ox + x_ - 2, 0):ox + x_ + 3] = (230, 30, 30)
            Image.fromarray(m).save(os.path.join(SH, 'look-%s-2d-stray.png' % name))
        w2 = 640; h2 = int(round(w2 * H / W))
        sheet = Image.new('RGB', (3 * w2 + 20, h2), (255, 255, 255))
        for k, im in enumerate((a, b, c)):
            sheet.paste(im.resize((w2, h2), Image.LANCZOS), (k * (w2 + 10), 0))
        sheet.save(os.path.join(SH, 'look-%s-sheet.png' % name))
    out = '\n'.join(lines) + '\n'
    run.write(tag + '.txt', out); print(out)
    if code != 0:
        print(text[-3000:])
