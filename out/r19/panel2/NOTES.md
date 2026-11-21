# Round 19, panel2: working notes (2026-11-18, 22:48 to 23:55)

README.md is the manual and carries the numbers. These notes say what was predicted, what was tried, what was
dropped and why, and what is still wrong. measured / seen / reasoned on every statement.

## Blunt summary

- The six faults the round-18 review found are fixed or honestly dropped. No rule passes the new panel (measured).
- The new hair number passes the flat sets (0 of 180 tiles over a line) and fails along's fin combs (0.81),
  away's whiskers (1.24, film 24 %) and p_tt1024's dust film (12 %) (measured; seen in hair-calibration.png).
- It has ONE known blind spot: a ragged, saw-toothed skin with short teeth (away on the cauliflower passes at
  0.058; seen, not clean by eye). And the panel has ONE known hole on the new sets: a ball that becomes a dome
  (one plane on every nudged set; seen in groupc.png) passes "bodies".
- So: fit as a filter, much better than round 18 as a certificate, NOT yet a certificate on its own. A rule that
  comes through every line still needs eyes on `worst/<rule>-<set>.png` (lower strips) and on its nudged solids.

## Predictions written before testing

1. (reasoned, before any run) The old number fails the flat set because a 3-pixel wearing-down removes every
   bud under 7 pixels across, and a fractal outline has such buds at every zoom. Prediction: counting only things
   that are long for their area leaves the flat sets at zero. Result: true only after two repairs (below).
2. (reasoned) rabbit turned 30 degrees is outside nearly every rule's bounded region. Result (measured): the
   orbit of 0 leaves at step 3 to 14 for 9 of 11 rules; lathe and p_cot keep it.
3. (reasoned) One plane's period-2 and period-3 regions are thin above the flat plane, so a lift that is fair for
   the two-plane rules may be outside for the yardstick. Result (measured): it keeps the orbit of 0 at 0.03 above
   c = -1 and loses it at 0.05; at the rabbit 0.015 stays and 0.02 goes. The nudges were set from that.
4. (reasoned) San Marco sits on the edge of every rule's bounded region, so any nudge is in or out by a hair.
   Result (measured): at (0.03, 0.05) four rules are out; at (0.01, 0.02) three (lathe, p_ss, p_cot).
5. (not predicted) With c lifted, the old "buds off the flat plane" count passes the yardstick. Found only when
   the first table showed "one plane: pass" on the nudged basilica. Repaired with a best-fit plane.

## The hair number, step by step (all measured on kept tiles; pictures looked at each time)

1. First version: wear down with a diamond of 3 and of 9 pixels, call each removed bit thin if length squared
   over area >= 4. Flat basilica 0.28, flat airplane 0.92. Seen: the red marks were the RIMS of round buds. A
   diamond worn out of a round bud leaves four crescents. Changed to true discs: flat basilica 0.15.
2. Still 0.15 (basilica), 0.07 (San Marco), 0.24 (cauliflower). Seen: necks of buds and slivers at the lips of
   the cauliflower's scallops. Rule added: a thin thing joined to a body counts only if it sticks out 6 pixels or
   more. All four flat sets: 0.000 on 180 tiles.
3. Dust, first version: loose specks that sit on nothing, even through a chain of specks. Flat airplane 0.22 a
   skin pixel (its strings of beads), p_tt1024's worst film 1.05, but another film tile of p_tt1024 only 0.04:
   seen, a dense film next to the skin chains onto the skin and is taken for buds. Dropped as the judge (still
   printed as "specks").
4. Dust, second version: "film" = where small bits and thin things, more than 4 pixels clear of every body, are
   dense in two directions. First try used every removed pixel and gave the flat basilica 0.86 % (small round
   buds standing on their own). Restricted to bits under 12 pixels and thin things: flat sets 0.00 %, p_tt1024's
   film tiles 3.9, 7.0, 11.6, 12.2 %, away 16 to 24 %.
