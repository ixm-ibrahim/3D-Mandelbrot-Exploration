# Outside formulas for a power-2 "3D Mandelbrot", each with its source

Round 23, section outside1. Every formula below was read today (2026-11-19) from a source that can be opened; none is
from memory. Most are quoted from the source code of Mandelbulber 2 (GPLv3), whose files name the forum thread each
formula came from. `MB2/` stands for
`https://raw.githubusercontent.com/buddhi1980/mandelbulber2/master/mandelbulber2/formula/` (files `definition/fractal_<name>.cpp`
or `opencl/<name>.cl`). Only the lines that do the squaring are copied; switches that are off by default are left out and named.

What could NOT be read: `www.fractalforums.com` answered every request with "SMF was unable to connect to the database"
(later HTTP 429), `web.archive.org` is blocked for the fetch tool, `bugman123.com` (Paul Nylander) has an expired
certificate, the AMS Notices PDF answered 403. So the forum posts themselves are not quoted; the thread addresses are
given as Mandelbulber's source files cite them.

Our rule names are those of `out/r23/outside1/outrules.py` (`O.get(name)` gives a rule of `out/r21/lib/mem.py`).
Our axes: flat plane z = 0, real line = x-axis. Numbers: `check.log` (flat check on 20,000 points per set, lift test,
round 17's screen and direction count), `compare.log`. "Lift" = share of flat-inside points that stay when lifted by a millionth.

## A. Formulas that are "square, then add c", tested

### 1. Mandelbulb, power 2 (Daniel White, Paul Nylander) — rule `mb2`
Source: `MB2/definition/fractal_mandelbulb_power2.cpp`, which cites
http://www.fractalforums.com/3d-fractal-generation/true-3d-mandlebrot-type-fractal/

    double temp = 1.0 - z2 / (x2 + y2);
    double newx = (x2 - y2) * temp;
    double newy = 2.0 * z.x * z.y * temp;
    double newz = -2.0 * z.z * sqrt(x2 + y2);

In words: longitude doubled, latitude doubled, length squared. (The bench's `mandelbulb` is the same with +2 z sqrt.)
- Flat check: 0 differ in all four sets. Lift 1.000 / 1.000.
- Door: fold (70.7 % of directions land mirror-reversed) and a tear at the two poles (largest stretch unbounded). Only 2
  directions go to -x: buds in the flat plane only.
- Seen (`all-solids-1.png`): c = -1 bodies with striped flakes and whiskers; rabbit bodies with loose debris.

### 2. Quaternion square, 3D cut — rule `quat3d`
Source: `MB2/definition/fractal_quaternion3d.cpp` (same thread as 1):
`z = CVector4(z.x * z.x - z.y * z.y - z.z * z.z, z.x * z.y, z.x * z.z, z.w);` then `z *= constantMultiplier122` (1, 2, 2).
- This is the lab's Lathe exactly. Flat check 0 differ. A whole circle of directions goes to -x: rings (seen).

### 3. Bristorbrot (Doug Bristor) — rule `bristor`
Source: `MB2/definition/fractal_bristorbrot.cpp`, cites http://www.fractalforums.com/theory/bristorbrot-3d/

    double newx = z.x * z.x - z.y * z.y - z.z * z.z;
    double newy = z.y * (2.0 * z.x - z.z);
    double newz = z.z * (2.0 * z.x + z.y);

- Flat check: 0 differ in all four sets (exact on z = 0 and on y = 0, a polynomial, no tear: jumps 3e-4 at step 1e-4).
  Lift 1.000 / 1.000. It does not square the length (|F| / r^2 between 0.58 and 1.49).
- Door: fold (50 %). 6 directions go to -x (four in the two planes, two off them), 2 to +x.
- Seen: c = -1 bodies with rough fins between the two planes, no round buds off them (`cuts-bristor.png`: the cuts at
  22.5 and 45 degrees are smooth with tiny bumps). Rabbit: one ridged lump (inside share 0.052 of the box against 0.016
  for one plane); the cut across the x-axis is a disc with two long arcs (the ears swept round).

### 4. Msltoe "Sym2" (msltoe, "choosing the squaring formula by location", 2009-2010) — rule `sym2`
Source: `MB2/definition/fractal_msltoe_sym2_mod.cpp`, "based on the formula from Mandelbulb3D", cites
http://www.fractalforums.com/theory/choosing-the-squaring-formula-by-location/15/

    if (fabs(z.y) < fabs(z.z)) // then swap
    { z.y = temp.z; z.z = temp.y; }      // making z.y furthest away from axis
    if (z.y > z.z) // then change sign of z.x and z.z
    { z.x = -z.x; }
    double v3 = (z2.x + z2.y + z2.z);
    double zr = 1.0 - z2.z / v3;
    temp.x = (z2.x - z2.y) * zr;
    temp.y = 2.0 * z.x * z.y * zr * scale;   // scale = 1
    temp.z = 2.0 * z.z * sqrt(z2.x + z2.y);

In words: of the two planes z = 0 and y = 0 take the nearer one, then square about it (a Mandelbulb-type square).
This is the IDEA of the lab's "Sphere inversions, two planes", published on the forum years ago.
- Flat check: c = -1: 0 differ. Rabbit: 2715 differ = every flat-inside point is lost (the sign change of x mirrors the
  flat plane: the plane's map is (x, y) -> (x^2 - y^2, -2 x |y|), which is the flat rule only when c is on the x-axis).
  Mandelbrot set 2337, Siegel 3415 differ. Lift: c = -1 1.000; rabbit 0.000 (nothing there at all, seen: empty panels).
- Door: tear (jump 2.0 at step 1e-4) and fold. 4 directions to -x, 2 to +x: the liked count.
- Against ours: for c = -1 the verdicts differ from `twoplane` on 3.8 % of the inside. Seen: the same clean bodies
  with four buds each.

### 5. Msltoe "Sym3" — rule `sym3`
Source: `MB2/definition/fractal_msltoe_sym3_mod.cpp` (same thread). As Sym2, but
`if (z.y > z.z) { z.x = -z.x; z.z = -z.z; }` and `v3 = (z2.x + z2.y + z2.z) + scale0 * scale0 * z2.y * z2.z` (scale0 = 0 here).
- Same numbers as Sym2 on every set (flat: c = -1 exact, rabbit lost), but NO tear (jumps 2e-4): the second sign
  change turns the tear into a mirror fold. Folded 50 %. 4 directions to -x, 2 to +x.

### 6. Msltoe "Sym4" — rule `sym4`
Source: `MB2/definition/fractal_msltoe_sym4_mod.cpp` (same thread):

    if (fabs(z.x) < fabs(z.z) * ...x) swap(z.x, z.z);      // multipliers 1
    if (fabs(z.x) < fabs(z.y) * ...y) swap(z.x, z.y);
    if (fabs(z.y) < fabs(z.z) * ...z) swap(z.y, z.z);
    if (z.x * z.z < 0.0) z.z = -z.z;
    if (z.x * z.y < 0.0) z.y = -z.y;
    temp.x = z.x * z.x - z.y * z.y - z.z * z.z;  temp.y = 2.0 * z.x * z.y;  temp.z = 2.0 * z.x * z.z;

In words: the largest coordinate is made the real one (cube symmetry), then the quaternion square.
- Flat check fails everywhere (c = -1: 4097 of 20,000 differ). Seen: a cross of lumps with debris; rabbit empty.

### 7. Eiffie's version of msltoe's bulb (Eiffie, reply 69, 27 January 2015) — rule `eiffie`
Source: `MB2/definition/fractal_eiffie_msltoe.cpp`, cites
http://www.fractalforums.com/theory/choosing-the-squaring-formula-by-location/60/

    double psi = fabs(fmod(atan2(z.z, z.y) + M_PI + M_PI_8, M_PI_4) - M_PI_8);
    double lengthYZ = sqrt(z.y * z.y + z.z * z.z);
    z.y = cos(psi) * lengthYZ;
    z.z = sin(psi) * lengthYZ;
    ... then the same square as Sym2 (m = 1.0 - z2.z / rr; (z2.x - z2.y) * m; 2 x y m; 2 z sqrt(z2.x + z2.y))

In words: the turn round the x-axis is folded into a wedge 22.5 degrees wide (eight wedges, each mirrored), so the
square is always taken about the nearest of FOUR planes through the x-axis (0, 45, 90, 135 degrees).
- Flat check: c = -1: 0 differ. Rabbit 2415, Siegel 3770, Mandelbrot 2264 differ (the fold makes y -> |y| in the flat
  plane; the cut is a mirror-symmetric "double rabbit", seen in `cuts-eiffie.png`). Lift: 1.000 / 0.594.
- Door: fold (50 %), no tear. 8 directions to -x (every 45 degrees), 2 to +x: the same count as `along`.
- Against ours: for c = -1 the verdicts differ from `along` on 2.8 % of the inside. Seen: bodies with eight buds
  round each, like `along`; cuts at 0, 45, 90 are the flat basilica, the cut at 22.5 is smooth. Rabbit: one round
  lump with spiral marks (inside 0.078 of the box; one plane has 0.016).

### 8. Benesi, power 2 (Matt Benesi) — rule `benesi`
Source: `MB2/definition/fractal_benesi.cpp`, cites http://www.fractalforums.com/index.php?action=profile;u=1170

    double r1 = zz.y + zz.z;   double tp = sqrt(r1);
    if (mul < 0.0 || z.x < tp) t.x = zz.x - r1; else t.x = -zz.x + r1;     // mul = c.x
    r1 = -1.0 / tp * 2.0 * fabs(z.x);
    t.y = r1 * (zz.y - zz.z);   t.z = r1 * 2.0 * z.y * z.z;

In words: x is the real line; the part across it has its turn round the x-axis doubled and its size made 2 |x| rho.
- Flat check: c = -1 0 differ; Mandelbrot 4806, rabbit 8169 differ. For c = -1 it is the Lathe exactly (0 of 400,000
  verdicts differ from `quat3d`): rings. Rabbit: a ridged lump.

### 9. Scator "ix" (Manuel Fernandez-Guasti, imaginary scator algebra) — rule `scator_ix`
Source: `MB2/opencl/scator_power2_imaginary.cl`, cites the thread
"ix-possibly-the-holy-grail-fractal-(in-fff-lore)" under http://www.fractalforums.com/new-theories-and-research/ and
https://luz.izt.uam.mx/drupal/en/fractals/ix (that page answered 404 today).

    REAL x2 = z.x * z.x; // + 1e-030f;
    REAL newx = x2 - y2 - z2 + (y2 * z2) / x2;
    REAL newy = 2.0f * z.x * z.y * (1.0f - z2 / x2);
    REAL newz = 2.0f * z.x * z.z * (1.0f - y2 / x2);

In words (reasoned from the code): with t = y / x and s = z / x, each of the two ratios is doubled like the tangent of
an angle (t -> 2t / (1 - t^2)), and x -> x^2 (1 - t^2)(1 - s^2). Two flat rules sharing one real part; it divides by x.
- Our rule switches the commented guard `+ 1e-30` ON. Without it the flat picture of c = -1 itself is lost to rounding
  (the orbit runs into the origin, 0 / 0): measured, 2960 of 2960 flat-inside points lost.
- Flat check (with the guard): 0 differ in all four sets; exact on z = 0 and on y = 0. Lift 0.998 / 0.946.
- Door: a tear along the whole plane x = 0 (jumps 1e10), fold 50 %. No direction goes to -x except the two axes.
- Seen: spiky stars with long needles for c = -1 and for the rabbit (`all-solids-2.png`, `cuts-scator_ix.png`: off
  the two planes the cuts are feathers and hyperbola-shaped shards). Fails "no shards" badly.

### 10. Hypercomplex (4D commutative; the "bicomplex" square), cut w = 0 — rule `hyper`
Source: `MB2/definition/fractal_hypercomplex.cpp`, cites
http://www.fractalforums.com/3d-fractal-generation/true-3d-mandlebrot-type-fractal/msg7235/#msg7235

    double newx = z.x * z.x - z.y * z.y - z.z * z.z - z.w * z.w;
    double newy = 2.0 * z.x * z.y - 2.0 * z.w * z.z;
    double newz = 2.0 * z.x * z.z - 2.0 * z.y * z.w;
    double neww = 2.0 * z.x * z.w - 2.0 * z.y * z.z;

The orbit leaves 3D (w becomes -2yz); our rule carries w along and starts it at 0 (the escape test looks at x, y, z).
- Flat check: 0 differ in all four sets. Lift 1.000 / 0.991.
- Door (reasoned): it is two flat rules side by side: x + i(y - z) and x + i(y + z) each follow the flat rule, so the
  solid is two copies of the flat picture pushed straight through space, crossed. Not screened as a map of directions.
- Seen: c = -1 bodies with four buds and a bumpy, faceted skin (differs from `twoplane` on 11.8 % of the inside).
  Rabbit: three bodies in place but flaky, with loose slivers (inside 0.009 of the box, less than one plane's 0.016).

### 11-13. The polynomial triples of "another shot at the holy grail" — rules `quickdudley`, `lkmitch`, `makin3d2`
Sources: `MB2/definition/fractal_quick_dudley.cpp`, `fractal_lkmitch.cpp`, `fractal_makin3d2.cpp`, all citing
http://www.fractalforums.com/3d-fractal-generation/another-shot-at-the-holy-grail/

    Quick Dudley:  newx = x2 - 2.0 * z.y * z.z;   newy = z2 + 2.0 * z.x * z.y;   newz = y2 + 2.0 * z.x * z.z;
    Lkmitch:       newx = x2 - 2.0 * z.y * z.z;   newy = z2 + 2.0 * z.x * z.y;   newz = y2 - 2.0 * z.x * z.z;
    Makin 3D-2:    newx = x2 + 2.0 * z.y * z.z;   newy = -y2 - 2.0 * z.x * z.z;  newz = -z2 + 2.0 * z.x * z.y;

- Flat check on z = 0 fails for all three (c = -1: 506, 901, 418 of 20,000 differ; rabbit lost or changed). A search
  over all planes through 0 (`O.best_plane`: 4000 random planes, best six refined) found no plane on which any of them
  is complex squaring up to a turn and a size (best misfit 0.39, 0.71, 0.40, where 0 is exact). So no turning helps.
- Seen: blocky, slab-like shapes with shards for c = -1; rabbit dust (Quick Dudley), nothing (Lkmitch), one spindle (Makin).

### 14. Xenodreambuie, power 2 — rule `xeno_t`
Source: `MB2/definition/fractal_xenodreambuie.cpp`, cites
http://www.fractalforums.com/3d-fractal-generation/true-3d-mandlebrot-type-fractal/273/

    double th = (atan2(z.y, z.x) + betaAngleOffset) * power;
    double ph = acos(z.z / aux.r) + alphaAngleOffset;
    if (fabs(ph) > 0.5 * M_PI) ph = sign(ph) * M_PI - ph;
    ph *= power;
    z.x = rp * cos(th) * sph;  z.y = rp * sin(th) * sph;  z.z = rp * cos(ph);

Its real line is its z-axis and its best plane is its y = 0; `xeno_t` turns it (ours (x, y, z) = its (z, x, y)).
- Flat check after the turn: c = -1 0 differ; Mandelbrot 3558, rabbit 2715 (all lost), Siegel 6557 differ: in its best
  plane the map is (|a| + i|b|)^2, the Burning Ship fold, not the flat rule (reasoned from the code, and measured).
- For c = -1 it is the Lathe exactly (0 of 400,000 verdicts differ): rings. Rabbit: nothing.

### 15. Mandelcup (pupukuusikko) — rules `cup0`, `cup1`
Source: `MB2/opencl/mandelcup.cl` (and `definition/fractal_mandelcup.cpp`), "based on formula by pupukuusikko", cites
http://www.fractalforums.com/the-3d-mandelbulb/a-new-3d-mandelbrot-variant-mandelcup/

    z.x /= r;  z.y /= r;                       // "stereographic projection, modified a bit"
    z.z = (z.z / r) + Shape;
    z.x /= z.z;  z.y /= z.z;
    temp = z.x * z.x - z.y * z.y;  z.y = 2.0f * z.x * z.y;  z.x = temp;      // complex multiplication
    temp = Scale * (1.0f + (Shape * Shape));  z.x *= temp;  z.y *= temp;
    REAL mag1 = z.x * z.x + z.y * z.y - 1.0f;  REAL mag2 = 1.0f / (mag1 + 2.0f);     // inverse stereographic
    z.x = z.x * 2.0f * mag2;  z.y = z.y * 2.0f * mag2;  z.z = mag1 * mag2;
    z *= r * r;

In words: project the direction onto a plane, square the complex number there, project back, square the length.
- `cup0` (Shape 0, Scale 1; the program's own default values were not read): no plane holds the flat picture
  (c = -1: 3049 differ). Seen: a ringed, cup-like shape; rabbit dust.
- `cup1` (Shape 1, Scale 1/2, OUR choice of the two dials): then the projection is the true stereographic one and
  the formula is the lab's "Sphere inversions, one plane" followed by a flip of z. Measured: flat check 0 differ, covers
  the sphere -2.00 times with no fold besides the flip, and 0 of 400,000 verdicts differ from `oneplane` for c = -1 and
  for the rabbit. So the one-plane rule exists outside as a dial setting of the Mandelcup.

### 16. Mandelnest (Jeannot), power 2 — rule `mandelnest`
Source: `MB2/opencl/mandelnest.cl`, cites https://fractalforums.org/share-a-fractal/22/mandelbrot-3d-mandelnest/4028/
and https://www.shadertoy.com/view/4lKfzy

    z.x = (native_cos(shift + Power * acos(z.x * rN)));    // the same for z.y and z.z; then z is normalised
    z *= pow(r, Power - offset1);

For power 2 each coordinate u (of the unit direction) becomes 2 u^2 - 1.
- No plane holds the flat picture (flat check: everything differs; lift 0.000); with c in our plane nothing stays (seen: empty).

### 17. Hopfbrot, degree 2, 3D cut (Oliver Knill 2023; name by Paul Nylander) — rule `hopfcut`
Source: https://mathworld.wolfram.com/Hopfbrot.html and https://arxiv.org/abs/2305.17848 . A point of 4D space is
written r U(t1, t2, phi) = r (cos phi cos t1, cos phi sin t1, sin phi cos t2, sin phi sin t2); the power is
r^d U(d t1, d t2, d phi); c is added. It lives in 4D. MathWorld: the cut phi = 0 is the Mandelbrot set, the cuts
t1 = 0 or t2 = 0 are Mandelbulbs.
- Our rule is the cut "fourth coordinate 0" for d = 2 (worked out from the definition, not quoted code): it is the
  Mandelbulb power 2 applied to (x, y, |z|). Measured: flat check 0 differ, and 0 of 400,000 verdicts differ from `mb2`
  for c = -1 and for the rabbit. Nothing new in 3D.

## B. Not "square, then add c" in our sense: one line each, not tested

- Mandelbox (Tom Lowe): box fold, sphere fold, scale, add c. No square.
- Msltoe toroidal bulb (`MB2/definition/fractal_msltoe_toroidal.cpp`, thread theory/toroidal-coordinates/msg9428): a
  power taken about a ring of radius 0.5, default powers 4, 8, 9; not a square about a point.
- Riemann sphere Msltoe (`fractal_riemann_sphere_msltoe.cpp`, thread the-3d-mandelbulb/riemann-fractals/msg33500):
  project the direction stereographically, replace the two plane coordinates by |sin(pi s)|, |sin(pi t)|, project back; no square.
- Riemann sphere Msltoe V1 and "Riemann bulb Msltoe Mod2" (threads "revisiting the Riemann sphere (again)" and "another
  way to make my Riemann sphere 'bulb' using a conformal transformation"): inversion plus a periodic tiling; no square.
- Hobold's "Riemandelettuce without trigonometry" (`opencl/riemann_sphere_hobold_pow4.cl`,
  fractalforums.org .../riemandelettuce-without-trigonometry/2996/msg16097): two half-angle doublings on the sphere;
  the source has powers 4 and 8 only.
- Msltoe Donut (`fractal_msltoe_donut.cpp`): sectors round a ring and an inversion; no square.
- Aexion's Quadray sets (`fractal_aexion.cpp`, thread the-3d-mandelbulb/quadray-sets/msg31458): the point is turned into
  four coordinates, c is made from their absolute values, and the square is a 4D one; not a 3D square plus c.
- Ides / Ides2 (`fractal_ides.cpp`, formula by Trafassel): new y is a multiple of x y z; not a square.
- Mandelbulb "pow2 v1" (`opencl/mandelbulb_pow2_v1.cl`, "based on pow2 code from David Makin"): formula 1 about
  another axis with sign switches; not tested separately.

## C. Could not be pinned down today (forum database down), so not tested

- Paul Nylander ("bugman"), "3D Mandelbrot formula based on the Hopf map" (2009):
  https://www.fractalforums.com/theory/3d-mandelbrot-formula-based-on-the-hopf-map/ . The search tool reports that a
  2017 reply there proposes the 4D "Hopfbrot"; formula 17 is that object as MathWorld defines it.
- "3D Mandelbrot formula based on rotation away from azimuthal axis":
  https://www.fractalforums.com/theory/3d-mandelbrot-formula-based-on-rotation-away-from-azimuthal-axis/
- "Summary of 3D Mandelbrot set formulas": https://www.fractalforums.com/theory/summary-of-3d-mandelbrot-set-formulas/
- Nylander's own page http://www.bugman123.com/Hypercomplex/index.html (certificate expired).

## D. What the community itself says about the goal (short, through the fetch tool)

- Daniel White's Mandelbulb page (https://www.skytopia.com/project/fractal/mandelbulb.html) calls the search "the Holy
  Grail of fractals" and says of the angle-doubling shapes that they are not what he would call a 3D Mandelbrot; what he
  hoped for is an apple-core body with spheres round it and further spheres round those.
- Wikipedia, "Mandelbulb" (https://en.wikipedia.org/wiki/Mandelbulb): "A canonical 3-dimensional Mandelbrot set does not exist".
- AMS Notices, April 2022 (https://www.ams.org/journals/notices/202204/rnoti-p624.pdf; the PDF refused the fetch, the
  search tool reports it): Tom Lowe is quoted as saying nothing nearly as significant as the Mandelbrot set has been found in 3D.
