# Round 27, judge: answers (Track B, "are we close?")

Every number here is from my own scripts (NOTES.md names the log for each). Marks: measured, seen, reasoned, theorem.
Pictures: `1-how-close.png`, `2-carried-over.png`, `3-pinched.png` (real shapes; solids from two eyes, 1000 x 750 x 700 blocks).
No explorer claimed success, and I found none.

## (1) Are we close? Eight plain lines

1. No. Balls on balls is a cousin of z^2 + c. The gap is one of kind, not of amount, and nothing this round closed it. (measured, seen, theorem)
2. How it is made: slide the point by the nearest whole number, turn it inside out through a sphere, repeat. That is sphere inversions and quaternion arithmetic and nothing else. That half of the hunch is right. (measured)
3. The same as z^2 + c: one simple move, repeated, leaves a body with smaller bodies on it at every size. For c = -1 even the layout is the same: a middle body, two neighbours, buds on buds, two bodies at every meeting point. (seen)
4. Different, and this is the whole gap: every move of the balls object can be undone. z^2 + c sends two points to one and cannot be undone. (reasoned)
5. What the eye sees of that: exact balls where the true bodies are pointed, kisses where they pinch, buds at the fractions where the true buds sit at the halvings. About 39 of every 100 parts of the true c = -1 area come out wrong. (measured)
6. It has no c and no power, and none of its dials plays the part of c. Three balls cannot meet in one point, so it has no rabbit. (measured for the dials tried; theorem for the rabbit)
7. Two repairs were tried. Carrying its bulbs onto the true flat picture makes the flat cut exact, but needles and upright walls grow wherever bodies meet. Swapping kisses for pinches turns the bodies into lemons and leaves buds only round the flat picture. (measured, seen)
8. So: sphere inversions are what make round bulbs come all over by themselves, and the very thing that lets them do it (each can be undone) is what keeps them from being z^2 + c.

### The user's question "how is it generated?", ready to pass on

Take a point. Slide it sideways by a whole number, so that it lands in the middle cell of a square grid. If it now lies
inside one of two unit spheres (one sits on the floor, one hangs from the ceiling), turn it inside out through that
sphere: near becomes far. Repeat. A point that ever drops below the floor or rises above the ceiling is inside a ball. A
point that comes to rest between them, outside both spheres, is outside for good. Eight rounds settle every point. In
quaternion words: take away a whole number, then take one over the mirrored number. Nothing else is in it: no c, no
power, no squaring.
(measured: my own recipe, written from this text, gives the same verdict as round 25's code at all 1.8 million points
tried; after 8 rounds none of 200000 points is undecided; the bodies are balls to one part in ten million.)

## (2) The three questions

### B1. How close is it, where is it off, and does it have a dial like c?

