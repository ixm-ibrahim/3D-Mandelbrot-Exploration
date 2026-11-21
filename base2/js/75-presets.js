// ---------- preset lists (Julia points, Kleinian groups) and the user's own saved Julia points.
// The build does not load JSON, so the two arrays below are copies of data/julia-presets.json and
// data/klein-presets.json. notes/ui_embed.py writes them between the marker lines: change the JSON
// and run that script, do not edit the arrays here.
// <julia-data>
const JULIA_PRESETS = [
  {"name": "Basilica", "note": "c = −1, the centre of the period-two disc. The figure in Kučera’s paper.", "c": [-1.0, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.9, "pitch": 0.55, "dist": 4.8}},
  {"name": "San Marco", "note": "c = −3/4, where the period-two disc meets the main cardioid. A fatter Basilica.", "c": [-0.75, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.9, "pitch": 0.55, "dist": 4.8}},
  {"name": "Douady rabbit", "note": "The centre of the period-three bulb. Three lobes meet at every pinch. Best with one plane and about 24 iterations.", "c": [-0.122561, 0.744862, 0.0], "source": "computed", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.6}},
  {"name": "Airplane", "note": "The period-three centre on the real axis, near −1.755. A thin spine strung with spiked stars.", "c": [-1.754878, 0.0, 0.0], "source": "computed", "planes": 2, "cam": {"yaw": -0.5, "pitch": 0.3, "dist": 4.0}},
  {"name": "Cauliflower", "note": "c = 1/4, the cusp of the main cardioid. In 3D it is a dimpled gourd.", "c": [0.25, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 5.0}},
  {"name": "Siegel disc", "note": "On the edge of the main cardioid, turning by the golden mean. Best with one plane.", "c": [-0.390541, -0.586788, 0.0], "source": "computed", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.8}},
  {"name": "Dendrite", "note": "c = i. The flat set has no inside, so the solid is a thin branching coral. Best with one plane.", "c": [0.0, 1.0, 0.0], "source": "classic", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.15, "dist": 4.4}},
  {"name": "Kokopelli", "note": "The centre of the period-four island above the rabbit’s bulb. A beaded coral. Best with one plane.", "c": [-0.15652, 1.032247, 0.0], "source": "computed", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.15, "dist": 4.6}},
  {"name": "Fat rabbit", "note": "The root of the rabbit’s bulb, where it joins the main cardioid. Best with one plane.", "c": [-0.125, 0.649519, 0.0], "source": "computed", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.8}},
  {"name": "Feigenbaum point", "note": "Near −1.4012, where the period doublings on the real axis pile up. A spiny rod.", "c": [-1.401155, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.2}},
  {"name": "Golden ratio", "note": "c = 1 − φ, about −0.618, inside the main cardioid. A knobbly shell.", "c": [-0.618034, 0.0, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.9, "pitch": 0.55, "dist": 4.6}},
  {"name": "−0.8 + 0.156i", "note": "Just outside the Mandelbrot set, beside the period-two disc. Best with one plane and about 24 iterations.", "c": [-0.8, 0.156, 0.0], "source": "classic", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.05, "dist": 4.8}},
  {"name": "0.285 + 0.01i", "note": "Just outside the cusp of the main cardioid. In 3D it is nearly the cauliflower’s gourd.", "c": [0.285, 0.01, 0.0], "source": "classic", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 5.0}},
  {"name": "−0.4 + 0.6i", "note": "Just outside the main cardioid. Best with one plane.", "c": [-0.4, 0.6, 0.0], "source": "classic", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.6}},
  {"name": "−0.70176 − 0.3842i", "note": "Outside the Mandelbrot set. Clusters of buds on a chain. Best with one plane and about 24 iterations.", "c": [-0.70176, -0.3842, 0.0], "source": "classic", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.05, "dist": 4.8}},
  {"name": "−0.835 − 0.2321i", "note": "Outside the Mandelbrot set, below the period-two disc. Curled ribbons. Best with one plane and about 24 iterations.", "c": [-0.835, -0.2321, 0.0], "source": "classic", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.05, "dist": 4.8}},
  {"name": "−0.7269 + 0.1889i", "note": "Barely outside the Mandelbrot set, in the valley between its two largest parts. Best with one plane.", "c": [-0.7269, 0.1889, 0.0], "source": "classic", "planes": 1, "cam": {"yaw": -1.571, "pitch": 1.05, "dist": 4.8}},
  {"name": "0.45 + 0.1428i", "note": "Well outside the Mandelbrot set. The solid breaks into rings of islands. Best with one plane and about 24 iterations.", "c": [0.45, 0.1428, 0.0], "source": "classic", "planes": 1, "iter": 24, "cam": {"yaw": -1.571, "pitch": 1.1, "dist": 4.6}},
  {"name": "Cracked Basilica", "note": "The Basilica pushed a little off the x-axis. The fold between the two planes cracks it into blocks.", "c": [-1.0, 0.045, 0.026], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
  {"name": "Thorn crystal", "note": "Just off the real axis where the period-two disc ends. Flat blades edged with thorns.", "c": [-1.25, 0.03, 0.02], "source": "explored", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 5.0}},
  {"name": "Split conch", "note": "The San Marco pushed off the x-axis. One long crack runs through the shell.", "c": [-0.75, 0.097, 0.026], "source": "explored", "planes": 2, "cam": {"yaw": -1.25, "pitch": 1.0, "dist": 4.6}},
  {"name": "Flint", "note": "Off both planes, a little above the main cardioid. A split stone with flat faces.", "c": [-0.4, 0.13, 0.075], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 4.6}},
  {"name": "Plated egg", "note": "Off both planes, above the middle of the main cardioid. An egg of shifted plates.", "c": [-0.2, 0.13, 0.075], "source": "explored", "planes": 2, "cam": {"yaw": -0.5, "pitch": 0.8, "dist": 4.4}},
  {"name": "Plated ball", "note": "At c = 0 the set is a plain ball. A small step off both planes slides its shell apart.", "c": [0.0, 0.087, 0.05], "source": "explored", "planes": 2, "cam": {"yaw": -0.5, "pitch": 0.8, "dist": 4.2}},
  {"name": "Cracked gourd", "note": "The cauliflower pushed off the x-axis. The gourd splits along its seams.", "c": [0.25, 0.097, 0.026], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
  {"name": "Pitted gourd", "note": "Off both planes, past the cusp of the main cardioid. The gourd is eaten into pits.", "c": [0.35, 0.05, 0.03], "source": "explored", "planes": 2, "cam": {"yaw": -0.9, "pitch": 0.4, "dist": 5.0}},
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

// Preset cameras were chosen on a wide stage. On a tall, narrow one the camera backs off by this factor
// so that wide sets are not cut off at the sides.
const presetNarrow = () => Math.max(1, 1.2 * stage.clientHeight / Math.max(1, stage.clientWidth));
const presetSame = (a, b) => Math.abs(a - b) < 1e-9;

// Jump to a Julia point: a shipped preset or one of the user's saved points.
function applyJuliaPreset(p) {
  S.c = p.c.slice(0, 3);   // a copy, because the c dials write into S.c in place
  // a point off the x-axis is torn by two planes, so each preset carries the plane count it was checked with
  if (p.planes && S.param.mercator) S.param.mercator.planes = p.planes;
  if (p.iter && S.iter < p.iter) S.iter = p.iter;   // a floor: some sets only show their shape from about 24 steps
  const own = p.source === 'saved';
  if (p.cam && !(own && S.flat)) {
    S.view.fly = false;   // the preset cameras turn around the origin
    resetCam({ cam: { yaw: p.cam.yaw, pitch: p.cam.pitch, dist: clampDist(p.cam.dist * (own ? 1 : presetNarrow())), target: p.cam.target || [0, 0, 0] } });
    if (!own) { S.v2.x = 0; S.v2.y = 0; S.v2.h = clamp(3.6, S.v2.hmin, S.v2.hmax); }   // the 2D view: every preset fits in this height
  }
  syncControls();
  refresh(false);   // not just touch(): the plane count is part of the approach's formula text
}
const juliaPresetAt = () => [...JULIA_PRESETS, ...juliaSaved].find(p => p.c.every((x, i) => presetSame(x, S.c[i]))) || null;

// Jump to a Kleinian preset. The cameras were framed for a field of view of 0.32.
function applyKleinPreset(p) {
  Object.assign(S.k, p.k);
  S.view.fly = false;
  resetCam({ cam: { yaw: p.cam.yaw, pitch: p.cam.pitch, dist: clampDist(p.cam.dist * 0.32 / S.view.fov), target: [0, 0, 0] } });
  S.v2.x = 0; S.v2.y = 0; S.v2.h = clamp(4.5, S.v2.hmin, S.v2.hmax);
  syncControls();
  touch();
}
// Index of the preset the Kleinian dials now stand at, or -1 when they have been moved off every preset.
const kleinPresetAt = () => KLEIN_PRESETS.findIndex(p => Object.keys(p.k).every(key => (key === 'three' ? !!S.k.three === !!p.k.three : presetSame(S.k[key], p.k[key]))));

// ---------- saved Julia points. Kept in localStorage where the page is allowed to; where it is not
// (a locked-down frame), every access throws and the list simply lives until the page is closed.
const JULIA_SAVED_KEY = 'squaringLab.juliaPoints.v1', JULIA_SAVED_MOST = 200;
let juliaSaved = [];
function juliaSavedLoad() {
  try {
    const list = JSON.parse(localStorage.getItem(JULIA_SAVED_KEY) || '[]');
    if (!Array.isArray(list)) return;
    const num = x => typeof x === 'number' && isFinite(x);
    juliaSaved = list.filter(p => p && Array.isArray(p.c) && p.c.length === 3 && p.c.every(num)).slice(0, JULIA_SAVED_MOST).map(p => {
      const out = { name: String(p.name || 'Saved point').slice(0, 60), note: '', c: p.c.slice(), source: 'saved' };
      if (num(p.planes)) out.planes = clamp(Math.round(p.planes), 1, 8);
      const k = p.cam;
      if (k && num(k.yaw) && num(k.pitch) && num(k.dist) && k.dist > 0) {
        out.cam = { yaw: k.yaw, pitch: k.pitch, dist: k.dist };
        if (Array.isArray(k.target) && k.target.length === 3 && k.target.every(num)) out.cam.target = k.target.slice();
      }
      return out;
    });
  } catch (err) { /* no storage, or something else wrote under this key: start with an empty list */ }
}
// -> true when the list reached storage, false when it will be gone after this visit
function juliaSavedStore() {
  try { localStorage.setItem(JULIA_SAVED_KEY, JSON.stringify(juliaSaved)); return true; } catch (err) { return false; }
}
// Save the current Julia point with the current camera. -> { ok, kept }: ok false when the list is full.
function juliaSavePoint(name) {
  if (juliaSaved.length >= JULIA_SAVED_MOST) return { ok: false, kept: false };
  const c = S.c.slice(0, 3), label = String(name || '').trim().slice(0, 60) || `c = (${c.map(x => dialFmt(+(+x).toFixed(4))).join(', ')})`;
  const p = { name: label, note: '', c, source: 'saved', cam: { yaw: cam.yaw, pitch: cam.pitch, dist: cam.dist, target: cam.target.slice() } };
  if (S.param.mercator) p.planes = S.param.mercator.planes;
  juliaSaved.push(p);
  return { ok: true, kept: juliaSavedStore() };
}
function juliaDeletePoint(i) {
  if (i < 0 || i >= juliaSaved.length) return false;
  juliaSaved.splice(i, 1);
  juliaSavedStore();
  return true;
}
