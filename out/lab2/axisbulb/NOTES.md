# axisbulb: bulbs about the real axis (lab 2 prototype)

Worked 23:31 to about 00:10. Everything is in `out/lab2/axisbulb/`. Test page: `dist/lab2-axisbulb.html`, built with
`python build.py --name lab2-axisbulb --base base4 --swap js/10-approaches.js=out/lab2/axisbulb/10-approaches.js`.
Nothing outside `out/lab2/axisbulb/` and `dist/lab2-axisbulb*.html` was written.

## Verdict first

**Not bodies with beads around both great circles. Lathe rings, or taffy.** No setting of this family reaches the
look of Figure 4, and for the basilica (c = -1) none can, for a reason that is a two-line proof (below).

- **k = 5 and k = -3 (the turn multiplied):** continuous, and exact on both planes as claimed. But the Mandelbrot
  solid and every Julia set with c off the x-axis are masses of flames and whiskers, the exact slice at z = 0 is an
  infinitely thin sheet standing in a different solid (the slice at z = 0.000000001 already has 32% less area), and
  the renderer's distance estimate breaks down. Worse than the folded rule for the user's complaint.
- **k = 1 with a wobble A = 0.2 (the best variant, the default of the dials):** clean, connected, slices change
  gently with height. It is the lathe with its rings warped: on the Mandelbrot solid some rings open into ribbons
  and the small period-2 body grows a few buds. The basilica is exactly the lathe's body of revolution, rings and all.
  The rabbit is smooth drapery.
- **Pinch (a dial I added, the only one that changes a Julia set with c on the x-axis):** the bodies get four fins
  (a star in cross-section). Fins, not beads.

## Why the basilica cannot get beads here (proved, then measured)

Write v by its length r, its angle β from the x-axis and its turn γ around it. Every rule of this family has the
form (r, β, γ) -> (r^n, nβ, G(β, γ)). When c is on the x-axis, adding c changes x only, so x' = r^n cos nβ + c and
the distance from the axis ρ' = r^n |sin nβ| depend on (r, β) alone. The turn never feeds back. So the escape of a
point does not depend on its turn, and the solid is the lathe's body of revolution **for every k, A and reach**.
Measured (checks.txt, 5a): of 20000 random start points, 0 get a different escape step from the lathe, for k = 5,
-3, 9 and for wobbles 0.2, 0.6. Rings stay rings. Beads need the angle from the axis or the length to depend on the
turn. The pinch does that (7055 of 20000 points change), and gives fins.

## The rule (as built; a re-implementation needs only this)

v = (x, y, z), r = |v|, ρ = |(y, z)|, β = atan2(ρ, x) in [0, π].

