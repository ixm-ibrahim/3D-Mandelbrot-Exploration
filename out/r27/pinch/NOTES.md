# In six plain lines (round 27, explorer "pinch", question B3)

1. No. In an object of the balls-on-balls kind (kept by moves that can each be undone) kisses cannot be swapped
   for pinches. A stretch that is a chain of sphere inversions always has two ends, and bodies that meet in a
   point at one end meet again at the other: rings of two or three round a gap, never a tree. The true flat
   picture never has such rings. THEOREM, and built: `orange.png`.
2. A ball cannot come to a point. THEOREM. The roundest body that can, and that a stretch keeps, is a body pointed
   at both ends and round about its middle line (a lemon). With the opening the true bodies have at the meeting
   point it is 1.9 times as long as wide for c = -1 and 2.75 times for the rabbit. MEASURED.
3. With one-way moves fitted to z^2 + c (every move a chain of sphere inversions, and c is in it): c = -1 gives a
   clean chain of pointed bodies, 16 of 100 parts of the true area wrong (the balls object: 39), but no buds at
   all. The rabbit gets its three bodies at one point, but with stray copies that run into each other, 41 of 100
   wrong at best. MEASURED, SEEN `pinch-flat.png`.
4. More fitted moves make it worse: they contradict each other, and the copies fill the whole plane or scatter.
   MEASURED, SEEN `b-rabbit.png`, `baff-c1.png`.
5. The nearest clean thing takes the layout from the true flat picture and only the shape of each body from
   sphere inversions: 8 (c = -1) and 12 (rabbit) of 100 parts wrong, no overlaps. It is the flat picture blown up
   body by body: buds only round the flat picture. MEASURED, SEEN `pinch-solids.png`.
6. Nothing all-over comes out by itself. Every fitted move keeps the flat plane, so no body ever leaves it.
   THEOREM. The one free turn (only when c is on the x-axis) swings the flat picture's buds out of the flat cut
   and makes no new ones. MEASURED, SEEN `pinch-turn.png`. None of these objects passes the five tests. It is the
   wall of round 25's pillars again, reached by another door.

Marks: MEASURED (a number from a script here, log named), SEEN (in a picture I opened), REASONED (an argument, not
checked by a run), THEOREM (short proof given here, or a textbook fact). Everything is in `out/r27/pinch/`.

## 0. What a "fitted move" is here, and the three ways

z^2 + c has two undo-moves (the two square roots). One keeps the far end of the picture in place, the other keeps
the meeting point of the biggest bodies in place. Each pulls toward its point by a definite factor, with a definite
turn. A chain of sphere inversions with the same fixed point, factor and turn still has one thing open: its SECOND
fixed point (THEOREM: a stretch made of sphere inversions has two fixed points; a slide has one). Three natural
answers, all built (`pinchlib.fitted`):

- **stretch about a point**: the second fixed point is at infinity (a plain stretch and turn about the point).
- **same bend**: the move also agrees with the undo-move in its bend at the point. Nothing is left to choose.
- **pinned**: the move sends the other fixed point of z^2 + c where the true undo-move sends it, so that the first
  bodies meet where the true ones meet.

Way (a): the two fitted one-step moves, used as undo-moves: the object is every copy of a seed they produce.
Seeds: a ball on the middle body's two ends, or a body pointed at both ends with its tips there.
Way (b): the same with the fitted two-step and three-step moves added.
Way (c): the bodies of the true flat picture, placed by the TRUE undo-moves (three landmarks each: the image of the
meeting point, of its twin and of 0), each replaced by a ball or by a body pointed at both ends.
A fourth thing, not asked for, settles line 1: a picture kept by a stretch AND its undo-move (`orange.py`).

A body pointed at both ends ("spindle" in the code) is what one sphere inversion makes of a round cone. Every
chain of sphere inversions carries such a body to another one with the same opening. THEOREM; MEASURED: 0 of
200000 verdicts differ between "carry the points" and "carry the three landmarks" (`checks.log`). Cuts across the
line between its tips are exact circles (MEASURED: spread of the radius 0.0e+00). With a half opening of 90 degrees
it is the ball (MEASURED: 0 of 200000 differ).

