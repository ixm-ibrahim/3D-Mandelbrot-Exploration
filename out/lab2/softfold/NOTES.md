# Soft fold: prototype notes

Everything is in `out/lab2/softfold/`. Test page: `dist/lab2-softfold.html` (base4 with `10-approaches.js` swapped).
Nothing outside this folder and `dist/lab2-softfold.html` was written.

## Verdict first

**The soft fold does what was asked numerically and fails visually.** It is exact on every plane, has no jump
at power 2, and the shader matches the JavaScript. But the Julia set for c = -1 is **not** a row of bodies
with beads. It is one bloated, billowing mass with X-shaped ridges where the planes cross: seen along the
x-axis it fills a rounded square about 1.7 across, where the folded picture has two crossing discs with beads. The rabbit and the
Mandelbrot solid are masses of shards and flames, as in the pillow round. No setting of the two dials, of the
curve, or of the blend path gives the Figure 4 look. Raising the blend dial toward 0.45 does not approach the
folded picture: the solid turns to dust first.

There is a reason, and it is not a matter of tuning (section "Why it cannot work").

## The rule (as built, id `softfold`)

Parameters: `planes` p (1 to 4, starts at 2), `blend` a (0 to 0.45, typed up to 0.49, starts at 0.25),
`curve` (0 smoothstep, 1 smootherstep), `mix` (0 great circle, 1 straight line renormalised, 2 pinch, see below).
The shader reads them as `uA = (p, a, curve, mix)`.

- M(d), the one-plane direction rule for a unit direction d: longitude φ = atan2(y, x) times n, Mercator latitude
  m = atanh(z) times n (z clamped to ±0.999999, n·m to ±20), result (cos nφ / cosh nm, sin nφ / cosh nm, tanh nm).
  For n = 2 the same thing without angles: (x² − y², 2xy, 2z) / (1 + z²).
