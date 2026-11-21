import json, sys
NS = [2, 3, 4, 5, 6, 8]
PS = [1, 2, 3, 4]
TYPE = "const L = window.squaringLab, $ = id => document.getElementById(id); const type = (id, v) => { const e = $(id); e.value = String(v); e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; "
for view in ('def', 'x'):
    acts = [{"js": TYPE + "L.R.warmOn = false; document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); $('qFast').click(); L.S.q.aa = 2; L.syncControls(); L.touch(); return JSON.stringify({cam: L.cam, q: L.S.q, n: L.S.n, par: L.S.param.mercator, ap: L.S.ap || L.S.approach});", "wait": "done", "timeout": 400}]
    for n in NS:
        for p in PS:
            js = TYPE + "type('powNum', %d); type('par-mercator-planesNum', %d); " % (n, p)
            js += "const camAfter = JSON.stringify(L.cam); "
            if view == 'x':
                js += "L.cam.yaw = 0; L.cam.pitch = 0; L.cam.target = [0,0,0]; L.cam.dist = 5.2; L.touch(); "
            else:
                js += "L.cam.yaw = -1.0; L.cam.pitch = 0.55; L.cam.dist = 5.2; L.cam.target = [-0.3,0,0]; L.touch(); "
            js += "return JSON.stringify({n: L.S.n, planes: L.S.param.mercator.planes, planesBox: $('par-mercator-planesNum').value, camAfter, f: $('f-mercator') ? $('f-mercator').textContent : null});"
            acts.append({"js": js, "wait": "done", "timeout": 400, "shot": "out/verify/p10/g_%s_n%d_p%d.png" % (view, n, p), "clip": "#view"})
    json.dump(acts, open('out/verify/p10/grid_%s.json' % view, 'w'), indent=1)
