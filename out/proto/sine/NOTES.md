# Pillow, "barycentric sines" layout: prototype notes

Approach id `pillow`, first entry of `APPROACHES` in `out/proto/sine/10-approaches.js` (generated from the frozen
`base2` copy by `out/proto/sine/make_approach.py`; nothing in `src/`, `base/`, `base2/`, `docs/`, `tools/` was touched).
Test page: `dist/proto-sine.html`. No dials.

## Verdict in four lines

- The numbers are clean: exact on z = 0, continuous everywhere, round trips at rounding level, shader equals JavaScript to 1e-6.
- Sliced off the plane the solid stays mostly in one piece: the largest piece is 94 to 100 percent of the solid at every
  height tried, with a few small detached islands at height 0.25 and 0.5 in the Mandelbrot solid.
- It does NOT look like Kucera's Figure 4. No row of lemon bodies, no beads. The Mandelbrot solid is a flame-like mass, the
  basilica is one lumpy body with a groove along z = 0.
- The map is creased across z = 0 and stretches unevenly (median stretch ratio 2.0, where 1.0 is ideal). Both come from the
  layout formula itself, not from the lift, so the free choices of this assignment cannot remove them.

## Formulas (as built)

`F_n(v) = |v|^k * Phi(k * PhiInv(v/|v|))`, `k = round(n)` (used for the length too). `k = 1` returns `v`; `|v| < 1e-20` with
`k > 0` returns 0; the length goes through `aprPow` (capped at e^42) like every other approach. If the input has `z == 0`
exactly, the output `z` is set to 0 exactly (see "the snap" below).

Layout of one triangle, weights `lA, lB, lC`, `T = 2*pi/3`, `e` = unit vectors at 0, 120, 240 degrees:

    H = (2/sqrt 3) * (sin(T lA) eA + sin(T lB) eB + sin(T lC) eC)
    lift (equal-area, "Lambert"):  z = q = 1 - |H|^2,   (x, y) = H * sqrt(1 + z)        [then z -> -z for a bottom triangle]

Evaluated from the heaviest corner (cyclic turn so that corner is "A", turn the result back by 120 degrees times its
colour), with `sb = sin(T w1/2)`, `sg = sin(T w2/2)`, `cb = sqrt(1 - sb^2)`, `cg = sqrt(1 - sg^2)` for the other two weights:

    S = sb cg + cb sg,  C = cb cg - sb sg,  D = (2/sqrt 3) sb sg
    Hx = 1 - 2 S (S + D),   Hy = 2 C (sb cg - cb sg),   q = 4 sb sg (4 C^2 cb cg + (2/sqrt 3) S (1 - 2 S^2 - S D))

This is the same H, rewritten so that `q` is a product: it is exactly 0 on an edge and nothing cancels beside one.

Inverse: `q = |d.z|`, `H = d.xy / sqrt(1 + |d.z|)`. Turn H by a multiple of 120 degrees so its angle is within 60 degrees of
A (`|Hy| <= sqrt 3 * Hx`). Then one unknown is left, `p = sin((b + g)/2)` with `b = T w1`, `g = T w2`:

    T0 = (Hy^2 + q) / (1 + Hx)          (= 1 - Hx, without the cancellation)
    f(p) = 2 p^2 + (2/sqrt 3) p (cc - ss) - T0,   ss = sqrt(1 - p^2),  e = Hy^2 / (4 ss^2),  cc = sqrt(1 - e)
    f'(p) = 4 p + (2/sqrt 3) ((cc - ss) + p^2 (1/ss - e/(cc ss^2)))
    start p = sqrt(T0 / 2)   (exact on the equator, at most about 10 percent high elsewhere), Newton, p clamped to [0, 0.8]
    sh = asin(p),  th = asin(clamp(Hy / (2 ss), -p, p)),   w1 = (sh + th)/T,  w2 = (sh - th)/T,  w0 = 1 - w1 - w2

