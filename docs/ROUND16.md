# Round 16: Julia first. The basilica must pass before any Mandelbrot solid is tried

## What the user said (2026-11-18, verbatim, newest last)

> ok the kleinian squaring approach seems wrong - z=0 is not correct, the easiest sign. The other one is that
> there is no 3d relationship with the number of bulbs to the power, but only to the number of planes. The
> original basilica julia set that was inspired from this paper is way more intuitive as the correct one, but I
> know extending it to the mandelbrot is different. So I need you to try again, and really believe in yourself
> - the number of planes should not decide the inherent geometry of the fractal in 3d. It should be some
> representation of what is happening in the 2d mandelbrot - with respect to what happens hidden in the 3d -
> extended to 3d (with respect to what happens hidden in the 4d), and it shouldn't look like any of the other
> approaches of disconnected stuff and wrong z=0 and simply rotating the fractal around the x-axis or however
> it is

> ok well n=3+ is not good enough. if julia is easier, then start with that basilica and don't attempt a
> mandelrbot until the julia passes, and if the mandelbrot fails, go back to another julia. I gave a bunch of
> constraints in my last message so don't forget about those, and what we've been trying to go for this whole
> time. and at higher n anyway, it looks to smear instead of looking how I would expect.

Standing: "whatever approach you use, the z=0 case should be identical to the 2d case"; every rule is an
entry of its own; no polish or checker rounds while the right rule is being searched for. The user is not a
mathematician and judges by pictures and plain words.

## The protocol (the user's, to be followed to the letter)

1. **Stage 1, the basilica** (Julia set for c = (-1, 0, 0), power 2). A rule passes only if ALL hold:
   - J1 the cut at z = 0 is the flat basilica exactly;
   - J2 the bodies along the x-axis are separate bodies that touch at single points (no matter above or below
     a touching point);
   - J3 it is not the flat set spun round the x-axis (no rings, no tubes round the axis);
   - J4 a body carries smaller round bodies in more than one direction (not only in the flat plane), and
     those carry smaller ones again;
   - J5 one piece, no shards, no dust;
   - J6 no tear: the rule itself has no jump anywhere (so that every c is safe);
   - J7 mirror-symmetric above/below and front/back (the flat basilica is);
   - J8 close up, detail is smaller bodies, not streaks or smear;
   - J9 nothing in the rule is a free count that decides how many directions the bodies grow in. If a count
     appears it must follow from the power or from space itself, and the brief must say which.
2. **Stage 2, the Mandelbrot solid**, only for rules that passed stage 1: cut at z = 0 is the flat set; one
   piece; a body with smaller round bodies on it in more than one direction; not a rock, not fins, not thin
   leaves, not rings, not shards.
3. If stage 2 fails, the rule is recorded as "basilica passes, Mandelbrot fails, because ..." and the search
   goes back to stage 1 with another rule.

## What is known (do not rediscover)

- The reference look for stage 1 is the old entry "Sphere inversions, two planes" at c = -1 (the paper's
  Figure 4 look): a ball with a bud up, down, front and back, side bodies with the same. It is the nearest
  plane's one-plane rule, and it TEARS on the planes |y| = |z| for every c off the x-axis (fails J6).
- "Sphere inversions, one plane" (P below): buds only in the flat plane (fails J4). Quaternion square: rings
  (fails J3). Square pillow: bodies joined at c = -1 (fails J2), lopsided at power 2 (fails J7), streaks
  (fails J8). Kleinian squaring: slice not exact (fails J1). Mandelbulb: smear.
- Orchestrator's scouts (stand-alone numpy, `out/me/r16/scout.py`, `scout2.py`, `scout3.py`, sheets
  `scout-129.png`, `scout2-161.png`, `scout3-161.png`, `basilicas.png`): rules that keep the point's own plane
  through the x-axis (lathe with any change of length by azimuth) give tubes, never beads. "Latitude times 3,
  longitude times 2" falls apart.

### The new rule: the one-plane square about a plane that turns with the point

    P(x, y, z) = r^2 / (r^2 + z^2) * (x^2 - y^2, 2xy, 2 z r),  r = |v|        (the one-plane square; in the lab: MATH.mercator, power 2, no turn, no lift)
    phi = atan2(z, y)                    (which way the point lies round the x-axis)
    psi = q * (phi - sin(2 m phi) / (2 m))        m = 2 at power 2,  q = -1 ("away") or +1 ("along")
    F(v) = Rot_x(psi) P( Rot_x(-psi) v ),   Rot_x(a)(x, y, z) = (x, y cos a - z sin a, y sin a + z cos a)

