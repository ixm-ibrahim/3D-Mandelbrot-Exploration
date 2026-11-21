# Round 23: can "two planes" and "along" be ironed into one rule? Look outside, and try the hinge-free door properly

Read this whole file before you start. Then read `docs/ROUND22.md` sections 1 (what the project is, the user's five
tests, the three rules that matter), 3 (what is known, and the library `out/r21/lib/mem.py`) and 6 (rules of the
house). They hold for this round too, with the changes given in section 5 below. Then read only what your section names.

No lab work this round: nobody touches `src/`, `base*/`, `squaring-lab.html`, `tools/`. Version 18 is published.

## 1. The user's newest words (2026-11-19, evening), verbatim

"the toy you made is not intuitive at all, I don't see the movements, like each step in the hop. and the original
sphere inversion 2-plane and along approaches have the best results, but in different things it would be awesome to
get that ironed out. Like the sphere inversion's blown up shapes look intuitive, like the 2d slices' "inside" parts
we would assume as having some 3d analog of it, with bulbs (or whatever feature that fractal has, idk how it would
work for dendrites and whisps/dusts and whatever, as I can't imagine what their 3d analog would look like besides a
blown up 2d version which is not what I want) on it not just on the axis planes but everywhere in the same pattern,
like the 2d spacing being done in 3d, not being stretched or warped or whatever. with the limitations of 3d
rotations, I would imagine that this has to happen with quaternion rotations somehow (one of the reasons why I
mention this is that the 3d versions of daudy rabbits tend to look like these weird un-rabbity shapes, rather than
recognizable bulbs and insides and whatevers - the along-once-then-plane approach gives the closest thing I've seen
for the rabbit, but it's still wrong and the approach seems arbitrarily wrong too)"

My reading (the orchestrator's, not theirs):
- "sphere inversion 2-plane" = lab entry "Sphere inversions, two planes" (id `fold`, bench `twoplane`): the one-plane
  square about the flat plane or the upright plane, whichever is nearer. Clean blown-up bodies with crisp buds in
  four directions for c on the x-axis; it TEARS on the diagonal planes, so the rabbit is shards.
- "along" = `turnalong` (bench `along`): eight buds, buds on buds, but thin fins between its planes, and one lump for
  the rabbit.
- What they want: the inflated, recognisable bodies of the sphere-inversion rules (for EVERY c, the rabbit too), with
  bulbs all over each body in the flat picture's own pattern and spacing, not only where a few planes through the
  x-axis cut it, and none of it stretched. One rule, not two glued together.

## 2. What the orchestrator worked out before this round (reasoned unless marked; attack it)

**(a) Why the two favourites are good at different things: the hinge.** Every rule so far that grows buds off the
flat plane uses the x-axis as a hinge: two planes, along, away, the winding rules, the Lathe. z^2 itself has no such
hinge: turning a point by an angle a about the upright axis turns its square by 2a, and the one-plane rule obeys
that (measured in round 22). A hinged rule is fine while every body sits on the hinge (c on the x-axis). Off it, it
goes wrong, and here is one cause worked by hand: above the rabbit's meeting point (x < 0, y > 0) along squares the
point in a plane tilted up toward it; squaring carries the point to the OTHER side of the x-axis, where the same
tilted plane lies BELOW the flat plane, so the tilt takes height away (height multiplied by 1.00 at height 0.075
where one plane gives 1.09; round 22 measured the same numbers without the reason).

**(b) What a hinge-free rule can do.** If a homogeneous rule |v|^2 G(direction) obeys "turn by a about the upright
axis -> square turns by 2a", G sends circles of latitude to circles of latitude. Then the directions sent into the
flat plane are whole circles of latitude (cones in space), each laid onto the flat plane; between two such circles
the image must pass over a pole, and a whole circle goes to the pole at once (a crushed cone) or the pole is torn.
So: hinge-free with no crushed cone and no tear means no buds off the flat plane at all (that is the one-plane rule).
This sharpens round 17's counting law ("the liked look needs 4 directions sent to -x and 2 to +x, so it needs a
tear, a fold, a triple winding or extra arms").

**(c) Shape-keeping needs the right cone.** A step keeps shapes at a place (stretches by the same 2|v| in all three
directions) only if G stretches the sphere of directions by exactly 2 there. On the equator: longitude doubled. On a
circle of latitude L laid ONCE round onto the equator: stretch 1/cos L, so it is 2 exactly at 60 degrees. That cone
is the flat plane rolled up so that z and -z touch (the flat picture has that symmetry for every c). For a power n
the cones are at cos L = k/n, k = 1 .. n - 1, wound k times: the count comes from the power.
Round 22's "capfold45" had its cone at 70.5 degrees wound twice (squeezed 3 to 1), and round 17's "pole rules" had
no principled size; neither was this.

**(d) First scout of that idea** (`out/r23/me/cone.py`; pictures `cone-cuts.png`, `cone-solids-*.png` beside it).
In the stereographic coordinate w (|w| = 1 the equator, north = infinity) the angle-true map
R_t(w) = (w^3 + t) / (w (1 + t w^3)), t = tan 15 degrees, covers the sphere 4 times without a fold, swaps the poles,
and lays a wavy circle near latitude 60 once round onto the equator with stretch 1.43 to 2.48 (2 on average).
It is not exact doubling on the equator, so it is blended into w^2 for Mercator latitude |mu| < 0.4. Measured: flat
check 0 of 20,000 differ, length squared to 5e-15, covers 4.00 times, 1.8 % of directions folded (in the blend).
Seen in the cuts: for c = -1 and c = -0.75 the upright cut is shells (t > 0) or one lump with horns (t < 0); the
rabbit is a spiky star (t > 0) or a small clean body with loose bits (t < 0). Likely cause (reasoned): its three
critical directions sit near latitude 28, one of them in the upright plane, and are sent to about 15 degrees above
+x or -x, inside the arms. The map has a threefold pattern round the upright axis (it must: 2a = -a for a = 120
degrees), the flat picture a twofold one. So: not a win as it stands; the family is open.

**(e) The pillow again.** Round 15's "Square pillow" (Mayer's quasiregular power map; numpy in
`out/r15/study/fastpil.py`, notes in `notes/_r15_reports.json` and `notes/_state.md` lines 366 to 500) is the "same
spacing everywhere" idea done on a flat square grid. It failed on c = -1 (one spindle with spikes: its two extra
arms lie in the upright plane) but its rabbit was "separate bodies meeting at single points, smaller bodies round
them", and a Joukowski layout gave "knobs on knobs" there. The user never looked at the pillow's rabbit as such.

