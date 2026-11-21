# Round 28, Track A, the dial checker ("ui"): sections 1.4 e and f

Page checked: `dist/r28-ui.html`, built by me with the command of `out/r28/dials/BUILD.txt` under my own name. It is
byte for byte the builder's `dist/r28-dials.html` (same md5, 5534020c...). Frozen page: `dist/r28-base-ui.html`
(`build.py --name r28-base-ui --base base20a`; same md5 as the builder's `r28-base.html`).
Every number below comes from a script in `out/r28/ui/mk/` whose log is in `out/r28/ui/logs/` (or `r26/`, `r27-new/`,
`r27-old/`). "Seen" means I opened the picture. I did not change the overlay. Nothing was written under `src/`,
`base*/`, `tools/` or any `out/r20..r27` folder (checked by file dates at the end: 0 files newer than my start).

## In plain lines

1. **The old lists pass on the new page as on Version 20.** Smoke list: 90 steps, 90 results, no console errors;
   87 of the 90 result lines are word for word those of the frozen page, two differ by a moving camera's timing and
   one counts the dials (79, was 78: the one new dial). Round 26's three lists and round 27's five scripts give the
   numbers that were kept for Version 20, to the digit. 0 holes in 11 views. 6 old states: 0 pixels differ.
2. **The dials do what section 1.2 says, driven with a real mouse, real keys and a finger**: both ends of every
   slider, typed 0, 1, 2000, 5000, -5, text and an emptied box, the two give-way rules both ways, the jump between
   50 and 100 (typed, dragged, arrow keys, step buttons), back below 100, Reset this section, Reset everything, the
   row in the Approach list, leaving and coming back four ways, the 2D view, a saved picture, the sentence of a
   saved 3D model, a reload. Wide window: 128 checks, 0 wrong. Phone: 87 checks, 0 wrong. No console error anywhere.
3. **3000 random moves of the three dials: no rule of 1.2 broken once** (the state is always an allowed one, the
   boxes always show it, the dial that was moved always gets its value, the sentences always fit the state).
4. **One thing I mark major, and it is outside the two windows the brief names**: on a phone held sideways (a
   picture more than about 2.3 times as wide as high) "Frame it" at sizes 300 and 400 leaves the nearer big
   neighbour cut off at the lower edge of the picture. At 1400x950 and 390x800, and in five laptop-sized windows,
   the whole chain is in the picture at every size I tried (55.56 to 2000), in 3D and in the 2D view.
5. **Seven small things** (words, and corners of the give-way rules), listed under "Defects". The largest of them
   is a matter of reading 1.2 point 4, which the builder declared himself: the second sphere FOLLOWS the size.
6. **The panel fits**: wide and phone, dark and light, in five states (among them four status sentences at once and
   the longest numbers): nothing sticks out, nothing is cut off, nothing lies over anything. Measured and seen.
7. **Old pictures stay**: after a visit past 100 and "Reset this section" the start picture is the same to the pixel
   as before the visit and as the frozen page's (0 of 604262 pixels). A picture saved at 150 while the section is
   reset under it is the picture of 150, to the pixel.
8. Three things the eye should know, none of them a fault: the picture jumps at 100; after a drag past 100 the
   neighbours fill the picture until Frame it is pressed; coming back below 100 the old look does not come back
   until the reset (the sentence says so).

## What was run

All input in the scripts marked "hand" is REAL: mouse presses, moves and releases, keys, typed characters and touches
sent through Chrome's debugging port (`mk/hand.py`, on the classes of `tools/shot.py`). They reach the page as a
user's own. A hand does not click what it cannot see: `hand.py` checks that the thing is on top at the point of the
click. Read by script: what the boxes show and what `S` holds. Done by script, and said so in the logs: the choice in
the drop-down "Whole numbers" (its change event), the Drawing radius put back to 8 once, the controls over the
picture hidden for a screenshot, the 3000 random moves (the boxes' own input and Enter-key events).

| what | script | log | result |
| --- | --- | --- | --- |
| old smoke list, new page | `smoke28.py` | `logs/smoke-new.log` | 90 steps, 90 results, exit 0, no console errors, 553 s |
| the same, frozen page | `smoke28.py` | `logs/smoke-old.log` | 90, 90, exit 0, no console errors, 457 s |
| the two compared | `cmp_smoke.py`, `again6b.py` | `logs/cmp-smoke.txt`, `logs/again6b.txt` | see (e) |
| round 26: use.js, spot.js, phone.js | `old26.py` | `r26/*-new.log` | exit 0, no console errors, lines as kept for Version 20 |
| round 27: verd, shape, same6, flat, holes | `old27.py` | `r27-new/logs/*.txt` | see (e) |
| holes on the frozen page, 4 views | `old27.py`, `cmp_holes.py` | `r27-old/logs/holes.txt`, `logs/cmp-holes.txt` | letter for letter the new page's lines |
| the dials, wide, dark (hand) | `f1.py wide dark` | `logs/f1-wide-dark.txt` | 128 OK, 0 wrong, no console errors |
| the dials, phone, dark (hand) | `f1.py phone dark ...` | `logs/f1-phone-dark-open-ends-give-jump-frame-leave-flat2d.txt` | 87 OK, 0 wrong |
| Frame it and 2D, phone, light (hand) | `f1.py phone light frame flat2d` | `logs/f1-phone-light-frame-flat2d.txt` | 9 OK |
| saved 3D model, four states (hand) | `f1.py wide dark mesh` | `logs/f1-wide-dark-mesh.txt` | four sentences, all right |
| large sizes, touching, keys, emptied box (hand) | `f1.py wide dark extras` (`f1_extras.py`) | `logs/f1-wide-dark-extras.txt` | 23 OK |
| words and fit, four layouts (hand) | `words.py` | `logs/words-{wide,phone}-{dark,light}.txt` | 20 states fit; every text collected |
| more user actions; finger on the phone (hand) | `more.py wide`, `more.py phone` | `logs/more-wide.txt`, `logs/more-phone.txt` | 10 OK, 8 OK |
| 3000 random moves (by script) | `fuzz.js` through `runjs.py` | `logs/fuzz.json` | 0 rules broken |
| Frame it in other windows (hand) | `sizes.py`, `sizes2.py` | `logs/sizes.txt`, `logs/sizes2.txt` | defect D1 |
| same picture after a visit; one drag too far (hand) | `last.py` | `logs/last.txt` | 0 pixels; see D4 |

Pictures: `out/r28/ui/shots/` (277 files). Seen by me: the start picture, 150 / 400 / 1000 / 2000 framed in 3D and
2D, 150 and 300 and 400 after a drag without Frame it, the touching cases (100 with equal spheres; second sphere 50
at 200; 25 at 400; 33.33 at 300) in 3D and 2D, 100.1, second sphere 50 at 55.56 and at 190, second sphere 2, size 2
and 1, depths 1 2 3 4 100, the saved picture file, the Approach list with the row (wide and phone), the panel in
three scroll positions for five states in wide dark, and samples of the other three layouts, the phone's Frame it
pictures, the sideways-phone pictures of D1. In all of them: whole balls, no holes, no speckle, nothing I would call
a wrong picture.

## (e) The old lists

**Smoke list (90 steps), put together as `out/r27/final/mk/smoke27.py` does it.** New page: 90 steps with JavaScript,
90 result lines, exit 0, "no console errors". Against my own run of the same list on the frozen page
(`cmp_smoke.py`): 87 result lines the same word for word. The three others:

- step 2 "wheel zoom eased 5.2 -> 5.263 -> 5.824" (frozen: 5.294 in the middle) and step 24 "fly camera moved 0.699"
  (frozen 0.689): a camera caught while it glides; the end values are the same.
- step 7: "79 dials, 26 selects, 14 reset buttons" (frozen: 78 dials). The one new dial.

Pictures the list saves: 54; 52 the same to the pixel on both pages. The two others: `smoke-16-fly.png` (the gliding
camera of step 24) and `smoke-6b-approach-menu.png`. The second was taken, on the new page, while the picture
behind the open list was still being drawn (seen: `shots/zz-smoke-6b-new-left-frozen-right.png`; the list's step 8
has no wait). Run again three times on each page (`again6b.py`): this time the frozen page was caught half drawn once
and the new page never, and after a wait the picture is the same to the pixel in all six runs. So: timing, not the
page.

**Round 26's lists** (`use.js`, `spot.js` at 1400x950, `phone.js` at 390x800, dark; cut into steps by round 26's own
`steps_of` and its `p_prelude.js`, the page taken as `run_final.py` takes it): exit 0 and "no console errors" in all
three. Against the lines round 26 kept for Version 20 (`out/r26/final/v20-*.log`): the same, except a few numbers
that are a clock's (where a playing picture stood when it was paused: 0.71 / 0.74 and 1.2 / 1.21; frames counted in
24.6 s: 1478 / 1374).

