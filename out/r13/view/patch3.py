"""One-off edits to src/js/66-learn-view.js (the view engineer's own file): exact-text replacements, each must match once."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, "src", "js", "66-learn-view.js")
with io.open(path, encoding="utf-8") as f:
    text = f.read()
edits = [
 # the helper, in front of the builder
 ("// ---------- the plan: the moves of the step on show, and everything the picture needs from them\n",
  "// What a move turns the point a about, and the flat sheet the point travels in: the hinge (or null), the sheet as\n"
  "// the move gives it (or null), two directions at right angles that span it, its centre (on the hinge) and how far\n"
  "// the point is from that centre.\n"
  "function learnVSheet(m, a) {\n"
  "  let hinge = null, sheet = null, fr = null;\n"
  "  try { hinge = m.hinge ? m.hinge(a) : null; sheet = m.sheet ? m.sheet(a) : null; } catch (e) { hinge = sheet = null; }\n"
  "  if (hinge && !(learnVFinite(hinge) && len(hinge) > 1e-9)) hinge = null;\n"
  "  if (sheet && !(sheet.length === 2 && learnVFinite(sheet[0]) && learnVFinite(sheet[1]))) sheet = null;\n"
  "  if (sheet) { const u = norm(sheet[0]), w0 = sub(sheet[1], scl(u, dot(u, sheet[1]))); if (len(w0) > 1e-9) fr = [u, norm(w0)]; }\n"
  "  if (!fr && hinge) {\n"
  "    const hn = norm(hinge); let r0 = sub([1, 0, 0], scl(hn, hn[0]));\n"
  "    if (len(r0) < 1e-6) r0 = sub([0, 1, 0], scl(hn, hn[1]));\n"
  "    r0 = norm(r0); fr = [r0, cross(hn, r0)];\n"
  "  }\n"
  "  let ctr = [0, 0, 0], rs = len(a);\n"
  "  if (fr) { const iu = dot(a, fr[0]), iw = dot(a, fr[1]); ctr = sub(a, add(scl(fr[0], iu), scl(fr[1], iw))); rs = Math.hypot(iu, iw); }\n"
  "  return { hinge: hinge ? norm(hinge) : null, sheet, fr, ctr, rs };\n"
  "}\n"
  "// ---------- the plan: the moves of the step on show, and everything the picture needs from them\n"),
 # frames
 ("  if (!L.fitHold) {\n    const key = [[0, 0, 0]], lo = [0, 0, 0], hi = [0, 0, 0];\n",
  "  const sheets = moves.map((m, j) => learnVSheet(m, pts[j]));\n"
  "  if (!L.fitHold) {\n    const key = [[0, 0, 0]];\n"),
 ("    key.forEach(v => { for (let i = 0; i < 3; i++) { lo[i] = Math.min(lo[i], v[i]); hi[i] = Math.max(hi[i], v[i]); } });\n"
  "    const ctr = lo.map((x, i) => Math.round((x + hi[i]) / 2 * 4) / 4 + 0);\n"
  "    let hx = 0.55, hy = 0.55, rr = 0.75, reach = 1;\n"
  "    key.forEach(v => { hx = Math.max(hx, Math.abs(v[0] - ctr[0])); hy = Math.max(hy, Math.abs(v[1] - ctr[1])); rr = Math.max(rr, len(sub(v, ctr))); reach = Math.max(reach, Math.abs(v[0]), Math.abs(v[1]), Math.abs(v[2])); });\n"
  "    L.frame = { ctr, hx, hy, rr, reach: Math.max(1, Math.ceil(reach - 0.2)) };\n"
  "    L.fit = rr;\n"
  "  }",
  "    const frame = list => {\n"
  "      const lo = [0, 0, 0], hi = [0, 0, 0];\n"
  "      list.forEach(v => { for (let i = 0; i < 3; i++) { lo[i] = Math.min(lo[i], v[i]); hi[i] = Math.max(hi[i], v[i]); } });\n"
  "      const ctr = lo.map((x, i) => Math.round((x + hi[i]) / 2 * 4) / 4 + 0);\n"
  "      let hx = 0.55, hy = 0.55, rr = 0.75, reach = 1;\n"
  "      list.forEach(v => { hx = Math.max(hx, Math.abs(v[0] - ctr[0])); hy = Math.max(hy, Math.abs(v[1] - ctr[1])); rr = Math.max(rr, len(sub(v, ctr))); reach = Math.max(reach, Math.abs(v[0]), Math.abs(v[1]), Math.abs(v[2])); });\n"
  "      return { ctr, hx, hy, rr, reach: Math.max(1, Math.ceil(reach - 0.2)) };\n"
  "    };\n"
  "    // A stage with room also holds what stands around the step: the unit circle or sphere and the whole of every\n"
  "    // sheet. A small stage (a phone) keeps to the step itself, and lets those run off the edge.\n"
  "    const wide = key.slice();\n"
  "    for (let i = 0; i < sp; i++) for (const s of [-1, 1]) { const v = [0, 0, 0]; v[i] = s; wide.push(v); }\n"
  "    sheets.forEach((q, j) => { if (!q.fr || !q.sheet || !(q.rs > 1e-6) || len(sub(pts[j + 1], pts[j])) < 1e-9) return; const r = Math.min(q.rs, 4); for (let i = 0; i < 12; i++) { const an = i / 12 * 2 * PI; see(add(q.ctr, add(scl(q.fr[0], r * Math.cos(an)), scl(q.fr[1], r * Math.sin(an)))), 9); wide.push(key.pop()); } });\n"
  "    L.frame = { tight: frame(key), roomy: frame(wide) };\n"
  "    L.fit = L.frame.roomy.rr;\n"
  "  }\n"
  "  // In space, a sheet seen edge on or a hinge seen end on is hard to read. Until the view is turned by hand, it\n"
  "  // is turned for the reader: the nearest direction to the usual one from which every hinge of this step shows.\n"
  "  if (sp === 3 && !L.view.s3.user && !L.fitHold) {\n"
  "    const V = L.view.s3, cp = Math.cos(V.pitch), sn = Math.sin(V.pitch), turning = sheets.filter((q, j) => q.fr && len(sub(pts[j + 1], pts[j])) > 1e-6).map(q => cross(q.fr[0], q.fr[1]));\n"
  "    const score = yaw => { let worst = 1; for (const nm of turning) { const d = Math.abs(dot([Math.sin(yaw) * cp, -Math.cos(yaw) * cp, sn], nm)); worst = Math.min(worst, d < 0.5 ? d / 0.5 : (1 - d) / 0.5); } return worst; };\n"
  "    if (turning.length && score(V.yaw) < 0.4) {\n"
  "      let best = V.yaw, bs = score(V.yaw);\n"
  "      for (let i = 0; i < 36 && bs < 0.62; i++) { const y = LEARN_V_VIEWS.s3.yaw + (i % 2 ? 1 : -1) * Math.ceil(i / 2) * PI / 18, sc = score(y); if (sc > bs + 1e-9) { bs = sc; best = y; } }\n"
  "      V.yaw = best;\n"
  "    }\n"
  "  }"),
 ("    moves, pts, paths, say, orbit, comp, follow, at, fault, away, end,", "    moves, pts, paths, say, orbit, comp, follow, at, fault, away, end, sheets,"),
 # the projector picks a frame by the room there is
 ("  const L = LEARN, w = L.w, h = L.h, vk = learnVKey(), V = L.view[vk], F = L.frame, f = F.ctr;",
  "  const L = LEARN, w = L.w, h = L.h, vk = learnVKey(), V = L.view[vk], F = vk === 'f1' || Math.min(w, h) < 300 ? L.frame.tight : L.frame.roomy, f = F.ctr;"),
 ("    return { cam: false, s, cx, cy, o: to([0, 0, 0]), to, from:", "    return { cam: false, s, cx, cy, reach: F.reach, o: to([0, 0, 0]), to, from:"),
 ("  return { cam: true, s, cx, cy, R, U, D, o: to([0, 0, 0]), to };", "  return { cam: true, s, cx, cy, R, U, D, reach: F.reach, o: to([0, 0, 0]), to };"),
 ("  const E = L.frame.reach;   // how far", "  const E = P.reach;   // how far"),
 # draw: use the cached sheet of the move
 ("  let hinge = null, sheet = null, fr = null;\n"
  "  if (m) { try { hinge = m.hinge ? m.hinge(a) : null; sheet = m.sheet ? m.sheet(a) : null; } catch (e) { hinge = sheet = null; } }\n"
  "  if (hinge && !(learnVFinite(hinge) && len(hinge) > 1e-9)) hinge = null;\n"
  "  if (sheet && !(sheet.length === 2 && learnVFinite(sheet[0]) && learnVFinite(sheet[1]))) sheet = null;\n"
  "  if (sheet) {\n"
  "    const u = norm(sheet[0]), w0 = sub(sheet[1], scl(u, dot(u, sheet[1])));\n"
  "    if (len(w0) > 1e-9) fr = [u, norm(w0)];\n"
  "  }\n"
  "  if (!fr && hinge) {\n"
  "    const hn = norm(hinge); let r0 = sub(ex, scl(hn, dot(ex, hn)));\n"
  "    if (len(r0) < 1e-6) r0 = sub(ey, scl(hn, dot(ey, hn)));\n"
  "    r0 = norm(r0); fr = [r0, cross(hn, r0)];\n"
  "  }\n"
  "  // the flat sheet the point travels in: through the point, with its centre on the hinge\n"
  "  const ra = len(a);\n"
  "  let ctr = O, rs = ra;\n"
  "  if (fr) { const iu = dot(a, fr[0]), iw = dot(a, fr[1]); ctr = sub(a, add(scl(fr[0], iu), scl(fr[1], iw))); rs = Math.hypot(iu, iw); }\n",
  "  // (the flat sheet the point travels in goes through the point, with its centre on the hinge: see learnVSheet)\n"
  "  const Q = m ? K.sheets[at.j] : { hinge: null, sheet: null, fr: null, ctr: O, rs: 0 }, hinge = Q.hinge, sheet = Q.sheet, fr = Q.fr, ctr = Q.ctr, rs = Q.rs;\n"),
 ("    const hn = norm(hinge), reach = vk === 's3' ? E * 1.05 : E * 0.85,", "    const hn = hinge, reach = vk === 's3' ? E * 1.05 : E * 0.85,"),
 # turning the view by hand ends the automatic choice; Reset view brings it back
 ("      V.yaw -= (x - d.x) * 0.01; V.pitch = clamp(V.pitch + (y - d.y) * 0.01, -1.5, 1.5); d.x = x; d.y = y;",
  "      V.yaw -= (x - d.x) * 0.01; V.pitch = clamp(V.pitch + (y - d.y) * 0.01, -1.5, 1.5); V.user = true; d.x = x; d.y = y;"),
 ("V.yaw -= dir[0] * 0.1; V.pitch = clamp(V.pitch + dir[1] * 0.1, -1.5, 1.5); }", "V.yaw -= dir[0] * 0.1; V.pitch = clamp(V.pitch + dir[1] * 0.1, -1.5, 1.5); V.user = true; }"),
 ("  el.viewReset.hidden = !(Math.abs(V.zoom - 1) > 1e-6 || (cam && (V.yaw !== D.yaw || V.pitch !== D.pitch)));",
  "  el.viewReset.hidden = !(Math.abs(V.zoom - 1) > 1e-6 || (cam && (V.user || V.pitch !== D.pitch)));"),
 ("  el.viewReset.addEventListener('click', () => { L.view[learnVKey()] = learnVCopy(LEARN_V_VIEWS[learnVKey()]); learnVNow(); });",
  "  el.viewReset.addEventListener('click', () => { L.view[learnVKey()] = learnVCopy(LEARN_V_VIEWS[learnVKey()]); learnVChanged(); });"),
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
