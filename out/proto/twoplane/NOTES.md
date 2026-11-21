# Pillow prototype, layout "radial from the altitude's midpoint" (twoplane)

Time: started 22:02, written up 22:43. Everything is in `out/proto/twoplane/`. Nothing outside it was edited.

Verdict in one line: the rule is correct and continuous, both planes z = 0 and y = 0 carry the flat set
exactly, the solid mostly stays in one piece when sliced, and the pictures are bad. They are fibrous and
creased all over and look nothing like Figure 4 of the paper. This layout should not be the one that ships.

## Files

| File | What |
|---|---|
| `10-approaches.js` | copy of `base2/js/10-approaches.js` with the approach `pillow` as the first entry, `GL_PILLOW`, `MATH.pillow`, `aprPillowFlat`, `aprPillowDir` |
| `checks.html`, `checks.json`, `checks.txt` | the numeric checks (stand-alone page, loads the modules as classic scripts), how to run them, their output |
| `pics.py` | builds the step lists for `tools/shot.py`: `all` (standard pictures and piece counts), `speed`, `count` (piece counts for the sphere-inversion approach), `extra` |
| `pics.txt`, `speed.txt`, `speed-run1.txt`, `count.txt`, `extra.txt`, `others.txt` | their outputs |
| `others.json` | draws every approach, every equation preset under the pillow, and z^n + c at eleven powers in both modes |
| `*.png` | the standard pictures; `j-bas-y.png` is one more (basilica along the y axis) |
| `extra/` | crease pictures and two Fine-preset pictures (not standard) |

Build and run:

```
python build.py --name proto-twoplane --base base2 --swap js/10-approaches.js=out/proto/twoplane/10-approaches.js
python notes/approaches_run.py out/proto/twoplane/checks.html out/proto/twoplane/checks.txt --actions out/proto/twoplane/checks.json
python out/proto/twoplane/pics.py all        (also: speed, count, extra)
```

## The rule, exactly

`F_n(v) = |v|^k · Φ(k · Φ⁻¹(v/|v|))`, `k = floor(n + 1/2)`. `F(0) = 0` for k > 0. Lengths are capped at e^42 as in
the other approaches; the origin under a negative power goes to (e^42, 0, 0).

A flat position is kept in lattice coordinates (a, b), meaning the point a·(1, 0) + b·(−1/2, √3/2). Scaling by k
is the same in either coordinate system, and staying in lattice coordinates avoids a multiply and a divide by √3/2.
T = 2π/3.

Φ⁻¹(d), d a unit direction:
```
s = atan2(hypot(d.x, d.y), |d.z|) / (π/2)            share of the way from the pole (O) to the equator
t = atan2(d.y, d.x) / T;  if t < 0: t += 3           equator position in thirds: 0 at A, 1 at B, 2 at C
k3 = min(floor(t), 2);  f = t − k3
(qB, qC) = (f, 0) if k3 = 0;  (1 − f, f) if k3 = 1;  (0, 1 − f) if k3 = 2      where the ray from O ends
lB = 1/4 + s·(qB − 1/4);  lC = 1/4 + s·(qC − 1/4)                             (lA = 1 − lB − lC)
(a, b) = (lB, −lC) if d.z >= 0, else (lB + lC, lC)
```
Φ(a, b):
```
i = floor(a), j = floor(b), fa = a − i, fb = b − j
w0 = 1 − max(fa, fb);  w1 = |fa − fb|;  w2 = min(fa, fb);  c0 = (i + j) mod 3   (0, 1 or 2)
(lA, lB, lC) = (w0, w1, w2) if c0 = 0;  (w2, w0, w1) if c0 = 1;  (w1, w2, w0) if c0 = 2
σ = −1 if fa >= fb (triangle points up: lower half sphere), else +1
m = min(2·lA, 4·lB, 4·lC);  s = 1 − m;  if s is 0: return (0, 0, σ)
t = 1/4 + (lB − 1/4)/s   if 4·lC is the least     (the ray leaves through edge AB)
t = 5/4 + (lC − 1/4)/s   else if 2·lA is the least (edge BC)
t = 5/2 + (lA − 1/2)/s   otherwise                 (edge CA)
φ = T·t;  e = (π/2)·m;  return (cos e · cos φ, cos e · sin φ, σ · sin e)
```
(`m` is the share of the way from the equator to the pole, so `θ = (π/2)(1 − m)` is the linear polar angle the
assignment asks for; writing it with `m` keeps a point with a zero weight exactly on the equator.)

