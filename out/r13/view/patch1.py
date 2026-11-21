"""One-off edits to src/js/66-learn-view.js (the view engineer's own file): exact-text replacements, each must match once."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, "src", "js", "66-learn-view.js")
with io.open(path, encoding="utf-8") as f:
    text = f.read()
edits = [
 ("const LEARN_V_FITS = [1.35, 1.8, 2.4, 3.2, 4.4, 6, 8, 10];",
  "const LEARN_V_FITS = [1.25, 1.5, 1.8, 2.2, 2.7, 3.3, 4, 5, 6.5, 8, 10];"),
 ("L.fit = LEARN_V_FITS.find(f => f >= R * 1.1) ||", "L.fit = LEARN_V_FITS.find(f => f >= R * 1.06) ||"),
 ("const s = (vk === 'f1' ? (w / 2 - 26) / fit : Math.min(w, h) / 2 * 0.9 / fit) * V.zoom;",
  "const s = (vk === 'f1' ? (w / 2 - 26) / fit : Math.min(w, h) / 2 * 0.93 / fit) * V.zoom;"),
 ("const s = (vk === 'h1' ? Math.min(w / 2 * 0.92 / fit, h / 2 * 0.9 / (fit * 0.8)) : Math.min(w * 0.62, h) / 2 * 0.88 / fit) * V.zoom;",
  "// a sheet seen at a slant is wide and low, so it may use the width; the ball of space needs the height\n"
  "  const s = (vk === 's3' ? Math.min(w, h) / 2 * 0.93 / fit : Math.min(w / 2 * 0.95 / (fit * 1.3), h / 2 * 0.92 / (fit * (vk === 'h1' ? 0.98 : 0.74)))) * V.zoom;"),
 ("  const ra = len(a);\n",
  "  // the flat sheet the point travels in: through the point, with its centre on the hinge\n"
  "  const ra = len(a);\n"
  "  let ctr = O, rs = ra;\n"
  "  if (fr) { const iu = dot(a, fr[0]), iw = dot(a, fr[1]); ctr = sub(a, add(scl(fr[0], iu), scl(fr[1], iw))); rs = Math.hypot(iu, iw); }\n"
  "  const round = (r, n) => circle(fr[0], fr[1], r, n).map(v => add(ctr, v));\n"),
 ("    trace(circle(fr[0], fr[1], ra), true); fill(C.ok, 0.1);\n    trace(circle(fr[0], fr[1], ra), true); stroke(C.ok, 1.25, 0.55);",
  "    trace(round(rs), true); fill(C.ok, 0.1);\n    trace(round(rs), true); stroke(C.ok, 1.25, 0.55);\n"
  "    seg(ctr, add(ctr, scl(fr[0], rs)), C.ink2, 1, 0.7, [4, 4]);"),
 ("if (sheet && fr && vk !== 'f1' && ra > 1e-6) {", "if (sheet && fr && vk !== 'f1' && rs > 1e-6) {"),
 ("if ((hinge || sheet) && so.length > 2) { trace([O].concat(so), true); fill(C.brass, 0.17); }",
  "if ((hinge || sheet) && so.length > 2) { trace([ctr].concat(so), true); fill(C.brass, 0.2); }"),
 ("else if (j > at.j) { trace(path); stroke(C.ink2, 1.25, 0.5, [2, 4]); }", "else if (j > at.j) { trace(path); stroke(C.ink2, 1.25, 0.42, [1.5, 5]); }"),
 ("if (K.paths[at.j]) { trace(K.paths[at.j].slice(Math.floor(at.t * N + 1e-9))); stroke(C.ink2, 1.25, 0.5, [2, 4]); }",
  "if (K.paths[at.j]) { trace(K.paths[at.j].slice(Math.floor(at.t * N + 1e-9))); stroke(C.ink2, 1.25, 0.42, [1.5, 5]); }"),
 ("const rw = Math.min(34 / P.s, 0.5 * ra), arc = [], steps = Math.max(8, Math.ceil(Math.abs(an) / 0.08));",
  "const rw = Math.min(34 / P.s, 0.5 * rs), arc = [], steps = Math.max(8, Math.ceil(Math.abs(an) / 0.08));"),
 ("arc.push(add(scl(fr[0], rw * Math.cos(q)), scl(fr[1], rw * Math.sin(q)))); }",
  "arc.push(add(ctr, add(scl(fr[0], rw * Math.cos(q)), scl(fr[1], rw * Math.sin(q))))); }"),
 ("const mid = an / 2, out = (34 / P.s * 1.0 + 16 / P.s);", "const mid = an / 2, out = rw + 17 / P.s;"),
 ("tag(add(scl(fr[0], out * Math.cos(mid)), scl(fr[1], out * Math.sin(mid))), learnVDeg(an),",
  "tag(add(ctr, add(scl(fr[0], out * Math.cos(mid)), scl(fr[1], out * Math.sin(mid)))), learnVDeg(an),"),
 ("  if (apart > 26) tag(start, 'start', C.ink2, -11, -11, 'right');",
  "  // labels stand clear of the arm: the point's outwards from the centre, the start's to the side the turn leaves behind\n"
  "  const away = (q, gap, side) => { let dx = q[0] - P.cx, dy = q[1] - P.cy; const d = Math.hypot(dx, dy); if (d < 2) { dx = 0.7; dy = -0.7; } else { dx /= d; dy /= d; } if (side) [dx, dy] = [-dy, dx]; return [q[0] + dx * gap, q[1] + dy * gap, dx > 0.35 ? 'left' : dx < -0.35 ? 'right' : 'center']; };\n"
  "  if (apart > 26) { if (vk === 'f1') label('start', qs[0], qs[1] + 36, C.ink2, 'center'); else { const t = away(qs, 19, true); label('start', t[0], t[1], C.ink2, t[2]); } }"),
 ("  disc(p, 7.5, C.stage); disc(p, 6, C.brass, off ? 0.35 : 1); if (off) ring(p, 6, C.brass, 1.75);\n"
  "  tag(p, at.done ? 'new z' : 'z', C.brass, 11, vk === 'f1' ? -20 : -11, 'left', small ? 13 : 15, 600);",
  "  disc(p, 8.5, C.stage); disc(p, 6.5, C.brass, off ? 0.35 : 1); if (off) ring(p, 6.5, C.brass, 1.75);\n"
  "  { const t = vk === 'f1' ? [qp[0], qp[1] - 22, 'center'] : away(qp, 18, false); label(at.done ? 'new z' : 'z', t[0], t[1], C.brass, t[2], small ? 13.5 : 15.5, 600); }"),
]
bad = 0
for old, new in edits:
    n = text.count(old)
    if n != 1:
        print("MATCHES", n, ":", old[:90]); bad += 1; continue
    text = text.replace(old, new)
if bad:
    sys.exit("nothing written")
with io.open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print("ok", len(edits))