**Round 27's scripts**, unchanged in what they do (`old27.py` gives them `R27_PAGE`, `R27_BASE` and an `R27_OUT` that
lands in my folder; `holes.py` and `flat.py` name one picture each with a fixed path under `out/r27/final/`, and only
that text was changed in the copy that ran, kept as `r27-new/logs/*-as-run.py`):

- `verd.py`: twin against tree.py 0 of 80000, shader 0 of 40644. Every line is the line round 27 kept.
- `shape.py`: all 14 lines (Learn from Balls on balls, "A whole shape" in 3D and 2D, back by the row, first group,
  Reset everything) as round 27 kept them for its merge rehearsal; no console errors.
- `same6.py` (new page against my frozen page): 6 states, picture alone 0 pixels differ, stage with controls 0.
- `flat.py`: the three lines of the 2D view at 100 and at 55.56 and the line of the saved model agree with the kept
  `flat.txt` in every number (72550 painted, 504 + 263, 36 shader-against-twin at depth 16; the model file 724913
  bytes with the same sentence).
- `holes.py`, its 11 views: 0 holes in every view. 7 lines are letter for letter the lines of round 27's
  `holes2.txt`; the other 4 views were only kept in an older wording, so I ran them on the frozen page: letter for
  letter the same (`logs/cmp-holes.txt`).

