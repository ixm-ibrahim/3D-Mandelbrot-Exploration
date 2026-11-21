"""Round 27, entry: the page's pictures of Balls on balls next to round 25's reference picture.
  python out/r27/entry/mk/sheet.py shots    take the pictures (square grid and honeycomb grid; from the front and nearly end-on,
                                            the eyes of tree-big.png as near as the lab's camera gets; plain clay; and the flat view)
  python out/r27/entry/mk/sheet.py          compose shots/sheet-vs-tree.png and shots/changes.diff is NOT made here
"""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
H = run.HEAD
S = os.path.join(run.ENTRY, 'shots')
# tree-big.png: eye (0.45, 0.5, 1.0) and (1.0, 0.25, 0.3) in the bench's frame (x right, y up, z toward the eye).
# The lab's camera turns round its own z (out of the flat plane); the bench's y is the lab's y, its z the lab's z.
VIEWS = [('front', -1.15, 0.42), ('end', -0.29, 0.23)]


def shots():
    steps = [run.UP, dict(js=H + "$('ap-balls').click(); await sleep(150); S.colour.mode = 7; S.q.aa = 16; go(); await settle(); return 'clay';", wait='done', timeout=600)]
    for g, gn in ((0, 'square'), (1, 'hex')):
        for name, yaw, pitch in VIEWS:
            steps.append(dict(js=H + "S.k.bgrid = %d; L.resetCam(); L.cam.yaw = %s; L.cam.pitch = %s; L.cam.dist *= 0.92; go(); await settle(); return '%s %s';" % (g, yaw, pitch, gn, name),
                              wait='done', timeout=600, shot='out/r27/entry/shots/sheet-%s-%s.png' % (gn, name), clip='#view'))
    steps.append(dict(js=H + "S.k.bgrid = 0; S.colour.mode = 0; L.resetCam(); S.flat = true; go(); await settle(); return 'flat';", wait='done', timeout=600, shot='out/r27/entry/shots/sheet-flat.png', clip='#view'))
    steps.append(dict(js=H + "S.flat = false; go(); await settle(); return 'start view, colours as the page opens';", wait='done', timeout=600, shot='out/r27/entry/shots/sheet-start.png', clip='#view'))
    code, text, vals = run.shot(run.PAGE, steps, 'sheet')
    run.write('sheet.log', text + 'exit %d\n' % code); print(text[-1500:])


def compose():
    ref = Image.open(os.path.join(run.ROOT, 'out', 'r25', 'klein', 'tree-big.png')).convert('RGB')
    cells = [[Image.open(os.path.join(S, 'sheet-%s-%s.png' % (g, v))).convert('RGB') for g in ('square', 'hex')] for v in ('front', 'end')]
    w, h = cells[0][0].size; k = (ref.width / 2) / w; cw, ch = int(w * k), int(h * k)
    W = ref.width * 2 + 30; Hh = max(ref.height, 40 + 2 * ch) + 20 + int(ch * 1.0) + 40
    im = Image.new('RGB', (W, Hh), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((10, 6), "Round 25's reference (out/r25/klein/tree-big.png)", fill=(240, 240, 245))
    im.paste(ref, (0, 24))
    x0 = ref.width + 30
    d.text((x0, 6), 'The page (dist/r27-entry.html), plain clay: square grid (left), honeycomb grid (right); from the front (top), nearly end-on (bottom)', fill=(240, 240, 245))
    for r in range(2):
        for c in range(2):
            im.paste(cells[r][c].resize((cw, ch)), (x0 + c * cw, 24 + r * ch))
    y = max(ref.height, 2 * ch) + 50
    d.text((10, y - 18), 'The page: the start view as it opens (left), the 2D view of the flat cut (right)', fill=(240, 240, 245))
    for i, n in enumerate(('sheet-start.png', 'sheet-flat.png')):
        a = Image.open(os.path.join(S, n)).convert('RGB'); im.paste(a.resize((cw, ch)), (i * (cw + 10), y))
    im.save(os.path.join(S, 'sheet-vs-tree.png')); print('wrote sheet-vs-tree.png', im.size)


if __name__ == '__main__':
    shots() if len(sys.argv) > 1 and sys.argv[1] == 'shots' else compose()
