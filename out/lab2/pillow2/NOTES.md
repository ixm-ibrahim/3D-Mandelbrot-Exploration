# lab2 / pillow2: is the pillow a rock by nature?

Work of 2026-11-17, 23:31 to 00:14 (43 minutes). Test page: `dist/lab2-pillow2.html`
(`python build.py --name lab2-pillow2 --base base4 --swap js/10-approaches.js=out/lab2/pillow2/10-approaches.js`).
Two approaches were added as the first entries of APPROACHES: `pillowsmooth` and `pillowboth`.

## summary

Yes for every pillow that can be built smoothly, and still yes for the best creased one.

- **With the creases gone the basilica is still one lump.** The angle-true pillow (`pillowsmooth`, no triangles, no
  creases, no seams) draws c = -1 as one smooth egg with a single spike: one piece at every height, 5.6 times the
  volume of the one-plane solid, and no waist at all where the flat bodies touch (cross-section at x = -0.618 is
  119 % of the cross-section through the centre; the one-plane rule gives 4 %, the folded rule 2 %).
- **The both-planes-exact pillow (`pillowboth`) is the nearest a pillow has come, and it is still one lump.** Both
  planes carry the flat set exactly, nothing jumps, the fin is gone, and the bodies have waists (27 % and 17 % at
  x = -0.618 and +0.618). But the waists never close: one piece at z = 0.2 where the one-plane and folded rules
  give three separate ovals. Its surface is fibrous and dusty everywhere. No bodies, no beads.
- **Why, and it is not "chaos on the whole sphere" as such.** The folded rule's direction map also stretches
  everywhere and has no attracting direction, and it draws bodies. What the two rules that draw bodies share, and
  no pillow has, is measured in `branch.json`: around every point of the plane they are a plain turn-and-scale
  (sideways stretch 2 = in-plane stretch 2, at every longitude, also around the direction (-1, 0, 0)). A pillow
  must wrap three sheets around three directions of the plane z = 0 (60, 180, 300 degrees; that is what degree 4
  costs), and 180 degrees is the negative x-axis, where the flat sets' touching points sit (-0.618 for the
  basilica, -0.75 for the Mandelbrot set). A smooth rule can only do a threefold wrap with sideways stretch 0, so
  everything near the negative x-axis is crushed onto the axis and shares its fate (bounded): a solid sleeve,
  hence the egg. A creased rule can keep some stretch there (radial 0.66 to 1.99, both 1.08 to 2.80 where 2 is
  needed in every direction) and the waist narrows as the stretch gets nearer an even 2 (119 % -> 74 % -> 27 %),
  but every crease is then copied onto a dense set of surfaces by the stretching, which is the fibrous look.
  So: smooth pillow = rock; creased pillow = fibres. That dilemma is the pillow's nature.