## (f) The dials

### What section 1.2 fixes, and what the page did (all with real input; `logs/f1-wide-dark.txt`)

- **Ends.** Size slider 2 to 400 (dragged past both ends: 400 and 2), typed 1 to 2000; second sphere slider 2 to
  100, typed 2 to 100; depth slider 1 to 100, typed 1 to 1000. Home and End on each slider go to its ends.
- **Typed past the ends.** Size: 0 gives 1 (box flashes "clamped"), 1 gives 1, 2000 gives 2000 (second sphere 2.5),
  5000 gives 2000 (clamped), -5 gives 1, "abc" and an emptied box leave 55.56 and flash "invalid". Also taken: "1e3",
  "150,5", spaces round a number. Second sphere: 0, 1 and -5 give 2; 2000 and 5000 give 100; "abc" leaves it. Depth:
  0 and -5 give 1; 2000 and 5000 give 1000; 2.6 gives 3; "abc" leaves it. Tab or a click elsewhere takes a typed
  number as Enter does; Escape throws it away.
- **Give way, size first.** From the start: 101 gives second sphere 49.5; 150 gives 33.33; 300 gives 16.67; 400
  gives 12.5; 2000 gives 2.5 (never under 2). A second sphere set on its own dial (30) stays at size 200 (60 is
  under 100) and gives way at 400 (to 12.5).
- **Give way, second sphere first.** Size 300, second sphere 40: the size becomes 125. Second sphere 100: the size
  becomes 50. Second sphere 50, size 80, second sphere 100: the size stays 80 (nothing has to give).
- **Back below 100.** The second sphere does not go back to 100; the sentence "The second sphere is now 50 % of the
  first. Reset this section puts it back to 100." is shown. "Reset this section" gives 55.56 / 100 / 16 with t
  exactly 1.4, and so does "Reset everything".
- **The jump.** Typed 51, 60, 75 give 50; 75.5, 76, 99 give 100. Dragged: the box shows 100 down to thumb 76, 50
  from 75 down to 50; let go at 66 the thumb goes to 50, at 90 to 100. Arrow keys on the slider and in the box, Page
  up / down, Shift + arrow, and the two small step buttons: one step from 50 up is 100, one step from 100 down is 50,
  the next is 49. On the phone the same with a finger on the slider (touch events): let go near 64 gives 50.
- **Sentences.** 100 with two equal spheres: Version 20's sentence word for word. Second sphere 50 at 200 and 25 at
  400: "At 200 the chain never ends ..." / "At 400 ...". Past 100: "Past 100 the second sphere has to be smaller
  than the first, or the two would cut into each other. It is now 33.33 % of the first." Depth 1 to 4: "With so few
  rounds of the search whole balls are still undecided, and they come out as broken shells."; at 5 it is gone.