## 1. The numbers at the meeting point (`step0.py`, `step0.log`)

- c = -1: meeting point at -0.61803; each step stretches there by 1.2361 with exactly a half turn. Far end
  1.61803, stretch 3.2361, no turn. MEASURED.
- Rabbit: meeting point at -0.27634 + 0.47973 i; stretch 1.1073, turn 119.94 degrees (0.3332 of a full turn, not
  exactly a third). Far end: stretch 2.7270, turn -20.60 degrees. MEASURED.
- How wide the true bodies open at the meeting point (share of small circles round it that is inside, over one
  whole period of sizes): c = -1: 0.629 inside, the two big bodies 0.613, so each opens 110 degrees. Rabbit: 0.695
  inside, the three big bodies 0.666, so each opens 80 degrees. MEASURED.
- A body pointed at both ends with these openings is 1.91 (c = -1) and 2.75 (rabbit) times as long as wide
  (MEASURED on the body, equal to the formula 1 / tan(quarter of the opening)). The true middle body of c = -1 is
  1.24 long and about 1.04 high: far rounder than any body with its own opening that a stretch keeps. REASONED
  from the two numbers: the true bodies are kept by a two-to-one move, not by a stretch.
- The two-step undo-moves of c = -1 cannot be fitted at two of their four fixed points (0 and -1, the centres of
  the two biggest bodies): the undo-move has no finite stretch there. The rabbit's three-step undo-moves: 3 of 8
  points the same. MEASURED. So the centres of the bodies are exactly where no sphere-inversion move can be fitted.
- How far the fitted one-step moves are from the true undo-moves at five landmarks: "pinned" is within 0.04 at the
  middle body's ends and centre, and off by 0.8 to 1.0 at the twin of the far end for c = -1 (rabbit 0.2 to 0.35).
  MEASURED. REASONED: the true undo-move turns that point a quarter turn off the x-axis (it is where the buds above
  and below the middle body come from); a sphere-inversion move fitted on the x-axis keeps the x-axis.

## 2. Way (a): two fitted moves (`step_a.py a`, `step_a.log`, `step_a_scan.log`, `a-c1.png`, `a-rabbit.png`)

Share of the true area with the wrong verdict (720 x 520 grid, the box of round 25; my measure gives 38.7 for the
balls object, round 25 had 38.6: `checks.log`). "Overlap" = share of the flat area of the largest bodies that lies
in two of them at once (bodies swallowed whole by a larger one not counted). All MEASURED.

- c = -1, ball seed: stretch about a point 74, same bend 39, pinned 45. Overlap 0 to 4.
- c = -1, pointed seed with the true opening (110): 47, 44, 35. Overlap 0 to 4.
- c = -1, pointed seed, the opening that fits best (140 degrees), pinned: **16**, overlap 0.
- Rabbit, ball seed: 152, 68, 98. Overlap 16 to 20.
- Rabbit, pointed seed with the true opening (80): 93, 60, 58. Overlap 8 to 22.
- Rabbit, the best of all fits and openings (same bend, 130 degrees): **41**, overlap 15.

SEEN (`a-c1.png`, `pinch-flat.png`): for c = -1 every version is a chain along the x-axis and nothing else. With
the ball seed and the pinned fit: beads that kiss. With the pointed seed: lemons tip to tip, pinched like the true
picture along the chain. There is no bud above or below any body, in any version. REASONED: both fitted moves keep
the x-axis, so every copy of a seed on the x-axis is on the x-axis.
SEEN (`a-rabbit.png`): with the ball seed the three bodies at the meeting point are one lump (three balls through
one point overlap: THEOREM of round 25). With the pointed seed there are three blades meeting in one point, as in
the true picture, and round them stray blades in wrong places that cross each other.
SEEN (`pinch-solids.png` right column, `solid-abest-rabbit-top.png`, `solid-pin-rabbit-a.png`): in space, a chain of
lemons for c = -1; for the rabbit lemons with smaller ones run into them; everything stands in the flat plane.

## 3. Way (b): more fitted moves (`step_a.py b`, `step_a.py baff`, logs `step_b.log`, `step_baff.log`)

