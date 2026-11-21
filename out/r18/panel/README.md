# Round 18: the Julia panel

Nine Julia sets. A rule must pass every one of them before its Mandelbrot solid may be drawn. Stand-alone numpy and
scipy; the iteration and the rule registry come from the round-16 bench (`out/r16/bench/bench.py`, `rules.py`, which
also loads the round-17 rules). Nothing here touches `src/` or builds a page.

## How to run (from the project root, `PYTHONIOENCODING=utf-8`, one core per process)

    python out/r18/panel/panel.py run <rule> [<rule> ...]     all nine sets: numbers, tiles, sheets/<rule>.png (10 to 25 minutes a rule)
    python out/r18/panel/panel.py ribs <rule>                  the rib number (kept in results/ribs-<rule>.json; 2 minutes)
    python out/r18/panel/panel.py table [<rule> ...]           pass / fail lines in plain words; with no rule named also writes table.txt
    python out/r18/panel/panel.py sheets [<rule> ...]          redraw sheets from saved numbers and tiles
    python out/r18/panel/panel.py user <newcomer or ->         sheet-for-user.png
    python out/r18/panel/panel.py run <rule> rabbit dendrite   only the named sets
    python out/r18/panel/panel.py close <rule>                 redo close cuts, pictures and the two late measures without a full run

Verdicts are worked out from the saved numbers each time (`verdicts()` in `panel.py`), so a threshold can be moved
without running anything again. `nums.py` prints every raw number on one line per (set, rule); `montage.py` puts one
tile of several rules side by side. `verdict_rows.py` prints one short verdict per (rule, set). `probe.py` (flat-set
thickness per step count, rule speed) and `_readme_results.py` (writes the last section of this file) are build aids.

| file | what |
|---|---|
| `results/<rule>.json` | every number, per set |
| `results/ribs-<rule>.json` | the rib number per set |
| `tiles/<rule>/<set>/*.png` | solid from the front and from above, cuts z = 0 and y = 0 (point by point), cut up through the meeting point (point by point), 12 close-cut tiles (point by point), tree at 6, 8, 10, 12 steps |
| `sheets/<rule>.png` | one row per set, pictures and the six lines |
| `sheet-for-user.png` | one row per set; columns one plane, two planes, along, best newcomer |
| `table.txt` | all lines of all rules |
| `look/` | working pictures used during calibration |

## The panel

| group | set | c | steps | box side |
|---|---|---|---|---|
| A, c on the x-axis | basilica | (-1, 0, 0) | 40 | 3.4 |
| A | sanmarco | (-0.75, 0, 0) | 40 | 3.2 |
| A | airplane | (-1.754878, 0, 0) | 40 | 0.84 round the middle body (whole set drawn once, 4.0) |
| A | cauliflower | (0.25, 0, 0) | 40 | 2.3 |
| B, c in the flat plane | rabbit | (-0.122561, 0.744862, 0) | 40 | 2.8 |
| B | dendrite | (0, 1, 0) | 10 (tree test at 6, 8, 10, 12) | 2.8 |
| B | siegel | (-0.390541, -0.586788, 0) | 40 | 2.9 |
| C, c out of the flat plane | rabbit90 | (-0.122561, 0, 0.744862) | 40 | 2.8 |
| C | rabbit30 | (-0.122561, 0.645069, 0.372431) | 40 | 2.8 |

Solids are sampled at 257 points a side. Escape radius as in the bench (exact for rules that square the length).

## The six tests, what each measures, and its threshold

"Yardstick" = the rule `oneplane` on the same set (every body a ball; clean, but nothing off the flat plane).
"Flat set" = z^2 + c itself on the same box, steps and escape radius. For group C there is no flat set; where a
comparison is needed the flat rabbit (the same c turned back into the flat plane) is used, and that is reasoning by
likeness, not a fact about the set.

