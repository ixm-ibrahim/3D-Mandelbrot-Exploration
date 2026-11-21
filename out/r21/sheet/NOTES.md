# Round 21, agent "sheet": ONE carried sheet through the x-axis

Every statement below is marked **measured** (a number I computed), **seen** (in a picture I opened) or **reasoned**.
All pictures are rough blocks made with `out/r21/lib/mem.py`; nothing here is a fine render.

## 0. In short

- 69 update rules for one carried sheet were coded and checked, next to the scout's 7 (which are a corner of this space).
- **Nothing in the family is "the right rule".** No rule gives round buds all over a body. The best the family can do is
  buds in FOUR directions (up, down, front, back: the flat page and the upright sheet), never more without a dial.
- **Why following gives ribs and rings** (measured, section 4.1): a bud's width round the x-axis is the one-plane
  width divided by (1 - share). Share 0: 14 degrees. Share 0.25: 19. Share 0.75: 52. Share 0.9: the full circle, a ring.
- **Why lagging gives blobs** (measured, section 4.2): a bud of the Mandelbrot solid lives only where the squaring sheet
  is within about 1.5 degrees of c's own sheet at every step. A lagging sheet is not there, so only the smooth middle is left.
- **Between the two there is no round ball in the Mandelbrot solid** (measured): thin lens, then arcs that break into
  pieces, then nothing, then a full ring.
- **A trap that the flat check does not see** (measured, section 4.3): many rules with memory are exact ON the flat
  page and yet the flat picture has NO BODY: lift a point of the flat rabbit by a millionth and it is lost.
  This kills every rule that turns the sheet away, overshoots, or moves it after the squaring.
- The closest rule, `evc005e70k16`, meets the letter of section 6 of the briefing on the six test sets (basilica
  with round buds in four directions, a clean rabbit with separate bodies, a Mandelbrot solid that is not spun).
  It is a construction with three dials, it is seamed and pitted for c just off the x-axis, and its Mandelbrot solid is
  "two flat Mandelbrot sets crossed at right angles with a smooth skin between". I do not call it a success.

## 1. Words

- P: the one-plane rule. `P(x,y,z) = f * (x^2 - y^2, 2xy, 2 r z)`, `r = |v|`, `f = r^2 / (r^2 + z^2)`.
- "P about the sheet at turn theta": `Rot_x(theta) P(Rot_x(-theta) v)`. In code `sq_at(x, y, z, th)` of `myrules.py`.
- theta: the turn of the carried sheet from the flat page. It starts at 0. theta and theta + 180 degrees are one sheet.
- phi: the turn of the point's OWN sheet, `phi = atan2(z, y)`. For a point on the x-axis phi is taken as theta.
- d: `phi - theta` brought into -90..90 degrees. How far the point's sheet is from the carried sheet.
- vote of a point: the vector `(y^2 - z^2, 2 y z)`. Its length is the squared distance from the x-axis, its direction
  is the point's own sheet in doubled angle `psi = atan2(2yz, y^2 - z^2)`.
- c is added by the library after every squaring. The Mandelbrot orbit starts at the point c with k = 0.

## 2. Every rule, in full (all are in `out/r21/sheet/myrules.py`, list `RULES`, `get(name)`)

### 2.1 "The sheet turns by h(d), then the point is squared" (`turn(h)`, carried: theta)
`theta <- theta + h(d)`, then the square is P about theta.

| name | h(d) |
|---|---|
| ease | d - sin(2d)/2 |
| over | d + sin(2d)/2 |
| easehalf | d - sin(2d)/4 |
| ease2 | d - sin(2d) |
| mirror | -d |
| away50 | -d/2 |
| twice | 2d |
| over150 | 1.5 d |
| thrice | 3d |
| snap45 | d if abs(d) > 45 degrees, else 0 |
| stick30 | d if abs(d) < 30 degrees, else 0 |