All MEASURED; SEEN where a picture is named.
- c = -1, two-step moves: nothing new can be added (section 1). Three-step moves added (8 moves): with "same bend"
  and "pinned" the copies fill the whole box (inside share 1.0000; hundreds to thousands of copies are not even
  bounded). With plain stretches about points: 72 (ball seed) and 45 (pointed seed) against 74 and 47 with two
  moves: a few stray small bodies in wrong directions, no buds where the true ones are (`baff-c1.png`).
- Rabbit, two-step moves added (4 moves): "same bend" 215 and 176; "pinned" fills the box; plain stretches 165 and
  107 against 152 and 93 with two moves. Three-step moves added: the same numbers to within 1.
  SEEN `b-rabbit.png`: orange growth spreading over the picture; `baff-rabbit.png`: more and more stray blades.
- REASONED: a fitted move agrees with the undo-move only near its own point. It pulls toward that point and pushes
  away from its second fixed point, and for the longer moves that second point lies inside the picture (MEASURED,
  `step0.log`: for c = -1 one of them is at -0.07 + 0.29 i, inside the middle body). So the moves are no longer
  shrinking moves on the picture, and copies grow without end. The more points are fitted, the smaller the region
  in which each move may be trusted.

## 4. Way (c): the true layout, sphere-inversion shapes (`step_c.py`, `step_c.log`, `c-c1.png`, `c-rabbit.png`)

All MEASURED. Bodies down to size 0.005: 333 (c = -1), 941 (rabbit).
- A ball for every body (on its two landmarks): c = -1 43, overlap 2.5. Rabbit 65, overlap 8.
- Pointed bodies with the true opening: c = -1 (110 degrees) 30. Rabbit (80 degrees) 38. Overlap 0.
- Pointed bodies with the opening that fits best: c = -1 **8.4** at 140 degrees (1.43 times as long as wide),
  overlap 0.2. Rabbit **11.5** at 120 degrees (1.73 times as long as wide), overlap 0.4. 120 degrees is also the
  widest three bodies round one point can have at all (THEOREM: three round cones with one tip and disjoint
  insides open at most 120 degrees each).
- The images of 0 lie almost on the straight line between the tips (off by 0.006 of the length in the median for
  c = -1, 0.069 for the rabbit), so the bodies are nearly straight lemons (`checks.log`).

SEEN (`c-c1.png`, `c-rabbit.png`, `pinch-flat.png` right column): the eye reads both as the true picture: bodies in
the right places, pinched where the true ones are pinched, three round a point for the rabbit. What is wrong: the
true bodies have a corner under every bud (REASONED: every meeting point of the true picture is a copy of the
first one), the lemons are smooth except at their two tips, so every bud stands with its point on a round side;
and the true bodies are a little fuller (SEEN: blue slivers).
SEEN (`pinch-solids.png` left and middle columns, `solid-tree-c1-top.png`): in space a chain of lemons, pinched tip
to tip, with small lemons standing on them in ONE row round each body, the row of the flat picture. From the
second eye the row is plain. Nothing above or below it.
MEASURED (`checks.log`): every landmark of every body has height 0.0 above the flat plane. Against the one-plane
solid the verdicts differ in 21.5 (c = -1) and 25.2 (rabbit) of 100 parts of the one-plane volume: it is the look of
"one plane", a little thinner.
What this is, said plainly: not an object made of sphere-inversion moves. The places come from the square roots of
z^2 + c itself. Only the outline of each body is a sphere-inversion shape. It is a drawing of the flat picture with
a compass, blown up body by body.

## 5. In space: what could give bulbs all over, and the turn

- THEOREM (nothing to choose). A chain of sphere inversions of space that keeps the flat plane and does there what
  a given flat move does is fixed up to the mirror in the flat plane (two such chains differ by one that leaves
  every point of the flat plane where it is: that is "do nothing" or the mirror). It commutes with the mirror, so
  it carries a ball or lemon centred on the flat plane to one centred on the flat plane. So ways (a), (b), (c) put
  nothing off the flat picture, whatever the seed. MEASURED: all landmark heights 0.0.
