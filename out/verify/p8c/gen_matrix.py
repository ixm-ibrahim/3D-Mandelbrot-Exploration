import json, os
HERE = 'out/verify/p8c'
PRE = "const L = window.squaringLab, $ = id => document.getElementById(id); const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; "
SETUP = {
  'm': PRE + "L.R.warmOn = false; L.S.q.aa = 3; L.S.view.zmax = 1000; L.touch(); return 'mandel';",
  'k': PRE + "L.R.warmOn = false; $('mode-k').click(); L.S.q.aa = 3; L.S.view.zmax = 1000; L.touch(); return 'klein default';",
  'k2': PRE + "L.R.warmOn = false; $('mode-k').click(); L.S.q.aa = 3; L.S.view.zmax = 1000; type('kcyNum', '0.05'); return 'klein cy=' + L.S.k.cy;",
  'n': PRE + "L.R.warmOn = false; L.S.q.aa = 3; L.S.view.zmax = 1000; type('powNum', '-2'); return 'n=' + L.S.n;",
}
for key, setup in SETUP.items():
    acts = [{"js": setup, "wait": "done", "timeout": 400}]
    dists = [30, 60, 150, 400]; bounds = [8, 30, 100, 500]
    for D in dists:
        for B in bounds:
            js = PRE + ("L.cam.target = [0,0,0]; L.cam.dist = %d; type('viewBoundNum', '%d'); L.touch(); const t0 = performance.now(); "
                        "return {dist: L.cam.dist, bound: L.S.view.bound, zmax: L.S.view.zmax, val: $('camVal').textContent};" % (D, B))
            acts.append({"js": js, "wait": "done", "timeout": 400, "shot": "%s/mx-%s-d%d-b%d.png" % (HERE, key, D, B), "clip": "#stage"})
    json.dump(acts, open('%s/mx-%s.json' % (HERE, key), 'w'), indent=0)
print('ok')
