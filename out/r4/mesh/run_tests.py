"""Tests for src/js/46-mesh.js. Builds dist/r4-mesh.html, drives it with tools/shot.py and checks the results.

  python out/r4/mesh/run_tests.py fields        the built-in fields: closed surface, volume, fit, zip and file formats
  python out/r4/mesh/run_tests.py real          the real picture (needs 45-export.js): Julia c = -1, Mandelbrot, Kleinian
  add --base base3 to build against that folder, --use <files...> to add live files to the build

Zips received through window.squaringLabSaveHook are written to out/r4/mesh/zips/ and read back here with
python's zipfile module; the STL, OBJ and PLY inside are parsed again and compared.
"""
import base64, io, json, math, os, re, struct, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MINE = ["src/js/00-core.js", "src/js/46-mesh.js", "src/css/46-mesh.css"]
NAME = "r4-mesh-real" if "real" in sys.argv[1:2] else "r4-mesh"


def build(base, extra):
    swaps = ["js/90-boot.js=out/r4/mesh/90-boot.js"] + [a for a in sys.argv if a.startswith("js/") and "=" in a]
    cmd = [sys.executable, "build.py", "--name", NAME, "--base", base, "--use"] + MINE + [e for e in extra if "=" not in e] + ["--swap"] + swaps
    print(subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True).stdout.strip())


