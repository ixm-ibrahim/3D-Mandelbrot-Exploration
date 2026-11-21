"""Round 15, entry: the picture sets of run.py (python out/r15/entry/run.py pictures <set>)."""
from run import view3, view2, RABBIT

P = "pick('sqpillow'); await sleep(250); S.n = 2; S.iter = 14; "
SIZE = {}


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
        ('sp-m', P + view3('m')),
        ('sp-j-basilica', P + view3('j', '[-1, 0, 0]')),
        ('sp-cut-m', P + view2('m', None, -0.5, 3.2)),
    ]


def solids():
    return [
        ('sp-m', P + view3('m')),
        ('sp-m-above', P + view3('m', cam=cam(pitch=1.45))),
        ('sp-m-below', P + view3('m', cam=cam(pitch=-1.45))),
        ('sp-m-side', P + view3('m', cam=cam(yaw=-1.5708, pitch=0.0))),
        ('sp-j-basilica', P + view3('j', '[-1, 0, 0]')),
        ('sp-j-basilica-below', P + view3('j', '[-1, 0, 0]', cam=cam(pitch=-0.9))),
        ('sp-j-rabbit', P + view3('j', RABBIT)),
        ('sp-j-rabbit-below', P + view3('j', RABBIT, cam=cam(pitch=-0.9))),
        ('sp-j-off-axis', P + view3('j', '[-1, 0.15, 0.1]')),
        ('sp-j-03', P + view3('j', '[0.3, 0, 0]')),
        ('sp-j-i', P + view3('j', '[0, 1, 0]')),
        ('sp-j-i-below', P + view3('j', '[0, 1, 0]', cam=cam(pitch=-0.9))),
    ]


def cuts():
    return [
        ('sp-cut-m', P + view2('m', None, -0.5, 3.2)),
        ('sp-cut-j-basilica', P + view2('j', '[-1, 0, 0]', 0, 3.2)),
        ('sp-cut-j-rabbit', P + view2('j', RABBIT, 0, 3.2)),
        ('sp-cut-j-off-axis', P + view2('j', '[-1, 0.15, 0.1]', 0, 3.2)),
        ('sp-cut-j-03', P + view2('j', '[0.3, 0, 0]', 0, 3.2)),
        ('sp-cut-j-i', P + view2('j', '[0, 1, 0]', 0, 3.2)),
    ]


SETS = {'first': first, 'solids': solids, 'cuts': cuts}


# ---------- close-ups: the camera moves in on one point, in three steps, with more orbit steps the closer it is
WAIT = " for (let i = 0; i < 900 && !L.idle(); i++) await sleep(100); "
DEPTHS = [(1.0, 14), (0.25, 20), (0.06, 26)]


def close_series(tag, c, target_js, pitch=None, depths=DEPTHS):
    """target_js: JavaScript giving the point to move in on (may use L.pick at the opening view)"""
    out = []
    for k, (dist, it) in enumerate(depths):
        js = P + view3('j', c) + WAIT
        js += "const w = $('stage').clientWidth, h = $('stage').clientHeight; const tg = window['__tg_%s'] || (window['__tg_%s'] = %s); " % (tag, tag, target_js)
        js += "if (!tg) throw new Error('no target for %s'); L.cam.target = tg.slice(); L.cam.dist = %s; %s S.iter = %d; go(); await sleep(200); " % (tag, dist, ('L.cam.pitch = %s; ' % pitch) if pitch is not None else '', it)
        out.append(('sp-close-%s-%d' % (tag, k + 1), js))
    return out


def close():
    return (close_series('bas-body', '[-1, 0, 0]', 'L.pick(w * 0.5, h * 0.42)')
            + close_series('bas-meet', '[-1, 0, 0]', '[-0.618, 0, 0]', pitch=0.9)
            + close_series('rab-body', RABBIT, 'L.pick(w * 0.5, h * 0.5)')
            + close_series('rab-meet', RABBIT, '[-0.2737, 0.4782, 0]', pitch=0.9))


SETS['close'] = close


