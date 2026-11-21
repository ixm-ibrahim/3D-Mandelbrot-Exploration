# Round 25: fresh eyes. Inflated by sphere inversions, bulbs all over by themselves, quaternions somewhere

Seven people start from seven different places and each builds and DRAWS at least one rule. One more person's only
job is to find a hole in the "wall" of section 3. Then a judge. Read `docs/ROUND23.md` sections 4 and 5 (how to
write and draw for this user; house rules): they hold unchanged. Write only inside `out/r25/<your name>/`. Your report
is `out/r25/<your name>/NOTES.md` (never a file called report.md). No work in `src/`, no browser. Write Python files
with the Write tool. Start every shell command with `cd` to the project root and run
`PYTHONIOENCODING=utf-8 python -W ignore ...`. Keep every run under 8 minutes (fewer blocks, fewer steps, or split);
long jobs in the background. Seven of you share one machine: be frugal (nd <= 200 for a look, more only for a claim).

## 1. What the user wants (verbatim)

The newest message, after three more rules of mine failed:

> none of these new tries are working. we're looking for an inflated version of the 2d (so spherical inversions
> have to be involved somehow) but the bulbs occur all over those 3d surfaces naturally, not chosen. and quaterions
> I imagine have to be involved somehow, if not fully, so the resulting object is not stretched or otherwise
> revealing the limitations of 3d rotations

Earlier, the same wish in other words:

> the original sphere inversion 2-plane and along approaches have the best results, but in different things it would
> be awesome to get that ironed out. Like the sphere inversion's blown up shapes look intuitive, like the 2d slices'
> "inside" parts we would assume as having some 3d analog of it, with bulbs (or whatever feature that fractal has
> ...) on it not just on the axis planes but everywhere in the same pattern, like the 2d spacing being done in 3d,
> not being stretched or warped or whatever. with the limitations of 3d rotations, I would imagine that this has to
> happen with quaternion rotations somehow (... the 3d versions of daudy rabbits tend to look like these weird
> un-rabbity shapes, rather than recognizable bulbs and insides ... the along-once-then-plane approach gives the
> closest thing I've seen for the rabbit, but it's still wrong and the approach seems arbitrarily wrong too)

Their standing tests, each a hard one:
1. The cut z = 0 is exactly the flat picture of z -> z^2 + c, for every c ("z=0 is not correct, the easiest sign").
2. The number of bulbs follows from the power; it never comes from a number of planes or any dial we pick.
3. No shards, no smear, no rings (the flat picture spun round an axis).
4. Their picture of "right": the paper's 3D basilica (Kucera, `notes/paper-kucera.txt`, Figure 4): a blown-up body
   with smaller round bodies on it in more than one direction. For EVERY c, the rabbit included.
5. A principled carry-over, "elegant, repeatable with different equations" (other powers).
They are not a mathematician and judge by pictures of real shapes. They notice lopsidedness at once.

## 2. Tools

`out/r21/lib/mem.py` (`sys.path.insert(0, 'out/r21/lib'); import mem as M`):
- `M.fixed(F, name, label)` wraps a function `F(x, y, z) -> (X, Y, Z)` on numpy arrays (the "square"; the library
  adds c after it). NaN or a far point counts as escaped.
- `M.stay(rule, x, y, z, cx, cy, cz, steps)` number of steps each orbit stays; `M.flat_check(rule, n=20000, steps=60)`
  counts verdicts on the flat plane that differ from the true complex orbit (must be 0 for all four sets).
- `M.cut_axis(rule, angle, w, h, steps, c=c)` a cut through the x-axis turned by `angle` (0 = flat, 90 = upright);
  `M.shade(n, steps)`; `M.julia_sheet(rules, path, sets=[(label, c), ...], w, h, nd, steps, cam, title)` rough solids,
  one row per rule (`cam` (0.45, 0.5, 1) = front, (0.2, 1, 0.35) = from above; nd = depth blocks, 230 takes 1 to 4
  minutes per rule and set); `M.bench('oneplane' | 'twoplane' | 'along')`; `M.RABBIT`, `M.SIEGEL`.
