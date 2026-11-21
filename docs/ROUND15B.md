# Round 15B: the pillow rule in closed form, and what the power does in 3D

Read `docs/ROUND15.md` first (the square pillow idea, the house rules, the report format). This file adds a
second version of the same idea and the user's newest words. Round 15's two engineers (entry, study) are
still at work on the first version; do not touch their files (`src/js/10-approaches.js`, `out/r15/entry/`,
`out/r15/study/`).

## What the user said after seeing round 14 (2026-11-18, verbatim)

> ok the kleinian squaring approach seems wrong - z=0 is not correct, the easiest sign. The other one is that
> there is no 3d relationship with the number of bulbs to the power, but only to the number of planes. The
> original basilica julia set that was inspired from this paper is way more intuitive as the correct one, but I
> know extending it to the mandelbrot is different. So I need you to try again, and really believe in yourself
> - the number of planes should not decide the inherent geometry of the fractal in 3d. It should be some
> representation of what is happening in the 2d mandelbrot - with respect to what happens hidden in the 3d -
> extended to 3d (with respect to what happens hidden in the 4d), and it shouldn't look like any of the other
> approaches of disconnected stuff and wrong z=0 and simply rotating the fractal around the x-axis or however
> it is

So the rule must have: the slice at z = 0 exactly the flat set; a number of bodies that comes from the power
(as the flat set of z^n has n - 1 lobes), never from a "planes" dial; no shards; no plain rings. Their picture
of "right" is the paper's 3D basilica: a body with smaller round bodies on it in more than one direction.

## The rule in closed form (reference: `out/me/r15/shadow_ref.py`, checked for n = 2..5; read and run it)

In 4D, written as two complex numbers of the same length rho: z1 = rho e^(ia), z2 = rho e^(ib). The 4D rule is
`(z1, z2) -> (conj(z1)^n, z2^n)`: both turning circles are turned n times as far, one of them backwards. A 3D
point stands for the pair together with its mirror pair (conj z1, conj z2); the pairs of angles (a, b) form a
doughnut, and folding it by (a, b) ~ (-a, -b) gives the pillow of round 15 (s = a / 2 pi, t = b / 2 pi). Three
numbers survive the folding: `x1 = Re z1, x2 = Re z2, w = Im z1 Im z2 / rho`, tied by
`w^2 rho^2 = (rho^2 - x1^2)(rho^2 - x2^2)`. In them the rule is polynomial (Chebyshev T_n, U_(n-1)):

    x1' = rho^n T_n(x1/rho),  x2' = rho^n T_n(x2/rho),  w' = -rho^(n-1) w U_(n-1)(x1/rho) U_(n-1)(x2/rho),  rho' = rho^n

The belt b0 = 2 pi/(n + 1) (x2 = c0 rho, c0 = cos b0, s0 = sin b0) returns to itself with a -> n a. Lab
coordinates lay that belt on the plane Z = 0, angle-true there:

    X = x1,   Y = s0 rho w / (rho - c0 x2),   Z = -(x2 - c0 rho) / s0
    back:  x2 = c0 rho - s0 Z,  w = Y (rho - c0 x2) / (s0 rho),
           rho = the root of  Y^2 (rho - c0 x2)^2 / s0^2 = (rho^2 - X^2)(rho^2 - x2^2)  with |X| <= rho, |x2| <= rho

For n = 2 this is `F(X, Y, Z) = (2 X^2 - rho^2, -4 X Y x2 (2 rho + x2) / (rho^2 + 2 x2^2), (2/sqrt3)(rho^2/2 - 2 x2^2))`
with `x2 = -(sqrt3/2) Z - rho/2`; on Z = 0, rho = sqrt(X^2 + Y^2) and F is (X^2 - Y^2, 2XY, 0).

Measured (orchestrator): rule against plain angles 2e-15 to 2e-14; plane against z^n 1e-15 to 7e-15; no jump
(largest jump shrinks tenfold with a tenfold smaller step); sideways stretch next to the plane exactly n with
the side flipped; rho on the unit sphere runs from 0.50 to 1.73 at n = 2 (so "length" here is rho, not the
plain length: the rule sends rho to rho^n; a point escapes when rho grows without end, and the plain length is
within those factors of rho). This is the SAME direction dynamics as round 15's entry but another way of laying
the pillow on space, so the solids will differ off the plane. Nobody has drawn it yet.

Known in advance (reasoned): the layout depends on the power (the belt moves), so each power has its own
formulas; the rule is lopsided above and below the plane for even n and mirror-symmetric in Z for n = 3; the
plane Y = 0 holds all four corner directions of the pillow and is where to expect spikes rather than bodies.

## shadow: a private entry drawn by the lab's own renderer (`out/r15/shadow/`)

