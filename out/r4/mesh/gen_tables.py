"""Build and verify the marching-cubes tables used by src/js/46-mesh.js.

The 256-entry edge table and triangle table are worked out from the cube itself, case by case, and checked
exhaustively, so that nothing rests on a table typed from memory:

  corners  v0..v7 and edges e0..e11 are numbered as in the standard tables (Lorensen and Cline as distributed
           by Paul Bourke): v0-v3 around the lower face, v4-v7 above them; e0-e3 around the lower face, e4-e7
           around the upper face, e8-e11 the uprights.
  bit c of the case number is set when corner c is INSIDE the solid.
  on a cube face whose two inside corners sit on a diagonal, the surface cuts each inside corner off on its
           own. This is the rule of the standard table, and because it only looks at the face, two cells
           that share a face always agree, so the surface has no cracks.

Checks made here: every case uses exactly its crossing edges; every triangle edge that lies inside the cell
is used twice, once each way, and never joins two points of one face; every other triangle edge lies on a
face, is used once, and is exactly the cut that the face rule prescribes; a random field on a small grid gives a closed, consistently turned surface;
a sphere comes out with positive volume (triangles turn counter-clockwise seen from outside).

Run:  python out/r4/mesh/gen_tables.py          prints the checks and writes out/r4/mesh/tables.js.txt
"""
import itertools, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
CORNER = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
EDGE = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
FACE = [((0, 1, 2, 3), (0, 0, -1)), ((4, 5, 6, 7), (0, 0, 1)), ((0, 1, 5, 4), (0, -1, 0)),
        ((1, 2, 6, 5), (1, 0, 0)), ((2, 3, 7, 6), (0, 1, 0)), ((3, 0, 4, 7), (-1, 0, 0))]
EDGE_OF = {frozenset(e): i for i, e in enumerate(EDGE)}
MID = [tuple((CORNER[a][k] + CORNER[b][k]) / 2 for k in range(3)) for a, b in EDGE]


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def face_cuts(case):
    """Directed cuts (edge, edge) on the six faces: the inside lies to the right, seen from outside the cube."""
    cuts = []
    for corners, nrm in FACE:
        ins = [bool(case >> c & 1) for c in corners]
        fe = [EDGE_OF[frozenset((corners[i], corners[(i + 1) % 4]))] for i in range(4)]   # edge i joins corner i and i+1
        crossing = [i for i in range(4) if ins[i] != ins[(i + 1) % 4]]
        pairs = []
        if len(crossing) == 2:
            side = [corners[i] for i in range(4) if ins[i]]
            pairs.append((fe[crossing[0]], fe[crossing[1]], side))
        elif len(crossing) == 4:
            for i in range(4):
                if ins[i]:   # cut this inside corner off on its own: the edges before and after it
                    pairs.append((fe[(i - 1) % 4], fe[i], [corners[i]]))
        for a, b, side in pairs:
            centre = tuple(sum(CORNER[c][k] for c in side) / len(side) for k in range(3))
            left = dot(cross(sub(MID[b], MID[a]), sub(centre, MID[a])), nrm) > 0
            cuts.append((b, a) if left else (a, b))
    return cuts


FACES_OF = [{f for f, (corners, _) in enumerate(FACE) if a in corners and b in corners} for a, b in EDGE]


def tri_area(a, b, c):
    n = cross(sub(MID[b], MID[a]), sub(MID[c], MID[a]))
    return dot(n, n) ** 0.5 / 2


def fill(loop):
    """The flattest way to fill a loop with triangles (least total area) among those in which no new line joins
    two points of the same cube face. Such a line would lie in the face, and the cell on the other side could
    draw the same line, leaving four triangles on one edge. Returns (area, triangles) or None."""
    n = len(loop)
    if n < 3:
        return (0.0, [])
    best = None
    for k in range(1, n - 1):
        if k > 1 and FACES_OF[loop[0]] & FACES_OF[loop[k]]:
            continue
        if k < n - 2 and FACES_OF[loop[k]] & FACES_OF[loop[n - 1]]:
            continue
        left, right = fill(loop[:k + 1]), fill(loop[k:])
        if left is None or right is None:
            continue
        cand = (left[0] + right[0] + tri_area(loop[0], loop[k], loop[n - 1]), left[1] + [(loop[0], loop[k], loop[n - 1])] + right[1])
        if best is None or cand[0] < best[0] - 1e-12:
            best = cand
    return best


def triangles(case):
    cuts = face_cuts(case)
    nxt = {}
    for a, b in cuts:
        assert a not in nxt, (case, cuts)
        nxt[a] = b
    tris, seen = [], set()
    for start in sorted(nxt):
        if start in seen:
            continue
        loop, e = [], start
        while e not in seen:
            seen.add(e); loop.append(e); e = nxt[e]
        assert e == start and len(loop) >= 3, (case, loop)
        got = fill(loop)
        assert got is not None, (case, loop)
        tris += got[1]
    return tris, cuts


