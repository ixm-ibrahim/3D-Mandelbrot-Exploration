# Round 19, panel2: the Julia panel, made fit to certify a pass

Eleven Julia sets. A rule must pass every one before its Mandelbrot solid may be drawn. This is the round-18
panel (`out/r18/panel/`, untouched) with the six faults its review found put right. Stand-alone numpy and scipy;
the iteration and the rule registry are the round-16 bench's. Nothing here touches `src/` or builds a page.

Every statement below is marked **measured**, **seen** (in a picture I looked at) or **reasoned**.

## How to run (from the project root, `PYTHONIOENCODING=utf-8`, one core per process)

    python out/r19/panel2/panel2.py run <rule>            everything for a new rule, 15 to 40 minutes
    python out/r19/panel2/panel2.py table [<rule> ...]    old verdict and new verdict side by side (no rule named: writes table.txt)

`run` is these steps, each of which can be run alone and keeps its numbers:

| step | command | what it does | time |
|---|---|---|---|
| orbit of 0 | `panel2.py orbits [<rule>]` | one orbit per off-plane c: does 0 stay bounded for 3,000 steps? | seconds |
| old tests | (inside `run`: the round-18 panel on its 7 flat-plane sets) | cut, one piece, bodies, truly 3D, mirror | 5 to 15 min |
| extras | `panel2.py extra <rule>` | "the solid stays" (volume at 20, 40, 60, 80 steps), airplane spines, cauliflower dents | 1 to 2 min |
| off-plane sets | `panel2.py runc <rule>` then `panel2.py fitd3 <rule>` | the four new sets, only where the orbit of 0 stays | 2 to 6 min |
| 120 tiles | `wide.py <rule>:<set> [...]` | the close-cut tiles, kept as they are in `wide/<rule>-<set>.npz` | 0.5 to 3 min a set |
| hair number | `panel2.py score` | the new number on every kept tile set (`wide/scores.json`) | 7 s a set |
| verdict moves | `panel2.py moves` | how the skin verdict changes with where one looks (`moves.txt`) | seconds |
| pictures | `sheets.py hair across groupc montages` | the sheets named below; `worst/<rule>-<set>.png` for every set | 1 min |

A rule with special planes of its own: give its mid angles as a third field, `wide.py <rule>:<set>:30,60`.

| file | what |
|---|---|
| `panel_r18.py` | the round-18 panel's code, unchanged (the "old" column comes from it) |
| `panel2.py` | new sets, new lines, new verdicts, the table |
| `wide.py`, `hairnum.py` | the 120 tiles; the new hair number (works on kept tiles, so it can be changed without cutting again) |
| `results/` | every number (`<rule>.json` old and new sets, `extra-<rule>.json`, `orbits.json`, `stay-calib.json`) |
| `table.txt`, `moves.txt` | all lines of all rules, old beside new; the verdict-moves table |
| `hair-calibration.png` | what the new hair number counts and what it leaves alone (start here) |
| `across.png` | the airplane's spines and the cauliflower's dents, counted |
| `groupc.png` | the new off-plane sets, six rules |
| `worst/<rule>-<set>.png` | per set: the six worst tiles by the new number AND the six worst by the old one |

## The sets

| group | set | c | note |
|---|---|---|---|
| A, c on the x-axis | basilica, sanmarco, airplane, cauliflower | as in round 18 | |
| B, c in the flat plane | rabbit, dendrite, siegel | as in round 18 | |
| C, the first step off both | bas_yz | (-1, 0.05, 0.03) | the basilica nudged, mostly along y |
| C | bas_zy | (-1, 0.03, 0.05) | the basilica nudged, mostly along z |
| C | sm_yz | (-0.75, 0.01, 0.02) | San Marco nudged |
| C | rab_up | (-0.122561, 0.744862, 0.015) | the rabbit lifted out of the flat plane |

Round 18's group C (the rabbit turned 90 and 30 degrees) is dropped. **Measured**: at "rabbit turned 30 degrees"
the orbit of 0 leaves at step 3 for one plane, two planes, away, p_tt16, p_tt256, p_tt1024, at step 5 for p_h4,
10 for p_ss, 14 for along; only the lathe and p_cot keep it (3,000 steps). So for nine of eleven rules that c lies
outside the rule's own bounded region and its Julia set is dust, as it should be: the old "fails: empty" there
was not a fault of those rules.