In words: each point is squared by the one-plane rule about a flat plane through the x-axis, its reference
plane. Near the flat plane z = 0 the reference plane IS z = 0 (psi has a flat spot there), near the upright
plane y = 0 it is that plane, and in between it turns smoothly. "Away": it turns against the point, so half way
between the two planes the point stands on the pole line of its reference plane. "Along": it turns with the
point and overtakes it, so half way the point lies in its own reference plane. On the x-axis F = P.

Measured (scout3, power 2, m = 2): planes z = 0 and y = 0 follow complex squaring to 7e-15 and 4e-15; no jump
(largest jump over 200,000 close pairs is 3e-3, 3e-4, 3e-5 at steps 1e-4, 1e-5, 1e-6); commutes with both
mirrors and with the quarter turn about x to 2e-15; length is squared exactly.

Seen in rough voxel pictures (257 a side, `out/me/r16/basilicas.png`): **the basilica of "away" looks like the
two-plane reference** (ball with 4 buds, side bodies, both cuts z = 0 and y = 0 the flat basilica) and of
"along" the same with 8 buds. Rough, not yet judged properly: that is this round's first job.

Rough peeks beyond the basilica (scout3, do not treat as verdicts): "away": the rabbit breaks into pieces
(60 % in the biggest), c off the flat plane leaves nothing, the Mandelbrot solid looks like two thin crossed
leaves. "Along": the rabbit is one swollen lump, c off the plane gives bodies, the Mandelbrot solid is a lumpy
body whose cuts at z = 0 and y = 0 are both the flat Mandelbrot set. The pure winding rule psi = -phi (no
flat spot, `scout2.py`) has the 4-bud basilica too but is paper thin off the x-axis, because next to the flat
plane it stretches sideways by 4r - 2x where the plane itself stretches by 2r; the flat spot makes that 2r.

Why two planes, and the power: the two planes are the two sideways axes of space, y and z, each making a flat
plane with the real axis. For a whole power n the same rule is used with P the one-plane n-th power and m = n
planes (at angles k * 180 / n round the x-axis), so the count round the axis follows the power: 2n ("away")
or 4n ("along"). That choice (m = n, not m = 2 for every power) is the orchestrator's, made because of J9 and
the user's words about the power; say so wherever it matters.

## House rules

`base15a/` (page `dist/v15a.html`) = the published Version 15; `src/` is identical to it. Build only with
`python build.py --name r16-<you> --base base15a --use <your files in src/>`. Never plain `python build.py`.
No git, no publishing. Scripts, logs, pictures under `out/r16/<you>/`. `tools/shot.py` drives headless Chrome
on the real GPU (`--help`); set `PYTHONIOENCODING=utf-8`; one run at a time; write scripts to files; run from
the project root. `tools/smoke-v14.json` is the page's test (62 steps). Words on the page: plain, sentence
case, no em dashes, nothing claimed that was not measured, every entry says where it falls short.

| who | files |
|---|---|
| bench | nothing in `src/`: stand-alone numpy under `out/r16/bench/` |
| entry | `src/js/10-approaches.js` (and `src/js/65-learn-steps.js` only if a sentence there becomes untrue) |

## bench: a test bench for the two stages, calibrated on rules whose verdict is known (`out/r16/bench/`)

Build `bench.py` (stand-alone numpy and scipy; reuse `out/me/r16/scout*.py` for the rules and the fast
iteration, `out/r14/turns/turns.py` for the voxel renderer and sheet maker, `out/r15/study/fastpil.py` for the
pillow). A rule is a function F(x, y, z) -> (X, Y, Z) on arrays; a registry `rules.py` holds at least: lathe,
one plane, two planes nearest (tears), square pillow, pure winding m = 2, turning away, turning along.

