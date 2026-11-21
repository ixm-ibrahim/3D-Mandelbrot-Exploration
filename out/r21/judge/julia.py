"""M.julia_sheet for the rules under judgment, from two eye positions, one rule per run (so that no run is long).

    python out/r21/judge/julia.py 1 along          eye 1 = (0.45, 0.5, 1.0), writes julia/cam1-along.png
    python out/r21/judge/julia.py 2 along          eye 2 = (0.2, 1.0, 0.35)
    python out/r21/judge/julia.py stitch           stacks the rows into julia-cam1-a.png, -b.png, julia-cam2-a.png, -b.png

The library's own sheet function is used unchanged (380 x 285 x 240 blocks) at 60 steps instead of its default 28,
because rough blocks at 28 steps hide dust and slow leaks."""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
CAMS = {1: (0.45, 0.5, 1.0), 2: (0.2, 1.0, 0.35)}
STEPS = 60; H = 285
D = os.path.join(J.HERE, 'julia'); os.makedirs(D, exist_ok=True)


def stitch():
    for ci, cam in CAMS.items():
        for tag, rules in (('a', J.RULES[:5]), ('b', J.RULES[5:])):
            rows = []
            for r in rules:
                p = os.path.join(D, 'cam%d-%s.png' % (ci, r.name))
                if os.path.exists(p):
                    rows.append(Image.open(p).crop((0, 56, Image.open(p).width, 56 + H + 36)))
            if not rows:
                continue
            im = Image.new('RGB', (rows[0].width, 50 + len(rows) * (H + 36)), (12, 14, 20)); d = ImageDraw.Draw(im)
            d.text((10, 10), 'Julia sets (rough blocks, %d steps), eye at %s' % (STEPS, cam), fill=(240, 240, 245), font=M.font(22))
            for i, s in enumerate(rows):
                im.paste(s, (0, 50 + i * (H + 36)))
            im.save(os.path.join(J.HERE, 'julia-cam%d-%s.png' % (ci, tag)))
            print('wrote julia-cam%d-%s.png with %d rows' % (ci, tag, len(rows)))


if __name__ == '__main__':
    if sys.argv[1] == 'stitch':
        stitch()
    else:
        ci = int(sys.argv[1])
        for nm in sys.argv[2:]:
            M.julia_sheet([J.get(nm)], os.path.join(D, 'cam%d-%s.png' % (ci, nm)), steps=STEPS, cam=CAMS[ci])