Two things added to make it work, neither a change of the rule:
- Exactly on z = 0 (`v.z == 0`) the complex power is taken directly, in JavaScript and in the shader. It is the
  same value (check 1 compares the two paths), and it stops round-off from lifting an orbit off the plane. The
  rule expands everywhere, so an error of 1e-7 off the plane grows up to about fourfold per step in the shader.
- `sqr` multiplies by `|v|²` instead of `exp(2 log |v|)`.

`mul(a, b)` for two different points, `cmap`, `aprDiv`, `aprSPow`: copied from the sphere-inversion approach
(`aprMmul` without folds; `cmap` is the identity). The approach text says so. No parameters, no dials.

## Checks (all in `checks.txt`)

1. Exactness, worst relative error over 500 points with z = 0 (300 random, 120 beside or on the angles 0°, 120°,
   180°, 240°, 80 with radius 1e-5 to 1e-2). "General path" is Φ(k·Φ⁻¹(d)) without the shortcut.

   | n | z = 0, general path | z = 0, MATH.pillow | 1e-13·r off the plane | plane y = 0 |
   |---|---|---|---|---|
   | 2 | 2.1e-15 | 1.7e-15 | 4.5e-13 | 1.8e-15 |
   | 3 | 4.2e-15 | 4.4e-15 | 8.2e-13 | 4.5e-15 |
   | 4 | 4.0e-15 | 3.4e-15 | 9.6e-13 | 3.5e-15 |
   | 5 | 4.5e-15 | 6.7e-15 | 1.3e-12 | 6.9e-15 |
   | 8 | 6.9e-15 | 7.0e-15 | 2.2e-12 | 7.0e-15 |
   | −1 | 1.3e-15 | 9.4e-16 | 1.0e-13 | 1.2e-15 |
   | −2 | 1.4e-15 | 1.7e-15 | 4.5e-13 | 1.8e-15 |
   | −3 | 3.6e-15 | 4.4e-15 | 8.2e-13 | 4.7e-15 |

   The plane y = 0 holds too: F(x, 0, z) is the complex power of x + iz, to the same 1e-15. That was the point
   of this layout and it is true.
2. Continuity, |F(d1) − F(d2)| / |d1 − d2| over 200000 random pairs 1e-5 apart, plus 14000 pairs that straddle the
   equator, the six meridians at multiples of 60°, the poles and the corner directions (some with one point
   exactly on the special place). No jump anywhere.

   | n | max | 99.9th percentile | median | worst straddling pair |
   |---|---|---|---|---|
   | 2 | 11.56 | 9.63 | 2.24 | 10.0 (corner meridian) |
   | 3 | 15.78 | 12.49 | 3.67 | 13.75 (corner meridian) |
   | −2 | 11.44 | 9.61 | 2.23 | 10.0 (corner meridian) |

   Bounded, but large: a conformal rule would give 2 and 3.
3. Round trip: Φ(Φ⁻¹(d)) = d to 2.0e-15 over 50000 directions. Φ⁻¹(Φ(u)) has the same triangle type and weights as u
   to 1.3e-15 over 50000 flat points in [−6, 6]², 0 type mismatches (the weights of u were worked out a second way,
   by plain geometry, not with the code under test).