The nudges were chosen small enough that the yardstick stays inside (**measured**): one plane keeps the orbit of 0
at a lift of 0.03 above c = -1 and loses it at 0.05 (step 27); at the rabbit it keeps it at a lift of 0.015 and
loses it at 0.02 (step 58). Round 19's own example (-1, 0.03, 0.05) is kept as bas_zy, and there one plane is
outside (step 26) and is not judged. San Marco at the brief's example size (0.03, 0.05) is outside for one
plane, lathe, p_ss and p_cot; at (0.01, 0.02) only for lathe (step 140), p_ss (742) and p_cot (140).

## What was wrong and what was done

### 1. The hair number failed the flat set itself

Old number: every inside pixel that a 3-pixel wearing-down removes, per pixel of skin line. It counts every small
round bud. **Measured** on the flat sets (one plane cut at 0 degrees, 45 tiles each): old number worst 1.83
(basilica), 1.09 (San Marco), 1.04 (airplane), 0.16 (cauliflower), against a line of 0.3.

New number (`hairnum.py`), two parts per tile:

- **thin**: the total LENGTH of thin things, per pixel of skin line. A thing is any loose piece, or anything a
  wearing-down by a disc of 3.3 or 9.3 pixels removes. It is thin when its length squared is at least 4 times its
  area (an ellipse 3.1 times as long as wide, or thinner) and it is at least 8 pixels long; a thin thing that is
  joined to a body counts only if it sticks out of that body by 6 pixels or more (so the neck of a bud and the rim
  of a bud are not fins). Round things are never counted, whatever their size: buds, buds cut off their stalk,
  buds with buds on them.
- **film**: the share of the tile covered by loose dust or by a comb. Small bits (under 12 pixels) and thin things
  that stand more than 4 pixels clear of every body, where they are dense in two directions (fattened by 4.3
  pixels they must hold a disc of radius 6.3). A string of beads or one needle is a line and does not count.

A tile is not clean when thin is over **0.10** or film is over **0.5 %**. A set is clean when no tile is over.

Calibration (**measured**; **seen** in `hair-calibration.png`, rows A to H):

| | thin, worst tile | film, worst tile | tiles over | by eye |
|---|---|---|---|---|
| flat basilica, San Marco, airplane, cauliflower (45 tiles each) | 0.000 | 0.00 % | 0 of 180 | round buds, strings of beads: clean |
| one plane, all 9 sets cut (120 tiles each) | 0.000 | 0.00 % | 0 of 1,080 | a clean line everywhere |
| two planes, basilica | 0.038 | 0.10 % | 0 of 120 | clean |
| two planes, airplane and cauliflower; along, airplane and cauliflower | 0.000 | 0.00 % | 0 | clean |
| away, cauliflower | 0.058 | 0.00 % | 0 of 120 | a ragged, saw-toothed coast: NOT clean by eye (see limits) |
| p_tt16, airplane | 0.075 | 0.00 % | 0 of 120 | not looked at |
| p_tt256, airplane | 0.110 | 0.10 % | 1 of 120 | a faint fuzz on one edge: on the line, luck |
| p_h4, cauliflower | 0.117 | 0.50 % | 4 of 120 | a ragged coast with fine streaks in its notches |
| away, airplane | 0.133 | 0.15 % | 2 of 120 | a ragged coast with short spikes |
| along, basilica (fin combs) | 0.81 | 2.0 % | 24 of 120 | combs of parallel fins |
| along, San Marco | 0.42 | 0.9 % | 12 of 120 | small fin combs |
| away, basilica (whiskers) | 1.24 | 24.4 % | 82 of 120 | whiskers, streaks, dust |
| p_tt1024, basilica (dust film) | 0.72 | 12.2 % | 15 of 120 | a film of dust at 45 degrees, needles at 11 and 34 |
| two planes, San Marco | 1.36 | 0.0 % | 10 of 120 | blade-shaped slivers lying against the skin |

