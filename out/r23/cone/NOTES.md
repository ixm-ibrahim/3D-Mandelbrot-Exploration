# Round 23, section "cone": the hinge-free door, done properly

Every statement is marked (measured) = a number computed here, (seen) = in a picture I opened, (reasoned).

## Verdict in plain words

**No. This door does not give the user's picture.** The rule can be built exactly as asked (exact and shape-keeping
on the flat plane, both 60-degree cones laid onto it once round with stretch exactly 2, no fold, no tear, the count
coming from the power), and for c = -1 and c = -0.75 it does grow extra round bodies off the flat plane that touch
the main body at single points. But three things spoil it:

1. **The skin is crusted.** Cuts along the planes I first chose looked clean; the rough solids do not. Every body is
   covered with scales and loose flakes, for all four shapes (seen, `sheet.png`, `sheet-top.png`). One plane's
   bodies are smooth; these are not.
2. **The pattern is threefold and the flat picture is twofold, and no turn of the pattern is both tidy and
   symmetric.** With the mirror-symmetric turns the basilica is a string of beads on arcs or one spiky lump; it is
   tidy only when the pattern is turned a quarter, and then the extra bodies all lean to one side (+y) of a shape
   whose flat picture is mirror-symmetric (seen, `cuts-weld-c-1.png`).
3. **Off the x-axis it gets worse, not better.** Rabbit: its bodies stay separate and fat, but the extra bodies come
   with loose bits. Siegel disc: a ragged body that keeps losing points (share of a test box inside: 0.040 after 30
   steps, 0.033 after 80, 0.031 after 200; one plane 0.044 / 0.043 / 0.043) and is thin (median height above the
   flat picture 0.040; one plane 0.329) (measured).

Also, even where it works it is not "bulbs everywhere in the flat picture's pattern": the main body gets two more
arms and two more buds (four directions sent to each flat direction instead of two), all of them on the two cones;
between the flat plane and the cones the rule squeezes (22 % of all directions squeezed more than 2 to 1, 13.5 % more
than 4 to 1) (measured).

## Files

- `conelib.py` direction maps and tools (numbers, lift test, cuts). `variants.py` every variant tested, thickness
  measure, extra cuts. `step1.py`, `scan.py`, `tune.py`, `power3.py`, `solids.py`, `final.py` the runs below.
- `best.py` the best rule. Load: `import sys; sys.path.insert(0, 'out/r23/cone'); import best; r = best.rule()`
  (`best.rule('c')` = cones turned to follow c; `best.rule(theta=0.0)` any other turn). Formula in its docstring.
- Pictures: `sheet.png` (the deliverable: c = -1, c = -0.75, rabbit, Siegel disc; rows one plane, along, best, best
  turned with c; rough solids, 30 steps, eye (0.45, 0.5, 1)), `sheet-top.png` (second eye (0.2, 1, 0.35), best rule
  only, if present), `step1-shells.png`, `cuts-weld-<set>.png` (six variants, five cuts), `cuts2-band-<set>.png`
  (one plane, five welded variants, scout-; six cuts, 60 steps), `solids-w90-a.png` (first solid of the un-banded
  weld), `power3-ci.png`, `power3-c2.png`.

## Step 1. Where the scout's shells come from (answered)

- R_t has three critical directions in each hemisphere (where it stops stretching), at latitude 32.9, longitudes 0,
  120, 240 for t > 0; they are sent to latitude 15.83, longitudes 0, -120, 120 (measured on a grid and by hand from
  t u^2 - (2 - 4 t^2) u + t = 0, u = w^3).
- Along the meridian through a critical direction the image never rises above 15.8 degrees: the whole fan of
  directions between the flat plane and the cone is folded into the thin wedge within 15.8 degrees of +x (reasoned,
  then measured:) of the 59,324 shell points of the upright cut of c = -1 (radius > 0.95, x > 0.2), whose own
  latitudes span 78 degrees (5th..95th percentile 3..68), the squares have latitude 1.7..19.1 (5th..95th), all at
  longitude 0; 67 % lie within 6 degrees of the critical value. After 10 steps their median height is 0 to four
  digits: they end on the flat cycle 0 <-> -1.