- In the balls object the bulbs all over come from the second direction of the slides: a slide keeps one point, and
  in space there is a whole plane of slides about it. A stretch has two fixed points and a line between them. What
  is free in space is a turn about that line. But on the flat plane the turn is already given by z^2 + c: a half
  turn for c = -1, 119.94 degrees for the rabbit, both about the UPRIGHT line through the meeting point. That is
  the turn that lays the two or three bodies round the meeting point in the flat plane. It is used up. REASONED
  from the theorem above.
- For the rabbit there is no other turn: a move of space that carries the three bodies' directions into one
  another is that turn or its mirror image (THEOREM: three directions fix a turn of space). Not built, nothing to
  build.
- Only when c is on the x-axis is there a free turn: about the chain itself (the x-axis), because the bodies on the
  chain are round about it. I built it for c = -1 on the tree of way (c): each body is swung round the x-axis by
  the angle tau for every undo-move of the kind that keeps the meeting point in its chain (`objs.swung_tree`,
  `step_turn.py`, `step_turn.log`, `pinch-turn.png`). MEASURED, for tau = 0, 30, 60, 90, 120, 137.5, 180 degrees:
  - the bodies never run into each other: at most 0.01 of 100 parts of the solid lies in two bodies at once, at
    every tau. So every turn is allowed.
  - the flat cut loses the buds: grid points of the flat cut that lie off the chain's own bodies: 3928 with no
    turn, 1964 with a quarter turn, 0 with 137.5 degrees. Wrong verdicts of the flat cut: 8.4, 11.5, 14.6 of 100.
  - the buds are 0.7 of 100 parts of the solid; with a turn they sit in a few directions round the chain.
  SEEN (`pinch-turn.png`): the same buds as before, now standing out of the chain's bodies in several directions
  like warts; small specks float free where a bud standing on a bud was swung by a different angle than the bud
  under it; no body has buds all over, and no new bud appears. Which of the two undo-moves counts for the turn
  depends on where the square root is cut (the half turn tau = 180 does not give back the unturned picture:
  MEASURED 11.5 against 8.4), so the numbers are those of one labelling; the look is the same for the other.
  This is a dial picked by hand, it exists only for c on the x-axis, and it spoils the flat cut.
- So: nothing all-over, only bodies round the flat picture, or the flat picture's own buds swung about the chain.

## 6. Two short arguments, and the picture of the first

**A ball cannot come to a point.** THEOREM. At every point of its skin a ball has a flat touching plane and fills
the whole side of it as closely as one likes: near the point it holds cones of every opening below 180 degrees. A
body that comes to a point there holds only cones up to its own opening. So an exact ball meets a neighbour round
against round (a kiss), or the neighbour stands on it with a point, but the ball itself is never pointed. Two
exact balls kiss; three cannot share a point (round 25).

**The roundest body that can.** A body that looks the same at every size at its point is kept by a stretch about
that point. In the stretch's own frame it is a cone, and the roundest cone is the round one. Brought back by one
sphere inversion it is the body pointed at both ends, with circles as its cuts across the middle line. With a
straight middle line it is 1 / tan(quarter of the opening) times as long as wide: the wider the opening the
rounder, and at 180 degrees it is the ball and the point is gone. THEOREM for the formula, MEASURED on the bodies.
True openings: 1.91 (c = -1) and 2.75 (rabbit). Widest possible for three at a point: 120 degrees, 1.73.
If the middle line is bent far round, the same body looks like a ball with a notch (SEEN `orange.png`), but then
its two tips sit side by side, and in the flat picture the two main meeting points of a body lie at its opposite
ends.

**A stretch has two ends.** THEOREM. Let g be a chain of sphere inversions that stretches about p. It has a second
fixed point q, and every point other than p is carried toward q by g again and again. Suppose a picture is kept by
g and by its undo-move, and two bodies with disjoint insides are pointed at p. Only finitely many disjoint cones
of one opening fit round a point, so some repeat of g keeps each of the two bodies. A body kept by that repeat
holds a point x, hence the points g(x), g(g(x)), ..., which run into q. So both bodies reach q: they meet at p AND
at q, and close a gap between them. In the true flat picture of z^2 + c two bodies never meet twice (the picture
has no holes: a gap closed in by two bodies would be a hole). So no picture kept by moves that can each be undone
has the layout of the flat picture with pinches. The balls object can only kiss.
(REASONED, from a result on such pictures as I remember it and did not re-read: where two bodies of a group
picture touch at a single point with no second point, the move that keeps that point is a slide. This is the
converse and I did not prove it.)

