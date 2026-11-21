# Round 22, section "mandel": the orbit of c (the Mandelbrot solid)

Everything here is made with the library's rules (`out/r21/lib/mem.py`, `out/r21/judge/myrules.py`), point by
point. Marks: **(m)** measured, **(s)** seen in a picture I opened, **(r)** reasoned.
Internal names: `along`, `oneplane`, `wake` = `alongmem.c_wake1` (lab: "Along once, then one plane"),
`evc` = `sheet.evc005e70k16` (lab: "Pulled plane"), `lathe`. "Tilt" = the turn of c's page round the x-axis, from the
flat page. "Sideways" = round the x-axis, out of the page.

## 0. Files

| file | what |
|---|---|
| `mlib.py` | the rules, `trace()` (the loop of `M.stay`, keeping every point and the page each squaring was taken about), `fate()`, `arcs()`. Self-test: the page it reports reproduces `rule.step` to 6e-15; its counts equal `M.mandel` (0 of 360 differ, all five rules) (m) |
| `circles.py` -> `circles.txt` | c walked round the x-axis on ten circles (1,440 places, 600 steps): arcs, where the orbits end |
| `orbits.py` -> `orbits.txt` | the top bud's middle tilted 0..90: stays / leaves, the first steps as own page > used page; size of the bud in three directions; how near the orbit comes back to the middle. **Its column "round" in part B is wrong** (it averages in the reach toward the x-axis, which runs on into the heart: 0.300); use `roundness.txt`. Part C: in the flat picture the bud ends where the return distance reaches about 0.15 |
| `axisbuds.py` -> `axisbuds.txt` | the same step lists for the disc at -1 and the bud at -1.3107; along's route from the flat page to the slanted page |
| `roundness.py` -> `roundness.txt` | sideways reach against in-page reach for the buds of period 3, 4, 5 |
| `extra.py` -> `extra.txt` | along once against one plane (2,000,000 c, three boxes); the control rule; where along's orbits end; the pulled plane's page step by step; the upright copy against the flat set |
| `extra2.py` -> `extra2.txt` | one plane with a tilted c: does any start point stay; the same circles for `m_w3` ("Wind, then square") |
| `slant.py` -> `slant.txt` | along's slanted page: the cut against the flat set at 80 / 300 / 1000 steps, how fast an orbit leaves that page, lift test |
| `myrules.py` | ONE control rule, `flip` (one-plane square, then mirrored in the flat page). Not a candidate; it tests an explanation and refutes it (section 5) |
| `pictures.py` -> `c-swung-out.png`, `bud-from-above.png` | the two pictures for the user |

Circles used (the flat bud each one runs through): top bud of period 3, middle -0.1226 + 0.7449i; period-4 bud
0.2823 + 0.5301i; the big disc at -1 (radius 0.05, 0.125, 0.2, 0.24 of its 0.25); the bud at -1.3107 (radius 0.02,
0.04 of about 0.058); the heart at x = -0.12 (radius 0.3, 0.55 of about 0.63).

## 1. What the orbit of c does, rule by rule (m)

One sentence that holds for all of them: **in the Mandelbrot solid the thing that is off the flat page is c itself,
and c is added again at every step.** A rule cannot deal with that once, at the start, as it can with a start point.

**Where buds stand at all.** In every rule, a bud of the flat set stands exactly where c lies in a page in which
its whole orbit is squared: the orbit then never leaves that page and does what it does in the flat picture
(own > used = 0>0, 45>45, 90>90 at every step, `orbits.txt` A). Lathe: every page (one arc of 360 degrees, a ring).
One plane and along once: the flat page (2 arcs). Pulled plane: flat and upright (4 arcs). Along: flat, upright
and the two slanted pages (4 wide arcs and 4 thin ones on the top bud).

