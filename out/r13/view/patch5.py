"""One-off edits to src/js/66-learn-view.js (the view engineer's own file): exact-text replacements, each must match once."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, "src", "js", "66-learn-view.js")
with io.open(path, encoding="utf-8") as f:
    text = f.read()
edits = [
 ("const LEARN_V_START = {            // the two points each space opens with (unused coordinates stay 0)\n"
  "  1: { z: [-1.2, 0, 0], c: [0.3, 0, 0] },\n"
  "  2: { z: [0.9, 0.7, 0], c: [-0.4, 0.3, 0] },\n"
  "  3: { z: [0.9, 0.5, 0.6], c: [-0.4, 0.3, 0.2] },\n"
  "};",
  "// The two points each space opens with (unused coordinates stay 0). On the line and on the page they are chosen\n"
  "// so that Next step can be pressed many times: the point wanders and then settles, it does not run away.\n"
  "const LEARN_V_START = {\n"
  "  1: { z: [-1.2, 0, 0], c: [-0.6, 0, 0] },\n"
  "  2: { z: [0.7, 0.4, 0], c: [-0.4, 0.3, 0] },\n"
  "  3: { z: [0.6, 0.3, 0.4], c: [-0.3, 0.2, 0.1] },\n"
  "};"),
 ("base.push([Math.cos(a), Math.sin(a), 0]); } follow.push(3, 21, 39, 57); }",
  "base.push([Math.cos(a), Math.sin(a), 0]); } follow.push(3, 14, 27, 44); }"),
 ("        g.beginPath(); g.arc(q0[0], q0[1] + lift, 5, 0, 2 * PI); stroke(hues[n % 4], 1.25, 0.7);\n"
  "        g.beginPath(); g.arc(q[0], q[1] + lift, 5, 0, 2 * PI); fill(C.stage); g.beginPath(); g.arc(q[0], q[1] + lift, 4, 0, 2 * PI); fill(hues[n % 4]);",
  "        g.beginPath(); g.arc(q0[0], q0[1] + lift, 6, 0, 2 * PI); stroke(hues[n % 4], 1.5, 0.75);\n"
  "        g.beginPath(); g.arc(q[0], q[1] + lift, 6.5, 0, 2 * PI); fill(C.stage); g.beginPath(); g.arc(q[0], q[1] + lift, 5, 0, 2 * PI); fill(hues[n % 4]);"),
 ("  if (off) label('off the line, in the hidden direction', P.cx, h - 16, C.ink2, 'center');",
  "  if (off) label('z is off the line, out in the hidden direction', P.cx, Math.min(h - 12, P.cy + 62), C.ink2, 'center');"),
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