**Built** (`orange.py`, `orange.log`, `orange.png`): the recipe of the balls object with the slide swapped for the
stretch and turn that z^2 + c has at its meeting point (factor 1.2361 with a half turn; factor 1.1073 with a third
of a turn) and one sphere inversion in a sphere that touches the first body. MEASURED: the two (three) biggest
bodies share BOTH tips ((-0.375, 0) and (0.375, 0); (-0.225, 0) and (0.225, 0)); overlap share 0.0000.
SEEN: two round bodies with a notch each, touching at two points with an eye-shaped gap between them; for the
rabbit's numbers two such bodies and a small lens between them, sharing both tips, with two slits as gaps.
Smaller pairs hang on the big ones round against round. It looks nothing like a flat picture of z^2 + c.

## 7. The five tests

The nearest object, way (c) with the best opening ("true layout, pointed bodies"):
1. Flat cut exactly the flat picture? **No.** 8.4 (c = -1) and 11.5 (rabbit) of 100 parts wrong. MEASURED.
2. Number of bulbs follows from the power? **Yes, but copied**: the bodies are placed by the square roots of
   z^2 + c, so their number per size is the flat picture's own. Nothing in space adds to it.
3. No shards, no smear? **Yes.** Overlap 0.2 and 0.4 of 100 parts; clean bodies from two eyes. MEASURED, SEEN.
4. No rings, and works for the rabbit? **Yes as worded** (no body is the flat picture spun round a line; the rabbit
   comes out as well as c = -1). But the reason for the test is not met: buds only round the flat picture.
5. Principled carry-over, nothing picked by hand? **No.** The layout is not made by sphere inversions at all, and
   the opening (140 / 120 degrees) is picked to fit.

Way (a), the only one in which every move is a chain of sphere inversions and c is in the recipe:
1. **No.** c = -1: 16 at best (35 with the true opening). Rabbit: 41 at best (58 pinned, true opening).
2. **No.** c = -1 has no buds at all, only the chain.
3. c = -1 **yes** (overlap 0). Rabbit **no** (overlap 15 to 22, stray copies crossing).
4. **No** for the rabbit (three bodies at a point are there, the rest is wrong). No rings: yes.
5. **No**: three ways to fit and the seed's opening are picks; with the picks fixed (pinned, true opening) the
   rest follows from c.

Way (b): fails 1 and 3 at once (fills the plane or scatters). The turned tree: fails 1 (the flat cut loses its
buds), 4 (no rabbit), 5 (a dial). The picture of section 6: fails 1 and 4 (rings round gaps), has no c.

## 8. Is this round 25's "one fitted at every point" pillars again?

Not the same build, the same wall. The scout's `fit` rule uses a different fitted move above every point of the
flat plane and steps forward; ways (a) and (b) use two to eight fitted moves everywhere and step backward. But:
- every fitted move keeps the flat plane, so nothing leaves the flat picture (section 5): the same reason the
  pillars stand only over the flat picture;
- the more points are fitted, the less each move may be used away from its own point (section 3). The end of that
  road is to use each move only at its own point, and that is `fit`. REASONED.
Way (c) is not `fit` either: it is the flat picture blown up body by body, the look of "one plane" (21 to 25 of
100 parts of the volume differ).
What is new here against round 25: the two-ends theorem and its picture (why the balls object can only kiss), the
measured openings and the lemon numbers, and the fact that a chain of lemons fitted by two moves is nearer the true
c = -1 picture (16) than the balls object (39) while having less of its structure (no buds).

## 9. Where the brief's section 3 is right, wrong or loose

- "A stretch about a point is a sphere-inversion move too (bodies come to a point there)": loose. Such a stretch
  always has a second fixed point. In a picture kept by the stretch and its undo-move the bodies meet there too
  (section 6). "Trees of bodies whose meeting points stretch instead of slide" exist only as one-way pictures.
- "Such a thing would have a c and could have a rabbit": right as far as it goes. Three bodies at one point do come
  out (SEEN). The rest of the rabbit does not (41 to 58 of 100 wrong, stray copies).