def build():
    edge_table, tri_table = [], []
    for case in range(256):
        crossing = {i for i, (a, b) in enumerate(EDGE) if (case >> a & 1) != (case >> b & 1)}
        tris, cuts = triangles(case)
        used = {e for t in tris for e in t}
        assert used == crossing, (case, used, crossing)
        directed = {}
        for t in tris:
            assert len(set(t)) == 3
            for i in range(3):
                k = (t[i], t[(i + 1) % 3])
                assert k not in directed, (case, k)
                directed[k] = 1
        rim = {k for k in directed if (k[1], k[0]) not in directed}
        assert rim == set(cuts), (case, rim, cuts)          # the open edges are exactly the cuts on the faces
        edge_table.append(sum(1 << e for e in crossing))
        tri_table.append(tris)
    return edge_table, tri_table


def march(field, n, tri_table, level=0.0):
    """Marching cubes on an n^3 grid of values (inside where value <= level); returns welded triangles."""
    vid, tris = {}, []
    def val(i, j, k): return field[(k * n + j) * n + i]
    for k in range(n - 1):
        for j in range(n - 1):
            for i in range(n - 1):
                case = 0
                for c, (dx, dy, dz) in enumerate(CORNER):
                    if val(i + dx, j + dy, k + dz) <= level:
                        case |= 1 << c
                for t in tri_table[case]:
                    tri = []
                    for e in t:
                        a, b = EDGE[e]
                        pa = (i + CORNER[a][0], j + CORNER[a][1], k + CORNER[a][2])
                        pb = (i + CORNER[b][0], j + CORNER[b][1], k + CORNER[b][2])
                        key = (min(pa, pb), max(pa, pb))
                        if key not in vid:
                            va, vb = val(*pa) - level, val(*pb) - level
                            s = va / (va - vb)
                            vid[key] = (len(vid), tuple(pa[q] + s * (pb[q] - pa[q]) for q in range(3)))
                        tri.append(vid[key][0])
                    tris.append(tuple(tri))
    pts = [None] * len(vid)
    for i, p in vid.values():
        pts[i] = p
    return pts, tris


def closed(tris):
    d = {}
    for t in tris:
        for i in range(3):
            k = (t[i], t[(i + 1) % 3])
            if k in d:
                return False
            d[k] = 1
    return all((b, a) in d for a, b in d)


def volume(pts, tris):
    return sum(dot(pts[a], cross(pts[b], pts[c])) for a, b, c in tris) / 6


def main():
    edge_table, tri_table = build()
    print("cases ok: 256; most triangles in a case:", max(len(t) for t in tri_table),
          "; triangles in all cases:", sum(len(t) for t in tri_table))
    # a field of noise visits every case, the face-diagonal ones included; its outermost layer is kept outside
    random.seed(7)
    n = 14
    seen = set()
    for trial in range(6):
        f = [random.uniform(-1, 1) for _ in range(n ** 3)]
        for k, j, i in itertools.product(range(n), repeat=3):
            if 0 in (i, j, k) or n - 1 in (i, j, k):
                f[(k * n + j) * n + i] = 1.0
        pts, tris = march(f, n, tri_table)
        for k, j, i in itertools.product(range(n - 1), repeat=3):
            seen.add(sum((f[((k + dz) * n + j + dy) * n + i + dx] <= 0) << c for c, (dx, dy, dz) in enumerate(CORNER)))
        assert closed(tris), "noise field %d is not closed" % trial
    print("noise fields: closed and consistently turned; cases met:", len(seen), "of 256")
    n = 20
    c, r = (n - 1) / 2, 7.3
    f = [((i - c) ** 2 + (j - c) ** 2 + (k - c) ** 2) ** 0.5 - r for k in range(n) for j in range(n) for i in range(n)]
    pts, tris = march(f, n, tri_table)
    v, true = volume(pts, tris), 4 / 3 * 3.141592653589793 * r ** 3
    assert closed(tris) and v > 0
    print("sphere: closed, volume %.1f against %.1f (%.2f%%), %d triangles" % (v, true, 100 * (v / true - 1), len(tris)))

    lines = ["const MESH_EDGE_TABLE = ["]
    for r0 in range(0, 256, 16):
        lines.append("  " + ", ".join("0x%03x" % x for x in edge_table[r0:r0 + 16]) + ",")
    lines.append("];")
    lines.append("const MESH_TRI_TABLE = [")
    row = "  "
    for case in range(256):
        cell = "'" + "".join("%x" % e for t in tri_table[case] for e in t) + "',"
        if len(row) + len(cell) + 1 > 118:
            lines.append(row.rstrip()); row = "  "
        row += cell + " "
    lines.append(row.rstrip())
    lines.append("];")
    with open(os.path.join(HERE, "tables.js.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote tables.js.txt")
    for case in (1, 2, 3, 5, 15, 250, 254):
        print(" case %3d: edges 0x%03x, triangles %s" % (case, edge_table[case], tri_table[case]))


if __name__ == "__main__":
    main()
