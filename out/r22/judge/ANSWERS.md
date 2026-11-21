# Round 22: what the orbits are doing. Answers to Q1 to Q4

Written by the judge, who did not do the work. Every sentence is marked **measured** (a number I computed again with
my own scripts, unless it says whose number it is), **seen** (in a picture I opened) or **reasoned**.
Words: a *page* is a plane through the x-axis (a book whose spine is the x-axis); the *flat page* holds the flat
picture; a *step* (or jump) is: square, then add c. Evidence and numbers are in `NOTES.md` beside this file.

The five pictures, in the order of the questions (all in `out/r22/judge/`):

1. `1-how-a-bud-is-made.png` (Q1, Q3)
2. `2-buds-on-a-bud.png` (Q1, Q3)
3. `3-rabbit-same-bodies.png` (Q2, Q3)
4. `4-why-the-bodies-run-together.png` (Q2)
5. `5-new-tries.png` (Q4)

## Q1. Why does "along" grow round buds in many directions, and why are the others smooth off the flat page?

1. A point belongs to the shape only if the place it jumps to belongs too, so a bud is a place whose points jump, in
   a few steps, into a body on the x-axis. **reasoned** (it is what "the orbit stays" means)
2. A point lands where the flat picture says only if it lies in the page it is squared in; a point that is off its
   page is thrown to the side and lands outside. **measured** (on the ring through the top bud of the middle body a
   point stays exactly when it is nearer to its page than 0.066 under along, 0.075 under one plane)
3. One plane squares every point about the flat page, so on every ring round the x-axis only the two places beside
   the flat page come through: two buds, smooth everywhere else; the Lathe squares every point in its own page, so
   the whole ring comes through and the bud is a ring. **measured** (2 places / the whole ring, on four rings)
4. Along has four pages (flat, upright and two slanted) in which a point is squared in its own page at every step,
   and its first jump also throws some points from between the pages next to the flat or the upright page: eight
   buds round the middle body, sixteen round the bodies beside it. **measured** (8, 16, 16, 16 on four rings); **seen** in picture 1
5. Each big bud of along carries sixteen small buds all the way round its own stalk, and only two of them lie in the
   big bud's own page: these are buds of 3D, not copies of the flat picture standing in a plane. **measured** (16 on
   a ring round the stalk of the big bud in the flat, the slanted and the upright page; one plane and "along once"
   have 2); that fourteen lie in none of the four pages is **reasoned** from where that ring runs; **seen** in picture 2
6. A bud comes out round where the step keeps shapes (beside the flat and the upright page) and thin where the step
   squeezes (beside the slanted pages, on the left half): there along's buds are one and a half to three times as
   long as thick, and the buds on them thinner again, which are the thin fins. **measured** (long to thick 0.91,
   1.47, 2.86 round the left body; the squeeze follows one formula to four digits); the "thinner again" figures
   (7 and 19 to 1) are the stability section's and I did not measure them again

## Q2. Why is the rabbit one lump under "along", and clean but one-plane-like under the others?

1. Nothing new hides in the lump: every orbit that stays ends up hopping round the same three spots of the flat
   picture, under along just as under one plane. **measured** (19,798 of 19,798 orbits of along; the same for one
   plane, along once, the Lathe)
2. So the lump is the same bodies as one plane's, grown fat off the flat page and pressed against each other along
   whole walls, where one plane's bodies touch at single points. **measured** (a seventh of along's skin is wall
   between two bodies; one plane: next to none); **seen** in picture 3
3. The cause shows above the point where three bodies meet: one plane lifts a point there a little further at every
   step, at every height, so that space empties and the bodies stay apart. **measured**; **seen** in picture 4
4. Along lifts a point only very close to the flat page; higher up it brings points down, they hover at one small
   height and slide sideways into a body, so the space above the meeting point is filled in. **measured** (the
   height is multiplied by 1.11 next to the page, by 1.00 at height 0.075, by 0.07 at height 0.3; three quarters of
   the space above the meeting point is inside at every height, against nothing above height 0.2 under one plane)
5. It brings them down because off the flat page along squares a point about a page tipped toward the point, as the
   Lathe does (the Lathe's rabbit is a lump of the same kind); for c = -1 that does no harm, because there every
   body and every meeting point sits on the x-axis, which lies in every page. **reasoned**, with these **measured**:
   for c = -1 all four of along's pages show the flat picture exactly, for the rabbit only the flat page does; two
   thirds of along's lump lies inside the Lathe's
6. One plane, "Along once" and "Pulled plane" stay clean because off the flat page they square about the flat page
   (or nearly so), which pushes points away as hard as the flat picture needs; the same habit is why they have no
   buds off the flat page. **measured** for one plane; pulled plane's rabbit is nine tenths one plane's (**measured**);
   the link between the two is **reasoned**

## Q3. Why does "Along once, then one plane" look promising, and what exactly does it lose?

1. Its first step is along's, and the eight big buds of the middle body need only one step to reach the x-axis: all
   eight are there, and round. **measured**
2. Every later step is one plane's, so whatever needs a second step off the flat page is lost: the bodies beside the
   middle one keep 6 of along's 16 buds, the rings further out keep 2, and each big bud carries 2 small buds instead
   of 16. **measured**; **seen** in pictures 1 and 2
3. On the rabbit it gives separate bodies, fatter than one plane's, but two of them hang loose, one above and one
   below the flat page. **measured** (the main piece and two loose ones of 7 % each); **seen** in picture 3
4. Each loose body is a place far off the flat page whose points the first step throws straight down into one
   ordinary body of the rabbit; from then on they are ordinary points of that body. **measured** (all of its points
   land in that one body); why nothing joins it to the rest is **reasoned**
5. Its Mandelbrot solid is one plane's to within a few parts in ten thousand (not exactly the same, as was said last
   round), because there c is added again at every step and a special first step cannot help. **measured** (4 of
   2,000,000 verdicts differ); the reason is **reasoned**, with this **measured**: one plane with such a tilted c
   keeps no start point at all

