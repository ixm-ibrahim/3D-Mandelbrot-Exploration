# Round 28, Track A ("dials"): the fixer's notes

Page: `dist/r28-fix.html` (md5 4b03c1dc...), built with the command in `out/r28/dials/BUILD.txt` under the name
`r28-fix`. The command is unchanged: no overlay file was added. Frozen page for comparison: `dist/r28-base.html`.
The page as the three checkers had it: `dist/r28-dials.html`; the overlay as I found it is kept in
`out/r28/fix/before/overlay/`, and `out/r28/fix/changes-by-the-fixer.diff` is every line I changed (158 put in, 24
taken out, in two files). Every number below comes from a script kept in `out/r28/fix/` and its log. "Seen" means I
opened the picture.

## In plain lines

1. Both majors are repaired. Everything else is repaired too, except four things that are not the page's to repair
   and three that I left alone on purpose (listed below with the reason).
2. E1, the fans and bumps in the 2D view with the second sphere at 50: gone. 11 views of the 2D picture, 0 pixels
   painted where nothing is (before: 142, 388, 152, 1434, 99 and 77 in six of them). The cause was in the distance
   the picture is drawn from, not in the drawing, so the 3D picture gained as well: the ribbed skin round the place
   where two buds kiss is smooth now (seen: `shots/pair-e1-3d-bud-kiss.png`).
3. What I added for it is one more "certainly free" room, the side spindle. It was put to lists of balls before it
   went into the page (63 settings, holds in 63) and afterwards the page's own distance was put to the lists again:
   never longer than the true distance at 320000 points round that place and at 240000 more in three whole
   settings. It is also no longer needlessly short there: "ten times the distance would still be free" at 87017 of
   320000 points before, at 0 after.
4. D1, Frame it in a low, wide picture: the whole chain is in the picture now in 844x390, 915x412 and 900x420 at
   every size tried (before: cut at the bottom at 300 and 400). In the windows that were right before, the camera
   stands where it stood.
5. The sentences under the note were gone through once (D2, D5, D6, D7, E3 and the 3D half of E1). The longest
   block is shorter than it was (404 characters where it was 504).
6. Every picture with two equal spheres is still the same to the pixel as on Version 20: 16 states, 0 pixels
   differ. Version 20's program text is the same to the byte. No console errors in any run.
7. One recipe, three voices, on the final page, three settings with a smaller second sphere: twin against the plain
   recipe 0 of 120000, shader against the plain recipe 0 of 122646.
8. The dial checker's own lists on the final page: 128 checks with real mouse and keys, 0 wrong; 3000 random moves,
   no rule broken.
