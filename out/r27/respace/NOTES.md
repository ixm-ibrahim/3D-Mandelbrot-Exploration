# Round 27, explorer "respace" (question B2): the balls object carried over to the true flat picture

Every statement is marked MEASURED (a number from a script in this folder, log named), SEEN (I opened the picture
named), REASONED (an argument, not checked by a run) or THEOREM. Everything is in `out/r27/respace/`.
Read before starting: `out/r25/klein/NOTES.md`, `out/r25/judge/ANSWERS.md`, `out/r25/wall/NOTES.md`. Not read:
`out/r25/vahlen/NOTES.md`, `out/r25/inverse/NOTES.md`.

## In six plain lines

1. The match of the two flat pictures exists and is exact as a verdict: body to body, rim to rim, fractions to
   halvings. Asked at the matched point, the object's flat cut gives the true verdict at 20000 of 20000 random points
   (as it stands it is wrong at 1146 of them, 37.3% of the true area). MEASURED.
2. Off the flat plane no way of carrying it over gives a clean solid. I built four. None passes the five tests. SEEN, MEASURED.
3. The move "fractions to halvings" is the thing that must NOT be taken off the flat plane: it presses the bulbs
   flat (the biggest bulb comes out 3.6 times as wide as thick, small ones are pressed to nothing). MEASURED, SEEN.
4. The best way leaves the bulbs where the balls object has them and only bends each ball into the true body
   (the hidden direction grows by the same factor as the flat directions). Flat cut exact, bulbs all over, the
   biggest bulb round (1.01), most others eggs (1.3 to 1.8), and a fringe of thorns round the outline of the flat
   picture, where a fifth of the bulbs are cut by an upright wall. SEEN, MEASURED.
5. That best way is a rule a shader can run, and it runs for the rabbit too (flat cut exact, 0 wrong of 20000).
   But the rabbit comes out as a slab with warts: upright walls and needles where three bodies meet. SEEN, MEASURED.
6. Why: the true bodies have a corner at every bud, at every size; the balls have none. Bending a ball into such a
   body leaves round bulbs only far from the rim. The off-plane bulbs also still come from the grid of whole
   numbers, not from the power. So: closer to the look, not the user's object. REASONED from what was measured.

## Files

- `carry.py`: everything. `qmark` / `qinv` / `Omega` / `Psi` (fractions and halvings), `Body` (a true body's own
  natural coordinate `bott`, its inverse `unbott`), `enter` (which body a flat point stands in), `Hflat` (the flat
  match), `own_family` (the middle ball with what hangs on it off the flat plane), `carried(body, way)` (the carried
  object as a rule of the bench library; draw with `c = (0, 0, 0)` and 2 steps).
- `chk1.py`, `chk2.py`, `chk3.py`: checks of the pieces (printed only; results quoted in section 0).
- `flatmatch.py check | picture`: step 1. Log `flatmatch-check.log`, picture `match.png`.
- `solids27.py solid | cuts | time`: solids (`depth-<set>-<way>-<eye>.npz`, `solid-*.png`) and `cuts.png`.
  `zoomcut.py`: `zoom-upright.png` (ways A and F), `zoom-upright-fit.png` (F and G).
- `roundness.py`: step 3, bulb by bulb. Log `roundness.log`. `squeezemap.py`: where way A squeezes. Log `squeezemap.log`.
- `tests5.py flat | mirror | blocks`: logs `tests-flat.log`, `tests-mirror.log`, `tests-blocks.log`.
- `compose27.py`: the pictures to show: `carried-c-1.png`, `carried-ways.png`, `carried-rabbit.png`.
- Sets: `b` = c = -1, `r` = the rabbit. Eyes: `a` = (0.45, 0.5, 1.0) from the front, `top` = (0.2, 1.0, 0.35) from above.
- Solids: 560 x 420 pixels, 300 blocks deep for way A and for the balls object itself; 400 x 300 x 200 for B, C, F, G.
  Flat orbit followed 48 steps in the solids, 300 in the flat checks. The balls object asked with 14 rounds.

## 0. The pieces, checked