**(f) What is not possible, as far as we know.** Shapes cannot be kept everywhere by any 3D rule (only sphere
inversions and the like keep angles in 3D), so every rule keeps shapes on a few surfaces only and squeezes between
them. Round 17 proved: no tear-free rule is exact on two mirror planes with the liked 4-and-2 count.

## 3. Sections

Four run at once (`outside1`, `outside2`, `cone`, `rabbit`), then `design`, then `judge`.
Every section writes `out/r23/<section>/NOTES.md` (what was done, numbers, what failed, every picture named) and
returns the structured report it is asked for.

### outside1: what has the fractal community tried for a power-2 3D Mandelbrot?

Use web search (load it with ToolSearch "select:WebSearch" if it is not loaded). People have hunted a "true 3D
Mandelbrot" for years (fractalforums, the Mandelbulb's authors, the formula lists of Mandelbulber and Mandelbulb3D:
power-2 Mandelbulb variants, "Msltoe" symmetric and toroidal formulas, Riemann-sphere formulas, Benesi, Aexion,
Bristorbrot, Hopf-map ideas, and others you find). Your memory of these formulas is NOT to be trusted: take each
formula from a source you can quote (source code or a post), give the URL, and write the formula out.
For each formula you can pin down (aim for 8 to 12): write it as a rule of our library; run `M.flat_check` (is the
cut z = 0 the flat picture? If a formula uses another axis convention, turn it so that its best plane is z = 0 and
say so); say which door it uses (tear, fold, winding, extra arms, crushed cone; `out/r17/blends/count_dirs.py`,
`turncount.py`, `screen.py` count this in seconds); draw c = -1 and the rabbit as rough solids from two eye
positions beside `oneplane`, `twoplane`, `along`. Formulas that are not "square, then add c" (Mandelbox and the
like) get one line each and no test.
Deliver: `formulas.md` (every formula with its source), `sheet.png` (the three that come closest to the user's
words, plain labels), and a straight answer: has anyone outside found something that passes the user's five tests,
or come closer than `along`?