4. Shader against JavaScript (float32 against float64), 1536 points per power, including points on and beside
   both planes, the corner meridians, the poles and the corner directions. Worst relative difference:
   n = 2: 7.5e-5, 3: 1.0e-4, 4: 2.0e-4, 5: 2.4e-4, 8: 4.2e-4, −1: 3.7e-5, −2: 7.5e-5, −3: 8.7e-5 (means about 1e-5).
   `sqr` against the power 2: 7.5e-5. `mul` against the sphere-inversion product: 1.5e-4. n = 2.4 and 2.6 round to
   2 and 3 in both. All finite at the origin, on the axes, at the corners and at 1e18 (largest component 1.74e18).
   For scale: the existing approaches were accepted at 2.4e-4 with a limit of 2e-3.
5. Distortion of D = Φ ∘ (×2) ∘ Φ⁻¹, 20000 random directions, singular values divided by 2:

   | | median | 95th | 99.9th | max |
   |---|---|---|---|---|
   | s1/s2 | 3.19 | 14.3 | 26.9 | 33.6 |
   | s1·s2 | 0.84 | 2.34 | 2.60 | 2.60 (min 0.32, mean 0.993) |

   Largest s1 5.7, smallest s2 0.165. Where: 72% of the worst 1% of s1/s2 lie within 15° of longitude of the
   meridians of B and C (on the side facing A, longitudes about ±108° to ±120°), at latitudes 43° to 66° either
   side of the equator, median 58°. None of the worst 1% is within 15° of A, B, C, the mid-edge directions or
   the poles. The largest area stretch (2.6) is at longitude ±150°, latitude ±17°; the smallest (0.32) beside the
   poles on the meridians at ±60°. For n = 3: s1/s2 median 3.8, 95th 11.1, 99.9th 21.6, max 26.7.
   The app's own scorecard agrees: "Roundness 34%, stretch from 0.36× to 11.5×".

   Why it is this bad: O is off-centre, so the rays to B and C are long (0.66 against 0.43 to A and 0.22 to the
   nearest edge point) and meet the edge AB at 19°. Measured against the angle at O, the layout alone already
   stretches longitude 4.2× there and 0.45× at the point of AB nearest to O, and the rule applies the layout
   twice (once inverted).

Also run: `others.json`: every approach draws at its defaults, every equation preset and z^n + c at n = −8 … 10 in
both modes draw under the pillow, 36 of 36, no console or shader errors.

## Pictures (1400x950 window, Balanced, default colours, 14 iterations)

Piece counts were done on a mask recomputed in double precision with `MATH.pillow` at the pixel centres of the
picture's own 862x701 grid (8-connected, pieces of at least 303 px = 0.05% of the picture), not on the PNG, because
the PNG has the stage controls drawn over it.

| Picture | slice | pieces | largest piece | specks |
|---|---|---|---|---|
| `m2d-z000.png` | Mandelbrot z = 0 | 1 | 100.00% | 4 (0.00%) |
| `m2d-z010.png` | z = 0.1 | 1 | 97.40% | 222 (2.60%) |
| `m2d-z025.png` | z = 0.25 | 3 | 94.80% (then 2.26%, 2.26%) | 31 (0.68%) |
| `m2d-z050.png` | z = 0.5 | 1 | 97.38% | 62 (2.62%) |
| `j-bas-2d-z000.png` | basilica z = 0 | 1 | 100.00% | 0 |
| `j-bas-2d-z020.png` | z = 0.2 | 1 | 99.73% | 94 (0.27%) |

For comparison, the same count for the sphere-inversion approach (`count.txt`): Mandelbrot with 2 planes: 1 piece
at z = 0, 0.1, 0.25 (99.8% or more), nothing left at z = 0.5 (118 px); basilica at z = 0.2: 3 pieces with 2 planes
(82.9%, 8.6%, 8.6%) and 3 with 1 plane (76.3%, 11.9%, 11.9%). So by this count the pillow slices are not more
connected for the Mandelbrot set, and they shed far more specks. The pillow solid is taller: it still fills
3.3% of the picture at z = 0.5.

