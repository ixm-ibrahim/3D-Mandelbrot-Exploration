# Round 24: follow the "second version"; the push; the extra copy laid round twice

Read `docs/ROUND23.md` sections 4 and 5 first (how to write and draw for this user, house rules): they hold here
unchanged. Read `out/r23/judge/ANSWERS.md` (what round 23 found and what may not be claimed). No work in `src/`,
no browser, every run under 8 minutes (split or run in the background), NaN = escaped. Write only inside your own
folder `out/r24/<section>/`. Your written report is `out/r24/<section>/NOTES.md` (never a file called report.md).
Write Python files with the Write tool, never name a script after a standard module, start every shell command with
`cd` to the workspace and use `PYTHONIOENCODING=utf-8 python -W ignore`.

## 1. What the user said (verbatim)

About two rough pictures of the "new try" of round 23 (`out/r23/me/first-test-for-user.png`; first version = dial
+0.268, second = dial -0.268):

> the second new try seems better than the first, since the first seems assymetrical strangely. Idk why - but
> anyways, keep investigating, since yes the rabbit structure is much better in the second one

A little later, about the lab entry "Pulled plane":

> btw I also see the "pulled plane" approach, that seems to be intuitive but it's too simplistic, like there's no 3d
> bulbs or patterns between the ones that seem to be mirrored on either plane - but looking at the mandelbrot, the
> inflation of the insides of the fractal seem better. but then strangely, why the rabbit doesn't have the mirrored
> bulbs on the vertical plane beats me, so it's still not perfect

Their standing wish (round 23): the clean "blown up" bodies of the sphere-inversion rules with bulbs "not just on
the axis planes but everywhere in the same pattern, like the 2d spacing being done in 3d, not being stretched or
warped", for every c, the rabbit included. Their five tests: exact flat picture; bodies from the power, not from a
number of planes; no shards; no rings; a principled carry-over. They notice lopsidedness at once and do not accept it.

## 2. What I measured tonight (scripts in `out/r24/me/`; attack all of it)

