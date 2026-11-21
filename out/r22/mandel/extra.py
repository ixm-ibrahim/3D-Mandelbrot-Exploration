"""Four side measurements for the Mandelbrot solid.   python out/r22/mandel/extra.py -> out/r22/mandel/extra.txt
1. 'Along once' against 'one plane': where do the two solids differ at all, and how different is the first step?
2. The control rule 'flip' (myrules.py): the sideways width of its period-3 bud.
3. 'along': where the orbits of the c inside its solid end up, and how much of the solid is the flat set spun round.
4. 'Pulled plane': the page it uses at steps 1, 2, 3, 6, 12, 30, 100 as c is tilted; and the upright copy against the flat set.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mlib as L
import importlib.util
_s = importlib.util.spec_from_file_location('mandel_rules', os.path.join(HERE, 'myrules.py'))      # 'myrules' is already round 21's judge
R = importlib.util.module_from_spec(_s); _s.loader.exec_module(R)
M = L.M
lines = []


def say(s=''):
    print(s); sys.stdout.flush(); lines.append(s)


def part1():
    say('1. ALONG ONCE against ONE PLANE (Mandelbrot solid, 80 steps)')
    rng = np.random.default_rng(11); one, wake = L.RULES['oneplane'], L.RULES['wake']
    for nm, lo, hi, n in (('whole box x -2.1..0.7, y and z -1.3..1.3', [-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], 2000000),
                          ('thin slab round the flat page, |z| < 0.15', [-2.1, -1.3, -0.15], [0.7, 1.3, 0.15], 2000000),
                          ('round the x-axis, y and z within 0.12', [-2.1, -0.12, -0.12], [0.7, 0.12, 0.12], 2000000)):
        c = rng.uniform(lo, hi, size=(n, 3))
        a = M.mandel(one, c[:, 0], c[:, 1], c[:, 2], 80) >= 80; b = M.mandel(wake, c[:, 0], c[:, 1], c[:, 2], 80) >= 80
        d = a != b
        say('   %-45s %d places: one plane keeps %d, along once keeps %d, verdicts that differ %d (%.4f%% of what one plane keeps)'
            % (nm, n, a.sum(), b.sum(), d.sum(), 100.0 * d.sum() / max(a.sum(), 1)))
        if d.any():
            q = c[d]; rho = np.hypot(q[:, 1], q[:, 2]); tl = np.abs(L.fold(np.arctan2(q[:, 2], q[:, 1]))) * L.DEG
            say('      the differing c: x %.3f..%.3f, distance from the x-axis median %.4f (largest %.4f), tilt out of the flat page median %.1f degrees; one plane keeps %d of them, along once %d'
                % (q[:, 0].min(), q[:, 0].max(), np.median(rho), rho.max(), np.median(tl), a[d].sum(), b[d].sum()))
        if nm.startswith('thin'):
            q = c[a]; tl = np.abs(L.fold(np.arctan2(q[:, 2], q[:, 1]))) * L.DEG; rho = np.hypot(q[:, 1], q[:, 2])
            A = L.about(q[:, 0], q[:, 1], q[:, 2], L.psi_along(q[:, 1], q[:, 2])); B = L.P(q[:, 0], q[:, 1], q[:, 2])
            df = np.sqrt(sum((A[i] - B[i]) ** 2 for i in range(3)))
            say('      the c that one plane keeps: tilt out of the flat page median %.2f degrees, 90%% under %.1f, 99%% under %.1f' % (np.median(tl), np.percentile(tl, 90), np.percentile(tl, 99)))
            say('      first step, along against one plane, for those c: the two landing places are apart by median %.2e, 90%% under %.2e, 99%% under %.2e, largest %.3f'
                % (np.median(df), np.percentile(df, 90), np.percentile(df, 99), df.max()))
            far = rho > 0.3
            say('      of those more than 0.3 from the x-axis (%d): largest tilt %.1f degrees, largest first-step difference %.2e' % (far.sum(), tl[far].max(), df[far].max()))


def part2():
    say(); say('2. CONTROL: the sideways half-width of the period-3 bud (c walked round the x-axis from the bud\'s middle, 600 steps), and the lift of the point that comes back to the middle')
    C3 = (-0.122561, 0.744862); n = 4000; d = np.linspace(0, np.radians(30), n)
    for nm, rule in (('oneplane', L.RULES['oneplane']), ('flip', R.get('flip'))):
        ins = M.mandel(rule, np.full(n, C3[0]), C3[1] * np.cos(d), C3[1] * np.sin(d), 600) >= 600
        edge = d[np.argmin(ins)]
        say('   %-9s first place outside at %.2f degrees = %.4f sideways (flat bud reaches 0.094 within the page): sideways / in-page = %.2f; places inside beyond that edge: %d'
            % (nm, np.degrees(edge), C3[1] * edge, C3[1] * edge / 0.0947, int(ins[np.argmin(ins):].sum())))
        # the lift after 2 steps for a tiny tilt
        s = 1e-4; b = s / C3[1]; x, y, z = C3[0], C3[1] * np.cos(b), C3[1] * np.sin(b); p = np.array([[x], [y], [z]])
        for k in range(2):
            X, Y, Z, _ = rule.step(p[0], p[1], p[2], (), k, x, y, z); p = np.array([X + x, Y + y, Z + z])
        say('             c lifted %.1e above the flat page: two steps later the orbit is %.3e from the middle, of which height %.3e: %.2f times the lift of c' % (s, np.linalg.norm(p), p[2, 0], abs(p[2, 0]) / s))
    say('   in the flat page the same c moved by 1e-4 comes back 2.02e-4 from the middle (|1 + 2 (c^2 + c)(1 + 2c)| = 2.02).')


def part3():
    say(); say('3. ALONG: where the orbit of c ends up, for the c inside its solid (random c in the box, 600 steps)')
    rng = np.random.default_rng(12); n = 60000; c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    rho = np.hypot(c[:, 1], c[:, 2]); spun = M.flat_stay(c[:, 0], rho, c[:, 0], rho, 600) >= 600
    for key in ('along', 'evc', 'oneplane'):
        pts, page, ns = L.trace(key, c[:, 0], c[:, 1], c[:, 2], 600); ins = ns >= 600
        per, kind = L.fate(pts, ns, 600)
        k = kind[ins]; tot = max(int(ins.sum()), 1)
        own = np.arctan2(pts[-101:-1, ins, 2], pts[-101:-1, ins, 1]); wg = np.hypot(pts[-101:-1, ins, 1], pts[-101:-1, ins, 2]) ** 2
        sp = 1 - np.hypot((wg * np.cos(2 * own)).sum(0), (wg * np.sin(2 * own)).sum(0)) / np.maximum(wg.sum(0), 1e-300)
        say('   %-9s inside %d of %d (%.2f%%); the flat set spun round holds %d; inside both %d; inside this but not the spun set %d; in the spun set but not this %d'
            % (key, ins.sum(), n, 100 * ins.mean(), spun.sum(), (ins & spun).sum(), (ins & ~spun).sum(), (~ins & spun).sum()))
        say('             ends: settled on a cycle %.1f%%, nearly settled %.1f%%, never repeats %.1f%% | orbits that end in ONE page (spread < 0.01): %.1f%%'
            % (100.0 * (k == 'cycle').sum() / tot, 100.0 * (k == 'near').sum() / tot, 100.0 * (k == 'cloud').sum() / tot, 100.0 * (sp < 0.01).mean()))
        if key == 'along':
            p = per[ins]; cyc = {}
            for q, kd in zip(p, k):
                if kd != 'cloud':
                    cyc[int(q)] = cyc.get(int(q), 0) + 1
            say('             cycle lengths: ' + ', '.join('%d:%d' % kv for kv in sorted(cyc.items(), key=lambda kv: -kv[1])[:10]))
            cl = (k == 'cloud'); cin = c[ins]
            say('             the never-repeating c: %.0f%% of them lie outside the spun flat set; of the c inside along but outside the spun set, %.0f%% never repeat'
                % (100.0 * (~spun[ins])[cl].mean(), 100.0 * cl[~spun[ins]].mean()))
            # 80 against 600 steps
            a80 = M.mandel(L.RULES['along'], c[:, 0], c[:, 1], c[:, 2], 80) >= 80; a200 = ns >= 200
            say('             kept at 80 steps %d, at 200 steps %d, at 600 steps %d (still leaking: the skin is made of orbits that take long to leave)' % (a80.sum(), a200.sum(), ins.sum()))


def part4():
    say(); say('4. PULLED PLANE: the page used at steps 1, 2, 3, 6, 12, 30, 100 (degrees from the flat page), c = middle of the period-3 bud tilted; "-" = the orbit has left')
    C3 = (-0.122561, 0.744862)
    for deg in (0, 1, 2, 3, 4, 5, 10, 20, 30, 45, 60, 80, 85, 88, 89, 90):
        a = np.radians(deg); pts, page, ns = L.trace('evc', C3[0], C3[1] * np.cos(a), C3[1] * np.sin(a), 600)
        row = ' '.join(('%6.1f' % ((page[k - 1, 0] * L.DEG) % 180)) if np.isfinite(page[k - 1, 0]) else '     -' for k in (1, 2, 3, 6, 12, 30, 100))
        say('   c tilted %2d: %s | %s' % (deg, row, 'stays' if ns[0] >= 600 else 'leaves after %d steps' % ns[0]))
    say('   The same with the orbit kept from leaving is not possible; so instead the pull alone: c pulls once per step with weight 16 x 0.745^2 = 8.9, ease 0.7, no orbit point pulling:')
    for deg in (5, 20, 45, 80):
        w = np.array([0.05, 0.0]); out = []
        for k in range(1, 101):
            pw = np.arctan2(w[1], w[0]); t = 2 * np.radians(deg) - pw; t = t - 2 * np.pi * np.round(t / (2 * np.pi)); a = pw + t - 0.7 * np.sin(t)
            w = w + 8.9 * np.array([np.cos(a), np.sin(a)])
            if k in (1, 2, 3, 6, 12, 30, 100):
                out.append('%6.1f' % (0.5 * np.degrees(np.arctan2(w[1], w[0]))))
        say('   c tilted %2d: %s' % (deg, ' '.join(out)))
    say('   The upright copy against the flat set (cut along the upright page, 600 x 560 places, 200 steps):')
    u, s = np.meshgrid(np.linspace(-2.1, 0.7, 600), np.linspace(1.3, -1.3, 560))
    fl = M.flat_stay(u, s, u, s, 200) >= 200
    for key in ('evc', 'along', 'oneplane'):
        up = M.mandel(L.RULES[key], u, 0 * s, s, 200) >= 200; d = up != fl
        say('   %-9s verdicts that differ from the flat set %d of %d (flat set holds %d); the differing places are at most %.3f from the x-axis (median %.3f)'
            % (key, d.sum(), d.size, fl.sum(), np.abs(s[d]).max() if d.any() else 0, np.median(np.abs(s[d])) if d.any() else 0))
    say('   c in the upright page at height h above the x-axis: c\'s pull has weight 16 h^2 against the flat page\'s 0.05, so the first squaring is about the upright page only if 16 h^2 + h^2 > 0.05, h > %.3f' % np.sqrt(0.05 / 17))


if __name__ == '__main__':
    t0 = time.time()
    for f in (part1, part2, part3, part4):
        f(); say('   (%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 'extra.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