So the three things the brief asked for hold: the flat sets score clean (0 of 180 tiles), and along's fin combs,
away's whiskers and p_tt1024's film of dust fail by a wide margin. The line 0.10 sits between the cleanest
failing picture I accept as a fault (0.133) and the highest clean one (0.058 by number; 0.038 if away's saw edge
is set aside). That gap is narrow at the low end: six tile sets of 74 have their worst tile between 0.04 and 0.14 (three
pass, three fail) and the next failing set is at 0.31. **A rule whose worst tile is between 0.04 and 0.15 must be
judged by eye**; outside that band the number and the eye agreed on every picture I looked at.

Two things were tried and dropped (**measured**): counting loose specks one by one (the flat airplane's strings
of beads score 0.22 a skin pixel, and a dense dust film chains onto the skin and scores 0.04: no line separates
them), and counting sharp tips to catch a saw edge (the flat basilica scored 1.7 a hundred skin pixels, away's
saw-toothed cauliflower 0.5: the wrong way round).

### 2. It looked in too few places

Now 8 half-planes through the x-axis (11.25, 22.5, ... 90 degrees from the flat plane: 45 is the mid angle of
the two-plane rules, 22.5 and 67.5 of `along`), 5 skin points, 3 widths: 120 tiles a set, against 12. How the
verdict moves with the choice is in `moves.txt` and at the end of this file. **Measured**: of the 40
(half-plane, skin point) pairs, p_tt1024's basilica fails in 8, so a look at one pair passes it 4 times in 5;
the old panel's own 12 tiles pass it (it did). along's basilica fails in 18 of 40. Of the 49 tile sets that
are not clean, 13 would have been called clean from the old 12 tile places alone: p_tt1024 basilica and airplane,
p_tt256 airplane, away airplane, p_cot San Marco, bas_yz and bas_zy, p_h4 cauliflower, two planes bas_yz and
sm_yz, along sm_yz, lathe bas_yz and rab_up.

### 3. "The solid stays"

New line: volume at 80 steps at least 90 % of the volume at 40 (129 points a side, one run to 80 steps).
Calibration (**measured**, `results/stay-calib.json`): the flat sets themselves keep 98.4 to 100 % of their
area; lathe at round 18's rabbit30 100 %; p_cot there 92 % (0.846 to 0.781, still leaking slowly: close to the
line); p_ss there 31 %; along there 5 %; one plane at bas_zy 0 %. On the panel's own sets every rule keeps 97 to
100 % with one exception: **away on the Siegel disc keeps 66 %** (0.317, 0.170, 0.131, 0.112 at 20, 40, 60, 80
steps): its plates are draining, which round 18 could not see. Not asked of the dendrite (a tree has no inside).

### 4. Group C

Replaced as above. For each rule the orbit of 0 is tested first; where it leaves, the cell reads "outside" and
nothing is judged. Where it stays: one piece (as before, against the flat set of the same (x, y)), the solid
stays, bodies (against the SAME rule's solid at the un-nudged c: thickest place at least 0.8 of it, volume 0.5
to 1.5 of it; and if the un-nudged set fails "bodies", so does this), truly 3D, clean close up. No mirror and no
exact cut can be asked.

"Truly 3D" had to be changed for these sets. **Measured**: with the old count (buds standing off z = 0) the
yardstick PASSED the nudged basilica with 10 round pieces "off the plane": when c is lifted, its flat row of
buds simply moves out of z = 0. Now the buds are measured against the plane that best fits the buds themselves:
one plane 0 off it (spread 0.008), lathe 0, two planes 27 (3 round, roundness 0.21: what comes off its crumpled
bodies is not round), along 54 (25 round, 0.58).

### 5. Airplane spines, cauliflower dents, San Marco's bodies, the Siegel disc's lump

- Airplane: the middle body cut across at x = 0, point by point, 1,440 directions, 80 steps. A spine is a
  direction in which matter stands clear of the body. **Measured**, **seen** in `across.png`: one plane 2 (both
  in the flat plane), two planes 12 (10 off it: 4 strong, 8 faint), along 8 (6 off), away 4 (2 off: exactly the 2
  needed), p_tt1024 16 (14 off); the lathe is a full disc (a sheet) and fails. The old voxel count gave 2 for
  two planes and for away and 6 for along.