Measured over 100000 random directions: 1 step leaves 4.6e-3, 2 steps 2.1e-5, 3 steps 4.7e-10, 4 steps 3.5e-16 of flat
error. JavaScript takes 4 steps, the shader 3. Flat point: `u = lB (1, 0) + lC (1/2, -+sqrt(3)/2)` as the brief says;
`Phi` locates the small triangle exactly as the brief says.

`mul(a, b)` and `cmap` are the sphere-inversion approach's with one plane (`aprMmul`, copied as `pilMul`). So
`mul(v, v)` is not `sqr(v)` under this approach: a formula such as `c*z*(1 - z)` mixes two rules.

## Checks (out/proto/sine/checks.txt, produced by check.html + checks.js + check.json)

1. Exactness on z = 0, JavaScript rule against the complex power, 500 points per power (300 random, 160 within 1e-1 to 1e-9
   of 0, 120, 180, 240 degrees, 40 with radius 1e-6 to 1e-1). Worst relative error: n=2 1.8e-15, n=3 5.1e-15, n=4 3.7e-15,
   n=5 6.4e-15, n=8 7.1e-15, n=-1 8.2e-16, n=-2 2.0e-15, n=-3 4.0e-15. Without the snap the output's |z| is at most
   5.4e-15 of its length, so the snap hides nothing in double precision.
2. Continuity, 200000 random pairs 1e-5 apart plus 74000 special pairs (across the equator, across the six meridians
   through corners and mid-edges, at the poles, corners and mid-edges). Largest ratio / 99.9th percentile / median:
   n=2 4.02 / 4.01 / 2.22; n=3 9.05 / 9.01 / 3.17; n=-2 4.02 / 4.00 / 2.22. No jump. The largest values are n^2 and sit on
   the equator beside the corner directions (0, 120, 240 degrees).
3. Round trips. Phi(PhiInv(d)) - d over 260000 directions: worst 1.6e-15. PhiInv(Phi(u)) against u over 200000 flat points
   (a quarter within 1e-3 of a lattice point): worst weight difference 4.4e-16, wrong triangle type away from an edge: 0.
4. Shader against JavaScript (float texture, 12800 points per power in five regions). Relative difference, worst:
   n=2 2.1e-6, n=3 3.2e-6, n=4 4.5e-6, n=5 5.5e-6, n=8 7.9e-6, n=-1 1.4e-6, n=-2 2.8e-6, n=-3 3.1e-6 (medians 2e-7 to 1.4e-6).
   On the plane the shader's z is exactly 0 and its x, y are within 1.3e-6 (n=2) to 4.8e-6 (n=8) of the complex power.
   sqr(v) = pw(v, 2) to 7e-6 absolute; pw(v, 1) = v exactly; everything finite at the origin, the axes, the corners and 1e18.
   mul against the sphere-inversion mul differs by up to 3.3e-3 absolute: the two programs hold the same text, the
   difference is that product's own sqrt(1 - Z^2) beside the poles, not something the pillow adds.
   FIRST RUN FAILED THIS CHECK at 2e-4 to 3e-3. Cause, measured in scratch/trig.html on this machine (Intel Arc, ANGLE /
   D3D11): the shader's cos() is good to 3.4e-5 and asin() to 6.7e-5 only, sin() and sqrt() to 1e-7. Fix: the layout uses
   half-angle sines and square roots only, and asin gets one Newton correction (`pilAsin`). Tested on this one GPU only.
5. Distortion of D = Phi o (times 2) o PhiInv, 20000 random directions, singular values divided by 2:
   s1/s2: median 2.03, 95th 4.77, 99.9th 33.4 (largest 129). s1*s2: median 0.92, 95th 1.80, 99.9th 2.02 (5th 0.39, 0.1th 0.07,
   mean 1.00). s1 alone never exceeds 2.01; s2 goes to 0.
   Where: the worst s1/s2 and the smallest s1*s2 sit at the mid-edge directions (60, 180, 300 degrees on the equator, within
   about 4 degrees of latitude). Those are the three points a doubling of the pillow must fold three times round a corner, so
   some loss there is forced; the forced part should be a small neighbourhood, here it is a broad band (mean s1/s2 of 7.8
   in the cell 50-60 degrees from a corner, latitude 0-15). The largest s1*s2 (2.02) sits at the corner directions.
   There is a second bad band at mid latitudes (45-60 degrees, mean s1/s2 3.2 to 3.4). Near the poles it is good (1.25 to 1.3).

