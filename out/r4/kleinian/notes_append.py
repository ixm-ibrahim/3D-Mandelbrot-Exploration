"""Append the round 4 section (the "Turning-out sphere" entries) to notes/klein-presets.md, once."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MARK = "## Round 4: fifteen entries that move the turning-out sphere"
path = os.path.join(ROOT, "notes", "klein-presets.md")
text = open(path, encoding="utf-8").read()
if MARK in text:
    text = text[:text.index(MARK)].rstrip("\n") + "\n"
new = [p for p in json.load(open(os.path.join(ROOT, "data", "klein-presets.json"), encoding="utf-8")) if p.get("group") == "Turning-out sphere"]
fitted = {(round(f["k"]["cx"], 4), round(f["k"]["cy"], 4), round(f["k"]["cz"], 4), f["k"]["mx"], f["k"]["three"]): f
          for f in json.load(open(os.path.join(HERE, "shots", "try1-fitted.json"), encoding="utf-8"))}
rows = []
for i, p in enumerate(new):
    k, cam = p["k"], p["cam"]
    f = fitted.get((round(k["cx"], 4), round(k["cy"], 4), round(k["cz"], 4), k["mx"], k["three"]), {})
    rows.append("| %d | %s | (%g, %g, %g) | %s | (%g, %g, %g) | %g | %s | %g, %g, %g, (%g, %g, %g) |" % (
        19 + i, p["name"], k["mx"], k["my"], k["mz"], "three" if k["three"] else "two", k["cx"], k["cy"], k["cz"], k["invR"],
        f.get("clear", ""), cam["yaw"], cam["pitch"], cam["dist"], *cam["target"]))
section = """
%s

Added for the user's remark N9 ("you also don't have any klein presets that mess with the turning-out sphere").
Nothing was removed and the first nineteen entries are unchanged. Full account: `notes/r4-kleinian.md`.

Every new entry reuses a group that is already in the list and changes only the sphere: its centre, and with it
the radius that makes the picture fit. Each has `"group": "Turning-out sphere"`, a `source` that starts with
`sphere`, and a camera with a `target` (the object is no longer centred on the origin when the centre leaves the
middle of a gap). `iter` is 60 as in the other entries; the page ignores it.

| # | Name | mu | Maps | Centre | invR | Room around the centre | Camera yaw, pitch, dist, target |
|---|---|---|---|---|---|---|---|
%s

"Room around the centre" is the distance from the centre to the nearest pearl or wall, from the pearl list. The
smaller it is, the larger the nearest pearls come out and the smaller the radius has to be.

Kinds of centre, and what each does to the picture:
- **To one side of a gap, or close to a wall** (19, 20, 23): the nearest wall or pearl grows into one large ball and
  the others gather round it.
- **Another gap of the same group** (24, 26, 30, 31): a different picture of the same pearls. Away from the gap in
  the middle the half-turn symmetry is gone.
- **A small sphere in a narrow gap** (25, 27, 28): one neighbourhood shown large.
- **Off the plane the pearls lie in** (29, 32): the flat disc of a two-map group curls into a bowl or a ball.
- **Moved in depth with the third map on** (21, 22, 33): the same lattice of pearls from another gap of it.

What each needs: the default field of view and a drawing radius of 3 or more (as the first nineteen), nothing
else. They were drawn at depth 150 (Fine, 1400x950), at depth 60, and at 375x812; the pictures at 60 and 150 do
not differ visibly (`out/r4/kleinian/shots/fine-sheet-*.png`, `d60-sheet-0.png`, `phone-sheet-0.png`).

How they were checked before drawing (`out/r4/kleinian/find.py`): the centre lies in a gap, and every pearl that
will look big in the picture is whole for the shader's search (14 random points inside each of the largest pearls
must all come out solid). The second check is new this round. The first nineteen were only tested for pearls of
radius 0.03 and up, and entry 8 (5/13 cusp) fails it: the five pearls nearest its centre are invisible to the
search, and one shows as a sliver at the lower left. Its centre was left as it is.

Rejected candidates are in `out/r4/kleinian/shots/try1-sheet-*.png`: mostly two plain wall spheres with little
between them (centres far off the plane of a two-map group, as the first round also found), and one centre on the
1/15 cusp that gave an endless string.
""" % (MARK, "\n".join(rows))
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text.rstrip("\n") + "\n" + section)
print("appended", len(rows), "rows")