- So the shells are the arm of the flat picture along +x (inside up to x = 1.618), fanned out over 60 degrees of
  latitude: each shell is one crossing of the skin by the line from c at 15.8 degrees above +x
  (seen, `step1-shells.png`: the orange shell points land between the two red lines).
- General rule this gives (reasoned): a critical direction d sent to e turns every crossing of the skin by the line
  c + s e (s > 0) into a saddle-shaped shell at radius sqrt(s) around d. Clean bodies need those three lines to
  leave the set at once and never come back.

## Step 2. Moving the critical directions inside the R_t family (nothing clean)

- Other t (by hand): t = 0.05 / 0.10 / 0.15 / 0.20 / 0.268 / 0.35 / 0.45 puts the cone at latitude 84.3 / 78.6 /
  72.9 / 67.4 / 60.0 / 51.4 / 41.5 with stretch 10.0 / 5.05 / 3.41 / 2.60 / 2.00 / 1.60 / 1.34 and sends the critical
  directions to latitude 61.3 / 45.9 / 34.4 / 25.3 / 15.8 / 7.6 / 1.4. The critical values rise only when the cone
  leaves 60 degrees and its stretch leaves 2. In this family the two wishes pull against each other (measured).
- A blend without the fold: not found. The scout's blend with width 0.2 / 0.3 / 0.4 folds 0.57 / 1.11 / 1.85 % of
  directions; letting t grow from 0 at the equator instead folds 0.95 % to 3.3 % (widths 0.3 to 1.3) (measured).
  Reason (reasoned): on the meridian through a critical direction R_t lifts the image only to 15.8 degrees while w^2
  has already lifted it higher at a third of that latitude, so a blend must come back down.
- Turned 30 degrees: registered (`rt30`, `rt-30`), numbers identical to the scout's with the critical values at
  longitudes 60, 180, 300; no pictures made, because the welded map of step 3 does the same job with no fold.
- All three onto a pole: impossible (reasoned, a count). Between the flat plane and the cone the map covers the
  upper half of the sphere three times (twice from the plane's side, once from the cone's), so the pole has three
  preimages there; a critical direction uses up two. One triple point on the pole plus one loose critical direction
  is possible in principle; not built (see "Not done").
- Also (reasoned): any map that is angle-true beside the flat plane and exact on it IS w^2 there, so every such rule
  is the one-plane rule in a belt and something else above it; the join can never be angle-true.

## Step 3. A map built from the conditions: the "welded cones" (the best rule)

Construction. E = the one-plane direction (w^2). C = the turn-over rho e^(i theta) / w with rho = tan 75: it lays the
60-degree cone onto the flat plane once round, angle-true, with stretch exactly (rho + 1/rho)/2 = 2, and sends
everything above the cone to the lower half. Between plane and cone both E and C point into the upper half, so the
straight mix G = normalise((1 - chi) E + chi C) never crosses the flat plane: nothing but the plane and the two cones
is sent into the flat plane (reasoned; measured: covers 4.0000).

- **No-fold condition (new, exact):** the mix must be chi = 2/3 at Mercator latitude MU60/3 (latitude 24.4), where E
  and C send a direction to the same latitude. Found by root-finding in `tune.py` (7 parameter sets, folded share
  0.000000 each), then understood: there E climbs at rate 2 and C falls at rate 1, and at the three longitudes where
  they agree the image must turn round in latitude and in longitude at the same point (reasoned). Any chi through
  that point works; `variants.band()` uses it (measured: folded 0.000000 for exact belts up to mu = 0, 0.2, 0.3).
