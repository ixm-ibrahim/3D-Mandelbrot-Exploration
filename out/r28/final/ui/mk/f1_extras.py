"""Round 28, dial checker (ui): the part "extras" of f1.py, kept in a file of its own (f1.py calls extras(...)).
More of section 1.4 f after the first run: large typed sizes with and without Frame it, the touching cases framed,
an emptied box, Escape, a click elsewhere, and keys on the other two dials. Real input throughout, except one line
that says "(by script)".
"""
PROBE2 = """const w = $('stage').clientWidth, hh = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 29; i++) for (let j = 0; j < 21; j++) { const hit = !!L.pick(w * (i + 0.5) / 29, hh * (j + 0.5) / 21); if (hit) { n++; if (i === 0 || j === 0 || i === 28 || j === 20) ring++; } }
  return { hits: n, rim: ring, reach: L.ballsReach(), bound: S.view.bound, dist: L.cam.dist, zmax: S.view.zmax, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', status: $('status').textContent };"""
FLAT2 = """const N = 240, side = S.v2.h, asp = $('stage').clientWidth / $('stage').clientHeight; let rim = 0, inside = 0;
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) { const x = S.v2.x + side * asp * ((i + 0.5) / N - 0.5), y = S.v2.y + side * ((j + 0.5) / N - 0.5); if (L.ballsInside(x, y, +S.cut || 0)) { inside++; if (i === 0 || j === 0 || i === N - 1 || j === N - 1) rim++; } }
  return { inside, rim, h: side, hmax: S.v2.hmax, reach: L.ballsReach(), halfw: side * asp / 2, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '' };"""