**Top bud (period 3), c walked right round, 600 steps** (`circles.txt`): lathe 1 arc of 360; one plane 2 arcs of
2.75 degrees; along once the same 2 arcs of 2.75; pulled plane 4 arcs of 8.75 at 0 / 90 / 180 / 270; along 4 arcs of
26.25 at 0 / 90 / 180 / 270 and 4 of 2.25 at the slanted pages. A ball as wide as the flat bud is tall would cover
about 14.5 degrees. (Round 21's judge had 2.9, 8.6 and 27.5 at 200 steps; confirmed.)

**One plane.** Tilt c by 1 degree: it still stays, on a three-hop whose third point stands 88 degrees off the flat
page (it is the point that comes back to the middle: only a hair above the page, but almost straight above 0).
Tilt 2: the pages of the orbit points go 2, 7, 88 / 3, 10, 87 / 5, 12, 86 ... and the orbit leaves after 28 steps.
Tilt 5: after 11. Tilt 10: 6. Tilt 30 to 60: 3. Upright: 2. The lift is multiplied on the way round: for a c lifted
by 0.0001 the point that comes back to the middle is 0.000536 above the page, **5.36 times the lift of c**
(`extra.txt` 2); the same c moved by 0.0001 inside the page comes back 0.000202 from the middle (2.02 times).
Reason (r): inside the page each step turns the small shift as well as stretching it, so the shifts of the three
steps partly cancel (|1 + 2 (c^2 + c)(1 + 2c)| = 2.02); out of the page the one-plane rule stretches the lift
(by 2 x length) but never turns it, so the lifts add up (1 + 2 x 0.869 x (1 + 2 x 0.755) = 5.36). That, and the fact
that the returning point is then squared about a page it stands square to, is why the bud is a blade.

**Along once, then one plane.** Not exactly one plane's solid, but as good as: of 2,000,000 random c in the box, one
plane keeps 28,906, along once 28,912, **8 verdicts differ** (0.028 % of the solid); in a slab |z| < 0.15: 30 of
217,813 (0.014 %); within 0.12 of the x-axis: 203 of 751,814 (0.027 %). The differing c are slivers of skin 0.07 to
0.19 from the x-axis at tilts round 40 degrees, and along once keeps a few more than it loses (`extra.txt` 1).
(Round 21's "0 of 200,000" was a sample too small to see them.) Why:
- the first step IS different: for the c that one plane keeps, the two landing places are apart by 0.005 (median),
  0.19 (99th percentile), 0.25 at most. It does not matter, because
- every later step is one plane's with the same tilted c, and **one plane with a c beyond its own solid keeps no
  start point whatever**: 0 of 300,000 random start points stay 200 steps for the top bud's middle tilted 2
  degrees or more, for the disc at -1 (radius 0.2) tilted 5 or more, for the heart (radius 0.3) tilted 45 or more;
  and wherever some start points stay, the orbit of c stays too (`extra2.txt` 1). So no first step can save it.
- Step lists (`orbits.txt` A): along once leaves 0 to 4 steps later than one plane at every tilt, never stays.
The same goes for "Wind, then square" (`m_w3`), whose trick is also a first step into the flat page: its top bud
has 4 arcs, at 0 / 180 (6.75 degrees) and 90 / 270 (1.75), and nothing at the 60-degree planes that carry its Julia
sets; other circles hold up to 36 arcs and are still losing places between 80 and 600 steps (heart at radius 0.3:
40.3 % of the circle inside, then 31.5 %) (`extra2.txt` 2). That is all I measured of it.

**Pulled plane.** c exactly upright: the plane is upright at the first step and stays (90>90 at every step), the
orbit is the flat orbit standing upright. The upright cut against the flat set: 372 of 336,000 places differ
(200 steps), every one within 0.053 of the x-axis; there c's pull (16 h^2 + h^2 at height h) is weaker than the
0.05 the flat page starts with, so the first squaring is still about the flat page (h < 0.054 from the rule (r),
0.053 measured). c in between: the plane goes part of the way and creeps (`extra.txt` 4): for c tilted 45 the plane
stands at 25, 29, 32, 50 at steps 1, 2, 3, 6 and the orbit leaves after 5 steps; tilted 20: 7, 10, 11, 15, leaves
after 6; tilted 5: 1.6, 2.1, 2.4, 2.9, 3.4, leaves after 24. With c pulling alone (no orbit), tilted 45: 24.8,
28.4, 30.3, 33.1, 35.4, 37.7, 39.9 at steps 1, 2, 3, 6, 12, 30, 100: after a hundred steps the plane is still 5
degrees short. Only within about 4 degrees of the flat page or of the upright page (arcs of 8.75) does the plane
get near enough soon enough. Why upright is special (r, from the formula): the pull falls short of c's page by 0.7 sin t,
t the doubled turn between plane and c; that is zero only at t = 0 and at t = 180 degrees (c square to the plane).
So the second copy is put there by the easing law, as round 21's judge said.
"Nothing between" needs one correction: **no buds between, but the big bodies do reach round.** The heart at
radius 0.3 and the disc at -1 at radius 0.125 are inside all the way round; further out the cut across is a
four-pointed star (heart at radius 0.55: 4 arcs of 49.5 degrees; disc at 0.2: 4 arcs of 16 to 18; at 0.24: 4 of
3.25). Where the flat orbit is pulled hard to one or two spots it survives a dozen squarings about the wrong page.
The pulled plane's orbits are lost in those first steps, not later: right up to the bud's sideways edge the
settled hop comes back to within 0.028 of the middle (`orbits.txt` C); under one plane and along that distance is
0.06 to 0.2 at the edge.

**Along.** Every orbit point is squared about a page at most 14.3 degrees from the page it lies in (the largest
value of sin(4 phi) / 4; every table shows "off its page by up to 14"). So a point that strays is followed: for c
tilted 5 the steps read 5>0, 16>3, 89>90: the point that comes back to the middle, standing straight up, is
squared about the upright page, nearly its own, and is sent back as the Lathe would send it. Consequences (m):
- **The solid is the flat set spun round the x-axis, roughened.** Of 60,000 random c, along keeps 4,071 (600
  steps); the spun flat set holds 4,221; 3,708 are in both, 363 only in along, 513 only in the spun set. The bodies
  ON the x-axis are complete all the way round: the heart at radius 0.55, the disc at -1 at radius 0.2, the bud at
  -1.3107 at radius 0.02 are 100 % inside, as under the Lathe.
- **Buds off the axis are patches of erratic width.** Sideways reach / in-page reach (1 = a ball), for the buds of
  period 3, 4, 5 (`roundness.txt`): in the flat and upright pages 1.77, 0.75, 5.05; in the slanted pages 0.16,
  3.30, 0.07. Which page gets the wide patch changes from bud to bud.
- **The rim is not a clean edge.** 21.6 % of the c in the solid have orbits that never repeat in 600 steps; of the
  c inside along but outside the spun set, 58 %. Walking c from the flat page to the slanted page (`axisbuds.txt`
  B) the hop goes, for the heart at radius 0.55: 1 spot, 2 spots, never repeats, 2, 1; for the disc at -1 at 0.2:
  2, 8, 16, 4, never repeats, 4, 2; at 0.24: 2, 16, 8, never repeats, then out. So going sideways the orbit is not
  simply let go: its hop doubles, turns disorderly, and only then, slowly, leaves (17 to 345 steps near the rim).
  The solid still leaks: 4,318 inside at 80 steps, 4,154 at 200, 4,071 at 600.
- 48.4 % of along's staying orbits end in one page, and 45 % end on a single spot (which lies in a page whatever
  it does); so hardly any hop of two or more spots ends in one page (one plane 97.5 % in one page, pulled plane 96.6 %).
- The slanted pages do not hold the flat picture firmly (`slant.txt`). The cut along the page at 45 degrees
  against the flat set (163,800 places): 657 verdicts differ at 80 steps, 1,601 at 300, 1,721 at 1000 (1,519
  flat-inside places lost, 4.5 % of the flat set); the upright and the flat page: 0, 0, at most 4. An orbit there
  that gets the slightest lift moves away from the page: for the disc at -1 (radius 0.2) started exactly in the
  slanted page the distance from the page is 2e-16 after 10 steps, 4e-8 after 100, 0.05 after 200 (rounding
  alone). The plane runs ahead of the point there. It is not a film, though: lifted by a millionth, 32,030 of the
  33,996 flat-inside places of that page are still inside (upright page 33,952; one plane's flat page 33,954).
  The period-5 bud reaches only 0.003 to 0.02 in that page against 0.04 in the flat page (300 steps).
That is the rock: the Lathe's ringed solid with each ring broken into four or eight patches of uneven width, and a
fringe of slow, disorderly orbits for a skin.

**The buds on the x-axis** (`circles.txt`, `axisbuds.txt` A). Disc at -1, radius 0.2: one plane 2 arcs of 7.75
degrees (tilt 5: leaves after 45 steps, tilt 90: after 5); along once the same arcs; pulled plane 4 arcs (18.25 at
0 / 180, 16.25 at 90 / 270); along the whole circle (two-hop for tilt up to 20, four-hop at 30 and 60, off its
page by up to 14). Bud at -1.3107, radius 0.04: one plane 2 arcs of 7.75; pulled plane 2 arcs of 27.75 at 0 / 180
and only 0.25 at 90 / 270 (so close to the axis c's pull is too weak to turn the plane at the first step: 90>0,
then 90>90); along 87.5 % of the circle in 34 arcs, with orbits that never repeat from tilt 30 to 60.

## 2. Answers to the section's four questions

1. **Why is along's solid a rock?** Because along never squares a point about a page more than 14 degrees from its
   own (m), the orbit of a tilted c does nearly what it does under the Lathe, so the solid is the flat set spun
   round (91 % of it lies in the spun set (m)), and what breaks the rings into patches is the leftover 14 degrees,
   which bites only near the skin and unevenly: patches 0.07 to 5 times as wide as a ball (m), rims made of orbits
   that wander for hundreds of steps (m). (s): `c-swung-out.png` row 5.
2. **Why is along once's solid one plane's?** Because the orbit of c has a tilted c added at every step, the later
   steps are one plane's, and one plane with such a c keeps no start point at all (m). The first step lands
   somewhere else (m) and it makes no difference to 9,997 of 10,000 c of the solid (m).
3. **Why has the pulled plane a second copy upright and no buds between?** A c that stands upright (square to the
   plane) gets the plane at once, by the easing law (m, r); any other c gets it part of the way and is thrown out
   in the first 5 to 25 steps, before the plane arrives (m). Big bodies survive those steps, buds do not (m).
4. **What would the orbit of c have to do for a round bud to stand away from the flat page?** Section 3.

## 3. What a round bud away from the flat page would take

(a) (m) At the bud's middle, c and its whole orbit must lie in one page and be squared in that page. All buds of
all five rules stand exactly at such c.

(b) (m) Moving c sideways out of that page by the bud's own radius, the orbit must be lost; not sooner, not later.
Measured sideways reach / in-page reach, periods 3 / 4 / 5: lathe never ends (ring); one plane 0.19 / 0.23 / 0.18
(a blade); pulled plane 0.60 / 0.85 / 0.62 (a lens), the same at its upright bud (0.59 / 0.83 / 0.61); along 1.77 /
0.75 / 5.05 and 0.16 / 3.30 / 0.07; the control `flip` 3.2 / 1.9 / 14.7. Nothing here is 1 for all three buds.

(c) (r, exact) How far the plane must follow c. Turn the whole picture round the x-axis: if the plane sits at the
share t of c's tilt at every step, the orbit of c is one plane's orbit of a c tilted (1 - t) as much, so the bud is
one plane's blade made 1 / (1 - t) times as thick. To be as thick as it is tall it needs t = 0.81, 0.77, 0.82 for
the three buds (that is thickness only; I did not check that the shape is then a ball): **the
plane has to go about four fifths of the way to c's page at once and stay there, and c must be left a fifth
of its tilt outside the plane.** (The pulled plane goes a third of the way at step 1 and reaches four fifths only
after a hundred steps (m: c tilted 4 degrees, plane at 1.3, 1.7, 1.9, 2.3, 2.7, 3.0, 3.3); its lens is 0.6 to
0.85.) A rule that follows c all the way makes a ring; one that does not follow makes a blade.

(d) (r) The catch. "Four fifths of c's tilt" is a tilt measured FROM a page where a bud stands. So the rule must
name those pages, and their number is what the user's second test forbids writing in: 1 (one plane), 2 (the
easing law), 4 (sin 4 phi). In none of the four rules does that number come from the power. For it to come from
the power the pages themselves would have to be made by the squaring. One way that is at least countable (r, not
tested, and the Mandelbulb, which doubles a second angle, fails the flat cut): if a squaring doubled the tilt as it
doubles the angle in the page, a hop of p spots could live only in pages that come back after p doublings: 1 page
for the heart, 3 for the disc at -1, 7 for the top bud, 15 for period 4.

(e) (m) Two ideas that do NOT work for the Mandelbrot solid:
- A special first step (along once; wind, then square): useless, because c comes back at every step (section 1).
- "Make the lifts cancel the way in-page shifts do." The control `flip` (one-plane square, then mirrored in the
  flat page; same Julia sets as one plane for c in the flat page) brings the returning point back at 1.89 times
  the lift of c, close to the in-page 2.02, instead of 5.36. Its buds are not balls but ribs: 3.2, 1.9 and 14.7
  times too wide, with more inside beyond. So how near the orbit returns to the middle does not decide where the
  bud ends; along shows the same (it returns at 0.2 and stays, where the flat picture lets go at about 0.15).

(f) (m, r) For the buds ON the x-axis a ball is the flat bud spun round the x-axis, which the Lathe and along
already give. The whole difficulty is buds off the axis: spun round the x-axis they are rings; a ball would be the
flat bud spun round its own stalk.

## 4. The two pictures for the user

- `c-swung-out.png`: five rows (lathe as the reference, then one plane, along once, pulled plane, along). In each:
  72 positions of the top bud's middle swung round the x-axis over the cut across the solid there (big dot = the
  orbit stays); the orbit of the c swung 8 degrees, step by step; the orbit of the c swung upright; the rough
  solid (40 steps, eye at (0.45, 0.5, 1)). One sentence under each row.
  Counts in it (m): 72, 2, 2, 4, 29 of 72 stay; the c swung 8 degrees: stays / out after 8 / out after 8 / out
  after 12 / stays on three spots that are NOT in its page; upright: stays / out after 2 / out after 3 / stays / stays.