- MEASURED (`chk1.py`): the re-spacing sends 1/2, 1/3, 2/3, 1/4, 3/4, 2/5, 3/5 to 1/2, 1/4, 3/4, 1/8, 7/8, 3/8, 5/8
  exactly; there and back misses by 2e-13 at worst.
- MEASURED (`chk2.py`, 40000 random flat points each): a first entry into the body of 0 is found for exactly the
  truly inside points (c = -1: 6002 of 6002, none wrongly; rabbit: 5597 of 5597, none wrongly). The body's natural
  coordinate b stays below 1 (largest 0.99997), satisfies b(two steps) = b squared to 8e-16 (rabbit: three steps,
  7e-16), is 1 at the point where the body hangs on its neighbours, and its derivative agrees with a difference
  quotient to 2e-6.
- MEASURED (`chk3.py`, picture `own-family.png`): of 16100 random points in the balls object 11113 are in the middle
  ball, 658 in balls hanging on it off the flat plane, 4329 in other families; on the flat plane the family is the
  middle disc and nothing else (0 of 34821); the family is its own mirror image above/below and left/right (0 of 400000 differ).

## 1. The flat match

What it is. In the true picture every body is brought to the body of 0 by the flat rule itself (n steps, one to
one), and there it has its own natural coordinate b: a round disc in which "two steps of the rule" is plain
squaring. In the object every body is a round disc already. Rim to rim: a rim point at the angle "k / 2^m of a
turn" from the point where the body hangs (a halving; that is where the true buds sit) goes to the rim point with
the object's own coordinate p/q (a fraction; that is where the object's buds sit), by the one order-keeping
rule that sends "the middle between two halvings" to "the fraction between two fractions" (numerators added,
denominators added). Inside to inside: along the straight line from the middle of the disc. Body to body: the
neighbours and buds are matched by six fixed moves, each a chain of circle inversions that carries the object's
flat cut onto itself (MEASURED indirectly: every matched body lies wholly inside the object, see below).

- MEASURED (`flatmatch-check.log`): 20000 random points of the box. The object's flat cut as it stands: wrong at 1146
  (37.3% of the true area; round 25 had 38.6% on a grid). Carried over: true verdict at 20000 of 20000. All 3076
  inside points are matched into a body, all 16924 outside points are sent outside.
- MEASURED: body to body. The 23 true bodies of at least 60 grid points land in 23 round discs of the object; no two
  of the discs overlap; each disc lies wholly inside the object. Middle body -> the middle disc (radius 0.525), the
  two neighbours -> the discs at x = +-0.817 (radius 0.291), the end bodies -> x = +-1.181, the bud above -> the disc
  at 0.639 i (radius 0.113).
- MEASURED: rim to rim. The halvings 1/4, 1/8, 3/8, 1/16, 3/16, 5/16, 7/16 of the middle body land on the fractions
  1, 1/2, 2, 1/3 (0.3351), 2/3, 3/2 (1.5049), 3 of the object's rim.
- SEEN (`match.png`): spokes at the halvings of every true body, and where they land in the object. Next to every
  point where two balls kiss there is a wide grey wedge that no grid point reaches. MEASURED (`respace-numbers.log`):
  the last 10 degrees of a ball's rim next to a kiss come from the last 0.07 degrees of the true rim next to the
  pinch; the last 5 degrees from 0.00002 degrees. This is round 25's "sliver against wedge" as a number.
- REASONED, and it matters for reading the 20000: the verdict comes out right for ANY choice of the six moves,
  because each of them carries the object onto itself. So "20000 of 20000" checks the arithmetic, not the choices.
  Two things in the match are picked: (a) which of a bud's own buds counts as "straight opposite": the object has a
  whole row of equal ones there, the true bud has one; my choice makes the match of the bud straight above the
  middle body lopsided left to right (SEEN in `match.png`: its colours are turned); no choice is its own mirror
  image and runs on one fixed set of moves; (b) the match of the gaps between bodies: outside goes to outside and
  nothing more is claimed.

## 2. The ways off the flat plane

