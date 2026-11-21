"""Write data/julia-presets.json: the Julia constants the lab offers to jump to.

  python notes/julia_build.py

The derived constants come from notes/julia_classics.py, so the file never holds a hand-copied digit string
for them. Everything else (names, notes, cameras, plane counts) is the table below; each row was chosen by
rendering it on the baseline build with notes/julia_render.py and looking at the picture.

Row: (name, c as (x, y, z) or a key of julia_classics.table(), source, planes, iterations or None, (yaw, pitch, dist), note)
  planes      the plane count of the sphere-inversion approach the picture was checked with
  iterations  given only where the set needs more than the lab's default of 14 to show its shape
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import julia_classics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONE = " Best with one plane."
ONE24 = " Best with one plane and about 24 iterations."

ROWS = [
    # ---- the named classics
    ("Basilica", "basilica", "classic", 2, None, (-1.9, 0.55, 4.8),
     "c = −1, the centre of the period-two disc. The figure in Kučera’s paper."),
    ("San Marco", "san marco", "classic", 2, None, (-1.9, 0.55, 4.8),
     "c = −3/4, where the period-two disc meets the main cardioid. A fatter Basilica."),
    ("Douady rabbit", "rabbit", "computed", 1, 24, (-1.571, 1.1, 4.6),
     "The centre of the period-three bulb. Three lobes meet at every pinch." + ONE24),
    ("Airplane", "airplane", "computed", 2, None, (-0.5, 0.3, 4.0),
     "The period-three centre on the real axis, near −1.755. A thin spine strung with spiked stars."),
    ("Cauliflower", "cauliflower", "classic", 2, None, (-1.25, 1.0, 5.0),
     "c = 1/4, the cusp of the main cardioid. In 3D it is a dimpled gourd."),
    ("Siegel disc", "siegel", "computed", 1, None, (-1.571, 1.1, 4.8),
     "On the edge of the main cardioid, turning by the golden mean." + ONE),
    ("Dendrite", "dendrite", "classic", 1, None, (-1.571, 1.15, 4.4),
     "c = i. The flat set has no inside, so the solid is a thin branching coral." + ONE),
    ("Kokopelli", "kokopelli", "computed", 1, None, (-1.571, 1.15, 4.6),
     "The centre of the period-four island above the rabbit’s bulb. A beaded coral." + ONE),
    ("Fat rabbit", "fat rabbit", "computed", 1, None, (-1.571, 1.1, 4.8),
     "The root of the rabbit’s bulb, where it joins the main cardioid." + ONE),
    ("Feigenbaum point", "feigenbaum", "classic", 2, None, (-0.9, 0.4, 5.2),
     "Near −1.4012, where the period doublings on the real axis pile up. A spiny rod."),
    ("Golden ratio", "golden ratio", "classic", 2, None, (-1.9, 0.55, 4.6),
     "c = 1 − φ, about −0.618, inside the main cardioid. A knobbly shell."),
    # ---- frequently shown values without a usual name
    ("−0.8 + 0.156i", "-0.8+0.156i", "classic", 1, 24, (-1.571, 1.05, 4.8),
     "Just outside the Mandelbrot set, beside the period-two disc." + ONE24),
    ("0.285 + 0.01i", "0.285+0.01i", "classic", 2, None, (-1.25, 1.0, 5.0),
     "Just outside the cusp of the main cardioid. In 3D it is nearly the cauliflower’s gourd."),
    ("−0.4 + 0.6i", "-0.4+0.6i", "classic", 1, None, (-1.571, 1.1, 4.6),
     "Just outside the main cardioid." + ONE),
    ("−0.70176 − 0.3842i", "-0.70176-0.3842i", "classic", 1, 24, (-1.571, 1.05, 4.8),
     "Outside the Mandelbrot set. Clusters of buds on a chain." + ONE24),
    ("−0.835 − 0.2321i", "-0.835-0.2321i", "classic", 1, 24, (-1.571, 1.05, 4.8),
     "Outside the Mandelbrot set, below the period-two disc. Curled ribbons." + ONE24),
    ("−0.7269 + 0.1889i", "-0.7269+0.1889i", "classic", 1, None, (-1.571, 1.05, 4.8),
     "Barely outside the Mandelbrot set, in the valley between its two largest parts." + ONE),
    ("0.45 + 0.1428i", "0.45+0.1428i", "classic", 1, 24, (-1.571, 1.1, 4.6),
     "Well outside the Mandelbrot set. The solid breaks into rings of islands." + ONE24),
    # ---- found by exploring with the sphere-inversion approach and two planes; all have a z part
    ("Cracked Basilica", (-1.0, 0.045, 0.026), "explored", 2, None, (-0.9, 0.4, 5.0),
     "The Basilica pushed a little off the x-axis. The fold between the two planes cracks it into blocks."),
    ("Thorn crystal", (-1.25, 0.03, 0.02), "explored", 2, None, (-1.25, 1.0, 5.0),
     "Just off the real axis where the period-two disc ends. Flat blades edged with thorns."),
    ("Split conch", (-0.75, 0.097, 0.026), "explored", 2, None, (-1.25, 1.0, 4.6),
     "The San Marco pushed off the x-axis. One long crack runs through the shell."),
    ("Flint", (-0.4, 0.13, 0.075), "explored", 2, None, (-0.9, 0.4, 4.6),
     "Off both planes, a little above the main cardioid. A split stone with flat faces."),
    ("Plated egg", (-0.2, 0.13, 0.075), "explored", 2, None, (-0.5, 0.8, 4.4),
     "Off both planes, above the middle of the main cardioid. An egg of shifted plates."),
    ("Plated ball", (0.0, 0.087, 0.05), "explored", 2, None, (-0.5, 0.8, 4.2),
     "At c = 0 the set is a plain ball. A small step off both planes slides its shell apart."),
    ("Cracked gourd", (0.25, 0.097, 0.026), "explored", 2, None, (-0.9, 0.4, 5.0),
     "The cauliflower pushed off the x-axis. The gourd splits along its seams."),
    ("Pitted gourd", (0.35, 0.05, 0.03), "explored", 2, None, (-0.9, 0.4, 5.0),
     "Off both planes, past the cusp of the main cardioid. The gourd is eaten into pits."),
]


def build():
    known = {r["key"]: r["c"] for r in julia_classics.table()}
    out = []
    for name, c, source, planes, iters, (yaw, pitch, dist), note in ROWS:
        if isinstance(c, str):
            c = (known[c][0], known[c][1], 0.0)
        # six decimals: what the lab's dials show, and far finer than a pixel
        c = [round(float(t), 6) + 0.0 for t in c]
        p = {"name": name, "note": note, "c": c, "source": source, "planes": planes}
        if iters:
            p["iter"] = iters
        p["cam"] = {"yaw": yaw, "pitch": pitch, "dist": dist}
        out.append(p)
    return out


def main():
    presets = build()
    path = os.path.join(ROOT, "data", "julia-presets.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + ",\n".join("  " + json.dumps(p, ensure_ascii=False) for p in presets) + "\n]\n")
    by = {}
    for p in presets:
        by[p["source"]] = by.get(p["source"], 0) + 1
    print("wrote data/julia-presets.json: %d presets %s, %d with a z part" % (len(presets), by, sum(1 for p in presets if p["c"][2] != 0)))


if __name__ == "__main__":
    main()