## Q4. What would a rule have to do, and do the orbits point at such a rule?

1. For a bud to stand off the flat page, a step must throw some places that are off the page onto it; the flat rule
   sends two places onto each spot, and a rule that does only that (one plane) can have buds round the flat page and
   nowhere else. **reasoned** (a proof for rules that do not fold space, an argument for the others); the counts are
   **measured**: one plane 2 places onto each spot and none from off the page, along up to 8 with 6 from off the page
2. For that bud to be round the steps on its way must keep shapes, and for it to carry buds itself the throwing has
   to happen at every step, on pages that last. **measured** on along (pages last, sixteen small buds) against
   "along once" (one step, two small buds)
3. For the bodies to stay apart when c leaves the x-axis, a point above a meeting point must be pushed away at every
   height, and it is enough that the spine of the pages runs through the meeting point. **measured** on new try 1:
   the lump is gone for the rabbit, the Siegel disc and one more c
4. For c = -1 all of this falls into place by position, since every body and every meeting point sits on the x-axis
   and pages through the x-axis last for ever, which is the whole reason along is the best so far there; for the
   rabbit the middles of the bodies and the meeting point are not on one line, and no second plane can hold them.
   **reasoned** (a proof for flat pages only, not for curved ones)
5. Six new rules were tried from these findings and none beats along: five fail outright, and the one that moves the
   spine (new try 1) frees the rabbit's bodies but its pages last one step only, so its skin is ridges and thin
   loose arcs instead of buds. **measured**; **seen** in picture 5
6. What the orbits point at next, not tried: pages that come back after as many steps as the flat picture has spots
   to hop round (three for the rabbit) instead of after one step; and getting the number of pages out of the power
   instead of writing it into the rule is still open. **reasoned**

## Also asked: "the stretch step, if we're not doubling the magnitude"

In every rule here the length is multiplied by itself, not doubled: 0.8 becomes 0.64, and 2 becomes 4; a length under
1 gets shorter, a length over 1 gets longer. **measured** (length of the square = length times length, to rounding,
for one plane, along and the Lathe)

## May be told

- Every orbit that stays ends on the flat picture's own spots, under along, one plane, along once and the Lathe, for
  every c looked at. There is no second thing hiding off the flat page. (For the Siegel disc: the orbits sink onto
  the flat page and circle there.)
- Along: 8 buds round the middle body, 16 round the bodies beside it, and 16 small buds round the stalk of each big
  bud, 14 of which are in none of along's four pages. Some of the small ones are round, some thin.
- Buds are round beside the flat and upright pages and thin beside the slanted ones on the left half; the thin fins
  are thin buds.
- One plane: two buds per ring, never anything off the flat page, and it cannot have: it sends only two places onto
  each spot.
- The rabbit's lump is the same bodies pressed wall to wall, and the cause is seen above the meeting point (picture 4).
- "Along once": all eight big buds of the middle body; 6 instead of 16 on the side bodies; 2 small buds per bud
  instead of 16; two loose bodies on the rabbit; a Mandelbrot solid that is one plane's to a few parts in ten thousand.
- "Pulled plane": buds in four directions (flat and upright), and a rabbit that is nearly one plane's.
- New try 1 (spine through the meeting point): the same shape as along for c = -1; for the rabbit no lump, bodies
  touching at single points, but ridges instead of buds. It is not a candidate.
- No rule found so far does everything, and nothing here beats along.
- The length is squared, not doubled.

## May NOT be told

- "Above the rabbit's meeting point along has nothing, so the lump is not joined there" (stability section). Wrong:
  straight above the meeting point along's shape is there from height 0.03 to 0.11 and again from 0.33 to 0.60.
- "The four slanted buds of along's middle body are nearly bare" (stability section and its picture
  `keeps-shapes.png`). Wrong: the slanted bud carries sixteen small buds round its stalk like the others.
- "Only the one-plane rule keeps angles everywhere" (this round's briefing). It never turns anything inside out, but
  it keeps shapes only near the flat page (a third of space).
- "The walls between the lump's bodies have no thickness." Not shown; no gap was found down to about a thousandth.
- "Along once has exactly one plane's Mandelbrot solid" (last round). Nearly, not exactly.
- "Along once has bare side bodies" (last round). It has six buds on them.
- "New try 1 beats along" or "fixes the rabbit". It is along itself for c on the x-axis, it has no buds off it, its
  definition jumps at one place, it leaks on the Siegel disc, and it has no Mandelbrot solid.
- "It is proved that no rule can do it all." Not proved. Proved only: no second flat page can serve the rabbit, and
  a rule that sends just two places onto each spot has no buds off the flat page.
- "The number of pages can never come from the power." Reasoned for one family of rules only.
- "Every thin fin is a bud flattened at a fold." Measured for buds that live on a slanted page; for the rest it is a
  reading supported by six traced points.
- "San Marco behaves the same." Only counted (and I re-counted one ring); nobody looked at it.
- "A plane that goes four fifths of the way to c would give round buds on the Mandelbrot solid." Worked out, never
  built, and about thickness only.
- In the orchestrator's one-step picture (`out/r22/me/one-step-ring.png`): "inside the left-hand body". The ring lands
  in the small body at the far left, not in the left-hand body.
