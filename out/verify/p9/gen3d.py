import json
acts = [{"js": "const L = window.squaringLab, $ = id => document.getElementById(id); L.R.warmOn = false; document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); $('ap-mercator').click(); L.S.q.aa = 3; L.syncControls(); L.touch(); const r = document.querySelector('#rules .rule'); return JSON.stringify({name: L.APPROACHES[0].name, par: L.S.param.mercator, panel: r ? r.innerText : null});", "wait": "done", "timeout": 400}]
for n in range(2, 9):
    acts.append({"js": "const L = window.squaringLab; L.S.n = %d; L.syncControls(); L.refresh(false); L.resetCam(); L.touch(); return JSON.stringify({n: L.S.n, cam: [L.cam.yaw, L.cam.pitch, L.cam.dist]});" % n,
                 "wait": "done", "timeout": 400, "shot": "out/verify/p9/s3d_n%d.png" % n, "clip": "#stage"})
# second angle, looking along the plane z=0 from the side and from above, n = 2, 3, 8
for n in (2, 3, 8):
    acts.append({"js": "const L = window.squaringLab; L.S.n = %d; L.syncControls(); L.refresh(false); L.resetCam(); L.cam.yaw = 0.4; L.cam.pitch = 0.08; L.touch(); return 'side n=%d';" % (n, n),
                 "wait": "done", "timeout": 400, "shot": "out/verify/p9/s3d_side_n%d.png" % n, "clip": "#stage"})
# Julia c = -1 in 3D for n = 2
acts.append({"js": "const L = window.squaringLab, $ = id => document.getElementById(id); $('mode-j').click(); L.S.n = 2; L.S.c = [-1,0,0]; L.syncControls(); L.refresh(false); L.resetCam(); L.touch(); return 'julia';",
             "wait": "done", "timeout": 400, "shot": "out/verify/p9/s3d_julia_n2.png", "clip": "#stage"})
REF = """
const refIn = (x, y, n, jul, c) => { let zx = jul ? x : 0, zy = jul ? y : 0; const cx = jul ? c[0] : x, cy = jul ? c[1] : y; for (let k = 0; k <= 14; k++) { const r = Math.hypot(zx, zy); if (r > 64) return false; if (k === 14) break; const a = Math.atan2(zy, zx) * n, m = Math.pow(r, n); zx = (r > 0 ? m * Math.cos(a) : 0) + cx; zy = (r > 0 ? m * Math.sin(a) : 0) + cy; } return true; };
"""
def cutcase(ap, n, mode, tag):
    js = ("const L = window.squaringLab, $ = id => document.getElementById(id);" + REF +
          "$('ap-%s').click(); $('mode-%s').click(); L.S.n = %d; L.S.iter = 14; L.S.c = [-1,0,0]; L.S.cutOn = true; L.S.cut = 0; L.syncControls(); L.refresh(false); L.resetCam(); L.cam.target = [%g,0,0]; L.cam.yaw = -Math.PI/2; L.cam.pitch = 1.5607; L.cam.dist = 5.5; L.touch();"
          "for (let i = 0; i < 4000 && !L.idle(); i++) await new Promise(r => setTimeout(r, 100));"
          "const st = $('stage'), w = st.clientWidth, h = st.clientHeight, b = L.basis(), fov = L.S.view.fov; let tot = 0, bad = 0, face = 0, refc = 0, maxerr = 0, nearBad = 0; const badpts = [];"
          "const jul = L.S.mode === 'j';"
          "const pl = (px, py) => { const u = (2 * px - w) / h * fov, v = (h - 2 * py) / h * fov; const d = [0,1,2].map(i => b.f[i] + u * b.right[i] + v * b.up[i]); const t = -b.pos[2] / d[2]; return [b.pos[0] + t * d[0], b.pos[1] + t * d[1]]; };"
          "const eps = 2.5 * 2 * L.cam.dist * fov / h;"
          "for (let py = 4; py < h; py += 8) for (let px = 4; px < w; px += 8) { const P = pl(px, py); const got = L.pick(px, py); const onFace = !!got && Math.abs(got[2]) < 1e-3; if (onFace) { face++; maxerr = Math.max(maxerr, Math.hypot(got[0] - P[0], got[1] - P[1])); } const r = refIn(P[0], P[1], %d, jul, L.S.c); if (r) refc++; tot++; if (r !== onFace) { bad++; let mixed = false; for (const [dx, dy] of [[eps,0],[-eps,0],[0,eps],[0,-eps],[eps,eps],[-eps,-eps],[eps,-eps],[-eps,eps]]) if (refIn(P[0] + dx, P[1] + dy, %d, jul, L.S.c) !== r) mixed = true; if (mixed) nearBad++; else if (badpts.length < 8) badpts.push([px, py, +P[0].toFixed(3), +P[1].toFixed(3), r, got]); } }"
          "return JSON.stringify({case: '%s', ap: L.APPROACHES[L.S.approach].id, n: L.S.n, mode: L.S.mode, w, h, tot, face, refc, bad, nearBad, farBad: bad - nearBad, pickVsRayMaxErr: maxerr, badpts, hView: 2 * L.cam.dist * fov, basis: b});"
          % (ap, mode, n, -0.5 if (mode == 'm' and n == 2) else 0, n, n, tag))
    return {"js": js, "wait": "done", "timeout": 600, "shot": "out/verify/p9/cut3d_%s.png" % tag, "clip": "#stage"}
acts.append({"js": "const L = window.squaringLab; L.S.colour.mode = 7; L.syncControls(); return 'clay';"})
for ap, n, mode in [('mercator', 2, 'm'), ('mercator', 3, 'j'), ('lathe', 2, 'm'), ('bulb', 5, 'm'), ('split', 2, 'j'), ('mercator', 8, 'm')]:
    acts.append(cutcase(ap, n, mode, '%s_n%d_%s' % (ap, n, mode)))
json.dump(acts, open('out/verify/p9/act3d.json', 'w'))
