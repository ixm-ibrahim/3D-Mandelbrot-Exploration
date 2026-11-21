"""Engineer "mesh", round 9: item 1, second step. A point just under the cut plane's face counts as part of the face."""
p = 'src/js/46-mesh.js'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)
rep("""const MESH_FACE_BELOW = 1.01, MESH_FACE_ABOVE = 3.01, MESH_FACE_DEEP = 1.5;
""", """const MESH_FACE_BELOW = 1.01, MESH_FACE_ABOVE = 3.01, MESH_FACE_DEEP = 1.5;
const MESH_FACE_NEAR = 0.5;          // a point this close under the cut plane's face, in cells, is coloured as part of it
""")
rep("""  //    that the colour the face had at the point before. A point belongs to the cut plane's face when its edge
  //    stands upright, the outside end lies above the face, and on the way up the cut plane is reached before the
  //    solid's own surface is: where the plane's distance passes the level, the solid's own is still within it.
  //    (Without this the face kept a rim of surface colours two to four cells wide.)""",
"""  //    that the colour the face had at the point before. A point belongs to the cut plane's face when its edge
  //    stands upright, the outside end lies above the face, and on the way up the cut plane is reached before the
  //    solid's own surface is: where the plane's distance passes the level, the solid's own is still within it.
  //    Round the rim of the face, where the solid is thinner than a cell, the two samples cannot tell which comes
  //    first, and the point ends up a little under the face: within MESH_FACE_NEAR cells it counts as the face too.
  //    (Without this the face kept a rim of surface colours two to four cells wide.)""")
rep("""    const reached = (L - si.zc) / (so.zc - si.zc);
    cut = si.own[ei] + reached * (so.own[eo] - si.own[ei]) <= L;""",
"""    const reached = (L - si.zc) / (so.zc - si.zc);
    cut = si.own[ei] + reached * (so.own[eo] - si.own[ei]) <= L || L - (si.zc + s * (so.zc - si.zc)) <= MESH_FACE_NEAR * h;""")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('edit 4 done')
