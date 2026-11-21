"""Engineer "mesh", round 9: the edit for item 3 (mesh-2): the warning for a solid finer than the grid says what helps."""
p = 'src/js/46-mesh.js'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)
rep("""  const warn = [];
  if (pieces >= MESH_MANY_PIECES) {
    warn.push(`This solid has parts thinner than one cell of the grid. They came out as ${meshCount(pieces)} loose pieces, so the model is rougher than the picture and can look unlike it. A higher resolution follows the picture more closely.`);
  }
  if (part) warn.push(`Only the largest piece was kept: ${meshShare(kept)} of the surface. Untick "Keep only the largest piece" and start again to get all ${meshCount(pieces)} pieces.`);""",
"""  // A solid finer than the grid (a negative power: sheets thinner than a cell of any grid on offer) cannot be made
  // to match its picture by any setting. Measured on the power -2 picture at 128, 256 and 512 cells with offsets
  // 0.5, 1 and 1.5 (notes/r9-mesh.md): with every piece kept, 93 to 99% of the picture's outline is covered and
  // the shapes of the picture are there from 256 cells on, together with outer shells that the picture draws only
  // in part; the largest piece alone lacks 16 to 82% of the picture; a larger offset joins more pieces but
  // thickens the sheets, and the outlines then agree less, not more. So the warning says what does help.
  const warn = [], fine = pieces >= MESH_MANY_PIECES, more = o.cells < 256 ? ' and choose 256 or 512 cells' : o.cells < 512 ? ' and choose 512 cells' : '';
  if (fine && part) {
    warn.push(`This solid has parts thinner than one cell of the grid. They came out as ${meshCount(pieces)} loose pieces, and only the largest was kept: ${meshShare(kept)} of the surface. So this model does not look like the picture. To get closer, untick "Keep only the largest piece"${more}, then start again. A larger surface offset joins more of the pieces, but it makes the thin parts thick.`);
  } else if (fine) {
    warn.push(`This solid has parts thinner than one cell of the grid. They came out as ${meshCount(pieces)} loose pieces, so the model is rougher than the picture and can look unlike it. ` +
      (o.cells < 512 ? `${o.cells < 256 ? '256 or 512' : '512'} cells follow the picture more closely. ` : '') + 'A larger surface offset joins more of the pieces, but it makes the thin parts thick.');
  } else if (part) warn.push(`Only the largest piece was kept: ${meshShare(kept)} of the surface. Untick "Keep only the largest piece" and start again to get all ${meshCount(pieces)} pieces.`);""")
rep("""let MESH_FACE_RULE2 = true;
""", """const MESH_FACE_RULE2 = true;        // the second exception of meshPoint's colours, kept as a switch so that it can be measured on and off
""")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('edit 3 done')
