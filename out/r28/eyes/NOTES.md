# Round 28, Track A, the eyes: holes and shells past 100, old pictures, speed (section 1.4 c second half, d, g)

## In plain lines

- The 3D picture is whole past 100. 32 views with the neighbours larger than the middle ball (101 to 2000, all
  three grids, start views, close views, along the chain), four of them again in light and on the phone,
  1.42 million rays walked with my own writing of the recipe: no ray goes through a ball without stopping, no ray is stopped behind a ball,
  no ray stops in the open. 42 more views drawn at random: the same.
- ONE THING IS WRONG, in the 2D view only, and only when the second sphere stands at exactly 50: where two buds on
  a neighbour kiss, the 2D picture paints a bump or a fan that is not there. At 49 it is gone. It is not in
  Version 20's own touching picture (size 100). The second-sphere dial lands on 50 for anything dragged between 50
  and 75, so a hand gets there easily.
- One faint thing in 3D: on the bare skin of a large neighbour (300 to 400, second sphere 25) there are a few pale
  lozenge-shaped shadows of nothing. They are 3 parts in 255 darker than the skin and go away with shadows off.
- Old pictures: 16 states (10 of Balls on balls with the second sphere at 100, 6 others) on the new page and on the
  frozen page, wide dark and phone light: 0 pixels differ in every one. The Learn tab: the whole window, 0 pixels.
- Speed: the first picture at the default takes 0.96 to 1.02 times what the frozen page takes (five runs each, in
  turn). 150 and 300 finish in about 0.3 to 0.4 s; the very first step past 100 takes about 1.1 s if it comes
  right after the first picture, 0.3 s if it comes five seconds later.
- No console errors in any run.
- A slip of my own, found and mended: my first runs pressed the box round "Reset this section" and not the
  button, so some views began from the dials of the view before. Every result below names the numbers the page
  really held; the views the slip spoiled were run again.