def extras(h, say, check, st, reset, typed, to_balls, brief, wrong, SHOTS, TAG):
    say('--- more, after the first run: large typed sizes, touching, keys on the other two dials')
    h.click('#resetAll'); h.done(); to_balls(h)
    for p in ('1000', '2000', '1'):
        reset(h); h.click('#ballsFrame'); st(h)
        h.js("S.view.bound = 8; L.syncControls(); L.touch(); return 1;"); st(h)       # (by script: the Drawing radius back to its start value, as on a fresh page)
        s = typed(h, 'Size', p); a = h.js(PROBE2)
        h.shot('%s/%s-x-size-%s-typed-no-frame.png' % (SHOTS, TAG, p), '#stage')
        say('size %s typed from the start view, Frame it not pressed: %d of 609 probes hit, %d on the rim; reach %.2f, Drawing radius %.2f; sentence "%s"' % (p, a['hits'], a['rim'], a['reach'], a['bound'], a['warn']))
        h.click('#ballsFrame'); s = st(h); b = h.js(PROBE2)
        h.shot('%s/%s-x-size-%s-framed-3d.png' % (SHOTS, TAG, p), '#stage')
        ok = b['rim'] == 0 and b['bound'] >= b['reach'] and b['hits'] > 0
        say('size %s, Frame it: %d probes hit, %d on the rim; reach %.2f, Drawing radius %.2f, camera distance %.2f (zoom limit %.2f); sentence "%s"; status "%s"  -> %s' % (
            p, b['hits'], b['rim'], b['reach'], b['bound'], b['dist'], b['zmax'], b['warn'], b['status'], 'OK (whole chain in the picture)' if ok else 'WRONG: the chain is not whole in the picture'))
        if not ok:
            wrong.append('Frame it at %s does not show the whole chain' % p)
        h.click('#flat'); st(h); h.click('#ballsFrame'); st(h)
        c = h.js(FLAT2)
        h.shot('%s/%s-x-size-%s-framed-2d.png' % (SHOTS, TAG, p), '#stage')
        ok2 = c['rim'] == 0 and c['halfw'] >= c['reach'] and c['inside'] > 0
        say('size %s, 2D view, Frame it: view %.2f high (limit %.2f), half its width %.2f, reach %.2f; %d of 57600 points inside, %d on the rim; sentence "%s"  -> %s' % (
            p, c['h'], c['hmax'], c['halfw'], c['reach'], c['inside'], c['rim'], c['warn'], 'OK' if ok2 else 'WRONG: the chain is not whole in the 2D view'))
        if not ok2:
            wrong.append('Frame it at %s, 2D view, does not show the whole chain' % p)
        h.click('#flat'); st(h)
    for label, steps in (('rho50-size200-touch', [('Rho', '50'), ('Size', '200')]), ('rho50-size190', [('Rho', '50'), ('Size', '190')]), ('rho50-size55.56', [('Rho', '50')]),
                         ('rho25-size400-touch', [('Rho', '25'), ('Size', '400')]), ('size100-equal-touch', [('Size', '100')]), ('size100.1', [('Size', '100.1')])):
        reset(h)
        for d, v in steps:
            typed(h, d, v)
        h.click('#ballsFrame'); s = st(h); b = h.js(PROBE2)
        h.shot('%s/%s-x-%s-framed-3d.png' % (SHOTS, TAG, label), '#stage')
        h.click('#flat'); st(h); h.click('#ballsFrame'); s2 = st(h)
        h.shot('%s/%s-x-%s-framed-2d.png' % (SHOTS, TAG, label), '#stage')
        h.click('#flat'); st(h)
        say('%s, Frame it: %s; %d probes hit, %d on the rim; reach %s, Drawing radius %.2f; in the 2D view the sentence reads "%s"' % (label, brief(s), b['hits'], b['rim'], b['reach'], b['bound'], s2['warn']))
    # an emptied box, and Escape
    reset(h); s = typed(h, 'Size', '')
    check('size box emptied (Ctrl+A, Backspace) and Enter', s, dict(size=55.56, rho=100, flag=('size', 'invalid')))
    h.click('#ballsSizeNum'); h.key('a', ctrl=True); h.chars('777'); h.key('Escape'); s = st(h)
    check('"777" typed into the size box and then Escape', s, dict(size=55.56, rho=100, warn_none=1))
    h.click('#ballsNote'); s = st(h)
    check('then a click elsewhere', s, dict(size=55.56, rho=100, warn_none=1))
    h.click('#ballsSizeNum'); h.key('a', ctrl=True); h.chars('170'); h.click('#ballsNote'); s = st(h)
    check('"170" typed into the size box and then a click elsewhere (no Enter)', s, dict(size=170, rho=29.41))
    # keys at the ends of the size dial and on its slider
    reset(h); typed(h, 'Size', '2000'); h.click('#ballsSizeNum'); h.key('ArrowUp'); s = st(h)
    check('size 2000, Arrow-up in the box', s, dict(size=2000, rho=2.5))
    h.key('ArrowDown'); s = st(h)
    check('then Arrow-down', s, dict(size=1999.9, rho=2.5))
    reset(h); typed(h, 'Size', '1'); h.click('#ballsSizeNum'); h.key('ArrowDown'); s = st(h)
    check('size 1, Arrow-down in the box', s, dict(size=1, rho=100))
    reset(h); typed(h, 'Size', '100'); x, y, _ = h.thumb('#ballsSize'); h.click_at(x, y); s = st(h)
    say('pressed the size slider\'s thumb at 100 to give it the focus: %s; focus on %s' % (brief(s), h.js("return document.activeElement.id;")))
    p0 = float(s['size']['box'])
    h.key('ArrowRight'); s = st(h)
    check('size slider, key ArrowRight from %g' % p0, s, dict(size=round(p0 + 0.1, 1)))
    h.key('End'); s = st(h)
    check('size slider, key End', s, dict(size=400, rho=12.5))
    h.key('Home'); s = st(h)
    check('size slider, key Home', s, dict(size=2), note='second sphere %s' % s['rho']['box'])
    reset(h); typed(h, 'Size', '100'); h.click('#ballsSizeNum ~ .dial-steps .dial-up'); s = st(h)
    check('size 100, step button up', s, dict(size=100.1, rho=49.95))
    h.click('#ballsSizeStep'); h.click('#ballsSizeNum ~ .dial-steps .dial-up'); s = st(h)
    check('the size dial\'s step choice switched to whole numbers, step up', s, dict(size=101, rho=49.5))
    h.click('#ballsSizeStep')
    reset(h); x, y, _ = h.thumb('#ballsDepth'); h.click_at(x, y); h.key('ArrowLeft'); s = st(h)
    check('depth slider, key ArrowLeft from 16', s, dict(depth=15))
    h.key('Home'); s = st(h)
    check('depth slider, key Home', s, dict(depth=1, warn_has='so few rounds'))
    h.key('End'); s = st(h)
    check('depth slider, key End', s, dict(depth=100, warn_none=1))
    h.click('#ballsDepthNum'); h.key('ArrowUp'); s = st(h)
    check('depth box, Arrow-up from 100', s, dict(depth=101))
    h.key('PageUp'); s = st(h)
    check('depth box, Page-up', s, dict(depth=111))
    reset(h)
