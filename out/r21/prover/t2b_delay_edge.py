"""'delay' balances on a knife edge: the closed form for the main body, against the computer.

    python out/r21/prover/t2b_delay_edge.py  ->  out/r21/prover/t2b_delay_edge.txt, t2b_delay_edge.png

Statement (NOTES.md, K2): let c0 be in the main body of the flat set and zeta its resting point (zeta^2 + c0 = zeta,
|zeta| < 1/2).  Under 'delay' (each point squared about the sheet of the point before) a small lift of the orbit off
the sheet of c dies out if  |zeta| - Re zeta < 1/2  and grows by the factor sqrt(2 (|zeta| - Re zeta)) per step otherwise.
Test: the cut of delay_cov along the sheet at 22.5 degrees, every c lifted off its sheet by 1e-9, 700 steps.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M, myrules as R


def main():
    W, H, steps = 520, 440, 700
    a, b = np.meshgrid(np.linspace(-0.85, 0.45, W), np.linspace(0.72, -0.72, H))
    c0 = a + 1j * b; zeta = (1 - np.sqrt(1 - 4 * c0)) / 2                 # the resting point with the smaller slope
    body = np.abs(zeta) < 0.5
    g = 2 * (np.abs(zeta) - zeta.real)                                    # growth factor squared
    pred = body & (g < 1.0)
    th = np.radians(22.5); lift = 1e-9                                    # c in the sheet at 22.5 degrees, lifted square to the sheet
    cy, cz = b * np.cos(th) - lift * np.sin(th), b * np.sin(th) + lift * np.cos(th)
    got = M.mandel(R.BY['delay_cov'], a, cy, cz, steps) >= steps
    out = []
    def say(t):
        print(t); out.append(t)
    say('main body of the flat set: %d grid points; the closed form says %d of them hold against a lift, %d do not' % (body.sum(), pred.sum(), (body & ~pred).sum()))
    say('the computer (delay_cov, sheet at 22.5 degrees, lift 1e-9, %d steps): holds %d of the main body' % (steps, (got & body).sum()))
    say('verdicts that differ inside the main body: %d (closed form holds, computer lost: %d; closed form lost, computer holds: %d)' % ((pred != got)[body].sum(), (pred & ~got & body).sum(), (~pred & got & body).sum()))
    # the sharper question: does the lifted orbit come BACK to the sheet (the closed form says: exactly where g < 1)?
    r = R.BY['delay_cov']; sh = a.shape
    x, y, z = a.ravel().copy(), cy.ravel().copy(), cz.ravel().copy(); cx_, cy_, cz_ = a.ravel(), cy.ravel(), cz.ravel(); st = tuple(r.init(x.size))
    alive = np.ones(x.size, bool)
    for k in range(steps):
        X, Y, Z, st = r.step(x, y, z, st, k, cx_, cy_, cz_)
        x, y, z = np.where(alive, X + cx_, x), np.where(alive, Y + cy_, y), np.where(alive, Z + cz_, z)
        alive &= (x * x + y * y + z * z) < 36.0; x, y, z = np.where(alive, x, 0.0), np.where(alive, y, 0.0), np.where(alive, z, 0.0)
    height = np.abs(-y * np.sin(th) + z * np.cos(th)).reshape(sh); alive = alive.reshape(sh)
    back = alive & (height < 1e-8); off = alive & (height >= 1e-8)
    say('after %d steps, of the main body: back in the sheet (height below 1e-8) %d | still bounded but OFF the sheet %d | left %d' % (steps, (back & body).sum(), (off & body).sum(), (~alive & body).sum()))
    say('closed form "the lift dies out" against "back in the sheet": %d of %d differ' % ((pred != back)[body].sum(), body.sum()))
    margin = body & (np.abs(g - 1.0) > 0.03) & (np.abs(zeta) < 0.48)
    say('leaving out a thin margin (growth factor squared within 0.03 of 1, or within 0.02 of the edge of the body): %d of %d differ' % ((pred != back)[margin].sum(), margin.sum()))
    if (off & body).any():
        say('the bounded orbits that stay off the sheet: height between %.2e and %.2e, median %.2e' % (height[off & body].min(), height[off & body].max(), np.median(height[off & body])))
    say('   closed form says dies out, but not back in the sheet: %d (of these left: %d) | closed form says grows, but back in the sheet: %d' % ((pred & ~back & body).sum(), (pred & ~alive & body).sum(), (~pred & back & body).sum()))
    img = np.zeros((H, W, 3), np.uint8); img[...] = (16, 20, 30)
    img[body & pred & back] = (238, 228, 200); img[body & ~pred & ~alive] = (150, 60, 60); img[body & ~pred & off] = (60, 200, 90)
    img[body & pred & ~back] = (240, 200, 40); img[body & ~pred & back] = (70, 130, 255)
    img[~body & got] = (110, 110, 120)
    im = Image.new('RGB', (W + 16, H + 60), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((8, 6), "'delay': the flat main body, every c lifted 1e-9 off its sheet, 700 steps", fill=(240, 240, 245), font=M.font(15))
    d.text((8, 28), 'cream: back in the sheet, as the closed form says | green: grows, stays bounded OFF the sheet | red: grows and leaves | yellow, blue: closed form and computer disagree', fill=(170, 175, 190), font=M.font(10))
    im.paste(Image.fromarray(img), (8, 52)); im.save(os.path.join(HERE, 't2b_delay_edge.png'))
    open(os.path.join(HERE, 't2b_delay_edge.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