- `bud-from-above.png`: the top bud of each solid cut level through its middle (the plane y = 0.7449, 300 steps),
  with the circle a ball would show, and below it the bud as a rough solid (50 steps, 200 x 200 x 130 blocks
  enlarged, eye at (1, 0.42, 0.22): looking along the x-axis so that the flat page is seen edge-on). Verdicts under
  the cuts: ring / blade, a fifth as thick as a ball / the same blade / lens, 0.6 / ragged bun, 1.8 times as wide.
  (s) The top row is the clear one. In the bottom row the blade and the lens read well; the Lathe's and along's
  tiles are close-ups of a ridge and of a lumpy mound and say little without the row above.
- Read as a non-mathematician (s): both pictures use only page, plane, orbit, c, bud, body, step, hop, spot; the
  only number of degrees is "8 degrees" for "a little". The words "ring", "blade", "lens", "bun" are everyday
  comparisons, one per shape. No internal name appears.

## 5. For the design section, in short

- (m) In the Mandelbrot solid a rule has to deal with c's tilt at EVERY step. It can do that by looking at c
  (pulled plane) or by following the orbit points, which carry c's tilt with them (along, lathe). A first-step
  trick does nothing (along once, wind then square).
- (r) How the plane answers to the TILT of c shows only in the Mandelbrot solid (and in Julia sets of a tilted c):
  a c in the flat page has tilt zero. So the buds of the Mandelbrot solid away from the flat page and the buds of
  the usual Julia sets are shaped by different parts of a rule: the first by how the plane answers to a tilted c
  (or to an orbit dragged along by it), the second by how it answers to the start point. (A rule that looks at c
  still acts on the usual Julia sets through c's distance from the x-axis: the pulled plane's c pulls toward the
  flat page there, which is how it keeps the rabbit clean.)