| test | measure | passes when | rests on |
|---|---|---|---|
| exact cut | cut at z = 0 on 601 x 601 points against the flat set | at most 0.1 % of the flat set's points differ (and never fewer than 8 allowed). Group C: not applicable | points |
| one piece | share of the solid in its biggest piece, a one-voxel gap allowed, and the same with no gap allowed | gap-allowed share >= 99.97 % AND strict share >= 98.5 %. An empty solid fails here. Airplane: NOT judged (its spine is thinner than a voxel). Dendrite: at 6, 8, 10, 12 steps, each at least what the flat tree gives on the same grid | voxels |
| bodies meet at points | (a) at the meeting point (basilica -0.618; rabbit (-0.276, 0.480), three bodies; San Marco -0.5): the smallest ball whose removal parts the bodies (close-up box 0.9 wide, 201 a side; the bodies are named by points 60 % of the way from the meeting point to 0, c, c^2 + c); how far the solid reaches straight up from the point; how full a ball of radius 0.1 round it is. (b) not a lump, no missing body: thickest place of the solid (largest ball that fits in it) over the thickest place of the flat set; volume over the yardstick's volume. Airplane: how full the cut across a neck is. Dendrite: "a tree stays a tree" (below) | ball <= 0.04 (or one step above the yardstick's; not demanded where the yardstick itself is not parted); reach <= 1.5 x the larger of (flat set's reach in its emptiest direction, yardstick's reach) + 0.004; ball no fuller than the flat disc + 2 points; thickest place between 0.8 and 1.15 of the flat set's; volume <= 2 x the yardstick's; airplane neck <= 1 % full | voxels, except the upward reach and the airplane's neck (points) |
| a tree stays a tree (dendrite, shown on the "bodies" line) | at 6, 8, 10, 12 steps: thickest place of the solid against the flat tree's; at 10 steps the doubling factor: a box twice the size round a point of the solid holds how many times more solid (2 = thread, 4 = sheet, 8 = lump) | thickest place <= 1.5 x the flat tree's + one voxel at every count, thinning at least half as fast as the flat tree, doubling factor <= 3.0 | voxels |
| truly 3D | share of the solid that changes when turned 45 and 22.5 degrees about the x-axis (the smaller); wear the solid down by a fifth of the flat set's thickest place: what comes off, how many pieces run >= 300 degrees round the x-axis (rings), how many stand off the set's plane (centre higher than half the piece's own size), how many of those are round (roundness >= 0.45), volume-weighted roundness of what stands off the plane. The set's plane is the flat plane, or for group C the plane through the x-axis and c | turn >= 0.5 %, no ring, >= 2 round pieces off the plane, their roundness >= 0.45. Airplane: no ring and >= 2 pieces (thin spikes) off the plane. Cauliflower (nothing comes off one body): >= 2 dimples off the flat plane and no groove round the axis, where a dimple is a hollow that a ball of radius 0.12 cannot enter. Dendrite: turn >= 0.5 % and >= 10 % of the tree clear of the flat plane | voxels |
| clean close up | 12 tiles per set, point by point, 80 steps: half-planes through the x-axis at 22.5 and 11.25 degrees from the set's plane, the biggest body met, two skin points on it, three widths (0.2, 0.04, 0.008, scaled to the body). Number per tile = inside pixels that a 3-pixel opening removes (fins, hairs, whiskers, specks under 3 pixels) per pixel of skin line. On the basilica also the bench's rib number (outline of the middle body cut across, 1,440 rays) | worst tile <= 0.3; basilica ribs <= 0.45. Dendrite: not measured (a tree has no skin) | points |
| mirror | share of the solid that changes under z -> -z (groups A and B) and y -> -y (group A) | <= 0.5 %. Group C: nothing to demand; the difference to the flat rabbit's solid turned by the same angle is reported | voxels |

## Calibration (rules whose verdict was known from pictures)

F: = fails; pie = one piece, bod = bodies meet at points (or the tree), d3 = truly 3D, cle = clean close up.

| rule | basilica | sanmarco | airplane | cauliflower | rabbit | dendrite | siegel | rabbit90 | rabbit30 |
|---|---|---|---|---|---|---|---|---|---|
| oneplane | F: d3 | F: d3 | F: d3 | F: d3 | F: d3 | F: d3 | F: d3 | F: pie (empty) | F: pie (empty) |
| twoplane | pass | pass | pass | pass | F: pie, d3, cle | F: pie, bod | F: pie, bod, d3, cle | F: pie, d3, cle | F: pie (empty) |
| lathe | F: d3, cle | F: d3, cle | F: d3, cle | F: d3 | F: bod, d3, cle | F: bod | F: d3, cle | F: bod, d3, cle | F: bod, d3, cle |
| along | F: cle | F: cle | pass | pass | F: bod, d3, cle | F: bod | F: d3, cle | F: bod, d3, cle | F: pie, bod, d3 |
| away | F: cle | F: cle | F: cle | F: cle | F: pie, d3, cle | F: pie, bod | F: pie, bod, d3, cle | F: pie, d3, cle | F: pie (empty) |

What the brief asked the calibration to show, and what came out:

- `oneplane` fails only "truly 3D" on every set of groups A and B: yes (7 of 7). On group C its solid is empty.
- `twoplane` passes group A and fails groups B and C: yes. It fails there by falling apart (rabbit: biggest piece
  97.5 %, 1,537 pieces; Siegel 98.6 %; dendrite 92 to 95 %), not by a tear test: the panel has no tear test, the
  bench's J6 is that.
- `lathe` fails "truly 3D" everywhere but the dendrite: by rings on group A (15, 11, 1, 4 rings; a turn changes
  0.0 %), on groups B and C because nothing round stands off the plane (2 rings, 0 round pieces). On the dendrite its
  sheets fail the tree test (doubling factor 4.4 = a sheet) while "truly 3D" passes: the tree's 3D test cannot tell
  a branch from a sheet.
- `along` passes the basilica on every coarse test and fails only the close cut (worst 1.51: combs of fins, droplets);
  fails groups B and C: rabbit and rabbit90 as a lump (no ball up to 0.32 parts the bodies, the ball at the meeting
  point is 75 % full against the flat disc's 71 %, volume 3.65 x the yardstick's), the dendrite as a lump
  (doubling 4.6), the Siegel disc on ridges (roundness of what stands off the plane 0.38) and hair (2.4), rabbit30 as
  wisps (thickest place 0.015 against 0.348).
- `away` fails the close cut on all of group A (basilica 4.9 and ribs 0.69; San Marco 10.9; airplane 0.64;
  cauliflower 0.42) and falls into plates and shards on groups B and C (rabbit: strict share 68 %, 3,067 pieces).

Where each threshold sits against the numbers seen (the reviewer should read this):

| threshold | passes seen | fails seen | comment |
|---|---|---|---|
| one piece, gap allowed 99.97 | 100.000 | 99.930 (away rabbit), 99.80, 99.67, 98.6, 97.5 | 99.930 is close; the strict share (68 %) decides it safely |
| one piece, strict 98.5 | 99.46 to 100 | 96.45 and below | new in this panel |
| ball that parts 0.04 | 0.02, 0.03 | none up to 0.32 | wide |
| ball fuller than flat disc + 2 | 42 to 50 against 63 to 71 | 75 against 71 (along rabbit) | thin on its own; the ball and the volume fail there too |
| volume <= 2 x yardstick | 0.87 to 1.41 | 3.33 (lathe rabbit), 3.65 (along rabbit) | wide |
| thickest place >= 0.8 x flat | 0.89 (away rabbit), 1.00 to 1.10 | 0.69, 0.21, 0.04 | 0.89 and 0.69 are both shard solids: this line is not sharp |
| thickest place <= 1.15 x flat | up to 1.10 | none | never exercised by a failing rule |
| tree doubling <= 3.0 | 2.19 (one plane) | 3.59 to 4.56 | fine |
| round pieces off the plane >= 2 | 10 to 46 | 0 | wide on basilica and San Marco |
| roundness off the plane >= 0.45 | 0.59 to 0.76; away 0.48 and 0.54 | 0.44, 0.43 (shard solids on the Siegel disc), 0.40 and below | close on both sides: away just passes, the shard solids just fail (both fail other tests too) |
| airplane: >= 2 spikes off the plane | 2 (twoplane, away), 6 | 0 (one plane) | AT the line for twoplane; weak |
| cauliflower: >= 2 dimples off the plane | 2 (twoplane, along, the newcomers), 6 | 0 (one plane) | AT the line: the two are the pair at the poles; weak |
| close cut, worst tile 0.3 | 0.00 (one plane), 0.15, 0.25 (twoplane), 0.26 (p_tt1024 basilica) | 0.42 (away cauliflower), 0.54, 0.64, 0.71 and up | the gap 0.26 to 0.42 is narrow |
| basilica ribs 0.45 | 0.00, 0.05, 0.25 | 0.69 (away) | as in the bench |

## Where a measure disagreed with a picture and was changed

1. Close cut, the skin point. First version: the point straight above the deepest point of the body. On every
   rule a bud sits exactly there, so `twoplane` (clean by eye) scored 11.6. Now two skin points to the side.
2. Close cut, the number. `out/me/r16/closecut.py` counts every loose pixel, so a round bud cut off its stalk
   counts as hair. Now only what a 3-pixel opening removes counts (thin things); the old number is stored as `old`.
3. Close cut, which tile decides. "Third worst of 12" was tried so that one tile on a row of small buds could not
   fail a clean rule. It let `p_tt1024` pass the cauliflower with long needles in two tiles (0.93, 0.61, then 0.15;
   seen in `sheets/p_tt1024.png`) and `away` pass it with a serrated skin (0.42, 0.30, 0.26). Now the worst tile
   decides, as in round 17.
4. Ribs. The bench's rib number was carried to every set and gave `twoplane` on San Marco 1.00 ("ribbed") where the
   cut across is a smooth disc with buds (`look/across.png`): at 40 steps San Marco's buds sit on fat necks and the
   measure reads them as grooves. It is judged on the basilica only; elsewhere it is printed and not used.
5. Lump. "Thickest place against the flat set's" alone gave `along` on the rabbit 1.00 (no lump) where the picture
   is a lump: the lump is layered, no bigger ball fits in it. Volume against the yardstick was added (3.65 x).
6. Truly 3D by the turn test alone: the lathe's solid is spun about the x-axis only when c is on the x-axis; on
   the rabbit a turn changes 56 % of it. Off the axis the lathe fails by "nothing round stands off the plane".
7. Airplane: the turn test cannot be used (the middle body is a near ball: a turn changes 0.0 % of `along`) and no
   round bud comes off any rule; the test counts thin spikes off the flat plane instead.
8. Cauliflower: nothing comes off a body that has only cusps, on any rule; dimples are counted instead.
9. San Marco: at 40 steps the flat set itself is joined across a neck (it reaches 0.12 from the point in its
   emptiest direction; the yardstick 0.47 straight up) and no ball up to 0.32 parts the yardstick. "Meeting at a
   point" cannot be seen there at any step count within reach; the ball is not demanded, only "no fatter than the
   yardstick" and "not a lump". That is a weak test and every rule passes it.

## Rules that passed the bench's stage 1

See `table.txt` for all lines. `p_tt1024` and `p_tt256` (round 17, "nearest plane, crossing smoothed"; the two that
also passed round 17's close cut) behave like `twoplane` with needles: `p_tt1024` passes basilica and airplane, fails
San Marco and the cauliflower on the close cut (3.38 and 0.93: long straight needles), falls apart on rabbit, dendrite,
Siegel and rabbit90 (rabbit: 97.3 %, 2,149 pieces) and is empty on rabbit30. `p_tt256` the same and fails the basilica
close cut too (0.54). `p_ss`, `p_cot`, `p_h4`, `p_tt16` (they pass the bench's eight tests but failed round 17's close cut): see the grid at the end of this file.

No rule passes the panel, and no rule passes a single set of group B or C (the yardstick fails only "truly 3D" on group B).

## Limits (read before trusting a line)

- Everything but the cuts is voxels at 257 a side (0.011 to 0.013 a voxel; airplane close-up 0.0033). Hair, fins and
  necks thinner than that are invisible to "one piece", "bodies" and "truly 3D"; only the close cut sees them, and
  it looks at two skin points in two half-planes per set, not at the whole skin.
- One step count per set (40; dendrite 6 to 12). San Marco and the cauliflower change slowly with the count.
- rabbit30: for every rule run here but the lathe and `p_cot` the solid at 40 steps is empty, crumbs or wisps. The lab's pictures of group C
  (`out/me/panel/panel-off.png`) show a lump for `along` and a bowl for `oneplane` there; point by point, 2 % of the
  cut z = 0 is inside for `along` at 40 steps (8 % at 20) and nothing for the others. The lab draws a surface where
  the bench finds no inside. The panel judges what the iteration says.
- rabbit90 adds nothing for rules that treat the planes y = 0 and z = 0 alike: their solid is the rabbit's, turned
  (difference 0.0 %; `twoplane` 1.6 %). rabbit30 is the real out-of-plane test.
- Group C's "bodies" line compares with the flat rabbit: reasoned, there is no flat set for such a c.
- The airplane and cauliflower "truly 3D" lines pass at exactly the threshold for `twoplane`; a rule could pass or
  fail them by luck. On the Siegel disc there is no meeting point and one fat body, so "bodies" cannot fail a
  layered lump there (`along` passes it at 1.37 x the yardstick's volume and fails on ridges and hair instead).
- The tree's "truly 3D" line cannot tell branches from sheets (the doubling factor on the "bodies" line can).
- No tear test and no test of the rule's smoothness: the bench's J6 stays the test for that.
- Thresholds were set on five known rules and then frozen; nothing was tuned on the round-17 rules, but the switch
  from "third worst" to "worst tile" was made after seeing `p_tt1024`'s needles (a picture, not a number).

## Results of this round (2026-11-18)

The grid of every rule that has been run (F: = the tests it fails there; `-` = that set was not finished when the
build stopped). All lines with their numbers: `table.txt`.

```
rule       basilica    sanmarco    airplane    cauliflower rabbit      dendrite    siegel      rabbit90    rabbit30   
twoplane   pass        pass        pass        pass        F:pie,d3,cl F:pie,bod   F:pie,bod,d F:pie,d3,cl F:pie      
oneplane   F:d3        F:d3        F:d3        F:d3        F:d3        F:d3        F:d3        F:pie       F:pie      
lathe      F:d3,cle    F:d3,cle    F:d3,cle    F:d3        F:bod,d3,cl F:bod       F:d3,cle    F:bod,d3,cl F:bod,d3,cl
away       F:cle       F:cle       F:cle       F:cle       F:pie,d3,cl F:pie,bod   F:pie,bod,d F:pie,d3,cl F:pie      
along      F:cle       F:cle       pass        pass        F:bod,d3,cl F:bod       F:d3,cle    F:bod,d3,cl F:pie,bod,d
p_ss       F:cle       F:cle       F:cle       pass        F:bod,d3,cl F:pie,bod   F:d3,cle    F:bod,d3,cl F:bod,d3   
p_cot      F:cle       F:cle       F:cle       pass        F:bod,d3,cl F:bod       F:d3,cle    F:bod,d3,cl F:bod,d3,cl
p_h4       F:cle       F:cle       pass        F:cle       F:pie,bod,d F:pie,bod   F:pie,d3,cl F:pie,bod,d F:pie,bod,d
p_tt16     F:cle       F:cle       pass        F:cle       F:pie,d3,cl F:pie,bod   F:pie,bod,d F:pie,d3,cl F:pie      
p_tt256    F:cle       F:cle       pass        F:cle       F:pie,d3,cl F:pie,bod   F:pie,bod,d F:pie,d3,cl F:pie      
p_tt1024   pass        F:cle       pass        F:cle       F:pie,d3,cl F:pie,bod   F:pie,bod,d F:pie,d3,cl F:pie      
```

**No rule passes the panel, and no rule passes a single set off the x-axis** (measured). `twoplane` passes the four
sets of group A and fails all five of groups B and C. `along` passes airplane and cauliflower, fails basilica and San
Marco on the close cut only, fails all of B and C. `p_tt1024` passes basilica and airplane. `p_ss` and `p_cot` look and
score like `along` (one pass each, the cauliflower); `p_h4` and `p_tt16` pass only the airplane.

**rabbit30** (c in no special plane) at 40 steps: EMPTY for `oneplane`, `twoplane`, `away`, `p_tt1024`, `p_tt256`
(none of 17 million sample points stays in); `along` is wisps (thickest place 0.015 against the flat rabbit's 0.348,
9,631 pieces, 2 % of the cut z = 0 inside, 8 % at 20 steps); `p_ss` is a cloud of crumbs, `p_h4` 18 loose crumbs;
`p_cot` alone keeps a ragged lump with fins (thickest place 0.51 of the flat rabbit's; it fails bodies, truly 3D and the
close cut); the lathe has its rabbit, turned (measured; seen in `look/front-extras.png`).

What the pictures show (seen in `sheet-for-user.png`, `sheets/*.png`, `look/front-all.png`, `look/worst-all.png`,
`look/meetcut-all.png`):

- basilica: `oneplane` smooth balls in a row, buds only round the waist; `twoplane` buds in four directions; `along`
  buds in eight directions, more and smaller; `away` the same with a rough skin; lathe discs and rings. Cut up
  through the meeting point: an X for every rule (two bodies, one point).
- San Marco: `oneplane` one smooth body with a waist; `twoplane` and `along` three balls with buds all over and deep
  grooves between; `away` ribbed like a melon. Cut up through the meeting point: an hourglass with a thick neck for
  the two-plane rules, completely full for `oneplane`.
- airplane: one small ball and a few specks on every rule; the cuts show the cross of spines.
- cauliflower: `oneplane` smooth with a seam of dimples round the waist; `twoplane` a potato with shallow dimples;
  `along` a barrel with a dozen eye-like dimples; `away` deep star-shaped creases; lathe grooves round it.
- rabbit: `oneplane` clean balls meeting at points, all in the flat plane; `twoplane` and both newcomers the balls
  recognisable but broken, in a cloud of loose pieces; `along` one ragged layered lump; `away` loose plates; lathe
  wrapped shells.
- dendrite (10 steps): `oneplane` a thin flat tree; `twoplane` a bush of thin bits in loose pieces; `along` a lump;
  `away` sparse fragments; lathe shells.
- Siegel disc: `oneplane` a smooth lens with buds on its rim; `twoplane` crumbs; `along` a lump with terraces; `away`
  thin crossed plates with shreds; lathe shells.
- rabbit90: `oneplane` nothing; the two-plane rules exactly their rabbit, turned. rabbit30: nothing but the lathe.
- close cuts, worst tile: `oneplane` a clean line everywhere; `twoplane` a clean line with a few buds cut through on
  group A, torn flaps on the rabbit; `along` a comb of parallel fins on the basilica, a ragged coast on rabbit and
  Siegel, a nearly clean line on airplane and cauliflower; `away` dense whiskers (basilica), curtains of streaks
  (San Marco), a saw edge (airplane, cauliflower); `p_tt1024` and `p_tt256` long straight needles on San Marco and
  the cauliflower, small fins on the basilica.

Numbers behind the main verdicts (measured):

| | one plane | two planes | along | away | lathe |
|---|---|---|---|---|---|
| basilica: round pieces off the flat plane | 0 | 10 | 46 | 10 | 0 (15 rings) |
| basilica: close cut, worst tile | 0.00 | 0.15 | 1.51 | 4.91 | (flat outline) |
| San Marco: close cut, worst tile | 0.00 | 0.25 | 0.71 | 10.85 | (flat outline) |
| cauliflower: dimples off the flat plane | 0 | 2 | 2 | 6 | 4, and 3 grooves round the axis |
| rabbit: biggest piece, gap allowed / strict | 100 / 99.96 | 97.5 / 95.5 | 100 / 99.99 | 99.93 / 68.4 | 100 / 99.99 |
| rabbit: ball that parts the three bodies | 0.03 | 0.02 | none up to 0.32 | 0.02 | none up to 0.32 |
| rabbit: volume | 0.444 | 0.570 | 1.621 | 0.465 | 1.479 |
| dendrite: doubling factor (2 thread, 4 sheet, 8 lump) | 2.2 | 3.6 | 4.6 | 3.6 | 4.4 |
| dendrite: biggest piece at 12 steps | 100 | 91.9 | 100 | 94.1 | 100 |
| Siegel: thickest place over the flat set's | 1.07 | 0.69 | 1.00 | 0.21 | 1.00 |
| rabbit30: volume | 0 | 0 | 0.179 (wisps) | 0 | 1.480 |

Newcomers (measured): `p_tt1024` close cut, worst tile: basilica 0.26, San Marco 3.38, airplane 0.06, cauliflower
0.93, rabbit 2.46, Siegel 6.07; rabbit biggest piece 97.3 % (2,149 pieces); dendrite 90.9 % at 12 steps, doubling
3.7; rabbit30 empty. `p_tt256`: basilica 0.54, San Marco 2.54, cauliflower 0.81; otherwise the same.

What the reviewer should attack first: (1) the close-cut line 0.3 sits between 0.26 (pass) and 0.42 (fail), and
round 17's own close cut, at another skin point, gave `p_tt256` 0.21 on the basilica where the panel gives 0.54;
(2) the airplane and cauliflower "truly 3D" lines pass at exactly the threshold for `twoplane`, and `along` passes
both sets outright although the rough pictures (a ball with specks, a barrel with dimples) do not show that it
should; (3) San Marco's "bodies" line passes everything; (4) the Siegel disc's "bodies" line cannot fail a layered
lump; (5) the thickness line 1.15 was never crossed; (6) group C leans on the flat rabbit (reasoned).