### 2.2 "The sheet moves the share lam toward the point's sheet" (`lam_rule`)
`h(d) = toward(d, lam) = 0.5 * atan2(lam sin 2d, (1 - lam) + lam cos 2d)` (the same blend of doubled-angle vectors as `M.blend`).

| name | share lam |
|---|---|
| lag60, lag67, lag90 | 0.6, 2/3, 0.9 (the scout has 0.25, 0.5, 0.75) |
| farfollow | sin^2 d |
| nearfollow | cos^2 d |
| axfar | (y^2 + z^2) / (x^2 + y^2 + z^2) |
| axnear | x^2 / (x^2 + y^2 + z^2) |
| fade | 0.5^(k+1), k = number of squarings before this one |
| mean | 1 / (k + 2) |
| wake | 1 - 0.5^k |

### 2.3 Votes (`vote(s, gamma, norm, after)`, carried: the vector w, which starts as (s, 0))
Each step `w <- gamma * w + (y^2 - z^2, 2yz)`; the sheet is `theta = 0.5 * atan2(w2, w1)`; square about it.

| name | s | gamma | other |
|---|---|---|---|
| vote1, vote025, vote4 | 1, 0.25, 4 | 1 | |
| voted1, voted4 | 1, 4 | 0.5 | |
| voten1 | 1 | 1 | vote divided by x^2+y^2+z^2 |
| votea1 | 1 | 1 | the point is squared BEFORE its own vote is added |

### 2.4 The sheet moved after the squaring (carried: theta)
- after25, after50, after75: square about theta; then `theta <- theta + toward(d, lam)`, lam = 0.25, 0.5, 0.75.
- image50, image100: square about theta giving (X, Y, Z); then theta moves the share 0.5 or 1 toward the sheet of
  (Y, Z), the image before c is added.
- peek50, peek100: the same trial squaring and move, and then the point is squared again about the moved sheet;
  that second square is the result.

### 2.5 Settling and waking (carried: theta)
- settle1: `h = d` for the first squaring, 0 ever after. settle1h: `h = toward(d, 0.4)` for the first squaring, then 0.
  settle3h: `toward(d, 0.4)` for three squarings, then 0.
- late2: `h = 0` for two squarings, then `h = d`. late3lag: `h = 0` for three squarings, then `toward(d, 0.5)`.

### 2.6 c's own sheet in the mix (carried: theta; phi_c = atan2(cz, cy), taken as theta when c is on the x-axis)
- cpull, cpull25: `theta <- theta + toward(phi_c - theta, 0.5 or 0.25)`; the point is not asked.
- cmix: first `theta <- theta + toward(phi_c - theta, 0.25)`, then `theta <- theta + toward(phi - theta, 0.25)`.
- bisect: carried: the own turn of the point before (0 at the start). Sheet = `prev + toward(phi - prev, 0.5)`;
  then prev becomes phi.

### 2.7 Second wave: "eased" votes (`evote(s, gamma, ease)`, carried: w, starts (s, 0))
One eased vote of a thing with coordinates (y, z) and weight factor k:

    psi_w = atan2(w2, w1);  t = atan2(2yz, y^2 - z^2) - psi_w, brought into -180..180 degrees
    a = psi_w + t - ease * sin(t);   w <- BASE + k * (y^2 + z^2) * (cos a, sin a)

With ease = 0 the vote is for the thing's own sheet. With ease = 1 a thing near the sheet votes for the sheet as it
is, a thing square to the sheet votes for its own sheet, and next to that it overshoots.
BASE is `gamma * w`, or, where gamma is "forget", `s * (cos psi_w, sin psi_w)` (only the old direction is kept).
After the vote the point is squared about `theta = 0.5 * atan2(w2, w1)`.

| name | s | gamma | ease |
|---|---|---|---|
| votefix010, votefix025, votefix1 | 0.10, 0.25, 1 | forget | 0 |
| evote005, evote010, evote025 | 0.05, 0.10, 0.25 | forget | 1 |
| evsum005, evsum010, evsum020, evsum040 | 0.05 .. 0.40 | 1 | 1 |
| evslow010 | 0.10 | 0.9 | 1 |
| evhalf010, evhalf025 | 0.10, 0.25 | 0.5 | 1 |
| evsumh010 | 0.10 | 1 | 0.5 |
| evsum005e70 | 0.05 | 1 | 0.7 |

