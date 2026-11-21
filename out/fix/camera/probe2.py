import json
PROBE = """const L = window.squaringLab, S = L.S, cam = L.cam; const w = document.getElementById('stage').clientWidth, h = document.getElementById('stage').clientHeight;
const keep = [cam.dist, cam.target.slice(), S.view.fov, cam.yaw, cam.pitch]; let best = null;
const one = (yaw, pitch, half) => { cam.yaw = yaw; cam.pitch = pitch; cam.target = [0,0,0]; cam.dist = 400; S.view.fov = half / 400; let n = 0, r = 0; const N = 22; for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) { const p = L.pick((i + 0.5) * h / N + (w - h) / 2, (j + 0.5) * h / N); if (p) { n++; r = Math.max(r, Math.hypot(p[0], p[1], p[2])); } } return [n, +r.toFixed(2)]; };
const a = one(-1, 0.55, S.view.bound), b = one(0.6, 0.1, S.view.bound), c = one(-1, 0.55, Math.max(a[1], b[1]) * 1.3 || 1), d = one(2.2, -0.4, Math.max(a[1], b[1]) * 1.3 || 1);
cam.dist = keep[0]; cam.target = keep[1]; S.view.fov = keep[2]; cam.yaw = keep[3]; cam.pitch = keep[4];
return [TAG, a, b, c, d];"""
acts = [{"js": "const L = window.squaringLab; Object.assign(L.S.q, { res: 0.4, aa: 1, shadow: false, ao: false }); L.touch();"}, {"wait": "done", "timeout": 200}]
for ap in ("mercator", "bulb"):
    for mode in ("m", "j"):
        for n in (-1, -2, -2.5, -3, -4, -8, 2, 3, 8):
            if ap == "bulb" and (mode == "j" or n in (-1, -2.5, 3)): continue
            acts.append({"js": "const L = window.squaringLab; L.S.approach = L.APPROACHES.findIndex(a => a.id === '%s'); L.S.mode = '%s'; L.S.n = %s; L.refresh(false);" % (ap, mode, n)})
            acts.append({"wait": "done", "timeout": 200})
            acts.append({"js": PROBE.replace("TAG", json.dumps("%s %s n=%s" % (ap, mode, n)))})
json.dump(acts, open("out/fix/camera/probe2.json", "w"), indent=1)
