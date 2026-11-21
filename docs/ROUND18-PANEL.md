# Round 18: the Julia panel (several Julia sets must pass before any Mandelbrot solid)

Read `docs/ROUND17.md` first (the user's earlier words, the record, the house rules, the three claims C1 to C3) and
`out/r16/bench/README.md` (the basilica bench this builds on). Round 17 is still running in `out/r17/`; do not touch
its folders or the bench's own files.

## What the user said (2026-11-18, after seeing Version 16; verbatim)

> the turning along approach is the closest we've gotten so far, the basilica looks almost exactly as people
> envision, with bulbs growing between things in a natural way, very nice. The only thing is, for continued
> research, is that maybe you should look at a few julia sets first, like dendrite and basilica, and perhaps a
> few more, and then when they all pass (and then the mandelbrot passes of course) then continue

So the order of work is now: **a panel of Julia sets, all of which must pass; only then the Mandelbrot solid;
only when that passes does anything else continue.** The look to keep is the basilica of "Turning plane, along"
(`along` in the bench): bodies touching at points, "bulbs growing between things in a natural way".

## The panel (orchestrator's pick; the user named the basilica and the dendrite)

| group | tag | c | why it is in |
|---|---|---|---|
| A, c on the x-axis | basilica | (-1, 0, 0) | the reference look |
| A | sanmarco | (-0.75, 0, 0) | bodies about to join; big smooth bodies |
| A | airplane | (-1.754878, 0, 0) | a thin spine with small bodies; thin necks |
| A | cauliflower | (0.25, 0, 0) | one body with cusps; nothing to hide behind |
| B, c in the flat plane, off the x-axis | rabbit | (-0.122561, 0.744862, 0) | three bodies meet at every pinch |
| B | dendrite | (0, 1, 0) | no inside at all: a tree |
| B | siegel | (-0.390541, -0.586788, 0) | one smooth body, no pinch points |
| C, c out of the flat plane | rabbit90 | (-0.122561, 0, 0.744862) | the rabbit turned a quarter turn about the x-axis |
| C | rabbit30 | (-0.122561, 0.645069, 0.372431) | a c in no special plane: what most of a Mandelbrot solid is made of |

What the orchestrator saw in the lab's own pictures of `along` and `oneplane` on this panel
(`out/me/panel/panel-axis.png`, `panel-plane.png`, `panel-off.png`; made by `out/me/panel/shots.py` and
`sheet.py`): `along` is good on the basilica and San Marco (bodies with buds in eight directions; San Marco
more ribbed), a rounded barrel on the cauliflower, thin specks on the airplane (unclear), and **a layered lump on
every set of groups B and C** (rabbit, dendrite, Siegel disc, both turned rabbits): no separate bodies, no tree.
`oneplane` is clean on groups A and B (bodies meeting at points, a thin tree for the dendrite) but everything
it has lies round the flat plane, and for group C it gives a hollow bowl. This agrees with claim C1 (a second
plane can carry its own flat picture only for c on the x-axis), which is still being checked in round 17.

## panel: build it, calibrate it, judge the known rules (`out/r18/panel/`)

Stand-alone numpy and scipy; import the bench's iteration helpers and rule registry (`out/r16/bench/bench.py`,
`rules.py`; rules registered by round 17 in `out/r17/*/myrules.py` are loaded too). One command:
`python out/r18/panel/panel.py run <rule> [<rule> ...]` -> for each rule and each panel set, pass or fail lines in
plain words with their numbers, a sheet of pictures per rule, all numbers in json; and
`python out/r18/panel/panel.py table`.

The tests are the user's, restated for a general Julia set. Find measures that agree with the pictures; the eye
is the judge and the numbers are set from pictures, never the other way round:

- **exact cut**: for c in the flat plane, the cut at z = 0 is the flat Julia set (for group C there is no flat
  set to compare with; say so).
- **one piece, nothing loose**: when the flat set is in one piece, so is the solid (every set on this panel is).
- **bodies where the flat set has bodies, meeting at points**: where two or three bodies of the flat set meet in
  one point (the basilica at -0.618; the rabbit at its resting point, about (-0.276, 0.480), where three meet;
  San Marco and the cauliflower have cusps, not such points: handle them honestly), the solid's bodies meet in
  that one point too. Not fused, and not a lump: a rule that swells the rabbit into one rock fails here. Use
  `oneplane` as the yardstick for what separate bodies look like in numbers (volume, how full a cut across the
  meeting point is, the ball that parts them).
- **a tree stays a tree** (dendrite): at each of several iteration counts the solid is thin everywhere and in
  one piece, and it thins as the count goes up, the way the flat tree and the `oneplane` tree do. A lump with
  holes fails.
- **truly 3D, in more than one direction** (the test `oneplane` must fail on every set): smaller bodies, or
  branches for the dendrite, stand off the flat plane as well as in it, and they are round bodies or thin
  branches, not rings round an axis, not sheets, not a puffed-up copy of the flat set.
- **clean close up**: no hair, fins, whiskers or loose droplets on the skin between the special planes
  (`out/me/r16/closecut.py` does this for the basilica; generalise it to each set or say where it cannot go).
- **symmetry it should have**: the same above and below the flat plane for groups A and B; for rabbit90 the
  solid should be the rabbit's solid turned a quarter turn if the rule treats both planes alike (report the
  difference; it is a pass or fail only for rules that claim that symmetry).

Calibrate on rules whose verdict is known from pictures, and show the calibration table: `oneplane` (clean,
must fail only "truly 3D" on groups A and B), `twoplane` (the liked basilica; cracks for c off the x-axis, so
group B and C must fail), `lathe` (rings: must fail "truly 3D" by rings), `along` (must pass the basilica by
these coarse tests, must fail groups B and C as lumps), `away` (ribbed, shards off the axis). If a measure
disagrees with a picture, change the measure and say so. Do not tune anything to make a new rule pass or fail.

Then run every rule in the registry that passed the bench's stage 1 (including any round-17 rule that has by
then), and write `out/r18/panel/sheet-for-user.png`: plain labels, one row per panel set, columns `oneplane`,
`twoplane`, `along` and the best newcomer if there is one, each tile with its pass or fail words. And
`out/r18/panel/README.md`: how to run, what each test measures, thresholds, calibration, limits.

Voxel solids hide fine things (round 16 learned this the hard way: `along`'s hair). Where a verdict rests on
voxels only, say so, and add at least one point-by-point cut per set.

Time: aim for 80 minutes, stop at 100.

## review: an independent check of the panel (`out/r18/review/`), after the builder is done

You did not build the panel and should not trust it. (1) For each calibration rule and each panel set, look at
the builder's pictures AND the lab's own pictures in `out/me/panel/` and write down your own pass or fail before
reading the builder's line; list every disagreement. (2) Hunt for a test that passes something it should not
(as the first bench passed `along`'s hairy skin), with a concrete case. (3) Check that no threshold sits so
close to a new rule's number that the verdict is luck. (4) Say in plain words whether the panel can be trusted
as the gate before a Mandelbrot solid, and what must be fixed first. Write `out/r18/review/report.md`. Do not
edit the builder's files.

Time: aim for 40 minutes, stop at 55.
