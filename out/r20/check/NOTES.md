# Round 20, section "check": trying to fail `m_w3` (wind three times, then one plane) on the Julia panel

Every statement is marked **measured**, **seen** (in a picture I looked at) or **reasoned**.

## 0. What I expected before computing anything (written first, 00:35)

Reasoned from the formula only (F = P(T(v)), T multiplies the turn round the x-axis by g, g(a) = 3a - sin(6a)/3):

- E1. The solid is the same after a third of a turn about the x-axis, for every c (v and v turned by 120 degrees
  have the same answer). So the six half-planes at 0, 60, ... 300 degrees all carry the flat picture, also for the
  rabbit. Expect: holds exactly.
- E2. Near the flat plane g(a) = a + 12 a^3 + ...: a point 10 degrees up is sent to 13.6, a point 20 degrees up to
  43.5, a point 30 degrees up to 90. So a ball of the one-plane rule that reaches 30 degrees round the axis is
  squeezed to about 16 degrees: the big bodies of the rabbit (which sit far from the x-axis and are wide in angle)
  should come out as LENSES about half as thick round the axis as they are wide, not balls. Expect: "thickest
  place" well under the flat set's; bodies line in danger on the rabbit.
- E3. Between the planes the rabbit has only thin arcs (seen in the orchestrator's cuts). In 3D an arc in a cut is a
  curved sheet. Expect: loose thin shells round the middle body -> "one piece" (strict) and "clean close up" fail
  on the rabbit at the rule's mid angles (30 and 90 degrees).
- E4. Dendrite: nothing at all between the planes. Expect three flat trees crossing on the x-axis only, each as
  thin as paper: at a fixed voxel size they fall apart sooner than the one-plane tree. "One piece" in danger.
- E5. Siegel disc: a sheet (W6). Expect "bodies" to fail the gross check (thickest place far under 0.8 of the
  flat set's) and "the solid stays" to fail or come close (a sheet thinner than a voxel loses volume).
- E6. Nudged sets. What matters is the DIRECTION of the nudge round the x-axis, three times over: bas_yz is a nudge
  at 31 degrees, which T sends to 95 degrees: the rule reads it as a pure lift of 0.058, and the one-plane rule
  loses the orbit of 0 at a lift of 0.05. Expect: bas_yz "outside" or badly changed. bas_zy is a nudge at 59
  degrees, sent to 179: the rule reads c as -1 - 0.058 i, well inside the flat period-2 disc. Expect: stays, a
  slightly skewed basilica. sm_yz is at 63 degrees, sent to 184: read as -0.75 - 0.022 i, which is just outside the
  flat Mandelbrot set (escape after about pi / 0.022 = 140 steps). Expect: "outside" at about step 140, as the
  lathe. rab_up is a lift of 1.2 degrees: g changes it by almost nothing. Expect: like the one-plane rule (stays).
- E7. Basilica, San Marco: ribs (J8 fail is known). Hair between the planes: W5 says fins. Expect "clean close up"
  to fail at 30 and 90 degrees, less so near 0 and 60.
- E8. Airplane: its bodies are tiny and near the x-axis; off the planes they are squeezed. Expect few or no round
  pieces off the plane in voxels; spines in six directions point by point.
- E9. Cauliflower: one body, six-fold scalloped; nothing to fail but "truly 3D" by dents.


## 1. Verdict in four lines

- **`m_w3` fails all eleven sets of panel2** (measured, the orchestrator's own run, `panel2-table.txt`). `along`
  fails nine and passes two (airplane, cauliflower); `twoplane` passes three; `oneplane` none (never truly 3D).
- **It is not better than `along` on the panel.** There is no set and no line where `m_w3` passes and `along` fails.
  It is worse on eight sets (the four on the x-axis by their skin, the Siegel disc, the two nudged basilicas and
  the nudged San Marco), and fails differently, not better, on the rabbit, the dendrite and the lifted rabbit.
- What it does better than `along`, and this is real: the flat picture stands exactly in three planes for every c of
  the flat plane (measured: 0 points differ on the rabbit and the Siegel disc), and it never swells into a lump
  (rabbit volume 0.97 of the one-plane yardstick; `along` 3.65).
- Two faults are built into the kind, not into the sinus profile: (a) away from its planes the rule stretches
  sideways by up to 5, which makes flakes of every wide body and whiskers on every skin; (b) the turn round the
  x-axis is tripled at every step, so for a c off the planes the inside of a body never comes to rest.

## 2. The eleven sets, one by one

Lines are panel2's (`out/r19/panel2/README.md`). "Seen" = in my pictures, named in section 6. cle = clean close up
(tiles over a line, of 120; thin line 0.10, film line 0.5 %), pie = one piece, bod = bodies, d3 = truly 3D,
sta = the solid stays.

| set | m_w3 | fails by | whole set, what a person sees | one bud, what a person sees | along, for comparison |
|---|---|---|---|---|---|
| basilica | FAIL | cle: 104 of 120 (thin to 2.37, film to 38 %); at all three widths 35, 34, 35 of 40. Bench J8 (ribs) fails too | the liked look: bodies in a row, buds in six rows 60 degrees apart, ribbed like a walnut (seen) | the first bud is a ribbed egg, round in section (thickness / width 1.01), but in the cut across the axis it is bare: its own buds lie only in its plane (under along the bud is covered with small round buds); rim whiskered; flat flakes stand on the skin half way between the planes; the bud on the bud is 0.68 as thick as the one-plane rule makes it (seen, measured) | F: cle, 24 of 120 (thin 0.81, film 2 %) |
| San Marco | FAIL | cle: 110 of 120 (film to 47 %) | as the basilica, studded with buds; half way between the planes the three bodies run together, the notches are filled (seen) | bud round (0.99); skin whiskers and dust | F: cle, 12 of 120 |
| airplane | FAIL | cle: 31 of 120 (0 wide, 2 middle, 29 fine tiles; thin 0.94, film 5 %) | a ball with six spines of beads, 4 off the flat plane; nothing wrong at this scale (seen) | a knobbly, toothed edge with short spikes, at the finest width only (0.002 wide). The mildest of its failures | passes |
| cauliflower | FAIL | cle: 30 of 120 (4, 10, 16 by width; thin 1.73) | a pumpkin with twelve grooves; cut across the axis away from the middle the outline is ragged and saw-toothed (seen) | blades and fins standing in the grooves (seen) | passes |
| rabbit | FAIL | pie: 82.1 % with no gap (needs 98.5); bod: thickest place 0.75 of the flat set's; d3: roundness 0.33; cle: 120 of 120 | a cloud of flakes and shards; only the three flat copies are whole, as plates (seen) | an ear is a thin flake: 0.49 and 0.59 as thick as wide (one plane: 1.15, 1.19; along: 4.8, 1.9); across the axis a spindle with slivers round it (seen, measured) | F: bod, d3, cle: one layered lump |
| dendrite | FAIL | pie: 98.2 % at 10 steps, 83.5 % at 12 (one plane, along: 100); tree test 3.6 (allowed 3.0; thread 2, sheet 4) | three flat trees 120 degrees apart, crossing on the x-axis; nothing at all between them (seen; area of the 30 degree cut 0.0001) | every branch is a flat ribbon half as thick as the flat tree is wide | F: bod, a lump |
| Siegel disc | FAIL | pie 90.7 %; sta: 71 % left from 40 to 80 steps; bod: thickest place 0.13 of the flat set's; d3; cle 99 of 102 | a six-armed star of thin sheets with wisps; no body (seen) | no bud to speak of: the disc is 0.008 thick at 80 steps where it is 0.45 wide, and still thinning | F: d3, cle, a terraced lump that stays |
| bas_yz | FAIL | pie 97.7 %; bod: thickest place x 0.31 of its own basilica; d3 (a ring); cle 26 of 120 | bodies crumpled like a walnut; outline hairy in every cut, the flat plane included; pinholes inside (seen) | the bud is a tuft of bristles in all three cuts (seen) | F: pie (98.19), cle 20 of 120; bud an egg, slightly lumpy |
| bas_zy | FAIL | pie 77.1 %; bod x 0.34; d3 (3 rings); cle 26 of 120 | as bas_yz | as bas_yz (not cut separately) | F: pie, cle 22 of 120 |
| sm_yz | FAIL | cle: 120 of 120 (film to 46 %) | San Marco, hardly changed (seen) | the whole skin under a film of dust, stripes of it lying along the skin (seen) | F: cle, 23 of 120 |
| rab_up | FAIL | pie: 39.2 % even with a one-voxel gap; bod; d3; cle 120 of 120 | flakes and shards, as the rabbit (seen in the sheet) | as the rabbit (not cut separately) | F: bod, d3, cle |

## 3. What I measured, by attack

**The rule's own symmetry and copies (W1, W3): hold.** Measured: the answer is unchanged by a 120 degree turn to
6e-14; both mirrors commute (0 and 4e-14). The half-plane cuts at 0, 120, 240 degrees are identical pixel for pixel,
and so are 60, 180, 300, on the rabbit, the Siegel disc, the lifted rabbit (0 of 10,354 differ) and bas_yz (1 of
12,493). On the rabbit and the Siegel disc the cut at 0 and at 60 degrees is the flat set, 0 points differ.
Basilica across the axis at x = 0: six identical buds, edges at 0.7862 in all six directions (measured; the
orchestrator's small picture makes the level ones look smaller, they are not).

**The skin (panel2's 120 tiles, plus my 45 tiles a set at 30, 60, 150 degrees, `wide30/`).** Measured:

    tiles over a line    basilica  sanmarco  airplane  cauliflower  rabbit  siegel  bas_yz  bas_zy  sm_yz  rab_up
    m_w3                 104/120   110/120   31/120    30/120       120     99/102  26      26      120    120
    along                24        12        0         0            118     113     20      22      23     115
    twoplane             0         10        0         0            72      52      15      16      12     92
    oneplane             0         0         0         0            0       0       0       outside 0      0

- On the basilica every half-plane fails except exactly the rule's own: by angle 11.25: 15 of 15, 22.5: 14, 33.75: 15,
  45: 15, 56.25: 15, 67.5: 15, 78.75: 15, and 0 of 15 at 30, 60, 90 and 150 degrees (measured). Those four are mirror
  planes of the solid, and a cut in a mirror plane hides what leans across it. The orchestrator's cuts were made at
  0, 30, 60 and 90 degrees only: exactly the places where the skin is clean. That is why it saw no hair.
- Seen (`skin-basilica.png`, `worst-m_w3.png`): a toothed outline already in the widest tile (0.2 wide, where the
  body's radius is 0.5), whiskers and a film of dust at 0.04 and 0.008 wide. Same place for the other rules:
  `along` a smooth line with droplets, `twoplane` and `oneplane` clean lines.
- The whiskers are part of the set, not slow leavers: the inside share of four tiles is the same to four figures at
  80, 320 and 1,280 steps (0.4487, 0.5025, 0.5090, 0.5552; measured).
- Control: panel2's number on the FLAT rabbit and the FLAT Siegel disc (not in its calibration): 0 of 45 tiles over
  each, worst thin 0.07 and 0.08, worst film 0.4 % and 0.1 % (measured). So the number is fair to these sets, but the
  flat rabbit sits close under both lines; one of my 15 tiles in the 60 degree copy plane, which IS the flat rabbit,
  reads film 0.7 %.
- On bas_yz and bas_zy the number does not look at the skin at all. Seen (`skin-bas_yz.png`): the tiles of `m_w3`
  are all cream with pinholes. The tile finder walks out from the body's deepest point and takes the first point
  that is not inside as the skin; in a body full of pinholes that is a pinhole. So "26 of 120" there is a count of
  pinhole tiles, and the ragged, hairy outline that the cuts show on every body (seen,
  `between-m_w3-bas_yz.png`, `bud.png` last row) is not in it. The other three rules' tiles on bas_yz do sit on
  the skin (seen).

**The 1,160 pieces.** Measured at 385 a side (face-joined pieces): 4,792 loose pieces holding 1.63 % of the
basilica; the one-plane rule on the same grid 88 pieces, 0.03 %. The share does not fall with finer voxels (biggest
piece 98.70, 98.31, 98.37 % at 129, 257, 385 a side). 74 % of the loose volume lies more than 3 degrees away from
all six planes: it is the dust and the loose needles of the tiles, not buds waiting for a finer grid.

**The rabbit between the planes** (`between-m_w3-rabbit.png`). Measured: area of the cut through the x-axis 0.655
in the flat plane, 0.281 at 10 degrees, 0.197 at 20, 0.151 at 30. Seen: at 10 degrees the ears are already slivers
and crescents; at 30 degrees only the middle body is left, with thin shells lying over it like onion skins. The
shells are real: the 30 degree area is 0.1501 at 40, 80, 160 and 320 steps. Voxels, face-joined: the biggest piece
holds 36, 52, 52, 52 % at 129, 257, 385, 513 a side (one plane: 61, 99.8, 99.9 %); with a one-voxel gap allowed
99.93, 99.95, 99.80, 99.79 % (the line is 99.97). So the flakes hang together by joins thinner than a voxel at
every size tried. The middle body is a six-sided nut: thickest place 0.260 against 0.348 flat.

**How thick bodies are round the axis** (`measure.py thick`, point by point). thickness round the axis / width in
the plane: basilica's first bud 1.01 (one plane 1.15), San Marco's 0.99, rabbit's ears 0.49 and 0.59, Siegel disc
0.02; the bud on the basilica's bud is 0.0063 thick against 0.0092 for the one-plane rule (0.68). So W5's first
sentence (a bud in a plane is as round as its flat twin at every depth) is not what I measure: buds in the planes
thin with depth too (0.87, then 0.68 of the one-plane rule's), only more slowly than between the planes. Reasoned:
g(a) = a + 12 a^3 is the plain turn only AT the plane, and a body is squeezed by as much as g pushes its edge
out: 13 % at 6 degrees off the plane, a factor 2 at 25 degrees.

**Step counts** (`measure.py stay`, 129 a side). Volume at 20, 40, 80, 160, 320 steps: basilica 0.697, 0.693, then
steady; rabbit 0.458, 0.436, steady; San Marco steady; **Siegel disc 0.350, 0.218, 0.154, 0.115, 0.089** (one plane
1.288, 1.201, 1.192, 1.192, 1.192). The Siegel sheet is still draining at 320 steps (W6 holds).

**The nudged sets: what a lifted c does** (`quick.py`, `nudge.py`, `extra.py nudge`, `screens.py`).
- I expected bas_yz and sm_yz to be "outside". Wrong: the orbit of 0 stays bounded 3,000 steps at all four.
  `m_w3` keeps the orbit of 0 at lifts where the one-plane rule loses it (rabbit lifted 0.03: stays).
- But it does not come to rest. Measured: at bas_yz and bas_zy the orbit of 0 never settles on a cycle and wanders
  through a region 1.3 across; `along`, `twoplane` and `oneplane` settle on the 2-cycle at both (one plane is
  outside at bas_zy). Of 60,000 points inside at 40 steps, the share still inside at 80, 320, 1,000, 3,000 steps is
  0.997, 0.982, 0.942, 0.836 at bas_yz and 0.999, 0.993, 0.977, 0.930 at bas_zy; for the three other rules 1.000
  throughout. So the nudged basilica of `m_w3` is a slowly leaking sponge. "The solid stays" passes it (80 over 40 =
  100 %): that line is blind to a leak this slow.
- How big a nudge the 2-cycle survives (19 directions, 0 to 90 degrees): every direction up to 0.02; at 0.03 one
  direction doubles to a 4-cycle; at 0.058, 9 of 19 directions churn or leave; `along` rests in 57 of 57 cases.
- Away from c = -1 it is worse: at c = -0.9 a nudge of 0.005 already leaves the orbit churning in 8 of 19
  directions. At sm_yz it wanders 0.43 across (nothing leaks in 3,000 steps), which goes with the film of dust on
  its whole skin. Reasoned: near the x-axis the rule multiplies the distance from the axis by 2|x| (as the flat
  rule) but triples the turn round the axis, and tripling an angle at every step never settles; each step c then
  pushes the point off the axis again in its own direction. Only at c = -1 does the cycle pull the point onto the
  axis completely (the flat cycle there is the strongest there is), which hides the churn until the nudge is big.
- All three copies stay identical for a lifted c (measured above), so the answer to "what does a lifted c do to
  three planes that all feed the flat plane" is: the planes keep agreeing with each other, and what they agree on
  is no longer a clean body.

**Two screens that take seconds** (`screens.py`, `screens.json`; I ran every registered wind rule, reading the other
sections' rules through the bench, judging none of them):

    rule       ear 1  ear 2 | of 57 nudged cases: rests on the 2-cycle / longer cycle / never settles / leaves
    oneplane   1.15   1.19  | 47 / 0 / 0 / 10
    twoplane   1.06   1.09  | 51 / 6 / 0 / 0
    along      4.83   1.92  | 57 / 0 / 0 / 0
    m_w3       0.49   0.59  | 35 / 5 / 15 / 2
    m_w3f      0.71   0.76  | 36 / 7 / 10 / 4
    m_w5       0.27   0.34  | 18 / 12 / 26 / 1
    m_w3lin    0.01   0.04  | 24 / 10 / 23 / 0
    w_b05      0.69   0.72  | 36 / 5 / 12 / 4
    w_b10      0.83   0.85  | 38 / 5 / 10 / 4
    w_b15      0.98   0.98  | 40 / 4 / 6 / 7
    w_b20      1.11   1.11  | 41 / 4 / 4 / 8      (m_w3b20 the same)
    w_b25      1.16   1.25  | 41 / 7 / 1 / 8      (m_w3b25 the same)
    m_w3saw    1.12   1.32  | 43 / 6 / 0 / 8
    w_c10      0.55   0.58  | 32 / 7 / 17 / 1
    w_c15      0.77   0.79  | 36 / 5 / 16 / 0
    w_5b05     0.52   0.53  | 25 / 10 / 21 / 1

An exact band of 15 degrees or more makes the ear as thick as it is wide at its middle (it says nothing about the
shards round it), and cuts the churn; none of them rests as `along` does.

## 4. My expectations against what came out

- E1 right. E2 right, and worse than expected (0.49, with shards). E3 right (120 of 120 tiles, 82 % strict).
- E4 right. E5 right ("stays" fails at 71 %).
- **E6 wrong**: all four nudged sets keep the orbit of 0; the fault is not escape but churn and a slow leak.
- **E7 half wrong**: I expected hair at 30 and 90 degrees. It is the other way round: 30, 60 and 90 are the only clean
  half-planes and everything between them is whiskered.
- E8: wrong about voxels mattering, right about six spines; I did not expect the fine-width teeth.
- E9: wrong, the cauliflower fails "clean" (30 of 120), fins in the grooves.

## 5. Holes in the panel that this rule found

1. "The solid stays" (80 steps over 40 at least 90 %) passes a body that loses 16 % by 3,000 steps. A line "the
   orbit of 0 comes to rest, or 1,000 over 40 at least 99 %" would catch it.
2. The tile finder of `wide.py` lands on a pinhole when the inside of a body has pinholes, and then the 120 tiles
   do not show the skin (bas_yz and bas_zy of this rule). It should walk in from outside, or skip holes smaller than
   the tile. And the hair number undercounts a ragged, bristly skin (the README's limit 1).
3. A rule with mirror planes of its own looks clean in exactly those planes. Panel2's eight angles happened to miss
   them (only 90 degrees is one); a checker who cuts only at the rule's "own" angles sees a clean skin.
4. The dendrite's "one piece" fail is a matter of thinness in voxels: reasoned, the three flat trees are joined at
   the origin (0 is on the flat tree). The honest fault there is "three pressed leaves, nothing between".

## 6. Files (all in out/r20/check/)

- `sheet.png`: the sheet for the user: 11 sets x 4 rules (front, along the x-axis, cut across), verdict words, then
  the basilica's skin for the four rules, then one bud for the four rules. Looked at, all three parts.
- `between-m_w3-<set>.png` for rabbit, siegel, dendrite, basilica, sanmarco, cauliflower, airplane, bas_yz, bas_zy,
  sm_yz, rab_up: half-planes at 0 to 60 degrees by 10, cuts across the axis, the 30 degree half-plane at 80, 160,
  320 steps, zooms. Looked at: all eleven. Airplane: clean balls on a line in every half-plane, thin spines in
  the planes at 0 and 60 degrees. rab_up: even its cut in the flat plane is now separate ragged blobs; between the
  planes slivers and onion shells as for the rabbit.
  NOT looked at: the two comparison sheets `between-oneplane-rabbit.png`, `between-along-rabbit.png`.
- `worst-m_w3.png`: per set the worst tiles by the new and by the old hair number (looked at). `skin-basilica.png`
  (looked at), `skin-cauliflower.png` (looked at: clean at 33.75 degrees at this skin point, ragged with spikes at
  78.75), `skin-bas_yz.png` (looked at, see section 3). `bud.png` (looked at).
- `closeup.png`: voxel boxes (257 a side) round one bud, for `m_w3` and `along` only (I stopped the job after two
  columns). Looked at, top five rows. Seen: the basilica's bud under `m_w3` is a ribbed egg with a few small buds in
  its own plane, and flat flakes (discs seen edge on) and small fins stand on the middle body's skin half way
  between the planes; under `along` the same bud is covered with small round buds in rows. The rabbit's ear is a
  spray of flakes for `m_w3` and a ribbed wall for `along`. `_mw3_tiles.png`, `_bas_x0.png`: working pictures (looked at).
- Numbers: `panel2-table.txt` (panel2's lines for the four rules), `quick.json`, `measure.json`, `nudge-*.json`,
  `extra.json`, `screens.json`, `worst-m_w3.json`, `wide30/scores-m_w3.json`, `between-*.json`, `logs/`.
- Code: `quick.py`, `solids.py`, `rabbit.py`, `measure.py`, `tiles30.py`, `worst.py`, `skin.py`, `bud.py`,
  `nudge.py`, `extra.py`, `screens.py`, `sheet.py`, `closeup.py`.

## 7. Not done, and what I did not touch

- No second panel2 run: all panel numbers are the orchestrator's run. I wrote nothing into `out/r19/panel2/`
  (my 30, 60, 150 degree tiles are in `out/r20/check/wide30/`); I read its tiles, scores and results.
- No Mandelbrot solid drawn, looked at or described.
- The bench's J1 to J8 were not re-run; J8 and the 1,160 pieces are the orchestrator's numbers, the pieces re-counted
  my own way.
- Not looked at closely: the airplane's beads off the flat plane (round or needles), sm_yz at one bud.
- The lab's own renderer was not used: every 3D picture here is the rough voxel renderer.