Speed, default picture, timed from `touch()` to idle, turn about in one session (`speed.txt`, `speed-run1.txt`):
pillow 1.07 to 6.08 s (10 runs, median 2.2 s), sphere inversions with 2 planes 0.96 to 6.81 s (10 runs, median
2.2 s). Ratio of medians 1.0; ratio of the fastest runs 1.07 / 0.96 = 1.1. The GPU was shared, and the spread
within one approach (6×) is far larger than any difference between them.

## Honest opinion of the pictures

- One piece off the plane: mostly. Every standard slice has one dominant piece (94.8% to 100%). The slice at
  z = 0.25 has two more real pieces, and every slice off the plane is ringed with specks and frayed edges
  (`m2d-z010.png` left half, `m2d-z050.png`).
- Detail in every direction like Figure 4: no. There are no round bodies and no beads. The basilica
  (`j-bas-3d.png`, `j-bas-top.png`) is three pointed, ridged bodies along the x axis, closer to stacked pyramids
  than to lemons; its outline along x (`j-bas-x.png`) is a diamond. The Mandelbrot solid (`m3d-default.png`) is a
  lump of feathered sheets. The detail that is there is striation along the creases, the same in every picture.
- Creases: everywhere, not only near B and C. `extra/j-c02-fromB.png` and `extra/j-c02-fromA.png` (Julia set for
  c = (0.2, 0, 0), nearly a ball) show them best: a ridge round the equator, a ridge along y = 0, and nested
  chevrons over the whole surface. They come from the three half-planes through the corner meridians and from
  every surface the power lays onto one of them (4 times as many after one squaring, 16 after two).
- Two planes: visible. The views along x (`m3d-x.png`, `j-bas-x.png`) are mirror-symmetric in both y and z, with a
  ridge on each plane. That is the one thing this layout delivers.
- Speckle: a dusty fringe on every thin edge at Balanced (`j-bas-3d.png`, `j-bas-top.png`, `j-rab-3d.png`). The
  Fine preset (`extra/j-bas-3d-fine.png`, `extra/m3d-default-fine.png`) thins the dust but the surfaces stay
  fibrous, so most of it belongs to the solid. I did not separate the two causes further.
- Smeared regions: long parallel fibres where the stretch is most one-sided, e.g. the left flank of
  `m3d-default.png` and the columns of the rabbit (`j-rab-3d.png`).
- Powers 3 and 8 (`m3d-n3.png`, `m3d-n8.png`): the same character, creased petals; n = 8 is a tidier ball of
  scales because the cells are smaller.

## Tried and dropped

Nothing in the layout: the assignment leaves no free choice, so there are no rejected versions and no subfolder
of them. Looked at and left out: a second shortcut for points exactly on y = 0 (the plane is exact in exact
arithmetic and nothing draws a y = 0 slice); a form without trigonometry (constant speed along the edges and a
linear polar angle are angles by definition: two inverse and four direct trig calls per power).

## Problems and loose ends

- The crease analysis predicts that across the plane y = 0 the creases cancel only on parts of the great circle
  (for n = 2 they remain between 45° and 90°, 135° and 225°, 270° and 315° of the angle in the x–z plane). I did
  not check that numerically.
- Continuity is tested, not proven, and only for n = 2, 3, −2.
- In the shader the plane y = 0 has no protection against round-off; only z = 0 does.
- A fractional power is rounded, so the picture jumps when the dial passes a half. The texts say so.
- Formulas with a product of two points (the lambda preset, c/z) use the sphere-inversion product: such pictures
  are a mix of two rules.
- With the pillow first in the list, "Reset this section" under Approach selects the pillow, and
  `tools/smoke.json` would fail its "first approach is Sphere inversions" step. The Julia presets' plane hints
  still go to the sphere-inversion approach only.
- Only 14 iterations were looked at. `tools/smoke.json` and `tests/approaches-page.json` were not run.
