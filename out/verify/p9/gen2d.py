import json, sys
APS = ['mercator', 'lathe', 'bulb', 'split', 'classic']
NS = [2, 3, 5, 8]
SCENES = [('m', None), ('j', [-1, 0, 0]), ('j', [-0.122561, 0.744862, 0])]
def win(mode, n):
    if mode == 'm':
        return (-0.5, 0, 3.2) if n == 2 else (0, 0, 3.0)
    return (0, 0, 3.6)
def build(aps, tag):
    acts = [{"js": "const L = window.squaringLab, $ = id => document.getElementById(id); L.R.warmOn = false; L.S.q.aa = 2; L.S.colour.mode = 7; L.S.cut = 0; L.syncControls(); $('flat').click(); const st = $('stage'), cv = $('view'); [...st.querySelectorAll('*')].forEach(e => { if (e !== cv && !e.contains(cv)) e.style.visibility = 'hidden'; }); L.touch(); return JSON.stringify({flat: L.S.flat, iter: L.S.iter, res: L.S.q.res, cw: cv.width, ch: cv.height, sw: st.clientWidth, sh: st.clientHeight, params: L.S.param});", "wait": "done", "timeout": 400}]
    for a in aps:
        for n in NS:
            for si, (mode, c) in enumerate(SCENES):
                x, y, h = win(mode, n)
                js = ("const L = window.squaringLab, $ = id => document.getElementById(id); $('ap-%s').click(); $('mode-%s').click(); L.S.n = %d; L.S.iter = 14; %s L.S.cut = 0; L.S.v2.x = %g; L.S.v2.y = %g; L.S.v2.h = %g; L.syncControls(); L.refresh(false); L.touch(); return JSON.stringify({ap: L.APPROACHES[L.S.approach].id, n: L.S.n, mode: L.S.mode, c: L.S.c, flat: L.S.flat, cut: L.S.cut, v2: L.S.v2, par: L.S.param['%s']});"
                      % (a, mode, n, ("L.S.c = %s;" % json.dumps(c)) if c else "", x, y, h, a))
                acts.append({"js": js, "wait": "done", "timeout": 400, "shot": "out/verify/p9/f_%s_n%d_s%d.png" % (a, n, si), "clip": "#view"})
    json.dump(acts, open('out/verify/p9/act2d_%s.json' % tag, 'w'))
build(['mercator', 'lathe'], 'a'); build(['bulb', 'split', 'classic'], 'b')