5. Speed: wearing down by a 19-pixel disc was 0.5 s a tile; done by distances now, 0.06 s a tile.
6. A sharp-tip count for saw edges was tried and dropped: flat basilica 1.7 per hundred skin pixels, away's
   saw-toothed cauliflower 0.5. The basilica's own buds end in points; a tooth and a pointed bud look the same.

Lines: thin 0.10, film 0.5 %. Where they sit (measured, worst tile of each of 74 tile sets):
clean sets at 0.000 (most), 0.038 (two planes, basilica), 0.058 (away, cauliflower: the blind spot), 0.075
(p_tt16, airplane); failing sets from 0.110 (p_tt256, airplane), 0.117 (p_h4, cauliflower), 0.133 (away,
airplane), then 0.31 and up. Film: clean sets up to 0.10 %; failing by film alone none (every film over 0.5 %
comes with thin over 0.10 except p_h4's cauliflower at exactly 0.50). The lines were set once from the first
calibration pictures (0.06 at first, 0.10 after seeing two planes on the basilica at 0.089 with the diamond) and
not moved after the round-17 rules were scored.

## The reference look and the new number

Two planes on San Marco goes from pass to fail (thin 1.36 in two mirror-image tiles, 0.2 to 0.3 in eight more).
Seen: blade-shaped bodies and slivers lying against the skin between the planes, at the finest zoom. The reviewer
called them "nearly clean by eye". The number does not: a 4-to-1 blade is a blade at any zoom. I did not move the
line to rescue the reference rule. If the user's eye says those slivers do not matter, the honest change is a
minimum SIZE in units of the body, not a higher line.

## The first step off the axis: what the pictures say (seen in groupc.png; numbers measured)

- two planes and p_tt1024 at (-1, 0.05, 0.03): the liked basilica crumples. Bodies creased all over; what comes
  off them is not round (roundness 0.21); 15 of 120 tiles not clean (blades up to 1.03 of the skin line).
- along there keeps its look best (smooth bodies, round buds, roundness 0.58) but its fin combs stay (20 of 120
  tiles) and its strict one-piece share is 98.19 % against 98.5.
- away: wrinkled, thickest place 0.31 of its own basilica's.
- one plane: each ball becomes a dome with a flat underside, buds on the rim. Thickest x 0.91, volume x 0.91:
  passes "bodies". It fails "truly 3D" (buds all in one plane, spread 0.008).
- the rabbit lifted by 0.015: every rule looks as on its own rabbit (two planes broken, along a lump).
So no rule keeps a clean, bodied, truly 3D solid one small step off the axis. That is the fair version of what
round 18's "empty at rabbit30" was trying to say.

## What is still wrong (in order of how much it matters for a pass)

1. Saw-toothed skin not counted (README limit 1). A measure is needed that tells teeth from buds; the two tries
   above failed. Idea not tried: compare each tile with the SAME tile at half the step count; a bud outline keeps
   its shape, a serrated one changes at every scale. Or roundness of the notches (the outside) instead of the
   teeth.
2. "A ball stayed a ball" on the nudged sets (README limit 2). Cheapest honest measure: the share of the nudged
   solid that differs from the un-nudged one after sliding it to the best overlap.
3. The 0.04 to 0.15 band of the thin number needs the eye.
4. The step counts are still one per set (40; close cuts 80).
5. The four off-plane sets were chosen on six rules' orbit tests. A new rule may be outside at bas_zy or sm_yz;
   then those cells read "outside" and say nothing. A rule that is outside at ALL four would pass group C
   untested; `table` shows that plainly but does not forbid it.
6. `run` for a new rule was not exercised end to end in this round (its steps were, one by one).

## Housekeeping

- Only `out/r19/panel2/` was written. `out/r18/panel/tiles/` is read (old pictures) and nothing else outside.
- At most four of my processes ran at once except for two short overlaps (a scorer beside four queues, about two
  minutes; a doubled `fitd3` start, about one minute, re-run cleanly afterwards and the result files checked).
- Files named report.md cannot be written here; this file and README.md stand in.