- **Frame it** at 55.56, 150, 400 (and 1, 1000, 2000), 3D and 2D, wide and phone, dark and light: no part of the
  object on the rim of the picture, the Drawing radius holds the chain, the zoom limit is moved when it is in the way
  (2000: camera at 72.8). Also 1920x1080, 1024x768, 820x1180, 360x640, 1366x640, 1280x600, 1536x730, 1920x940,
  1400x700: whole. (Not whole: see D1.) "Reset view" after zooming in at 400 and at 2000 brings the whole chain back.
- **The row** in the Approach list: one real click gives Kleinian, Balls on balls, 55.56 / 100 / 16, no sentence;
  with the dials left at 150 it comes back to 150 / 33.33 with its sentence and frames the whole chain.
- **Leaving and coming back** (dials left at 150, depth 20): Show Mandelbrot and Kleinian again; Show Julia, another
  approach from the list, and back by the row; the first group and back; the Learn tab and back: every time 150 /
  33.33 / 20, the sentence, the program for a smaller second sphere, the whole chain in the picture.
- **2D view** at 150, 300, and 150 with the second sphere at 50: the picture's own number against the twin at 200 x
  200 points of the view: 0 differ.
- **Saved picture** at 150 (the page's own Start and Save buttons, default size and quality): 1724 x 1402, the
  picture of the screen (seen). Started at 150 and the section reset while it was drawn: 0 of 2417048 pixels differ
  from the first file.
- **Saved 3D model**: at the start "... neighbours 55.56 % of the middle ball, square grid, depth of search 16." (as
  Version 20, no second sphere named); at 150 "... neighbours 150 % of the middle ball, second sphere 33.33 % of the
  first, square grid, depth of search 16."; second sphere 50 at 55.56 and second sphere 25 at 300 with the honeycomb
  grid and depth 12: named rightly.
- **Reload**: the page opens as new (it keeps nothing between visits, as Version 20); the row then gives the start
  values, and size 80 leaves the second sphere at 100.
- **Others**: Extreme ranges on and off changes none of the three dials; the panel folded and opened; depth 1000 at
  the three worst places finishes within a second.

### Defects

**D1. MAJOR by the letter of 1.2 point 8, small in what the eye sees, and outside the two windows the brief names.
"Frame it" (and the row, which frames the same way) cuts the nearer neighbour off in a low, wide picture.**
Steps: a window 844 x 390 (a phone held sideways; also 915 x 412 and 900 x 420); the row Balls on balls; type 400
into "Size of the neighbours"; press Frame it. The right-hand big ball runs out of the lower edge of the picture
(about a tenth of it is missing), and at 300 the far right end of the chain is cut as well. Script:
`python -B out/r28/ui/mk/sizes2.py` (and `sizes.py` for 900 x 420). Numbers (`logs/sizes2.txt`): at 844 x 390 the
picture is 810 x 318; size 300: 188 pixels of the object on the bottom edge and 31 on the right edge; size 400: 185
and 4; at 915 x 412: 199 and 186 on the bottom edge. Size 150 is just inside (0 pixels on the edge, 2 to 3 probes in
the outermost ring). At 900 x 420 size 2000 is cut too (by the probes: 6 on the rim). Seen: `shots/sizes2-new-844x390-size-400.png`,
`-size-300.png`, `shots/sizes-900x420-size-400-3d.png`. The 2D view is whole in these windows.
Where it is fine: 1400x950, 390x800, and every window whose picture is less than about 2.1 times as wide as high
(1366x640: 1.90; 1280x600: 2.09, there the chain's right end stands within a fortieth of the picture's width of
the edge). Reasoned from the code, not tested by changing it: `ballsCam()` takes the camera's distance as the
largest of 3.3, 3.6 r / aspect and `3.75 * tall`; in a low picture the last one decides and is too small (the
windows that are fine have at least 4.5 times `tall`). Version 20 in the same window: whole at 55.56; at size 90 it
has 14 pixels of its own on the right edge.

**D2. minor. Touching "within rounding" is not seen as touching.** Steps: Reset this section; type 33.33 into
"Second sphere"; type 300 into "Size". 300 x 0.3333 = 99.99. The chain is 257 long and runs out of the picture on
both sides exactly as at true touching (seen: `shots/sizes-near-touch-rho33.33-size300-3d.png`, `-2d.png`), but the
page shows "The chain of balls runs out past the Drawing radius in the View section, so its far ends are not drawn."
and keeps showing it after Frame it; in the 2D view no sentence speaks of the chain at all. 1.2 point 6 asks for the
"never ends" sentence where p rho = 100 "within rounding". The test in `ballsTouch` is exact (1e-9). (`logs/sizes.txt`)

**D3. minor. The page remembers which dial moved last, shows it nowhere, and a number typed again does not count.**
Steps: Reset; type 150 into Size (second sphere becomes 33.33 by itself); type 33.33 into Second sphere and press
Enter (the hand has now set it, and by point 4 "the dial the user moved wins"); type 200 into Size. The second sphere
goes to 25. Had the hand typed 33.3, it would have stayed (200 x 0.333 = 67). Two panels that look the same act
differently. Cause, read in the code: the box holds that number already, so the dial kit takes it as nothing typed
and `BALLS_DIAL.follows` stays set. (`logs/f1-wide-dark.txt`, the line "33.33 typed into the second sphere's own
box")

**D4. minor, and a decision more than a defect: the builder's "follows".** By the bare formula of point 4 the second
sphere moves only when size x second sphere is over 100. The page moves it with the size whenever the size dial set
it last. Measured: size 150 then 250 gives 20 (bare formula: 33.33 stays); size dragged to 400 and then to 2 gives
50 (bare formula: 12.5 stays); in the 3000 random moves the second sphere moved 630 times with the size, 278 of them
without having to. What follows from the rules, with or without "follows", and a user will meet it:
- one drag too far and back changes the OTHER dial for good (`logs/last.txt`): size 80, slider dragged up to 131 and
  back to 82 in one go: the second sphere is 50 and stays; second sphere at size 150 dragged up to 85 and back down
  to 40 in one go: the size is 50, it was 150.
- "100" is three pictures: with two equal spheres an endless bar; one arrow step up, 100.1, three balls (second
  sphere 49.95); one step down again, 100 with the second sphere at 50, a short chain and no bar.
The builder's reading is the one that makes a drag past 100 smooth (with the bare formula the picture would jump at
about 202 and 404). I would keep it; it is the orchestrator's call.

**D5. minor. Typed 100.004: the box shows 100 and the sentence says "Past 100".** Steps: Reset; type 100.004 into
Size, Enter. Size shows 100, second sphere 50, sentence "Past 100 the second sphere has to be smaller than the first
... It is now 50 % of the first." (t is 0.99998.) Only a typed number with three decimals gets there; the slider and
the arrows step by 0.1.

**D6. minor, words.**
- The tooltip of the second sphere's box reads "From 2 to 100" and its arrows read "Up to the next whole number.
  Hold Shift for ten steps.", but 51 to 99 cannot be had and the step up from 50 goes to 100. (The dial kit writes
  both by itself.)