### 2.8 Second wave: eased votes, and c votes too (`evc(s, ease_c, ease, kc)`, carried: w, starts (s, 0))
Each step: first c casts an eased vote (coordinates (cy, cz), ease `ease_c`, weight factor `kc`, BASE = w), then the
point casts an eased vote (ease `ease`, factor 1, BASE = w), then the point is squared about the sheet along w.
A c on the x-axis has no vote.

| name | s | ease_c | ease | kc |
|---|---|---|---|---|
| evc002, evc005, evc010 | 0.02, 0.05, 0.10 | 1 | 1 | 1 |
| evcp005 | 0.05 | 0 | 1 | 1 |
| evc005e50, evc005e70, evc005e85 | 0.05 | 0.5, 0.7, 0.85 | same | 1 |
| evc005p70 | 0.05 | 1 | 0.7 | 1 |
| evc005e70k4, **evc005e70k16** | 0.05 | 0.7 | 0.7 | 4, 16 |

## 3. Numbers

Files: `checks.txt` (flat check and turned check, 8,000 points each), `vol-a.txt`, `vol-b.txt`, `vol-c.txt` (volumes),
`thick.txt` (body test; some later rows were printed to the console only and are quoted below), `arcs.txt`, `upright.txt`,
`explain-lag.txt`, `explain-turn.txt`, `explain-off.txt`, `explain-stab.txt`.
Scripts: `checks.py`, `measure.py` (vol / thick / arcs), `explain.py`, `stab.py`, `upright.py`, `pics.py`, `sheets.py`, `closeup.py`, `final.py`.

**The upright sheet (measured, 20,000 places, 60 steps, `upright.txt`).** Verdicts in the cut along the upright sheet
that differ from the flat picture, Mandelbrot / basilica: lathe 0 / 0, along 0 / 0, **ease 0 / 0**, lag67 2 / 0,
evc005e70k16 22 / 31, evc005e70 113 / 31, evsum010 331 / 124, over 604 / 0, mirror 1,549 / 0, one-plane 3,274 / 497.

**Flat page (measured).** All rules: 0 verdicts of 8,000 differ, for the Mandelbrot set, basilica, rabbit and Siegel
disc. One exception: `bisect` (12 differ for the Mandelbrot set, 1,125 for the rabbit): it is out.

**Turned check (measured).** Spun (0.00 %): `settle1` and the scout's `own`. `twice` also shows 0.00 % but its solid
is nearly empty (0.46 % inside). Every other rule: 0.05 % to 3.3 % of pairs differ for the Mandelbrot solid.

**Volume of the rabbit in the box, % at 30 / 80 / 200 steps (measured, 120,000 points).** One-plane 1.90 / 1.85 / 1.85.

| what happens | rules (rabbit volume) |
|---|---|
| gone or nearly gone | over, mirror, away50, twice, over150, thrice, ease2, after50, after75, image50, image100, peek50, peek100 (all 0.00); settle1 0.09; settle1h 0.23; after25 0.28; fade 0.43; settle3h 0.60 |
| leaks away as steps grow | ease 2.50 / 0.97 / 0.07; farfollow 2.42 / 0.51 / 0.01; easehalf 5.07 / 2.91 / 0.79; evote005 2.52 / 1.30 / 0.45; evote010 2.46 / 1.52 / 0.80; late3lag 4.20 / 3.17 / 2.38; scout lag50 5.87 / 4.55 / 3.46; scout lag60 2.41 / 0.08 / 0.00 |
| swollen lump (3 to 4 times the one-plane volume) | scout lag25 5.81, lag67 5.42, lag75 5.68, lag90 6.00, first 6.22; wake 6.58; nearfollow 5.50; cmix 8.11; voted1 6.10; voted4 7.08; votefix025 5.91; votefix1 7.82; late2 4.89; evhalf010 4.84 |
| bodies, stable from 80 steps on | cpull 1.85 (it IS the one-plane rule for c in the flat page); vote4 3.02; vote1 3.64; evsum005 1.05; evsum010 1.14; evc005 1.53; evc005e70 2.08; evc005e70k4 2.55; **evc005e70k16 2.11** |

