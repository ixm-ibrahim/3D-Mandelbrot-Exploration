# Round 22: two new lab entries, and a look at what the orbits actually do

Read this whole file before you start. It is the only briefing you get. Then read only what your section names.

## 1. What this project is

A user who is not a mathematician is looking for the "right" 3D version of z -> z^2 + c. They judge by pictures
and plain words. A 3D rule is a "square" F(v) of a 3D point v; the orbit is v -> F(v) + c. The Julia set of c: all
start points whose orbit stays bounded. The Mandelbrot solid: all c for which the orbit of 0 stays bounded.
Axes: the flat page is the plane z = 0 (x to the right, y up); the x-axis is the real line.

The user's own tests for the right rule (all must hold):
1. The cut at z = 0 is exactly the flat (complex) picture.
2. Bodies and buds come from the power the way they do in the flat set, not from a dial that sets a number of planes.
3. No shards, no dust, no disconnected debris.
4. NOT the flat set simply spun round the x-axis: no rings.
5. A principled carry-over of what the flat rule does, not an arbitrary construction.
Their picture of "right": a body with smaller ROUND bodies on it in more than one direction, each with smaller ones
on it ("bulbs growing between things in a natural way"), and the bulbs should be bulbs of 3D in their own right
("unique bulbs"), not only copies of the flat picture standing in a few planes.

The lab (`squaring-lab.html`, built from `src/` by `build.py`) is a single web page that draws these solids on the
GPU. It has 19 entries in its Approach list. Version 17 is published; `base17a/` is a frozen copy of it and `src/`
is identical to it at the start of this round.

Rules that matter here (bench names; all exact on the flat page):
- `oneplane` (lab entry "Sphere inversions, one plane", id `mercator`): P(x, y, z) = f (x^2 - y^2, 2xy, 2rz),
  r = |v|, f = r^2 / (r^2 + z^2). Keeps angles everywhere. Clean for every c, buds round the flat page only.
- `lathe` (lab "Quaternion square (Lathe)"): (x^2 - y^2 - z^2, 2xy, 2xz). Everything is spun round the x-axis: rings.
- `along` (lab "Turning plane, along", id `turnalong`): phi = atan2(z, y); psi = phi - sin(4 phi)/4; the square is
  Rot_x(psi) P(Rot_x(-psi) v). The user's best so far: the basilica (c = -1) is a row of bodies with eight round
  buds round each, and buds on the buds. Faults: for c off the x-axis (rabbit, Siegel disc) one swollen lump; the
  Mandelbrot solid is a lumpy rock; thin fins close up.

## 2. The user's newest words (2026-11-19), verbatim

After a first explanation of `along` in the orchestrator's own vocabulary:
"I have no idea what you're saying, you're not explaining it in terms I understand"

After round 21's sheet (`out/r21/judge/sheet-for-user.png`: along / the literal reading / "the plane is pulled
toward the orbit's points" / "first step as along, every later step about the flat page"):
"yes add them - but what's that last approach? it looks promising. and the first approach you did looks promising
too with features in 3d, but not in the way I hoped with unique bulbs and whatnot. Why is that approach doing smooth
stuff instead of the bulbs in 3d in the basilica? and why is the along approach the best so far? like can't we
examine the dynamics of those orbits, and see what's going on? also I still don't really understand the stretch
step, if we're not doubling the magnitude"

So this round has two jobs:
- Part A (section `entry`, then `entrycheck`): add the two near misses of round 21 to the lab, each as its own entry.
- Part B (sections `buds`, `lump`, `stability`, `mandel`, then `design`, then `judge`): examine the dynamics of the
  orbits and say, in pictures and plain words, what is going on.

**How to write for this user (a hard rule for every label, caption and sentence meant for them).** Use their words:
plane, rotate / swing, orbit, c, bulbs or buds, body, the power, the flat picture. One everyday comparison is fine
(the orchestrator used: a book whose spine is the x-axis; every plane through the x-axis is a page; a rule answers
"which page is this point squared in?"). No names coined during the work (no "sheet lag", "psi", "easing"), no
charts of one quantity against another, no degrees or percentages unless they are the point. Say what a person
would SEE. Internal names and numbers belong in NOTES.md, not in a picture for the user.

## 3. What is already known (do not redo; build on it or attack it)

