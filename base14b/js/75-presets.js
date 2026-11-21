// ---------- preset lists (Julia points, Kleinian groups) and the user's own saved Julia points.
// The build does not load JSON, so the two arrays below are copies of data/julia-presets.json and
// data/klein-presets.json. notes/ui_embed.py writes them between the marker lines: change the JSON
// and run that script, do not edit the arrays here.
// <julia-data>
const JULIA_PRESETS = [
  {"name": "Basilica", "note": "c = −1, the middle of the round bulb on the left of the Mandelbrot set. A string of rounded beads, and the figure in Kučera’s paper.", "c": [-1.0, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.9, "pitch": 0.55, "dist": 4.8}},
  {"name": "San Marco", "note": "c = −3/4, where the round bulb on the left of the Mandelbrot set touches its heart-shaped body. The Basilica’s beads have run together into one scalloped shell.", "c": [-0.75, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.9, "pitch": 0.55, "dist": 4.8}},
  {"name": "Douady rabbit", "note": "The centre of the largest bulb on top of the Mandelbrot set. Three lobes meet at every pinch. The lobes stand out better at about 24 iterations.", "c": [-0.122561, 0.744862, 0.0], "source": "computed", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.6}},
  {"name": "Airplane", "note": "Near −1.755 on the x-axis, the middle of the small copy of the Mandelbrot set far out on its left spike. A thin spine strung with spiky beads.", "c": [-1.754878, 0.0, 0.0], "source": "computed", "planes": 2, "cam": {"yaw": -0.5, "pitch": 0.3, "dist": 5.2}},
  {"name": "Cauliflower", "note": "c = 1/4, the tip of the dent on the right of the Mandelbrot set’s heart-shaped body. A smooth gourd whose frilled rim is the 2D cauliflower.", "c": [0.25, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 5.0}},
  {"name": "Siegel disc", "note": "On the rim of the Mandelbrot set’s heart-shaped body, at an angle set by the golden ratio. A smooth slab with a frilled edge.", "c": [-0.390541, -0.586788, 0.0], "source": "computed", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.8}},
  {"name": "Dendrite", "note": "c = i, the tip of a thin hair on top of the Mandelbrot set. The 2D set has no inside, so the solid is a thin branching coral.", "c": [0.0, 1.0, 0.0], "source": "classic", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.15, "dist": 4.4}},
  {"name": "Kokopelli", "note": "The middle of a tiny copy of the Mandelbrot set, on a hair above its largest top bulb. A beaded coral.", "c": [-0.15652, 1.032247, 0.0], "source": "computed", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.15, "dist": 4.6}},
  {"name": "Fat rabbit", "note": "The point where the largest top bulb joins the Mandelbrot set’s heart-shaped body. The rabbit’s lobes have swollen into one slab with a frilled edge.", "c": [-0.125, 0.649519, 0.0], "source": "computed", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.8}},
  {"name": "Feigenbaum point", "note": "Near −1.4012 on the x-axis, where the row of ever smaller bulbs on the left of the Mandelbrot set ends. A flat, spiny rod.", "c": [-1.401155, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.6}},
  {"name": "Golden ratio", "note": "About −0.618 on the x-axis, inside the Mandelbrot set’s heart-shaped body. A smooth lens with a scalloped rim.", "c": [-0.618034, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.9, "pitch": 0.55, "dist": 4.6}},
  {"name": "−0.8 + 0.156i", "note": "Just outside the Mandelbrot set, in the valley between its heart-shaped body and the round bulb on the left. A row of bulbs about to come apart. They are still fused at 14 iterations: raise the iterations to about 24.", "c": [-0.8, 0.156, 0.0], "source": "classic", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.05, "dist": 4.8}},
  {"name": "0.285 + 0.01i", "note": "Just outside the Mandelbrot set, in the dent on its right. In 3D it is almost the Cauliflower’s gourd.", "c": [0.285, 0.01, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 5.0}},
  {"name": "−0.4 + 0.6i", "note": "Just outside the Mandelbrot set’s heart-shaped body, at its upper left. A slab with a frilled edge.", "c": [-0.4, 0.6, 0.0], "source": "classic", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.6}},
  {"name": "−0.70176 − 0.3842i", "note": "Outside the Mandelbrot set, at the lower left of its heart-shaped body. Clusters of buds on a chain. They are still fused at 14 iterations: raise the iterations to about 24.", "c": [-0.70176, -0.3842, 0.0], "source": "classic", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.05, "dist": 4.8}},
  {"name": "−0.835 − 0.2321i", "note": "Outside the Mandelbrot set, just below the round bulb on its left. Curled ribbons. They are still fused at 14 iterations: raise the iterations to about 24.", "c": [-0.835, -0.2321, 0.0], "source": "classic", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.05, "dist": 4.8}},
  {"name": "−0.7269 + 0.1889i", "note": "Barely outside the Mandelbrot set, in the valley between its two largest parts. A scalloped shell, close to the San Marco.", "c": [-0.7269, 0.1889, 0.0], "source": "classic", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.05, "dist": 4.8}},
  {"name": "0.45 + 0.1428i", "note": "Well outside the Mandelbrot set, to its right. The solid breaks into rings of islands.", "c": [0.45, 0.1428, 0.0], "source": "classic", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.6}},
  {"name": "Cracked Basilica", "note": "The Basilica pushed a little off the x-axis. With one plane it stays a smooth Basilica. The cracks of the name belong to the earlier version: choose Sphere inversions, two planes in the Approach section.", "c": [-1.0, 0.045, 0.026], "source": "two planes", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
  {"name": "Thorn crystal", "note": "Just off the x-axis, where the round bulb on the left of the Mandelbrot set ends. Flat blades edged with thorns.", "c": [-1.25, 0.03, 0.02], "source": "explored", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 5.4}},
  {"name": "Split conch", "note": "The San Marco pushed off the x-axis. With one plane it is a smooth conch. The long crack of the name belongs to the earlier version: choose Sphere inversions, two planes in the Approach section.", "c": [-0.75, 0.097, 0.026], "source": "two planes", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 4.6}},
  {"name": "Flint", "note": "Inside the Mandelbrot set’s heart-shaped body, a little off the x-axis. With one plane it is a smooth egg with a frilled band. The split stone of the name belongs to the earlier version: choose Sphere inversions, two planes in the Approach section.", "c": [-0.4, 0.13, 0.075], "source": "two planes", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 4.6}},
  {"name": "Plated egg", "note": "Near the middle of the Mandelbrot set’s heart-shaped body, a little off the x-axis. With one plane it is a smooth egg. The shifted plates of the name belong to the earlier version: choose Sphere inversions, two planes in the Approach section.", "c": [-0.2, 0.13, 0.075], "source": "two planes", "planes": 2, "cam": {"yaw": -0.5, "pitch": 0.8, "dist": 4.4}},
  {"name": "Plated ball", "note": "At c = 0 the set is a plain ball, and this is a small step away from it. With one plane it stays a smooth ball. The plates of the name belong to the earlier version: choose Sphere inversions, two planes in the Approach section.", "c": [0.0, 0.087, 0.05], "source": "two planes", "planes": 2, "cam": {"yaw": -0.5, "pitch": 0.8, "dist": 4.2}},
  {"name": "Cracked gourd", "note": "The Cauliflower pushed off the x-axis. With one plane it is a smooth gourd with a few dimples. The cracks of the name belong to the earlier version: choose Sphere inversions, two planes in the Approach section.", "c": [0.25, 0.097, 0.026], "source": "two planes", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
  {"name": "Pitted gourd", "note": "In the dent on the right of the Mandelbrot set, a little off the x-axis. A gourd eaten into pits. There are more of them in the earlier version: choose Sphere inversions, two planes in the Approach section.", "c": [0.35, 0.05, 0.03], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
];
// </julia-data>
// <klein-data>
const KLEIN_PRESETS = [
  {"name": "0/1 cusp, the starting view", "note": "The lab's own starting group, μ = 2i. Two wall spheres and pearls that just touch, spread in every direction by the third map.", "k": {"mx": 0.0, "my": 2.0, "mz": 0.0, "three": true, "L": 1.0, "iter": 60, "invR": 1.2, "cx": 1, "cy": 1, "cz": 0}, "cam": {"yaw": 0.35, "pitch": 0.35, "dist": 7}, "source": "cusp 0/1"},
  {"name": "0/1 cusp, one row of pearls", "note": "The same group without the third map, seen from above. The pearls and the round gaps between them together make the Apollonian gasket.", "k": {"mx": 0.0, "my": 2.0, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 1.162, "cx": 1, "cy": 1, "cz": 0}, "cam": {"yaw": -1.5708, "pitch": 1.15, "dist": 6.4}, "source": "cusp 0/1"},
  {"name": "1/15 cusp, spirals", "note": "A classic cusp. The strings of pearls wind into spirals before they close up. Two maps, seen from above.", "k": {"mx": 0.011279, "my": 1.958591, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.8, "cx": -1, "cy": 0.4894, "cz": 0}, "cam": {"yaw": -1.5708, "pitch": 1.15, "dist": 6.4}, "source": "cusp 1/15"},
  {"name": "1/2 cusp", "note": "μ = 1 + √3·i. Two maps. The picture is mirror-symmetric, with round windows between the strings of pearls.", "k": {"mx": 1.0, "my": 1.732051, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.879, "cx": -1, "cy": 0.5774, "cz": 0}, "cam": {"yaw": -1.2, "pitch": 0.75, "dist": 6.4}, "source": "cusp 1/2"},
  {"name": "1/3 cusp", "note": "Turned out through the middle of a round gap, which gives the picture a half-turn symmetry. Third map on.", "k": {"mx": 0.581203, "my": 1.693897, "mz": 0.0, "three": true, "L": 1.0, "iter": 60, "invR": 0.662, "cx": 0.2906, "cy": 0.8469, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "cusp 1/3"},
  {"name": "2/5 cusp", "note": "Two maps. A short chain of pearls runs between two large ones, and the picture has a half-turn symmetry.", "k": {"mx": 0.766588, "my": 1.642139, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.561, "cx": 1.3833, "cy": 0.8211, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "cusp 2/5"},
  {"name": "1/5 cusp", "note": "Third map on. Two large pearls joined by a short chain, with round windows on either side.", "k": {"mx": 0.220105, "my": 1.766742, "mz": 0.0, "three": true, "L": 1.0, "iter": 60, "invR": 0.465, "cx": 0.1101, "cy": 0.8834, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "cusp 1/5"},
  {"name": "1/4 cusp", "note": "Two maps, seen from above. One wall sphere, with strings of pearls closing around round windows.", "k": {"mx": 0.352201, "my": 1.721433, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.775, "cx": -0.647, "cy": 1.2734, "cz": 0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "cusp 1/4"},
  {"name": "5/13 cusp, branching", "note": "5/13 is a ratio of Fibonacci numbers, like 1/2, 1/3, 2/5 and 3/8 before it. The pearls thin out into branches.", "k": {"mx": 0.718292, "my": 1.622179, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.48, "cx": 0.548, "cy": 0.855, "cz": 0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "cusp 5/13"},
  {"name": "8/21 cusp, near the golden mean", "note": "The next fraction in the same sequence: 8/21 is close to 0.382, one minus the golden mean. Fine branches of pearls stand around one wall sphere.", "k": {"mx": 0.700468, "my": 1.62031, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.622, "cx": -0.996, "cy": 0.293, "cz": 0}, "cam": {"yaw": -1.5708, "pitch": 1.15, "dist": 6.4}, "source": "cusp 8/21"},
  {"name": "Above the 3/10 cusp", "note": "μ raised by 0.09 from the 3/10 cusp into the family. The strings of pearls have come apart into one loose chain.", "k": {"mx": 0.5, "my": 1.748312, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.657, "cx": -0.75, "cy": 0.8742, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "inside"},
  {"name": "Above the 1/2 cusp", "note": "μ raised by 0.17 from the 1/2 cusp. The strings of pearls no longer close up.", "k": {"mx": 1.0, "my": 1.902051, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.902, "cx": -1, "cy": 0.6, "cz": 0}, "cam": {"yaw": -1.5708, "pitch": 1.15, "dist": 6.4}, "source": "inside"},
  {"name": "Inside, near the 0/1 cusp", "note": "μ = 0.1 + 1.95i, a little above the boundary. Two wall spheres with horns that curl but do not close.", "k": {"mx": 0.1, "my": 1.95, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.982, "cx": 1.05, "cy": 0.975, "cz": 0.0}, "cam": {"yaw": -1.5708, "pitch": 1.15, "dist": 6.4}, "source": "inside"},
  {"name": "1/3 cusp, leaning in depth", "note": "The two maps of the 1/3 cusp turned 25° about the x-axis, which gives μ a j part. The walls now cut the group at a slant, so the pearls come out in unequal sizes.", "k": {"mx": 0.581203, "my": 1.535192, "mz": 0.715872, "three": false, "L": 1.0, "iter": 60, "invR": 0.656, "cx": 0.2906, "cy": 0.7676, "cz": 0.3579}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "explored"},
  {"name": "2/5 cusp, leaning in depth", "note": "The 2/5 cusp turned 20° about the x-axis, with the third map on.", "k": {"mx": 0.766588, "my": 1.543106, "mz": 0.561645, "three": true, "L": 1.0, "iter": 60, "invR": 0.561, "cx": 1.3833, "cy": 0.7716, "cz": 0.2808}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "explored"},
  {"name": "0/1 cusp, leaning 30°", "note": "μ = √3·i + j: the starting group turned 30° about the x-axis. Two maps, seen from above.", "k": {"mx": 0.0, "my": 1.732051, "mz": 1.0, "three": false, "L": 1.0, "iter": 60, "invR": 1.092, "cx": 1, "cy": 0.866, "cz": 0}, "cam": {"yaw": -1.5708, "pitch": 1.15, "dist": 6.4}, "source": "explored"},
  {"name": "Leaning 30°, seen across", "note": "The same leaning group with the third map on, seen from the side: a disc of pearls with round windows.", "k": {"mx": 0.0, "my": 1.732051, "mz": 1.0, "three": true, "L": 1.0, "iter": 60, "invR": 0.862, "cx": 0, "cy": 1.13, "cz": 0}, "cam": {"yaw": 0.0, "pitch": 0.25, "dist": 6.4}, "source": "explored"},
  {"name": "Leaning both ways", "note": "μ = 0.5 + 1.7i + 0.5j: a real part and a j part at once, a little inside the boundary.", "k": {"mx": 0.5, "my": 1.7, "mz": 0.5, "three": false, "L": 1.0, "iter": 60, "invR": 0.825, "cx": -0.988, "cy": 0.53, "cz": 0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4}, "source": "explored"},
  {"name": "Stretched in depth", "note": "μ = 2i with the third map's step doubled (L = 2), so the rows of pearls stand twice as far apart in depth.", "k": {"mx": 0.0, "my": 2.0, "mz": 0.0, "three": true, "L": 2.0, "iter": 60, "invR": 1.157, "cx": 1, "cy": 1, "cz": 0}, "cam": {"yaw": 0.5, "pitch": 0.5, "dist": 6.4}, "source": "explored"},
  {"name": "0/1 cusp, sphere moved to one side", "note": "The starting group with two maps. The sphere sits to one side of the big gap, so the pearls close into a ring around one large window.", "k": {"mx": 0.0, "my": 2.0, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.958, "cx": 0.55, "cy": 1.0, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [-0.412, -0.033, 0.138]}, "source": "sphere 0/1 cusp", "group": "Turning-out sphere"},
  {"name": "0/1 cusp, sphere close to a wall", "note": "Two maps. The sphere sits low in the gap, close to one wall. That wall becomes a large ball inside a collar of pearls.", "k": {"mx": 0.0, "my": 2.0, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.892, "cx": 1.0, "cy": 0.45, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [0.005, -0.707, 0.342]}, "source": "sphere 0/1 cusp", "group": "Turning-out sphere"},
  {"name": "0/1 cusp, third map: moved back", "note": "The starting group, turned out from a point one unit further back. The two wall spheres are joined by a net of pearls with large round windows.", "k": {"mx": 0.0, "my": 2.0, "mz": 0.0, "three": true, "L": 1.0, "iter": 60, "invR": 1.14, "cx": 1.0, "cy": 1.0, "cz": 1.0}, "cam": {"yaw": 0.5, "pitch": 0.45, "dist": 6.4, "target": [0.004, 0.166, 0.04]}, "source": "sphere 0/1 cusp", "group": "Turning-out sphere"},
  {"name": "0/1 cusp, third map: across and back", "note": "The same group again, with the sphere one unit to the side and one unit back. The windows now face the camera.", "k": {"mx": 0.0, "my": 2.0, "mz": 0.0, "three": true, "L": 1.0, "iter": 60, "invR": 1.097, "cx": 0.0, "cy": 1.0, "cz": 1.0}, "cam": {"yaw": 0.5, "pitch": 0.45, "dist": 6.4, "target": [0.082, 0.104, 0.03]}, "source": "sphere 0/1 cusp", "group": "Turning-out sphere"},
  {"name": "0/1 cusp, third map: close to a wall", "note": "The sphere sits half way between the middle of the gap and one wall, so one wall sphere grows and the other shrinks.", "k": {"mx": 0.0, "my": 2.0, "mz": 0.0, "three": true, "L": 1.0, "iter": 60, "invR": 0.967, "cx": 1.0, "cy": 0.5, "cz": 0.0}, "cam": {"yaw": 0.5, "pitch": 0.45, "dist": 6.4, "target": [0.147, -0.578, 0.169]}, "source": "sphere 0/1 cusp", "group": "Turning-out sphere"},
  {"name": "1/2 cusp, gap under the upper wall", "note": "Two maps. From this gap the picture is a disc of pearls with two round windows.", "k": {"mx": 1.0, "my": 1.732051, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.814, "cx": 0.0, "cy": 1.1547, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [-0.01, -0.138, 0.264]}, "source": "sphere 1/2 cusp", "group": "Turning-out sphere"},
  {"name": "1/2 cusp, small sphere, narrow gap", "note": "A small sphere in a narrow gap beside the lower wall. The wall fills the middle and the pearls nearest the sphere stand in a ring around it.", "k": {"mx": 1.0, "my": 1.732051, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.593, "cx": 0.8707, "cy": 0.2015, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [-0.274, -0.8, 0.415]}, "source": "sphere 1/2 cusp", "group": "Turning-out sphere"},
  {"name": "1/3 cusp, through a side gap", "note": "Two maps. The sphere has left the middle gap for the one beside it, so the half-turn symmetry is gone and the disc opens on one side.", "k": {"mx": 0.581203, "my": 1.693897, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.758, "cx": -0.418, "cy": 1.2213, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [-0.01, -0.154, 0.287]}, "source": "sphere 1/3 cusp", "group": "Turning-out sphere"},
  {"name": "1/3 cusp, beside the large pearls", "note": "A small sphere in a narrow gap. The pearls next to it come out large and the rest of the disc is cut by three round bays.", "k": {"mx": 0.581203, "my": 1.693897, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.65, "cx": 0.997, "cy": 0.7236, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [0.006, 0.648, 0.215]}, "source": "sphere 1/3 cusp", "group": "Turning-out sphere"},
  {"name": "1/4 cusp, between the strings", "note": "Two maps. A small sphere between two strings of pearls: the nearest pearl comes out large and the strings fan out behind it.", "k": {"mx": 0.352201, "my": 1.721433, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.549, "cx": 0.3527, "cy": 0.6928, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [0.005, 0.003, 0.191]}, "source": "sphere 1/4 cusp", "group": "Turning-out sphere"},
  {"name": "1/4 cusp, sphere lifted off the plane", "note": "The sphere of the 1/4 cusp entry raised half a unit out of the plane the pearls lie in. The flat disc curls into a bowl under one wall sphere.", "k": {"mx": 0.352201, "my": 1.721433, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.88, "cx": -0.647, "cy": 1.2734, "cz": 0.5}, "cam": {"yaw": -1.2, "pitch": 0.6, "dist": 6.4, "target": [0.034, 0.116, 0.024]}, "source": "sphere 1/4 cusp", "group": "Turning-out sphere"},
  {"name": "2/5 cusp, sphere in the middle gap", "note": "Two maps. The sphere sits in the gap between the two large pearls, which come out at opposite ends of the picture.", "k": {"mx": 0.766588, "my": 1.642139, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.532, "cx": 0.6174, "cy": 0.8202, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [0.06, -0.041, 0.208]}, "source": "sphere 2/5 cusp", "group": "Turning-out sphere"},
  {"name": "1/15 cusp, through the opposite gap", "note": "The spirals from the gap on the other side of the strip: one wall sphere with the spirals wound around it.", "k": {"mx": 0.011279, "my": 1.958591, "mz": 0.0, "three": false, "L": 1.0, "iter": 60, "invR": 0.766, "cx": 0.9823, "cy": 0.4457, "cz": 0.0}, "cam": {"yaw": -1.35, "pitch": 1.0, "dist": 6.4, "target": [-0.045, -0.119, 0.282]}, "source": "sphere 1/15 cusp", "group": "Turning-out sphere"},
  {"name": "Leaning 30°, lifted off the plane", "note": "μ = √3·i + j with two maps. The sphere is raised half a unit in depth, so the two wall spheres lean together inside a ring of pearls.", "k": {"mx": 0.0, "my": 1.732051, "mz": 1.0, "three": false, "L": 1.0, "iter": 60, "invR": 1.052, "cx": 1.0, "cy": 0.866, "cz": 0.5}, "cam": {"yaw": -1.2, "pitch": 0.6, "dist": 6.4, "target": [-0.008, -0.202, 0.051]}, "source": "sphere leaning 30°", "group": "Turning-out sphere"},
  {"name": "Leaning 30°, third map: moved back", "note": "The leaning group with the third map on, turned out from a narrow gap one unit back. One pearl comes out large in front of a disc with round windows.", "k": {"mx": 0.0, "my": 1.732051, "mz": 1.0, "three": true, "L": 1.0, "iter": 60, "invR": 0.732, "cx": 0.0, "cy": 0.866, "cz": 1.0}, "cam": {"yaw": 0.5, "pitch": 0.45, "dist": 6.4, "target": [0.237, 0.66, -0.001]}, "source": "sphere leaning 30°", "group": "Turning-out sphere"},
];
// </klein-data>

// ---------- what a list entry does
// An entry sets only what it is about. A Julia entry sets the point c. A Kleinian entry sets the group (mu, L,
// the third map) and its turning-out sphere. The camera, the iterations, the depth of the search, the quality and
// the approach are the user's and stay as they are. "Frame it" is the separate, camera-only step.
const presetSame = (a, b) => Math.abs(a - b) < 1e-9;
// Preset cameras were chosen on a wide stage with the starting field of view. On a tall, narrow stage the camera
// backs off so that wide sets are not cut off at the sides (Julia) or hidden behind the zoom slider (Kleinian).
const presetNarrow = () => Math.max(1, 1.2 * stage.clientHeight / Math.max(1, stage.clientWidth));
const presetNarrowK = () => (stage.clientWidth < stage.clientHeight ? 1.2 : 1);
// A recommended distance, as it has to be at the field of view in use. The distances in the lists were chosen at
// the starting field of view (0.32). A solid that just fitted the picture there still does at another one from
// a distance that goes with the sine of half the angle. (Going by the tangent, as this did before, put the camera
// inside the solid at a wide angle.)
const presetFit = f => f / Math.hypot(1, f);
const presetDist = (dist, back) => dist * back * presetFit(0.32) / presetFit(S.view.fov);
// Make room for a view that a button promises to show whole: a zoom limit that the distance lies beyond is moved
// just as far as that distance, and a drawing radius smaller than the solid (`radius`, from the centre) is raised
// to hold it. Limits that are not in the way stay as the user set them. -> the distance, inside the hard limits
function presetRoom(dist, radius) {
  const v = S.view, d = clamp(dist, CAM_LIM.zmin[0], CAM_LIM.zmax[1]);
  if (d > v.zmax) v.zmax = d;
  if (d < v.zmin) v.zmin = d;
  if (radius > 0 && v.bound < radius) v.bound = radius;
  return d;
}
// Move the camera, and the frame of the 2D view, to a recommended view. `hint` is { yaw, pitch, dist, target? } or
// nothing (then the mode's own starting view is used); `back` is the narrow-stage factor; `flatH` is the height of
// the 2D picture that holds the whole object. The camera mode (arcball or fly) is left as it is. The distance is
// held to the user's zoom limits, unless `room` is given: that is the radius of the solid, for the buttons that
// promise the whole solid in the picture (see presetRoom).
function presetFrame(hint, back, flatH, room) {
  if (!hint) { resetCam(); touch(); return; }
  const want = presetDist(hint.dist, back), dist = room ? presetRoom(want, room) : clampDist(want);
  resetCam({ cam: { yaw: hint.yaw, pitch: hint.pitch, dist, target: hint.target || [0, 0, 0] } });
  S.v2.x = 0; S.v2.y = 0; S.v2.h = clamp(flatH, S.v2.hmin, S.v2.hmax);
  touch();
}
// The same for the 3D camera alone, always with room made: what a trap solid example uses.
function presetCam(hint, back, room) {
  resetCam({ cam: { yaw: hint.yaw, pitch: hint.pitch, dist: presetRoom(presetDist(hint.dist, back), room), target: hint.target || [0, 0, 0] } }, '3d');
}
// The starting view of what is on show, `mult` times as far back, with room made for it (see presetRoom). The
// zoom limits are lifted while the camera works out its start, so that the distance comes back unheld.
function presetHome(mult, room) {
  const v = S.view, lim = [v.zmin, v.zmax];
  v.zmin = CAM_LIM.zmin[0]; v.zmax = CAM_LIM.zmax[1];
  resetCam();
  const want = cam.dist * mult;
  v.zmin = lim[0]; v.zmax = lim[1];
  cam.dist = presetRoom(want, room);
}

// ----- Julia points. A key names an entry: 'p3' is the fourth shipped one, 's0' the first saved one.
const juliaEntry = key => (!key ? null : key[0] === 's' ? juliaSaved[+key.slice(1)] : key[0] === 'p' ? JULIA_PRESETS[+key.slice(1)] : null) || null;
const juliaFits = p => !!p && p.c.every((x, i) => presetSame(x, S.c[i]));
// The key of the entry the point c stands on: `prefer` while it still fits (two entries may share a point), else
// the first saved point that fits, else the first shipped one, else 'own'.
function juliaKeyAt(prefer) {
  if (juliaFits(juliaEntry(prefer))) return prefer;
  let i = juliaSaved.findIndex(juliaFits);
  if (i >= 0) return 's' + i;
  i = JULIA_PRESETS.findIndex(juliaFits);
  return i >= 0 ? 'p' + i : 'own';
}
const juliaPresetAt = () => juliaEntry(juliaKeyAt());
function applyJuliaPreset(p) {
  S.c = p.c.slice(0, 3);   // a copy, because the c dials write into S.c in place
  syncControls();
  uiJuliaMark();
  touch();
}
// Distances that replace an entry's own for "Frame it". The Airplane's spine ran out of the picture at its 4.0.
const JULIA_FRAME_DIST = { Airplane: 5.2 };
// Camera only. A saved point, or a point that is in no list, gets the Julia view the page starts with.
function frameJuliaPreset(p) {
  const k = p && p.cam;
  presetFrame(k ? { ...k, dist: JULIA_FRAME_DIST[p.name] || k.dist } : null, presetNarrow(), 3.6);
}
// The two Sphere inversions entries of the Approach list. An entry of the Julia list was found under one of them:
// with one plane (JULIA_ONE), or with two or more (JULIA_TWO, whose Planes dial holds the count).
const JULIA_ONE = 'mercator', JULIA_TWO = 'fold';
// The note of a shipped entry. Some end with advice that only fits the Sphere inversions approach ("Best with one
// plane and about 24 iterations."). An entry no longer sets those dials, so the advice is shown as advice, and
// only while one of those two entries is the one in use.
function juliaNoteFor(p) {
  const m = /^(.*?)\s*Best with ([^.]*)\.$/.exec(p.note || '');
  if (!m) return p.note || '';
  return ap().id === JULIA_ONE || ap().id === JULIA_TWO ? `${m[1]} With this approach it looks best with ${m[2]}.` : m[1];
}
// "As it was found": the planes and the iterations a shipped entry records. The planes name one of the two
// Sphere inversions entries of the Approach list. -> what differs from the page's own now, as
// { entry?, planes?, iter? }, or null when there is nothing to change:
//   entry   the id of the approach to go to, when it is not the one in use
//   planes  the count for the Planes dial of the two-planes entry, when the entry was found with two or more and
//           that entry is not already in use with that count
//   iter    the iterations
// The approach counts only while one of the two Sphere inversions entries is in use: with any other approach in
// use, which of those two the entry was found under changes nothing in the picture.
function juliaFoundDiff(p) {
  if (!p || p.source === 'saved') return null;
  const d = {}, id = ap().id, two = S.param[JULIA_TWO];
  if (p.planes >= 2 && two && (id === JULIA_ONE || id === JULIA_TWO) && !(id === JULIA_TWO && two.planes === p.planes)) {
    d.planes = p.planes;
    if (id !== JULIA_TWO) d.entry = JULIA_TWO;
  } else if (p.planes === 1 && id === JULIA_TWO && S.param[JULIA_ONE]) d.entry = JULIA_ONE;
  if (p.iter > 0 && S.iter !== p.iter) d.iter = p.iter;
  return d.entry === undefined && d.planes === undefined && d.iter === undefined ? null : d;
}
// What the button says it will do, for a result of juliaFoundDiff: the words on it, and the full sentence for
// its tooltip. The words always start with the button's name, "As it was found".
const juliaCount = k => ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'][k] || String(k);
function juliaFoundWords(d) {
  if (!d) return { label: 'As it was found', title: '' };
  const name = id => (APPROACHES.find(a => a.id === id) || {}).name || id;
  const short = [], long = [];
  if (d.planes !== undefined) {
    // With the two-planes entry already in use the click only moves its Planes dial, so the words name the dial:
    // "Planes at 2". Otherwise it changes the entry, and the words name what the entry is called: "two planes".
    short.push(d.entry ? `${juliaCount(d.planes)} planes` : `Planes at ${d.planes}`);
    // (the Planes dial of that entry may stand at another count, so the sentence always names the count)
    long.push(d.entry ? `Chooses the approach ${name(d.entry)}, with Planes at ${d.planes}` : `Sets Planes to ${d.planes}`);
  } else if (d.entry) { short.push('one plane'); long.push(`Chooses the approach ${name(d.entry)}`); }
  if (d.iter !== undefined) { short.push(`${d.iter} iterations`); long.push((long.length ? 'sets' : 'Sets') + ` Iterations to ${d.iter}`); }
  return { label: 'As it was found: ' + short.join(', '), title: long.join(' and ') + ', as when this entry was found. Nothing else changes.' };
}
// Set them, and nothing else: the point c and the camera stay, and so do the dials of every approach except the
// Planes dial named above. -> whether anything changed.
function applyJuliaFound(p) {
  const d = juliaFoundDiff(p);
  if (!d) return false;
  if (d.entry !== undefined) S.approach = APPROACHES.findIndex(a => a.id === d.entry);
  if (d.planes !== undefined) S.param[JULIA_TWO].planes = d.planes;
  if (d.iter !== undefined) S.iter = d.iter;
  syncControls();
  if (d.entry !== undefined) refresh(false); else if (d.planes !== undefined) uiApproachParam(); else touch();
  uiJuliaMark();
  return true;
}

// ----- Kleinian entries
const KLEIN_KEYS = ['mx', 'my', 'mz', 'three', 'L', 'cx', 'cy', 'cz', 'invR'];   // what an entry sets, and all it sets
function kleinFits(p) {
  if (!p) return false;
  return KLEIN_KEYS.every(key => (key === 'three' ? !!S.k.three === !!p.k.three
    : key === 'L' && !p.k.three ? true                // without the third map L does nothing
    : p.k[key] === undefined || presetSame(S.k[key], p.k[key])));
}
function applyKleinPreset(p) {
  KLEIN_KEYS.forEach(key => { if (p.k[key] !== undefined) S.k[key] = p.k[key]; });
  syncControls();
  uiKleinMark();
  touch();
}
// Index of the entry the Kleinian dials stand at (`prefer` first, while it still fits), or -1 when they are the user's own.
function kleinPresetAt(prefer) {
  return kleinFits(KLEIN_PRESETS[prefer]) ? prefer : KLEIN_PRESETS.findIndex(kleinFits);
}
function frameKleinPreset(p) { presetFrame(p && p.cam, presetNarrowK(), 4.5); }
// Wording kept out of the data files: "the family" is explained nowhere on the page.
const kleinNoteFor = p => String(p.note || '').replace(/from the (\S+) cusp into the family/, 'above the $1 cusp');
// What is wrong with the group as the dials stand, in plain words, or ''. The limits are where the testers'
// pictures broke up: none of the shipped entries is inside them.
function kleinTrouble() {
  const k = S.k, out = [];
  if (k.my < 1.45 || Math.hypot(k.my, k.mz) < 1.6) out.push('The walls are so close together that the pearls overlap and the picture breaks up. The known pictures keep the i part of μ between about 1.6 and 2.');
  if (k.three && k.L < 1) out.push('With L below 1 the rows of pearls overlap in depth, which punches holes in them.');
  if (k.cy <= 0 || k.cy >= k.my) out.push('The centre of the turning-out sphere is inside a wall, so the solid fills the picture. Keep centre y between 0 and the i part of μ.');
  else if (kleinSwallowed()) {
    out.push('The turning-out sphere is so large that the solid has grown past the camera, which fills the picture from edge to edge or leaves it black. The solid grows with the square of this radius: twice the radius makes it four times as large. Lower the radius or zoom out.'
      + (kleinReach() > S.view.bound ? ' The solid now also reaches past the Drawing radius in the View section, so from further away only its middle is drawn until that is raised too.' : ''));
  }
  // from further away the same solid is no longer in the camera's way, and that is when the cut shows
  else if (S.mode === 'k' && !S.flat && kleinReach() > S.view.bound) out.push('The solid reaches past the Drawing radius in the View section, so only its middle is drawn. Raise the Drawing radius to see all of it.');
  return out.join(' ');
}
// How far the turned-out solid reaches from the middle of the picture. Turning inside out through a sphere of
// radius R carries a wall at distance d from the sphere's centre onto a ball of diameter R² / d that touches the
// middle of the picture, so the nearer wall gives the reach. (Pearls nearer to the centre than both walls reach
// further still: this is the least the solid reaches.) Infinity while the centre is inside a wall.
function kleinReach() {
  const k = S.k, d = Math.min(k.cy, k.my - k.cy);
  return d > 0 ? k.invR * k.invR / d : Infinity;
}
// True when the camera stands inside that reach, or so close to it that the solid fills the picture. The share
// was measured on the starting group with the starting camera (7 from the middle of the picture): from a reach of
// 4.4 on (radius 2.1) nine probes in ten over the picture hit the solid, at 3.6 (radius 1.9) eight in ten.
// A camera that has come in close on a solid of ordinary size is not this case: the solid must also be too large
// for the distance the Kleinian view starts at.
const KLEIN_NEAR = 0.6, KLEIN_START = 7;
function kleinSwallowed() {
  if (S.mode !== 'k' || S.flat) return false;
  const eye = Math.hypot(...basis().pos);
  return kleinReach() > KLEIN_NEAR * Math.max(eye, KLEIN_START);
}

// ---------- trap solid examples: settings found in testing that give a good object in one click.
// An example sets the kind of picture (for a Julia set also the point c, for a Kleinian picture also the group and
// its turning-out sphere, which is what the starting entry of that list sets), the trap shape, what the trap does,
// its thickness, the skipped steps, its radius, the trap centre (back to the middle, where the pictures were
// chosen), and a camera that shows the object whole. Nothing else: the approach, power, equation, iterations,
// quality and colours stay the user's.
//
// Orbit steps skipped at the start, for the three Mandelbrot examples in the order they stand below. The count
// means the same in every kind of picture (0 keeps the trap shape itself in the solid, 1 leaves it out), so the
// pictures chosen in testing, which needed 2, 2 and 1 while Mandelbrot mode still counted the starting value of
// z as a step, are 1, 1 and 0 here.
const EXAMPLE_SKIP_M = [1, 1, 0];
// trap: the numbers of S.colour.trap (1 cross, 4 planes, 5 sphere shell, 6 ring). solid: 1 the trap is the solid,
// 2 it is added to the solid. cam: as in the lists, chosen on a wide stage at the starting field of view.
// room: the radius the object reaches to, for the drawing radius.
const EXAMPLES = [
  { name: 'Spiky coral', head: 'Mandelbrot', mode: 'm', trap: 1, solid: 1, thick: 0.05, skip: EXAMPLE_SKIP_M[0], radius: 1, cam: { yaw: -1.0, pitch: 0.55, dist: 5.2, target: [-0.6, 0, 0] }, room: 3 },
  { name: 'Discs and arches', head: 'Mandelbrot', mode: 'm', trap: 4, solid: 1, thick: 0.05, skip: EXAMPLE_SKIP_M[1], radius: 1, cam: { yaw: -1.0, pitch: 0.55, dist: 5.2, target: [-0.6, 0, 0] }, room: 3 },
  { name: 'Rings around the set', head: 'Mandelbrot', mode: 'm', trap: 6, solid: 2, thick: 0.05, skip: EXAMPLE_SKIP_M[2], radius: 1, cam: { yaw: -1.0, pitch: 0.55, dist: 5.9, target: [-0.6, 0, 0] }, room: 3 },
  { name: 'Chain of bubbles', head: 'Julia', mode: 'j', c: [-1, 0, 0], trap: 5, solid: 1, thick: 0.05, skip: 1, radius: 0.7, cam: { yaw: -1.9, pitch: 0.55, dist: 4.8 }, room: 3 },
  { name: 'Sea urchins', head: 'Julia', mode: 'j', c: [-1, 0, 0], trap: 1, solid: 1, thick: 0.05, skip: 1, radius: 1, cam: { yaw: -1.9, pitch: 0.55, dist: 4.8 }, room: 3 },
  { name: 'Arches and hoops', head: 'Julia', mode: 'j', c: [-0.122561, 0.744862, 0], trap: 4, solid: 1, thick: 0.05, skip: 1, radius: 1, cam: { yaw: -1.571, pitch: 1.1, dist: 5.3 }, room: 3 },
  { name: 'Pearls and balls', head: 'Kleinian', mode: 'k', trap: 5, solid: 2, thick: 0.05, skip: 1, radius: 1, cam: { yaw: 0.35, pitch: 0.35, dist: 7 }, room: 4 },
  { name: 'Rings in the lace', head: 'Kleinian', mode: 'k', trap: 6, solid: 1, thick: 0.05, skip: 1, radius: 1, cam: { yaw: 0.35, pitch: 0.35, dist: 7 }, room: 4 },
  { name: 'Discs under the set', head: 'Kleinian', mode: 'k', trap: 4, solid: 2, thick: 0.05, skip: 1, radius: 1, cam: { yaw: 0.35, pitch: 0.35, dist: 7 }, room: 4 },
];
const EXAMPLE_KEYS = ['trap', 'solid', 'thick', 'skip', 'radius'];   // the fields of S.colour an example sets
const EXAMPLE_CENTRE = ['tx', 'ty', 'tz'];   // the trap centre: every example puts it back to the middle, where its picture was chosen
// Whether the page stands on an example: everything it sets, except the camera, which is the user's to move.
function exampleFits(e) {
  if (!e || S.mode !== e.mode) return false;
  if (e.c && !e.c.every((x, i) => presetSame(x, S.c[i]))) return false;
  if (e.mode === 'k' && !kleinFits(KLEIN_PRESETS[0])) return false;
  return EXAMPLE_KEYS.every(key => presetSame(S.colour[key], e[key])) && EXAMPLE_CENTRE.every(key => presetSame(S.colour[key], 0));
}
const exampleAt = () => EXAMPLES.findIndex(exampleFits);
function applyExample(e) {
  if (!e) return;
  S.mode = e.mode;
  if (e.c) S.c = e.c.slice(0, 3);
  if (e.mode === 'k') KLEIN_KEYS.forEach(key => { const v = KLEIN_PRESETS[0].k[key]; if (v !== undefined) S.k[key] = v; });
  EXAMPLE_KEYS.forEach(key => { S.colour[key] = e[key]; });
  EXAMPLE_CENTRE.forEach(key => { S.colour[key] = 0; });
  presetCam(e.cam, presetNarrow(), e.room);
  syncControls();
  refresh(false);
}

// ---------- saved Julia points: a name and the point c, nothing else. Kept in localStorage where the page is
// allowed to; where it is not (a locked-down frame), every access throws and the list simply lives until the
// page is closed.
const JULIA_SAVED_KEY = 'squaringLab.juliaPoints.v1', JULIA_SAVED_MOST = 200;
let juliaSaved = [];
function juliaSavedLoad() {
  try {
    const list = JSON.parse(localStorage.getItem(JULIA_SAVED_KEY) || '[]');
    if (!Array.isArray(list)) return;
    const num = x => typeof x === 'number' && isFinite(x);
    // points saved by an earlier build also carry a camera and a plane count: those are dropped here
    juliaSaved = list.filter(p => p && Array.isArray(p.c) && p.c.length === 3 && p.c.every(num)).slice(0, JULIA_SAVED_MOST)
      .map(p => ({ name: String(p.name || 'Saved point').slice(0, 60), note: '', c: p.c.slice(), source: 'saved' }));
  } catch (err) { /* no storage, or something else wrote under this key: start with an empty list */ }
}
// -> true when the list reached storage, false when it will be gone after this visit
function juliaSavedStore() {
  try { localStorage.setItem(JULIA_SAVED_KEY, JSON.stringify(juliaSaved.map(p => ({ name: p.name, c: p.c })))); return true; } catch (err) { return false; }
}
// Save the current Julia point. -> { ok, kept, at, dup }: ok false when the list is full; kept false when storage
// is blocked; at is the index of the entry; dup true when this point was already saved under this name.
function juliaSavePoint(name) {
  const c = S.c.slice(0, 3);
  let label = String(name || '').trim().slice(0, 60) || `c = (${c.map(x => dialFmt(+(+x).toFixed(4))).join(', ')})`;
  const same = juliaSaved.findIndex(p => p.name === label && p.c.every((x, i) => presetSame(x, c[i])));
  if (same >= 0) return { ok: true, kept: juliaSavedStore(), at: same, dup: true };
  if (juliaSaved.length >= JULIA_SAVED_MOST) return { ok: false, kept: false };
  // the same name on another point gets a number, so the two can be told apart in the list
  if (juliaSaved.some(p => p.name === label)) {
    let k = 2;
    while (juliaSaved.some(p => p.name === `${label} (${k})`)) k++;
    label = `${label} (${k})`;
  }
  juliaSaved.push({ name: label, note: '', c, source: 'saved' });
  return { ok: true, kept: juliaSavedStore(), at: juliaSaved.length - 1, dup: false };
}
function juliaDeletePoint(i) {
  if (i < 0 || i >= juliaSaved.length) return false;
  juliaSaved.splice(i, 1);
  juliaSavedStore();
  return true;
}