### outside2: what does mathematics say?

Use web search. Find what is published on: uniformly quasiregular maps of Lattes type and power type (Mayer), the
Zorich map, quasiregular analogues of z^2 + c or of the Mandelbrot set in 3D (Fletcher, Nicks, Tsantaris and
others), Julia sets of quasiregular maps in R^3 with pictures, the paper this project started from
(`notes/paper-kucera.txt`) and papers citing it, Hopf-fibration or quaternion-rotation constructions of a 3D square,
and any stated obstruction (Liouville's theorem on conformal maps, Rickman, branch sets of quasiregular maps).
Check section 2 (a) to (f) against what you find and against your own reasoning: which statements are theorems
(cite), which are wrong (say why, with a counterexample you computed if you can), which are open.
Deliver: `references.md` (title, authors, year, URL, two lines on what it gives us), `verdicts.md` (each of 2 (a) to
(f): theorem / wrong / open, with the reason), and up to three constructions worth building that this project has not
tried (see `docs/ROUND22.md` section 3, `notes/_state.md`, and the lab's entry list in `src/js/10-approaches.js`
around line 1367 for what has been), each written as a formula a programmer can type. Build and test the most
promising one with the library if time allows.

### cone: the hinge-free door, done properly

Start from `out/r23/me/cone.py` (read it; `python out/r23/me/cone.py check` prints the numbers of section 2 (d)).
Goal: a rule that is exact and shape-keeping on the flat plane, lays the two 60-degree cones onto it once round with
stretch 2, and gives clean bodies. Things to try, in this order, stopping when something is clean on c = -1,
c = -0.75, the rabbit and the Siegel disc:
1. Find where the shells come from (follow orbits from the shell region; where do the critical directions go?).
2. Move the critical directions or what they are sent to: other t; a blend that removes the 1.8 % fold; turning the
   threefold pattern by 30 degrees (the y-mirror is lost: say what that costs); sending the critical directions
   exactly onto a pole or onto a place the flat set never fills.
3. A map that is not R_t at all but has the same job (equator doubled, 60-degree cones once round with stretch 2):
   build it from the conditions, for example from latitude and longitude with three smooth branch points per
   hemisphere, or as R_t composed with a turn about the upright axis.
4. Power 3 (cones at cos L = 2/3 and 1/3): does the count of extra bodies follow the power?
For each try: `M.flat_check`, a lift test (a flat-inside point lifted by a millionth must stay), covers / folded
share / stretch on the cones (the functions are in `cone.py`), cuts (flat, upright, and across the x-axis), rough
solids from two eye positions.
Deliver: the best rule as a function in `out/r23/cone/best.py` with a one-line way to load it, a sheet
`sheet.png` (c = -1, c = -0.75, rabbit, Siegel disc; rows: one plane, along, your best), and a plain verdict: does
this door give the user's picture, yes or no, and if no, what exactly spoils it.

### rabbit: every door on the shapes that are off the x-axis

The user's complaint is the rabbit ("weird un-rabbity shapes"). Put every door side by side on shapes whose c is off
the x-axis, same eye, same size, same number of steps: rabbit, Siegel disc, dendrite c = i, and c = -0.12 + 0.75i
turned 10 degrees out of the flat plane. Rules: `oneplane`, `twoplane`, `along`, round 21's `alongmem.c_wake1`
("Along once") and `sheet.evc005e70k16` ("Pulled plane") through `out/r21/judge/myrules.py`, the square pillow and
its Joukowski layout (`out/r15/study/fastpil.py` and what its `needs_from_others` in `notes/_r15_reports.json`
describes), the bench's `mandelbulb`, round 17's `b_pcd`, and the scout's `cone+` / `cone-`.
Then answer with measurements, for each rule: are the bodies separate, do they touch at single points, are there
bodies or buds off the flat plane, and are those round or stretched (ratio long to thick), joined or loose?
Then try to do better for the rabbit INSIDE each door, at most two tries per door, and say what you tried:
- pillow door: a layout that is not mirror-symmetric, or the Joukowski layout with the belt made angle-true;
- hinge doors (along, two planes): is there any choice of hinge taken from the flat rule itself, the same for every
  c, that is not the x-axis? (Section 2 (a) and (b) say no; try to break that.)
- along once: the user calls it the closest and also arbitrary. Measure what "along for the first N steps, then one
  plane" gives for N = 0, 1, 2, 3, 5 and many: at which N does the rabbit start to swell, and does any N keep both
  the eight buds of c = -1 on every body and a clean rabbit?
Deliver: `sheet-doors.png` (one row per rule, plain labels, real shapes), `sheet-n.png` (the N sweep, c = -1 and
rabbit), and a table in NOTES.md.

### design (after the four; it is given their reports)

You decide what this round can honestly claim. Read the four NOTES.md and look at their pictures.
1. Take at most six rules that the four sections point at (theirs, combinations, or your own) and test each on
   c = -1, c = -0.75, the rabbit, the Siegel disc and the dendrite, with flat check, lift test, 30 against 80 steps,
   cuts off the mirror planes, two eye positions.
2. Answer the user's question as it was asked: can the clean blown-up bodies of "two planes" and the buds of "along"
   be had in one rule, for every c? Yes with the rule, or no with the reason in three plain sentences, or "not
   known" with the narrowest open question you can state.
3. If something comes closer to the user's words than `along` does on c = -1 AND closer than "along once" does on
   the rabbit, say so only after you tried to make it fail.
Deliver: `out/r23/design/rules.py` (loader for your rules), `sheet.png`, NOTES.md.

### judge (last; it is given every report)

You did not do the work. Re-measure the claims that matter with your own scripts (`out/r21/judge/` and
`out/r22/judge/` show how). Fix or drop any picture whose caption says more than was measured.
Write `out/r23/judge/ANSWERS.md`:
- "Can two planes and along be ironed into one rule?" in at most six short sentences;
- "What has anyone else found?" in at most four;
- "What does the best new try look like, and what is wrong with it?" in at most four;
- "May be told" and "May NOT be told" lists.
Make at most three pictures for the user (section 4 says how), the first of them a sheet of real shapes: c = -1 and
the rabbit for "two planes", "along", "along once" and the best new rule of this round.

## 4. How to write and draw for this user (a hard rule; they said "you're literally speaking in greek to me")

- A picture for the user shows real shapes (rough solids or lab-style renders) first. No diagrams of coloured dots,
  no cuts with a legend, unless a shape picture cannot show the point.
- A caption is at most two short sentences that say what a person SEES ("the rabbit's bodies are separate and
  round; nothing grows above or below them").
- Words they use: plane, rotate / swing, orbit, c, bulbs or buds, body, the power, the flat picture, blown up.
  Words we may add: dot or point, hop or step, "off the flat picture", survive. Do NOT use: page, sheet, hinge,
  door, cone copy, critical, covers, winding, Jacobian, stretch ratio, latitude, or any rule's internal name. If you
  need one of these ideas, say it with a thing a person can picture.
- Numbers only when the number is the point, and never an angle or a percentage as the explanation of something.
- Internal names and numbers go in NOTES.md.

## 5. Rules of the house: changes for this round

- `docs/ROUND22.md` section 6 holds, except: nobody touches `src/`; nobody uses `tools/shot.py` or any browser;
  `outside1` and `outside2` may use web search, the others may not need it.
- Each section works in `out/r23/<section>/` and reads the others' folders only after they have finished (`design`,
  `judge`). `out/r23/me/` is the orchestrator's: read it, do not write there.
- The machine has run slowly at times today. Keep single runs under 8 minutes, print progress, and prefer cuts
  (seconds) to rough solids (minutes) while exploring; make solids for what you will show.
- A NaN is an escape: a rule that returns NaN for points near the origin or a pole will look like holes. Check
  `np.isfinite` on a test batch for every new rule.
- Aim for 75 minutes, stop at 100.
