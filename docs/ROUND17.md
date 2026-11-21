# Round 17: back to the basilica with another rule, and a hard look at what can exist

Read this whole file, then your own section. `docs/ROUND16.md` has the protocol in full and the house rules;
`out/r16/bench/README.md` says how the bench works. Everything is under the project root (your working directory).

## What the user asked for (verbatim; these are the tests, do not soften them)

2026-11-18, after the round with "Kleinian squaring":

> ok the kleinian squaring approach seems wrong - z=0 is not correct, the easiest sign. The other one is that
> there is no 3d relationship with the number of bulbs to the power, but only to the number of planes. The
> original basilica julia set that was inspired from this paper is way more intuitive as the correct one, but I
> know extending it to the mandelbrot is different. So I need you to try again, and really believe in yourself
> - the number of planes should not decide the inherent geometry of the fractal in 3d. It should be some
> representation of what is happening in the 2d mandelbrot - with respect to what happens hidden in the 3d -
> extended to 3d (with respect to what happens hidden in the 4d), and it shouldn't look like any of the other
> approaches of disconnected stuff and wrong z=0 and simply rotating the fractal around the x-axis or however
> it is

Later the same day, the order of work:

> ok well n=3+ is not good enough. if julia is easier, then start with that basilica and don't attempt a
> mandelrbot until the julia passes, and if the mandelbrot fails, go back to another julia. I gave a bunch of
> constraints in my last message so don't forget about those, and what we've been trying to go for this whole
> time. and at higher n anyway, it looks to smear instead of looking how I would expect.

The user is not a mathematician and judges by pictures. Earlier standing wishes: the cut at z = 0 must be exactly
the flat set; the goal is a 3D Mandelbrot solid in the spirit of the 3D basilica of Kučera's paper
(`notes/paper-kucera.txt`, Figure 4: a body with smaller round bodies on it in more than one direction).

## The record so far (power 2; "basilica" = Julia set of c = (-1, 0, 0))

| rule | basilica | Mandelbrot solid |
|---|---|---|
| Two planes, nearest plane (`twoplane`) | the look the user liked; tears for c off the x-axis | crossed flat slabs with fins (rough picture) |
| Sphere inversions, one plane (`oneplane`) | clean, but buds only in the flat plane | a flat slab: thin lens buds on the rim of the flat plane |
| Quaternion square (`lathe`) | rings | rings |
| Square pillow, Mandelbulb | joined or smeared | rocks with fins |
| Turning plane, away (`away`) | 4 buds, but ribbed, whiskers | (two thin crossed leaves; not judged) |
| Turning plane, along (`along`) | passes the bench's eight tests | FAILS: lumpy rock, ridges, period-2 body fused on |

Pictures: `out/r16/bench/sheet-for-user.png` (bench), `out/me/v16/basilica-check.png` (lab renders and close
skin), `out/me/r16/refsolids-161.png` (Mandelbrot solids of five rules side by side).

**New since the bench was built (orchestrator, measured):** the bench's voxels are too coarse to see hair.
`python out/me/r16/closecut.py <rule>` cuts the basilica through the x-axis between the special planes, point by
point, at three widths, and prints a hair number per tile (loose or spiky pixels per pixel of skin line).
Calibration: `twoplane` worst 0.04, `oneplane` 0.00 (clean by eye); `along` 3.1 (thin fins, tufts of hair,
droplets by eye), `away` 17, `wind2` 10.6. So `along` does NOT have a clean skin; its bench pass was flattering.
**From now on stage 1 = the bench's eight tests AND closecut worst <= 0.3 AND your own eye on
`out/me/r16/closecut-<rule>.png`.** closecut takes a minute; use it as the first screen.

## Three claims by the orchestrator (reasoned; two agents are asked to break them)

- **C1, the invariant line.** Let a rule be exact on the flat plane (there it is z -> z^2). If for some c in the
  flat plane a second plane P2 (crossing the flat plane in a line L) is mapped into itself by v -> F(v) + c, then
  L is mapped into itself by z -> z^2 + c, and that forces L to be the real axis and c to be real. So a second
  plane carrying its own flat picture can exist only for c on the x-axis. This matches the paper's own sentence:
  the truly 3D construction "is unfortunately limited to c in R". Consequence claimed: in a Mandelbrot solid,
  every c off the x-axis has a Julia set with at most one such plane.