- "the moves that have the same fixed points and the same stretch there as the two undo-moves": each undo-move has
  ONE fixed point in the picture. The second fixed point of the fitted move must be supplied, and the three natural
  ways give three different objects (16 to 47 of 100 wrong for c = -1 with one seed).
- "A stretch about a point can come with any turn about its axis" (task text): true in space, but on the flat plane
  the turn is fixed by z^2 + c and is about the upright line. A free turn exists only about the chain and only for
  c on the x-axis (section 5).
- "for the rabbit the meeting point is turned by a third each step": 119.94 degrees, 0.3332 of a turn. MEASURED.
- "A round ball cannot come to a point, so exact balls and pinched bodies exclude each other": right (THEOREM).
  To add: a pointed body can stand on a ball (point against round); that is what every bud does in way (c).
- Not in the brief: for c = -1 the two fitted moves give no buds at all, because both keep the x-axis; and the
  centres of the bodies are the points where no move can be fitted (no finite stretch).

## 10. Not done, not checked

- Only c = -1 and the rabbit. No other c, no picture of the whole family of way (a) as c moves.
- Fitted moves of four steps and more. Seeds other than a ball and a straight lemon.
- A turn of each body's buds about that body's own middle line (bud by bud, by hand). Not built: it is not one move
  of space, and for the rabbit the theorem of section 5 leaves no turn.
- I tried to count the buds that come loose under the turn; the count was unreliable and is not kept. The loose
  specks are SEEN only.
- The picture of section 6 has one row of smaller copies (one touching sphere). More spheres would give more rows;
  not built. Its three-dimensional form with a plane full of stretches (bodies as arches all over a ball) is
  REASONED only.
- The converse in section 6 (touching once forces a slide) is remembered, not proved or re-read.
- The solids are unions of exact bodies; the skin is found by halving between blocks. The lab's renderer was not
  used. Nothing was put into the lab.
- `step_turn.log` numbers belong to one labelling of the two undo-moves (section 5).
- Pictures not opened by me after the last run: `b-c1.png`, `solid-treeball-*.png`, `solid-pinball-*.png`,
  `solid-turn90-c1-*.png` singly (the turned ones are in `pinch-turn.png`, which I opened).

## 11. Files

- `pinchlib.py`: fitted moves, bodies (ball, body pointed at both ends), flat cut of a union, solid of a union,
  sheets. `fam.py`: every copy of a seed under a set of moves; the true tree; overlap share. `objs.py`: the objects
  by name. `render.py <object> <eye> [w h blocks]`: one solid (kept as `depth-*.npz`, picture `solid-*.png`).
- `step0.py` -> `step0.log`. `step_a.py a | b | baff` -> `step_a.log`, `step_b.log`, `step_baff.log`, pictures
  `a-*.png`, `b-*.png`, `baff-*.png`. `step_a_scan.py` -> `step_a_scan.log` (the opening of the seed, 40 to 90
  degrees, three fits; in the code the fits are called 'affine' = stretch about a point, 'osc' = same bend,
  'pin' = pinned).
- `step_c.py` -> `step_c.log`, `c-c1.png`, `c-rabbit.png`. `step_turn.py` -> `step_turn.log`.
- `checks.py` -> `checks.log`. `orange.py` -> `orange.log`, `orange.png`.
- `compose.py` -> `pinch-flat.png`, `pinch-solids.png`, `pinch-turn.png`, `compose.log`. `render.log`.
- Run as: `PYTHONIOENCODING=utf-8 python -u -W ignore <script>` from this folder. Every run takes seconds to two
  minutes; the solids are 760 x 570 with 600 depth blocks.

## 12. Captions a person could be shown (two short sentences each)

- `pinch-flat.png`, right column: "The true layout with every body drawn as a lemon. Near, not exact."
- `pinch-solids.png`, left: "The flat picture blown up body by body. Buds sit only round the flat picture."
- `orange.png`: "Made the way the balls object is made, with a stretch in place of the slide. Bodies that meet in a
  point meet again at a second point."
- `pinch-turn.png`: "The same buds, swung round the chain. No new ones come, and the flat cut loses them."
