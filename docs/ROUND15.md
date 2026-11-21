# Round 15: the square pillow with a belt (a new rule to try)

## Where this comes from

The user (not a mathematician, judges by pictures and plain words) is looking for a rule that carries
z -> z^2 + c into 3D with: the slice at z = 0 exactly the flat set, no seam or tear for any c, and detail in
every direction (not rings, not one smooth lump, not whipped cream). Round 14 closed five more roads
(`notes/_r14_reports.json`). Their standing words: "we're just working on getting the right approach for the
3d fractal" (so: no polish or checker rounds), "whatever approach you use, the z=0 case should be identical to
the 2d case", and every rule is an entry of its own in the Approach menu.

This round tries one new rule, found by the orchestrator. It is a cousin of the Mandelbulb and of the old
"Pillow" entry, but it differs from both in the one way that matters, so do not assume their verdicts.

## The rule (reference code: `out/me/r15/pillow_ref.py`, checked; read it first)

Directions (unit vectors) are laid on a **square pillowcase**: a flat cylinder with coordinates
s in R/Z (round the pillow) and t in [0, 1/2] (from the south seam to the north seam), each end zipped shut:
(s, 0) ~ (-s, 0) and (s, 1/2) ~ (-s, 1/2). It is the torus R^2/Z^2 with (s, t) ~ (-s, -t). It is flat
everywhere except at four corner points (the ends of the two seams).

**Direction map D** (double both coordinates, then mirror):
`t <= 1/4: (s, t) -> (-2s, 2t)`; `t > 1/4: (s, t) -> (2s, 1 - 2t)`.
On the flat pillow this is a plain "scale by 2" around every point (with a mirror), and each direction has 4
directions that land on it. The belt t = 1/3 comes back to itself with s -> 2s: **that belt is the equator,
s = longitude / 360**. So the plane z = 0 follows complex squaring exactly. No corner point and no fold lies
on the belt (that is what the old triangle pillow could not have: its plane ran through the corners).

**Rule:** `F(v) = |v|^2 * dir(D(pil(v/|v|)))`, then `+ c`. For v with z exactly 0 the result must have z
exactly 0 (use the exact complex square there, as other entries do).

**Layout** (sphere <-> pillow), my first cut, the same formula on both halves of the sphere:
north (z >= 0) `p = (x, y)/(1 + z)`, south `p = (x, y)/(1 - z)`;
`p = ((1 + B^2)/2 * cos(2 pi s), B * sin(2 pi s))`, B in [0, 1], B = 1 the equator, B = 0 the seam;
north `B = sinh(bn (1/2 - t))/sinh(bn/6)`, south `B = sinh(bs t)/sinh(bs/3)`, with bn, bs such that
dB/dt = 2 pi at the equator (bn = 2.2684160573, bs = 6.0668455453). Going from p to (s, t) needs
B^2 = beta, the root in [0, 1] of `beta (1 + beta)^2 - 4 px^2 beta - py^2 (1 + beta)^2 = 0` (one root; py = 0
gives beta = max(0, 2|px| - 1); on the seam beta = 0 and cos(2 pi s) = 2 px).

**Measured by the orchestrator** (`python out/me/r15/pillow_ref.py`): sphere -> pillow -> sphere to 3e-11 on
200,000 directions; the equator through the general formula is angle doubling to 2e-15; no jump (largest
jump over 400,000 close pairs shrinks in step with the step size); stretch of unit directions: median 1.86,
1 % 0.16, 99 % 5.4, largest 10; just above and just below the plane the sideways stretch is 2.0000 at every
longitude, the same as the stretch in the plane, with the side flipped (above goes below).

