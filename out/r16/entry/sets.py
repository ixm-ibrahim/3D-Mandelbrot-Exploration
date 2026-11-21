"""Round 16, entry: the picture sets of run.py (python out/r16/entry/run.py pictures <set>)."""
from run import view3, view2, RABBIT

SIZE = {}
IDS = (('ta', 'turnaway'), ('tl', 'turnalong'))
REF = ('f2', 'fold')
BAS = '[-1, 0, 0]'
OFF = '[-1, 0.15, 0.1]'


def P(id_, n=2, it=14):
    return "pick('%s'); await sleep(250); S.n = %s; S.iter = %d; " % (id_, n, it)


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


ABOVE, BELOW, ALONGX = cam(pitch=1.45), cam(pitch=-1.1), cam(yaw=0.0, pitch=0.0)


# the basilica from four sides, for the two new rules and for Sphere inversions, two planes
def bas():
    out = []
    for tag, id_ in IDS + (REF,):
        out += [
            ('%s-bas-front' % tag, P(id_) + view3('j', BAS)),
            ('%s-bas-above' % tag, P(id_) + view3('j', BAS, cam=ABOVE)),
            ('%s-bas-alongx' % tag, P(id_) + view3('j', BAS, cam=ALONGX)),
            ('%s-bas-below' % tag, P(id_) + view3('j', BAS, cam=BELOW)),
        ]
    return out


# close-ups at three depths: the bud on top of the middle body (in the flat basilica it reaches from 0.52 to 0.68 on
# the upright axis), and the place where the middle body and the left body touch, (-0.618, 0, 0)
BUD = [('[0, 0, 0.6]', 0.9, 14, 0.35), ('[0, 0, 0.62]', 0.3, 20, 0.35), ('[0, 0, 0.705]', 0.09, 26, 0.35)]
MEET = [('[-0.618, 0, 0]', 1.0, 14, 0.9), ('[-0.618, 0, 0]', 0.25, 20, 0.9), ('[-0.618, 0, 0]', 0.06, 26, 0.9)]


def close():
    out = []
    for tag, id_ in IDS + (REF,):
        for nm, ser in (('bud', BUD), ('meet', MEET)):
            for k, (tg, dist, it, pitch) in enumerate(ser):
                out.append(('%s-close-%s-%d' % (tag, nm, k + 1), P(id_, 2, it) + view3('j', BAS, cam=cam(pitch=pitch, dist=dist, target=tg))))
    out.append(('reset-close', P('turnaway') + view3('j', BAS)))
    return out


# the other sets, honestly: the rabbit, a c off the flat plane, the Mandelbrot solid from three sides, the flat cuts
def others():
    out = []
    for tag, id_ in IDS:
        out += [
            ('%s-rabbit' % tag, P(id_) + view3('j', RABBIT)),
            ('%s-rabbit-above' % tag, P(id_) + view3('j', RABBIT, cam=ABOVE)),
            ('%s-off' % tag, P(id_) + view3('j', OFF)),
            ('%s-m-front' % tag, P(id_) + view3('m')),
            ('%s-m-above' % tag, P(id_) + view3('m', cam=ABOVE)),
            ('%s-m-alongx' % tag, P(id_) + view3('m', cam=ALONGX)),
            ('%s-m-side' % tag, P(id_) + view3('m', cam=cam(yaw=-1.5708, pitch=0.0))),
        ]
    return out


def cuts():
    out = []
    for tag, id_ in IDS + (('ref', 'mercator'),):
        out += [
            ('%s-cut-m' % tag, P(id_) + view2('m', None, -0.5, 3.2)),
            ('%s-cut-bas' % tag, P(id_) + view2('j', BAS, 0, 3.2)),
            ('%s-cut-rabbit' % tag, P(id_) + view2('j', RABBIT, 0, 3.2)),
            ('%s-cut-off' % tag, P(id_) + view2('j', OFF, 0, 3.2)),
        ]
    out.append(('reset-cuts', P('turnaway') + view3('j', BAS)))
    return out


# whole powers: the count round the x-axis should follow the power. Power 3 has no period-2 body on the x-axis (its
# flat set reaches from -0.385 to 0.385 there), so: power 3 with c = (0.3, 0, 0) and with c = (0, 1, 0), the middle of
# its period-2 body; power 4 with c = -1, the middle of its period-2 body on the x-axis.
def powers():
    out = []
    for tag, id_ in IDS:
        out += [
            ('%s-n3-j03-front' % tag, P(id_, 3) + view3('j', '[0.3, 0, 0]')),
            ('%s-n3-j03-alongx' % tag, P(id_, 3) + view3('j', '[0.3, 0, 0]', cam=ALONGX)),
            ('%s-n3-ji-front' % tag, P(id_, 3) + view3('j', '[0, 1, 0]')),
            ('%s-n3-ji-alongx' % tag, P(id_, 3) + view3('j', '[0, 1, 0]', cam=ALONGX)),
            ('%s-n4-bas-front' % tag, P(id_, 4) + view3('j', BAS)),
            ('%s-n4-bas-alongx' % tag, P(id_, 4) + view3('j', BAS, cam=ALONGX)),
            ('%s-n3-m' % tag, P(id_, 3) + view3('m')),
            ('%s-n3-m-alongx' % tag, P(id_, 3) + view3('m', cam=ALONGX)),
            ('%s-n4-m' % tag, P(id_, 4) + view3('m')),
        ]
    out.append(('reset-powers', P('turnaway') + view3('j', BAS)))
    return out


