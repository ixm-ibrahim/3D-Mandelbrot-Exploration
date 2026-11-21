"""One-off edits to the view engineer's own files: exact-text replacements, each must match once."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
jobs = {
 os.path.join(ROOT, "src", "js", "66-learn-view.js"): [
  ("    pd('zx', 'The point z, along x'), pd('zy', 'The point z, along y', () => L.space >= 2), pd('zz', 'The point z, along z', () => L.space === 3),\n"
   "    pd('cx', 'The point c, along x'), pd('cy', 'The point c, along y', () => L.space >= 2), pd('cz', 'The point c, along z', () => L.space === 3),",
   "    // (the labels are upper case, which would print the points z and c as capitals: class asis keeps them as typed)\n"
   "    pd('zx', 'The point <span class=\"asis\">z</span>, along x'), pd('zy', 'The point <span class=\"asis\">z</span>, along y', () => L.space >= 2), pd('zz', 'The point <span class=\"asis\">z</span>, along z', () => L.space === 3),\n"
   "    pd('cx', 'The point <span class=\"asis\">c</span>, along x'), pd('cy', 'The point <span class=\"asis\">c</span>, along y', () => L.space >= 2), pd('cz', 'The point <span class=\"asis\">c</span>, along z', () => L.space === 3),"),
  ("    if (vk === 's3') { seg([0, 0, -E], [0, 0, E], C.ink2, 1.25, 0.95); tag([0, 0, E], 'z', C.ink2, 8, -4); }",
   "    if (vk === 's3') { seg([0, 0, -E], [0, 0, E], C.ink2, 1.25, 0.95); tag([0, 0, E], 'z', C.ink2, 8, -4); }\n"
   "    // the page does not have the z-axis: it stands on it dashed, and is the hinge whenever the page turns\n"
   "    if (vk === 'h2') { seg([0, 0, -E * 0.85], [0, 0, E * 0.85], C.ink2, 1.25, 0.6, [5, 5]); if (!(m && K.sheets[at.j].hinge)) tag([0, 0, E * 0.85], 'z, the hidden direction', C.ink2, 8, 2); }"),
  ("  el.canvas.setAttribute('aria-label', 'Drawing of one step: the point z, the point c, and the move being played. The sentence under the picture says the same in words.');",
   "  el.canvas.setAttribute('aria-label', 'Drawing of one step: the point z, the point c, and the move being played. The sentence under the picture says the same in words. With the picture in focus, the arrow keys turn a tipped view or move z in a flat one, plus and minus zoom, and the space bar plays or pauses.');"),
 ],
 os.path.join(ROOT, "src", "css", "65-learn.css"): [
  ("/* The pin module (85-pin.css)",
   "/* a low window (a phone held sideways): the picture gives way, so that the controls under it stay in reach */\n"
   "@media (max-width: 920px) and (max-height: 480px) {\n"
   "  body.is-learn .stage { height: clamp(140px, 44vh, 240px); }\n"
   "}\n"
   "/* The pin module (85-pin.css)"),
 ],
}
for path, edits in jobs.items():
    with io.open(path, encoding="utf-8") as f:
        text = f.read()
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            sys.exit("MATCHES %d : %s" % (n, old[:90]))
        text = text.replace(old, new)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("ok", os.path.basename(path), len(edits))