Basilica, San Marco and the airplane are steady for every rule (for example ease 2.65 / 2.65 / 2.65).
The dendrite is empty at 80 steps for every rule, as it should be.

## 4. Why the family behaves as it does

### 4.1 Ribs and rings: the first-step law (measured)

Take the bud on top of the basilica's middle body. Walk round the x-axis on the circle through its middle
(x = 0, radius 0.62) and note where you are inside (2,880 places, 80 steps).

The start point is squared about the sheet the rule gives it. It lands where the flat picture says only if it lies
IN that sheet. After the sheet has turned by h(d) the point is `d - h(d)` off its sheet. So:

- a bud sits where `d - h(d) = 0`: always at the flat page, and at the upright sheet exactly when h(90) = 90 degrees;
- its width round the axis is the one-plane width (14.1 degrees) divided by the size of `1 - h'` there.

For "move the share lam": `1 - h'` is `1 - lam` at the page and `(1 - lam) / (2 lam - 1)` at the upright sheet.

| share | bud at the page: measured, law | bud at the upright sheet: measured, law |
|---|---|---|
| 0 | 14.1, 14.1 | none, none |
| 0.10 | 15.6, 15.7 | none, none |
| 0.25 | 18.9, 18.8 | none, none |
| 0.40 | 23.6, 23.5 | none, none |
| 0.45 | 25.6, 25.7 | none, none |
| 0.55 | 27.4, 31.4 | 2.9, 3.1 |
| 0.60 | 30.9, 35.3 | 6.4, 7.1 |
| 0.67 | 37.4, 42.4 | 12.9, 14.1 |
| 0.75 | 51.9, 56.5 | 27.4, 28.2 |
| 0.90 | ring, ring | ring, ring |

Other rules (same circle): ease and over: four buds of 12.4 degrees (law 14.1). mirror, thrice, ease2: four buds of
6.1 (law 7.1). easehalf: four of 25.4 (law 28.3). twice: two buds only, because h(90) = 0.
For comparison `along`: eight buds of 13 degrees; the lathe: the full circle.

In plain words: the closer the sheet follows, the less the answer depends on which side of the x-axis you start,
so every bud is smeared round the axis. Small buds become ribs, and when the smear closes it is a ring.

### 4.2 Blobs: what a bud of the Mandelbrot solid needs (measured)

Same walk on the circle through the middle of the period-3 bud (x = -0.1226, radius 0.7449).

- One-plane rule: inside on 2.9 degrees only. The bud is a thin lens about the page: 0.04 thick, 0.19 tall.
  So a bud survives only while the squaring sheet is within about 1.5 degrees of c's own sheet.
- Moving the share lam, measured (width of the arc at the page; pieces on the whole circle): 0.10: 17 degrees, 2 pieces.
  0.25: 38 degrees, 6 pieces. 0.40: 62 degrees, 22 pieces. 0.45: 14 degrees, 226 pieces. 0.55 and 0.60: nothing off
  the page. 0.67 and above: the full ring.

So there is no round ball anywhere on the way: thin lens, arcs, dust, nothing, ring (seen in `explain-across.png`, row 2).
A lagging sheet stays near the flat page while c is added off that sheet at every step; the cycle that makes the
bud cannot form; what is left is the middle part, which needs no cycle of its own. That is the blob.

### 4.3 The flat picture can be a film with no body (measured)

Take points well inside the flat picture, lift them 0.000001 off the page, count how many are lost (300 steps).