9. Not repaired, and why: E2 (the pale patches are the shadow of a hull, measured; curing it means a new hull,
   which is a derivation of its own), E4 (the lab's shared lighting), D6 e (decision 6 fixes where the sentences
   stand), and the "follows" of the size dial (D4: the orchestrator's call, left exactly as the builder built it).
10. Three things I decided inside the brief and the orchestrator should look at: section "For the orchestrator".

## One line per defect

| id | verdict | what was done, or why not |
| --- | --- | --- |
| E1 (major) | **repaired** | New room "the side spindle" in the program for a smaller second sphere and in the twin: 2D ghosts 2441 -> 0; the 3D ribs gone; one status sentence for the swollen kiss at 50. Details below. |
| D1 (major) | **repaired** | The start view now also asks that each big ball is whole in the picture (`ballsSee`), for a smaller second sphere only: 4 cut pictures -> 0. Details below. |
| D2 | repaired | "The chain never ends" is shown where the two shown numbers multiply to 100 x 100 within their rounding (33.33 and 300), in 3D and in 2D (`ballsTouchShown`). |
| D3 | repaired | A number typed again into the second sphere's own box now counts as set by the user (size 150, 33.33 typed again, size 200: stays 33.33). And the hidden state is shown: while the second sphere follows the size, one short sentence says so. |
| D4 | **not repaired: a decision, not a defect** | The builder's "follows" is untouched. With it the two consequences the checker lists remain. The orchestrator's call; dropping it is still one edit (`ballsSetShare`), and the new sentence goes with it by itself. |
| D5 | repaired | The give-way goes by the size as the dial shows it: 100.004 reads 100, is 100, and with two equal spheres gives Version 20's touching picture and sentence. |
| D6 a | repaired | The second sphere's box reads "From 2 to 50, or 100"; its two step buttons add "From 50 one step goes to 100." / "From 100 one step goes to 50.", also after the dial kit repaints them. |
| D6 b | repaired | Where the Drawing radius is smaller than the neighbours themselves the page says "The Drawing radius in the View section cuts the two big neighbours open. Frame it makes room for them." in place of "its far ends are not drawn". |
| D6 c | repaired | The help under the size dial is one sentence again. |
| D6 d | repaired in part | The touching sentence for a smaller second sphere is two short sentences (35 words, was 51); the block of the checker's case is 404 characters (was 504). It is still four statements when four things are true. |
| D6 e | **not repaired** | Decision 6 says the sentences stand where `ballsTrouble` stands today. Moving them under the dials is a change to `body.html` and a decision. |
| D7 | repaired for a smaller second sphere | "Here the chain is too long for one picture, so Frame it shows a stretch of it.", in 3D and in 2D. With two equal spheres (size 99) the page says what Version 20 says: left so, because those sentences are Version 20's. |
| E2 | **not repaired, cause found** | Not a shadow of nothing and not of a ball: the shadow of the HULL ball on the bottom wall. Measured below. The cure is a tighter hull, which needs its own derivation and checks. |
| E3 | repaired | Depth 1 adds "With a single round most of the picture is one wall of colour." after the sentence of decision 6, which stays for every depth under 5. Depth 2 is broken shells (seen), so it keeps the sentence alone. |
| E4 | **not repaired** | The black crescents are the lab's own lighting in a deep gap (shadow and crevice shading both at their darkest), in the part of the program every picture shares. Decision 9: nothing else in the lab changes. |
| spindle as written in 1.3 | nothing to repair in the page | The brief's line, not the page's. The page uses the right spindle; the comment above `GL_BALLS_RHO` says so. |
| size dial follows beyond the bare formula | see D4 | The same thing seen by the truth checker. |
| flat-cut hair points | **not repaired: single precision** | 8 of the 9 are in Version 20's own program, which may not change. Re-measured on the final page for three settings with a smaller second sphere: 0 of 61206. |
| shader and twin apart at touching, Version 20 | **not repaired** | Version 20's own program and state (decision 7). |
| one stalled launch | **could not be reproduced** | More than 40 launches of the repaired page by my scripts (16 in `notch.py` alone), none stalled. |
| states by hand only | repaired | A radius between 0.5 and 1 written into the state is taken as the dial would take it (0.7 -> 50); the twin reads t from the page the way the picture does (1448 of 4096 verdicts differed, now 0); the size box shows the size that is drawn. |
| far balls and single precision | **not repaired: a limit** | The frame carries far points close to (0, 0, 1); the same limit as Version 20's far chain. |

## The overlay: what I changed

Two files of five. `00-core.js`, `40-render.js`, `46-mesh.js` are as the builder left them (compared byte for byte).

- `js/32-balls.js`: `ballsSide` and `ballsSideRoom` (the side spindle, for the twin) and the same in `GL_BALLS_RHO`
  with a long comment above it; `ballsSee` and its use in `ballsCam` (D1); `ballsTouchShown` (D2); `ballsTrouble`
  rewritten (the sentences); `ballsSetShare` and `ballsSetRho` take the numbers as the dials show them (D5);
  `ballsRho` takes a hand-written radius between 0.5 and 1 as the dial would; `ballsInside` and `ballsEstimate`
  read t from the page through `ballsT`. `GL_BALLS` and the comment above it: the same to the byte
  (`mk/frozen.py`, `logs/frozen.txt`).
- `js/80-ui.js`: the help of the size dial; the size box shows `ballsShare(ballsT(t))`; a typed-again number in the
  second sphere's box (D3); the words on that box and its step buttons (D6 a).

## E1: what was wrong, what was built, and the numbers

**Reproduced first** (`eyes/mk/flat2.py`, the checker's own script pointed at my folder; `logs/e1-before-run.txt`):
142, 388, 152, 1434, 0, 99, 77 ghost pixels in the seven views, the checker's numbers to the pixel.

**The cause.** At 50 the second sphere and its copy at the next whole number kiss, on the top wall. Just beside the
kiss, under the wall and outside both, the "certainly free" length was the distance to the second sphere, and that
falls off like the SQUARE of the distance from the kiss, while the nearest ball is as far off as the kiss itself.
The 2D view draws its outline wherever the distance is under a pixel, so it drew the outline where nothing is. The
fan of lines is that place carried round by the search. Near 50 (49.9) the same, less.

**The cure: the side spindle** (comment above `GL_BALLS_RHO`). It is the argument of the spindle once more, lying
on its side. The two inversions (about the second sphere's centre and about its copy's) hold two points of the line
through both centres fixed; every circle through both crosses both spheres squarely; so the spindle swept by such
an arc is carried onto itself, and so is the top wall. If its piece outside both spheres holds no ball, none of it
does. That piece holds none when the spindle reaches no further from the line than
w = min(top - HB, D - rho), D = 1 for the square grid and for a line only, sqrt(3) / 2 for the honeycomb grid:
then it stays above everything that grows on the bottom wall and clear of every other copy of the second sphere.
REASONED, and then MEASURED:

- On lists of balls, before it was built in (`mk/side.py`, `logs/side.txt`, no browser; the truth checker's
  `tkit.py`): 21 settings on each of the three grids (second sphere 50, 49.9, 49.5, 49, 45, 40, 33.33, 25, 20,
  12.5, 5, 2 % of the first; sizes from 20 to touching): no listed ball reaches into the spindle and the recipe
  calls none of 40000 random points of it INSIDE, in 63 of 63. That the test can fail (`mk/side_wider.py`,
  `logs/side-wider.txt`): a spindle twice as wide holds 26594 listed balls on the honeycomb grid (150 / 50) and
  15442 (250 / 40). w is safe but not the largest that would do: on the square grid and for a line only even
  twice the width holds in my trials, and 3 % wider holds everywhere.
- The page's own distance round that place, against the lists (`mk/notch.py`, the truth checker's test `over`;
  `logs/notch-before.txt`, `logs/notch-final.txt` on the final page, `logs/notch-after1.txt` on the page with the
  side spindle alone: the same numbers): 16 settings, 20000 outside points each.
  Longer than the true distance: 0 of 320000 before, **0 of 320000 after**.
  Twice the distance would still be free: at 118821 points before, at 3348 after. Ten times: 87017 before, 0 after.
- The truth checker's whole test on the final page, three settings (`truth/mk/bc_page.py D J M`,
  `truth/logs/bc_summary.txt`): estimate longer than the true distance 0 of 240000 (box, mid, top, edge); the
  shader's own number beyond what single precision explains: 0 of 58685; shader against twin within 1 % at every
  point (worst 0.95 %, where the spheres touch).

