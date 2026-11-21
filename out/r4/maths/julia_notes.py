"""Rewrite the notes in data/julia-presets.json in plain words and set the cameras that needed it.

  python out/r4/maths/julia_notes.py            (rewrites data/julia-presets.json in place; safe to run again)

The notes are written for someone who knows the picture of the Mandelbrot set but not the names of its parts:
"the heart-shaped body" is the main cardioid, "the round bulb on the left" the period-two disc, "the largest
bulb on top" the period-three bulb. Each note says where the point is and what the solid looks like with the
page as it opens (Sphere inversions, one plane). Where a picture needs a setting the entry does not change, the
note ends with that as a hint. Nothing but `note` and the cameras listed in CAMS is touched; no entry is removed.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PATH = os.path.join(ROOT, "data", "julia-presets.json")
TWO = "set Planes to 2 under Sphere inversions"
NOTES = {
    "Basilica": "c = −1, the middle of the round bulb on the left of the Mandelbrot set. A string of rounded beads, and the figure in Kučera’s paper.",
    "San Marco": "c = −3/4, where the round bulb on the left of the Mandelbrot set touches its heart-shaped body. The Basilica’s beads have run together into one scalloped shell.",
    "Douady rabbit": "The centre of the largest bulb on top of the Mandelbrot set. Three lobes meet at every pinch. The lobes stand out better at about 24 iterations.",
    "Airplane": "Near −1.755 on the x-axis, the middle of the small copy of the Mandelbrot set far out on its left spike. A thin spine strung with spiky beads.",
    "Cauliflower": "c = 1/4, the tip of the dent on the right of the Mandelbrot set’s heart-shaped body. A smooth gourd whose frilled rim is the 2D cauliflower.",
    "Siegel disc": "On the rim of the Mandelbrot set’s heart-shaped body, at an angle set by the golden ratio. A smooth slab with a frilled edge.",
    "Dendrite": "c = i, the tip of a thin hair on top of the Mandelbrot set. The 2D set has no inside, so the solid is a thin branching coral.",
    "Kokopelli": "The middle of a tiny copy of the Mandelbrot set, on a hair above its largest top bulb. A beaded coral.",
    "Fat rabbit": "The point where the largest top bulb joins the Mandelbrot set’s heart-shaped body. The rabbit’s lobes have swollen into one slab with a frilled edge.",
    "Feigenbaum point": "Near −1.4012 on the x-axis, where the row of ever smaller bulbs on the left of the Mandelbrot set ends. A flat, spiny rod.",
    "Golden ratio": "About −0.618 on the x-axis, inside the Mandelbrot set’s heart-shaped body. A smooth lens with a scalloped rim.",
    "−0.8 + 0.156i": "Just outside the Mandelbrot set, in the valley between its heart-shaped body and the round bulb on the left. A row of bulbs about to come apart. They are still fused at 14 iterations: raise the iterations to about 24.",
    "0.285 + 0.01i": "Just outside the Mandelbrot set, in the dent on its right. In 3D it is almost the Cauliflower’s gourd.",
    "−0.4 + 0.6i": "Just outside the Mandelbrot set’s heart-shaped body, at its upper left. A slab with a frilled edge.",
    "−0.70176 − 0.3842i": "Outside the Mandelbrot set, at the lower left of its heart-shaped body. Clusters of buds on a chain. They are still fused at 14 iterations: raise the iterations to about 24.",
    "−0.835 − 0.2321i": "Outside the Mandelbrot set, just below the round bulb on its left. Curled ribbons. They are still fused at 14 iterations: raise the iterations to about 24.",
    "−0.7269 + 0.1889i": "Barely outside the Mandelbrot set, in the valley between its two largest parts. A scalloped shell, close to the San Marco.",
    "0.45 + 0.1428i": "Well outside the Mandelbrot set, to its right. The solid breaks into rings of islands.",
    "Cracked Basilica": "The Basilica pushed a little off the x-axis. With one plane it stays a smooth Basilica. The cracks of the name belong to the earlier version: %s." % TWO,
    "Thorn crystal": "Just off the x-axis, where the round bulb on the left of the Mandelbrot set ends. Flat blades edged with thorns.",
    "Split conch": "The San Marco pushed off the x-axis. With one plane it is a smooth conch. The long crack of the name belongs to the earlier version: %s." % TWO,
    "Flint": "Inside the Mandelbrot set’s heart-shaped body, a little off the x-axis. With one plane it is a smooth egg with a frilled band. The split stone of the name belongs to the earlier version: %s." % TWO,
    "Plated egg": "Near the middle of the Mandelbrot set’s heart-shaped body, a little off the x-axis. With one plane it is a smooth egg. The shifted plates of the name belong to the earlier version: %s." % TWO,
    "Plated ball": "At c = 0 the set is a plain ball, and this is a small step away from it. With one plane it stays a smooth ball. The plates of the name belong to the earlier version: %s." % TWO,
    "Cracked gourd": "The Cauliflower pushed off the x-axis. With one plane it is a smooth gourd with a few dimples. The cracks of the name belong to the earlier version: %s." % TWO,
    "Pitted gourd": "In the dent on the right of the Mandelbrot set, a little off the x-axis. A gourd eaten into pits. There are more of them in the earlier version: %s." % TWO,
}
# Cameras: only the distance changes. The Airplane ran out of the picture at 4.0; the right tips of the other two
# reached the zoom slider (5.2 and 5.0 before).
CAMS = {"Airplane": 5.2, "Feigenbaum point": 5.6, "Thorn crystal": 5.4}


def main():
    with open(PATH, encoding="utf-8") as f:
        items = json.load(f)
    names = [it["name"] for it in items]
    missing = [n for n in NOTES if n not in names] + [n for n in names if n not in NOTES]
    if missing:
        raise SystemExit("names do not match the data: %r" % missing)
    for it in items:
        it["note"] = NOTES[it["name"]]
        if it["name"] in CAMS:
            it["cam"]["dist"] = CAMS[it["name"]]
        bad = [ch for ch in "—!" if ch in it["note"]]
        if bad:
            raise SystemExit("%s: the note holds %r" % (it["name"], bad))
    rows = ",\n".join("  " + json.dumps(it, ensure_ascii=False) for it in items)
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + rows + "\n]\n")
    words = [len(it["note"].split()) for it in items]
    print("%d entries written; notes run from %d to %d words" % (len(items), min(words), max(words)))


if __name__ == "__main__":
    main()