- After a large size is typed and before Frame it (2000: seen, `shots/f1-wide-dark-x-size-2000-typed-no-frame.png`)
  the sentence says "... so its far ends are not drawn", while it is the two big neighbours themselves that the
  Drawing radius cuts open: one of them shows as a flat wall over the right third of the picture. Frame it cures it.
- The help of the size dial is now two sentences (round 27 asked for one each). Plain, and I would leave it.
- With the spheres touching, a smaller second sphere and a depth under 5, four sentences stand in one block: 504
  characters. It fits (182 pixels high in both layouts). The touching sentence alone is 51 words.
- On the phone the status sentences stand above the dials, so while the size dial is under the thumb they are
  scrolled out of sight behind the pinned picture. The second sphere's own box, right below, does show the number.

**D7. minor, and already so on Version 20.** When the chain is too long to frame but does not touch (second sphere
50, size 199.8: reach 57), Frame it shows a stretch: in 3D with the Drawing-radius sentence (right after the button
whose tooltip promises "a view that shows the whole chain. A zoom limit or a Drawing radius that is in the way is
moved as well."), in the 2D view with no sentence at all. Version 20 does both at size 99 (measured on the frozen
page, `logs/sizes.txt`). Point 8 asks for "a plain sentence when it is not" possible.

### For the orchestrator to weigh: plainness of "second sphere"