**The 2D picture** (`logs/e1-after-run.txt`, final shader; pictures `eyes/shots/after-*.png`, pairs in `shots/`):

    view (size / second sphere)       ghosts before   after     short distance with nothing near: before   after
    150 / 50 start                         142           0                                         690       16
    200 / 50 start                         388           0                                        5412     1450
    150 / 50 close, depth 16               152           0                                        9093        9
    150 / 50 close, depth 100             1434           0                                       14894       29
    60 / 50 close                           99           0                                         524       21
    100 / 50 start                          77           0                                         268       52
    150 / 49 close                           0           0                                          14        3
    also after: 100 / 50 honeycomb, 199.9 / 50 close, 300 / 25, 150 / 33.33: 0 ghosts, 0 holes in each.
    Twin against the checker's recipe at every pixel centre: 0 of 604262 in all 11.

Seen: `shots/pair-e1-2d-bud-kiss.png` (the fan is gone, the two round lobes stay: they are what 16 rounds leave
undecided, and at depth 100 they are two small bumps, `shots/pair-e1-2d-bud-kiss-depth100.png`);
`shots/pair-e1-2d-size200.png` (the band with round holes, its edges clean).

**The 3D picture.** The checker asked for a sentence; the picture changed as well. Before, the skin round the bud
kiss was covered with dark ribs (the same too-short distance, read by the slope and the shadow). After: smooth skin
and the two lobes (seen, `shots/pair-e1-3d-bud-kiss.png`). Rays, the checker's method (`eyes/mk/rays.py` and
`walk.py`, 13 views with the size past 100, 38016 rays each; `eyes/logs/walk-after.txt`): HOLES 0 in 13, IN THE OPEN
0 in 13. SEEN THROUGH: 10, 2 and 6 rays in the three views where balls kiss (before: 1, 2, 6), none of them through
a ball: thin threads that only the depth calls solid. In the bud-kiss view that is 9 more than before; the rays
step further there now, and a thread thinner than a step can be passed. The sentence: "With the second sphere at 50
the buds on a neighbour kiss, and where the depth of the search runs out those places come out swollen." It is
shown at 50 whenever the touching sentence is not (which says the same).

## D1: Frame it in a low, wide picture

**Reproduced first** (`ui/mk/sizes2.py`, real mouse and keys; `ui/logs/sizes2-before.txt`): cut at the bottom and
right at 300 and 400 in 844x390, at the bottom in 915x412, the checker's pixels.