**First rough look** (`out/me/r15/first-look-129.png`, voxels at 129^3, 30 steps, very coarse): the cut at
z = 0 is the flat set (basilica, rabbit, Mandelbrot); the rabbit is a set of separate rounded bodies with
smaller bodies round them in space; c = -1 is bodies with horns, and its cut at y = 0 is one band with thin
spikes; the Mandelbrot solid is a lopsided rock with fins. The rule is not mirror-symmetric in z (the belt is
a third of the way up the pillow, not half), so solids differ above and below the plane. Nothing finer is
known yet. Do not oversell it: the job of this round is to find out what it really looks like.

**Whole powers n >= 2** (reasoned, not measured): `(s, t) -> (-n s, n t)`, then with u = n t mod 1:
`u <= 1/2: (-n s, u)`, else `(n s, 1 - u)`. The belt is t0 = 1/(n + 1), so the layout depends on n: north
covers t in [t0, 1/2], south [0, t0], each with its own b so that dB/dt = 2 pi at the belt
(`b coth(b * width) = 2 pi`). For n = 3 the belt is at 1/4 and the rule is mirror-symmetric in z.

## Base and house rules

`base14b/` (page `dist/v14b.html`) = the published Version 14; `src/` is identical to it. Build only with
`python build.py --name r15-<you> --base base14b --use <your files in src/>`. Never plain `python build.py`.
No git, no publishing. Scripts, logs, pictures under `out/r15/<you>/`. `tools/shot.py` drives headless Chrome
on the real GPU (`--help`); set `PYTHONIOENCODING=utf-8`; one run at a time; write scripts to files; run from
the project root. `tools/smoke-v14.json` is the page's test (62 steps).

Words on the page: plain, sentence case, no em dashes, a control is called by its label, nothing is claimed
that was not measured. Every entry says honestly what it is and where it falls short.

| who | files |
|---|---|
| entry | `src/js/10-approaches.js` (and `src/js/65-learn-steps.js` only if a sentence there becomes untrue) |
| study | nothing in `src/`: a stand-alone numpy study under `out/r15/study/` |

## entry: a new entry in the Approach menu

- id `sqpillow`, name "Square pillow", in a **new group** `{ id: 'pillow', title: 'Doubling on a pillow grid' }`
  placed after 'quaternion' and before 'angles'. Append the entry at the end of APPROACHES (old indices must
  not move). The old entry `pillow` ("Pillow", group 'tried') stays as it is; add one sentence to its texts
  only if needed to tell the two apart.
- Shader (`mul`, `pw`, `sqr`, `cmap`) and `MATH.sqpillow`, mirroring each other. Read how the round-14
  entries were built (`kleinsq`, `rotorframe` in `10-approaches.js`, between the marks R14-TEXTS-BEGIN/END for
  the texts) and how the distance estimate treats a rule that does not keep shapes; follow that. The cubic for
  beta: a closed form or a few safeguarded Newton steps, your choice, but the shader must agree with MATH and
  with the reference. Powers: whole n >= 2 as above (nearest whole power for others, said in the text, the way
  `kleinsq` does it); n = 2 is the one that matters, and it must be right before any other power is touched.
  `mul` of two different points: take it from Sphere inversions, one plane, as the other entries of this kind
  do, and say so.
- Dials: none required. If the study engineer's layout family turns out cheap, one dial for it is welcome,
  but only after n = 2 with the fixed layout is done and drawn.
- Checks (numbers, not a checker round): MATH against `out/me/r15/pillow_ref.py` on 20,000 random points
  (aim 1e-9; export points and results through a small script); shader against MATH; z = 0 exact with output
  z exactly 0; the page's Mandelbrot slice at z = 0 against the flat set; `tools/smoke-v14.json` once on your
  page (if two entries are found to draw the same picture by design, report it, do not edit the smoke file).