def drive(steps, name, size="1400x950", theme="dark"):
    """Run steps through tools/shot.py; returns ({step number: value}, whole output)."""
    path = os.path.join(HERE, name + ".steps.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(steps, f)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "tools/shot.py", "--url", "dist/%s.html" % NAME, "--actions", path, "--size", size, "--theme", theme],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=env)
    out, res = r.stdout + r.stderr, {}
    for line in out.splitlines():
        m = re.match(r"step (\d+) result: (.*)$", line)
        if m:
            res[int(m.group(1))] = json.loads(m.group(2))
        elif not line.startswith("step") or "TIMED OUT" in line:
            print("   | " + line[:400])
    print("   shot.py exit code %d" % r.returncode)
    return res, out


def helpers():
    with open(os.path.join(HERE, "check.js"), encoding="utf-8") as f:
        code = f.read()
    with open(os.path.join(HERE, "draw.js"), encoding="utf-8") as f:
        return {"js": code + f.read() + "\nreturn 'helpers loaded';"}


# ---------- reading the files back
def read_stl(data):
    assert data[:5] != b"solid", "a binary STL must not begin with the word solid"
    nt = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + 50 * nt, "STL length %d does not fit %d triangles" % (len(data), nt)
    ids, pts, tris, bad_normals = {}, [], [], 0
    for t in range(nt):
        rec = struct.unpack_from("<12fH", data, 84 + 50 * t)
        tri = []
        for e in range(3):
            key = data[84 + 50 * t + 12 + 12 * e: 84 + 50 * t + 24 + 12 * e]
            if key not in ids:
                ids[key] = len(pts); pts.append(rec[3 + 3 * e: 6 + 3 * e])
            tri.append(ids[key])
        a, b, c = (pts[i] for i in tri)
        u, v = [b[k] - a[k] for k in range(3)], [c[k] - a[k] for k in range(3)]
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        ln = math.sqrt(sum(x * x for x in n)) or 1
        if sum(n[k] / ln * rec[k] for k in range(3)) < 0.99:
            bad_normals += 1
        tris.append(tuple(tri))
    return pts, tris, bad_normals


def closed(tris):
    """(edges used twice the same way, edges without a partner): both 0 for a closed, consistently turned surface."""
    seen, twice = set(), 0
    for t in tris:
        for e in range(3):
            k = (t[e], t[(e + 1) % 3])
            if k in seen:
                twice += 1
            seen.add(k)
    return twice, sum(1 for a, b in seen if (b, a) not in seen)


def pieces(npts, tris):
    par = list(range(npts))
    def find(v):
        while par[v] != v:
            par[v] = par[par[v]]; v = par[v]
        return v
    for a, b, c in tris:
        ra, rb = find(a), find(b)
        if ra != rb: par[rb] = ra
        rc = find(c)
        if rc != ra: par[rc] = ra
    return len({find(t[0]) for t in tris})


def volume(pts, tris):
    v = 0.0
    for a, b, c in tris:
        p, q, r = pts[a], pts[b], pts[c]
        v += p[0] * (q[1] * r[2] - q[2] * r[1]) + p[1] * (q[2] * r[0] - q[0] * r[2]) + p[2] * (q[0] * r[1] - q[1] * r[0])
    return v / 6


def read_obj(text):
    pts, cols, tris = [], [], []
    for line in text.splitlines():
        if line.startswith("v "):
            f = [float(x) for x in line.split()[1:]]
            assert len(f) == 6, "a v line should hold x y z r g b: " + line
            pts.append(f[:3]); cols.append(f[3:])
        elif line.startswith("f "):
            tris.append(tuple(int(x) - 1 for x in line.split()[1:]))
    return pts, cols, tris


def read_ply(data):
    end = data.index(b"end_header\n") + 11
    head = data[:end].decode("ascii")
    assert "format binary_little_endian 1.0" in head
    nv, nt = int(re.search(r"element vertex (\d+)", head).group(1)), int(re.search(r"element face (\d+)", head).group(1))
    assert len(data) == end + 15 * nv + 13 * nt, "PLY length does not fit its header"
    pts = [struct.unpack_from("<3f3B", data, end + 15 * v) for v in range(nv)]
    tris = []
    for t in range(nt):
        k, a, b, c = struct.unpack_from("<B3i", data, end + 15 * nv + 13 * t)
        assert k == 3
        tris.append((a, b, c))
    return [p[:3] for p in pts], [p[3:] for p in pts], tris


def check_zip(saved, label, want_mm=100.0, expect_pieces=1):
    """Write the zip to disk, unpack it with zipfile, parse every file back. Returns a dict of findings."""
    os.makedirs(os.path.join(HERE, "zips"), exist_ok=True)
    raw = base64.b64decode(saved["b64"])
    path = os.path.join(HERE, "zips", label + "-" + saved["name"])
    with open(path, "wb") as f:
        f.write(raw)
    z = zipfile.ZipFile(path)
    bad = z.testzip()
    out = {"zip": saved["name"], "bytes": len(raw), "entries": {i.filename: i.file_size for i in z.infolist()}, "crc": "all correct" if bad is None else "BAD: " + bad,
           "stored": all(i.compress_type == zipfile.ZIP_STORED for i in z.infolist())}
    names = z.namelist()
    stl = next((n for n in names if n.endswith(".stl")), None)
    obj = next((n for n in names if n.endswith(".obj")), None)
    ply = next((n for n in names if n.endswith(".ply")), None)
    readme = z.read("readme.txt").decode("utf-8")
    out["readme_lines"] = len(readme.splitlines())
    ref = None
    if stl:
        pts, tris, badn = read_stl(z.read(stl))
        twice, lone = closed(tris)
        lo = [min(p[k] for p in pts) for k in range(3)]; hi = [max(p[k] for p in pts) for k in range(3)]
        out["stl"] = {"triangles": len(tris), "points after welding": len(pts), "edges used twice the same way": twice, "edges without a partner": lone,
                      "closed": twice == 0 and lone == 0, "pieces": pieces(len(pts), tris), "normals that disagree with the corners": badn,
                      "size mm": [round(hi[k] - lo[k], 3) for k in range(3)], "lowest z": round(lo[2], 4),
                      "centre x y": [round((lo[k] + hi[k]) / 2, 4) for k in range(2)], "volume mm3": round(volume(pts, tris), 1)}
        assert abs(max(hi[k] - lo[k] for k in range(3)) - want_mm) < 1e-3 * want_mm, "longest side is not %s mm" % want_mm
        assert out["stl"]["closed"], "the STL is not closed"
        assert out["stl"]["pieces"] == expect_pieces or expect_pieces is None, "pieces: %d" % out["stl"]["pieces"]
        ref = (len(pts), len(tris))
    if ply:
        pp, pc, pt = read_ply(z.read(ply))
        twice, lone = closed(pt)
        out["ply"] = {"triangles": len(pt), "points": len(pp), "closed": twice == 0 and lone == 0, "colour range": [min(min(c) for c in pc), max(max(c) for c in pc)]}
        assert out["ply"]["closed"], "the PLY is not closed"
        if ref: assert ref == (len(pp), len(pt)), "PLY and STL disagree: %s against %s" % ((len(pp), len(pt)), ref)
    if obj:
        op, oc, ot = read_obj(z.read(obj).decode("ascii"))
        twice, lone = closed(ot)
        out["obj"] = {"triangles": len(ot), "points": len(op), "closed": twice == 0 and lone == 0}
        assert out["obj"]["closed"], "the OBJ is not closed"
        if ply:
            assert ot == pt, "OBJ and PLY triangles differ"
            # the OBJ is written y-up: (x, y, z) of the lab is (x, z, -y) in the file
            worst = max(max(abs(a[0] - b[0]), abs(-a[2] - b[1]), abs(a[1] - b[2])) for a, b in zip(op, pp))
            wcol = max(max(abs(a[k] * 255 - b[k]) for k in range(3)) for a, b in zip(oc, pc))
            out["obj"]["largest difference from the PLY, mm"] = round(worst, 6)
            out["obj"]["largest colour difference, of 255"] = round(wcol, 3)
            assert worst < 1e-4 * 1.01 and wcol < 0.2
    return out, readme


def show(title, value):
    print("== " + title)
    print(json.dumps(value, indent=1, ensure_ascii=False) if not isinstance(value, str) else value)


def fields():
    R2 = "const m = window.squaringLabMeshTest.mesh, T = window.meshT;"
    sphere = lambda r: "(x, y, z) => Math.hypot(x, y, z) - (%s)" % r
    steps = [
        helpers(),
        # 2: the sphere at offset 0 (true volume 4/3 pi) through the UI's smallest resolution
        {"js": "const run = await meshT.run('sphere', 0, { cells: 96, offset: 0 }); " + R2 + " return { run, closed: T.closed(m), fit: T.fit(m, " + sphere("1") + "), "
               "volume: m.volume / m.unit ** 3, trueVolume: 4 / 3 * Math.PI, h: m.h, box: m.box, grid: [m.n, m.n, m.nz] };"},
        # 3: the sphere at the default settings (128 cells, offset 0.5): the surface is the sphere of radius 1 + 0.5 h
        {"js": "const run = await meshT.run('sphere', 0, {}); " + R2 + " const r = 1 + 0.5 * m.h; return { run, closed: T.closed(m), fit: T.fit(m, (x, y, z) => Math.hypot(x, y, z) - r), "
               "volume: m.volume / m.unit ** 3, trueVolume: 4 / 3 * Math.PI * r ** 3, h: m.h, grid: [m.n, m.n, m.nz] };"},
        {"js": "return await meshT.save();"},
        # 5: torus (volume 2 pi^2 R r^2 with r = 0.35 + 0.5 h; Euler number 0)
        {"js": "const run = await meshT.run('torus', 0, { cells: 128 }); " + R2 + " const r = 0.35 + 0.5 * m.h; return { run, closed: T.closed(m), "
               "fit: T.fit(m, (x, y, z) => Math.hypot(Math.hypot(x, y) - 1, z) - r), volume: m.volume / m.unit ** 3, trueVolume: 2 * Math.PI ** 2 * r * r, grid: [m.n, m.n, m.nz] };"},
        # 6: gyroid, a thin wall: all pieces kept, then the largest only
        {"js": "const run = await meshT.run('gyroid', 0, { cells: 96, largest: false }); " + R2 + " return { run, closed: T.closed(m), pieces: m.pieces, grid: [m.n, m.n, m.nz] };"},
        {"js": "const run = await meshT.run('gyroid', 0, { cells: 192, offset: 0.25 }); " + R2 + " return { run, closed: T.closed(m), pieces: m.pieces, grid: [m.n, m.n, m.nz] };"},
        {"js": "return await meshT.save();"},
        # 9: pearl: zero inside, reads 1.6 times too long outside (the Kleinian situation), at offset 0 and 0.5
        {"js": "const run = await meshT.run('pearl', 0, { cells: 96, offset: 0 }); " + R2 + " return { run, closed: T.closed(m), fit: T.fit(m, " + sphere("1") + "), "
               "volume: m.volume / m.unit ** 3, trueVolume: 4 / 3 * Math.PI };"},
        {"js": "const run = await meshT.run('pearl', 0, { cells: 96, offset: 0.5 }); " + R2 + " const r = 1 + 0.5 * m.h / 1.6; return { run, closed: T.closed(m), fit: T.fit(m, (x, y, z) => Math.hypot(x, y, z) - r), "
               "volume: m.volume / m.unit ** 3, trueVolume: 4 / 3 * Math.PI * r ** 3 };"},
        # 11: noise: every case of the tables, all pieces kept; then the largest piece of it
        {"js": "const run = await meshT.run('noise', 40, { largest: false }); " + R2 + " return { run, closed: T.closed(m), pieces: m.pieces };"},
        {"js": "const run = await meshT.run('noise', 56, {}); " + R2 + " return { run, closed: T.closed(m), pieces: m.pieces };"},
        {"js": "return await meshT.save();"},
        # 14: the cut plane and the drawing radius are part of the model: a sphere cut at z = 0.3, and one clipped by a drawing radius of 0.8
        {"js": "const L = window.squaringLab; L.S.cutOn = true; L.S.cut = 0.3; const run = await meshT.run('sphere', 0, { cells: 96, offset: 0 }); L.S.cutOn = false; " + R2 +
               " const hh = 1.3; return { run, closed: T.closed(m), volume: m.volume / m.unit ** 3, trueVolume: Math.PI * hh * hh * (3 - hh) / 3, sizeMm: m.size };"},
        {"js": "const L = window.squaringLab; L.S.view.bound = 0.8; const run = await meshT.run('torus', 0, { cells: 96, offset: 0 }); L.S.view.bound = 8; " + R2 +
               " return { run, closed: T.closed(m), sizeMm: m.size };"},
        # 16: zipStore on its own: a string and bytes
        {"js": "const L = window.squaringLab; const blob = L.zipStore([{ name: 'a.txt', data: 'h\\u00e9llo w\\u00f6rld\\n' }, { name: 'dir/b.bin', data: new Uint8Array([0, 1, 2, 250, 251, 252]) }, { name: 'empty.txt', data: '' }]); "
               "const bytes = new Uint8Array(await blob.arrayBuffer()); return { name: 'zipstore.zip', size: bytes.length, type: blob.type, b64: btoa(String.fromCharCode.apply(null, bytes)) };"},
        # 17: cancel, nothing chosen, and a field with nothing solid in it
        {"js": "const L = window.squaringLab, T = window.meshT; window.squaringLabMeshTest = { field: 'gyroid' }; L.MESH.opt.cells = 512; document.getElementById('meshDiscard').click(); "
               "document.getElementById('meshStart').click(); await new Promise(r => setTimeout(r, 700)); const during = { busy: L.meshBusy(), step: document.getElementById('meshStep').textContent, "
               "startHidden: document.getElementById('meshStart').parentNode.hidden }; document.getElementById('meshCancel').click(); const t0 = performance.now(); while (L.meshBusy()) await new Promise(r => setTimeout(r, 10)); "
               "const cancelled = { ms: Math.round(performance.now() - t0), message: document.getElementById('meshMsg').textContent, result: !!L.MESH.result, startBack: !document.getElementById('meshStart').parentNode.hidden }; "
               "L.MESH.opt.cells = 96; Object.assign(L.MESH.opt, { stl: false, obj: false, ply: false }); document.getElementById('meshStart').click(); const none = { busy: L.meshBusy(), message: document.getElementById('meshMsg').textContent }; "
               "Object.assign(L.MESH.opt, { stl: true }); L.S.view.bound = 0.5; window.squaringLabMeshTest = { field: 'torus' }; document.getElementById('meshStart').click(); while (L.meshBusy()) await new Promise(r => setTimeout(r, 10)); "
               "L.S.view.bound = 8; const empty = { message: document.getElementById('meshMsg').textContent, result: !!L.MESH.result }; L.MESH.opt.obj = L.MESH.opt.ply = true; L.syncControls(); return { during, cancelled, none, empty };"},
    ]
    res, out = drive(steps, "fields")
    for i, title in ((2, "sphere, 96 cells, offset 0"), (3, "sphere, default settings (128 cells, offset 0.5)"), (5, "torus, 128 cells"), (6, "gyroid, 96 cells, every piece"),
                     (7, "gyroid, 192 cells, offset 0.25, largest piece"), (9, "pearl (zero inside), offset 0"), (10, "pearl, offset 0.5"), (11, "noise, 40 cells, every piece"),
                     (12, "noise, 56 cells, largest piece"), (14, "sphere cut at z = 0.3"), (15, "torus clipped by a drawing radius of 0.8"), (17, "cancel, no kind of file, nothing solid")):
        if i in res:
            v = res[i]
            if "volume" in v:
                v["volumeErrorPercent"] = round(100 * (v["volume"] / v["trueVolume"] - 1), 3)
            show(title, v)
        else:
            print("== %s: NO RESULT" % title)
    for i, label, want in ((4, "sphere", 1), (8, "gyroid", 1), (13, "noise", 1)):
        if i in res:
            found, readme = check_zip(res[i], label, expect_pieces=want)
            show("zip read back: " + label, found)
            if label == "sphere":
                show("readme.txt", readme)
    if 16 in res:
        raw = base64.b64decode(res[16]["b64"])
        z = zipfile.ZipFile(io.BytesIO(raw))
        show("zipStore on its own", {"crc": "all correct" if z.testzip() is None else "BAD", "type": res[16]["type"], "entries": {i.filename: z.read(i.filename).decode("utf-8", "replace") if i.filename.endswith(".txt") else list(z.read(i.filename)) for i in z.infolist()}})
    return out


def real():
    R2 = "const m = window.squaringLabMeshTest.mesh, T = window.meshT;"
    pre = "const L = window.squaringLab; L.R.warmOn = false; "
    steps = [
        helpers(),
        {"js": pre + "document.getElementById('mode-j').click(); L.S.c = [-1, 0, 0]; L.S.q.aa = 2; L.syncControls(); L.refresh(false); return 'julia c = -1';", "wait": "done", "timeout": 300,
         "shot": "out/r4/mesh/real-julia-picture.png", "clip": "#stage"},
        {"js": "const run = await meshT.run(null, 128, {}); " + R2 + " return { run, closed: T.closed(m), pieces: m.pieces, grid: [m.n, m.n, m.nz], box: m.box, sizeMm: m.size };"},
        {"js": "return await meshT.save();"},
        {"js": "return meshT.draw(window.squaringLabMeshTest.mesh, 0.5, 0.45);", "shot": "out/r4/mesh/real-julia-mesh.png", "clip": "#meshView"},
        {"js": "document.getElementById('meshView').remove(); " + pre + "document.getElementById('mode-m').click(); L.syncControls(); L.refresh(false); return 'mandelbrot default';", "wait": "done", "timeout": 300,
         "shot": "out/r4/mesh/real-mandel-picture.png", "clip": "#stage"},
        {"js": "const run = await meshT.run(null, 128, { obj: false, ply: false }); " + R2 + " return { run, closed: T.closed(m), pieces: m.pieces, grid: [m.n, m.n, m.nz], box: m.box, sizeMm: m.size };"},
        {"js": "return await meshT.save();"},
        {"js": "return meshT.draw(window.squaringLabMeshTest.mesh, 0.5, 0.45);", "shot": "out/r4/mesh/real-mandel-mesh.png", "clip": "#meshView"},
        {"js": "document.getElementById('meshView').remove(); " + pre + "document.getElementById('mode-k').click(); L.syncControls(); L.refresh(false); return 'kleinian default';", "wait": "done", "timeout": 300,
         "shot": "out/r4/mesh/real-klein-picture.png", "clip": "#stage"},
        {"js": "const run = await meshT.run(null, 128, { obj: false, ply: false }); " + R2 + " return { run, closed: T.closed(m), pieces: m.pieces, grid: [m.n, m.n, m.nz], box: m.box, sizeMm: m.size };"},
        {"js": "return await meshT.save();"},
        {"js": "return meshT.draw(window.squaringLabMeshTest.mesh, 0.5, 0.45);", "shot": "out/r4/mesh/real-klein-mesh.png", "clip": "#meshView"},
    ]
    res, out = drive(steps, "real")
    for i, title, label in ((3, "Julia set, c = -1, 128 cells", "julia"), (7, "Mandelbrot, default, 128 cells", "mandel"), (11, "Kleinian, default, 128 cells", "klein")):
        show(title, res.get(i, "NO RESULT"))
        if i + 1 in res:
            found, readme = check_zip(res[i + 1], label)
            show("zip read back: " + label, found)
            if label == "julia":
                show("readme.txt", readme)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    base = args[args.index("--base") + 1] if "--base" in args else "base2"
    extra = args[args.index("--use") + 1:] if "--use" in args else []
    build(base, extra)
    (real if args and args[0] == "real" else fields)()