SETS = {'bas': bas, 'close': close, 'others': others, 'cuts': cuts, 'powers': powers}


# the same pictures with the page's "Distance estimate" set to "Rough" (S.q.de = 0) instead of "Exact" (the default)
ROUGH, EXACT = 'S.q.de = 0; ', 'S.q.de = 3; '


def rough():
    out = []
    for tag, id_ in IDS:
        out += [
            ('%s0-bas-front' % tag, P(id_) + ROUGH + view3('j', BAS)),
            ('%s0-bas-above' % tag, P(id_) + ROUGH + view3('j', BAS, cam=ABOVE)),
            ('%s0-bas-alongx' % tag, P(id_) + ROUGH + view3('j', BAS, cam=ALONGX)),
            ('%s0-bas-below' % tag, P(id_) + ROUGH + view3('j', BAS, cam=BELOW)),
        ]
        for nm, ser in (('bud', BUD), ('meet', MEET)):
            for k, (tg, dist, it, pitch) in enumerate(ser):
                out.append(('%s0-close-%s-%d' % (tag, nm, k + 1), P(id_, 2, it) + ROUGH + view3('j', BAS, cam=cam(pitch=pitch, dist=dist, target=tg))))
    out.append(('f20-bas-front', P('fold') + ROUGH + view3('j', BAS)))
    out.append(('reset-rough', P('turnaway') + EXACT + view3('j', BAS)))
    return out


SETS['rough'] = rough


# everything else in one run: the other sets and the powers with the Rough estimate (the Exact one draws fog for
# "away"), one Exact picture of each Mandelbrot solid and rabbit to show what the page draws as it opens, the flat cuts
def rest():
    out = []
    for tag, id_ in IDS:
        R = P(id_) + ROUGH
        out += [
            ('%s0-rabbit' % tag, R + view3('j', RABBIT)),
            ('%s0-rabbit-above' % tag, R + view3('j', RABBIT, cam=ABOVE)),
            ('%s0-off' % tag, R + view3('j', OFF)),
            ('%s0-m-front' % tag, R + view3('m')),
            ('%s0-m-above' % tag, R + view3('m', cam=ABOVE)),
            ('%s0-m-alongx' % tag, R + view3('m', cam=ALONGX)),
            ('%s0-m-side' % tag, R + view3('m', cam=cam(yaw=-1.5708, pitch=0.0))),
            ('%s0-meet-60' % tag, P(id_, 2, 60) + ROUGH + view3('j', BAS, cam=cam(pitch=0.9, dist=0.25, target='[-0.618, 0, 0]'))),
        ]
        for n, c, nm in ((3, '[0.3, 0, 0]', 'n3-j03'), (3, '[0, 1, 0]', 'n3-ji'), (4, BAS, 'n4-bas')):
            out.append(('%s0-%s-front' % (tag, nm), P(id_, n) + ROUGH + view3('j', c)))
            out.append(('%s0-%s-alongx' % (tag, nm), P(id_, n) + ROUGH + view3('j', c, cam=ALONGX)))
        out += [
            ('%s0-n3-m' % tag, P(id_, 3) + ROUGH + view3('m')),
            ('%s0-n3-m-alongx' % tag, P(id_, 3) + ROUGH + view3('m', cam=ALONGX)),
            ('%s0-n4-m' % tag, P(id_, 4) + ROUGH + view3('m')),
            ('%s-m-front' % tag, P(id_) + EXACT + view3('m')),
            ('%s-rabbit' % tag, P(id_) + EXACT + view3('j', RABBIT)),
            ('%s-n4-bas-front' % tag, P(id_, 4) + EXACT + view3('j', BAS)),
        ]
    out.append(('f20-meet-60', P('fold', 2, 60) + ROUGH + view3('j', BAS, cam=cam(pitch=0.9, dist=0.25, target='[-0.618, 0, 0]'))))
    out.append(('f2-rabbit', P('fold') + EXACT + view3('j', RABBIT)))
    out.append(('f2-m-front', P('fold') + EXACT + view3('m')))
    return out + [(n, 'S.q.de = 3; ' + js) for n, js in cuts()]


SETS['rest'] = rest


# the flat cuts again with the Rough estimate (no neighbouring orbits), to see whether the few pixels that differ
# from Sphere inversions, one plane come from the distance estimate looking sideways out of the plane
def cuts0():
    out = []
    for tag, id_ in IDS + (('ref', 'mercator'),):
        out += [
            ('%s0-cut-m' % tag, P(id_) + ROUGH + view2('m', None, -0.5, 3.2)),
            ('%s0-cut-bas' % tag, P(id_) + ROUGH + view2('j', BAS, 0, 3.2)),
            ('%s0-cut-rabbit' % tag, P(id_) + ROUGH + view2('j', RABBIT, 0, 3.2)),
        ]
    out.append(('reset-cuts0', P('turnaway') + EXACT + view3('j', BAS)))
    return out


SETS['cuts0'] = cuts0