The words are fixed by decisions 3 and 6, and they are in the house vocabulary. But read as the user reads: the
picture is made of balls, and "Second sphere, % of the first" sits right under "Size of the neighbours, % of the
middle ball". Someone who has just made the neighbours LARGER is then told "Past 100 the second sphere has to be
smaller than the first". Nothing on the page says that the two spheres are not balls of the picture; the help says
"The sphere inversions use two spheres", which only helps a reader who knows what a sphere inversion uses. I think
a non-mathematician does not get this at first reading. What the dial does to the picture is plain and true to the
pictures (the neighbours' buds get smaller and stand further apart; at 2 the neighbours are bare). A label and a
sentence that say that would be understood; this is a suggestion, not a defect of the build.

### What the eye should know (seen; none of it a fault of the build)

- **The picture jumps at 100.** At 100 with two equal spheres: an endless bar with holes. At 100.1: three balls, the
  neighbours with small sparse buds (`shots/f1-wide-dark-x-size100-equal-touch-framed-3d.png`, `-x-size100.1-...`).
- **After a drag past 100 without Frame it** the camera stays where it was, and the two neighbours fill the sides of
  the picture (`shots/f1-wide-dark-size-400-after-drag-no-frame.png`). One press of Frame it shows all of it.
- **Back below 100 the old look does not return** until the reset: at 55.56 with the second sphere at 50 the
  neighbours are almost bare, where Version 20's are covered with balls on balls
  (`shots/f1-wide-dark-x-rho50-size55.56-framed-3d.png` against `shots/f1-wide-dark-as-the-row-gives-it.png`). The
  sentence says what to press.
- At 1000 and 2000 the middle ball is a few pixels between two huge balls; at size 2 and 1 the picture is one ball.
- Depth 1 is not "broken shells" but a wall of colour over most of the picture; 2 and 3 are broken shells.

### Checked and found clean

Everything in the list under "What section 1.2 fixes"; the fit of the panel (`words.py`: every part inside the
panel and the window, no text cut off, the numbers 1999.9 and 1000 inside their boxes, no part over another, no
sideways scroll; 5 states x 4 layouts); the row and its explanation on wide and phone; the theme (dark and light
both taken by the page); no stale text anywhere in the page that still speaks of "three dials" for this entry; the
programs (`k-balls` with two equal spheres, `k-balls2` otherwise, never a failed program); a state past 100 survives
Learn, the first group, another kind of picture, Extreme ranges, a folded panel; 3000 random moves; touch input on
all three sliders; no console error or warning in any of my runs.

### My own mistakes on the way (kept in the logs, so that nobody takes them for faults of the page)

- `logs/f1-wide-dark-first-run.txt` marks three lines WRONG. All three were my script's: it asked whether
  `#ballsPart` has a box (it is `display: contents`, so it never has one); it "typed" an empty text without emptying
  the box; it wanted 34.33 where the dial's arrows go to the next whole number (34). The second run is clean.
- `logs/f1-phone-dark-first-run.txt` marks two lines WRONG: my click on an approach in the open list landed on a
  point that the pinned picture covers on the phone. `hand.py` now looks first. The third run is clean.
- `logs/f1-phone-dark-second-run-stopped.txt`: in the second phone run the browser stopped answering for about 16
  minutes and then closed (12:58 to 13:14), at a step that passed in the first and third run in two seconds (leaving
  the 2D view at 150 after Frame it). Other agents were using the machine. I could not make it happen again and do
  not know the cause; I name it so that it is not lost.
- `sizes.py` marks 900x420 only by probes; `sizes2.py` reads the picture's own edge pixels as well.

## Files

- `mk/hand.py` (real input), `mk/f1.py` + `mk/f1_extras.py`, `mk/words.py`, `mk/more.py`, `mk/sizes.py`,
  `mk/sizes2.py`, `mk/last.py`, `mk/fuzz.js` + `mk/runjs.py`: section f.
- `mk/smoke28.py`, `mk/old26.py`, `mk/old27.py`, `mk/queue_old.py`, `mk/cmp_smoke.py`, `mk/cmp_holes.py`,
  `mk/again6b.py`: section e.
- `logs/`, `r26/`, `r27-new/`, `r27-old/`, `smoke-smoke-new/`, `smoke-smoke-old/`, `again6b/`, `shots/`.
- Left in `dist/`: `r28-ui.html`, `r28-base-ui.html`.