- **Worth showing the user?** Not as a candidate. `pillowboth` should not be shown (ugly, 2.7 times slower, and
  its z = 0 picture is drawn 6 to 9 % too fat). `pillowsmooth` is the only clean pillow picture and is cheap, but
  its z = 0 slice is not the flat set (51 % of the Mandelbrot set's area differs); at most a history entry
  labelled "reference, not exact", or one picture in the write-up that explains why the pillow route is closed.
- Untested and the only pillow idea left: a layout that is an even threefold cone (stretch exactly 2 in every
  direction) at the three wrap directions. First-order reasoning says the touching points would then pinch; it
  would still be creased everywhere. The measurements point elsewhere: keep each plane a turn-and-scale.

## formulas

### pillowsmooth (angle-true pillow, power 2; 4 and 8 by repeating)

    F(v) = |v|^2 * L(v/|v|)
    L: d = (x, y, z) unit.  w = (x + i y) / (1 + |z|)            (chart of the lower half sphere, |w| <= 1)
       N = 2 w^3 - 1,  D = w (2 - w^3),  q = |N|^2 + |D|^2
       L(d) = ( 2 Re(N conj D) / q,  2 Im(N conj D) / q,  s * (|N|^2 - |D|^2) / q ),  s = -1 if z > 0, +1 if z < 0
       input z exactly 0 -> output z exactly 0

This is w -> (2w^3 - 1)/(w(2 - w^3)) with w = (x + iy)/(1 - z); the map commutes with the mirror z -> -z
(R(1/conj w) = 1/conj R(w)), so the upper half is computed as the mirror image, and N/D is kept as a pair so
nothing is divided by zero. Power dial: n < 1.5 gives v; 1.5..3 one application (length |v|^2); 3..6 two
(|v|^4); above 6 three (|v|^8). No other powers exist in this reference.

### pillowboth (both planes exact; whole powers m = round(n))

    F_m(v) = |v|^m * Phi(m * PhiInv(v/|v|))

Sheet arithmetic exactly as out/proto/radial (three coordinates (XA, XB, XC), times m about the corner A, whole
and fractional parts give the triangle, its colour and its weights; lower half sphere = mirror image in edge AB).
Layout of one triangle on the half sphere z >= 0, weights (lA, lB, lC):

    mn = min(lA, lB, lC); e = 3 mn; s = 1 - e
    k = edge the ray from the centre meets (0: AB, 1: BC, 2: CA); t = (next weight - mn)/s, 1/2 if s = 0
    p = (cos(pi e/2) cos(T (k + t)), cos(pi e/2) sin(T (k + t)), sin(pi e/2)),  T = 2 pi/3     ("lin" radial layout)
    slide:  c = hypot(p.x, p.z)
            p.x >= 0:  a = (4/3) atan2(p.z, p.x);   (x, z) = c (cos a, sin a)
            p.x <  0:  b = (2/3) atan2(p.z, -p.x);  (x, z) = c (-cos b, sin b)        y unchanged

Inverse: undo the slide first (z + sqrt3 x >= 0: a = (3/4) atan2(z, x), (x, z) = c (cos a, sin a); else
b = (3/2) atan2(z, -x), (x, z) = c (-cos b, sin b)), then e = atan2(z, hypot(x, y)) * 2/pi, a = atan2(y, x)/T
(+3 if negative), k = min(floor(a), 2), t = a - k, weights = e/3 + (1 - e) * (1-t, t, 0) rotated to edge k.
The slide is the maths check's first alternative: tau' = (4/3) tau up to 90 degrees, (2/3) tau + 60 after; the
second branch is written from the far side so that z = 0 stays exactly 0. Face centres land at
(-1/2, 0, +-sqrt3/2). Input z exactly 0 -> output z exactly 0. Length for m = 2 is r*r in the shader.

In both approaches mul(a, b) of two different points and cmap are the one-plane sphere-inversion ones (cmap is
the identity).

## checks (all in double precision; checks.py, branch.py, inpage.py)

1. pillowsmooth is the pillow (checks-fast.log, A): R(1) = 1, R(w) = w^2, R(w^2) = w to 3e-15 (A fixed, B and C
   swapped); 2000 random targets each have exactly 4 distinct preimages; R' = 2 (w^3 + 1)^2 / (w (2 - w^3))^2,
   zeros (double) at longitude 60, 180, 300 degrees on |w| = 1 with images at 120, 0, 240 degrees;
   R(w) - 1 = (w - 1)(w + 1)^3 / (w (2 - w^3)); R'(1) = 8.000000 = 2^3; poles swap. Direct test: with
   Phi = Moebius(Weierstrass P' of the triangular lattice, lattice sum over 129,889 points),
   max |R(Phi(u)) - Phi(2u)| = 3.6e-13 over 300 random u; a triangle edge lands on |w| = 1 to 2e-16 and the
   altitude through A on the real axis to 2e-16. So R is "double the flat sheet" exactly.
2. Its z = 0 map against doubling (B): the plane is kept (|R| - 1 = 1e-15 on the circle; page: output z exactly 0),
   image angle = 2t + 2 atan2(sin 3t, 2 - cos 3t), wobble max 60.000 degrees at t = 20 degrees, rms 41.9 degrees,
   angular speed 0 to 8 where doubling is 2. Relative error against z^2 up to 1.0. The z = 0 Mandelbrot slice
   differs from the flat set in 48,254 px = 51.4 % of the flat set's area (numpy mask); in the picture 29 % extra
   and 22 % missing. The z = 0 "basilica" is an egg of area 3.41 against 1.52.
   Direction map: mean area stretch 3.99 (degree 4), stretch ratio in two perpendicular directions 1.0000
   (angle-true), linear stretch 0.14 / 1.48 / 4.04 at the 5th / 50th / 95th percentile.
3. pillowboth in the page (inpage.json, MATH.pillowboth, 200,000 points per plane): z = 0 follows z^2 to 2.5e-15
   with output z exactly 0; y = 0 follows (x + iz)^2 to 2.8e-15 (|y| < 8e-15). Largest step along 24 great
   circles: 0.00295 at 20,000 samples, 0.000308 at 200,000 (ratio 9.6: no jump). pillowsmooth: 0.00251 and
   0.000251 (ratio 10.0). Page against the maths check's own numpy code (out/proto/maths/pillow.py +
   twoplane_patch.py), 400 points: max difference 9e-15, so `pillowboth` is that rule; pillowsmooth 2.4e-15.
4. Around the direction (-1, 0, 0) (branch.json; a circle of directions of radius 1e-3, image radius per unit):
   one plane 2.000 to 2.000, image goes round once; folded 2.000 to 2.000, once; radial 0.66 to 1.99, three
   times; both 1.08 to 2.80, three times; smooth 0.0000007 (crushed), three times. Sideways stretch along the
   rest of z = 0: one plane and folded 2.0 everywhere; radial 2.0; both 1 (60..90 degrees), 2, 4 (150..180);
   smooth 0 to 8 (median 0.8).
5. Solids, 110^3 grid, 14 steps, bailout 64 (checks.json, D). Basilica c = -1:

   | rule | volume | half height z | half width y | section at x=-0.618 / centre | at +0.618 | 3D pieces |
   |---|---|---|---|---|---|---|
   | one plane | 0.815 | 0.51 | 0.68 | 3.8 % | 3.8 % | 1 (99.96 %) |
   | folded | 0.696 | 0.68 | 0.68 | 2.3 % | 2.3 % | 1 (99.95 %) |
   | pillow radial | 2.143 | 0.92 | 0.75 | 74 % | 34 % | 1 (100 %) |
   | pillowboth | 1.038 | 0.75 | 0.75 | 27 % | 17 % | 1 (99.97 %) |
   | pillowsmooth | 4.573 | 1.06 | 0.85 | 119 % | 35 % | 1 (100 %) |

   (Bodies that touch at a point read 2 to 4 % on this grid, and the whole grid counts as one piece because
   touching voxels are joined.) Mandelbrot solid, volume / half height z / half width y: one plane 0.473 / 0.28 /
   0.93; folded 1.114 / 1.04 / 1.04; radial 1.033 / 1.51 / 0.98; pillowboth 0.876 / 0.98 / 0.95; pillowsmooth
   1.180 / 1.28 / 1.13. So pillows are 3.5 to 5.4 times as tall as the one-plane lens, about as tall as the
   folded solid.
6. z = 0 pictures against the one-plane picture (flatdiff.txt, colour mode Depth from the camera, solid pixels):
   folded 12 px and 0 px differ; pillowboth draws 5,599 extra solid px on the Mandelbrot set (5.9 %) and 7,214 on
   the basilica (8.6 %), none missing, although its rule is exact there (numpy mask at z = 0: 0 px differ).
7. No console errors and no shader compile errors in any run (4 picture logs, inpage.log).

## components (pieces in the 2D slices)

Counted two ways: numpy masks on the pictures' own 864 x 703 grid (checks-fast.log C; 8-connected, pieces under
304 px are specks) and from the pixels of the plain- pictures (flatdiff.txt). They agree.

