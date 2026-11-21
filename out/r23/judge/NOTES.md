# Round 23, section "judge": notes

I did not do the work of this round. Everything below marked **measured** is a number from my own scripts in this
folder (my orbit loop `jl.stay`, my points, my grids); **seen** is from a picture I opened; **reasoned** is argument.
Nothing outside `out/r23/judge/` was written. Internal names are used here and nowhere in the user's pictures.

Names: `cones` = the cone section's "welded cones" (every step); `cones1`, `cones2`, `cones3` = the same for the first
1, 2, 3 squarings of each orbit and the one-plane rule after that (design section's `cones1`); `alongonce` = along for
the first squaring, then one plane.

## 0. Are these the same rules? (`jl.py` run as a script, log `j0_same.log`)

I typed one plane, two planes, along, along once, the welded cones and cones1/2 again from their written formulas and
compared them with the sections' own on 200,000 points (flat points, points on the upright axis and 0 among them),
steps 0 to 2: largest difference 8e-14 or less for all seven; all finite; length squared to 3e-14. **measured**
My loop against the library's `M.stay`: 0 of 60,000 counts differ (along, cones1, rabbit). **measured**
`alongonce` (round 21's `alongmem.c_wake1`) IS "along for the first squaring, then one plane" to 8e-14. **measured**

## 1. Basics: flat picture, lift, leak, dendrite (`j1_basic.py`, `j1_basic.log`)

Ten rules (one plane, two planes, along, along once, cones, cones1, cones2, design's pillowJ, lens, bristor):
- flat check, 20,000 flat points, 60 steps: 0 verdicts differ for every rule on the Mandelbrot set, c = -1, c = -0.75,
  rabbit, Siegel disc. **measured**
- lift by a millionth: every rule keeps all or all but one of 2937 / 4386 / 2752 points (c = -1, c = -0.75, rabbit);
  Siegel: cones loses 3 of 3664, pillowJ 8, the rest 0 or 1. **measured**
- share of a box inside after 30 / 80 / 200 steps. Rabbit: one plane 0.0159 / 0.0155 / 0.0155; along once 0.0244 /
  0.0236 / 0.0236; cones1 0.0230 / 0.0223 / 0.0223; cones 0.0341 / 0.0323 / 0.0322; along 0.0579 / 0.0571 / 0.0571.
  Siegel: cones 0.0399 / 0.0325 / 0.0303 (**it leaks**: the cone section's 0.0404 / 0.0329 / 0.0310 holds); pillowJ
  0.0323 / 0.0302 / 0.0295; two planes 0.0327 / 0.0307 / 0.0305; bristor 0.0371 / 0.0340 / 0.0332. cones1 does not leak. **measured**
- dendrite c = i: 0 of 120,000 box points inside at 80 steps for all ten (along 39 and bristor 11 at 30 steps, 0 at 80). **measured**

## 2. Bodies off the flat picture on fine blocks (`j2_bodies.py`; logs `j2_rabbit.log`, `j2_basilica.log`, `j2_more.log`)

Blocks of 0.008, upper half, 100 steps. A body off the flat picture = a lump left after peeling 0.032 that lies wholly
above z = 0.05, grown back to full size. "Grounded" pieces are those that reach the flat plane. JOINED = in a grounded
piece when blocks must share a face; TOUCHING = only when a corner is enough; FLOATING = neither (gap given).
`j2_rabbit-firsttry.log` is my first run with a worse definition (distance to the single biggest piece); kept, not used.

Rabbit (**measured**):

| rule | thin (thinner than about 0.05) | bodies off the flat picture: joined / touching / floating | longest : thick, largest | volume not holding on, even by corners |
|---|---|---|---|---|
| one plane | 3.0 % | none | - | 0.0 % |
| along once | 2.6 % | 10: 4 / 1 / 5; the biggest (volume 0.046) FLOATS, gap 0.11 | 2.22 | 14.5 % |
| cones1 | 2.9 % | 6: 2 / 4 / 0; two big (0.063, 0.020), both touching | 1.41 | 0.0 % |
| cones2 | 3.6 % | 16: 2 / 14 / 0 | 3.08 | 0.1 % |
| cones | 20.7 % | 65: 6 / 59 / 0 | 3.49 | 1.0 % |
| pillowJ | 10.3 % | 26: 2 / 24 / 0 | 2.56 | 1.2 % |
| along | 12.0 % | one piece, 3.6 times one plane's volume (229 small lumps, all joined) | 7.69 | 0.0 % |
| two planes | 10.7 % | 44: 34 / 4 / 6 | 3.19 | 4.5 % |

Two more shapes off the x-axis with bodies (**measured**): c = 0.2823 + 0.5301i (four bodies round each meeting point):
along once 11 bodies, 10 joined, none floating, up to 2.49; cones1 8, all touching, up to 1.66.
c = -0.5043 + 0.5628i (five): along once 10 bodies, 6 FLOATING (the biggest, gap 0.14), up to 4.11; cones1 9, all
joined, up to 1.85. Siegel disc: neither has a separate body off the flat picture.

c = -1 (**measured**): cones1 has one big round body per half (volume 0.078, 1.05 to 1, middle at y = +0.52, z = 0.77)
and one small one on the other side (0.0017, at y = -0.32): lopsided. "Floating, gap 0.016" for the bud straight
above the middle body under two planes / along / along once is two blocks: a point contact my grid misses, not a
floating body.

## 3. Trying to make cones1 fail; c = -1 against along (`j3_attack.py`, `j3_attack.log`)

a. Lopsidedness, share of the inside whose verdict changes (**measured**). c = -1, y to -y: one plane, two planes,
   along, along once 0.0 %; cones1 24.4 %, cones 38.0 %. Rabbit, the half turn the flat rabbit has: one plane 0.0 %;
   two planes 21 %, along 32 %, along once 32 %, cones1 35 %, cones 48 %. Above / below: 0.0 % for all.
   So cones1 breaks a symmetry of c = -1 that along keeps; on the rabbit along once is as lopsided as cones1.
b. c = -1, separate arcs of inside on rings round the x-axis (**measured**). Round the middle body (x = 0, radius 0.56
   to 0.74): one plane 2, two planes 4, along 8, along once 8, cones1 6, cones2 6. Round the next body (x = -1, radius
   0.24): two planes 8, along 16; one plane, along once, cones1: the ring lies wholly inside and no larger ring meets
   anything. So cones1 is behind along on c = -1.
c. c = -0.12 + 0.75i turned out of the flat plane (**measured**): one plane, two planes, along once, cones1, cones2 are
   EMPTY from 3 degrees on; cones nearly (0.0027 at 3, 0.0001 at 5); along (0.064 at 10) and pillowJ (0.025) stay.
   Design expected cones1 empty at 10 degrees without running it: confirmed.
d. Mandelbrot solid, 300,000 points (**measured**): along once differs from one plane on 2 points, cones1 on 1, cones2
   on 8; nothing further than 0.3 from the flat plane. along: 5 times one plane's volume, 39 % of it further than 0.3.
e. Where cones1's extra bodies hold on (**reasoned**, then **measured**). The first step sends the point
   (-0.2395, -0.1389, 0.4795) on the upper cone exactly onto the rabbit's meeting point. Small balls round that point
   (radius 0.08 to 0.01) show 3 patches of 16 % each, 47 % of the skin inside: the same numbers, to the digit, as one
   plane at the flat meeting point. So the extra bodies meet the middle body the way the flat rabbit's own bodies meet.
   Under `cones` (every step) the same balls show 5 or 6 patches: the crust.
f. What stands on the cones (**measured**): for cone points at 60 degrees, verdicts of cones1 and of cones equal the
   flat picture's verdict of the point rho^2 e^(i(90 deg - lon)) + c: 0 of 40,000 differ, c = -1, rabbit, Siegel, both
   cones. So the extra bodies are the flat picture a second time, one cone point per flat point.
   **reasoned**: cones1's shape is everything that one cone step throws into one plane's shape; nothing in it is
   self-similar off the flat plane, so no buds on buds.

## 4. Outside claims (`j4_outside.py`, `j4_outside.log`; `j5_cover.py`, `j5_cover.log`)

- Msltoe Sym2 / Sym3 against two planes, c = -1: differ on 3.97 % of the inside (outside1: 3.8 %). Eiffie against
  along: 2.53 % (outside1: 2.8 %). 273 and 176 points of 300,000: the same within sampling. Mandelcup (1, 1/2)
  against one plane: 0 points, c = -1 and rabbit. **measured**
- Flat check, 20,000 points: Sym2 / Sym3 rabbit 2756 differ (nothing inside at all); Eiffie rabbit 2511 differ, Siegel
  empty; mb2, quat3d, bristor, scator_ix, hyper, hopfcut, cup1: 0 on c = -1, rabbit, Siegel. **measured**
- Eiffie's formula and its date (reply 69, 27 January 2015) are in the header and body of
  `fractal_eiffie_msltoe.cpp` of Mandelbulber 2 as outside1 quotes them (fetched from GitHub). Daniel White's page says
  of the Mandelbulb: "there's good reason to believe that it isn't the real McCoy". **seen** (fetched). The year of
  Msltoe's thread was not read by anyone (forum down).
- Turn law (turn by a about the upright axis, the square turns by 2a): one plane and fold30 obey it to 2e-15 at 37,
  90, 120, 180 degrees; the welded cones only at 120; two planes, along, lathe at none. **measured**
- Briefing 2 (a): above the rabbit's meeting point, height after one step over height before: one plane 1.107 /
  1.098 / 1.074 / 1.026 at heights 0.01 / 0.075 / 0.15 / 0.3; along 1.105 / 0.997 / 0.735 / 0.070. **measured**
- Briefing 2 (b) is wrong as written: fold30, typed again from outside2's formula, passes the flat check (0 of
  20,000), is continuous (1e-6 moves the square by 1.6e-5), obeys the turn law, and its 45-degree cone holds the
  rabbit's flat picture exactly (0 of 40,000 differ); 4850 of 5191 flat-inside points stay half a degree off the cone
  (93 %), 3523 five degrees off (68 %). **measured**
- One plane = length squared, longitude doubled, Mercator latitude doubled: 2e-14. **measured**. That this is the
  published "product extension" (Cabrera, Makienko, Sienra 2015) is outside2's reading; I did not read the paper.
- Quaternion square cut to 3D: the square of a point turned round the x-axis is the square turned the same way
  (3e-14); for c = -1 turning the start point changes 0 of 300,000 verdicts. **measured**
- Bristorbrot on the upright plane y = 0 with c in that plane: 0 of 20,000 differ for c = -1, rabbit, Siegel. Each of
  its two planes is exact for a c lying in it; no clash with the proof (one c lies in both only on the x-axis). **measured**, **reasoned**
- Coverings (1800 x 3600 directions): one plane covers 2.0000, folded 0; welded cones cover 4.0000, folded 0.0000 %,
  21.7 % of directions squeezed more than 2 to 1 and 13.6 % more than 4 to 1 (cone section: 21.8, 13.5), stretch
  1.997 both ways at 59.95 degrees; along covers 0 net and turns 39 % of directions over. **measured**

## 5. Claims that did not hold

1. Design, section 5: "one plane's own bodies pass the face test, so cones1's contacts are thinner than theirs". On
   my grid (0.008) one plane's own rabbit bodies do NOT hold together by faces either (29.5 % of the upper half is
   outside the biggest face-joined piece, `j2_rabbit-firsttry.log`), and the ball test (3 e) gives identical contacts.
   "Touching at a point" is right; "thinner than one plane's" is a grid accident.
2. Briefing 2 (b) (orchestrator): see section 4. Needs "and never folds".
3. Rabbit section: the pillow's bodies off the flat plane "all joined". At 0.008 only 2 of 26 are joined by faces, 24
   touch at a point, and 1.2 % of the volume does not hold on at all; thin share 10.3 %.
4. Design, table: "cones1: 8 bodies off the flat plane" (blocks 0.02) / "4 per half" (blocks 0.01). I count 6 per half
   (2 big, 4 small). The count depends on the smallest body counted; not a number to tell.
Held: everything else I re-measured (sections 1 to 4), including outside1's two percentages, the cone section's
coverings, squeeze and Siegel leak, design's "no leak" and "along once floats", outside2's counterexample.

## 6. The verdicts asked for

- Does the best new rule beat along on c = -1? **No** (3 a, 3 b; seen in `1-shapes.png`).
- Does it beat along once on the rabbit? **Yes, by what I could measure**: nothing floats (along once: 5 of 10 bodies,
  14.5 % of the volume), bodies rounder (1.41 against 2.22), same thin share, no leak, contacts like the flat
  picture's own; and the same on the five-bodied c. I tried finer blocks, a second eye, three more c, 200 steps, the
  contact test: it did not break. What it shares with along once: a special first step, empty when c is turned 3
  degrees, one plane's Mandelbrot solid, as lopsided under the rabbit's half turn. And its extra bodies are the flat
  picture's bodies again (3 f), which is not what the user asked for.
- The fixed rule of this round is `cones`, and it fails: crust (20.7 % thin on the rabbit), Siegel leak.

## 7. The pictures (all made here, from my own depth maps: `jdep.py`, `jsheet.py`, `jcaptions.py`; cache in `cache/`)

Rough solids 340 x 255 x 220 blocks, 60 steps, picture 3.2 wide; eyes (0.45, 0.5, 1) "front" and (0.2, 1, 0.35) "above".
I opened all three in their final form (after the last change of captions and labels); captions say only what sections 1 to 4 hold.
- `1-shapes.png`: rows two planes, along, along once, cones1, cones; c = -1 and rabbit, both eyes. **seen**: two
  planes clean with four buds / shards; along eight buds and buds on buds / ribbed lump; along once buds on the middle
  body, a few on the others / separate bodies with smooth extras; cones1 smooth, two big round extra bodies on the
  middle body (four arms from above) / separate round bodies; cones crusted everywhere.
  "fewer on the others" for along once is round 22's count (6 against 16) and seen, not re-counted here.
- `2-what-others-found.png`: Msltoe Sym2, Eiffie, Mandelbulb power 2, Bristorbrot (front eye), beside two planes and
  along. **seen**: Sym2 = two-planes look, rabbit empty; Eiffie = along look, rabbit a lump with round marks;
  Mandelbulb flakes and whiskers; Bristorbrot ridged four-sided bodies, rabbit a ridged slab.
- `3-one-step-against-every-step.png`: rabbit, along for 1 / 2 / 3 / all steps (rabbit section's `along2`, `along3`
  through its loader) and cones for 1 / 2 / 3 / all. **seen**: along: separate, running together, lump with ribs,
  ribbed lump; cones: smooth round, more and some stretched, thin blades, crust.
No section's picture was passed on. The cone section's cut pictures must not be shown as clean bodies (its own warning; agreed).
The rabbit section's `sheet-n.png` and `sheet-doors.png` were not checked by me and are not among the three.

## 8. Not done, and limits

- No Mandelbrot solid was drawn; section 3 d has numbers only.
- The papers behind outside2's verdicts were not read by me; only its counterexample and formulas were re-measured.
- Of outside1's 17 formulas I ran ten and drew four; quat3d (rings), hyper, scator were not drawn here.
- The pillow on c = -1 ("fused"), the lens, the power-3 cones, design's counting argument and the rabbit section's
  hinge tries were not re-measured.
- Blocks of 0.008 cannot tell a point contact from a gap under about 0.014; the ball test (3 e) was done for one
  contact of cones1 only.
- House rule broken once: I patched `j2_bodies.py` with a shell heredoc; I then read the whole file, mended one
  broken line with the edit tool, and re-ran it.
- Time: about 100 minutes.

## 9. Files

`jl.py` (rules typed again, my loop), `j0_same.log`, `j1_basic.py/.log`, `j2_bodies.py`, `j2_rabbit.log`,
`j2_rabbit-firsttry.log`, `j2_basilica.log`, `j2_more.log`, `j3_attack.py/.log`, `j4_outside.py/.log`,
`j5_cover.py/.log`, `jdep.py`, `jdep-1..3.log`, `jsheet.py`, `jcaptions.py`, `cache/`, `ANSWERS.md`, the three pictures.