# the meeting places again: the flat bodies' touching point lies INSIDE the solid (a camera 0.25 away from it sees
# nothing), so the camera moves in on the skin straight above it instead
def meet():
    out = []
    for tag, c, pt in (('bas-meet', '[-1, 0, 0]', '[-0.618, 0, 0]'), ('rab-meet', RABBIT, '[-0.2737, 0.4782, 0]')):
        for k, (dist, it) in enumerate(DEPTHS):
            js = P + view3('j', c) + WAIT
            js += "const w = $('stage').clientWidth, h = $('stage').clientHeight; "
            js += "if (!window['__tg_%s']) { L.cam.target = %s; L.cam.pitch = 0.9; L.cam.dist = 1.6; go(); await sleep(300); %s window['__tg_%s'] = L.pick(w * 0.5, h * 0.5); } " % (tag, pt, WAIT, tag)
            js += "const tg = window['__tg_%s']; if (!tg) throw new Error('no target'); L.cam.target = tg.slice(); L.cam.pitch = 0.9; L.cam.dist = %s; S.iter = %d; go(); await sleep(200); " % (tag, dist, it)
            out.append(('sp-close-%s-%d' % (tag, k + 1), js))
    return out


SETS['meet'] = meet


# the same flat cuts drawn by "Sphere inversions, one plane" on the same page, to compare pixel by pixel
PM = "pick('mercator'); await sleep(250); S.n = 2; S.iter = 14; "


def flatref():
    return [
        ('ref-cut-m', PM + view2('m', None, -0.5, 3.2)),
        ('ref-cut-j-basilica', PM + view2('j', '[-1, 0, 0]', 0, 3.2)),
        ('ref-cut-j-rabbit', PM + view2('j', RABBIT, 0, 3.2)),
        ('ref-cut-j-03', PM + view2('j', '[0.3, 0, 0]', 0, 3.2)),
        ('ref-cut-j-i', PM + view2('j', '[0, 1, 0]', 0, 3.2)),
    ]


SETS['flatref'] = flatref


def powers():
    p = lambda n: "pick('sqpillow'); await sleep(250); S.n = %d; S.iter = 14; " % n
    back = " S.n = 2;"
    return [
        ('sp-m-n3', p(3) + view3('m')),
        ('sp-m-n3-side', p(3) + view3('m', cam=cam(yaw=-1.5708, pitch=0.0))),
        ('sp-cut-m-n3', p(3) + view2('m', None, 0, 3.2)),
        ('ref-cut-m-n3', "pick('mercator'); await sleep(250); S.n = 3; S.iter = 14; " + view2('m', None, 0, 3.2)),
        ('sp-m-n4', p(4) + view3('m')),
        ('sp-m-n5', p(5) + view3('m')),
        ('sp-j-n3', p(3) + view3('j', '[0.3, 0.5, 0]')),
    ]


SETS['powers'] = powers


# power 3 close up: the knobbly buds of the opening pictures, at three depths
def close3():
    out = []
    p3 = "pick('sqpillow'); await sleep(250); S.n = 3; S.iter = 14; "
    for tag, mode, c, tgt in (('n3-j', 'j', '[0.3, 0.5, 0]', 'L.pick(w * 0.5, h * 0.5)'), ('n3-m', 'm', None, 'L.pick(w * 0.2, h * 0.6)')):
        for k, (dist, it) in enumerate(DEPTHS):
            js = p3 + view3(mode, c) + WAIT
            js += "const w = $('stage').clientWidth, h = $('stage').clientHeight; const tg = window['__tg_%s'] || (window['__tg_%s'] = %s); " % (tag, tag, tgt)
            js += "if (!tg) throw new Error('no target for %s'); L.cam.target = tg.slice(); L.cam.dist = %s; S.iter = %d; go(); await sleep(200); " % (tag, dist, it)
            out.append(('sp-close-%s-%d' % (tag, k + 1), js))
    out.append(('sp-n3-reset', "S.n = 2; S.iter = 14; " + P + view3('m')))
    return out


SETS['close3'] = close3
