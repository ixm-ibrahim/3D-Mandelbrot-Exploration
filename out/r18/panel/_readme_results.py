"""Appends the 'Results of this round' section to README.md (run once at the end of the build)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import panel as P

p = os.path.join(HERE, 'README.md')
s = open(p, encoding='utf-8').read()
cut = s.find('## Results of this round')
if cut >= 0:
    s = s[:cut]
s = s.replace("`p_ss`, `p_cot`, `p_h4`, `p_tt16`: see the end of `report.md` for how far their runs got.",
              "`p_ss`, `p_cot`, `p_h4`, `p_tt16` (they pass the bench's eight tests but failed round 17's close cut): see the grid at the end of this file.")
grid = P.table().split('\n\n')[0]
extra = '''## Results of this round (2026-11-18)

The grid of every rule that has been run (F: = the tests it fails there; `-` = that set was not finished when the
build stopped). All lines with their numbers: `table.txt`.

```
%s
```

**No rule passes the panel, and no rule passes a single set off the x-axis** (measured). `twoplane` passes the four
sets of group A and fails all five of groups B and C. `along` passes airplane and cauliflower, fails basilica and San
Marco on the close cut only, fails all of B and C. `p_tt1024` passes basilica and airplane. `p_ss` and `p_cot` look and
score like `along` (one pass each, the cauliflower); `p_h4` and `p_tt16` pass only the airplane.

**rabbit30** (c in no special plane) at 40 steps: EMPTY for `oneplane`, `twoplane`, `away`, `p_tt1024`, `p_tt256`
(none of 17 million sample points stays in); `along` is wisps (thickest place 0.015 against the flat rabbit's 0.348,
9,631 pieces, 2 %% of the cut z = 0 inside, 8 %% at 20 steps); `p_ss` is a cloud of crumbs, `p_h4` 18 loose crumbs;
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
0.93, rabbit 2.46, Siegel 6.07; rabbit biggest piece 97.3 %% (2,149 pieces); dendrite 90.9 %% at 12 steps, doubling
3.7; rabbit30 empty. `p_tt256`: basilica 0.54, San Marco 2.54, cauliflower 0.81; otherwise the same.

What the reviewer should attack first: (1) the close-cut line 0.3 sits between 0.26 (pass) and 0.42 (fail), and
round 17's own close cut, at another skin point, gave `p_tt256` 0.21 on the basilica where the panel gives 0.54;
(2) the airplane and cauliflower "truly 3D" lines pass at exactly the threshold for `twoplane`, and `along` passes
both sets outright although the rough pictures (a ball with specks, a barrel with dimples) do not show that it
should; (3) San Marco's "bodies" line passes everything; (4) the Siegel disc's "bodies" line cannot fail a layered
lump; (5) the thickness line 1.15 was never crossed; (6) group C leans on the flat rabbit (reasoned).
''' % grid
open(p, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n\n' + extra)
print('README results section written')