- F(v) = |v|ⁿ · D(v/|v|) (length through the lab's capped `aprPow`). (0, 0, 0) for |v| < 1e-20 and n > 0.
- p = 1: D = M.
- p ≥ 2, with d = v/|v|:
  1. If z < 0, or z = 0 and y < 0, replace d by (x, −y, −z) and undo that on the result (the half turn about
     the x-axis commutes with the rule).
  2. If z = 0 exactly, or √(y² + z²) ≤ 1e-15 (on the x-axis, where all planes agree): D = M(d).
  3. Otherwise ρ = √(y² + z²), w = π/p, u = atan2(z, y)/w, j = min(floor(u), p − 1), t = u − j.
     Weight s = S(clamp((t − a)/(1 − 2a), 0, 1)), S(q) = q²(3 − 2q) or q³(q(6q − 15) + 10).
     A = M(x, ρ cos tw, ρ sin tw) (plane j's answer, in plane j's frame).
     B = M(x, ρ cos((t − 1)w), ρ sin((t − 1)w)) turned by +w about the x-axis (plane j + 1's answer, same frame).
     A is skipped when s = 1, B when s = 0.
  4. Blend. mix 0: with c = A·B, e = B − cA: if c < 0 and |e| < 1e-3 (opposite answers) take A when s < 0.5,
     else B; otherwise D = cos(θ)A + sin(θ)e/|e| with θ = s·atan2(|e|, c). mix 1: normalise((1 − s)A + sB), same
     fallback when its length is under 1e-3.
  5. Turn D about the x-axis by j·w (cos jw = (y cos tw + z sin tw)/ρ, sin jw = (z cos tw − y sin tw)/ρ).
- `sqr(v)` is `pw(v, 2)`. `mul(a, b)` is copied unchanged from Sphere inversions with one plane (`aprMmul`).
  `cmap(c) = c`: the constant is not folded.
- mix 2, "pinch" (my addition, see below): only the nearer plane answers (A for t < 0.5, B otherwise), and it is
  pulled along a great circle toward a target T by τ = S(clamp((min(t, 1 − t) − a)/(0.5 − a), 0, 1)).
  T = (1, 0, 0) for an even power; for an odd power T = (x, g·ρ cos σ, g·ρ sin σ) with σ the seam's angle in the
  frame and g the sign of n.

## Numeric checks (`checks.txt`, made by `run_checks.py` from `checks.js`; pinch settings also in `checks-pinch.txt`)

1. **Exactness: pass.** 500 points per plane, on and beside the axes, down to |v| = 1e-5. Worst |F − zⁿ|/|zⁿ|
   over all planes: n=2 1.7e-15, n=3 3.9e-15, n=4 3.4e-15, n=5 7.7e-15, n=8 6.6e-15, n=−1 1.0e-15, n=−2 1.7e-15,
   n=−3 4.0e-15. Same for p = 2, 3, 4 and every a, curve and mix tried. planes = 1 against Sphere inversions
   with one plane: 3.7e-15.
2. **Continuity: pass at n = 2 and −2 everywhere tried; one real tear found at n = 3.** 200000 random pairs
   1e-5 apart plus 10000 to 20000 straddling the planes, as many straddling the half-way seams, the band edges,
   20000 near the x-axis, 18000 around the spots where the two plane answers are opposite.
   Largest |F(d1) − F(d2)|/|d1 − d2| (99.9th percentile of the random pairs in brackets):

   | setting | n = 2 | n = 3 | n = −2 |
   |---|---|---|---|
   | p=2 a=0.25 smoothstep, great circle (default) | 8.27 (7.99) | 4.14 (4.06) | 8.27 (7.99) |
   | p=2 a=0 | 5.66 (5.47) | 3.57 (3.54) | 5.66 (5.47) |
   | p=2 a=0.45 | 38.2 (34.6) | 18.3 (16.9) | 38.2 (34.7) |
   | p=2 a=0.25 smootherstep | 10.05 (9.69) | 5.03 (4.88) | 10.05 (9.66) |
   | p=2 a=0.25 straight | 22.6 (17.8) | 5.69 (5.40) | 22.6 (18.1) |
   | p=2 a=0 straight | 11.9 (10.2) | 3.15 (3.09) | 11.9 (10.4) |
   | p=3 a=0.25 | 8.92 (8.61) | 9.46 (9.20) | 8.92 (8.61) |
   | p=3 a=0 | 5.35 (5.06) | **73375 JUMP** (18.2) | 5.35 (5.06) |
   | p=4 a=0.25 | 9.38 (8.83) | 9.56 (8.99) | 9.38 (8.86) |
   | pinch p=2 a=0.25 / a=0 / a=0.4 | 8.90 / 5.83 / 19.6 | 8.29 / 5.15 / 19.1 | 8.89 / 5.83 / 19.6 |
   | pinch p=3 a=0.25 | 14.7 | 11.9 | 14.7 |

   The jump: wherever the two plane answers point exactly opposite ways and the weight is strictly between 0 and
   1, a blend has no answer and the direction is torn at that single ray. Table 2b in `checks.txt` lists those
   spots. For p = 2 they lie on the planes themselves (weight 0 or 1) for every power tried, so p = 2 has no
   tear. For p = 3 they sit at t = 0.220 (n = 3), 0.153 (n = 4), 0.133 (n = 5), 0.078 and 0.116 (n = 8); for
   p = 4 at t = 0.422 (n = 5) and 0.172 (n = 8). They are harmless only when a is larger than that t, so p = 4
   at n = 5 is torn at every a up to 0.42. The rule also agrees with a second copy written straight from the
   task text (R_k M R_k⁻¹, textbook slerp) to 8e-8 or better.
3. **GLSL against JavaScript: pass.** 20480 values per setting (8 powers; points in z = 0, y = 0, the other
   planes, the seams, beside z = 0). |glsl − js|/(1 + |js|): median 8e-6 to 1e-5, 99.9th 1.1e-4 to 2.2e-4, worst
   1.7e-4 to 7.0e-4, none over 2e-3. `sqr` against the JavaScript square 5e-5 to 2.5e-4, `mul` against the Sphere
   inversions shader 1e-6 to 1.3e-5, `cmap(c) − c` = 0. A point of z = 0 returns z = 0 exactly. Finite at the
   origin, on the axes and at 1e18. (A first version returned NaN for v = (−2, 0, 1e-30): `length(d.yz)`
   underflowed to 0. Fixed by the 1e-15 test in step 2.)
4. **Distortion at n = 2: bad in the blend, and this is the fault that matters.** s1 ≥ s2 are the singular
   values of the direction map's derivative, divided by 2.

   | setting | s1/s2 median | 95th | 99.9th | s2 smallest | surface turned over |
   |---|---|---|---|---|---|
   | planes = 1 (for scale) | 1.000 | 1.00 | 1.0 | 3.1e-3 | 0.0 % |
   | p=2 a=0.25 (default) | 1.001 | 15.0 | 547 | 3.1e-5 | 7.3 % |
   | p=2 a=0 | 1.53 | 10.6 | 319 | 2.6e-4 | 5.2 % |
   | p=2 a=0.45 | 1.000 | 12.1 | 967 | 2.6e-4 | 4.7 % |
   | p=2 a=0.25 smootherstep | 1.000 | 15.0 | 563 | 2.2e-4 | 7.4 % |
   | p=2 a=0.25 straight | 1.001 | 14.8 | 598 | 4.8e-5 | 6.3 % |
   | p=3 a=0.25 | 1.008 | 9.1 | 417 | 9.8e-5 | 29.0 % |
   | p=4 a=0.25 | 1.000 | 6.5 | 360 | 1.9e-5 | 30.6 % |
   | pinch p=2 a=0.25 | 1.000 | 127 | 10235 | 5.9e-10 | 0.0 % |
   | pinch p=2 a=0.4 | 1.000 | 106 | 17816 | 6.2e-9 | 0.0 % |

   (Numbers of the last run in `checks.txt`. The 99.9th percentile and the smallest s2 depend on the 20000
   directions drawn: an earlier run, `checks-before-pinch.txt`, gave 590 and 4.2e-4 for the default.)

   Inside each plane's band the map is the one-plane rule (ratio 1). All 40 worst directions of every setting sit
   in the blend, none in a plane's own band. For the blends with p = 2 they are about 79° from the x-axis (median)
   at t = 0.40 to 0.50; for p = 3 and 4, 59° to 71° at t = 0.26 to 0.42. For the pinch they are on the seam
   itself (t = 0.50), at any angle. "Turned over" is the
   share of directions where the derivative has a negative determinant: the blend folds the sphere of directions
   back over itself, and s2 passes through 0 on the fold lines. The first prototype round's pillow had no such
   regions; this is new and worse.
   Symmetries: the rule commutes with the turn by 180°/p about the x-axis and with the mirrors z → −z and
   y → −y to 1.1e-14 or better (2000 points, n = 2, 3, −2, every setting).

## Why it cannot work (an argument, checked numerically for p = 2, n = 2; not a written-out proof)

The seam half way between two planes is a mirror plane of the rule, so the rule has to send it into itself. Just
before the seam the two plane answers are mirror images of each other. On the seam at 45° (p = 2, n = 2) the
plane-0 answer runs round a loop that circles the z-axis and reaches 70° of latitude, while the seam's own great
circle stays under that loop and touches it only at the +x direction. So a continuous rule has two choices there:

- land somewhere on the seam circle away from the loop, which drags a strip of directions back across ground the
  plane rule has already covered. That is the fold-over measured above (4 to 7 % of directions, about 30 % for
  3 and 4 planes). A great-circle blend sends the seam out to 117° from +x and back, a map of degree 0, nothing
  like angle doubling;
- or crush the whole seam onto the +x direction. I built that as mix 2, "pinch". It has no fold-over (0.0 %
  measured) and no jump, but every seam point then follows the real map r² + c, so for c = −1 each seam plane
  holds a full disc of radius 1.62: the picture is the bodies with four enormous fins (`explore/pinch-j-bas-x.png`).

Either way the seam planes carry dynamics that have nothing to do with the folded picture, and their filled sets
are fat. The folded rule escapes this only by jumping. Counting covers says the same thing: a rule with p exact
planes and no fold-over is a map of degree 2p on the sphere of directions, against degree 2 for one plane.

## Pictures

Standard set, default settings (p = 2, a = 0.25, smoothstep, great circle), 1400x950 window, Balanced, 12 passes:
`<name>.png` (default colours) and `plain-<name>.png` (Depth from the camera) for m3d-default, m3d-top, m3d-x,
m3d-y, m3d-cut0, m3d-cut02, m2d-z000, m2d-z010, m2d-z025, m2d-z050, j-bas-3d, j-bas-top, j-bas-x, j-bas-2d-z000,
j-bas-2d-z020, j-rab-3d, j-off-3d, m3d-n3, m3d-n8. 38 files, no console or shader errors (`pictures.log`).
I looked at all 38 as six contact sheets (`sheets/std-*.png`, each tile 640 px wide), not at full size one by one.
Exploration: 20 variants × 7 views in `explore/` (4 passes, Depth colours), sheets `explore/sheet-<view>.png`.

Pieces of the solid in the 2D slices (`pieces.txt`; pieces under 0.05 % of the picture ignored):

| slice | pieces | largest, share of solid area | specks ignored | solid, share of picture |
|---|---|---|---|---|
| m2d z = 0 | 1 | 100 % | 0 | 15.5 % |
| m2d z = 0.10 | 3 | 93.7 % | 90 | 12.6 % |
| m2d z = 0.25 | 7 | 82.0 % | 68 | 6.0 % |
| m2d z = 0.50 | 1 | 94.4 % | 39 | 2.4 % |
| j-bas z = 0 | 1 | 100 % | 0 | 13.7 % |
| j-bas z = 0.20 | 1 | 100 % | 18 | 17.7 % |

What the pictures show:
- z = 0 slices are the flat Mandelbrot set and the flat basilica.
- Basilica: one swollen mass with two holes in the z = 0.2 slice; that slice is larger than the z = 0 slice
  (17.7 % against 13.7 %), the opposite of a row of bodies. From along x it is a rounded square about 1.7 across.
  No beads anywhere.
- Rabbit and the off-axis basilica: no flat torn sheets hanging in space. The off-axis basilica is one lumpy
  rock. The rabbit reads as a heap of blobs and curled shards; from one view I cannot tell whether it is one
  piece, and I did not slice it. Neither reads as a recognisable set.
- Mandelbrot: flames and fins in every view; seen along x a clean four-armed cross. Off-plane slices stay mostly
  in one piece but with fringes and islands (3 and 7 pieces at z = 0.1 and 0.25).
- a: 0 to 0.15 gives the smoothest, fattest blob; 0.25 to 0.35 the same with sharper ridges; 0.42 and 0.48 turn
  to dust with thin spikes on the seams. I did not render the folded baseline again beside a = 0.48, so "it
  does not tend to the folded picture" rests on the first round's folded pictures, and part of the dust may be
  the ray marcher failing on the steep blend rather than the set itself.
- Smootherstep and the straight blend are indistinguishable from the default in the pictures.
- p = 3 and 4: dustier and more shattered than p = 2 at the same a.
- Powers 3 and 8: smooth lumps with knobs, no tearing seen at the default.

## Speed (`speed.txt`): m3d-default, Balanced, 12 passes, four rounds back to back, shorter of two redraws

| rule | median | best |
|---|---|---|
| soft fold p=2 a=0.25 | 1.41 s | 1.05 s |
| soft fold, pinch a=0.4 | 1.45 s | 1.29 s |
| soft fold p=1 | 1.19 s | 0.63 s |
| Sphere inversions p=1 | 0.89 s | 0.64 s |
| Sphere inversions p=2 | 1.22 s | 1.14 s |

Soft fold against Sphere inversions: 1.58 times one plane, 1.16 times two planes (medians). The run is noisy:
soft fold with one plane is the same rule as Sphere inversions with one plane and still measured 1.34 on medians
(0.98 on best times), so read the ratios as "about 1.2 to 1.6", not to two digits. The solids also differ, so
this compares pictures, not cost per evaluation.

## What I would choose, and what is wrong

- If one setting must be shown: p = 2, a = 0.25, smoothstep, great circle. It is the least bad, and it is not good.
- The approach does not reach the target and I do not think a different S, a or p can. Any fix has to change what
  happens on the seams, and the seam argument above says the choice there is fold, crush or jump.
- Still open: no proof of the seam argument beyond p = 2, n = 2; the pinch's odd-power target is a guess that
  happened to test continuous at n = 3; fractional powers were not tested at all; the approach texts (about,
  crush, smooth) were written before the results and the scorecard was not looked at; light theme and phone
  untouched.

## Files

`10-approaches.js` (the deliverable; made by `make_approach.py`), `checks.js`, `run_checks.py`, `checks.txt`,
`checks-pinch.txt`, `checks-before-pinch.txt`, `pictures.py`, `pictures.json`, `pictures.log`, `pieces.py`,
`pieces.txt`, `speed.py`, `speed.txt`, `explore.py`, `explore/`, `sheets/`, the 38 pictures.
