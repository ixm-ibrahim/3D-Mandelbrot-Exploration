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
  {"name": "Cracked Basilica", "note": "The Basilica pushed a little off the x-axis. With one plane it stays a smooth Basilica. The cracks of the name belong to the earlier version: set Planes to 2 under Sphere inversions.", "c": [-1.0, 0.045, 0.026], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
  {"name": "Thorn crystal", "note": "Just off the x-axis, where the round bulb on the left of the Mandelbrot set ends. Flat blades edged with thorns.", "c": [-1.25, 0.03, 0.02], "source": "explored", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 5.4}},
  {"name": "Split conch", "note": "The San Marco pushed off the x-axis. With one plane it is a smooth conch. The long crack of the name belongs to the earlier version: set Planes to 2 under Sphere inversions.", "c": [-0.75, 0.097, 0.026], "source": "explored", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 4.6}},
  {"name": "Flint", "note": "Inside the Mandelbrot set’s heart-shaped body, a little off the x-axis. With one plane it is a smooth egg with a frilled band. The split stone of the name belongs to the earlier version: set Planes to 2 under Sphere inversions.", "c": [-0.4, 0.13, 0.075], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 4.6}},
  {"name": "Plated egg", "note": "Near the middle of the Mandelbrot set’s heart-shaped body, a little off the x-axis. With one plane it is a smooth egg. The shifted plates of the name belong to the earlier version: set Planes to 2 under Sphere inversions.", "c": [-0.2, 0.13, 0.075], "source": "explored", "planes": 2, "cam": {"yaw": -0.5, "pitch": 0.8, "dist": 4.4}},
  {"name": "Plated ball", "note": "At c = 0 the set is a plain ball, and this is a small step away from it. With one plane it stays a smooth ball. The plates of the name belong to the earlier version: set Planes to 2 under Sphere inversions.", "c": [0.0, 0.087, 0.05], "source": "explored", "planes": 2, "cam": {"yaw": -0.5, "pitch": 0.8, "dist": 4.2}},
  {"name": "Cracked gourd", "note": "The Cauliflower pushed off the x-axis. With one plane it is a smooth gourd with a few dimples. The cracks of the name belong to the earlier version: set Planes to 2 under Sphere inversions.", "c": [0.25, 0.097, 0.026], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
  {"name": "Pitted gourd", "note": "In the dent on the right of the Mandelbrot set, a little off the x-axis. A gourd eaten into pits. There are more of them in the earlier version: set Planes to 2 under Sphere inversions.", "c": [0.35, 0.05, 0.03], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
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
// Move the camera, and the frame of the 2D view, to a recommended view. `hint` is { yaw, pitch, dist, target? } or
// nothing (then the mode's own starting view is used); `back` is the narrow-stage factor; `flatH` is the height of
// the 2D picture that holds the whole object. The camera mode (arcball or fly) is left as it is.
function presetFrame(hint, back, flatH) {
  if (!hint) { resetCam(); touch(); return; }
  resetCam({ cam: { yaw: hint.yaw, pitch: hint.pitch, dist: clampDist(hint.dist * back * 0.32 / S.view.fov), target: hint.target || [0, 0, 0] } });
  S.v2.x = 0; S.v2.y = 0; S.v2.h = clamp(flatH, S.v2.hmin, S.v2.hmax);
  touch();
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
// The note of a shipped entry. Some end with advice that only fits the Sphere inversions approach ("Best with one
// plane and about 24 iterations."). An entry no longer sets those dials, so the advice is shown as advice, and
// only while that approach is the one in use.
function juliaNoteFor(p) {
  const m = /^(.*?)\s*Best with ([^.]*)\.$/.exec(p.note || '');
  if (!m) return p.note || '';
  return ap().id === 'mercator' ? `${m[1]} With this approach it looks best with ${m[2]}.` : m[1];
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
  return out.join(' ');
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
