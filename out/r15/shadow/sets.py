"""Round 15B, shadow: the picture sets of run.py (python out/r15/shadow/run.py pictures <set>)."""
from run import view3, view2, RABBIT

SIZE = {}


def P(n=2, it=14):
    return "pick('pillow4d'); await sleep(250); S.n = %d; S.iter = %d; " % (n, it)


def PM(n=2, it=14):
    return "pick('mercator'); await sleep(250); S.n = %d; S.iter = %d; " % (n, it)


def cam(yaw=None, pitch=None, dist=None, target=None):
    js = ''
    if yaw is not None:
        js += 'L.cam.yaw = %s; ' % yaw
    if pitch is not None:
        js += 'L.cam.pitch = %s; ' % pitch
    if dist is not None:
        js += 'L.cam.dist = %s; ' % dist
    if target is not None:
        js += 'L.cam.target = %s; ' % target
    return js


def first():
    return [
        ('p4-n2-m', P() + view3('m')),
        ('p4-j-basilica', P() + view3('j', '[-1, 0, 0]')),
        ('p4-n2-cut', P() + view2('m', None, -0.5, 3.2)),
    ]


# the Mandelbrot solid of one power: the opening view, from above, from below, along the x-axis, and the cut at z = 0
def power(n):
    x = -0.5 if n == 2 else 0
    return [
        ('p4-n%d-m' % n, P(n) + view3('m')),
        ('p4-n%d-above' % n, P(n) + view3('m', cam=cam(pitch=1.45))),
        ('p4-n%d-below' % n, P(n) + view3('m', cam=cam(pitch=-1.45))),
        ('p4-n%d-alongx' % n, P(n) + view3('m', cam=cam(yaw=0.0, pitch=0.0))),
        ('p4-n%d-side' % n, P(n) + view3('m', cam=cam(yaw=-1.5708, pitch=0.0))),
        ('p4-n%d-cut' % n, P(n) + view2('m', None, x, 3.2)),
        ('ref-n%d-cut' % n, PM(n) + view2('m', None, x, 3.2)),
    ]


JUL = [('basilica', '[-1, 0, 0]'), ('rabbit', RABBIT), ('offaxis', '[-1, 0.15, 0.1]'), ('c03', '[0.3, 0, 0]')]


def julia():
    out = []
    for tag, c in JUL:
        out.append(('p4-j-%s' % tag, P() + view3('j', c)))
        out.append(('p4-j-%s-below' % tag, P() + view3('j', c, cam=cam(pitch=-0.9))))
        out.append(('p4-j-%s-side' % tag, P() + view3('j', c, cam=cam(yaw=-1.5708, pitch=0.0))))
        out.append(('p4-j-%s-cut' % tag, P() + view2('j', c, 0, 3.6)))
    return out


def juliaref():
    return [('ref-j-%s-cut' % tag, PM() + view2('j', c, 0, 3.6)) for tag, c in JUL if tag != 'offaxis']


SETS = {'first': first, 'julia': julia, 'juliaref': juliaref}
for _n in (2, 3, 4, 5):
    SETS['n%d' % _n] = (lambda n: (lambda: power(n)))(_n)

# ---------- close-ups: the camera moves in on one point of the skin, in three steps, with more orbit steps the closer it is
WAIT = " for (let i = 0; i < 900 && !L.idle(); i++) await sleep(100); "
DEPTHS = [(1.0, 14), (0.25, 20), (0.06, 26)]


def close_series(tag, c, look, pick='L.pick(w * 0.5, h * 0.5)', depths=DEPTHS, n=2):
    """look: camera settings (JavaScript) for the wide view in which the middle of the picture is picked as the target."""
    out = []
    for k, (dist, it) in enumerate(depths):
        js = P(n) + view3('j' if c else 'm', c) + WAIT
        js += "const w = $('stage').clientWidth, h = $('stage').clientHeight; "
        js += "if (!window['__tg_%s']) { %s go(); await sleep(300); %s window['__tg_%s'] = %s; } " % (tag, look, WAIT, tag, pick)
        js += "const tg = window['__tg_%s']; if (!tg) throw new Error('no target for %s'); %s L.cam.target = tg.slice(); L.cam.dist = %s; S.iter = %d; go(); await sleep(200); " % (tag, tag, look, dist, it)
        js += "window.__note = '%s target ' + tg.map(x => +x.toFixed(4)).join(' ');" % tag
        out.append(('p4-close-%s-%d' % (tag, k + 1), js))
    return out


# ---------- the final pictures, framed for the size of each solid (out/r15/shadow/extent.txt)
MCAM = {2: ('[-0.3, 0, -0.4]', 6.6), 3: ('[0, 0, 0]', 6.0), 4: ('[0, 0, 0.5]', 6.8), 5: ('[0, 0, 0.7]', 7.2)}


def solids():
    out = []
    for n in (2, 3, 4, 5):
        t, dist = MCAM[n]
        out += [
            ('f-n%d-m' % n, P(n) + view3('m', cam=cam(dist=dist, target=t))),
            ('f-n%d-above' % n, P(n) + view3('m', cam=cam(yaw=-1.5708, pitch=1.5, dist=dist, target=t))),
            ('f-n%d-below' % n, P(n) + view3('m', cam=cam(yaw=-1.5708, pitch=-1.5, dist=dist, target=t))),
            ('f-n%d-alongx' % n, P(n) + view3('m', cam=cam(yaw=0.0, pitch=0.0, dist=dist, target=t))),
            ('f-n%d-side' % n, P(n) + view3('m', cam=cam(yaw=-1.5708, pitch=0.0, dist=dist, target=t))),
        ]
    return out


def julias():
    out = []
    for tag, c in JUL:
        t = '[0, 0, -0.7]'
        out.append(('f-j-%s' % tag, P() + view3('j', c, cam=cam(dist=7.5, target=t))))
        out.append(('f-j-%s-side' % tag, P() + view3('j', c, cam=cam(yaw=-1.5708, pitch=0.0, dist=7.5, target=t))))
        out.append(('f-j-%s-above' % tag, P() + view3('j', c, cam=cam(yaw=-1.5708, pitch=1.5, dist=7.5, target=t))))
    return out


SETS['solids'] = solids
SETS['julias'] = julias


def close():
    top = cam(yaw=-1.25, pitch=1.0, dist=4.8, target='[0, 0, 0]')
    return (close_series('bas-body', '[-1, 0, 0]', top, 'L.pick(w * 0.5, h * 0.5)')
            + close_series('bas-meet', '[-1, 0, 0]', cam(yaw=-1.5708, pitch=0.9, dist=1.6, target='[-0.618, 0, 0]'), 'L.pick(w * 0.5, h * 0.5)')
            + close_series('rab-body', RABBIT, top, 'L.pick(w * 0.5, h * 0.5)')
            + close_series('m-bud', None, cam(yaw=-1.5708, pitch=0.9, dist=1.6, target='[-0.75, 0, 0]'), 'L.pick(w * 0.5, h * 0.5)'))


SETS['close'] = close


# power 3 close up, on the Mandelbrot solid: the bud that stands on the lobe of the flat set at +y, and the end of one of the four arms
def close3():
    return (close_series('n3-bud', None, cam(yaw=-1.5708, pitch=1.1, dist=1.6, target='[0, 0.95, 0]'), n=3)
            + close_series('n3-arm', None, cam(yaw=-1.5708, pitch=0.3, dist=1.6, target='[0.75, 0, 0.75]'), n=3))


SETS['close3'] = close3
