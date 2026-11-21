"""One-off edits to src/js/66-learn-view.js (the view engineer's own file): exact-text replacements, each must match once."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, "src", "js", "66-learn-view.js")
with io.open(path, encoding="utf-8") as f:
    text = f.read()
edits = [
 ("g.beginPath(); g.arc(P.cx, P.cy, P.s, 0, 2 * PI); stroke(C.ink2, 1.25, 0.5);",
  "g.beginPath(); g.arc(P.o[0], P.o[1], P.s, 0, 2 * PI); stroke(C.ink2, 1.25, 0.5);"),
 ("      label(vk === 'f1' ? 'hinge (hidden)' : 'hinge, seen end on', P.cx + 13, P.cy + (vk === 'f1' ? -22 : 15), C.ok, 'left', 0, 600);",
  "      label(vk === 'f1' ? 'hinge (hidden)' : 'hinge, seen end on', P.o[0] + 13, P.o[1] + (vk === 'f1' ? -24 : 16), C.ok, 'left', 0, 600);"),
 ("      const top = q1[1] < q0[1] ? q1 : q0;\n      label('hinge', top[0] + 8, top[1] + 4, C.ok, 'left', small ? 12 : 13.5, 600);",
  "      // the word stands by the upper end of the line, or by the highest part of it that is in the picture\n"
  "      const up = q1[1] < q0[1] ? 1 : -1; let at1 = up > 0 ? q1 : q0;\n"
  "      for (let i = 20; i >= 4; i--) { const q = P.to(scl(hn, up * reach * i / 20)); at1 = q; if (q[0] > 12 && q[0] < w - 60 && q[1] > 16 && q[1] < h - 16) break; }\n"
  "      label('hinge', at1[0] + 9, at1[1] + 2, C.ok, 'left', small ? 12.5 : 14, 600);"),
 ("const away = (q, gap, side) => { let dx = q[0] - P.cx, dy = q[1] - P.cy;",
  "const away = (q, gap, side) => { let dx = q[0] - P.o[0], dy = q[1] - P.o[1];"),
 ("    const v = [r2((x + d.dx - P.cx) / P.s), L.space > 1 ? r2((P.cy - (y + d.dy)) / P.s) : 0, 0];",
  "    const at2 = P.from(x + d.dx, y + d.dy), v = [r2(at2[0]), L.space > 1 ? r2(at2[1]) : 0, 0];"),
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