You may NOT edit `src/js/10-approaches.js` (the round-15 entry engineer is in it). Work on a private copy:
copy `base14b/js/10-approaches.js` to `out/r15/shadow/10-approaches.js`, add your entry there, and build with
`python build.py --name r15-shadow --base base14b --swap js/10-approaches.js=out/r15/shadow/10-approaches.js`.
Put everything you add between the marks `// R15B-BEGIN` and `// R15B-END` (one block for the code and
texts, one line for the group, one for the entry in APPROACHES), so the orchestrator can merge it.

- id `pillow4d`, name "Pillow from 4D (closed form)", group `{ id: 'pillow', title: 'Doubling on a pillow grid' }`
  (the other engineer adds the same group with the entry `sqpillow`; use exactly this id and title).
- Shader (`mul`, `pw`, `sqr`, `cmap`) and `MATH.pillow4d`, whole powers n >= 2 (nearest whole power for
  others, said in the text). The gauge rho: a quartic; closed form or a few safeguarded Newton steps from a
  safe start, checked against the reference's bisection. Exact on Z = 0 with output Z exactly 0. Look at how
  the round-14 entries (`kleinsq`, `rotorframe`) are built and how the orbit code estimates distance for a
  rule that does not keep shapes. Note that this rule's natural length is rho, not |v|: decide, from how the
  shader's escape test and distance estimate work, whether that needs care, and say what you did.
- **Pictures are the point**, and the power is the question: a contact sheet
  `out/r15/shadow/sheet-pillow4d.png` with, for n = 2, 3, 4, 5: the Mandelbrot solid (opening view, from
  above, from below, along the x-axis) and its cut at z = 0; for n = 2: Julia sets c = -1, the rabbit
  (-0.12, 0.74, 0), c = (-1, 0.15, 0.1), c = (0.3, 0, 0); and close-ups at 3 depths of a body's surface and of
  a place where two bodies meet. Count, by eye and say so, how the number of bodies round the main body
  changes with n in the plane and off it.
- Checks by numbers: MATH against `out/me/r15/shadow_ref.py` (export points, aim 1e-9); shader against MATH;
  the page's Mandelbrot slice at z = 0 against the flat set for n = 2 and 3; how far the drawn skin stands
  from brute-force membership. `tools/smoke-v14.json` once on your page.
- Texts from your own numbers and pictures, in plain words. Do not oversell.

Time: aim for 75 minutes, stop at 95.

## powers: what the power does in 3D, in numbers and voxels (`out/r15/powers/`)

Stand-alone numpy, nothing in `src/`. Start from `out/me/r15/shadow_ref.py` (make the gauge fast first: a
safeguarded vectorised Newton or the quartic in closed form, checked against the bisection to 1e-10);
`out/r14/turns/turns.py` has a voxel renderer, cuts and a sheet maker; `out/me/r15/first_look.py` shows a
minimal voxel run. Questions, in order of weight:

1. **Bodies and the power.** For n = 2, 3, 4, 5: the Mandelbrot solid and one Julia set with c on the
   x-axis inside the period-2 body of that power's flat set. How many bodies sit round the main body in the
   plane (flat sets: n - 1 lobes for the Mandelbrot set) and how many off the plane? Is there a clear count
   that follows the power (n - 1, n + 1, n^2 - 1, ...)? Views from above, below and along the axes; cuts at
   z = 0, y = 0, x = const. Label and count connected pieces at a fine grid and say whether the sets are in
   one piece when the flat set is.
2. **Bodies or lumps, and detail at smaller sizes** for n = 2 at c = -1 and the rabbit, as in round 15's
   study questions 1 and 2, but for this layout (zoomed boxes at 3 sizes).
3. **Shapes under repetition:** the ratio of the largest to the smallest stretch of F^k (no c), k = 1..6, at
   random points (median, 99 %), measured in the plain length. Compare with `out/me/r15/pillow_ref.py` (the
   other layout), with Sphere inversions, one plane (`turns.E1`) and with the Mandelbulb at power 2.
4. **Which layout is nearer to round bodies:** this one or `pillow_ref.py`? Same c, same views, side by side.
5. The lopsidedness: how different are the halves above and below the plane at n = 2, 4 (volumes, heights),
   and is n = 3 mirror-symmetric to rounding?

Deliver `out/r15/powers/sheet-for-user.png`: plain-word labels; the pictures that answer 1 and 2 first; a
short note of what came out. And a blunt verdict against the user's own words above: exact slice (yes or
no), bodies from the power (yes or no, with the count), shards or one piece, rings or not, and how near to
"a body with smaller round bodies on it in more than one direction".

Time: aim for 65 minutes, stop at 85.