## Lifts tried (scratch/lifts.txt; numbers for D at n = 2)

| lift | s1/s2 median / 95th / 99.9th | largest s1 | largest pair ratio at 1e-5 | kept |
|---|---|---|---|---|
| orthographic, z = sqrt(q) | 1.67 / 6.38 / 40.8 | 107 | 269 (grows as the pairs get closer) | no |
| equidistant | 2.14 / 4.86 / 28.3 | 2.04 | 4.08 | no |
| z = k q + (1 - k) q^2, k = 0.5 | 2.27 / 5.71 / 33.4 | 2.58 | 5.15 | no |
| k = 0.75 | 2.16 / 4.92 / 27.9 | 2.09 | 4.16 | no |
| k = 1 (equal-area) | 2.03 / 4.77 / 33.4 | 2.01 | 4.02 | YES |
| k = 1.25 | 1.94 / 5.10 / 33.2 | 2.42 | 4.82 | no |
| k = 1.5 | 1.88 / 5.75 / 35.0 | 3.12 | 6.23 | no |
| k = 2 | 2.21 / 8.14 / 38.3 | 4.91 | 9.69 | no |

Orthographic is out for a reason, not a number: `q` reaches 0 linearly at an edge, so `sqrt(q)` has infinite slope there. On
the equator itself the inverse cancels it, but on every other curve that the power sends onto the equator nothing does, and
the stretch is unbounded. Any blend that keeps a share of it keeps that. Among the smooth lifts the differences are small;
k = 1 has the lowest largest stretch, the best 95th percentile and the cheapest inverse (no power, no trig). No pictures were
made for the rejected lifts. `rejected/gpu-trig/` holds the first picture set, drawn before the cos/asin fix (same lift; the
pictures look the same, its checks.txt shows the failed parity).

## Pictures (all 18 looked at), and the piece counts (pieces.py)

A solid pixel is one within 30 of the 2D view's inside colour (233, 223, 199); 8-connected; pieces under 0.05 percent of the
864x703 picture (304 px) ignored; the stage's own buttons blanked.

Counting on the default-colour pictures does not work: the default palette's pale band outside the solid has the same
colour as the inside, and the count picks those bands up (it gave 10 "pieces" for the flat Mandelbrot set and 28 for the
flat basilica; that file is pieces.txt, kept as a warning). The counts below are from the same six views redrawn with the
plain-silhouette colour mode (S.colour.mode = 6), saved in silhouette/ (silhouette.json, pieces-silhouette.txt).

| slice | height | pieces | largest piece's share of the solid | specks under the floor |
|---|---|---|---|---|
| m2d-z000 | 0 | 1 | 100.00 % | 0 |
| m2d-z010 | 0.1 | 1 | 99.97 % | 7 (21 px) |
| m2d-z025 | 0.25 | 4 (43574 px, then 371, 358, 346) | 94.10 % | 33 (1657 px) |
| m2d-z050 | 0.5 | 3 (14626 px, then 343, 336) | 95.23 % | 9 (53 px) |
| j-bas-2d-z000 | 0 | 1 | 100.00 % | 0 |
| j-bas-2d-z020 | 0.2 | 1 | 100.00 % | 0 |

So the bulk is one piece at every height, but at 0.25 the Mandelbrot solid does shed real islands: two groups of small
detached pieces up and down on the left (silhouette/m2d-z025.png), about 6 percent of the solid's area there. Their edges
are faint in the picture, so their area is undercounted. Only silhouette/m2d-z025.png was looked at among the silhouettes.

