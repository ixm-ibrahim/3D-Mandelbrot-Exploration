"""The chosen "Turning-out sphere" entries: names and notes here, numbers from the fitted candidates.

   python out/r4/kleinian/final.py            writes out/r4/kleinian/sel.json (the new entries, in the data file's format)
   python out/r4/kleinian/final.py --write    also appends them to data/klein-presets.json (the first nineteen are kept as they are)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GROUP = "Turning-out sphere"

# index in shots/try1-fitted.json, name, note
CHOSEN = [
    (2, "0/1 cusp, sphere moved to one side",
     "The starting group with two maps. The sphere sits to one side of the big gap, so the pearls close into a ring around one large window."),
    (1, "0/1 cusp, sphere close to a wall",
     "Two maps. The sphere sits low in the gap, close to one wall. That wall becomes a large ball inside a collar of pearls."),
    (5, "0/1 cusp with the third map, sphere moved in depth",
     "The starting group, turned out from a point one unit further back. The two wall spheres are joined by a net of pearls with large round windows."),
    (6, "0/1 cusp with the third map, sphere moved across and in depth",
     "The same group again, with the sphere one unit to the side and one unit back. The windows now face the camera."),
    (8, "0/1 cusp with the third map, sphere close to a wall",
     "The sphere sits half way between the middle of the gap and one wall, so one wall sphere grows and the other shrinks."),
    (12, "1/2 cusp, through the gap under the upper wall",
     "Two maps. From this gap the picture is a disc of pearls with two round windows."),
    (15, "1/2 cusp, small sphere in a narrow gap",
     "A small sphere in a narrow gap beside the lower wall. The wall fills the middle and the pearls nearest the sphere stand in a ring around it."),
    (18, "1/3 cusp, through a side gap",
     "Two maps. The sphere has left the middle gap for the one beside it, so the half-turn symmetry is gone and the disc opens on one side."),
    (19, "1/3 cusp, small sphere beside the large pearls",
     "A small sphere in a narrow gap. The pearls next to it come out large and the rest of the disc is cut by three round bays."),
    (22, "1/4 cusp, small sphere between the strings",
     "Two maps. A small sphere between two strings of pearls: the nearest pearl comes out large and the strings fan out behind it."),
    (23, "1/4 cusp, sphere lifted off the plane",
     "The sphere of the 1/4 cusp entry raised half a unit out of the plane the pearls lie in. The flat disc curls into a bowl under one wall sphere."),
    (25, "2/5 cusp, sphere in the middle gap",
     "Two maps. The sphere sits in the gap between the two large pearls, which come out at opposite ends of the picture."),
    (27, "1/15 cusp, through the opposite gap",
     "The spirals from the gap on the other side of the strip: one wall sphere with the spirals wound around it."),
    (30, "Leaning 30°, sphere lifted off the plane",
     "μ = √3·i + j with two maps. The sphere is raised half a unit in depth, so the two wall spheres lean together inside a ring of pearls."),
    (33, "Leaning 30° with the third map, sphere moved across and in depth",
     "The leaning group with the third map on, turned out from a narrow gap one unit back. One pearl comes out large in front of a disc with round windows."),
]


def entries():
    fitted = json.load(open(os.path.join(HERE, "shots", "try1-fitted.json"), encoding="utf-8"))
    out = []
    for idx, name, note in CHOSEN:
        f = fitted[idx]
        k = f["k"]
        kk = {"mx": k["mx"], "my": k["my"], "mz": k["mz"], "three": bool(k["three"]), "L": float(k["L"]), "iter": 60,
              "invR": k["invR"], "cx": k["cx"], "cy": k["cy"], "cz": k["cz"]}
        cam = {"yaw": f["cam"]["yaw"], "pitch": f["cam"]["pitch"], "dist": f["cam"]["dist"], "target": f["cam"]["target"]}
        # the first word of `source` is what the page falls back on for the group heading
        base = f["group"].replace("x3", "").replace("lean30", "leaning 30°")
        out.append({"name": name, "note": note, "k": kk, "cam": cam, "source": "sphere " + base + (" cusp" if "/" in base else ""), "group": GROUP})
    return out


def main():
    new = entries()
    json.dump(new, open(os.path.join(HERE, "sel.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(len(new), "entries -> out/r4/kleinian/sel.json")
    if "--write" in sys.argv:
        path = os.path.join(ROOT, "data", "klein-presets.json")
        old = json.load(open(path, encoding="utf-8"))
        keep = [p for p in old if p.get("group") != GROUP]
        assert len(keep) == 19, len(keep)
        rows = ",\n".join("  " + json.dumps(p, ensure_ascii=False) for p in keep + new)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("[\n" + rows + "\n]\n")
        print("data/klein-presets.json:", len(keep) + len(new), "entries")


if __name__ == "__main__":
    main()