- `stage1(rule)`: numbers for J1 to J8 on the basilica plus one standard sheet per rule (front, above, along
  the x-axis; cuts z = 0, y = 0, x = 0, x = -0.618; close-ups of a bud at 3 sizes). Proposed measures (improve
  them if they do not separate the known rules the way the pictures do): J1 cut against the flat set at
  801 x 801, differing points; J2 area of the cut x = -0.618034 over the cut x = 0, inside length of the
  upright line through the touching point, and whether taking out a small ball there splits the solid;
  J3 share of the solid that changes when it is turned 45 degrees about the x-axis, and whether the cut x = 0
  minus its core disc is a ring; J4 number and directions of separate buds on the middle body (wear the solid
  down by a small radius and count what comes off: how many, and how many stand off the flat plane), and the
  same again on one bud; J5 biggest piece at 321 a side; J6 the jump test at three step sizes; J7 mirror
  volumes; J8 how evenly the skin's normals point in small boxes at 3 sizes (streaks and sheets point one or
  two ways, bodies all ways).
- **Calibrate first**: the bench is right only if two planes nearest passes J1 to J5, J7, J8 and fails J6;
  one plane fails J4; lathe fails J3; pillow fails J2 and J7. Give the table and say where a measure had to
  be changed to get there. Thresholds come from this table, not from guesses.
- Then run stage 1 on turning away, turning along and the pure winding. Report each J as pass or fail with
  its number.
- `stage2(rule)` for the Mandelbrot solid (cut at z = 0 against the flat set; biggest piece; thin leaf or
  body: how full the cut x = -0.2 is inside its bounding circle; the period-2 body: attached at a point or
  along a patch; buds on the main body off the flat plane: how many come off when worn down; skin as in J8;
  lopsidedness). **Run stage 2 only on rules that passed stage 1**, and say so in the report.
- Also for every rule that passes stage 1, as a warning light only: the Julia sets for the rabbit
  (-0.12, 0.74, 0), c = (-1, 0.15, 0.1) and c = (-0.6, 0.3, 0.3): volume and biggest piece.
- Deliver `out/r16/bench/sheet-for-user.png` (plain labels: the basilica of each new rule beside the two-plane
  reference, the pass/fail lines; and, only for stage-1 passers, the Mandelbrot solid with its verdict), and
  `out/r16/bench/README.md` saying how to add a rule and run both stages (the next round's searchers will use
  it).

Time: aim for 70 minutes, stop at 90.

## entry: the two turning-plane rules as entries in the lab (`src/js/10-approaches.js`)

- ids `turnaway` "Turning plane, away" and `turnalong` "Turning plane, along", both in the existing group
  'inversions' (they are built from Sphere inversions, one plane), appended at the end of APPROACHES. No dials.
- Shader (`mul`, `pw`, `sqr`, `cmap`) and MATH mirrors. The one-plane rule is already in the file (GL_MERC_CORE,
  MATH.mercator): turn the point by -psi about x, apply it, turn the answer by +psi. z exactly 0 in, z exactly
  0 out (special-case it as other entries do; sin(pi) is not 0 in floating point). Powers: P is the one-plane
  power for any n the one-plane entry supports; the number of planes m is the nearest whole number to |n|, at
  least 1 (so the count follows the power); say in the formula text what m is. `mul` of two different points:
  from Sphere inversions, one plane, said in the text.
- Checks by numbers: MATH against `out/me/r16/scout3.py` (turning(q)) at power 2 on 20,000 points (aim 1e-12);
  shader against MATH; planes z = 0 and y = 0 against complex squaring; the page's cut at z = 0 against Sphere
  inversions, one plane (pixel for pixel); the jump test; `tools/smoke-v14.json` once (two entries drawing the
  same picture by design: report, do not edit the smoke file).
- **Pictures are the point**: `out/r16/entry/sheet-turning.png` from the lab's own renderer: for each of the
  two, the basilica from the front, from above, along the x-axis, from below; close-ups at 3 depths of a bud
  on the middle body and of the place where two bodies touch (does detail go on as smaller bodies?); the same
  basilica for "Sphere inversions, two planes" beside them; then, honestly, the rabbit, c = (-1, 0.15, 0.1),
  and the Mandelbrot solid from three sides with its cuts at z = 0 and y = 0. And the basilica at power 3
  (c = -1... use a c inside the period-2 body of the cube's flat set on the x-axis) to show the count
  following the power.
- Texts from your own numbers and pictures. They must say plainly what the Mandelbrot solid looks like, good
  or bad. Do not call the rule "the answer": stage 2 has not been judged.

Time: aim for 70 minutes, stop at 90.

## Report (everyone)

summary; files_changed; done (what, evidence); not_done (what, why); findings (plain words); pictures;
names_added; needs_from_others; risks. Say what you measured and what you only reasoned.