- (m) Follow all the way: ring. Do not follow: blade, a fifth as thick as tall. Follow a third at once and four
  fifths in the end: lens, 0.6 to 0.85. (r) Four fifths at once: thickness right (section 3c).
- (m) The pulled plane loses its orbits in the first 5 to 25 steps, while the plane is still on its way; nothing
  goes wrong later. (r, not tried) A plane that is where it will end up BEFORE the first squaring would not have
  this loss; such a plane is a function of c alone, and a function of c that jumps between "nearest to flat" and
  "nearest to upright" has a seam half way.
- (m) Along's fault in this solid is not too little following but too much, and unevenly: never more than 14
  degrees off, so it is nearly the Lathe; the patch widths (0.07 to 5 balls) and the disorderly rim come from
  what is left over.
- (m) Refuted: "bring the returning point back at the in-page rate" (`flip`, section 3e).
- (r) Open: where the pages that carry buds should come from, if not from a number in the rule (section 3d).

## 6. What I did not do

- No cuts or solids coloured by where the orbit ends; the ends are in tables only.
- The on-axis buds (disc at -1, bud at -1.3107) are in the tables, not in a picture.
- Power 2 only. Three off-axis buds (periods 3, 4, 5) for roundness; the smaller buds were not measured.
- "Never repeats" means: no cycle up to length 64 to within 0.001 in 600 steps. I did not separate orbits that
  wander for ever from very long cycles or from orbits that would leave after more than 600 steps.
- The step-by-step fine print (stretch ratios, inside-out) is the stability section's; I measured none of it.
- (d) of section 3, the doubled tilt, is an idea, not a rule; nothing was built or tested.
- I did not look at the lab or at `src/`; the pictures are the library's rough blocks, not the lab's rendering.