All ways share one frame. For a point p = (flat point z, height h): follow the flat rule on z until it first stands
in the body of 0; go to that body's natural coordinate b. Then ask the middle ball of the object, with the bulbs
that hang on it off the flat plane, at a point made from (b, h). The flat bodies of the object are not used: the
true flat picture supplies them. Nothing is drawn above the gaps between bodies (the match has no point to offer
there), so the solid stands exactly over the flat picture.

- Way A, "same factor". The hidden direction is multiplied by the same factor as the flat directions, at every
  step and in the natural coordinate: (b, |db/dz| h). No re-spacing. Why not arbitrary: REASONED: any lift that keeps
  small shapes at the flat plane must agree with it close to the plane; this is the plainest one. What is picked:
  straight columns (the lifts differ once the height is no longer small against the distance to the rim).
- Way B, "re-spaced, spun". Way A, then the angle from the hanging point is moved from halvings to fractions on
  every circle round the body's own axis. This is the task's "the upright plane is carried like the flat plane",
  done body by body: every plane through a body's axis gets the flat re-spacing. Not arbitrary.
- Way C, "re-spaced in the flat directions". Way A, then the same move applied to the flat angle only, heights
  untouched. The plainest reading of "carry the flat match up".
- Way F, "fitted sphere inversion". At every flat point the natural coordinate is replaced by the sphere inversion
  that fits it best there (same value, same factor, same bend), and that inversion is used off the plane. Exact
  for a ball. Way G: F, with way A wherever the fitted inversion is inside-out. Both are tries that failed.
- Not built: the literal "upright plane through the x-axis carried exactly as the flat plane, everything between by
  a turn". It needs the match of the gaps between bodies, and that is the arbitrary part of section 1.

## 3. What the eye sees, and the numbers

c = -1 (`carried-c-1.png`, `carried-ways.png`, `cuts.png`, `zoom-upright.png`; SEEN unless marked):

- Way A, from the front: the chain of pointed bodies of the true flat picture, blown up, bulbs all over every body,
  bulbs on bulbs. The big bulbs are round. A few dark slanted grooves on the middle body and short thorns at the
  points where bodies meet. From above: a fringe of thorns all round the outline.
- Way A, upright cut through the x-axis (`zoom-upright.png`, top left): the big bulb in the middle is a circle; the
  bulbs toward a pinch lean and stretch into leaves, then into hairs; at the pinch the two bodies meet along a short
  upright edge, not in a point.
- Way B: every bulb is pressed into a flat wart. Way C: bulbs smeared sideways. Way F: bulbs round and the pinch a
  clean pair of cones (`zoom-upright.png`, bottom left), but thin fins shoot up all over the solid
  (`tried-fit-b-a.png`). Way G: fewer fins, still all over (`solid-b-G-a.png`).

How round (MEASURED, `roundness.log`; 154 first bulbs off the flat plane on a quarter of the ball, each an exact
ball in the object, 700 points of its skin carried back; longest against shortest width):

| host body, way | 3 large bulbs | 20 medium bulbs | 131 small bulbs | cut by a wall |
|---|---|---|---|---|
| middle body, A | 1.01, 1.48, 1.48 | middle value 1.63, worst 2.65 | middle value 1.34, worst 6.5 | 29 of 154 |
| left neighbour, A | 1.36 to 1.69 | 1.70, worst 3.7 | 1.40, worst 6.5 | 29 |
| bud above, A | 1.41 to 1.85 | 1.84, worst 4.5 | 1.45, worst 6.5 | 29 |
| middle body, B | 1.85, 1.86, 3.61 | 6.2, some pressed to nothing | 2.6, worst beyond 900 | 37 |
| middle body, C | 1.01, 1.82, 1.82 | 4.0, some pressed to nothing | 3.0, some pressed to nothing | 30 |

(This table is for the judge, not for the user.) "Cut by a wall": at least 2% of the bulb's skin has no place over
the body it stands on (it leans out over the rim, where nothing is drawn); the ratios are of the whole bulbs only.
The cut ones are the bulbs nearest the flat plane. "Pressed to nothing": bulbs that stand at a fraction of the
re-spaced angle, where the re-spacing has slope zero; the measured ratio is beyond a million. The biggest bulb under
way B: its 26 degrees on the ball come from 11.3 degrees of true angle (MEASURED, `respace-numbers.log`).