Round 21 (`out/r21/judge/NOTES.md`, `out/r21/checker/NOTES.md`, the searchers' NOTES.md beside them):
- A plane made only from the x-axis, c and the orbit (nothing fixed to start from) gives exactly the flat set spun.
- Starting from the flat page: following the orbit closely stretches every bud round the x-axis into a rib, then a
  ring; following loosely gives the one-plane picture; one step behind gives dust.
- First-step law (measured, sheet agent): on the circle through the bud on top of the basilica's middle body, a bud
  sits where the start point lies in the page it is first squared about.
- The rabbit comes apart into bodies only where the squaring page is c's own page to within about one degree.
- `M.flat_check` can pass while the flat picture has no body behind it (a film): lift a flat-inside point by a
  millionth and it is lost. Always run a lift test beside the flat check.
- The orchestrator's picture of one step (`out/r22/me/one-step-ring.png`, script `ring.py` beside it): 48 test points
  on a circle round the x-axis at x = 0, radius 0.62, c = -1. One step sends them to x = -1 - 0.62^2 = -1.384 (when
  squared in their own page) at some distance from the x-axis. Lathe: all 48 land on one spot on the axis, all stay
  (a ring). One plane: they land on a tall line, up to 0.384 off the axis; 2 of 48 stay (two buds). Along: they land
  in a small cluster, at most 0.179 off the axis; 8 of 48 stay (eight buds), the eight that lie in their own page.
- Limits known for FIXED rules: no second plane besides c's own can be KEPT by a rule and show the flat picture when
  c is off the x-axis (two kept planes meet in a line through 0 on which their two squarings disagree); only the
  one-plane rule keeps angles everywhere; `along` turns 44 % of space inside out (negative Jacobian).

The library (use it; do not write your own iteration): `out/r21/lib/mem.py`, read its docstring.

    import sys; sys.path.insert(0, 'out/r21/lib'); import mem as M
    r = M.bench('along')                      # also 'oneplane', 'lathe', 'away', 'm_w3', ...
    r = M.Rule(name, label, step, init)       # step(x, y, z, st, k, cx, cy, cz) -> (X, Y, Z, st'); c is added by the library
    M.stay(r, x, y, z, cx, cy, cz, steps)     # steps each orbit stays inside |v| < 6
    M.cut_axis(r, ang, w, h, steps, c=...); M.cut_across(r, x0, w, steps, c=...); M.solid(...); M.shade(...); M.shade_solid(...)
    M.flat_check(r); M.spun_check(r); M.julia_sheet([...], path); M.mandel_sheet([...], path); M.RABBIT; M.SIEGEL; M.JSETS

The two near misses, loaded from their makers' files by `out/r21/judge/myrules.py`:

    sys.path.insert(0, 'out/r21/judge'); import myrules as J
    J.get('alongmem.c_wake1'); J.get('sheet.evc005e70k16')

## 4. Part A: the two lab entries

Every rule is its own entry in the Approach list (the user's rule: never a dial setting of another entry). Both go in
the group `inversions`, at the END of `APPROACHES` in `src/js/10-approaches.js`, after `windsq`.

**Entry 1, id `alongonce`, name "Along once, then one plane"** (round 21's `alongmem.c_wake1`).
The first squaring of an orbit is done by the rule of "Turning plane, along" (`tpPower(v, n, true)` / the GLSL of
`GL_TURNALONG`); every later squaring by the one-plane rule (`MATH.mercator` with its default one plane / its GLSL).
The orbit carries only a count.

**Entry 2, id `pulledplane`, name "Pulled plane"** (round 21's `sheet.evc005e70k16`).
The orbit carries a 2-vector w, which starts as (s0, 0) with s0 = 0.05: "the flat page, held weakly". A plane through
the x-axis at turn t is written as the doubled-angle direction (cos 2t, sin 2t); w points at the carried plane and
its length is how firmly it is held. One "pull" by a thing with coordinates (y, z), weight k and ease e:
    pw = atan2(w2, w1);  t = atan2(2yz, y^2 - z^2) - pw, brought into -180..180 degrees;  a = pw + t - e sin t;
    w <- w + k (y^2 + z^2) (cos a, sin a)
Each squaring of an orbit point v with the constant c: (i) c pulls: coordinates (cy, cz), ease e = 0.7, weight
kc = 16 (a c on the x-axis pulls with weight 0); (ii) the point pulls: coordinates (y, z), ease 0.7, weight 1, on
the w just changed; (iii) theta = atan2(w2, w1) / 2 and the square is Rot_x(theta) P_n(Rot_x(-theta) v), P_n the
one-plane power n; (iv) c is added by the orbit. The three numbers s0 = 0.05, e = 0.7, kc = 16 were set by hand in
round 21; make them three sliders of this entry with those defaults (the user explores by moving sliders), named in
plain words, and say in the entry's texts that they are hand-set.

**Conventions for both.**
- A squaring of the exact origin gives the origin, counts for nothing and changes nothing that is carried. So in the
  Mandelbrot view (start value 0) the first squaring that counts is the squaring of c, as in the library, where the
  Mandelbrot orbit is started at c with k = 0. Check that your lab entries agree with the library's rules in both
  views (see "Parity" below).
- What is carried belongs to ONE orbit and is fresh at the start of every orbit. The GLSL orbit code
  (`GL_ORBIT` in `src/js/30-shaders.js`, function `orbitDE` and every other loop that iterates `f`) runs
  neighbour orbits interleaved with the main one when the distance estimate asks for them; `deMax: 0` (as the
  entries `turnalong` and `windsq` have) switches the neighbours off. Find EVERY place an orbit is iterated
  (picture, colouring, traps, probes, the flat cut, mosaic, 3D model export in `46-mesh.js` / `45-export.js`,
  anything else) and make sure the carried state is reset at the start of each and never shared between two orbits.
  If the equation box calls the power more than once in a step (z^2 + z^3 ...), decide what that means, keep it
  simple, and say so in the entry's note.
- The constant c is not visible to `pw` / `sqr` today; `f(z, c)` has it. Make it visible in the least invasive way.
- Entries that carry nothing must draw exactly as they did: no change in their compiled shader beyond what is
  unavoidable, and no slower. Prove it: for five other entries (mercator, lathe, turnalong, windsq, bulb) the picture
  of your build equals the picture of `base17a` pixel for pixel, or differs by rounding noise only (say how much).
- The card's measurements and the Learn tab work on a single squaring `MATH[id](v, n, q)`. For these two entries
  they show the FIRST squaring of a fresh orbit (count 0; for `pulledplane` with the page's current c), and the
  entry's note says so in one plain sentence. Add written-out Learn moves only if they come cheaply; the generic
  moves are acceptable.
- Texts (tag, note, formula, about, round note, crush, smooth, slice): the plain style of the neighbouring entries
  (`TP_*`, `WS_*`), every sentence something measured (round 21's judge and checker notes hold the numbers) or
  readable off the rule. Say the faults as plainly as the strengths. For `alongonce`: eight buds on the basilica's
  middle body only, the rabbit in smooth separate bodies of which two float free, the Mandelbrot solid the same as
  one plane's. For `pulledplane`: buds in four directions for c on the x-axis, fading as c leaves it; a rabbit that
  is nearly one plane's; thin loose flakes over the skin close up; three hand-set numbers.
- Also in this build, one wording fix the user has now asked about twice. The Learn tab's generic move from
  `learnStretchTo(F)` (`src/js/65-learn-steps.js`) says "Then the length goes from a to the rule's length, b". The
  user reads "Stretch" as doubling. Where the rule's length is the plain power of the length (|F(v)| = |v|^n to
  rounding), say it the way `learnSayStretch` does and add the plain contrast, for example at power 2: "Its length
  is multiplied by itself, not doubled: 0.80 becomes 0.64, and 2 would become 4. A length under 1 gets shorter, a
  length over 1 gets longer." Keep the old sentence for rules whose length is not the plain power.

**Build and test** (section `entry` is the ONLY one that may touch `src/`; `entrycheck` may not).
- Build: `python build.py --name r22-entry --base base17a --use <every src file you changed>` -> `dist/r22-entry.html`.
  Do NOT run `--page`, do not publish, do not touch `squaring-lab.html` or `base*/`.
- Test with `tools/shot.py` (headless Chrome on the real GPU; ONE run at a time on this machine;
  `PYTHONIOENCODING=utf-8`). `out/r20/entry/NOTES.md`, `out/r20/entry/smoke.py` and `out/r20/entry/10-approaches.diff`
  show how the last entry was added and tested; `out/me/panel/shots.py` and `sheet.py` show how to drive the lab for
  a sheet of pictures. The smoke list `tools/smoke-v14.json` and the 67 steps of `out/r20/entry/smoke.py` must still
  pass on your build with no console errors, plus steps for the two new entries (select, Julia and Mandelbrot view,
  the flat cut, power 3, the three sliders, the Learn tab, a 3D model export if the entry allows one).
- Parity: for each new entry, compare the lab's own picture with the library's point-by-point picture of the same
  rule: the flat cut of the basilica, the rabbit and the Mandelbrot set (must be the flat pictures), a cut that is
  not a mirror plane, and the whole solid from one camera, for the basilica, the rabbit and the Mandelbrot solid.
  Say what differs and by how much. If the lab has no way to show a cut you need, compare silhouettes.
- Deliver: `dist/r22-entry.html`; `out/r22/entry/NOTES.md` (what you changed, file by file; every orbit loop you
  found and what you did there; test results; what you could not do); `out/r22/entry/changes.diff` against `base17a`;
  `out/r22/entry/sheet-for-user.png` made from the lab itself: basilica, rabbit and Mandelbrot solid for
  `turnalong`, `alongonce`, `pulledplane`, same camera, plain labels.

`entrycheck` did not write the code and should not trust it. Re-run the smoke lists yourself, re-do the parity
comparison with your own script, check the five untouched entries against `base17a`, read the diff for any orbit
loop that was missed (search for every call of `f(` and `start(` in the GLSL and every JS loop over `MATH[`), read
every new sentence a user will see (true? plain? does it name a fault?), and try to break the entries (power 1, 3,
-2; the equation `z^2 + z^3 + c`; Julia and Mandelbrot; mosaic; inside-out; the 2D cut; switching entries back and
forth; a phone-sized window). Return a list of defects, each with how to see it, worst first, or say there are none.
You may build your own test pages under other names in `dist/`; you may not edit `src/`.

## 5. Part B: what are the orbits doing?

The user's questions, each of which needs an answer a person can SEE:
- Q1. Why does `along` grow round buds in many directions, and why are the others smooth off the flat page?
- Q2. Why is the rabbit (and every c off the x-axis) one lump under `along`, and clean but one-plane-like under the others?
- Q3. Why does "Along once, then one plane" look promising, and what exactly does it lose?
- Q4. What would a rule have to do, step by step, for a body to carry round buds all over that are buds of 3D in
  their own right, for every c? Is there anything in the orbits that points at such a rule?

Write rules of your own in `out/r22/<you>/myrules.py` (`RULES = [M.Rule(...)]`), scripts and pictures in your folder,
findings in `out/r22/<you>/NOTES.md` (NOT report.md). Sections:

### buds: how a bud is made, step by step (Q1, Q3)
A bud is a place whose points are carried, in a few steps, into a bigger body. Follow them. For `lathe`, `oneplane`,
`along`, `alongmem.c_wake1`, `sheet.evc005e70k16` on the basilica (then San Marco): take rings and small balls of
test points round each body and round a bud, and record where 1, 2, 3, 4 steps send them, which page each step used
and how far the point was from that page. Check and extend the one-step picture of section 3: is "a bud sits exactly
where the point lies in the page it is squared in" the whole story for the second and third generation of buds, for
the buds ON buds that `along` has round the axis, and for bud roundness (what decides whether a bud is a ball, a
lens or a rib)? Why is the skin BETWEEN along's buds smooth in some places and finned in others? Explain
c_wake1's bare side bodies and evc's four directions in the same terms. Deliver two or three pictures a
non-mathematician can read (the style of `out/r22/me/one-step-ring.png`), each with one plain sentence per row.

### lump: where do the points of the rabbit's lump go? (Q2)
For `along` with the rabbit's c, the Siegel disc's c and c = -1 + i t for t = 0.03, 0.1, 0.2: sort every bounded
orbit by where it ends up (the flat cycle? another cycle off the page? a closed curve? a cloud that never settles?).
Colour cuts and rough solids by that. How much of the lump goes to the flat cycle, and what does the rest do? Draw
the trails of a few typical orbits over the solid. Do the same for `oneplane` and `alongmem.c_wake1` (clean bodies),
so the difference is visible. Then explain the lump mechanically: what one step of `along` does to the three pages
that do not hold c; where the points that the flat rule throws out are caught instead. For `c_wake1`: what are the
two bodies that float free, where do their points go, and why are they not joined to the rest? State plainly what a
rule must NOT do if the rabbit is to stay in separate bodies.

### stability: the fine print of each step (Q1, Q2)
Numbers behind the pictures. For `oneplane`, `along`, `lathe`, `away`: at each point, how far the step is from
keeping shapes (the ratio of its largest to its smallest stretch, and whether it turns space inside out); map that
in cuts and relate it to where the buds are round, where the fins sit, where the lump is. For every cycle of the
flat picture that matters (basilica 0 <-> -1; the rabbit's three-cycle; the Siegel point; the two fixed points):
does the rule pull nearby points off the page toward it, push them away, or neither, and how fast, compared with
the pull inside the page? Does `along` have cycles that are not in the flat page, and are they attracting? What are
the thin fins of `along` in terms of orbits (points that fall exactly into one of the four pages after some steps)?
One picture for the user: a cut coloured by "keeps shapes / squeezes / turns inside out", with the solid's outline
on it, for `along` and `oneplane`, plain legend.

### mandel: the orbit of c (Q1 to Q3 for the Mandelbrot solid)
For `along`, `oneplane`, `alongmem.c_wake1`, `sheet.evc005e70k16`: for c on circles round the x-axis through the
buds of the flat Mandelbrot set (the big disc at -1, the period-3 buds, the bud at -1.3107), where does the orbit of
c go, which pages does it use, where does it end up? Why is along's solid a rock, why is c_wake1's exactly one
plane's, why has evc's a second copy standing upright and nothing between? What would the orbit of c have to do for
a round bud to stand on the solid away from the flat page? One or two pictures for the user, plain labels.
(The order of work is still Julia sets first: this section explains, it does not rank rules by their Mandelbrot solid.)

### design (runs after the four above; it is given their reports): what the orbits point at (Q4)
Read the four NOTES.md files. From what the orbits do, say what a step must do for (a) a bud to exist at a place off
the flat page, (b) to be round, (c) to carry buds itself, (d) for the bodies to stay separate when c leaves the
x-axis, (e) for the count of buds to come from the power and not from a number written into the rule. Which of these
pull against each other, and is the conflict a proof or only what has been seen so far? Then try: at most six new
rules that follow from the findings (with memory or without), each defined in full, tested with the library on the
basilica AND the rabbit (flat check, lift test, cuts at angles that are not mirror planes, cuts across, two eye
positions, 30 against 80 steps). Report failures as plainly as successes. A rule that only matches `along` on the
basilica and `oneplane` on the rabbit by switching between them on a dial is not a finding.

### judge (runs last; it is given all reports): is it true, and can the user read it?
You did not do the work and should not trust it. Re-measure the central claims of each report with your own
scripts; open every picture meant for the user and read it as someone who knows no mathematics: is every label in
the user's words (section 2)? Does the picture show what its caption says? Fix or redraw the user's pictures where
needed (in `out/r22/judge/`), at most five in all, ordered so that they answer Q1 to Q4 in turn; write
`out/r22/judge/ANSWERS.md`: the answer to each of Q1 to Q4 in at most six plain sentences, each marked measured /
seen / reasoned, and a list "may be told / may NOT be told". If `design` claims a rule that beats `along`, try to
fail it on the Julia sets (`out/r21/judge/` shows how round 21's judge did that).

## 6. Rules of the house

- Work from the project root (the folder that holds `docs/`, `out/`, `src/`). Run python with `PYTHONIOENCODING=utf-8`.
- Write Python files with the Write tool, not with shell heredocs (backslashes get mangled). Never name a script
  after a standard module (`numbers.py` broke numpy last round).
- Only `entry` touches `src/`. Nobody touches `base*/`, `squaring-lab.html`, `notes/`, `docs/`, `tools/`,
  `out/r21/`, `out/r22/me/` or another section's folder. Nothing is published. No browser except through
  `tools/shot.py`, and only `entry` and `entrycheck` use it.
- Several agents run at once: keep each run under about 10 minutes and do not start more than one heavy run at a time.
- LOOK at every picture you rely on (Read the PNG) before you say what it shows. Mark every statement measured (a
  number you computed), seen (in a picture you opened) or reasoned.
- Known traps. A cut along a mirror plane of the rule hides its faults: also cut at 11.25, 22.5 and 33.75 degrees
  and across the x-axis. Rough blocks at 20 to 30 steps hide dust and slow leaks: compare 30 and 80 steps. "Round
  buds" seen from one side may be rings: look from a second eye position or cut across. A c just outside the flat
  Mandelbrot set (for example -0.75 + 0.1i) has no flat inside at all: do not use it as a test shape.
- Report failures as plainly as successes. "Nothing here works, and this is why" is a full result.
- Aim for 75 minutes, stop at 100.