**The cause** as the checker reasoned it: the rule of thumb measured the picture's height against a ball in the
middle of the picture; a big neighbour stands beside the middle and nearer to the eye.

**The cure.** `ballsSee(c, r, ...)`: from how far a ball is wholly inside the eye's four side planes, exact, with 8 %
of air. Asked for the middle ball with its buds, the two neighbours, and the ball that holds the rest of the chain
at either end. The camera takes the larger of that and the old rule, so no view comes nearer than it was. Only for a
smaller second sphere: with two equal spheres the start view is Version 20's own expression (decision 7).

**After** (`ui/logs/sizes2.txt`, pictures `ui/shots/sizes2-*.png`, the old ones in `ui/shots/before/`): 35 of 35
pictures of the new page whole (7 windows, sizes 55.56, 101, 150, 300, 400), 0 pixels of the object on any edge.
The four pictures still marked cut in that log are the frozen page's own (the endless chain at 100, and its 14
pixels at size 90). 900x420 (`ui/mk/sizes.py`, `ui/logs/sizes.txt`): 55.56, 150, 400, 2000 whole in 3D and 2D, and
so are 1920x1080, 1024x768, 820x1180, 360x640. Seen: `shots/pair-d1-844x390-size400.png`, `-size300.png`.
In the wide window the camera did not move: the start view at 150 / 50 stops 5839 of 38016 rays, the checker
counted 5838.

## The sentences as they are now

All in `ballsTrouble`. With two equal spheres every sentence is Version 20's, word for word (plus the depth
sentence of decision 6). Before and after, by the checkers' own steps with real input: `logs/small-before.txt`,
`logs/small-after.txt`, `logs/small-final.txt` (script `mk/small.py`).

- Touching (also within rounding), smaller second sphere: "At 200 the chain never ends, so the picture shows a
  stretch of it. Where the depth of the search runs out, the far balls and the places where two balls kiss come out
  swollen." (2D: circles.)
- Too long to frame, not touching: "Here the chain is too long for one picture, so Frame it shows a stretch of it."
- The Drawing radius cuts the neighbours: "The Drawing radius in the View section cuts the two big neighbours open.
  Frame it makes room for them."
- Past 100: the sentence of decision 6, unchanged; while the second sphere follows the size it is followed by "It
  follows the size until you set it yourself."
- At 50, not touching: the kiss sentence above.
- Depth under 5: the sentence of decision 6; at depth 1 followed by "With a single round most of the picture is
  one wall of colour."

## E2: whose shadow the pale patches are (measured, not repaired)

`eyes/mk/skin.py` again on the final page (`eyes/logs/skin.txt`): unchanged, 98.7 against 101.7, gone with shadows
off. So the side spindle did not touch it. Then I walked the light's own ray from 8 pixels, in and beside the patch,
the way the shadow march does, reading both numbers of the page's distance (`mk/skinray.py`, `logs/skinray.txt`),
and asked the truth checker's list how far the nearest ball really is at the darkest stop (`mk/skintrue.py`,
`logs/skintrue.txt`, 3.9 million balls). In the patch:

    the page reads 0.064 ("free", the hull); "best" alone would read 0.137; the nearest ball is really 0.100 away.
    The shadow darkens under 1.00 of (10 x distance / length of the ray): the page 0.66, the truth 1.03.

So with the true distance there would be no shadow there, by a hair; the page's is the shadow of the ball of
diameter HB that stands for "the first bud on the bottom wall and everything that grows on it". Near its top that
ball holds only a thin chain of small balls, and the light's ray passes 0.06 above it. A hull of two balls (the
first bud, and the next link of the chain on top of it) would lift the page's 0.66 to about 0.8, by my arithmetic,
not to 1. Making the patches go needs a hull that follows the chain further, with its own derivation and its own
run against the lists. I did not start that inside a repair round for a patch 3 parts in 255 darker than the skin.

## For the orchestrator

1. **One more sentence than decision 6 lists** (the kiss at 50), one more for "too long", one for "the Drawing
   radius cuts the neighbours", and two short add-ons ("It follows the size ...", "With a single round ..."). Each
   answers a defect; the sentences of decision 6 themselves stand word for word. If fewer are wanted, each is one
   `out.push` in `ballsTrouble`.
2. **"Within rounding" is my reading**: the two dials show two decimals, and the sentence appears where
   10000 - size x second sphere <= 0.005 x (size + second sphere). 33.33 and 300 touch by it, 50 and 199.9 do not
   (they get "too long"). The dial checker's `fuzz.js` asks for the sentence at exact touching only; it did not
   meet such a state in its 3000 moves, but with other moves it would call this "shown without touching".
