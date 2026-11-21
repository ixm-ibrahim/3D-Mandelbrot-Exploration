"""Round 25, section 'inverse': the one rule of this corner worth re-measuring. It FAILS (see NOTES.md); it is here
so that the judge can make it fail with his own scripts.

    import sys; sys.path.insert(0, 'out/r25/inverse'); import best
    r = best.rule()            # the zip square on the square pillow (b = 1): a mem.Rule, exact on the flat plane
    r = best.rule(b=2.0)       # the same on a pillow twice as tall: bodies apart, thin needles, different above and below
    r = best.rule(mirror=True) # the other way up
    inside = best.both(c, mode='all')   # zip and its mirror image together; 'all' = every choice of square stays,
                                        # 'any' = some choice stays. inside(x, y, z) -> True / False (from a grid of blocks)

The zip square. Directions are laid on a flat pillow (a tube, t = longitude / 360, s = 0 .. b/2 across, both ends
zipped shut). In pillow coordinates the square is u -> 2 conj(u):
    s <  b/4:  (t, s) -> (-2 t, 2 s)        s >= b/4:  (t, s) -> (2 t, b - 2 s)        length -> length squared
The flat circle is the line s = b/3 (there: t -> 2 t, plain doubling; no corner of the pillow lies on it).
Its four roots halve every distance on the pillow, in every direction alike.

    python out/r25/inverse/best.py        the flat check
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import roots as R
M = R.M


def rule(b=1.0, mirror=False):
    return R.Zip(b, mirror).rule()


def both(c, mode='all', b=1.0, n=224, pre=1):
    Fs = [R.Zip(b).F, R.Zip(b, True).F]; Kf, meta = R.grid_K(Fs, c, mode, n=n)
    return R.inside_grid(Fs, c, mode, Kf, meta, pre=pre)


if __name__ == '__main__':
    for b in (1.0, 2.0):
        print('zip b = %g: flat check' % b, M.flat_check(rule(b), n=20000, steps=60))
