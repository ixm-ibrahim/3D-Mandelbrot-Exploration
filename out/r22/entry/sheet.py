"""Round 22, entry: the sheet for the user, made from the lab itself (dist/r22-entry.html).

  python out/r22/entry/sheet.py shots      nine pictures -> out/r22/entry/sheet/
  python out/r22/entry/sheet.py compose    -> sheet-for-user.png
Three entries (rows), three solids (columns), the same camera down each column, Iterations 40 (Mandelbrot solid: 30).
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
ROWS = [('turnalong', 'Turning plane, along', 'the best so far'),
        ('alongonce', 'Along once, then one plane', 'new in the lab'),
        ('pulledplane', 'Pulled plane', 'new in the lab')]
CAM = "L.resetCam(); L.cam.yaw = -1.9; L.cam.pitch = 0.3; L.cam.dist = 4.6;"
COLS = [('basilica', 'c = −1 (the basilica)', "S.mode = 'j'; S.c = [-1, 0, 0]; S.iter = 40; " + CAM),
        ('rabbit', 'The rabbit', "S.mode = 'j'; S.c = [-0.122561, 0.744862, 0]; S.iter = 40; " + CAM),
        ('mandel', 'The Mandelbrot solid', "S.mode = 'm'; S.iter = 30; L.resetCam();")]
# one plain sentence per row: what a person sees in these pictures (written after looking at them)
SEEN = {
    'turnalong': ['Round buds in many directions on every body of c = −1.',
                  'The rabbit is one swollen lump. The Mandelbrot solid is a lumpy rock.'],
    'alongonce': ['c = −1: the middle body keeps buds in many directions, the other bodies keep only a few. The rabbit comes apart into smooth bodies; two are not joined to the rest (one below; one above, seen here in front of the others).',
                  'The Mandelbrot solid is the flat cushion of the one-plane rule, with thin curved wings at its left end. The wings have no thickness.'],
    'pulledplane': ['c = −1: buds in four directions, two in the plane of the flat picture and two straight above and below it. The rabbit is a row of clean bodies, with buds round the flat picture only.',
                    'The Mandelbrot solid shows the flat picture twice, once lying and once standing, and is smooth in between.'],
}


def shots():
    steps = [run.UP]
    for id_, _, _ in ROWS:
        for tag, _, set_ in COLS:
            js = run.HEAD + "$('ap-%s').click(); await sleep(250); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.flat = false; S.cutOn = false; S.mosaic = false; %s document.querySelectorAll('#stage *').forEach(e => { if (e.tagName !== 'CANVAS' && !e.querySelector('canvas')) e.style.visibility = 'hidden'; }); go(); await settle(); return apId() + ' %s iter ' + S.iter + ' failed ' + L.R.failed;" % (id_, set_, tag)
            steps.append({'js': js, 'wait': 'done', 'timeout': 900, 'shot': 'out/r22/entry/sheet/%s-%s.png' % (id_, tag), 'clip': '#stage canvas'})
    os.makedirs(os.path.join(HERE, 'sheet'), exist_ok=True)
    code, text, vals = run.shot(run.PAGE, steps, 'sheet-steps', '1400x950')
    run.write('sheet.log', text + 'exit %d\n' % code); print(text[-900:], 'exit', code)


def compose():
    from PIL import Image, ImageDraw
    sys.path.insert(0, os.path.join(run.ROOT, 'out', 'r21', 'lib'))
    import mem as M
    W = 560; pad = 14
    def tile(id_, tag):
        a = Image.open(os.path.join(HERE, 'sheet', '%s-%s.png' % (id_, tag))).convert('RGB')
        s = min(a.width, int(a.height * 4 / 3)); x0 = (a.width - s) // 2; h = int(s * 3 / 4); y0 = (a.height - h) // 2
        a = a.crop((x0, y0, x0 + s, y0 + h))
        return a.resize((W, round(a.height * W / a.width)), Image.LANCZOS)
    th = tile(ROWS[0][0], COLS[0][0]).height
    rowh = th + 112; top = 124
    im = Image.new('RGB', (pad + len(COLS) * (W + pad), top + len(ROWS) * rowh + 6 + 58), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 12), 'The two new entries of the lab, beside Turning plane, along', fill=(240, 240, 245), font=M.font(28))
    d.text((pad, 52), 'Pictures from the lab itself. The same camera down each column. Iterations at 40 (the Mandelbrot solid: 30).', fill=(165, 175, 190), font=M.font(17))
    for j, (tag, ct, _) in enumerate(COLS):
        d.text((pad + j * (W + pad), 90), ct, fill=(200, 205, 215), font=M.font(19))
    for i, (id_, name, what) in enumerate(ROWS):
        y = top + i * rowh
        d.text((pad, y), name, fill=(235, 220, 170), font=M.font(22))
        d.text((pad + d.textlength(name + '  ', font=M.font(22)), y + 5), '(' + what + ')', fill=(165, 175, 190), font=M.font(16))
        for k, line in enumerate(SEEN[id_]):
            d.text((pad, y + 32 + 22 * k), line, fill=(215, 218, 226), font=M.font(16))
        for j, (tag, ct, _) in enumerate(COLS):
            im.paste(tile(id_, tag), (pad + j * (W + pad), y + 84))
    # second pass: the fault these nine pictures do not show (measured in out/r22/entrycheck/offplane.txt and in second.log)
    yf = top + len(ROWS) * rowh + 4
    d.text((pad, yf), 'Not in these pictures: c = −1 and the rabbit’s c lie in the plane of the flat picture. When c is moved out of that plane (the dial “c along z”), both new entries', fill=(235, 190, 150), font=M.font(16))
    d.text((pad, yf + 22), 'can show jagged shards or a thin slab where no point really stays. Sphere inversions, one plane does the same. The entries’ own texts say so.', fill=(235, 190, 150), font=M.font(16))
    im.save(os.path.join(HERE, 'sheet-for-user.png')); print('sheet-for-user.png', im.size)


if __name__ == '__main__':
    shots() if sys.argv[1] == 'shots' else compose()