Pages: `dist/r28-eyes.html` (my build, byte for byte the builder's `dist/r28-dials.html`: same md5) and
`dist/r28-base-eyes.html` (my build of `base20a`, byte for byte `dist/r28-base.html`). Everything is in
`out/r28/eyes/`: scripts in `mk/`, logs in `logs/`, pictures in `shots/`, enlargements in `crops/` and `marks/`.
Every count below is in `logs/summary.txt` (written by `mk/sumup.py` from what the other scripts kept).
"Seen" means I opened the picture.

## 1. What is wrong

### E1 (major: a wrong 2D picture). Second sphere at exactly 50: bumps and fans where two buds on a neighbour kiss

Steps: Balls on balls, type 150 into Size of the neighbours, type 50 into Second sphere, tick 2D view, Frame it.
(Or: `python out/r28/eyes/mk/flat2.py dw 1400x950 dark p150-r50-2d`.)

- Seen (`shots/dw-p150-r50-2d.png`, enlarged in `marks/dw-p150-r50-2d-bump.png`): each of the two large circles
  carries a small double bump at four places, at picture points (+-1.54, +-0.80) and (+-1.57, +-0.80). At 200 with
  50 (`shots/dw-p200-r50-2d.png`, `marks/flat2-dw-p200-r50-2d-zoom.png`) eight fans about 30 pixels wide stand on
  the two edges of the band. In the close view (`shots/dw-p150-r50-2d-budkiss.png`) two round lobes with a fan of
  thin pink lines above them; with depth 100 (`...-budkiss-d100.png`) the lobes are gone and a filled fan stands
  there instead.
- Measured (`logs/flat2-dw.txt`; "ghost" = a pixel painted in the inside colour with nothing solid within about
  1.5 pixels, by my recipe at the page's own depth on a grid of quarter pixels):

      second sphere exactly 50, 9 views: 2441 ghost pixels      any other second sphere, 10 views: 0
      150 / 50 start view 142   200 / 50 start view 388   199.9 / 50 close 72   100 / 50 start 77
      60 / 50 close 99 (so also below 100)   150 / 50 close 152   150 / 50 close, depth 100: 1434
      150 / 49 close 0   150 / 48, 150 / 40, 150 / 33.33, 101 / 49.5, 300 / 25, 400 / 25, 1000 / 5: 0
      second sphere 100 (Version 20's object) at 55.56 and at 100 with depth 400: 0

  At every ghost pixel the page's own twin `ballsInside` says OUTSIDE, and the page's `ballsEstimate` there is
  under 0.4 of a pixel, while the nearest solid point is really 2 to 3 pixels away in the middle and up to 8.5
  (depth 16), and 9.5 in the middle and up to 26.5 at depth 100. So this is not the recipe's picture: the distance the 2D view is drawn from is far too
  short in the notch between two copies of the second sphere, which touch each other exactly when it is 50.
- Phone and light theme: the same places (`shots/dp-*-2d.png`, `lp-*`, `lw-*`; ghosts 147, 12 and 51 by the same
  count, which is strict about colour and so finds fewer on the light theme, where the fans are plainly seen as
  dark fans).
- Version 20's own touching picture (size 100, second sphere 100, 2D: `same/old-1400x950-dark-balls-100-2d.png`,
  seen) has no such fans. So this is new.
- How a hand gets to exactly 50: the second-sphere dial put anywhere between 50 and 75; or the size dragged past
  100 and back under 100 (the builder's known gap 1: it then stays at 50).
- In 3D the same place is not wrong by the page's own rule, but it shows: in the close view
  (`shots/dw-p150-r50-budkiss.png`, `crops/dw-p150-r50-budkiss-lobes.png`, seen) two swollen lobes with a black
  slit between them. 2213 of 37961 rays stop on what only the depth of the search calls solid; with depth 100 it
  is 49, and with the second sphere at 49 it is 0 (`shots/dw-p150-r49-budkiss.png`: smooth skin). No sentence
  speaks of this unless the size is also at the touching value (150 with 50 shows only "Past 100 the second
  sphere has to be smaller ...").
- The builder's known gap 6 ("with the second sphere at exactly 50 the buds on a neighbour touch ... all three
  voices agree, so it is the recipe's picture") holds for the 3D picture and for where the twin says inside. It
  does not hold for the 2D fans.

### E2 (minor). Pale lozenge-shaped shadows of nothing on the bare skin of a large neighbour

Steps: `python out/r28/eyes/mk/rays.py dw 1400x950 dark p300-r25-neighbour` (size 300, second sphere 25, eye 0.8
from the bud at the whole number (1, 1) of the right neighbour), picture `shots/dw-p300-r25-neighbour.png`, lower
middle, box (355, 598) to (445, 678); the same at 390 and at 400 (touching), depth 16 and 100
(`crops/dw-p3*-low.png`, `crops/dw-p400-r25-neighbour-low*.png`, contrast raised 2.5 times so that they show).

- Seen: three lozenges side by side at 300; scale-like marks at 390 and 400. At the page's own contrast they are
  just visible once one knows where to look.
- Measured (`mk/skin.py`, `logs/skin.txt`): the patch is 98.7 against 101.7 of 255 round it, darkest tenth 95.3,
  largest step between neighbouring pixels 8 (smooth skin: 2). With shadows off the patch is gone (101.3 against
  101.7, largest step 2, no step of 4 or more against 329). With the crevice shading off it stays. So it is the
  shadow: a shadow ray is slowed where the certain-room length is short although no ball is near.
- The rays themselves are right there: 38016 of 38016 stop, none in the open, none further than 1.1 pixels from a
  ball by the page's own measure.

### E3 (minor, wording). Depth 1 is not "broken shells" but one slab over most of the picture

Steps: type 1 into Depth of the search at the default size (`shots/dw-depth1.png`), or at 150
(`shots/dw-p150-depth1.png`).

- Seen: a flat violet wall with a saw-tooth edge covers the left three quarters of the picture; the balls show
  only at its right edge. At depth 3 (`dw-depth3.png`, `dw-p150-depth3.png`): whole balls with one end of the
  chain in shards and blobs. At depth 5 (`dw-depth5.png`, `dw-p150-depth5.png`): whole balls, clean.
- Measured: depth 1: 32762 and 30651 of 38016 rays stop, 583 and 501 rays run through 2 pixels or more of what
  only the depth calls solid without stopping (longest 319 px); depth 3: 71 and 7; depth 5, 100, 400: 0.
  None of these runs through a ball.
- The sentence is shown ("With so few rounds of the search whole balls are still undecided, and they come out as
  broken shells."), as decision 6 asks. I list it because at depth 1 and 2 the user loses the whole picture, which
  the sentence does not say. For the orchestrator to weigh; the decision itself I do not reopen.

### E4 (minor, old lighting in a new place). Black crescents beside the middle ball at 1000 and 2000

Steps: type 1000 into Size of the neighbours, Frame it (`shots/dw-p1000-start.png`,
`crops/dw-p1000-start-middle.png`).

- Seen: between the two huge neighbours, round the small middle ball, crescents of pure black. On the dark theme
  they read as holes (the background is 8, 13, 18; the crescents are 0, 0, 0). On the light theme
  (`crops/sheet-lw.png`) they read as a deep shadow.
- They are not holes: every ray there stops 2 to 3 pixels before a ball (`mk/spot.py dw p1000-start 404 316 420
  332`), and over the whole view 0 rays go through a ball. It is the lab's own shadow in a deep gap; the same
  black slit stands beside a bud at size 2 with the second sphere at 100 (`shots/dw-p2-close.png`), which is
  Version 20's own program.

## 2. What I checked and found clean

### 2.1 Holes, missing balls, shells, noise in 3D (section 1.4 c)

Method (`mk/rays.py`, `mk/walk.py`, after `out/r27/final/mk/holes.py`): the dials are set by typing (Reset this
section, size, second sphere, grid, depth, Frame it, then the camera for a close view), the picture is drawn and
saved, and `pick()` is asked at every 4th pixel of every 4th row (38016 rays wide, 6408 on the phone). Every one
of those rays, not a sample of them, is then walked in half-pixel steps with my own numpy writing of the recipe
of section 1.1 (`mk/recipe.py`; nothing in it comes from the builder's code; self-check in
`logs/recipe-selfcheck.txt`). The page's twin agrees with my recipe at 0 of 13.1 million pixel centres (2D views).

- HOLE: the page stops nowhere on a ray that runs through solid for 2 pixels or more.
- SEEN THROUGH: the page stops more than 2 pixels behind such a stretch.
- IN THE OPEN: a stop with nothing solid at the stop, at 78 probes within 2.5 px, at 3000 within 3 px and at
  400000 more within 1.5 px.
- Each hole and each seen-through ray is split: through a BALL (a point of the stretch reaches a wall in 300
  rounds) or only through what the page's depth leaves undecided (which the page counts as inside).
- The saved picture against pick(): a pixel with pick() stopping all round it that is painted as the background
  (to within 1 of its colour), and the other way round.

Results (`logs/summary.txt`, long lines in `logs/walk-dw.txt` and so on):

    dark, wide, size past 100:   32 views, 1216512 rays, 768445 stops: HOLES 0, SEEN THROUGH 9 (a ball: 0), IN THE OPEN 0
    light wide / dark phone / light phone, 4 views each: 203328 rays: HOLES 0, SEEN THROUGH 0, IN THE OPEN 0
    size 2, depth 5, 100, 400:    7 views,  266112 rays: HOLES 0, SEEN THROUGH 0, IN THE OPEN 0
    picture against pick(), every view: 0 patches either way
    42 views drawn at random (mk/fuzz.py, 1500 rays each, 13 eyes closer than 0.2 to the object, 9 touching
    settings): HOLES 0, SEEN THROUGH 0, IN THE OPEN 0

The 9 seen-through rays (199.9 / 50 kiss 6, 200 / 50 near kiss 2, 150 / 50 bud kiss 1) pass a stretch of which
no point reaches a wall in 300 rounds: the swelling at a kiss where the depth runs out, not a ball (the first 8
one by one in `logs/thru-dw.txt`: threads 3.5 to 9.5 pixels thick). The stops "further than 2 px from the
nearest ball the search meets" by the page's own measure (up to 2221 a view in the close views where balls
kiss, worst 86.6 px) go with the stops on such depth-only solid (2213 in that view); at 200 / 50 with depth 400
they are 19 (close) and 3 (start).

The views, with the numbers the page held, and what I saw (dark, wide; contact sheets `crops/sheet-3d-a..d.png`):

- 101 / 50 start: middle ball thick with buds between two neighbours of its own size, a small ball at each end.
  Whole.
- 150 / 50 start (also light wide, dark phone, light phone): small middle ball, two larger neighbours, chains
  tapering to both ends. Whole, no shells.
- 199.9 / 50 start and 200 / 50 start: a bar of large balls and clusters of small ones with round holes, running
  out of the picture left and right. At 200 the page says so; at 199.9 it says the chain runs past the Drawing
  radius. Thin bridges over the round holes are what the depth leaves undecided (`mk/tube.py`).
- 300 / 25 start (4 layouts): two smooth large balls, small middle ball with buds, a ball and a bud at each end.
- 400 / 25 honeycomb start (touching): large balls with small clusters between, out of the picture on both sides.
- 300 / 12.5 honeycomb start, 400 / 12.5 line-only start: two large balls, middle ball between; with a line only
  the buds sit in one ring. Whole.
- 1000 start (4 layouts), 2000 start, 2000 / 2 start: two huge smooth balls, a tiny middle cluster, end balls.
  See E4 for the black crescents.
- 150 / 33.33 line-only start; 150 / 33.33 along the chain; 300 / 16.67 honeycomb along the chain: whole balls,
  buds with their shadows, nothing broken. (Along the chain the near neighbour fills the picture.)
- 150 / 50 honeycomb, close view of a neighbour (4 layouts): six-fold clusters of buds on smooth skin. Clean.
- 200 / 50 honeycomb close view; 199.9 / 50 kiss; 200 / 50 line-only kiss; 200 / 50 near kiss (eye 0.006 from the
  object): crowded but whole; dark specks are shadow, not background (`mk/bgexact.py`: 0 patches of background
  colour inside the stops).
- 400 / 25 close view of a neighbour, 390 / 25, 400 / 25 depth 100, 300 / 25: bare skin, one bud cluster with a
  long shadow. See E2.
- 400 / 12.5 far end; 300 / 25 grazing the skin; 1000 middle: whole balls; the grazing view shows a smooth
  horizon, no bands.
- Size 2 start, size 2 with second sphere 2, size 2 close: one ball with tiny dimples and one bud. The second
  sphere at 2 gives the same picture as at 100 here (the stops are the same 6177).
- Depth 100 and 400 at the default: the same picture as depth 16 to the eye; 150 / 50 depth 100 and 200 / 50
  depth 400 (start and kiss): whole, crisper at the kisses.

### 2.2 The 2D view (section 1.4 c)

19 views dark wide, 2 each in the three other layouts (`mk/flat2.py`): the page's twin and its estimate are read
at every pixel, my recipe on a grid of quarter pixels. Holes (a pixel wholly solid with its 8 neighbours and not
painted inside): 0 in every view. Ghosts: 0 in every view whose second sphere is not exactly 50 (E1). Seen
(`crops/sheet-2d-a.png`, `sheet-2d-b.png`): chains of clean circles with small circles on them; 1000 with a line
only: two large circles, a small one between, one at each end.

### 2.3 Old pictures (section 1.4 d)

`mk/same.py`, the same steps on both pages, typed like a hand, the picture alone compared (controls hidden):

    wide dark (1400x950) and phone light (390x800), 16 states each: 0 pixels differ in every state
    Balls on balls, second sphere 100: as the row gives it; 100 square; 100 honeycomb close at the kiss; 70 line
      only depth 40; 10 depth 5 in 2D; 100 in 2D; 35 honeycomb from the other side; 25 depth 200;
      the default after a trip past 100 (300 typed, then Reset this section);
      50 reached as 150, second sphere 50, second sphere back to 100 (against a typed 50 on the frozen page)
    not Balls on balls: Mandelbrot as the page opens; Mandelbrot, another approach (quat4), power 4; Julia,
      turnalong, with a cut; Julia, pulledplane, 2D; first Kleinian group as it opens; its preset 5 in 2D
    the Learn tab, whole window: 0 pixels differ (both layouts)

The whole window, wide: 28 pixels differ in two of the 2D states, in one row, the handle of the zoom slider. The
frozen page differs from ITSELF there by 12 to 28 pixels between two runs (`mk/same_twice.py`,
`logs/same-twice.txt`), so that is the page's own play. The whole window on the phone differs in three states
that follow Balls on balls: the same content, scrolled by 61 px (0 pixels differ in the rows both show) and by
about 700 px (`logs/same-phone-shift.txt`, `same/pair-phone-*.png` seen). The Balls on balls section is one dial
taller, so the page stands elsewhere after it; the pictures are the same to the pixel. Not counted as a defect.
The status line of the Learn tab read "862 x 511" on one page and "862 x 701" on the other in `same.py`; asked
again three times each (`mk/learn.py`), both pages give the same numbers. It was the moment of reading.

### 2.4 Speed (section 1.4 g)

`mk/speed.py first 5`: a fresh browser each time, 3 s after the page is up one click on the row Balls on balls;
new, old, old, new, ... (`logs/speed-first-1400x950.txt`).

    background preparing as a user has it: new 1273 ms (1315, 1259, 1273, 1084, 1684), old 1324 ms (1172, 1324,
      1546, 1324, 1262): 0.96 times (medians), 1.00 times (means)
    background preparing off:              new 1140 ms, old 1113 ms: 1.02 times (medians), 0.97 times (means)

`mk/speed.py past 3` (`logs/speed-past-1400x950.txt`, quiet machine; `logs/speed-past-run.txt` is an earlier
run while my own walks loaded the machine):

    150 typed as soon as the first picture is done: 1.05 to 1.10 s (the other program is built at that moment)
    150 typed 5 s later: 0.28 to 0.32 s      300 typed: 0.32 to 0.43 s
    Frame it at 300: 0.12 to 0.17 s          150 typed again: 0.12 s (the clock's floor)

Under load the same steps took up to 1.3 s and 0.77 s. Drawing times of the views in section 2.1 were 0.25 to
3.6 s (the longest: 400 / 25 close view, touching, while my walks ran).

## 3. Not done, and limits

- Rays stand 4 pixels apart; a fault smaller than that between them would be missed in 3D. The 2D check is at
  every pixel.
- pick() marches with 300 steps where the picture uses 260; the picture itself was held against pick() and showed
  no patch either way, but that test cannot see a single wrong pixel in a busy place.
- "In the open" trusts probes; the 11 stops that passed 3000 probes all stood 0.5 to 0.9 px from a ball
  (`logs/openprobe-dw.txt`).
- Light and phone were run for four 3D views and two 2D views, and old pictures for wide dark and phone light.
- I did not test the dials themselves (section 1.4 f), the lists of balls (a, b) or the old lists (e).
- The first try at the speed test stalled for 20 minutes because one of my own scripts starved the machine
  (`logs/speed-first-stalled.txt`); I stopped my own run and its own browser and ran it again.
- `logs/reset-slip-first-runs.txt` lists what each early view really showed. Five 2D views of the first batch
  held another second sphere than their names say; `mk/flat2.py` ran them again with the right press, and the
  2D numbers above are from that second run.

## 4. Files

- `mk/eyerun.py` (helper), `mk/recipe.py` (my recipe), `mk/views.py` (the views, each eye checked: `logs/cams.txt`)
- `mk/rays.py` + `mk/walk.py` (3D), `mk/flat2.py` (2D), `mk/fuzz.py` (random views), `mk/brief.py`, `mk/sumup.py`
- second looks: `mk/spot.py`, `mk/tube.py`, `mk/thru.py`, `mk/openprobe.py`, `mk/bgexact.py`, `mk/picdiff.py`,
  `mk/ghosts2d.py`, `mk/skin.py`, `mk/slip.py`
- `mk/same.py`, `mk/same_twice.py`, `mk/learn.py` (old pictures), `mk/speed.py` (speed)
- `mk/queue1.sh` to `queue5.sh`: the order the browser scripts ran in, one at a time
- `logs/summary.txt`: every count quoted here