- Numbers of the best rule (`best.py`, belt exact up to mu = 0.2 = latitude 11.4, mix ends at mu = 0.604) (measured):
  flat check 0 of 20,000 differ on all four tests, a flat point is thrown 0.0 off the plane; length squared to 7e-15;
  finite on a batch that includes flat points and points on the upright axis; covers 4.000004; folded share 0.0;
  stretch on the flat plane 2.00000 both ways; the 60-degree circle is sent to the flat plane (to 0.15 degrees at
  the grid row 60.075) with stretch 2.0045 both ways there (2 at 60); critical directions at latitude 24.4,
  longitudes 30, 150, 270, sent to latitude 44.9, longitudes 60, -60, 180; 21.8 % of directions squeezed more than
  2 to 1 and 13.5 % more than 4 to 1.
- Lift test (150 steps; lost of flat-inside points lifted by 1e-6 / 1e-3 / 1e-2): c = -1: 0 / 4 / 26 of 938;
  c = -0.75: 0 / 0 / 35 of 1385; rabbit 1 / 15 / 43 of 801; Siegel 1 / 44 / 142 of 1119 (measured).
- 30 against 80 against 200 steps (share of the box +-1.8, +-1.4, +-1.4 inside): c = -1: 0.0383 / 0.0382 / 0.0382
  (one plane 0.0256); c = -0.75: 0.0806 / 0.0804 / 0.0804 (0.0552); rabbit 0.0352 / 0.0330 / 0.0330 (0.0168);
  Siegel 0.0404 / 0.0329 / 0.0310 (0.0443 / 0.0431 / 0.0431) (measured). So c = -1 and -0.75 are stable solids about
  half as big again as one plane's; the rabbit settles after a loss; the Siegel disc leaks.
- Median height of the solid above flat-inside points (150 steps; c = -1 / -0.75 / rabbit / Siegel): one plane
  0.180 / 0.329 / 0.134 / 0.329; along 0.180 / 0.243 / 0.329 / 0.329; best 0.180 / 0.243 / 0.134 / 0.040; the
  un-belted weld (`weld90`) 0.099 / 0.054 / 0.040 / 0.000 (its Siegel disc is a film: 100 % of points lost below
  height 0.01); scout- 0.329 / 0.599 / 0.073 / 0.073 (measured).
  Why the belt matters (reasoned): the mix pushes every direction away from the flat plane faster than the angle-true
  rate, at all longitudes at once; R_t pushes up at some longitudes and down at others and so keeps the Siegel body.
- The turn theta (seen, `cuts-weld-c-1.png`, `cuts-weld-c-075.png`, 50 steps):
  theta = 0 (cones open along +x, mirror-symmetric): upright cut through x is a main body with strings of beads on
  arcs from the plane to the cone, for c = -1 and c = -0.75: the shells of the scout, broken up.
  theta = 180 (open along -x, mirror-symmetric): one lump with spikes.
  theta = 90 (turned a quarter, no y-mirror): c = -1 and c = -0.75 are a clean row of bodies in the upright cut
  through x, and in the upright cut through y the main body carries two round bodies on its +y side, one on each
  cone, joined to it at single points, and small buds on the -y side.
  Reason (reasoned from step 1): the three critical values sit at longitudes 2 theta / 3 + 0, 120, 240. For theta = 0
  or 180 one of them points along +x, from c = -1 straight through the bodies; for theta = 90 they point along -x and
  +-60 degrees, away from the set.
- Rabbit (seen, `cuts2-band-rabbit.png`, 60 steps): the three big bodies are there and fat in the cut through 0 and c;
  the cone copies appear as extra bodies above and below with dusty fringes; a wider exact belt (mu 0.3) gives more
  dust, not less. Siegel disc (seen, `cuts2-band-Siegeldisc.png`): film without the belt, a feathered body with loose
  bits with it.
- Cones turned to follow c (`best.rule('c')`, theta = 1.5 arg c, so that one critical value always points from c
  straight away from 0): the rabbit's cuts are cleaner (three clean bodies in a row in the cut through 0 and c,
  separate round bodies in the tilted cut) but the solid is as crusted as the fixed rule's (seen, `sheet.png`). It
  looks at c, it has a seam (theta jumps by 180 degrees where arg c wraps round: the two sides are mirror images),
  and it is undefined for c off the flat plane. I do not put it forward.