- Cauliflower: the outline cut across at x = 0; a dent is a place where the outline lies at least 1 % of the
  radius inside its own rubber band (convex hull). **Measured**: one plane 2 (both in the flat plane), two
  planes 32 (30 off), along 8 (6 off), away 40 (38 off), lathe 0. (A first version counted places where the
  radius is smallest and gave one plane 2 "dents" at the poles of its oval: dropped.)
- San Marco's "bodies" line passed every rule because at 40 steps nothing meets at a point there, not even for
  the yardstick. It now reads NOT JUDGED unless the gross check (thickness, volume) fails.
- The Siegel disc's "bodies" line passed along's terraced lump. It cannot tell a smooth body from a layered one,
  so it too reads NOT JUDGED unless the gross check fails; the terraces are failed by "truly 3D" (roundness 0.38)
  and by the close cut (113 of 120 tiles).

### 6. Old and new side by side

F: = the lines it fails there. pie = one piece, sta = the solid stays, bod = bodies, d3 = truly 3D, cle = clean close up.

```
OLD (round 18 panel, as it judged)
rule       basilica     sanmarco     airplane     cauliflower  rabbit       dendrite     siegel       rabbit90     rabbit30    
twoplane   pass         pass         pass         pass         F:pie,d3,cle F:pie,bod    F:pie,bod,d3 F:pie,d3,cle F:pie       
oneplane   F:d3         F:d3         F:d3         F:d3         F:d3         F:d3         F:d3         F:pie        F:pie       
lathe      F:d3,cle     F:d3,cle     F:d3,cle     F:d3         F:bod,d3,cle F:bod        F:d3,cle     F:bod,d3,cle F:bod,d3,cle
away       F:cle        F:cle        F:cle        F:cle        F:pie,d3,cle F:pie,bod    F:pie,bod,d3 F:pie,d3,cle F:pie       
along      F:cle        F:cle        pass         pass         F:bod,d3,cle F:bod        F:d3,cle     F:bod,d3,cle F:pie,bod,d3
p_ss       F:cle        F:cle        F:cle        pass         F:bod,d3,cle F:pie,bod    F:d3,cle     F:bod,d3,cle F:bod,d3    
p_cot      F:cle        F:cle        F:cle        pass         F:bod,d3,cle F:bod        F:d3,cle     F:bod,d3,cle F:bod,d3,cle
p_h4       F:cle        F:cle        pass         F:cle        F:pie,bod,d3 F:pie,bod    F:pie,d3,cle F:pie,bod,d3 F:pie,bod,d3
p_tt16     F:cle        F:cle        pass         F:cle        F:pie,d3,cle F:pie,bod    F:pie,bod,d3 F:pie,d3,cle F:pie       
p_tt256    F:cle        F:cle        pass         F:cle        F:pie,d3,cle F:pie,bod    F:pie,bod,d3 F:pie,d3,cle F:pie       
p_tt1024   pass         F:cle        pass         F:cle        F:pie,d3,cle F:pie,bod    F:pie,bod,d3 F:pie,d3,cle F:pie       

NEW (panel2). sta = the solid stays; "outside" = the orbit of 0 leaves, c is outside the rule's bounded region, not judged; "open(12tiles)" = no line fails, but the skin was looked at in 12 tiles only, so it is not a pass; "-" = not run
rule       basilica      sanmarco      airplane      cauliflower   rabbit        dendrite      siegel        bas_yz        bas_zy        sm_yz         rab_up       
twoplane   pass          F:cle         pass          pass          F:pie,d3,cle  F:pie,bod     F:pie,bod,d3, F:d3,cle      F:d3,cle      F:cle         F:pie,d3,cle 
oneplane   F:d3          F:d3          F:d3          F:d3          F:d3          F:d3          F:d3          F:d3          outside       F:d3          F:d3         
lathe      F:d3          F:d3          F:d3          F:d3          F:bod,d3,cle  F:bod         F:d3          F:d3,cle      F:d3,cle      outside       F:bod,d3,cle 
away       F:cle         F:cle         F:cle         pass          F:pie,d3,cle  F:pie,bod     F:pie,sta,bod F:pie,bod,d3, F:pie,bod,d3, F:cle         F:pie,bod,d3,
along      F:cle         F:cle         pass          pass          F:bod,d3,cle  F:bod         F:d3,cle      F:pie,cle     F:pie,cle     F:cle         F:bod,d3,cle 
p_ss       F:cle         F:cle         pass          pass          F:bod,d3,cle  F:pie,bod     F:d3,cle      F:cle         F:cle         outside       F:bod,d3,cle 
p_cot      F:cle         F:cle         pass          pass          F:bod,d3,cle  F:bod         F:d3,cle      F:cle         F:cle         outside       F:bod,d3,cle 
p_h4       F:cle         F:cle         pass          F:cle         F:pie,bod,d3, F:pie,bod     F:pie,d3,cle  F:cle         F:cle         F:cle         F:pie,bod,d3,
p_tt16     F:cle         F:cle         pass          F:cle         F:pie,d3,cle  F:pie,bod     F:pie,bod,d3, F:pie,d3,cle  F:pie,d3,cle  F:cle         F:pie,d3,cle 
p_tt256    F:cle         F:cle         F:cle         F:cle         F:pie,d3,cle  F:pie,bod     F:pie,bod,d3, F:d3,cle      F:d3,cle      F:cle         F:pie,d3,cle 
p_tt1024   F:cle         F:cle         F:cle         F:cle         F:pie,d3,cle  F:pie,bod     F:pie,bod,d3, F:d3,cle      F:d3,cle      F:cle         F:pie,d3,cle
```