- **Pictures are the point.** A contact sheet `out/r15/entry/sheet-sqpillow.png`: Mandelbrot solid from the
  opening view, from above and from below; Julia c = -1, the rabbit (-0.12, 0.74, 0), c = (-1, 0.15, 0.1),
  c = (0.3, 0, 0), c = i (0, 1, 0); cuts at z = 0; and **close-ups**: zoom into a body's surface and into the
  place where two bodies meet, at 3 depths, to answer "does detail go on at smaller sizes, and what kind:
  smaller bodies, fibres, smooth sheets?". Also n = 3 and n = 4 Mandelbrot solids if the powers are done.
  Say what the 3D picture's skin can be trusted for: compare the drawn solid with a brute-force membership
  test (the page has probes; the round-12 "tried" notes describe how the skin stood up to 0.3 off for the old
  pillow) and report the number.
- Texts of the entry (tag, note, formula, about, roundNote, crush, smooth, slice): written from your own
  numbers and pictures. Plain picture for the reader: "The Mandelbulb doubles two angles on a globe grid,
  which is squeezed toward the poles, so things smear. A pillowcase grid is not squeezed anywhere except at
  four corner points. Double both ways on that grid and nothing smears." Use it only as far as your
  pictures bear it out. Say that the rule is lopsided above and below the plane at power 2, and why.

Time: aim for 70 minutes, stop at 90.

## study: what is this rule, in numbers and voxel pictures (`out/r15/study/`)

Stand-alone numpy (the round-14 trial `out/r14/turns/turns.py` has a voxel renderer, cuts and a sheet maker
you may reuse; `out/me/r15/first_look.py` shows how the orchestrator drew the first look; the bisection there
is slow, a vectorised Newton or closed form will pay off). Questions, in order of weight:

1. **Bodies or one lump?** For c = -1 at a fine grid: do the bodies of the flat basilica become separate
   bodies in space that touch at points (cross-section at x = -0.618 against the centre, as the old pillow
   table in `out/lab2/pillow2/NOTES.md` did: one plane 3.8 %, old pillows 27 to 119 %)? The first look's cut
   at y = 0 shows one band, so look closely: is there matter above and below the touching point?
2. **Detail at smaller sizes?** Zoomed voxel pictures (a small box at high resolution) of the surface at 3
   sizes, for c = -1 and the rabbit: smaller bodies on bodies, or fibres, or smooth?
3. **Does it keep shapes under repetition?** This is the property the rule was chosen for. Measure the
   stretch of F^k (no c, k = 1..6) in three perpendicular directions at random points (numerical
   derivative): the ratio largest / smallest stretch, median and 99 %. Compare with the same numbers for
   "Sphere inversions, one plane" (turns.E1) and for the Mandelbulb at power 2 (lat and lon doubled). The
   expectation (reasoned, to be tested): bounded for the pillow, growing without end for the other two.
4. **Is another layout better?** The layout is a free choice wherever it keeps the belt on the equator with
   s = longitude. Try at least: (a) a rectangular pillow (t in [0, h/2], D the same with heights scaled, belt
   at h/3; h changes how much room lies above and below the belt); (b) other seam lengths (the factor 1/2 in
   (1 + B^2)/2); (c) other B(t) profiles. Judge by question 3's numbers and by how round the bodies of the
   rabbit come out. Report the best layout as a formula the entry engineer could use.
5. **Mandelbrot solid** at a finer grid and from several sides: bulbs, fins, or a rock? Its cuts at z = 0
   (must be the flat set) and y = 0.
6. Power 3 (belt at 1/4, mirror-symmetric): one Julia set and the Mandelbrot solid, for comparison.

Deliver `out/r15/study/sheet-for-user.png`: plain-word labels, the pictures that answer 1, 2 and 5, a short
note of what came out. And a verdict in the report: is this rule nearer to what the user is after than
"Sphere inversions, one plane" (smooth lump), the quaternion square (rings) and the Mandelbulb (smear)? Be
blunt; a clear "no, because" is as useful as a yes.

Time: aim for 60 minutes, stop at 80.

## Report (everyone)

summary; files_changed; done (what, evidence); not_done (what, why); findings (plain words); pictures;
names_added; needs_from_others; risks. Say what you measured and what you only reasoned.
