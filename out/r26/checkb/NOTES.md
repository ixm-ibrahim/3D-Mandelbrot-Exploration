# Round 26, checker "eyes": the joined page as the user would meet it

Page judged: `dist/r26-checkb.html`, built by me with `python build.py --name r26-checkb` at 01:58 and byte for
byte the joiner's `dist/r26-join.html` (`cmp` says identical). I changed no file in `src/`. Everything here is in
`out/r26/checkb/`.

Verdict: **fix first**, but the list of things to fix first is short (three, each a few lines) and the thing the
user asked for is there and reads well. In 2D the ten-second test passes plainly.

## 0. How it was done

`eyes.py go NAME.js` cuts a list into steps and runs it through `tools/shot.py`; `eyes.py sheet` tiles pictures.
Every list drives the page by its own controls (the Learn tab, the "A whole shape" radio, the buttons and switches
under the picture, the ticks, the slider's `input` event, scripted pointers and wheel on the stage). The test handle
was used only to read state back, and in t6/t8 to set a c or a slider place exactly.

| list | what | sizes and themes | log |
|---|---|---|---|
| t1.js | Learn, "A whole shape", let it play by itself: a whole-window picture every 0.47 s | 1400x950 dark, light | t1-wide-dark.log, t1-wide-light.log |
| t2.js | the same in 3D (3D switch under the picture, Play) | 1400x950 dark, light | t2-wide-*.log |
| t3.js | 3D, five approaches x ten views (steps 0, 2, 4, 8, 16; turned; zoomed; Julia c = -1) | 1400x950 dark, light | t3-wide-*.log |
| t4.js | Julia shape, Both, the diamond dragged (left picture, right picture, out of the shape), the four named c | 1400x950 dark, light | t4-wide-*.log |
| t5.js | the phone: finding Learn, playing, every control, the panel | 390x800 dark, light | t5-phone-*.log |
| t6.js | every sentence the feature can show, read from the page | 1400x950 | t6-words.log, t6-words-pretty.txt |
| t7.js, t7b.js | feel: Play to first movement, the slider under the hand, 3D frame times | 1400x950 dark | t7-feel-wide-dark.log, t7b-feel-run1.log, t7b-feel-run2.log |
| t8.js | Both in 3D, c off the flat plane, zooming a late step, one-step buttons, reset, leaving and coming back | 1400x950 dark | t8-odds-wide-dark.log |
| t9.js | how much each step takes away (from mask2) | | t9-bites.log |
| t10.js | step 1 held at 0.4, 3D beside 2D | 1400x950 dark, light | t10-step1-*.log |

All 19 runs end "no console errors", exit code 0. 455 pictures taken; I looked at all of them: the long runs as
sheets (`sheet-*.png`, each tile carries its file name; the light-theme play frames only as small tiles), the
ones a finding rests on at full size.

## 1. The ten-second test, 2D (t1)

Passes. Sheets `sheet-t1-wide-dark-0.png` to `-8.png`.

What the clock showed after the click on "A whole shape" (t1-wide-dark.log):

| seconds | picture | sentence |
|---|---|---|
| 0 to 0.05 | whole disc | "The big circle: every point no further than 2 from the centre. ..." |
| 0.05 to 1.1 | whole disc, label "step 1" in red | "Step 1: every dot goes from 0 to its own c. That is still inside the big circle, so nothing is thrown out yet." |
| 1.1 to 1.45 | whole disc | "What is left after 1 step: still the whole big circle, because ..." |
| 1.45 to 2.9 | half the disc lights up salmon, darkens, is gone; a thin outline stays | "Step 2: every point that is still here takes one more step. ..." |
| 4.3 | after 3 steps: a pear | |
| 7.2 | after 5 steps: the Mandelbrot outline can be recognised | |
| 10.0 | after 7 steps | |
| 23.5 | after 16 steps, Play button says Play again | "What is left after 16 steps. After endlessly many steps this becomes the Mandelbrot set." |

- Is it plain that a circle is being eaten away into the Mandelbrot shape? Yes, from the pictures alone, by second
  three. The salmon bite, its fading, and the thin outline it leaves say it without a word.
- The bite is visible long enough: full colour for about 0.5 s, fading over 0.6 s more (Normal speed).
- The ghost (thin outline of the shape before) is a help, not clutter: when the red is gone it still shows what
  was lost.
- The last step looks finished: the well-known shape, the button back to "Play", a closing sentence.
- What a newcomer would misread or miss:
  1. The opening sentence is on the page for a twentieth of a second (the play starts at once), so the first
     sentence anyone can read is the "every dot goes from 0 to its own c" one, over a picture in which nothing
     moves for 1.45 s. (defect W1)
  2. From step 9 on nothing can be seen to change at this size, for the last 11.6 of 23.5 seconds, while the label
     flips between red "step N" and "after N steps". Numbers (t9-bites.log, stage 862x511, big circle 215 px):
     step 2 takes 50.2 % of the disc, step 3 16.8 %, step 4 6.9 %, step 5 3.8 %, step 6 2.2 %, step 8 1.0 %
     (1,487 stage pixels along the whole rim), step 12 0.36 %, step 16 0.18 % (263 pixels). The Julia shape at the
     opening c: step 8 0.28 %, steps 13 to 16 between 28 and 6 pixels. Zoomed in 4.5 times the bite of step 13 is
     there to see (`t8-odds-wide-dark-08-2d-m-12.3-zoomed.png`). (defect M1)
  3. The shape of step 16 takes 24 % of the stage's width.

## 2. The same in 3D (t2, t3, t10)

- Step 0 (`t2-wide-dark-a-step0.png`, `sheet-t3-wide-light-0a.png`): a shaded ball, clearly round, with a
  highlight. Not a flat disc, not a dark blob. Dark theme: reads as a polished brass ball; that it is see-through
  can only be guessed from a second soft glow low on the right. Light theme: reads as a ball of tinted glass.
- Far side and inside: seen as soon as there is something inside. "After 2 steps" (`t2-wide-dark-play-05.png`) is
  the best 3D picture of the feature: a brass body inside a grey glass ball. With "Sphere inversions, two planes"
  and "Turning plane, along" the folds inside show through at steps 2 to 4 (`sheet-t3-wide-dark-1a.png`,
  `-2a.png`); with the Lathe the nested rings show at step 8 (`sheet-t3-wide-dark-3b.png`).
- Does it read as a solid being carved? Yes for steps 2 to 6, by the before and after. But two things spoil it:
  1. **Step 1: the whole ball turns red for about a second, and the sentence under it says "nothing is thrown out
     yet".** Held at 0.4 of step 1 the page asks the 3D picture for skin 0 with tint 1
     (t10-step1-dark.log). `sheet-t10-step1.png` puts it beside the 2D page at the same place, where the disc
     rightly stays brass. In Both the left ball is red too, under "Left: ... nothing is thrown out". (defect E1)
  2. In the dark theme the whole body turns the warning colour at every step, and the brass body that stays cannot
     be seen through it until late in the step. So in 3D the red does not say which part goes; in 2D it does.
     From step 7 on the picture is a small gold lump that blinks red sixteen times
     (`sheet-t2-wide-dark-rest.png`, `t10-step1-dark-3d-m-06.4.png` beside `t10-step1-dark-2d-m-06.4.png`).
     In the light theme the red skin is see-through enough and it reads as a red peel round the body
     (`sheet-t2-wide-light-0.png`, tiles 03 and 06). (defect E2)
- Steps 8 and 16, by approach (dark `sheet-t3-wide-dark-*a.png`, `*b.png`; light `sheet-t3-wide-light-*`):

| approach | after 8 | after 16 | turned and zoomed |
|---|---|---|---|
| Sphere inversions, one plane | smooth lump, clear | smooth, clear, small | lovely; from above it is the Mandelbrot outline |
| Sphere inversions, two planes | crumpled foil, still a shape | grain: a speckled lump | at 16 a cloud of grain with a few sheets in it |
| Turning plane, along | spiky wool | noise: a ball of gold wool (`t3-wide-dark-24.png`, `-27.png`) | no shape to make out at 16 |
| Quaternion square (Lathe) | glass shells with rings, the best "glass" | the rings turn to dotted lines, form still readable | readable |
| Mandelbulb | lump with whorls | grainy on top, outline readable | from above the outline is clear |

  So: the glass does not turn into noise by step 8 for any of the five; by step 16 it does for two of them and
  half does for two more. By eye I cannot tell how much of that is the rule's own raggedness and how much is the
  drawing. (defect M2)
- As the view opens the Mandelbrot shape is seen nearly edge on: an island. Turned to look from above
  (`t3-wide-dark-05.png`) it is at once the shape of the 2D page. (suggestion S1)
- Turning and zooming work: a drag turns, the wheel zooms, "Reset view" appears; in Both one drag turns both
  pictures (`t8-odds-wide-dark-05-3d-both-08-turned.png`); with c lifted off the plane the diamond gets a dotted
  stalk and the sentence about the cut is dropped (`t8-odds-wide-dark-06-3d-j-c-lifted.png`).

## 3. Mandelbrot shape, Julia shape, Both (t4)

- From the pictures the difference is plain: `sheet-t4-wide-dark-2-both.png`, `-3-both.png`. Step 1 of Both is a
  good moment: left nothing happens, right a big bite.
- Dragging the diamond: the right picture follows live, 16.7 ms a frame through the whole drag (t4-wide-dark.log,
  20 frames, 14.6 to 18.4 ms). The diamond of the right picture can be taken too. Dragged out of the left shape
  (c = 0.6, 0.6) the right shape falls into crumbs (`t4-wide-dark-drag-4-outside-released.png`): the best single
  demonstration of how the two belong together, and no sentence points at it. (suggestion S2)
- Is it clear that the diamond in the left picture chooses the right picture? After one drag, yes. Before it,
  only from the words: both pictures carry the same diamond and nothing in the picture ties them. (defect M9)
- The four named values match their pictures (`sheet-t4-wide-dark-5-named.png`): the basilica, the rabbit, a
  thin branching line for c = i, a disc for c = 0.
- The one-line helps are where a non-mathematician stumbles: section 4.

## 4. Words (t0, t6)

Read from the page at every half step, for the six choices and nineteen odd cases (powers 3, 2.5 and −2, a
modifier, c outside the big circle, outside the shape and off the flat plane, four other approaches); 47 KB in
`t6-words-pretty.txt`.

- **"Do not use" list: 0 hits** (iterat*, escape, bailout, radius, preimage, level set, orbit, potential,
  membership, sample, voxel, shader, mesh, render).
- **Not true by section 1: none found.** "Becomes the Mandelbrot set" is said only on the 2D page with a whole
  power of 2 or more; in 3D the last sentence is "The picture stops here. More steps could only take more away.";
  the cut sentence is dropped for c off the plane and for "Mandelbulb, classic"; "thrown out" is always the rule
  of the game. The one untruth is in the picture, not the words (E1).
- **Circle where it shows a ball:** the tooltip of "Start again" says "Back to the big circle" in 3D
  (t2-wide-dark.log, step 3). Nothing else: all 3D sentences say ball, the panel's note says both.
- **Sentences a non-mathematician would stumble on, with a better wording.** (The first five are the round's own
  example texts, so this is a decision for the lead, not a builder's slip.) The trouble is the same each time:
  "a c", "its dot" and "0" are used as if known, and this part of the panel never says what a step is.

| where | now | better |
|---|---|---|
| panel note | "Take every point inside the big circle (in 3D, the big ball) and let each one take steps. ..." | add: "A step is the lab's rule: square, then add c. (Follow: One point shows one step slowly.)" |
| help, Mandelbrot | "Every point of the picture is a c of its own, and its dot starts at 0." | "Each point of the picture is tried as the number c, the one that is added at every step. Its dot always starts at the centre." |
| help, Julia | "One c for everybody, the diamond. Every point of the picture is a place to start from." | "The number c is the same for all: the diamond. Each point of the picture is a place where a dot starts." |
| help, Both | "The two side by side: the Mandelbrot shape with the diamond at c, and the Julia shape of that c." | "Side by side. The diamond in the left picture picks one c; the right picture is the Julia shape for that c. Drag the diamond and watch the right picture." |
| step 0, Mandelbrot | "... Each point is a c of its own, and its dot starts at 0." | "... Each point is tried as the number c; its dot starts at the centre." |
| step 1 under way | "Step 1: every dot goes from 0 to its own c. That is still inside the big circle, so nothing is thrown out yet." | "Step 1: each dot jumps from the centre to its own point. Nobody lands outside the big circle, so nothing is thrown out yet." |
| after step 1 | "What is left after 1 step: still the whole big circle, because the first step only takes each dot from 0 to its own c." | "After 1 step the whole big circle is still there: the first step only carried each dot from the centre to its own point." |
| Both, whole step | "What is left after 3 steps: on the left for every c, on the right for the one c of the diamond." | "What is left after 3 steps. Left: the Mandelbrot shape. Right: the Julia shape for the diamond's c." |
| label | "Step 3 of 16: being taken" | "Step 3 of 16: under way" |
| 3D, What to notice | "With this approach and a c in the flat plane, as now, cutting the 3D shape through the middle (at z = 0) gives exactly the 2D shape of the same step." | "Slice this 3D shape level through its middle, where the dotted ring runs, and the cut is exactly the 2D picture of the same step. (True for this approach while c's z dial stands at 0.)" |
| 3D, the rule | "In 3D space a step is taken the way the approach chosen under Approach and equation takes it: "...", with its dials and the power as they stand there." | "In 3D the steps follow the approach chosen under Approach and equation, now "...", with its dials and power as set there." |
| named values | "c = −0.1226 + 0.7449i, the rabbit"; "c = i, a dendrite" | "the rabbit (c at x −0.12, y 0.74)"; "a bare twig (c at x 0, y 1)". The dials say "along x" and "along y"; "i" is explained nowhere, and "dendrite" is a specialist's word. |
| 3D hint, Julia and Both | "Drag to turn the picture. Scroll or pinch to zoom." | add "Move c with its dials." (in 3D a drag on the diamond turns the picture; t8-odds-wide-dark.log step 6: c unchanged) |
| late steps | the same sentence to the end | from the step whose bite is thinner than a pixel: "The bites are now too fine to see at this size. Zoom in." |
| tooltip, 3D | "Back to the big circle" | "Back to the big ball" |

- Plain and good as they are: "The ones that land outside the big circle are thrown out.", "What is left after N
  steps.", "The circle is not bent into the shape. It is eaten away ...", "The picture stops here. More steps could
  only take more away.", "nothing is left to see: every point of the picture has been thrown out".
- At 1400x950 two sentences leave one short word alone on a second line ("0.", "c."), as the joiner says.

## 5. Reach and layout (t5)

Phone 390x800, dark and light (`sheet-t5-phone-dark-1.png` to `-9.png`, `sheet-t5-phone-light-*.png`).

- Good: at the top of the page the stage (y 327 to 569) and the whole transport (to y 799) are in the window
  together; once the page is scrolled the stage pins to the top (0 to 242) with the transport under it (250 to
  472), and the panel scrolls beneath. Picture, sentence, slider, Play, the two steppers, Start again,
  Mandelbrot / Julia / Both and 2D / 3D are all in reach without the picture leaving (t5-phone-dark.log, step 21:
  every "inWindow" true).
- Nothing jumps when the sentence changes: the sentence box stays 57 px high (three lines) and the slider stays at
  y 338 for all five sentences tried; at 1400x950 the slider stands at the same height under one-line and
  two-line sentences in every picture (not measured there, seen). Page width stays 390.
- Defects, all minor:
  - Where the reader lands after tapping "A whole shape", the transport's row MANDELBROT | JULIA | BOTH stands
    about 57 px (by the picture) above the lab's own tabs MANDELBROT | JULIA | KLEINIAN | LEARN (`t5-phone-dark-play-00.png`). A thumb
    meant for the upper "Julia" that hits the lower one leaves Learn. (M5)
  - Both: the status label of the left picture ("the start", "after 16 steps") runs into the top of the big circle
    and its "2"; "Unpin picture" covers the top right and "Reset view" the bottom right of the right picture
    (`zoom-phone-both-labels.png`). (M6)
  - Small targets: 2D and 3D are 33 px wide each, the tick numbers 16x18 px, the Speed box 23 px high (in this
    browser the page does not see a coarse pointer, which would give the switches 44 px of height). (M7)
- Light theme: everything readable at both sizes. Brass becomes a dark gold, the bite brick red; less contrast
  between the two than in the dark theme but enough (`sheet-t4-wide-light-1.png`). The glass looks more like glass
  in the light theme than in the dark (`sheet-t3-wide-light-0a.png`, `-1a.png`, `-3b.png`).
- 1400x950: the numbers 1 and −1 of the upright axis sit exactly on the top and bottom tips of the Mandelbrot
  shape and look like dirt on them (`zoom-t1-end-axis-numbers.png`). (M8)

## 6. Feel (t7, t7b)

Other work was using this machine and its graphics card the whole time (processor load 42 to 93 % in my
samples; 24 to 31 Chrome processes of other runs had been started shortly before each of mine), so the 3D figures
are upper bounds and the slow ones cannot be laid at the page's door.

- Play to first movement (t7, step 3 and 4): the button says "Pause" within 0.5 ms; the slider knob has moved
  after 31 to 54 ms; the picture's own label changes within one frame. In 3D the first picture is off the card
  after 21 to 52 ms. For the Mandelbrot shape the shape itself first changes 1.45 s after Play (step 1 takes
  nothing away); for the Julia shape at once.
- The slider under the hand, 2D (one value a frame, 0 to 16 and back, 180 frames): the page needs 2.1 ms a change
  (Mandelbrot) and 4.6 ms (Both); 16.7 ms between frames in the middle, slowest 41.6 and 51 ms; the picture never
  disagreed with the knob. It follows the hand.
- The slider in 3D, opening approach: the card needed 13.7 ms a picture in the middle on the quieter run
  (t7b-feel-run2.log; one in twenty over 72 ms), 26.7 ms on a busier one, 67.8 ms on the busiest (t7), each at
  862x511. Both, busiest run: 113 ms.
- 3D while it plays, opening approach, Normal speed: 16.7 ms between frames in the middle on all three runs. The
  card: 8.2 ms a picture in the middle, one in twenty over 42.6 ms, slowest 80 ms (run 2); 8.5 / 70 / 163 ms
  (run 1); 25 / 136 / 280 ms (t7, when the play took 28.7 s instead of 23.2). Other approaches, busiest run only:
  two planes, Both 25.5 ms in the middle; Turning plane, along 16.9; Lathe 14.6 with one picture of 666 ms;
  Mandelbulb, Both 39.4.
- A yardstick for how busy the card was: one and the same resting picture (step 3, 1724x1022) took 58 to 138 ms
  on run 2 and 75 to 264 ms on run 1.
- By the middle values 3D is smooth while it plays (the joiner's quiet-machine 8.4 to 8.7 ms is what I see too).
  Whether the stalls are the page's or the neighbours' I could not settle. Not verified on a quiet machine by me.
- The one-step button plays one step in 1.1 s and stops on it; back goes back at once; both are greyed at the
  ends (t8, step 12).

## 7. Defects

Major (fix before the user sees it):

- **E1.** 3D, step 1: the whole ball turns the warning colour while the sentence says nothing is thrown out; in
  Both the left ball too. `sheet-t10-step1.png`, `t2-wide-dark-play-00.png`, `t2-wide-light-play-00.png`.
  Fix in `learnShapeLevels` (67): no tint for a skin from which the step takes nothing (k = 0 with
  `learnShapeZeroStays()`); for Both the two pictures then need levels of their own, which the contract does not
  have yet (a `levels` on a pane that overrides `o.levels` would do).
- **W1.** On the first switch the play starts at once, so the opening sentence is up for 0.05 s and the first
  1.45 s show a still picture under the hardest sentence. t1-wide-dark.log (62 ms: step 0 text; 537 ms: step 1
  text), `t1-wide-dark-play-00.png`. Fix: when a play starts from 0, rest on step 0 for about 1.5 s first
  (`Sh.dwell` in `learnShapePlay`).
- **W2.** The helps and sentences that tell the Mandelbrot shape from the Julia shape lean on "a c of its own",
  "its dot", "0", and nothing in this part of the panel says what a step is. This user has twice called such
  text Greek. Wordings in section 4. Decision for the lead: these are the round's own example sentences.

Minor:

- **E2.** 3D, dark theme: at every step the whole body goes red and hides the body that stays; from step 7 a
  small lump blinks red. Fix: bring the new body up at full strength from the start of the step and draw the
  outgoing skin as red glass (strength near the ghost's, not 0.96), as the light theme nearly does already.
- **M1.** The second half of a play shows nothing at normal size (numbers in section 1). Shorter late steps, a
  gentle zoom, or the sentence of section 4.
- **M2.** 3D at steps 12 to 16 is grain for the rougher approaches; no shape for "Turning plane, along".
- **M3.** Tooltip "Back to the big circle" in 3D.
- **M4.** 3D with a diamond: the hint does not say that c is moved by its dials there.
- **M5, M6, M7.** Phone: the two look-alike rows; labels and buttons over the pictures of Both; small targets.
- **M8.** Axis numbers on the tips of the shape.
- **M9.** Both: nothing in the picture ties the left diamond to the right picture before the first drag. Naming
  the right picture "Julia shape for the diamond's c" would.
- **M10.** While playing, the sentence changes every 0.35 / 1.1 s; "What is left after N steps." is up for 0.35 s.
  One sentence for the whole play and the "what is left" form at rest would be calmer.
- **M11.** The late shapes are small on the stage (24 % of its width at step 16 in 2D, less in 3D).

Suggestions: **S1** open the 3D view from higher up (pitch about 0.9 instead of 0.4) so that the Mandelbrot
outline is seen. **S2** a line under "What to notice" for Both: "Drag the diamond out of the left shape and the
right one falls to pieces."

## 8. Good, and not to be touched

1. The 2D bite: salmon, darkening, gone, a thin outline left. The feature rests on it.
2. The resting 2D picture: brass shape, dashed big circle, faint axes.
3. Both side by side with a live diamond in each picture, at a full 60 frames a second.
4. The four named values and what they show.
5. The fixed height of the sentence and the transport: nothing jumps.
6. The phone layout: picture pinned, everything under it in reach.
7. 3D after 2 to 4 steps: a brass body inside a glass ball. The 3D pictures in the light theme.
8. Turning and zooming in 3D, both pictures of Both together, "Reset view".
9. Zooming the flat picture at a late step: the bites are there again.
10. The honest endings: "After endlessly many steps this becomes the Mandelbrot set" only where it is known,
    "The picture stops here" elsewhere, "nothing is left to see" when the picture is empty.
11. "The circle is not bent into the shape. It is eaten away."
12. Coming back from another tab keeps the kind, the step and c; "Reset this section" puts Follow back to One
    point and the second visit does not play by itself (t8, steps 13 to 15).

## 9. Not done

- No quiet machine: the 3D timings are upper bounds (section 6).
- Only scripted pointers and touches in headless Chrome. No real phone, no real finger, no Safari or Firefox, no
  sharp (2x) screen.
- Reduced motion, keyboard use, the lost-graphics case and the page without the 3D module were not repeated; the
  joiner's logs cover them.
- One point (the old Learn) was not rechecked beyond seeing it open (`t1-wide-dark-b-learn.png`).
