# Pillow rule, layout "radial from the centre": prototype notes

Verdict first: the rule is exact on z = 0 and continuous everywhere, as claimed, and every numeric check
passes. The pictures are not good. The solid is one fat lump with a fibrous, shredded surface, not the lemon
bodies with rows of beads of Kucera's Figure 4. This layout distorts shapes a lot (median stretch ratio 2.6,
95th percentile 6.0 for the best variant, against the ideal 1), and no choice of profile inside the assignment
brings that near 1. I would not ship this layout.

Files (all in `out/proto/radial/`):
- `10-approaches.js`: base2 copy + approach `pillow` as the first entry. Written only by `make_approach.py`
  (`--round 0|1 --profile area|lin`), so the variants differ by two constants.
- `checks.js`, `run_checks.py` -> `checks.txt`: the numeric checks, run inside the built page.
- `pictures.py` -> `pictures.json`, `pictures.log`: the standard pictures. `pieces.py`: piece count of the slices.
- `speed.py` -> `speed.txt`. `proto.py`, `proto2.py`: numpy copy of the rule used to compare profiles.
  `nearplane.py`: how fast the slice changes off the plane.
- `rejected/lin/`, `rejected/area-sharp/`: the two dropped variants (approach file, checks, 7 key pictures each).
- `extra-*.png`: three views redrawn with 2000 ray steps, and 2D slices at z = 0.005 and 0.02.
- Test pages: `dist/proto-radial.html` (final), `dist/proto-radial-lin.html`, `dist/proto-radial-areasharp.html`.

## Formulas (final version: equal-area profile, rounded level curves)

Layout, weights (lA, lB, lC) -> unit direction with z >= 0:

    mn = min(lA, lB, lC);  e = 3 mn;  s = 1 - e                    (s: 0 centre, 1 boundary)
    k = 0 if lC is smallest (edge AB), else 1 if lA <= lB (edge BC), else 2 (edge CA)
    t = (next - mn) / s, next = lB, lC, lA for k = 0, 1, 2          (t = 1/2 when s = 0)
    w = 2t - 1;  lam = sqrt(1 + 3 w^2)                              (centre-to-edge distance on this ray / inradius, 1..2)
    eps = e / (1 + s (lam - 1))                                     (rounding; without it eps = e)
    z = eps (2 - eps);  rho = (1 - eps) sqrt(1 + z);  tau = (2 pi / 3)(k + t)
    direction = (rho cos tau, rho sin tau, z)

Inverse, (x, y, z >= 0) -> weights:

    eps = z / (1 + sqrt(1 - z))
    a = atan2(y, x) / (2 pi / 3), plus 3 if negative;  k = min(floor(a), 2);  t = a - k
    w = 2t - 1;  lam = sqrt(1 + 3 w^2);  e = lam eps / (1 + eps (lam - 1))
    m = (1-t, t, 0), (0, 1-t, t), (t, 0, 1-t) for k = 0, 1, 2;   l = e/3 + (1 - e) m