- **C2, no even doubling with two planes.** For a continuous rule that is exact on z = 0 and y = 0 and commutes
  with the mirrors y -> -y and z -> -z: go once round the negative x-axis on a small circle; the sideways part of
  the answer must turn 1 + 4k times (k whole). k = 0 is `along` (lathe-like there; measured 39 % of directions
  land mirror-reversed, the rule folds space over); k = -1 is `away` (directions wrapped four times, stretch up to
  9.9 where the plane gives 2). Claimed: every such rule either folds or over-wraps somewhere, and that is where
  hair (folds) or whiskers (over-stretch) come from. Kaleidoscope folds ("fold onto the wedge round the flat
  plane, then the one-plane rule") were checked by hand: they either tear on y = 0 or lose the exact cut.
- **C3, how buds can sit on a Mandelbrot solid.** The skin of the main body is where the resting point of
  v -> F(v) + c stops attracting: some eigenvalue of its 3 x 3 derivative reaches size 1. A period-q bud attaches
  where a complex pair is exp(+-2 pi i p / q): on a two-dimensional skin that is a curve, so the bud is a ridge or
  a ring. Where a real eigenvalue reaches -1 the period-2 body attaches along a whole patch (fused; measured on
  `along`: M4). A bud touching at ONE point needs all three sizes to reach 1 together; that happens on the rim of
  an exact plane on which the rule keeps angles in 3D (sideways stretch = in-plane stretch, as in `oneplane`).
  Claimed: round buds touching at points can only sit in rows on such planes (so "the number of planes" counts the
  rows), and anything else is rings, ridges or fused lumps. A rule keeping angles everywhere cannot double (in
  3D only sphere inversions and their compositions keep angles everywhere).

If C1 to C3 hold, a Mandelbrot solid with round buds all over, touching at points, cannot come from a smooth
rule, and the honest target becomes the best member of one of three kinds: rows of buds on a few planes with a
full body between (nobody has a full body yet), rings, or ridges. The user has NOT accepted this; they asked for
another try. So this round does both: try again properly, and test the claims.

## House rules

- Nothing in `src/`, `base*/`, `dist/` or `squaring-lab.html`; nothing is published. Work only in your own folder
  `out/r17/<your section name>/`. Do not edit `out/r16/bench/*.py` (ask for a change in your report instead).
- Bench rules: put them in `out/r17/<name>/myrules.py` as `RULES = {'<prefix>_<short>': (function, 'Plain label', '')}`
  with functions `F(x, y, z) -> (X, Y, Z)` on numpy arrays, no c added, |F(v)| = |v|^2. The bench loads every such
  file. Use your prefix on every rule name (given in your section) so that result files do not collide.
- Commands (from the project root, `PYTHONIOENCODING=utf-8`; several may run at once, one core each):
  `python out/me/r16/closecut.py <rule>`; `python out/r16/bench/bench.py stage1 <rule>` (about 100 s);
  `... lights <rule>` and `... stage2 <rule>` (the bench refuses these unless its stage 1 passed; do not get
  round that for a new rule, and do not run them at all for a rule whose closecut fails).
- The order of work is the user's: basilica first. A rule's Mandelbrot solid may be drawn ONLY after its basilica
  passed stage 1 as defined above. Between the two sits **stage 1b** (still Julia, added by the orchestrator so
  that bad rules fail early): `lights` for the rule; the rabbit c = (-0.122561, 0.744862, 0) must be one piece,
  not a swollen lump and not shards. `oneplane` is the yardstick for "not worse"; you may compute its rabbit by
  calling the bench's functions directly for that one known rule.
- Report in plain words with numbers; say "measured", "seen in the picture" or "reasoned" for every claim. Do not
  oversell: a rule fails a test or passes it. Time: aim for 70 minutes, stop at 90. One line in
  `notes/_state.md` is NOT yours to write.

## profiles (prefix `p_`): the reference-plane family, done properly

`along` and `away` are two members of one family: F(v) = Rot_x(psi) P(Rot_x(-psi) v) with P the one-plane square
and psi a function of the point (see `out/me/r16/scout3.py`). Explore it as a family, with stage 2 in mind:

1. psi may depend on the angle phi round the x-axis AND on how far the point stands from the x-axis
   (t = rho / r, 0 on the axis, 1 on the plane x = 0). Orchestrator's first candidates: `psi = phi - a(t) sin(4 phi)/4`
   with a(0) = 0 (pure lathe at the axis, which is smooth there and makes the bodies ON the axis balls touching
   at points, as in the lathe's Mandelbrot solid) rising to a(1) = 1; and profiles whose flat spots are narrower or
   wider and whose crossing between the planes is gentler (slope just above 1 instead of 2).
2. For each candidate: closecut first, then stage 1, then 1b, then stage 2 if and only if allowed.
3. Say what limits the family: which test each member fails and why, in terms a non-mathematician can follow.
4. If a member passes stage 1 and 1b, run stage 2 and say bluntly what its Mandelbrot solid is.

## blends (prefix `b_`): rules that are not a turned one-plane rule

Free design, same tests. Starting points (orchestrator, untested): (a) the two one-plane answers P1(v) (about
z = 0) and P2(v) (about y = 0) averaged with weights that are 1 and 0 on the planes, then brought back to length
|v|^2 (the two answers are never opposite off the x-axis, checked by hand, so the average never vanishes; weights
y^2 / (y^2 + z^2) and z^2 / (y^2 + z^2), or steeper); the same with the lathe mixed in near the x-axis; (b) a
turn on the sphere of directions from P1's answer to P2's answer (great-circle blend); (c) anything of your own
that keeps the cut z = 0 exact, has no tear, and gives the basilica buds in more than one direction. Think about
WHY the two-plane basilica has a clean skin (each half keeps angles on the sphere of directions) and try to keep
as much of that as a continuous rule can. Read C2 before you start and try to design round it.

## prover: are C1, C2 and C3 true?

No bench work. Take each claim as something to refute. For each: the exact statement that is true (with its
assumptions), a proof or a reference, or a counterexample. In particular: (1) C1: is the step from "plane mapped
into itself" to "invariant line" sound; what about a second surface that is not a plane (curved), or does not
cross the flat plane in a line; for c off the real axis, is there any curve in the flat plane that z^2 + c maps
into itself and on which a second sheet could hang (external rays, the Hubbard tree; for the rabbit the tree is
a tripod, so would the sheet be branched)? (2) C2: prove or break the turning count 1 + 4k and the claim that
k = 0 forces folding and k != 0 forces over-wrapping; state what is forced and what is only typical. (3) C3:
check the counting (Neimark-Sacker surfaces, resonance curves, period doubling patches) against the literature
on bifurcations of 3D maps; is there ANY smooth 3-parameter family with buds attached at isolated points over a
whole patch of the skin? What is known about "true 3D Mandelbrot" attempts (bicomplex or tricomplex sets,
Mandelbulb history) that bears on this? (4) The useful end: given what is true, what is the best object that
CAN exist and still meets as many of the user's words as possible? Be concrete enough that an engineer could
try it. Write `out/r17/prover/report.md` in plain words (the user may read it) with the mathematics in a
second part.

## hunter: test C1 to C3 by numbers, and hunt for a counterexample

Stand-alone numpy in `out/r17/hunter/`; you may import the bench's rules and iteration helpers. (1) For the
Mandelbrot solids of `oneplane`, `lathe`, `along` and `twoplane` (these are KNOWN rules, already drawn in
`out/me/r16/refsolids-161.png`; this is measurement of known solids, not a new attempt): find the resting point
of v -> F(v) + c and its 3 x 3 derivative over the main body; map the skin by which eigenvalue reaches size 1
(complex pair or real, +1 or -1); draw the curves where the pair's angle is 1/3 and 1/4 of a turn; check against
the solid itself whether the period-3 and period-4 bodies sit along those curves, and whether the period-2 body
sits on the "-1" patch. Pictures a non-mathematician can read. (2) C1: for the rabbit c and each known rule, look
for any plane other than z = 0 that the map keeps (numerically: fit planes to long orbits started near candidate
planes); report what is found. (3) C2: measure the turning count round the negative x-axis and the share of
mirror-reversed directions for `along`, `away`, `twoplane`, and any rule the searchers have registered by then.
(4) The hunt: try to build ANY smooth rule (it need not pass the basilica tests; say so clearly) whose Mandelbrot
solid has a bud off its special planes touching the main body at one point. A found counterexample matters more
than anything else in this round; a failed hunt should say how hard you looked. Write
`out/r17/hunter/report.md` and a picture sheet `out/r17/hunter/sheet.png`.
