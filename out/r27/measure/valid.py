"""Round 27, measure, part 5a: which settings of the object's dials give an object at all (balls that do not overlap)?

    python out/r27/measure/valid.py t        the dial t below 1 (the ladder)          -> valid-t.log
    python out/r27/measure/valid.py slide    the sideways slide of the glued copy     -> valid-slide.log
    python out/r27/measure/valid.py klein    the lab's old Kleinian group (mu)        -> valid-klein.log

For each setting: list the balls down to a cut-off, then (a) do any two balls overlap, and how deep; (b) does the recipe
decide every random point, and the same way after 60 and after 400 rounds.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballkit as K


def expand(reps, grid, R=3.2):
    """The balls with all their slid copies whose centre is within R of the upright axis."""
    i, nx, ny = grid.pairs(-reps[:, 0], -reps[:, 1], np.full(len(reps), R))
    B = reps[i].copy(); B[:, 0] += nx; B[:, 1] += ny
    return B


def test(grid, top, slide=(0.0, 0.0), klein=None, rho=0.012, n=6000, seed=5, cap=6000):
    gens = K.klein_gens(klein) if klein is not None else K.recipe_gens(top, slide)
    reps, info = K.build(grid, gens, top, rho_min=rho, cap=cap, strict=False)
    if len(reps) > 2 * cap:                                    # a run-away list: keep the largest balls only
        reps = reps[np.argsort(-reps[:, 3])[:2 * cap]]
    B = expand(reps, grid, R=2.2); cnt, deep = K.overlaps(B, n_big=300)
    # balls that poke through the two walls count as overlaps as well
    poke = float(np.max(np.maximum(B[:, 3] - B[:, 2], B[:, 2] + B[:, 3] - top), initial=0.0)) if len(B) else 0.0
    rng = np.random.default_rng(seed); w = grid.period * 1.0
    P = rng.uniform([-w, -w if grid.rank == 2 else 0.0, 0.0], [w, w if grid.rank == 2 else 0.0, top], size=(n, 3))
    a = K.recipe(P[:, 0], P[:, 1], P[:, 2], grid, top, 60, slide, klein); b = K.recipe(P[:, 0], P[:, 1], P[:, 2], grid, top, 400, slide, klein)
    big = B[np.argsort(-B[:, 3])[:4000]]; inb = np.zeros(n, bool)
    for s in range(0, len(big), 500):
        q = big[s:s + 500]; inb |= (((P[:, None, :] - q[None, :, :3]) ** 2).sum(2) < q[None, :, 3] ** 2).any(1)
    return {'balls': info['n'], 'capped': info['capped'], 'overlap_pairs': cnt, 'deepest': max(deep, poke), 'undecided60': float((a < 0).mean()), 'undecided400': float((b < 0).mean()),
            'inside': float((b == 1).mean()), 'outside': float((b == 0).mean()), 'in_ball_but_outside_by_recipe': int((inb & (b == 0)).sum())}


def line(tag, r):
    return ('%-34s balls %6d%s | overlapping pairs %6d, deepest %.3f | recipe: inside %.3f, outside %.3f, undecided after 60 / 400 rounds %.4f / %.4f | in a ball but "outside" by the recipe: %d'
            % (tag, r['balls'], '+' if r['capped'] else ' ', r['overlap_pairs'], r['deepest'], r['inside'], r['outside'], r['undecided60'], r['undecided400'], r['in_ball_but_outside_by_recipe']))


def run_t(say):
    say('THE DIAL t BELOW 1. Ladder: t = cos(180 degrees / m). Between the rungs the balls should overlap.')
    ts = [(0.5, 'm = 3'), (0.6, ''), (np.cos(np.pi / 4), 'm = 4'), (0.76, ''), (np.cos(np.pi / 5), 'm = 5'), (0.84, ''), (np.cos(np.pi / 6), 'm = 6'), (0.89, ''),
          (np.cos(np.pi / 8), 'm = 8'), (0.95, ''), (np.cos(np.pi / 12), 'm = 12'), (0.99, ''), (1.0, 'm = infinity'), (1.4, 'default')]
    for gname, per in (('line', 1.0), ('gauss', 1.0), ('eisen', 1.0), ('line', 2.0), ('gauss', 2.0)):
        g = K.Grid(gname, per); say('grid %s, slides by %g' % (gname, per))
        for t, tag in ts:
            r = test(g, 2 * t, rho=0.012 if g.rank == 2 else 0.004)
            say('   ' + line('t = %.4f %s' % (t, tag), r))


def run_slide(say):
    say('THE SIDEWAYS SLIDE of the glued copy (the second unit sphere sits at (slide, 2t)).')
    say('Rule to test: no overlap exactly when no unit sphere on the floor cuts a unit sphere on the ceiling, AND (for slides by 1) twice the slide is a whole number of the grid.')
    for gname, per, slides, ts in (('line', 1.0, [(0, 0), (0.5, 0), (0.25, 0), (0.1, 0), (0.37, 0)], (1.4, 1.0, 0.97)),
                                   ('gauss', 1.0, [(0, 0), (0.5, 0), (0.5, 0.5), (0.25, 0), (0.25, 0.25), (0.3, 0.1)], (1.4, 1.0, 0.95)),
                                   ('eisen', 1.0, [(0, 0), (0.5, 0), (0.5, 0.2887), (0.25, 0.433), (0.3, 0.1)], (1.4, 1.0)),
                                   ('line', 2.0, [(0, 0), (0.3, 0), (0.7, 0), (1.0, 0), (0.5, 0)], (1.4, 1.0, 0.98, 0.9, 0.87)),
                                   ('gauss', 2.0, [(0, 0), (0.3, 0.1), (1.0, 0), (1.0, 1.0), (0.6, 0.6)], (1.4, 1.0, 0.9, 0.72)),
                                   ('gauss', 2 ** 0.5, [(0, 0), (0.3, 0.1), (0.7071, 0), (0.7071, 0.7071)], (1.4, 1.0, 0.5)),
                                   ('eisen', 3 ** 0.5, [(0, 0), (0.3, 0.1), (0.866, 0.5)], (1.4, 1.0, 0.5))):
        g = K.Grid(gname, per); say('grid %s, slides by %g' % (gname, per))
        for sl in slides:
            for t in ts:
                # nearest floor centre to the ceiling centre
                dx, dy = g.near(np.array([sl[0]]), np.array([sl[1]])); gap = np.sqrt(dx[0] ** 2 + dy[0] ** 2 + 4 * t * t) - 2
                r = test(g, 2 * t, slide=sl, rho=0.012 if g.rank == 2 else 0.004)
                say('   ' + line('slide (%.3g, %.3g) t = %.2f gap %+.3f' % (sl[0], sl[1], t, gap), r))


def run_klein(say):
    say("THE LAB'S OLD KLEINIAN GROUP in the flat plane: slides by 2 and q -> mu + 1/q, mu = (slide, height).")
    say('Rule to test (enough, not needed): no overlap when the unit circles about 0, 2, 4 ... and about mu, mu + 2 ... do not cut each other.')
    g = K.Grid('line', 2.0)
    for mu in [(0, 2.0), (0, 2.4), (0, 1.9), (0.5, 2.0), (0.5, 1.95), (0.5, 1.9), (1.0, 1.8), (1.0, 1.74), (1.0, 1.70), (0.66, 1.90), (0.66, 1.86), (0.3, 2.2), (0, 1.0), (0, 2 ** 0.5), (0, 3 ** 0.5), (1.0, 1.0)]:
        m3 = (mu[0], 0.0, mu[1]); dx, dy = g.near(np.array([mu[0]]), np.array([0.0])); gap = np.sqrt(dx[0] ** 2 + mu[1] ** 2) - 2
        r = test(g, mu[1], klein=m3, rho=0.004)
        say('   ' + line('mu = (%.3g, %.4g) gap %+.3f' % (mu[0], mu[1], gap), r))


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 't'
    log = open(os.path.join(HERE, 'valid-%s.log' % a), 'w')

    def say(s):
        print(s); log.write(s + '\n'); log.flush()
    {'t': run_t, 'slide': run_slide, 'klein': run_klein}[a](say)