How the skin verdict moves with where one looks (`moves.txt`; thin and film are the worst tile; "old 12" = the new number on the old
panel's 12 tile places only; the last column is the chance of a pass if only ONE half-plane and ONE skin point were cut):

```
rule-set               tiles    thin  film %   over half-planes skin points     pairs     old 12  pass chance if ONE (half-plane, skin point) pair were looked at
along-airplane           120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
along-bas_yz             120   0.541    2.07     20      7 of 8      5 of 5  16 of 40  not clean   60 %
along-bas_zy             120   0.541    2.07     22      8 of 8      5 of 5  18 of 40  not clean   55 %
along-basilica           120   0.810    1.99     24      6 of 8      5 of 5  18 of 40  not clean   55 %
along-cauliflower        120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
along-rab_up             120   2.879    8.45    115      8 of 8      5 of 5  40 of 40  not clean    0 %
along-rabbit             120   4.276    7.48    118      8 of 8      5 of 5  40 of 40  not clean    0 %
along-sanmarco           120   0.424    0.91     12      2 of 8      4 of 5   8 of 40  not clean   80 %
along-siegel             120   3.574    9.49    113      8 of 8      5 of 5  40 of 40  not clean    0 %
along-sm_yz              120   0.826    1.74     23      6 of 8      5 of 5  14 of 40      clean   65 %
away-airplane            120   0.133    0.15      2      2 of 8      1 of 5   2 of 40      clean   95 %
away-bas_yz              120   0.444   11.37     38      8 of 8      5 of 5  24 of 40  not clean   40 %
away-bas_zy              120   0.444   11.37     36      8 of 8      5 of 5  23 of 40  not clean   42 %
away-basilica            120   1.243   24.43     82      6 of 8      5 of 5  30 of 40  not clean   25 %
away-cauliflower         120   0.058    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
away-rab_up              120   1.457    4.11     74      8 of 8      5 of 5  35 of 40  not clean   12 %
away-rabbit              120   1.552    4.24     65      8 of 8      5 of 5  33 of 40  not clean   18 %
away-sanmarco            120   1.880   42.78     88      6 of 8      5 of 5  30 of 40  not clean   25 %
away-siegel              120  18.255   62.30    101      7 of 8      5 of 5  35 of 40  not clean   12 %
away-sm_yz               120   3.631   46.27    117      8 of 8      5 of 5  40 of 40  not clean    0 %
flat-airplane             45   0.000    0.00      0      0 of 1     0 of 15   0 of 15          -  100 %
flat-basilica             45   0.000    0.00      0      0 of 1     0 of 15   0 of 15          -  100 %
flat-cauliflower          45   0.000    0.00      0      0 of 1     0 of 15   0 of 15          -  100 %
flat-sanmarco             45   0.000    0.00      0      0 of 1     0 of 15   0 of 15          -  100 %
lathe-bas_yz             120   0.324    0.22      3      2 of 8      2 of 5   3 of 40      clean   92 %
lathe-bas_zy             120   0.465    0.50      4      2 of 8      2 of 5   3 of 40  not clean   92 %
lathe-rab_up             120   4.266   10.27     75      7 of 8      5 of 5  29 of 40      clean   28 %
oneplane-airplane        120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
oneplane-bas_yz          120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
oneplane-basilica        120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
oneplane-cauliflower     120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
oneplane-rab_up          120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
oneplane-rabbit          120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
oneplane-sanmarco        120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
oneplane-siegel          120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
oneplane-sm_yz           120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
p_cot-airplane           120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
p_cot-bas_yz             120   0.402    0.28      7      6 of 8      2 of 5   6 of 40      clean   85 %
p_cot-bas_zy             120   0.402    0.28      6      5 of 8      2 of 5   5 of 40      clean   88 %
p_cot-basilica           120   0.484    0.49     14      6 of 8      4 of 5  10 of 40  not clean   75 %
p_cot-cauliflower        120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
p_cot-sanmarco           120   0.374    0.65      4      4 of 8      1 of 5   4 of 40      clean   90 %
p_h4-airplane            120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
p_h4-basilica            120   2.014    4.73     47      7 of 8      5 of 5  27 of 40  not clean   32 %
p_h4-cauliflower         120   0.117    0.50      4      4 of 8      2 of 5   4 of 40      clean   90 %
p_ss-airplane            120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
p_ss-bas_yz              120   1.254    0.90     19      7 of 8      5 of 5  14 of 40  not clean   65 %
p_ss-basilica            120   0.753    0.67     16      6 of 8      4 of 5  14 of 40  not clean   65 %
p_ss-cauliflower         120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
p_tt1024-airplane        120   1.128    6.40      3      1 of 8      3 of 5   3 of 40      clean   92 %
p_tt1024-bas_yz          120   1.361    5.63     44      8 of 8      5 of 5  27 of 40  not clean   32 %
p_tt1024-bas_zy          120   1.361    5.63     39      8 of 8      5 of 5  25 of 40  not clean   38 %
p_tt1024-basilica        120   0.719   12.23     15      5 of 8      4 of 5   8 of 40      clean   80 %
p_tt1024-cauliflower     120   0.856    6.90     18      7 of 8      5 of 5  15 of 40  not clean   62 %
p_tt1024-rab_up          120   1.771    2.00     92      8 of 8      5 of 5  37 of 40  not clean    8 %
p_tt1024-rabbit          120   1.635    4.05     71      8 of 8      5 of 5  37 of 40  not clean    8 %
p_tt1024-sanmarco        120   1.024   14.37     28      7 of 8      5 of 5  18 of 40  not clean   55 %
p_tt1024-sm_yz           120   1.154    5.98     37      8 of 8      5 of 5  24 of 40  not clean   40 %
p_tt16-airplane          120   0.075    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
p_tt16-basilica          120   0.959    8.41     46      7 of 8      5 of 5  29 of 40  not clean   28 %
p_tt256-airplane         120   0.110    0.10      1      1 of 8      1 of 5   1 of 40      clean   98 %
p_tt256-basilica         120   0.849    8.94     28      7 of 8      5 of 5  22 of 40  not clean   45 %
p_tt256-cauliflower      120   0.311    0.98     13      7 of 8      4 of 5  13 of 40  not clean   68 %
p_tt256-sanmarco         120   0.993   17.02     35      7 of 8      5 of 5  20 of 40  not clean   50 %
twoplane-airplane        120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
twoplane-bas_yz          120   1.026    0.69     15      5 of 8      5 of 5  11 of 40      clean   72 %
twoplane-bas_zy          120   0.454    0.69     16      5 of 8      5 of 5  13 of 40  not clean   68 %
twoplane-basilica        120   0.038    0.10      0      0 of 8      0 of 5   0 of 40      clean  100 %
twoplane-cauliflower     120   0.000    0.00      0      0 of 8      0 of 5   0 of 40      clean  100 %
twoplane-rab_up          120   1.339    1.99     92      8 of 8      5 of 5  38 of 40  not clean    5 %
twoplane-rabbit          120   1.646    4.04     72      8 of 8      5 of 5  38 of 40  not clean    5 %
twoplane-sanmarco        120   1.360    0.00     10      5 of 8      3 of 5  10 of 40  not clean   75 %
twoplane-siegel          120   0.346    3.54     52      8 of 8      5 of 5  30 of 40  not clean   25 %
twoplane-sm_yz           120   0.733    0.49     12      6 of 8      5 of 5  10 of 40      clean   75 %
```

What changed, cell by cell (**measured**):

- two planes on San Marco: pass -> fails "clean" (10 of 120 tiles, blade-shaped slivers against the skin at
  22.5 to 67.5 degrees; **seen**, `hair-calibration.png` row H). The reference look therefore passes 3 of 4 on
  the x-axis by this panel. Whether those slivers matter is for the eye; the number is far over the line (1.36).
- p_tt1024 on the basilica: pass -> fails "clean" (film 12.2 %, 15 of 120 tiles), as the reviewer found by eye.
- p_tt1024 and p_tt256 on the airplane: pass -> fail "clean" (3 and 1 of 120 tiles; p_tt256's is on the line).
- lathe on basilica, San Marco, airplane: no longer fails "clean" (its cut through the axis is the flat set).
- away on the cauliflower: fails "clean" -> passes. This is a FAULT OF THE NEW NUMBER, see limits.
- p_ss and p_cot on the airplane: fail "clean" -> pass. The old number was 0.32 for both (two hundredths over its
  line); the 120 tiles find nothing thin at all (0.000).
- p_cot on San Marco stays a fail, but only because 120 tiles were cut: on the old 12 tile places the new number
  finds nothing (4 of 120 tiles fail, in 4 of 40 places).
- away on the Siegel disc: now also fails "the solid stays" (66 %).
- every rule that had a solid on rabbit90 or rabbit30 loses those cells; the four new cells replace them.

**No rule passes the panel.** No rule passes all four off-plane sets either.

## Limits: what this panel still cannot certify (read before trusting a pass)

1. **A ragged or saw-toothed skin is not counted** (**seen**, `worst/away-cauliflower.png`, lower strip:
   serrated coasts with cliffs; thin 0.06, film 0). The new number counts long thin things and dust, not short
   teeth. away fails three other group-A cells, so no verdict of this round hangs on it, but a rule whose only
   fault is a saw edge would get through. Until a measure exists, the lower strip of every `worst/` picture (the
   six tiles the OLD number calls worst) must be looked at by eye.
2. **A body that changes shape without getting thinner is not counted.** **Seen** in `groupc.png`: one plane's
   balls become domes with a flat underside on every nudged set; the "bodies" check passes them (thickest place
   x 0.91, volume x 0.91). The panel has no line that says "a ball stayed a ball".
3. The thin line 0.10 has numbers close on both sides (0.058, 0.110, 0.133). Between 0.04 and 0.15 the eye decides.
4. Lines within a tenth of their threshold on the new sets: along bas_yz "one piece" 98.19 % against 98.5;
   two planes bas_yz "bodies" 0.82 against 0.8; away's airplane 2 spines off the plane against 2.
5. The 120 tiles cover a quarter turn (11.25 to 90 degrees) on one side of the flat plane, the biggest body met
   in each half-plane, 80 steps. The other three quarters are covered only by symmetry, which holds for every
   rule run so far and must be checked for a new one (the mirror line does that on groups A and B only).
6. Everything but the cuts is voxels at 257 a side, as before.
7. The orbit-of-0 test is one orbit and 3,000 steps. Near San Marco escape is slow (p_ss leaves at step 742); a c
   whose orbit leaves after step 3,000 would be called inside.
8. The 120 tiles were cut for 74 (rule, set) pairs: every pair of the five calibration rules and p_tt1024 that
   has a skin, and for the other round-17 rules every pair that would otherwise have passed. Where they were not
   cut the "clean" line says so in words ("ONLY the old panel's 12 tiles"), fails if those fail and is left
   OPEN if they do not: a cell with no failing line and an open skin line prints `open(12tiles)`, not pass.
   (No cell of the grid above is in that state.)
9. Not done: a tear test (the bench's J6 stays the test), ribs off the basilica, and the review's remark that
   "reaches straight up from the meeting point" is measured in a plane that is exact for two-plane rules.