3. **A size typed with more than two decimals** is now taken as shown when the second sphere is smaller (the state
   holds the shown number), and as it came with two equal spheres (so Version 20's states do not change by a hair).
4. D4, the "follows". Untouched. If it stays, the new sentence makes it visible. If it goes, drop
   `|| (BALLS_DIAL.follows && rho < 1)` in `ballsSetShare`; the sentence then never shows.
5. The dial checker's remark on the plainness of "second sphere": not a defect of the build, not touched.

## Final checks on dist/r28-fix.html

| what | script | log | result |
| --- | --- | --- | --- |
| old pictures against the frozen page | `eyes/mk/same.py 1400x950 dark` | `eyes/logs/same-1400x950-dark.txt` | 16 states (10 of Balls on balls with two equal spheres, the default among them; 6 others): **0 pixels differ**. The Learn tab, whole window: 0. |
| Version 20's program text | `mk/frozen.py` | `logs/frozen.txt` | the same to the byte |
| twin against the plain recipe, smaller second sphere | `truth/mk/bc_page.py D J M` | `truth/logs/bc_D.txt`, `bc_J.txt`, `bc_M.txt` | 150 / 33.33 square, 150 / 50 honeycomb, 200 / 50 square (touching): 0 of 40000 each; the twin with nothing passed says the same |
| shader against the plain recipe | the same | the same | flat cut 0 of 20402, in space 0 of 20480, in each of the three |
| console | every run above and below | | no console errors, no warnings |
| the dials, real mouse and keys | `ui/mk/f1.py wide dark` | `ui/logs/f1-wide-dark.txt` | 128 OK, 0 wrong |
| 3000 random moves of the dials | `ui/mk/fuzz.js` | `ui/logs/fuzz.json` | no rule broken; the same counts as on the builder's page (the second sphere moved 630 times with the size, 278 of them without having to: the "follows") |
| the panel still fits | `ui/mk/words.py phone dark`, `wide dark` | `ui/logs/words-phone-dark.txt`, `words-wide-dark.txt` | 5 states each, 0 wrong: nothing sticks out, nothing is cut off, nothing overlaps. The checker's longest block (second sphere 50, size 200, depth 3) is 142 px high on the phone (it was 182). |

The whole window differs from the frozen page by 11 to 28 pixels in four states, in one row: the handle of the
zoom slider, where the frozen page differs from itself between two runs (the eyes checker measured that).

## Not done, and limits

- Phone (390x800) and the light theme: only the panel test was run again (phone, dark). The repairs are in the
  distance, the camera's distance and the words, none of which knows the theme; the camera rule was run in 12
  window sizes.
- The longest block of sentences that can now arise was not looked at on the phone: Drawing radius cut, chain too
  long, past 100, kiss at 50 and depth 1 at once, about 600 characters. It is one flowing paragraph like the
  others.
- The old smoke list and the round 26 / 27 scripts were not run again. They never set a smaller second sphere,
  and with two equal spheres the program, the uniform, the start view and the sentences are Version 20's.
- The side spindle was not measured for speed by itself. The 13 ray views drew in 0.3 to 0.9 s each (the page's own
  status line, on a machine other agents were using).
- 9 more rays "seen through" a depth-only thread in the bud-kiss view (see E1). If that matters, the cure is in
  the march, not in the distance.
- Lists of balls go down to radius 0.0003 (0.00001 for a line only), finer near the second sphere; a room too long
  only into smaller balls would escape. The argument does not depend on size.
- I ran one browser script at a time. Other agents were on the machine, so no timing here is exact.

## Files (all under out/r28/fix/)

- `mk/adopt.py`: copies the three checkers' scripts to `eyes/mk`, `ui/mk`, `truth/mk`, pointed at my folder and
  page (nothing else in them is changed). `FIX_PAGE=dist/r28-dials.html` runs any of them on the page as it was.
- `mk/side.py`, `mk/notch.py` (the side spindle), `mk/small.py` (the small defects, real input), `mk/skinray.py`,
  `mk/skintrue.py` (E2), `mk/frozen.py`, `mk/pairs.py`.
- `logs/`, `eyes/logs/`, `ui/logs/`, `truth/logs/`; pictures in `shots/`, `eyes/shots/`, `ui/shots/`.
- `before/overlay/`: the overlay as I found it. `before/r28-fix-step1-e1.html`: the page with the side spindle
  alone (what `notch-after1` and `e1-after1` ran on; the shader did not change after it).