What the pictures show, bluntly:
- z = 0 is the flat set in both modes (m2d-z000, j-bas-2d-z000, cut face of m3d-cut0).
- One piece off the plane: yes for the bulk. m2d-z010 is one blob, z025 a dog-bone with small islands beside it, z050 a lens.
- Like Figure 4: no. m3d-default is a mass of flames and fins with no recognisable bulbs. j-bas-3d is ONE lumpy body, not a
  big lemon flanked by smaller ones; j-bas-top shows a pointed lens, not a row of bodies; there are no bead rows anywhere.
- The flat set sits at the bottom of a groove. j-bas-2d-z020 (a fat oval) is much larger than j-bas-2d-z000 (the basilica):
  just off the plane the solid widens. In j-bas-x and m3d-y the plane z = 0 shows as a pinched horizontal line. This is the
  crease, and it is also why the 3D body does not resemble the flat set it contains.
- A second straight ridge runs along the mirror plane y = 0 (j-bas-top, j-bas-x).
- m3d-x: the solid reaches further along z (out of the frame, beyond about 1.2) than along y.
- m3d-n3 has one large smooth concave face (a smeared region); m3d-n8 is a ball of bumps, the most presentable of the set.
- j-rab-3d is a cluster of leaf-like lobes, in one piece, detail in every direction.
- No speckle or noise seen at this zoom, no seams (no jumps).

## Why it is creased and uneven (derivation, not measured separately)

- Crease. Moving off an edge at right angles in the flat triangle also moves H along the circle, at a rate proportional to
  sin(phi)(1 + cos(phi)), phi = angle from the edge's midpoint. The mirror triangle does the same, so a straight flat line
  crossing an edge becomes a V on the sphere. Only the edge's midpoint is free of it. A lift, which changes the height only,
  cannot straighten it. The check that would show it directly (one-sided derivatives across z = 0) was not run.
- Uneven stretch across the plane. Beside an edge `q` grows like `g(theta) * distance`, `g = cos(phi) + cos(2 phi)/2 - 1/4`:
  5/4 at the midpoint, 0 at the corners. So the stretch of D across the equator is `2 g(2 theta)/g(theta)`: 4 at the corner
  directions, 2.9 at 30 degrees, 1.5 at 45, 0 at 60. An even map would have 2 everywhere. Consequence for the pictures: the
  plane z = 0 repels twice as hard as it should near the positive x-axis and not at all near the negative one.

## Speed

Default Mandelbrot picture, 862x701, Balanced, redrawn 8 times per approach in turn in one page (speed.json, speed.log):
pillow median 4.07 s (best 3.18), sphere inversions with its default 2 planes median 2.81 s (best 2.16). Ratio about 1.45.
The GPU was shared; two of the sixteen redraws took 11 and 20 s and are the reason for using medians.

## Not done, not proven

- No second layout version. The first one does not look like Figure 4 and the time went into the checks, the GPU precision
  fault and the pictures. What I would try next is outside this assignment's free choices: add a twist to H that cancels the
  sideways drift at the edges, and make the rate across an edge constant along it.
- "The solid is connected" is a pixel count on six slices, not a proof.
- The approach's page texts (tag, about, crush, smooth, slice) are first drafts. The scorecard ran without errors but I did
  not read what it printed for this approach.
- Other equation presets, the mosaic, negative powers and the Kleinian mode were not drawn with this approach. Only
  z^n + c at n = 2, 3, 8 in Mandelbrot mode and n = 2 in Julia mode.
- Distortion was measured for n = 2 only.
- The cos/asin workaround was tested on one GPU.
- The snap makes "z = 0 stays z = 0" true by construction in the shader. Without it, 32-bit rounding would push plane points
  off by about 1e-6 per step, and near the positive x-axis that error would double or quadruple every step.

## Files

10-approaches.js, make_approach.py, check.html, checks.js, check.json, checks.txt, pictures.json, pictures.log, pieces.py,
pieces.txt (wrong, see above), pieces-silhouette.txt, silhouette.json, silhouette/, speed.json, speed.log, the 18 PNGs, scratch/ (pillow-core.js with every lift, lifts.html, lifts.txt, trig.html),
rejected/gpu-trig/ (first picture set and its checks.txt).