The library is `out/r21/lib/mem.py` (`import mem as M`; `M.fixed`, `M.stay`, `M.flat_check`, `M.cut_axis`,
`M.julia_sheet`, `M.bench('oneplane' | 'twoplane' | 'along')`, `M.RABBIT`, `M.SIEGEL`). The direction maps below are
written in the stereographic coordinate w of a direction (|w| = 1 is the flat plane's circle, the upright axis is
w = 0 and infinity); every rule is F(v) = |v|^2 * (direction map of v's direction), then + c.

(a) **The family.** `R_t(w) = (w^3 + t)/(w (1 + t w^3))`, blended into plain doubling w^2 beside the flat plane
(`out/r23/me/cone.py`, `cone_rule(t)`). t = 0 is the one-plane rule. t = +0.268 is the user's "first version",
t = -0.268 their "second version". t = -1/2 is `w -> (2w^3 - 1)/(w(2 - w^3))`, the angle-true form of the TRIANGLE
PILLOW of the very first prototype round (`notes/_pillow_lab.json`; multiplication by 2 on two flat triangles): it
pulls neighbouring directions apart by exactly 2 everywhere (`dirs.py`: 1.98..2.00 over 20,000 directions).

(b) **Why the first version is lopsided and worse** (`dirs.py`). On directions alone t = +0.268 has three favourite
directions (+x fixed; 120 <-> 240) that pull every direction in (all of 20,000 random directions end there). For
t < 0 there is none; directions are pulled apart at 1.83 per step on average at t = -0.268.

(c) **THE PUSH** (`push.py`; this is the new thing). Lift a direction of the flat circle by a small latitude and look
at the latitude of its square: push = image latitude / lift. One plane: 1.93 at every longitude (lift 15 degrees).
First version: 1.02 at longitudes 0 / 120 / 240 and 3.53 at 60 / 180 / 300. Second version: the other way round.
At a meeting point of bodies (a repelling fixed point of the flat rule at distance d from 0) a lifted point runs
away if push * d > 1 and is held if push * d < 1. c = -1 (meeting points on the x-axis, longitude 180, d = 0.618):
one plane 1.20, first 2.18, second 0.63. Rabbit (meeting point at longitude 119.9, d = 0.554): one plane 1.07,
first 0.57, second 1.96. So each version keeps the bodies apart exactly where its strong side faces the meeting
point and grows them into one lump where its weak side does. The meeting point of the p/q bulb lies at about
360 p/q degrees. One plane's own margin is thin (1.07 for the rabbit), so a rule must push at least as hard as
plain doubling at every longitude where a meeting point can be, which is nearly every longitude.

(d) **Seen** (`sweep-cuts.png`, `tri.py`): for EVERY negative t (-0.10 ... -0.45) and for the exact t = -1/2 end
(`tri.py`, my "kite" layout: flat check 0 of 20,000, covers 4, no fold) the upright cut of c = -1 and of c = -0.75
is one fused lump; the rabbit keeps a clean body with small bodies above and below it; the Siegel disc is shattered.
Reasoned: for t = -1/2 the three branch directions lie ON the flat circle at 60 / 180 / 300 and the push there is
about -1 (measured -1.05), so c on the negative x-axis is fused by the nature of that pillow, whatever the layout
(the square pillow had the same fate in round 16).

(e) **Tried and dropped** (`conefold.py`, `conefold-cuts.png`): "two planes with the second plane bent into a cone"
(latitude folded back at 20, 30, 40 degrees, then one plane; round 23's `fold30`). Fused lumps for c = -1 and
c = -0.75, shards over the rabbit. Reasoned: a fold in latitude smears every body along an arc between the flat
plane and its copy on the cone; "two planes" escapes that only because bodies on the x-axis are round about it.

(f) **The lead** (`mfold.py`, `mfold-cuts.png`): lay the extra copy round an EVEN number of times:
`R(w) = (w^m + t)/(w^(m-2) (1 + t w^m))`, m = 4 (copy twice round) or 6 (four times); blended the same way.
On the flat circle it is doubling for every m. R(-w) = R(w) for even m, so the solid keeps the flat picture's
half-turn sameness: NOT lopsided (seen in the cuts). Covers the sphere 2 + 2 (m - 2) times. For t < 0 the push is
strong at multiples of 360/m. Measured push * d at lifts 8 / 15 / 25 degrees:
m = 4, t = -0.10: c = -1 1.38 / 1.63 / 1.77, rabbit 1.03 / 0.88 / 0.69;
m = 6, t = -0.10: c = -1 1.49 / 2.06 / 1.66, rabbit 1.33 / 1.84 / 1.49 (both above 1: the only setting found so far
that keeps BOTH apart; its weak longitudes are 30, 90, 150, ..., so expect trouble at the 1/4 bulb).
Seen in the cuts: for m = 4 the upright cut of c = -1 is a symmetric row of separate bodies with thin horns at four
corners; the rabbit a body with four arms and spikes; for m = 6 separate lens-shaped bodies with thin whiskers.
The copy stands at latitude 55 (m = 4, t = -0.10; stretch along its circle 3.5 where 2 keeps shapes), 43 (-0.20),
34 (-0.30), 30 (m = 6, t = -0.10; stretch 2.3). Whether the horns and whiskers are blades, hairs or bodies in the
round is NOT known: only cuts were made. Solids of m = 4 and 6 are being drawn by me as `mfold-solids-a.png`.

(g) **My reasoning about the roughness** (not measured; round 23 measured only the symptom: the welded cones are
smooth when used for one step, 3 to 1 for two steps, blades for three, a crust at every step). A body k levels down
the tree passes k times through the zone off the flat plane. If the rule squeezes there, the squeezes multiply.
Only a direction map with the same spacing everywhere (t = -1/2 in its own flat geometry) does not compound, and
its flat geometry cannot be laid on the round ball without three corners.
Seen since (`solids2.py`, `raw-vs-blend-a.png`, rough solids, 30 steps): with NO blend (angle-true everywhere, flat
picture wrong) c = -1 is a SMOOTH lump (t = -0.27: smooth with a few knobs; t = -0.5: a smooth egg with one point);
the blended t = -0.27 is spiky all over; `tri` (squeeze median 5.7) is ribbed all over. The unblended rules have no
rabbit at all (their flat picture is another set), so the comparison exists for c = -1 only. This speaks for
"the roughness comes with the squeeze, not with the copies", and it is one picture, not a proof.

## 3. The sections

Each section: `out/r24/<section>/NOTES.md` with every statement marked measured / seen / reasoned, a `sheet.png` of
ROUGH SOLIDS (two eyes: (0.45, 0.5, 1) and (0.2, 1, 0.35)) for whatever it claims (cuts alone do not count: round 23
was fooled by cuts), and a loader for its best rule (`best.py` with `rule()`).

### `twice` : the extra copy laid round an even number of times
1. Reproduce `mfold.py` (flat check, push table). Draw solids, both eyes, 30 and 120 steps, for c = -1, c = -0.75,
   the rabbit, the Siegel disc, and three more: the middle of the 1/4 bulb (c = 0.282 + 0.530i), the middle of the
   2/5 bulb (find it: period 5, angle 2/5), the airplane (c = -1.7549). Rules: one plane, along, m = 4 at
   t = -0.10 / -0.20 / -0.30, m = 6 at t = -0.05 / -0.10 / -0.20, m = 8 at one sensible t.
2. Say what the horns and whiskers ARE in the round (bodies, blades, hairs), and where they come from (the copy's
   stretch 2 / cos of its latitude against 2? the blend zone? branch directions?). Measure, do not guess.
3. Try to make them bodies: (i) the "welded" form of round 23 (`out/r23/cone/conelib.py`, `variants.py`, `tune.py`:
   exact doubling in a belt, the copy's own map beside the copy, a mix between with the no-fold condition) carried
   to m = 4 and 6; (ii) the width of the blend; (iii) t.
4. Check the half-turn sameness on the solid (turn it by 180 degrees about the upright axis: how many blocks differ)
   and the mirror in y for real c. Report lopsidedness as a number.
5. Verdict in plain words against the user's five tests, beside `along` for c = -1 and "along once" for the rabbit.

### `push` : is the push law right, and can a rule push evenly and still have copies?
1. Test the law of 2 (c) on at least ten c (those above plus the 1/5, 1/6, 3/7 bulbs and one c just inside the
   main body): for one plane, the first and second version, m = 4, m = 6, the welded cones (`out/r23/design/rules.py`
   name `cones`), my `tri`. Prediction (push * d along the meeting cycle, at several lifts) against what happens
   (are the bodies fused at the meeting point: measure the neck). Where does the law fail?
2. For each pattern list the c it must spoil (weak longitudes against 360 p/q).
3. Search for the evenest push that still has copies off the flat plane: welded forms with a wide exact belt, small
   |t| with large m, anything else. What does evenness cost (round 23: thin bodies, a leaking Siegel disc)? Give the
   trade as numbers and as solids.
4. One more idea to test, mine: let the pattern face the meeting point of each c (complex t; for m = 3,
   t = -|t| (a/|a|)^3 with a = (1 - sqrt(1 - 4c))/2 the flat fixed point). It looks at c. Say what it does on the
   panel and what it would mean for a Mandelbrot solid (c off the flat plane has no a).

### `rough` : where does the roughness come from?
1. Test 2 (g) by measurement: sort the bodies of a solid by how many steps their points spend more than 12 degrees
   off the flat plane before they settle, and measure how long : thick the bodies of each depth are. Rules: the
   second version, the welded cones, m = 4, m = 6, and each of them with NO blend (angle-true everywhere, flat
   picture wrong: `cone_rule(t, blend=False)`), and `tri`.
2. Take 200 points of thin scrap (the peel test of round 23's design section, `out/r23/design/battery.py`) and 200
   points of thick body next to them; follow their orbits; say at which step and where on the sphere of directions
   they part.
3. Say plainly: is the roughness the blend's, the squeeze's, the branch directions', or does it belong to every
   rule that lays extra copies? What would a rule need to be free of it? Is that possible together with 2 (c)?

### `design` (after the three): the best rule this round can honestly put forward
Read the three NOTES.md. Build the best candidate (or two), run the full battery of round 23's design section
(`out/r23/design/battery.py`, `table.py`) on c = -1, c = -0.75, rabbit, Siegel disc, dendrite, 1/4 bulb, try to
make it fail (finer blocks, more steps, c moved 3 degrees out of the flat plane, a second eye), and draw
`out/r24/design/sheet.png` and `sheet-top.png` beside two planes, along and "along once". Say what it is NOT.

### `judge` (last): `out/r24/judge/ANSWERS.md`
As in round 23: you did not do the work; recompute what you rely on with your own scripts; every sentence marked.
Answer in short numbered plain lines (section 4 of ROUND23.md): (1) Why is the first version lopsided and why has
the second the better rabbit? (2) Does the copy laid round twice (or four times) remove the lopsidedness, and what
does it look like in the round? (3) Where does the roughness come from and can it be had without? (4) Is anything
here closer to the user's words than `along` on c = -1 AND than "along once" on the rabbit? Lists "may be told" and
"may NOT be told". At most three pictures of real shapes for the user, captions of at most two short sentences.