| slice | one plane | folded | pillowboth | pillowsmooth |
|---|---|---|---|---|
| Mandelbrot z = 0 | 1 piece, 100 % | 1, 100 % | 1, 100 % (picture 5.9 % too fat) | 1, 99.7 %, 82 specks, not the flat set |
| Mandelbrot z = 0.10 | 1, 100 % | 1, 99.8 %, 36 specks | 5 pieces, largest 94.2 %, 186 specks (pixels: 7 pieces, 91.9 %) | 1, 99.96 % |
| Mandelbrot z = 0.25 | 1, 100 % | 2, 95.7 % + 3.9 % | 5 pieces, largest 93.4 %, 23 specks | 1, 99.9 % |
| basilica z = 0 | 1, 100 % | 1, 100 % | 1, 100 % (picture 8.6 % too fat) | 1, 100 %, an egg of area 3.41 |
| basilica z = 0.02 | 1, area 98 % of flat | 1, 96 % | 1, area 108 % of flat | 1, area 100 % of its own |
| basilica z = 0.20 | 3 pieces 76 / 12 / 12 % | 3 pieces 83 / 8.5 / 8.5 % | 1 piece 99.7 %, 100 specks | 1 piece, 100 % |
| basilica z = 0.40 | 1 | 1, 97 % | 3 pieces 88.7 / 4.5 / 4.5 % | 1, 100 % |