1. The lathe power: w = R · (cos nβ, sin nβ · y/ρ, sin nβ · z/ρ), with R = exp(min(n · ln(max(r, 1e-30)), 42)) (the
   lab's capped power), (y/ρ, z/ρ) = (1, 0) when ρ = 0, and w = 0 when r < 1e-20 and n > 0.
   For n = 2 the shader uses w = (x² - y² - z², 2xy, 2xz), capped at 1.74e18 per component.
2. The turn, applied to w: ρ' = |(w.y, w.z)|; if ρ' = 0 return w. (c, s) = (w.y, w.z) / ρ', r' = |w|.
   - e = (c + i·s)^|k| by |k| complex multiplications starting from 1; conjugate e if k < 0.
   - if A ≠ 0: t = clamp((ρ'/r') / sin(reach), 0, 1) (t = 1 when reach = 0), W = t²(3 - 2t),
     φ = A · W · 4cs(c² - s²)   [= A·W·sin 4γ], e = e · (cos φ + i sin φ).
   - if B ≠ 0: g = 1 + B · (2cs)² · (ρ'/r')²   [= 1 + B sin² 2γ sin² nβ], else g = 1.
   - F(v) = g · (w.x, ρ' · Re e, ρ' · Im e)   (capped at 1.74e18 per component when B ≠ 0).
3. mul(a, b) = turn(lathe product), the lathe product being (a.x b.x - a.y b.y - a.z b.z, a.x b.y + b.x a.y,
   a.x b.z + b.x a.z) capped. **This is copied from the lathe approach**, which treats its spin dial the same way.
   sqr(v) = turn(lathe square). cmap(c) = c.

Dials: `k` (whole, -7 to 9, default 1), `wob` = A (0 to 1 on the slider, -1 to 1 typed, default 0.2), `reach`
(degrees, 0 to 90, default 45), `pinch` = B (0 to 4, default 0). uA = (k, A, reach, B).

In angles, for odd k: (β, γ) -> (nβ, kγ + A·W·sin 4γ), length r^n (1 + B sin² 2γ sin² nβ).

Two departures from the wording of the assignment, both deliberate:
- **The turn is applied to the result of the lathe power**, so its turn is γ or γ + 180°. For odd k that is the
  assignment's formula exactly (k(γ + 180°) = kγ + 180°). For even k it differs by half a turn where sin nβ < 0.
  Even k is not exact on z = 0 either way. This makes pw(v, 2) = sqr(v) = mul(v, v).
- **W is taken at the result's angle from the x-axis**, not the input's. The wobble then fades wherever the image
  touches the axis (also at the cones that are crushed onto it), at every power.

e^(iγ) is raised to the power k by multiplication and sin 4γ is a polynomial, so a point with z = 0 comes out with
z exactly 0 (same for y = 0). That is needed: for |k| > 1 the two planes repel in the turn direction, so a rounding
leak of 4e-7 (sin 5π in 32-bit numbers) would be multiplied by 5 at every step.

## Claims of the assignment, checked

| Claim | Result |
|---|---|
| continuous for whole k | yes (check 2) |
| exact on z = 0 and y = 0 when k = 1 mod 4 | yes: 1, 5, 9, -3, -7. k = 3, -1: z = 0 exact, y = 0 carries conj(w)^n. Even k: neither plane |
| planes at 45° carry conj(z)^n | yes for k = 5 and -3. For k = 9, -7 (and 1) they carry the power itself |
| wobble keeps z = 0 and y = 0 exact for any A | yes, also at A = 1 with reach 0. With k = 1 it keeps the 45° planes exact too |
| milder family γ -> γ + (k - 1)·γ·W(β), W rising smoothly | **cannot be done, not built.** At γ = 180° it gives 180°·(1 + (k - 1)W), which is 180° only when (k - 1)W is an even whole number, so the half y < 0 of the plane z = 0 is no longer exact, and the rule tears along that half-plane unless (k - 1)W is whole. A turn map of degree 1 cannot be deformed into one of degree k. The multiplier could only change in steps at cones where sin nβ = 0. Not tried |
| some A and W turn the lathe's rings into rows of beads | **no**, see the proof above for c on the axis; on the Mandelbrot solid the rings open into ribbons |

## Numbers (all in checks.txt; run with `python out/lab2/axisbulb/run_checks.py`, about 20 s)

1. **Exactness**, 500 points per plane, n = 2, 3, 4, 5, 8, -1, -2, -3: worst relative error
   1.8e-15, 4.6e-15, 3.6e-15, 5.4e-15, 7.3e-15, 9.1e-16, 1.6e-15, 4.6e-15, the same on z = 0 and on y = 0, for
   k = 5, -3, 9, -7 and for k = 1 with wobble 0.2, 0.6 and with pinch 1.5. Limit was 1e-6.
2. **Continuity**, 200000 random pairs 1e-5 apart plus 56000 special pairs (straddling the 8 half-planes at
   multiples of 45°, the 8 seams half way, both ends of the x-axis, the crushed cones). Largest ratio, and 99.9th
   percentile of the random pairs:

   | setting | n = 2 | n = 3 | n = -2 |
   |---|---|---|---|
   | k = 5 | 10.00, 9.86 | 15.00, 14.60 | 10.00, 9.87 |
   | k = -3 | 6.00, 5.92 | 9.00, 8.77 | 6.00, 5.93 |
   | k = 1, A = 0.2 | 3.35, 3.21 | 4.97, 4.64 | 3.35, 3.21 |
   | k = 1, A = 0.6 | 6.31, 5.95 | 9.35, 8.50 | 6.31, 5.98 |
   | k = 5, A = 0.2 | 10.92, 10.63 | 16.25, 15.54 | 10.92, 10.66 |
   | k = 1, B = 1.5 | 5.58, 5.48 | 8.16, 7.95 | 5.57, 5.48 |
   | k = -7, A = 1, reach 0, B = 4 | 82.59, 79.75 | 118.92, 111.66 | 82.60, 79.76 |
   | k = 1 (lathe) | 2.00, 2.00 | 3.00, 3.00 | 2.00, 2.00 |
   | Sphere inversions folded on 2 planes | 6073288, 2.00 (jump) | | |

   No jump anywhere. For a plain k the largest stretch is |n·k|, at the x-axis.
3. **GLSL against JavaScript**, 11 settings x 8 powers x 640 points: worst |glsl - js| / (1 + |js|) between 9.2e-5
   and 1.6e-4 (always at n = 8, the limit of 32-bit numbers), no value above 2e-3. sqr() against the JavaScript
   square at most 2.4e-5, mul(a, b) against the lathe product followed by the turn at most 2.5e-5. A point with
   z = 0 comes back with z exactly 0 in every setting, a point with y = 0 with y exactly 0 (except k = 2, which
   does not keep that plane). Finite at the origin, on the axes and at 1e18.
4. **Distortion at n = 2**, 20000 directions, s1/s2 median, 95th, 99.9th percentile:
   k = 5: 2.83, 4.9, 174. k = -3: 1.99, 6.4, 290. k = 1, A = 0.2: 2.84, 19.5, 871. k = 1, A = 0.6: 2.32, 38.6, 1402.
   k = 5, A = 0.2: 2.79, 5.3, 174. Pinch 1.5: 1.73, 19.4, 871. Lathe: 2.01, 19.2, 871. Sphere inversions, one
   plane: 1.00, 1.0, 1. All 200 worst values lie within 5° of the plane x = 0, which the rule crushes onto the
   negative x-axis (s2 goes to 0 there, as for the lathe); none near the x-axis. Beside the x-axis s1 = |k|.
5. **What the user would see when slicing** (5b, 5c). Area of the Mandelbrot solid's slice at heights
   0, 1e-9, 1e-6, 1e-4, 0.01, 0.05, 0.1, 0.25, 0.5 (40 steps):

   | setting | areas |
   |---|---|
   | k = 5 | 1.622, 1.107, 1.046, 1.020, 1.074, 1.012, 0.892, 0.622, 0.315 |
   | k = -3 | 1.622, 1.314, 1.199, 1.165, 1.168, 1.034, 0.820, 0.447, 0.291 |
   | k = 1, A = 0.2 | 1.622, 1.620, 1.613, 1.608, 1.602, 1.581, 1.539, 1.285, 0.766 |
   | k = 1, B = 1.5 | 1.622, 1.620, 1.612, 1.612, 1.584, 1.337, 1.056, 0.472, 0.252 |
   | lathe | 1.622, 1.620, 1.612, 1.612, 1.608, 1.593, 1.557, 1.292, 0.768 |
   | Sphere inversions, one plane | 1.622, 1.619, 1.612, 1.602, 1.460, 0.930, 0.624, 0.018, 0.000 |
   | folded on 2 planes | 1.622, 1.619, 1.612, 1.609, 1.637, 1.428, 1.111, 0.445, 0.000 |

   **For k = 5 the slice loses a third of its area between z = 0 and z = 1e-9.** The plane is exact but repelling:
   the turn is multiplied by k at every step, so a point 1e-9 off the plane is far from it after 13 steps. At the
   attracting fixed point p of z² + c the multiplier across the plane is 2k·Re p against 2|p| inside it (c = -0.5,
   k = 5: 3.66). The exact flat set is a sheet of zero thickness; a 3D picture cannot show it. Cutting by
   half-planes through the axis says the same (turn 0°: 0.806, turn 0.001°: 0.515). With the wobble at 0.2 nothing
   of the kind happens (0.806, 0.806, 0.798 ...).

## Pieces in the 2D slice pictures (pieces.txt)

Best variant: Mandelbrot z = 0: 1 piece (100%); z = 0.10: 1 piece (99.9%); z = 0.25: 2 pieces (largest 90.2%;
11.73% and 1.26% of the picture); z = 0.50: 2 pieces (largest 99.2%; the other is 0.05%). Basilica z = 0: 1 piece;
z = 0.20: 3 pieces (largest 79.5%). The lathe itself gives the same 2 pieces at z = 0.25 (largest 90.3%): they are
bodies that touch in one point of the x-axis, so a level slice separates them. Not a tear.
Other variants at z = 0.25: k = 5: 7 pieces and 177 specks (largest 90.8%); k = -3: 3 pieces and 80 specks (90.5%);
A = -0.2: 2 pieces (91.0%); A = 0.6: 2 pieces and 30 specks (91.4%); pinch 1.5: 2 pieces and 15 specks (87.4%).

## Speed against the lathe (speed.txt and speed-before-pinch-dial.txt)

m3d-default, Balanced, 12 passes, stage 862 x 701, 3 rounds, median, back to back. Two runs:

| setting | run 1 | run 2 |
|---|---|---|
| lathe | 1.09 s | 1.00 s |
| axisbulb k = 1, A = 0 (returns early, the lathe itself) | 0.56 s, 0.51x | 1.21 s, 1.21x |
| axisbulb k = 1, A = 1e-6 (the lathe's solid, whole code path) | 0.94 s, 0.87x | 1.22 s, 1.22x |
| axisbulb k = 1, A = 0.2 (best variant) | 1.22 s, 1.11x | 0.94 s, 0.94x |
| axisbulb k = 5 | 1.75 s, 1.61x | 1.35 s, 1.35x |
| axisbulb k = 9, A = 0.2 | 1.87 s, 1.71x | 2.13 s, 2.12x |

**Not resolved better than about ±50%**: the same code (k = 1, A = 0 is the lathe) measured 0.51x and 1.21x. The GPU
was shared. Honest reading: with k = 1 the cost is the lathe's within the noise; k = 5 about 1.3 to 1.6x; k = 9 with
wobble about 1.7 to 2.1x (part of that is a rougher solid, which costs more ray steps).

## Pictures

Best variant (k = 1, A = 0.2, reach 45°), default window 1400 x 950, Balanced, clipped to the stage, each as
`<name>.png` (default colours) and `plain-<name>.png` (Depth from the camera): m3d-default, m3d-top, m3d-x, m3d-y,
m3d-cut0, m3d-cut02, m2d-z000, m2d-z010, m2d-z025, m2d-z050, j-bas-3d, j-bas-top, j-bas-x, j-bas-2d-z000,
j-bas-2d-z020, j-rab-3d, j-off-3d, m3d-n3, m3d-n8. 38 files. Contact sheets: sheet-m3d.png, sheet-m2d.png,
sheet-jbas.png, sheet-rest.png.
Other variants, 10 files each plus sheet.png: v-k5, v-km3, v-k1-am020 (A = -0.2), v-k1-a060, v-k1-a020 (the best
variant again, made first), v-k1-b150 (pinch 1.5), v-lathe (the lathe approach, for comparison).
Extras: x-pinch/ (pinch 0.5, 1.5, 4 at 4 passes), sheet-k5-km3-de0.png and v-k5/extra-*.png (see next section).

What they show:
- m3d-*: the lathe's Mandelbrot body. Along the x-axis the rings are slightly squared; some rings on the big body
  stand open as ribbons; buds on the small body. m3d-cut0 shows the exact flat set on the cut face, m3d-cut02 one
  connected face.
- m2d-*: z = 0 is the flat Mandelbrot set. The outline shrinks smoothly with height.
- j-bas-*: a row of lemon-shaped bodies with rings. j-bas-x is a set of perfect circles. No beads.
- j-rab-3d: smooth drapery. j-off-3d: nearly the body of revolution. m3d-n3: rings with torn edges. m3d-n8: rings.
- The fine coloured rings on smooth surfaces in the default colours are the known trap-colouring fault.

## The distance estimate fails for |k| > 1

With k = 5 the Balanced picture of the basilica is a dark smeared spindle, although the solid is the lathe's.
2000 ray steps do not help (v-k5/extra-plain-j-bas-3d-steps2000.png). With the distance estimate set to "none" the
same picture is the lathe's row of bodies (v-k5/extra-plain-j-bas-3d-de0.png, v-k5/extra-sheet.png). Cause: the
estimate divides by the size of the orbit's derivative, which grows by k per step in the turn direction although the
escape does not depend on the turn at all. The flames of the k = 5 and k = -3 Mandelbrot solid are **not** only this
artefact: they are still there with the estimate off and 700 steps (sheet-k5-km3-de0.png), and the cut at z = 0.02
is a ragged fish shape, not the Mandelbrot set.

## What I tried

1. Plain k = 5 and k = -3. Rejected: flames, zero-thickness exact slice, broken distance estimate.
2. Wobble with k = 1: A = 0.2, 0.6, -0.2, reach 45°. A = 0.2 and -0.2 look alike (warped lathe); 0.6 is taffy.
3. k = 5 with a wobble 0.2: numbers only (same faults as k = 5).
4. Pinch B = 0.5, 1.5, 4 with k = 1: four-finned bodies; the flat disc at x = 0 survives as a ring.

## Problems, plainly

- The target look is not reached, and for c on the x-axis it cannot be reached by turning alone.
- The default dials are k = 1, A = 0.2 (the best variant), not the k = 5 the assignment leads with.
- I looked at every picture, but most of them on contact sheets at half size; 9 at full size.
- The pinch dial came late: checks and one key set of pictures, no tuning, no full set.
- reach was only used at 45° (and 0° in one check setting). Negative A only by typing.
- Speed is inconclusive to ±50%.
- The panel texts (crush, smooth, slice, round note) were written quickly and not compared with the scorecard.
- Not verified in the shader, only reasoned: the existing lathe approach with spin 5 computes the turn through
  angles, so in 32-bit numbers its plane z = 0 should leak for y < 0. Worth a look by whoever owns it.

## For the next round

Two conditions came out of this, and any candidate can be tested against them in a minute with section 5 of
checks.js: (1) the angle from the axis or the length must depend on the turn, or the basilica stays a body of
revolution; (2) the exact planes must not repel in the turn direction, or the exact slice has no thickness.
A wobble with negative A makes the two planes attract (turn derivative 1 - 4|A|W there). Untested idea: combine that
with a pinch whose profile is much sharper than sin² 2γ, so the lathe's rings are cut into short arcs at the planes.