Rule, with m = round(n), r = |v|, d = v / r:

    l = Inverse(d.x, d.y, |d.z|)
    X = l if d.z >= 0, else (lA + lC, lB + lC, -lC)                 (mirror image in the edge AB)
    Y = (m XA - (m - 1), m XB, m XC)                                (times m about corner A)
    i = floor(Y), f = Y - i, S = fA + fB + fC, colour k = (iB - iC) mod 3
    g = (1, 0, 0)                 if S < 0.5 or S >= 2.5            (exactly on a lattice point)
      = (1 - fA, 1 - fC, 1 - fB)  if 1.5 < S < 2.5                  (upside-down triangle: lower half sphere, "flip")
      = (fA, fB, fC)              otherwise
    weights[(k + j) mod 3] = g[j], j = 0, 1, 2;  D = Layout(weights);  if flip: D.z = -D.z
    F(v) = r^m D          (r^m through the lab's aprPow, so lengths stop at e^42)

(XA, XB, XC) are the weights of the triangle with A at the origin, continued linearly over the whole sheet:
the task's lattice coordinates are (a, b) = (XB, -XC). Three coordinates instead of two keep a zero weight
exactly zero through the multiplication on all three edges, so a point of z = 0 returns z = 0 exactly (in the
shader too), with no rounding noise leaving the plane. `checks.js` rebuilds Phi and PhiInv from the task's
wording ((a, b), split along fa = fb) and the two agree to 5e-15.

Why equal area: in "triangular polar coordinates" (s, t) the triangle's area element is s ds dt, uniform in t,
so cos(theta) = 1 - s^2 makes the unrounded layout exactly area-true and needs no trig for the latitude.
Why rounding: near the centre the level curves of s are triangles; eps makes them circles there and leaves the
boundary alone (eps = e to first order only at mid-edges; at corners eps = e/2).

`mul` of two different points, `cmap`, `aprDiv`, `aprSPow`: copied from Sphere inversions with one plane
(the approach text says so). So mul(v, v) is NOT the pillow square; only `pw` and `sqr` use the pillow.

## A bug the checks caught

First build: exactness failed with relative error 1.73 at exactly 60, 120, 240 degrees, and the continuity
ratio was 1e9 at the corner directions, for every power except 3. Cause: on a lattice point all three
fractions are 0, which is neither "sum 1" nor "sum 2", so all weights were 0 and the layout returned corner A.
Fixed by the S < 0.5 / S >= 2.5 case above. All numbers below are after the fix.

## Check results (final version, `checks.txt`)

1. Exactness on z = 0, 500 points (160 on or within 1e-1..1e-14 of 0, 60, 120, 180, 240, 300 degrees, 60 with
   radius down to 1e-5), worst |F - z^n| / |z^n|:
   n=2 2.1e-15, n=3 4.6e-15, n=4 4.0e-15, n=5 5.6e-15, n=8 7.3e-15, n=-1 1.6e-15, n=-2 1.9e-15, n=-3 4.7e-15.
   The z part is exactly 0 in every case. (Closer to the origin than 1e-5 a negative power passes the lab's cap
   of 1.7e18 and the comparison is meaningless, so the test stops there.)
2. Continuity, 274000 pairs 1e-5 apart (200000 random; 20000 straddling the equator; 20000 straddling the
   meridians at 0, 60, ..., 300 degrees; 10000 at the poles; 12000 at the corner directions; 12000 at the
   mid-edge directions). |F(d1) - F(d2)| / |d1 - d2|:
   n=2: max 8.02, 99.9th percentile 5.93, median 2.32.  n=3: max 13.75, 99.9th 9.39, median 3.45.
   n=-2: max 8.02, 99.9th 5.93. No jump anywhere.
3. Round trips, 20000 samples: |Phi(PhiInv(d)) - d| <= 7.2e-15; PhiInv(Phi(u)) has the same triangle type
   every time and weights within 8.3e-16.
4. GLSL against JavaScript, 20480 values (8 powers, 2560 points, 12 of every 64 in the plane, 12 just beside
   it): worst |glsl - js| / (1 + |js|) = 3.2e-4 (at n = 8), none above 2e-3; sqr() 3.5e-5; mul() against the
   Sphere inversions shader 1.7e-6; shader z for plane points exactly 0; finite at the origin, on the axes and
   at 1e18.
5. Distortion of D = Phi o (x2) o PhiInv, 20000 directions, singular values / 2:
   s1/s2: median 2.56, 95th 6.02, 99.9th 10.3, max 11.8.  s1*s2: median 0.935, 5th 0.54, 95th 1.57, 99.9th 2.69.
   (n = 3: s1/s2 median 2.90, 95th 6.05, 99.9th 9.6; s1*s2 median 0.94, 95th 1.61.)
   Where: median s1/s2 by |latitude|: 0-10 deg 1.48, 10-25 deg 1.76, 25-45 deg 3.06, 45-65 deg 3.78,
   65-80 deg 2.65, 80-90 deg 2.27. All 40 worst s1/s2 sit within a few degrees of the equator on the mid-edge
   meridians (60, 180, 300 degrees): those three directions are the branch points of the doubling (three
   sheets meet there), so some blow-up there is built into any pillow layout. The worst s1*s2 (0.27) sit next
   to the poles on the corner meridians.

## What I tried and dropped

| variant | s1/s2 median / 95th / 99.9th (n=2) | s1*s2 5th / median / 95th | kept |
|---|---|---|---|
| polar angle linear in s (the starting point), `rejected/lin` | 4.44 / 6.73 / 9.0 | 0.75 / 1.02 / 1.15 | no |
| equal area, triangular level curves, `rejected/area-sharp` | 3.99 / 7.59 / 11.1 | 1.00 / 1.00 / 1.00 (exactly even) | no |
| equal area + rounded level curves | 2.56 / 6.02 / 10.3 | 0.54 / 0.94 / 1.57 | yes |
| linear + rounded (numpy only) | 2.66 / 5.63 / 9.3 | 0.43 / 0.88 / 1.79 | no |
| stereographic radius = s^a, a = 1, 0.8, 0.6, 0.45 (numpy only) | 3.89 .. 3.0 / 5.3 .. 8.1 | 95th 1.7 .. 3.0, 99.9th up to 27 | no |
| equal area + rounded + longitude blended toward the true angle near the centre (numpy only) | 2.31 / 4.88 / 10.0 | 0.57 / 0.91 / 1.71 | no: two more atan and a tan per step for a small gain |

All variants pass checks 1 to 4 (the two built ones were run through `checks.js`; their reports are in
`rejected/*/checks.txt`). Their pictures look the same in kind, a little more shredded.
Smoothing the corners of the distance to the boundary (the rounding) helps the median a lot and costs area
evenness. Nothing in this family gets the median under 2.3: the meridians leave the equator along rays to the
triangle's centre instead of at right angles, and that shear is the layout itself.

## Pictures: honest opinion

Standard set (18 pictures) in this folder, Balanced preset, default colours, 864x703 stage.

- z = 0 is right: `m2d-z000.png` is the Mandelbrot set, `j-bas-2d-z000.png` the basilica.
- Off the plane the solid stays mostly in one piece but its edge is ragged and it sheds crumbs:
  - `m2d-z000` (z = 0): 1 piece, 100 %.
  - `m2d-z010` (z = 0.1): 7 pieces over 0.05 % of the picture plus 60 specks; largest 94.3 % of the solid.
  - `m2d-z025` (z = 0.25): 6 pieces plus 68 specks; largest 84.0 %.
  - `m2d-z050` (z = 0.5): 2 pieces plus 16 specks; largest 85.4 %.
  - `j-bas-2d-z000` (z = 0): 1 piece. `j-bas-2d-z020` (z = 0.2): 1 piece plus 1 speck, 100 %.
- The flat set is fragile. Numpy copy of the rule (`nearplane.py`): at z = 0.003, 98 % of the flat set is still
  solid; at 0.01, 95 %; at 0.03, 91 %; at 0.1, 63 %; at 0.25, 37 %. By z = 0.02 the disc and the needle have
  already merged into one wedge (`extra-m2d-z002.png`). So the cut face of the 3D view "at height 0"
  (`m3d-cut0.png`), which samples within a few thousandths of the plane, shows that fattened outline, not the
  crisp flat set. More ray steps do not change it (`extra-m3d-cut0-steps2000.png` is identical).
- It does not look like Figure 4. `j-bas-3d`, `j-bas-top`, `j-bas-x`: one rock-shaped lump, no separate
  lemon bodies, no rows of beads on either great circle. The basilica's bulbs exist only in the plane; at
  z = 0.2 the slice is a plain blob. Detail in every direction, yes, but as fibres and scales, not as bulbs.
- Mandelbrot at n = 2 (`m3d-default`, `m3d-top`, `m3d-x`, `m3d-y`): a large pale, smooth, smeared shell
  about 1.6 units in radius with shredded edges, a dark band along the equator plane, and shredded foliage
  round the middle. From above the outline is not the Mandelbrot outline. Along x the solid runs out of the
  frame top and bottom (it is taller than 3.3 units in z).
- Creases: visible as kinks in the colour bands of every off-plane 2D slice, as the bright seam along the
  equator plane in the top views, and as flat facets on the knobs of `m3d-n8` and the slabs of `m3d-n3`.
  They are the rays from each triangle's centre to its corners and their images under the multiplication.
- Speckle: the Julia pictures have a hairy, grainy surface at 12 passes.
- `m3d-n8` is the most presentable: a ball of knobs, bulb-like. `j-rab-3d` is a clump of petals.

## Speed

`speed.txt`: default Mandelbrot picture, Balanced, 12 passes, four alternating rounds in one page, shorter of
two redraws per round. Pillow median 3.21 s (best 2.22), Sphere inversions (2 planes, its default) median
1.87 s (best 1.46): ratio 1.72. The single numbers scatter from 2.2 to 4.8 s and from 1.5 to 4.2 s on the
shared GPU, so read the ratio as "about 1.5 to 2 times slower". Pillow has no polynomial fast path for the
square (atan2, sqrt, cos, sin, three floors per step).

## Not done, not proven

- Not checked whether the pale shell in the n = 2 Mandelbrot views is real solid or the distance estimate
  reading short on a strongly sheared map. It is not a step-count artefact (2000 steps give the same picture);
  a brute-force volume sample would settle it. The 2D slices do not depend on the distance estimate.
- The other approaches: the page loads with no console errors, Sphere inversions drew in the speed run and
  its shader compiled in check 4. I did not rerun `tests/approaches-page.json` over all approaches.
- Scorecard texts for the pillow are drafts; I did not read the scorecard with this approach on screen.
- Fractional n is rounded inside the rule (texts say so). Negative n and n = 3, 4, 5, 8 are checked
  numerically; pictures exist for 2, 3 and 8 only.
- The entry carries `parts: { layout, inverse }` so `checks.js` can reach the two halves of the wrapping.