Radial pillow for reference: basilica area grows off the plane (1.52 at 0, 1.75 at 0.02, 1.99 at 0.1), 1 piece.

## speed

Default Mandelbrot picture (864 x 703, Balanced), 6 timed redraws each, turn about in one page (inpage.json):
medians one plane 0.86 s, folded 1.06 s, pillowsmooth 1.19 s, pillowboth 2.30 s. Ratios to one plane: 1.00,
1.23, 1.37, 2.66. Single redraws ranged 0.5 to 4.7 s on the shared GPU.

## pictures

`pillowsmooth/` and `pillowboth/`: m3d-default, m3d-top, m3d-x, j-bas-3d, j-bas-top, j-bas-x, j-rab-3d, m2d-z000,
m2d-z010, m2d-z025, j-bas-2d-z000, j-bas-2d-z020, each in the default colours and as plain-<name>.png (colour
mode "Depth from the camera"). `mercator1/` and `mercator2/`: the same twelve, plain- only, for comparison.
Looked at: pillowsmooth plain-j-bas-3d, j-bas-top, plain-m3d-default; pillowboth plain-j-bas-3d, plain-j-bas-top,
plain-j-bas-2d-z020, plain-m3d-default; mercator2 plain-j-bas-3d. The other 62 pictures were not looked at.

- pillowsmooth basilica: a smooth egg, slightly dimpled, one spike toward +x. No bodies, no beads.
- pillowsmooth Mandelbrot: a smooth fat body with sprays of spikes and fins. No creases.
- pillowboth basilica: a fibrous, dusty diamond; the outline from above hints at a fat middle with wings; a dark
  pinched line along z = 0. No bodies, no beads.
- pillowboth Mandelbrot: a lump of feathered sheets.
- folded (mercator2) basilica: the Figure 4 look: a row of round bodies with rings of small beads.

## problems

- Neither approach looks like Figure 4, and neither should be offered as a fix.
- pillowboth's z = 0 picture is too fat (5.9 % and 8.6 % extra solid pixels) although the rule is exact on the
  plane. Cause not found; the earlier pillows had the same fault. It would fail the standing requirement on screen.
- The shader was not compared with the JavaScript numerically for either approach. pillowboth's shader calls
  atan, sin and cos, which an earlier engineer measured as good to only 4 to 5 digits on this GPU.
- pillowboth: the plane y = 0 is exact in double precision only; nothing protects it in the shader.
- pillowboth keeps the slide's kink at 90 degrees and the radial layout's creases; no smoothing was tried.
- The explanation of the lump is measured at one direction and argued to first order; it is not a proof. The
  "even threefold cone" layout was not built.
- pillowsmooth exists for powers 2, 4, 8 only; below 1.5 it returns v. Negative powers do nothing.
- pillowboth rounds fractional powers.
- Pictures use 14 steps only; powers other than 2 were not drawn; the texts on the page were not read on screen.
- 3D piece counts on a 110^3 grid cannot tell touching bodies from joined ones; the section ratios do that job.
- The private page puts the two pillows first, so its Approach reset selects pillowsmooth and tools/smoke.json
  would fail on it. tests/ were not run.
- 43 minutes used against the 40 minute target.

## files

- `10-approaches.js` (generated by `make_approach.py` from base4), `pictures.py`, `checks.py`, `checks_rules.py`,
  `branch.py`, `inpage.py`
- results: `checks-fast.json` / `checks-fast.log` (A, B, C), `checks.json` / `checks-solid.log` (D; its A section
  carries an older, wrong wording of the edge test), `branch.json`, `inpage.json`, `inpage.log`, `flatdiff.txt`
- pictures: `pillowsmooth/`, `pillowboth/`, `mercator1/`, `mercator2/` (each with pictures.json and pictures.log)
