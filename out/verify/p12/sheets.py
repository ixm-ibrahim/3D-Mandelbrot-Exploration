from PIL import Image
import os
d = os.path.dirname(os.path.abspath(__file__)) + os.sep
def sheet(names, out, cols=5, w=430):
    ims = [(n, Image.open(d + n).convert('RGB')) for n in names if os.path.exists(d + n)]
    if not ims: return
    h = int(w * ims[0][1].height / ims[0][1].width)
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * w, rows * h), (0, 0, 0))
    for i, (n, im) in enumerate(ims):
        S.paste(im.resize((w, h), Image.LANCZOS), ((i % cols) * w, (i // cols) * h))
    S.save(d + out); print(out, [n for n, _ in ims])
aps = ['mercator', 'lathe', 'bulb', 'classic', 'split']
sheet(['b-ap-%s-n2.png' % a for a in aps] + ['b-ap-%s-nm2.png' % a for a in aps] + ['b-ap-%s-n3.png' % a for a in aps], 'sheet-approaches.png')
sheet(['b-eq-%d.png' % i for i in range(8)] + ['b-eq-typed-z4.png', 'b-eq-typed-mix.png', 'b-eq-reset.png', 'b-mod-ship.png', 'b-mod-bar.png', 'b-mod-absx.png'], 'sheet-eq-mod.png', cols=4, w=480)
sheet(['b-julia-basilica.png', 'b-julia-rabbit.png', 'b-klein.png', 'b-klein-trap.png', 'b-mosaic.png'], 'sheet-modes.png', cols=3, w=560)
sheet(['b-col-%d.png' % i for i in [0, 2, 3, 4, 5, 6, 7]] + ['b-trap-%d.png' % i for i in [0, 1, 3, 5, 6, 7]], 'sheet-colour.png', cols=5, w=400)