- **The solids (seen, `sheet.png`, 340 x 255 x 210 blocks, 30 steps):** best rule, c = -1: main body, two side
  bodies, extra bodies above; all of them covered with scales and small loose pieces. c = -0.75: one lumpy mass with
  ridges, bodies hard to tell apart. Rabbit: a crusted mass in the rabbit's outline. Siegel disc: the same. One
  plane beside it is smooth in all four; along is clean for c = -1 and -0.75 and a lump for the other two. The cuts
  I trusted first were along planes that hide this: it is the trap named in the house rules.
- **Second eye (seen, `sheet-top.png`, from above, best rule only):** c = -1 is a main body with bodies beside and
  above it, all furrowed by long thin grooves and crusted; c = -0.75 is one mass cut by parallel grooves; rabbit and
  Siegel disc are crusted lumps. The grooves are thin slots cut into the bodies, so the shells of step 1 are thinner
  here, not gone.

## Step 4. Power 3 (the count does follow the power)

Built the same way (`power3.py`): w^3 beside the flat plane; kappa1 / w^2 beside the cone cos L = 2/3 (latitude
48.19, twice round, turned over); w / kappa2 beside the cone cos L = 1/3 (latitude 70.53, once round). No-fold
conditions by the same argument: first mix 3/5 at mu = 0.4 MU1, second mix 2/3 a third of the way from MU1 to MU2.
Measured: covers 9.0001 (= 3 squared; power 2: 4.0000 = 2 squared), folded share 0.000000, flat plane equals z^3 to
1e-14, the circle at 48.1 goes round -2.00 times with stretch 2.995 both ways, the circle at 70.5 goes round 1.00
times with stretch 2.996; five critical directions between plane and first cone (latitude 21.5 -> 55.0), three
between the cones (57.3 -> -29.2); along a meridian the image crosses the flat plane at latitudes 0, +-48.2, +-70.5
and nowhere else. So each flat direction has 3 + 2 + 2 + 1 + 1 = 9 directions sent to it (power 2: 2 + 1 + 1 = 4):
the number of extra arms and buds is set by the power, with no dial. Seen (`power3-ci.png`, c = i, where 0 -> i -> 0):
with both pairs of cones opening along +x the upright cut 36 degrees from x shows the main body with five separate
round bodies round it and the cut through y three bodies joined at points, against one side body for the one-plane
rule; with the first pair turned a quarter the cut through y is one spiky lump. No solids were made for power 3, so
whether its skin is crusted too is not known.

## Things worth knowing for the next section

- The door is a map of directions that covers the sphere n squared times (4 for the square). Mayer's power map (the
  pillow) does that too: this is the pillow's cousin with the flat plane kept as a circle that is turned by 2a.
- (reasoned) "Once round on the cone" cannot share the flat picture's half-turn symmetry: on the plane G(-d) = G(d),
  on the cone G(d turned 180 degrees) is the opposite direction. So the solid of a real c never has both mirror
  symmetries of its flat cut. This holds for any rule that passes this door, not just mine.
- (reasoned) Three critical directions per hemisphere is forced (the belt between plane and cone is a ring laid
  three times over a disc: 0 = 3 - b gives b = 3). Their images cannot all be the pole. In the welded map they are
  always at latitude 44.9; in R_t at 15.8.

## Not done

- No look at the Mandelbrot solid. No solids for power 3. No second eye position for one plane and along (the
  round-22 sheets have them); `sheet-top.png` covers the best rule only, if the run finished.
- The cause of the crust was not traced orbit by orbit. Likely (reasoned, not measured): the mix zone squeezes more
  than 4 to 1 on 13.5 % of directions, and every body is a pulled-back copy of that zone.
- The one-triple-point layout (one critical direction sent to the pole with three sheets, one left over) was not
  built; it would keep the y-mirror and leave a single critical line to place.
- No search over the shape of chi beyond the no-fold condition and four belt widths.