| rule | Mandelbrot set | rabbit | Siegel disc |
|---|---|---|---|
| one-plane | 0.1 % | 0.1 % | 0.0 % |
| scout lag25 | 10.5 % | 0.1 % | 0.2 % |
| scout lag50 | 7.8 % | 61.7 % | 1.6 % |
| lag60 | 6.4 % | 100 % | 0.8 % |
| scout delay | 37.8 % | 100 % | 100 % |
| ease | 3.1 % | 79.3 % | 6.3 % |
| over | 17.7 % | 100 % | 100 % |
| mirror | 56.8 % | 100 % | 100 % |
| away50, twice, after50, image100, peek100 | 30 to 74 % | 100 % | 100 % |
| vote1, vote025 | 1.7 %, 2.6 % | 0.0 % | 0.0 % |
| evsum010, evc005, evc005e70k16 | 0.2 %, 0.2 %, 0.1 % | 0.1 % | 0.0 % |
| along | 0.2 % | 0.0 % | 0.0 % |

Basilica, San Marco, airplane: 0.0 to 0.4 % for every rule. The trouble is only for c off the x-axis.
`explain-film.png` shows where: for lag25 it is the period-2 disc and the period-3 buds of the flat Mandelbrot set.

Why (reasoned, partly checked). The point's own sheet is not defined on the x-axis and swings wildly next to it.
A rule that turns the carried sheet by the point's own direction is thrown about every time the orbit passes near
the axis, and for c off the axis the orbit does that again and again (the rabbit's cycle goes through 0).
A first-order formula is in `stab.py`: lift eta, tilt a, slope kappa = h'(0), cycle point x + iy of length r:
`a' = (1 - kappa) a + kappa eta / y`, `eta' = 2 r eta - 2 (r - x) y a'`. It flags 92 % (lag 0.25), 85 % (lag 0.5),
61 % (lag 0.67), 100 % (mirror) and 99.8 % (over) of the places measured lost, but it flags too much: where it says
"unstable" the point is often not lost, it only stops following the flat cycle (`explain-stab.png`). So the formula
is a partial explanation, not a law.

Votes weighted by the squared distance from the x-axis do not have this fault (points near the axis have no say),
and that is why they are the only rules whose rabbit keeps its body.

### 4.4 Why a bud at the upright sheet costs a tear (reasoned)

Suppose a rule (a) is the same on both sides of the flat page, (b) leaves the sheet alone for points close to the
x-axis, (c) gives a point in the upright sheet the upright sheet. Walk once round the x-axis. Close to the axis the
sheet does not turn at all. Far out, (a) and (c) force the sheet to make an odd number of half-turns. A number of
turns cannot change smoothly from 0 to 1, so somewhere between there is a surface where the sheet jumps: a tear.
In the vote rules it is where the votes cancel (w = 0). Seen: grooves, brims and fins on the rabbit
(`close-rabbit80b.png`, `close-rabbit80c.png`), streaks in the upright cut of the Mandelbrot solid (`mandel-m2.png`).
A rule that is NOT the same on both sides of the page (a handed rule) escapes this argument. I did not test one.

### 4.5 The question "is there a setting between where a bud off the page is a round ball?"

- Julia sets with c on the x-axis: yes, at exactly one place, the upright sheet. Share 2/3 makes that bud as round
  as the one-plane's own buds (12.9 against 14.1 degrees) but stretches the bud at the page 2.6-fold. No share
  makes both round: that needs `1 - lam` and `(1 - lam)/(2 lam - 1)` both near 1. The rule `ease` makes all four round.
- Mandelbrot solid, plain following: no (4.2).
- Mandelbrot solid, eased votes: buds at the flat page AND at the upright sheet, nowhere else. Width round the axis
  against the flat bud's height 0.19 (measured): evc005 x0.2 (thin lenses), evc005e70k16 x0.6, evc005e70 x1.1 to
  1.2, evc005e50 x2.4 to 2.7 (arcs). So the thickness can be dialled; the place cannot.
- Why only those two sheets (reasoned): the recipe knows only the x-axis and the flat start. The flat page and the
  sheet square to it are the only sheets that this singles out. Any other place needs a dial (as `along` has: its
  sin(4 phi) sets four planes).

## 5. The three best rules

### 1. `evc005e70k16` (eased votes, c votes sixteen-fold)
Carried: w, starts (0.05, 0). Each step: c casts an eased vote with ease 0.7 and weight 16 (cy^2 + cz^2); the point
casts an eased vote with ease 0.7 and weight y^2 + z^2; the point is squared by P about the sheet along w (2.7, 2.8).

- Flat page exact: yes (0 of 8,000 four times; body test 0.1 % lost). measured
- Basilica: buds in four directions, 19 degrees wide at the page and 15 at the upright sheet, not rings. measured;
  rows of buds along two great circles seen in `close-basilica60.png` (that picture shows evc005e70; k does not
  matter when c is on the x-axis).
- Rabbit: separate bodies, clean at rough resolution from four eye positions at 80 steps (`close-rabbit80d.png`).
  Volume 2.17 / 2.11 / 2.11. Its smaller bodies sit round the flat page only, as in the one-plane rule. seen, measured
- Siegel disc and San Marco: clean at 70 steps (`julia-s4.png`). seen. But the Siegel disc's volume is not settled:
  6.35 / 5.63 / 5.38 at 30 / 80 / 200 steps (one-plane: 4.98 / 4.82 / 4.82). A slow leak, not looked at closer. measured
- Mandelbrot solid: not spun (1.21 % of pairs differ). Flat set in the flat page and, but for a small notch, in the
  upright sheet (22 of 20,000 places differ there, measured); smooth heart shapes at 11.25, 33.75, 67.5, 78.75 degrees; the cut across is a four-pointed star.
  It is a body with four keels and rows of buds along the keels (`final-evc005e70k16.png`, `close-mandelz.png`). seen
- Faults. For c just off the x-axis (c = -1 + 0.03i, -1 + 0.1i, -0.75 + 0.1i) the bodies have a seam, fins, and at
  -0.75 + 0.1i a pitted surface (`final-evc005e70k16.png`, row 2). Three dials (0.05, 0.7, 16) and c's vote: it is a
  construction, not a carry-over of the flat rule. Against `along`: cleaner for c off the axis (`final-along.png`
  shows `along` shattered at -0.75 + 0.1i), four bud directions against eight.
- Not checked: no fine render, no close-up of the rabbit's skin.

### 2. `ease` (no dial)
Carried: theta. `theta <- theta + d - sin(2d)/2`, then P about theta.

- Flat page exact: yes on the page, but the flat rabbit has no body (79 % lost at a millionth). measured
- Basilica, San Marco, airplane: clean, four round buds of 12.4 degrees each, and the upright cut of the basilica is
  the flat basilica (`cuts-g1.png`, `close-basilica60.png`, `julia-s2.png`). measured, seen
- Rabbit: dust; volume 2.50 / 0.97 / 0.07. Siegel disc: fins. measured, seen
- Mandelbrot solid: not spun; the upright cut is the flat set exactly (0 of 20,000 places differ), but off the two
  sheets the period-3 bud is dust (188 pieces on the circle) and 3 to 14 % of the flat set has no body. measured, seen

### 3. `vote4` (plain votes, the tamest form of "follow the plane the orbit makes")
Carried: w, starts (4, 0). `w <- w + (y^2 - z^2, 2yz)`, square about the sheet along w.

- Flat page exact: yes, with body (rabbit 0.0 % lost, Mandelbrot 0.7 %). measured
- Basilica: buds only at the flat page (two arcs of 15 degrees). It is a slightly fattened one-plane rule. measured
- Rabbit: separate bodies with rows of small warts, and rings of specks round it (`close-rabbit80c.png`). seen
- Mandelbrot solid: not spun; the period-3 bud at the page is 14 degrees wide (about as wide as tall), none off the page.

## 6. Pictures (all opened and looked at)

| file | what it shows |
|---|---|
| `cuts-ref.png` | cuts of basilica and rabbit for the bench rules and the scout's: 2 buds (one-plane), ring (lathe), 8 (along) |
| `cuts-g1.png` .. `cuts-g9.png` | the same cuts for every rule of mine. g1: ease has 4 round buds, its rabbit is dust; over, mirror, twice: the rabbit is gone |
| `julia-s1.png` (24 steps), `julia-s2.png`, `julia-s3.png`, `julia-s4.png` (70 steps) | rough solids of the six Julia sets for the shortlists |
| `close-rabbit80.png`, `80b`, `80c`, `80d` | the rabbit at 80 steps from four eye positions: vote rules, evsum (grooves, a flange), evc (a brim), k4 and k16 (clean) |
| `close-basilica60.png` | the basilica's middle body close up: one-plane (buds on one circle), along (all over, with fins), ease and evc005e70 (two circles) |
| `close-mandelz.png` | the Mandelbrot solid where a bud at +z would sit: nothing (one-plane), rough rock (along, ease), a keel with a row of buds (evc005e70) |
| `mandel-m1.png` .. `m4.png`, `mandel-a1.png` .. `a5.png` | Mandelbrot cuts and rough solid for every rule |
| `explain-across.png` | cuts across the x-axis as the share goes 0 to 0.9: 2 buds, 4 buds, ring; and the Mandelbrot row: lens, lobes, shards, ring |
| `explain-film.png` | the flat Mandelbrot set lifted a millionth: red where it has no body |
| `explain-stab.png` | the first-order formula against that measurement |
| `final-evc005e70k16.png`, `final-along.png` | the harder look: c just off the x-axis, cuts at sheets that are not mirror planes, four eye positions |

## 7. What failed, and why

- **Turn away, overshoot** (mirror, away50, twice, over150, thrice, over, ease2): the flat picture loses its body
  for every c off the x-axis (4.3). The rabbit is a film on the page. Out.
- **Sheet moved after the squaring, or toward the image** (after, image, peek, and the scout's delay): the same. Out.
- **Settling** (settle, fade): the sheet stops at the wrong place. For the rabbit it must come back to c's own sheet
  (the flat page); if it stops elsewhere, the rule is the one-plane rule for a c that is off its sheet, and nothing stays.
- **Waking** (wake, late2, late3lag, the scout's first): lumps, like the lathe's.
- **Lag by distance from the sheet** (farfollow, nearfollow, snap45, stick30): wedge-shaped tears or dust.
- **Lag by distance from the axis without a scale** (axfar, axnear): rings where the point is far out, a broken rabbit.
- **Plain votes**: the rabbit keeps its body, but the basilica has buds only at the page (strong flat start) or arcs and
  ribs (weak flat start), and the Mandelbrot solid goes to rings (vote025: the full circle).
- **c's sheet alone** (cpull): for c in the flat page it is the one-plane rule exactly. Its Mandelbrot solid has arcs
  of 28 degrees at the page and no buds off it.
- **Eased votes without c's vote** (evsum): four buds on the basilica, but the rabbit's bodies have a groove and a
  flange where the upright plane cuts them, and some specks.
- **bisect**: fails the flat check.
- Two of my runs went over the ten-minute limit (the basilica close-up and the Mandelbrot zoom).

## 8. On Claim S

Nothing here speaks against it. Every rule of mine uses only the x-axis, c, the orbit's points and the flat start.
The two rules that forget the start at once (settle1, own) are spun exactly (0.00 %). All others are not spun, and
the only places where a bud of any width sits are the flat page and the sheet square to it (measured on the two
circles for 20 rules, `arcs.txt`). Elsewhere there is only dust or arcs of 1 to 3 degrees (`first`, `late2`, `ease`,
`easehalf`, `evote010`); `along`, which has a dial, has its buds at 45-degree steps.