Where way A squeezes (MEASURED, `squeezemap.log`: a tiny bulb standing on the skin, by how far out its foot is in
the body's natural coordinate): middle of the body 1.08; 0.6 to 0.8 of the way out 1.27; 0.8 to 0.9: 1.43; 0.9 to
0.96: 1.66; 0.96 to 0.99: 2.25 (worst 21); the last hundredth: 4.3 (worst 63). Three quarters of the skin is below
1.5, 3% is above 3 (rabbit: 57% below 1.5, 7% above 3). Worst: at the rim, next to every bud root. No bound: REASONED
(the factor |db/dz| goes to zero or jumps at every corner of the rim, and there is a corner at every bud).

Pinches under way A (MEASURED, `squeezemap.log`): the height of the skin on the way to the pinch of c = -1 is 0.34,
0.25, 0.19 at 0.9, 0.99, 0.999 of the way out. It does not come down to the flat plane at any size I reached: an
upright edge. For the rabbit it is 0.33, 0.33, 0.37: it rises. REASONED: a corner of a right angle gives an edge of
fixed height, a sharper corner a blade that grows; the rabbit's bodies have the sharper corner.

Loose pieces (MEASURED, `tests-blocks.log`, blocks of 0.01 above the flat plane): way A, c = -1: 22 pieces that do not
reach the flat plane, holding 0.02% of the solid; highest block 0.74 (the top of the big bulb). Way B: 103 pieces,
0.35%. Rabbit, way A: 50 pieces, 0.06%. Rabbit, way B: 281 pieces, 0.49%, needles up to 1.29.

The rabbit (`carried-rabbit.png`, SEEN): from the front the rabbit's bodies with bulbs on them, three bodies round
each meeting point, kept apart. But between the bodies there are flat upright faces, and needles shoot far out from
the meeting points. From above it is a slab with warts on its two faces and sheer walls along its outline.

## 4. The five tests and the mirror test (way A, the best of the four)

| test | c = -1 | rabbit |
|---|---|---|
| 1. flat cut exact | YES: 0 wrong of 20000; 0 of 3076 inside points lost when lifted by a millionth | YES: 0 wrong of 20000; 2 of 2788 lost when lifted by a millionth |
| 2. bulbs follow from the power | NO: the flat bodies do (they are the true ones), the bulbs off the flat picture come from the square grid of whole numbers | NO, the same |
| 3. no shards, no smear | NO: thorn fringe round the outline, 29 of 154 bulbs cut by an upright wall, bodies meet along an upright edge (`carried-c-1.png`) | NO: upright faces and needles at every meeting point (`carried-rabbit.png`) |
| 4. no rings, and works for the rabbit | no rings: YES (turned by a random angle round the x-axis, 20.8% of the solid changes; the balls object itself 12.2%) | runs, flat cut exact, bodies apart; fails test 3 worse than c = -1 |
| 5. principled, nothing picked | NO: picked are the grid (square or honeycomb), the size dial t, straight columns, and the wall above the rim | NO, the same |

(MEASURED: `tests-flat.log`, `tests-mirror.log`, `roundness.log`.) Ways B, C, F, G: test 1 YES for both sets (0 wrong
of 20000 each), test 3 NO by a wide margin, the rest as way A.

Mirror test (MEASURED, `tests-mirror.log`, 150000 random points): c = -1, ways A and B: the solid is its own mirror
image above and below the flat plane (0 points differ), left and right (0), up and down in the flat plane (0).
Rabbit: above and below 0, half turn in the flat plane 0 (the flat rabbit has no other mirror).

The honest point about test 4. The brief expects "only c = -1 and its relatives". For the MATCH of section 1 that is
right: it uses the object's flat bodies, and three balls cannot meet in a point. For way A it is not right: way A
uses from the object only the middle ball and what hangs on it off the flat plane, and from the flat picture only
"each body has its own natural coordinate". That holds for every c whose orbit of 0 comes back to 0 (measured for
c = -1 and the rabbit; REASONED for the others; for c where 0 is only pulled toward a cycle the coordinate is a
different one and I did not build it). What does not carry: roundness near meeting points. The sharper the corner
where bodies meet, the worse; the rabbit is already worse than c = -1.

## 5. Rule or redrawn picture?

A rule. Every way above is a verdict for every point of space; the solids were made by asking it block by block.
The recipe a shader would run for way A (c = -1: p = 2 steps per round; rabbit: 3):

    z = x + i y, h = the hidden coordinate, m = 1
    repeat (up to about 50 times):
        if z is in the body of 0: stop
        m = m * 2|z|;  z = z*z + c                      (if |z| > 4: OUTSIDE)
    "z is in the body of 0": follow z every p-th step; it must stay in the band between the two points where the
        body hangs (|Re(z conj(alpha))| < |alpha|^2, alpha = (1 - sqrt(1 - 4c)) / 2) and fall to 0.
    b  = a z * product over k of ( g_k / (a z_k^2) ) ^ (1 / 2^(k+1)),   z_0 = z, z_(k+1) = g_k = p steps from z_k,
         a = -2 for c = -1 (in general the product of 2 z along the orbit of 0)
    b' = its derivative (carried along in the same loop)
    q  = R * ( -Re b, -Im b, |b'| * m * h ),   R = half the width of the middle ball
    INSIDE if q is in the middle ball, or in a ball that hangs on it through a chain that starts off the flat plane
        (the object's own recipe, plus one 2 x 2 table of whole numbers that remembers at which fraction the chain started).

Cost, MEASURED (`solids27.py time`): 14 times the balls object's own verdict in numpy (14 s against 1 s for 2.4
million points). Not built and not checked: a distance for the ray marcher. REASONED: with thorns at every size along
the outline no safe long step exists near the flat plane, so a shader would have to creep there.

## 6. Corrections to the brief

1. "Carry the match off the flat plane" (section 3, B2) assumes the rim match fractions -> halvings is the thing to
   extend. Measured, it is the one part that must stay in the flat plane: taken off it (ways B and C) it presses
   the biggest bulb to 3.6 : 1 and small bulbs to nothing, because its slope is zero exactly at the fractions, and
   the fractions are where the bulbs stand. The way that keeps bulbs round (A) does not use the rim match at all.
2. "This can only ever be c = -1 and its relatives" (my task, item 4): true for the flat match, not for way A,
   which runs for the rabbit with an exact flat cut (0 wrong of 20000). See section 4.
3. Round 25 (klein) "no re-spacing with bounded squeeze turns the flat tree into the basilica": confirmed with a
   number (0.07 degrees of the true rim spread over 10 degrees of the ball at every kiss). Added: the exact verdict
   itself is cheap and holds for any choice of the moves, so an exact flat check proves nothing about the match.
4. "A round ball cannot come to a point, so exact balls and pinched bodies exclude each other" (section 3): right,
   and what the carry-over gives instead is seen: under way A two carried bodies meet along a short upright edge
   (c = -1) or a blade (rabbit), under way F in a clean pair of cones, at the price of fins elsewhere.

## 7. Not done, not checked

- The honeycomb grid, other values of the size dial t, c other than -1 and the rabbit, other powers.
- Roundness of the bulbs on bulbs (second generation) and of the rabbit's bulbs one by one (for the rabbit only the
  skin map of section 3 and the pictures).
- Whether way A looks different when each body is also given the bulbs that lean over from its neighbours
  (`OWN_ONLY = False` in `carry.py`); only the default was drawn.
- Finer solids than 560 x 420 x 300 blocks; the thorn fringe has detail at every size and will look denser when finer.
- The literal quarter-turn extension through the x-axis (section 2), and any match of the gaps between bodies
  that is better than "outside goes to outside".
- A cleaner lift near the rim: the canonical "union of all balls whose middle disc lies in the body" (round 25,
  wall, door iii) gives cones at corners and no fins, but it has no coordinate to hang bulbs on. I did not find one.
- Nothing was built into the lab, nothing under `src/` was touched, nothing was published.