Answer.
- Close in layout, off in kind. Against the true flat picture of c = -1, 38.5 of every 100 parts of the true area get the wrong verdict, at the lab's setting and at the best setting alike. (measured; round 25 had 38.6)
- c = -1 is not the true picture it sits nearest to. That is c = -0.84 on the x-axis: 16.6 of 100 wrong (c = -0.8: 17.3; c = -0.75: 20.6; c = -0.9: 20.7). There the true bodies are themselves nearly round. Still one part in six wrong, and the buds are in other places. (measured; seen in measure's `fit-c-084.png`)
- Off in three ways the eye can check:
  - Balls against pointed bodies. Every body is a ball: of 200000 points just under the skin of four bodies, none is outside. (measured)
  - Kiss against pinch. Round the meeting point of c = -1 about 140 of the 360 degrees of a small circle lie outside, however small the circle (144, 140, 140, 130, 138 at five sizes). Round a kiss of balls the outside shrinks with the circle: 30, 6.7, 2.2, 0.64, 0.21. (measured)
  - Fractions against halvings. On the balls object a walk round the middle ball meets a bud at every fraction (1/2, 1/3, 2/3, 1/4 ... each within 0.0002 of the way). On the true picture the buds are attached at 1/2, 1/4, the eighths, the sixteenths of the way round. (measured)
- A kiss alone does not tell the two apart: the true picture of c = -0.75 kisses too, and tighter than balls can (5.4, 0.48, 0.08 degrees). Exact balls and fractions tell them apart. (measured)
- No dial like c. (measured for what was tried, reasoned for "none")
  - The dial t (size of the neighbours) changes sizes only. Between c = -0.5 and c = -0.75 it can follow what c does to the sizes (best t 2.1, 1.5, 1.3), never to shapes or to the places of buds.
  - New from measure, and it holds under my own test: below t = 1 the dial has single settings where the balls close up in rings of 3, 4, 5, 6, 8. Between those settings the balls would cut into each other.
  - The sideways slide: on the square grid only half steps are allowed (the chain forks). On a coarser grid the slide is free (the chain bends). Every setting keeps two bodies at every meeting point.
  - The nearest thing to a rabbit is the ring of three: three balls that kiss two at a time round a hole, at one single setting. It is not a rabbit: three balls cannot share a point. (theorem; seen in measure's `rabbit-nearest.png`)
  - The plain chain of balls, fitted as well as it can be to the true rabbit, gets 56 of every 100 parts wrong. One plain disc gets 68. (measured)

Evidence: `j1_recipe.log`, `j1b_ball.log`, `j2_fit.log`, `j3_kiss.log`, `j7_family.log`, `j8_rabbitfit.log`, `j9_buds.log`.
Picture: `1-how-close.png`. For the buds, measure's `buds.png` reads at a glance and may be shown as it is.

The five tests for the balls object: (1) flat cut exact: no. (2) bulbs from the power: no, it has no power. (3) no shards, no smear: yes. (4) no rings: yes, it is not a spun flat picture; the rabbit: no. (5) principled carry-over: no, it carries over a cousin.

### B2. Can it be carried over so that the flat cut becomes exact, and do the bulbs off the flat picture survive?

Answer.
- The flat cut can be made exact. The bulbs survive in part. The result is not clean, and it is not the user's object. (measured, seen)
- What was built (respace's best of four ways): keep the true flat picture, body by body. Give each body its own round shape, and stamp onto it the bulbs that the middle ball of Balls on balls carries off the flat plane.
- What holds, by my own check:
  - Flat cut exact for c = -1 and for the rabbit: 0 wrong verdicts of 30000 random points each. (measured)
  - The same above and below the flat plane, and for c = -1 the same left and right (0 of 200000 points differ). Not a spun flat picture. (measured)
  - The biggest bulb is round (1.01 times as long as thick). The next four are eggs (1.48). Of 28 medium bulbs the middle value is 1.55, the worst 2.65. For the rabbit, which respace did not measure bulb by bulb: 1.01, then 1.7, medium 1.9, worst 4.0. (measured)
- What fails:
  - Needles. Where a bud is attached, the solid shoots up in hair-thin needles. For c = -1, columns more than twice as high as the middle body (taller than 1; the body is 0.5 high) stand over 16 of 1.4 million flat grid points; for the rabbit over 106. They are real, not a fault of the drawing: asked point by point they are there too, up to 1.6 high at the points I asked again. (measured, seen)
  - Upright walls. Where two bodies meet, each still stands 0.15 high (c = -1) when one is 0.002 to 0.005 away from the meeting point; the body is 0.5 high at its middle. For the rabbit the skin rises toward the meeting point, from 0.27 to 0.43: a blade. (measured)
  - A quarter of the first bulbs (20 of 79) lean out over the rim and are cut off by an upright wall. (measured)
  - Loose pieces: 38 with blocks of 0.01 and 160 with blocks half that size (c = -1); 66 and 336 (rabbit). The finer one looks, the more there are. (measured)
  - The bulbs are borrowed. They sit where the grid of whole numbers puts them, not where the squaring would put them. Nothing in the rule makes them.
- respace's own surprise stands: the re-spacing from fractions to halvings is the one thing that must not be taken off the flat plane. It would have to squeeze the biggest bulb from 26 degrees into 11, and the last 10 degrees of a ball's rim out of the last 0.07 degrees of the true rim. (measured; the bulbs "pressed flat" I saw in respace's picture only)
- The flat match itself is exact as a verdict (0 wrong of 30000), but that proves little: it comes out right for any choice of the moves. (measured; reasoned by respace, and I agree)

Evidence: `j5-flat.log`, `j5-family.log`, `j5-round.log`, `j5-pieces.log`, `j10_needles.log`, `j11_misc.log`.
Picture: `2-carried-over.png`.

The five tests for the carried-over object: (1) flat cut exact: yes, both sets. (2) bulbs from the power: no. (3) no shards, no smear: no for c = -1, worse for the rabbit, and worse the finer one looks. (4) no rings: yes; works for the rabbit: it runs, and fails test 3 there. (5) principled, nothing picked: no (the grid, the size dial, straight columns, and nothing drawn above the gaps are all picked).

Where I differ from respace: at my finer blocks c = -1 has needles too, not only "short thorns", and the loose pieces are more than 22 and 50 and grow with finer blocks (NOTES.md).

### B3. Can kisses be swapped for pinches while every move stays a sphere inversion?

Answer.
- Not in an object of the balls-on-balls kind. If a picture is kept by a stretch about a point and also by its undo-move, bodies that meet in a point there meet again at a second point and close a ring round a gap. The true flat picture has no such rings. (theorem: pinch's short proof, which I read and find sound)
- With one-way moves fitted to z^2 + c there is a c, and three bodies do meet in one point. But:
  - c = -1 gives a bare chain of pointed bodies with no buds at all: 0 of 1764 bodies lie off the x-axis. 16 of 100 parts wrong. (measured)
  - The rabbit gets its three bodies at a point plus stray copies that run into each other: 41 of 100 wrong at best. (measured; seen in pinch's `pinch-flat.png`)
- The nearest clean thing takes the places of the bodies from the true flat picture and only their shape from sphere inversions. Each body becomes a lemon, pointed at both ends. Flat cut 8.4 of 100 parts wrong for c = -1, 11.6 for the rabbit. Clean from both eyes. (measured, seen)
- It gives nothing all over. Every lemon is centred on the flat plane (no tip of any body is off it), so the buds sit in one row round the flat picture. It is the flat picture blown up body by body: the look of "one plane". (measured, seen)
- A ball cannot come to a point, and a body pointed like the true ones cannot be round: with the true opening at the meeting point (about 110 degrees for c = -1, about 80 for the rabbit) a lemon is 1.9 and 2.75 times as long as wide. (theorem; measured)
- The one free turn (about the chain, and only when c is on the x-axis) swings the flat picture's own buds out of the flat cut and makes no new ones: the flat cut goes from 8.4 to 11.5 to 14.6 of 100 wrong. (measured)

Evidence: `j6_pinch.log`, `j11_misc.log`, `j12_opening.log`.
Picture: `3-pinched.png`.

The five tests for the lemons: (1) flat cut exact: no, near. (2) bulbs from the power: copied from the flat picture, nothing added in space. (3) clean: yes. (4) no rings: yes as worded, but the buds are only round the flat picture, which is what the test is there to catch. (5) principled: no, the places are not made by sphere inversions and the opening is picked to fit.

One caution about pinch's picture `orange.png`: its bodies are built with their tips at the two points, so "they share both tips" is put in by hand. The picture shows that such an object exists without bodies running into each other. The claim rests on the proof.

## (3) Is there a lead worth another round?

There is none.

- The carried-over object (picture 2) is the nearest to the look, and it does pass two things round 25's nearest tries failed: it is the same above and below, and one and the same build gives c = -1 and the rabbit with the flat cut exact. But it passes them by not being a rule off the flat plane at all. Its bulbs are stamped on, not made by the squaring. So it fails tests 2 and 5 by the way it is made. It fails test 3 at every point where a bud is attached, at every size, and more with finer blocks. That will not polish away: each true body has a corner at every bud, and at a corner its own round shape is squeezed to nothing.
- The lemons (picture 3) are "one plane" again.
- The balls object itself has no dial that leads toward z^2 + c: I tested the three dials and found forks, bends and rings, never a third body at a meeting point.
- What is open is what was open after round 25, unchanged: whether some rule that folds space onto the flat plane can keep its squeeze bounded step after step. Nobody here has a candidate. This round shuts two more ways and opens none: moves that can be undone give kisses and no c (B3), and a body-by-body carry-over breaks at the corners (B2).
- If the orchestrator wants one thing from the user, it is a question, not a round: does picture 2 look worth having as its own clearly labelled entry ("bulbs borrowed from Balls on balls"), knowing its needles? I would not build it unasked.

## (4) What may and may not be told

### May be told

- How it is generated, in the words above. It is exactly sphere inversions and quaternion arithmetic.
- The hunch is half right. Sphere inversions and quaternion arithmetic are what make round bulbs come all over by themselves. The other half: each such move can be undone, and z^2 + c cannot be undone, because it sends two points to one.
- It has the layout of c = -1: a middle body, two neighbours, buds on buds. About 39 of every 100 parts of the true area come out wrong.
- By eye: round balls where the true bodies are pointed; kisses where they pinch; buds at the fractions (1/2, 1/3, 2/3, 1/4 ...) where the true ones sit at the halvings (1/2, 1/4, 3/4, 1/8 ...).
- The true flat picture it sits nearest to is not c = -1 but one a little to the right on the x-axis (c = -0.84), where the true bodies are themselves nearly round. Even there one part in six is wrong.
- It has no c and no power, and none of its dials acts like c. One dial changes the size of the neighbours. A sideways slide makes the chain fork or bend. Below a certain size setting the balls close up in rings of three, four, five, but only at single settings.
- It cannot be a rabbit: three balls cannot meet in one point. The nearest it comes is three balls kissing round a hole.
- We tried carrying its bulbs onto the true flat picture. The flat cut is then exact, for c = -1 and for the rabbit, and the biggest bulbs stay round. But needles and upright walls grow wherever bodies meet, the rabbit is worst, and the bulbs are borrowed, not made by the squaring.
- We tried swapping kisses for pinches. The bodies become lemons, the flat cut is near but not exact, and the buds sit only round the flat picture.
- It is proved that in an object made the way Balls on balls is made, kisses cannot be swapped for pinches.
- Nobody found the user's object this round either. The wall of round 25 stands.

### May NOT be told

- That we are close, or "pretty close to something". The gap is one of kind.
- That the carried-over object is a 3D picture of c = -1 or of the rabbit, or that it "works". It has needles at every meeting point and its bulbs are stamped on.
- That the balls object "is" the picture of c = -0.84, or fits it well. One part in six is wrong and the buds are elsewhere.
- That the lemons are a find. They are the flat picture blown up body by body.
- That the ring of three balls is a rabbit, or a step toward one.
- That one of the dials is "like c".
- That the user's object is impossible. No proof reaches every rule. Everything in round 25's list still holds.
- Any number I did not re-measure: the ring of three against the rabbit (89 of 100), anything about the lab's old Kleinian picture and its spirals, "never spirals", the fins and pressed bulbs of respace's other ways, pinch's "more fitted moves fill the plane".
- Any internal name, angle or percentage as an explanation.

## (5) Pictures for the user

1. `1-how-close.png`: top row, the true flat picture of c = -1, the flat cut of Balls on balls, and one on the other. Bottom row, the solid from two eyes and the meeting point ten times closer.
   Caption: "The same layout, but round balls where the true bodies are pointed: about 39 of every 100 parts of the true area come out wrong. Where two true bodies pinch, two balls only kiss."
2. `2-carried-over.png`: the bulbs carried onto the true flat picture, c = -1 and the rabbit, each from the front and from above.
   Caption: "The bulbs of Balls on balls carried onto the true flat picture: the flat cut is now exact. But needles and upright walls grow wherever bodies meet, and the rabbit is worst."
3. `3-pinched.png`: kisses swapped for pinches, c = -1 and the rabbit, each from the front and from above.
   Caption: "Kisses swapped for pinches: every body becomes a lemon, and the flat cut is near, not exact. The buds then sit only round the flat picture; none come all over."

## Corrections to the brief (ROUND27.md), as I found them

- Section 1, "one dial t >= 1": below 1 there are single good settings (rings of 3, 4, 5, 6, 8). Confirmed by my own test on two grids. On the square grid with slides by every whole number, rings of 3 and 4 leave no outside at all, and at rings of 5 and 6 my test is not quite clean (8 and 5 contradictions of 480000): not resolved.
- Section 1, "about 39 of every 100": stands (38.5).
- Section 3, "the object may sit nearer to c = -0.75": it does (20.6), but the nearest is c = -0.84 (16.6).
- Section 3, "kisses instead of pinches" as the sign of the difference: true pictures can kiss too (c = -0.75). Balls and fractions are the sign.
- Section 3, B2, "extend the match off the flat plane": the rim match is the one part that must stay in the flat plane. And "only c = -1 and its relatives" is not so for the carry-over that was built: it runs for the rabbit with an exact flat cut.
- Section 3, B3, "a stretch about a point is a sphere-inversion move too": yes, but it has two ends, and that is what rules pinches out of an object of the balls-on-balls kind.
- Section 1, "it can never be a rabbit": stands.