- Rules with memory or rules that look at c: see `class Rule` (init, step) in mem.py and `out/r21/lib/` users.
- Worked examples to copy from: `out/r25/me/natural.py`, `out/r24/me/mfold.py`, `out/r24/me/tri.py`, `out/r24/me/push.py`.
The four standard sets: c = -1 (basilica), the rabbit, c = -0.75, the Siegel disc. Add what your idea needs.
Rough solids decide; cuts alone do not (round 23 was fooled by clean cuts of a rule whose solid was crusted).

## 3. The wall (attack it; the section `wall` exists for that)

Every rule so far has the form "v -> F(v) + c with one fixed F". Facts, each marked:

(W-a) THEOREM (round 23, `out/r23/outside2/verdicts.md`). If F is exact on the flat plane (test 1) and treats every
direction round the upright axis alike, as z^2 does (turn the point by an angle a about the upright axis and its
square turns by 2a: "nothing chosen"), then F sends circles of latitude to circles of latitude, each wound twice,
and off the flat picture it can do only one of four things: nothing new (bodies only round the flat picture: the
one-plane rule, the Douady-Earle extension), a FOLD (latitude turns back: measured tonight, every body is smeared
along an arc into a lump, `out/r24/me/conefold.py`), a CRUSHED circle (a whole circle of directions sent to one
direction: rings, or pillars: the fitted-inversion rule below), or a TEAR (shards).
(W-b) THEOREM. A second flat plane holding a true copy of the flat picture exists only for c on the x-axis. That is
the whole secret of "two planes" and "along", and why they fail for the rabbit.
(W-c) REASONED, standard. 3D rotations cannot be doubled consistently: turning by A then B, each twice, is not the
same as (A then B) twice. In the flat plane it is. The quaternion square q^2 is consistent only with spinning about
the real axis, which is why it draws the flat picture spun round the x-axis (measured: rings for real c, the
"un-rabbity" taffy for the rabbit).
(W-d) REASONED, standard (Gauss-Bonnet). A doubling pattern with the same spacing everywhere cannot be wrapped round
a ball-like surface without special points: at least 3 corners (two flat triangles glued: `out/r24/me/tri.py`) or
4 (the square pillow, Mayer's quasiregular power map). A doughnut needs none.
(W-e) MEASURED tonight (`out/r24/me/push.py`). Where bodies meet (a repelling cycle of the flat rule), a point lifted
off the flat plane is either pushed further away (bodies stay apart) or held (bodies grow into one lump). One plane
pushes evenly at every longitude. Every rule with extra copies that I built pushes unevenly, and each one makes a
lump at the c whose meeting point faces its weak side.
(W-f) MEASURED (rounds 23, 24). Squeeze multiplies down the tree of bodies: smooth for one step, blades after three,
a crust at every step. Only sphere inversions keep shapes in 3D (Liouville), and no chain of inversions is z^2.

What this adds up to (my reading, NOT proven as a whole): exact flat picture + nothing chosen + separate round bulbs
off the flat picture cannot all be had from one fixed F. Doors that are not closed by any proof: (i) F may depend on
c or on the orbit's own history, so that the flat picture does the choosing; (ii) F need not be "length squared
times a map of directions"; (iii) the object need not come from iterating a 3D map at all (limit sets of groups or
of inverse branches; things built from the flat picture's own structure); (iv) 4D with a better way down to 3D than
a flat cut.

## 4. Everything tried, with its verdict (do not rebuild these; build on them)

Lab entries (`src/js/10-approaches.js`) and bench rules (`out/r16/bench/rules.py`, `out/r21/lib/mem.py`):
- One plane (longitude doubled, Mercator latitude doubled; = the published "product extension"): exact, clean
  blown-up bodies, buds only round the flat picture. The user's baseline for "inflated".
- Two planes (fold across the planes |y| = |z|, then one plane): c = -1 clean with buds in four directions; shards
  for the rabbit. Along (a smooth 8-fold fold about the x-axis): c = -1 "almost exactly as people envision" (the
  user); the rabbit one lump. Away, Wind then square (k = 3): worse.
- Along once / Pulled plane (rules with memory): clean rabbit, a few extra bodies, "arbitrary" / "too simplistic".
- Quaternion square (Lathe), 4D slices, rotor, rotor with a frame: rings or taffy; tears.
- Kleinian squaring (the paper's piecewise sphere inversions on arcs of the unit circle, one and two planes): the
  flat cut is only a cousin of the flat picture (the paper's map is only topologically like z^2: its conjugacy is a
  Minkowski-question-mark kind of function); rejected by the user for that and for "number of planes".
- Square pillow (Mayer's power map with the flat circle as a belt), triangle pillow (first prototype, radial
  layout; tonight `tri.py`, kite layout): exact; c = -1 fused along the whole x-axis by its nature (three branch
  directions lie ON the flat circle at 60 / 180 / 300); rabbit rough; spikes at corners.
- Cone rules R(w) = (w^m + t)/(w^(m-2)(1 + t w^m)) blended into w^2 (m = 3: lopsided; m = 4, 6: even but hairy
  stars and a rough lump for the rabbit, `out/r24/me/mfold-solids-a.png`); "welded cones" (round 23): smooth for
  one step, crust at every step.
- Cone-fold (latitude folded back, then one plane): lumps. Lens (one plane with an arc blown up): blades.
- Tonight (`out/r25/me/natural.py`, `natural-cuts.png`): `fit` = at every flat point z0 the one chain of
  inversions that agrees with z^2 there in place, speed and bend (the Ahlfors-Weill extension), circles made
  spheres: square(z0, t) = (z0^2 (4r^2 - 3t^2)/(4r^2 + t^2), height 8 t r^3/(4r^2 + t^2)), r = |z0|. Exact, nothing
  chosen, and useless: endless pillars above and below every body. `mid s` = the quaternion slerp between the
  one-plane square and the quaternion square: lumps, or nothing at all, in the upright cut.
- 17 formulas of the fractal community (`out/r23/outside1/formulas.md`): Mandelbulb power 2, Bristorbrot, scator,
  hypercomplex, Msltoe's Sym2 / Sym3 (= the two-planes look), Eiffie (= the along look), ...: none passes.
The paper itself says its truly 3D construction is "so far unfortunately limited to c in R" and omits it.

## 5. The eight sections

Each of the first seven: understand your corner properly (read, search the web if it helps, think), then BUILD the
most natural rule or object it offers, run the flat check, draw rough solids (both eyes) of c = -1 and the rabbit
at least, and say in six plain lines what it gives and which of the user's tests it fails. A rule that fails is a
full result if you say exactly why. Do not polish a failing rule; try the next most natural one from your corner
(up to three). Deliver `NOTES.md`, `sheet.png` (+ `sheet-top.png`), `best.py` with `rule()`.

- `vahlen` : Sphere inversions of 3D space ARE quaternion arithmetic: every chain of sphere inversions is
  v -> (a v + b)(c v + d)^-1 with quaternions a, b, c, d acting on v = x + y i + z j (Vahlen, Ahlfors). Start there.
  What is the natural "square" in that language? Candidates to work out and test: squaring the matrix instead of
  the point; all maps v -> v a v, v a v*, and products with the other involutions of the quaternions that send
  x + y i + z j to itself and are z^2 on z = 0 (classify them: it is a finite list of quadratic maps); the square of
  a spinor (a point of space as q i q*, the Hopf map) with every natural rule for the leftover phase.
- `klein` : the paper's own road, done properly. Sullivan's dictionary; the paper's group with generators g1, g2
  and the third generator g3 in the upright plane. What exactly is its flat cut, how far is it from the flat
  picture (a number), and is there any honest repair? What is the "not chosen" group: one that contains the flat
  group and acts on the whole sphere by its own symmetry (the Picard group and Schmidt's Farey circles and
  triangles; the Eisenstein version; the Hurwitz quaternions one dimension up)? Matings of the modular group with
  z^2 + c (Bullett, Penrose). Draw the best Kleinian-kind object for c = -1 and say what plays the role of the
  rabbit. If the flat cut is not exact, say by how much and whether the eye could tell.
- `torus` : even doubling without any special point lives on a doughnut, and the natural doughnut is the Clifford
  torus in the sphere of unit quaternions, brought to 3D by one sphere inversion (stereographic view). Hopf
  coordinates, toroidal coordinates, the book of spheres through the unit circle. Can a rule be built on that whose
  flat cut is exact? I found two obstacles (doubling the angle round the unit circle sends the inside of the unit
  circle to the outside; rules built page by page on spheres through the unit circle have no escape to infinity
  off the flat plane). Check them, then look for the version that survives.
- `fromc` : door (i). Rules in which nothing is chosen by us because the flat picture chooses: the rule may look at
  c (the flat fixed points, the period, the meeting point's direction) or carry a quaternion (a frame) along the
  orbit that is turned by the same turns the point makes. Must be exact on the flat plane for every c and must say
  what it does for c off the flat plane (the Mandelbrot solid). Read how "along once" and "Pulled plane" carry
  state (`out/r21/lib/mem.py`, `out/r22/`), then find the least arbitrary rule of this kind.
- `inverse` : door (iii). Build the 3D object backwards: the flat Julia set is the limit of the two square roots
  z -> +-sqrt(z - c) applied over and over. In 3D a point has more natural roots (two for one plane; a whole
  circle of quaternion roots for a point on the negative real axis). Which finite, natural sets of 3D roots give a
  limit set with bulbs all over, and is its flat cut the flat Julia set? Draw limit sets by inverse iteration
  (points) and, where a forward rule exists, as solids.
- `pillow` : the even-spacing family done as well as it can be (Lattes maps; Mayer; Zorich). It is the one family
  where squeeze does not multiply, and its special points are as few as a ball allows. Is the fused x-axis really
  forced for every pillow, every invariant circle and every layout (triangle (3,3,3), square (2,2,2,2), (2,4,4),
  (2,3,6); mirror versions)? If one escapes, build it. If none does, say precisely why, and draw the best even-
  spacing rabbit there is.
- `fourd` : door (iv). Do it where it is natural, in 4D with quaternions (or pairs of complex numbers), and come
  down to 3D otherwise than by a flat cut: stereographic views, shadows, cuts by spheres through the flat plane,
  the set of 3D points whose WHOLE circle of lifts stays, or any lift at all. The flat plane must come out exact.
  The plain quaternion and bicomplex rules are known to be trivial in 4D (a spun copy; a product of two flat
  pictures): look for a 4D rule that is not, or for a way down that hides it.
- `wall` : find the hole. List every assumption behind section 3 and behind my "adds up to". For each door (i) to
  (iv) say whether it is really open, and name the most promising concrete construction behind it (give formulas).
  Check (W-a) yourself. Check (W-d) and (W-e). Then write the honest statement for the user: at most eight short
  plain lines saying what cannot be had together, what can, and what the paper's author ran into. No mathematics
  words (ROUND23.md section 4).

- `judge` (last): `out/r25/judge/ANSWERS.md`. You did not do the work. Re-measure the best two or three candidates
  with your own scripts (flat check; solids from two eyes at finer blocks and more steps; c moved 3 degrees out of
  the flat plane; lopsidedness as a number), try to make them fail, and answer in short numbered plain lines:
  (1) Did anyone find a rule or an object that is inflated, has bulbs all over by themselves, and is not stretched?
  (2) If not: what is the nearest thing, and exactly which of the user's tests does it give up?
  (3) Does the wall stand? What is the honest sentence about it?
  (4) What should be tried next, if anything?
  Lists "may be told" and "may NOT be told". At most three pictures of real shapes for the user (captions of at
  most two short sentences), the best candidate beside two planes and along for c = -1 and beside "along once"
  for the rabbit.
