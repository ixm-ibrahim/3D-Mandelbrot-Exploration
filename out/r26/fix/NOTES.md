# Round 26, the fixer: notes

The page that holds the work is `dist/r26-fix.html`, built from `src/` at 04:33 with
`python build.py --name r26-fix` (md5 `8ebc92be894d155cf2e236362e71ad6b`; built again at the end under another
name and found byte for byte the same). Every result below was measured on that build unless it says otherwise.

"As joined" below means `dist/r26-fix-before.html`, a byte copy of the joiner's `dist/r26-join.html`. Before my
first edit `src/` built exactly that page (`cmp`: identical, 02:54).

Changed: `src/js/67-learn-shape.js` (931 to 1135 lines), `src/js/68-learn-shape3d.js` (536 to 575),
`src/css/67-learn-shape.css` (66 to 74). Not changed: `src/js/66-learn-view.js`, `src/js/90-boot.js`.
Nothing was published. `squaring-lab.html`, `base*/`, `out/r25/`, `out/r21/` and the folders of the checkers,
the joiner and the builders were not written to (their lists were run from here, with the logs and pictures
written here).

## 1. One line per defect

All 22 defects were reproduced on the page as joined, except M13 (see there). "Proof" names the step of
`before.log` / `after.log` (the list `defects.js`), of `before-phone.log` / `after-phone.log` (`defects_phone.js`),
and the before/after picture. All files are in `out/r26/fix/`.

| id | verdict | on the page as joined | on the mended page | proof |
|---|---|---|---|---|
| A1 | cured | Power 1, Julia, 3D, step 12: "What is left after 12 steps." over an empty ball (picture covers 0 %). Same with c = (7, 0, 0) at step 2. | "After 12 steps nothing is left to see: every point of the picture has been thrown out." (c = 7: "After 2 steps nothing is left to see ...") | step 26 and 28; `pair-A1-nothing-left-in-3d.png`; the checker's `t16_confirm` and `t10_words3d` (0 flags, were 8) |
| A2 | cured | "Quaternions, 4D (slices)", w = 1.5. Mandelbrot shape, 3D: "nothing is thrown out yet" and "still the whole big ball", but 2,956 of 4,169 grid points of the ball are thrown out by step 1. Julia shape: "The big ball. Every point is a place to start from", but only 1,213 of 4,169 start inside. | Step 1: "every point that is still here takes one more step. The ones that land outside the big ball are thrown out." After it: "What is left after 1 step." Julia, step 0: "The start. With this approach's dials as they stand, the points near the surface of the big ball already count as outside, so the shape begins smaller." | step 24 and 25; `pair-A2-4d-slice-words.png`; `a-after-t10_words3d.log`: DEFECTS 0 |
| A3 | cured | `out2([-2, 0], 'm', null, 16)` = 15, `mask2` = 17; 1 of 16,641 points differs | 17 and 17 (41 and 41 with 40 steps); 0 of 16,641 differ | step 30; `a-after-t1_flat.log`: DEFECTS 0 (was 1) |
| A4 | cured | One point at step 1, move 1, 0.4; whole shape, 3D, 2D, back: step 0, move 0 | back at step 1, move 1, 0.4. Ending in 3D still starts afresh, as before | step 31; `a-after-t6_use.log`: DEFECTS 0 (was 1) |
| A5 | cured | 3D, c = (-1.8, 0.9, 0), zoom 4.5: the diamond is at pixel -480, the letter "c" stands alone at the left edge | neither is drawn (`diamonds: [null]`) | step 29; `pair-A5-lone-letter-c.png`; `a-after-t11_more.log`: DEFECTS 0 |
| E1 | cured | 3D, step 1 at 0.4: skin 0 asked with strength 0.96 and tint 1; the ball (in Both the left ball) is red under "nothing is thrown out" | the Mandelbrot ball is asked as one brass skin (`0:a1.00`) through the whole of step 1; in Both the right picture has its own skins (`1:a1.00 0:a0.42:t1.00`) | step 10 to 12; `pair-E1-step-1-in-3d.png` (dark and light); the checker's `t10.js`: `checkb-t10-wide-dark.log` |
| W1 | cured | the opening sentence is up for under 0.07 s; at 74 ms the page says "Step 1: every dot goes from 0 to its own c ..." | the play rests 1.5 s on the start (0.9 s at Fast, 2.4 s at Slow) with the opening sentence; first move after 1,553 ms | step 2 and 3; `more.log` step 3; `pair-W1-first-half-second.png` |
| W2 | cured | "a c of its own", "its dot starts at 0", "One c for everybody"; no word on what a step is | the eyes checker's wordings (section 3) | step 7; `pair-W2-M12-panel-words-2d.png` |
| E2 | cured | 3D, between two steps: the whole body red (`2:a0.96:t1.00`), the body that stays at 0.32 | the body that stays at full strength from the first eighth of the step, the part that goes a thin red peel round it (0.42); no red where the bite is too thin to see | step 13 to 16; `pair-E2-a-step-under-way-in-3d.png`; `sheet-steps-dark.png`, `sheet-steps-light.png` |
| M1 | cured (by the sentence) | steps 9 to 16 of a play: nothing to see, and the sentence goes on as if there were | from the step whose bite is under one pixel thick: "The bites are now too fine to see at this size. Zoom in." (by hand: "Step 13: this bite is too fine to see at this size. Zoom in."). Zoomed in, the plain sentence is back. | step 3, 5, 19; `more.log` step 4 and 5; `pair-M1-late-step-2d.png`, `pair-M1-late-step-3d.png` |
| M2 | cured for the drawing's share | step 16 of "Turning plane, along": a ball of gold wool | from step 5 to step 11 the near side of the body goes from glass to solid; the folds read | step 20 to 23; `pair-M2-step-16-rough-approaches.png`; the trial: `sheet-trylook-16.png`, `sheet-trylook-zoom.png`, `sheet-trylook-zoom2.png` |
| M3 | cured | tooltip of "Start again" in 3D: "Back to the big circle" | "Back to the big ball" | step 7 (`againTitle3d`) |
| M4 | cured | 3D hint with a diamond: "Drag to turn the picture. Scroll or pinch to zoom." | "Drag to turn, scroll or pinch to zoom. Move c with its dials." | step 7; `pair-M3-M4-3d-julia-hint.png` |
| M5 | cured | phone: the row MANDELBROT, JULIA, BOTH right above the lab's tabs, unnamed | the word "Shape" stands before the row (at every width) | `after-phone.log` step 2; `pair-M5-M7-phone-rows.png` |
| M6 | partly cured | phone, Both: the label runs into the big circle and its "2" | the big circle of two small pictures takes 76 % of the smaller side (was 84 %); the "2" at the top is left out. "Unpin picture" and "Reset view" still stand in the corners of the right picture | `pair-M6-phone-both.png` |
| M7 | partly cured | 2D and 3D: 33 and 32 px wide | 44 px each. The tick numbers (16 x 18) and the Speed box (23 high) are as they were | `after-phone.log` step 3 |
| M8 | cured | the figures 1 and -1 of the upright axis sit on the tips of the shape | the figures of the upright axis stand to the right of it | `pair-M8-axis-numbers.png` |
| M9 | cured | Both: the right picture is named "Julia shape" | "Julia shape for the diamond's c"; and under "What to notice": "After a step or two, drag the diamond out of the left shape and the right one falls to pieces." | step 7 and 8; `pair-M9-both-names.png` |
| M10 | cured | a play shows 32 sentences, the shortest for 0.32 s; "0." alone on a second line (lines of 790 and 14 px); "being taken" | a play shows 4 sentences: the opening one for 1.5 s, the play sentence for 11.4 s, "too fine" for 11.7 s, then the closing one; the lines are 755 and 145 px wide; "under way" | step 3 and 6; `pair-M10-sentence-and-label.png` |
| M11 | partly cured | 3D opens at pitch 0.4: a flat shape is seen nearly edge on | 3D opens at pitch 0.9. The late shapes are as small as before: no zoom of its own was added | step 17 and 18; `pair-M11-3d-as-it-opens.png` |
| M12 | cured | "cutting the 3D shape through the middle (at z = 0)"; "c = i, a dendrite"; "c = -0.1226 + 0.7449i" | the eyes checker's wordings (section 3) | step 7; `pair-M12-panel-words-3d.png`, `pair-W2-M12-panel-words-2d.png` |
| M13 | not reproduced | on a machine that was quiet at the time, a 3D play: 16.7 ms between frames (95 of 100 under 16.8), the card 5.2 ms a picture in the middle, slowest 8.5, none over 34 ms of 1,387. The checker saw one in twenty over 42 ms | two plays: 16.7 ms (16.8), the card 9.3 and 6.7 ms a picture in the middle, slowest 12.3 and 33.8, none over 34 ms of 1,481 and 1,480 | `checkb-t7b-feel-before.log`, `checkb-t7b-feel-1.log`, `checkb-t7b-feel-2.log` (the checker's own `t7b.js`); section 6 |

## 2. What I decided where the checkers left a choice

- **W1, the rest at the start.** Only a play from end to end that starts at step 0 rests (Play, the space bar,
  the play that starts by itself). The one-step button does not (`more.log` step 2: step 1 reached after 1.12 s),
  and Play from the middle does not (step 3: moving after 0.15 s).
- **M10, one sentence for a play.** While the steps play from end to end the sentence is "At each step every point
  that is still here takes one more step. The ones that land outside the big circle are thrown out." Standing
  still, with the slider, or one step at a time, each step has its own sentence as before. An empty picture is
  still said during a play ("Nothing is left to see: ...").
- **M1.** Of the three cures offered I took the sentence. Shorter late steps would have left the same stillness,
  and a zoom that moves by itself is a new feature (section 7). "Too fine" is measured, not guessed: the page
  counts the points each step throws out and divides by the length of the shape's outline, which gives the bite's
  thickness in pixels of the picture as it stands. Under 1 pixel is too fine. At 1400 x 950 the Mandelbrot shape's
  bites are 1.25, 0.91 and 0.60 px at steps 8, 9 and 10 (`thick.log`), and step 9 is where the eyes checker
  stopped seeing them. On the phone (stage 356 x 240) it is step 7 (`thick-phone.log`). A step that throws out
  nothing the picture shows is not called too fine.
- **A1, how the page knows a 3D shape is gone.** The 3D picture is not read back. The 3D module got one more
  question, `view.columns()`: the shape seen from straight above without glass, 192 x 192 upright lines with 192
  points each, from the same program the picture is drawn with. If no line meets shape k, nothing is left to see.
  It is asked once for a rule, a kind and a c, and costs the card 3 to 10 ms (`more.log` step 9, all 21
  approaches, a view of its own; inside the page 3 to 27 ms, `longframes.log`). I did not take the suggested grid of a few thousand points in JavaScript: at 0.2 between points it
  would call a shape gone while crumbs 20 pixels across are on show. The claim is made up to zoom 1.5 only.
  Checked against the arithmetic for ten settings at every step (`more.log` step 10): 0 wrong. The page says
  "nothing is left" at the step the 0.1 grid goes empty or up to three steps later, never earlier, except that at
  the power 1 it says so at step 8, where exactly one point is left (two balls touching).
  The same look from above gives the thickness of the bites in 3D (M1, E2).
- **E2, the red peel.** The suggested cure, tried and kept: the body that stays comes up at once, the outgoing
  skin thins to glass and then turns red. First thin, then red, so the whole body never flashes. One thing more
  was needed: at late steps the peel lies less than two pixels off the body and reddened all of it at every step,
  which is the blinking the checker described. So the peel's strength now follows the bite's thickness (full from
  3 px, none under half a pixel). Zoomed in, the peel is back (`more.log` step 5: `12:a0.36:t0.87` at zoom 4.5).
- **M2.** Tried four strengths of the near side at step 16 and step 10 for five approaches
  (`sheet-trylook-*.png`, taken on an earlier build of this page). At 0.6 the folds of "Turning plane, along" and
  the faces of "two planes" read; the smooth approaches lose nothing. Steps 0 to 5 are untouched glass, so the
  pictures the eyes checker praised (a brass body in a glass ball after 2 to 4 steps) are as they were. How much
  of the raggedness is the rule's own I cannot say either; the sentence was not changed for it.
- **M9, the line about dragging the diamond out.** It is true for a whole power of 2 or more without modifiers
  and from step 1 on, so it is shown only on the 2D page, in Both, for such a rule, and it begins "After a step or
  two". (At step 0 the left shape is the whole big circle and nothing falls apart.)
- **W2, the note.** "square, then add c" is true of the power 2 only. With another power the note reads
  "take to the power 3 (the dial "Power n"), then add c."
- **M12, the named values.** The name comes first, as the checker wrote it ("the rabbit (c at x -0.12, y 0.74)").
  Away from the plain power 2 only the value is shown, as before.

## 3. The words now (read from the page, `after.log` step 7, `core-words.log`)

- Note: "Take every point inside the big circle (in 3D, the big ball) and let each one take steps. A point that
  lands outside is thrown out. Press Play under the picture and watch what is left after each step. A step is the
  lab's rule: square, then add c. (Follow: One point shows one step slowly.)"
- Mandelbrot shape: "Each point of the picture is tried as the number c, the one that is added at every step. Its
  dot always starts at the centre."
- Julia shape: "The number c is the same for all: the diamond. Each point of the picture is a place where a dot
  starts."
- Both: "Side by side. The diamond in the left picture picks one c; the right picture is the Julia shape for that
  c. Drag the diamond and watch the right picture." (3D: "Move c with its dials and watch the right picture.")
- Step 0, Mandelbrot: "The big circle: every point no further than 2 from the centre. Each point is tried as the
  number c; its dot starts at the centre."
- Step 0, Both: "Two big circles. Left: each point is tried as the number c; its dot starts at the centre. Right:
  each point is where a dot starts, all with the diamond's c." (156 letters, the longest; it fits its three lines
  on the phone, `after-phone.log` step 8: 54 sentences, none too long.)
- Step 1 under way: "Step 1: each dot jumps from the centre to its own point. Nobody lands outside the big circle,
  so nothing is thrown out yet."
- After step 1: "After 1 step the whole big circle is still there: the first step only carried each dot from the
  centre to its own point."
- Both, a whole step: "What is left after 3 steps. Left: the Mandelbrot shape. Right: the Julia shape for the
  diamond's c."
- Label: "Step 3 of 16: under way".
- 3D rule: "In 3D the steps follow the approach chosen under Approach and equation, now "Sphere inversions, one
  plane", with its dials and power as set there."
- 3D, What to notice: "... Slice this 3D shape level through its middle, where the dotted ring runs, and the cut is
  exactly the 2D picture of the same step. (True for this approach while c's z dial stands at 0.)" For the
  Mandelbrot shape alone the bracket is "(True for this approach.)". Shown for the same 17 approaches as before
  (`join-cut.log`: they differ from the flat shape at 0 to 8 of 66,049 points; the 4 without the sentence at
  9,576 to 23,852).
- Named values: "the basilica (c at x -1, y 0)", "the rabbit (c at x -0.12, y 0.74)", "a bare twig (c at x 0,
  y 1)", "a plain disc (c at x 0, y 0)".
- The Julia step-0 sentence and the endings ("becomes the Mandelbrot set", "The picture stops here ...") are the
  round's own and were not flagged; they are as they were.
- Words of the "do not use" list: none, in three independent lists (`core-words.log`, `join-gone.log`,
  `a-after-t12_rest.log`: 0 found).

## 4. The checks, all on the final build

`sh out/r26/fix/final.sh PART` reruns each part. `final-run.out` is the record of the run 04:33 to 05:21,
`feel-run.out` that of the timings 05:23 to 05:40.

| part | what | result |
|---|---|---|
| smoke | the old smoke list of Version 18, 90 steps (`smoke-fix.log`) | 90 of 90 pass, no time-out, no console error. 87 result lines word for word as then; the 3 others are the joiner's three (two clock-dependent numbers, and 76 dials and 25 selects) |
| One point | builder core's `point.js` on the frozen page and on this page | 13 pictures, 0 pixels differ |
| One point | the arithmetic checker's `t8_old`: 109 states on the frozen page and on this page | 0 states differ (state, texts, stage and transport pixels) |
| mine | `defects.js` dark and light, `defects_phone.js` dark and light, `thick.js`, `motion.js`, `more.js`, `panel.js` | all end "no console errors" |
| eyes | the eyes checker's t0, t1, t2, t3, t4, t5, t6, t8, t9, t10 (14 runs, two themes, two sizes) | all end "no console errors", exit 0 |
| arith | the arithmetic checker's 15 scripts, `t9_robust` in four parts, `t7_play` four times | all exit 0. Flags: `t16`, `t10`, `t1`, `t6`, `t11`, `t12`, `t13`, `t15`, `t2b`, `t4`, `t8`, `t9` (all four), `t7_play` (all four): 0. `t2_pixels` 5, `t3_slice` 7, `t5_solid` 2, `t14_moving` 1: the same flags, of the same kind and nearly the same size, as in the checker's own run, where each was looked at and explained (their notes, section 2) |
| join | the joiner's look (4), hands, lost, cut, odd, gone, phone2 (2), no3d | all end "no console errors" |
| core | builder core's three, mask, words, drag, ui, calm, play (4), phone (2) | all end "no console errors" |
| three | builder three's slice and robust checks | slice against out: 56 cases, 3,698,744 points, 101 differ, none further than 1e-4 from a skin: number for number what the joiner had. So `slice()` is untouched by my change to the program text |

Checks of my own additions (`more.log`):
- `columns()` against the module's own `out()`: 33 x 33 lines with 48 points, seven approaches, both kinds: 0 to 3
  of 1,089 lines differ, every one within a hair of a skin (step 8).
- "Nothing is left" against the arithmetic: 0 wrong in ten settings (step 10).
- The graphics taken away and given back on an empty 3D shape: the sentence is right again afterwards (step 11).
- Plays: Both in 2D, an empty Julia shape in 3D, Both in 3D: 4 sentences each (step 6).

## 5. Lists of others that were run with a piece of their text changed

Each asked for words or a wait that I changed on purpose. The log of each run names the change in its first lines.

| list | changed | why |
|---|---|---|
| eyes `t3.js` | finds the named button by "x -1, y 0" instead of "c = -1" | M12 |
| joiner `cut.js`, `odd.js` | know the cut sentence by "the cut is exactly the 2D picture" | M12 |
| joiner `gone.js` | "Right: the Julia shape" for "Right: what is left"; "Left: the Mandelbrot shape" for "Left: what is left for every c"; no longer demands that nothing is said about an empty 3D Julia shape | W2; and that demand was defect A1 |
| core `ui.js` | waits 4.1 s for 2.6 s after the first switch; finds the four named buttons by their new words | W1, M12 |
| core `calm.js` | waits 2.1 s for 0.5 s after Play | W1 |
| arith `t12_rest` | reads the name of a named value from its own element (it is now the first part of the button) | M12 |
| arith `t2_pixels`, `t7_play`, `t9_robust`, `t11_more`, `t14_moving` | their pixel reference puts the big circle of two small pictures at 76 % of the smaller side | M6 |

Without those changes the same runs stop at exactly those places (seen in a first run on an earlier build).

## 6. Measurements (1400 x 950, dark, this machine, quiet at the time: 05:23 to 05:50)

- Play at Normal: 24.6 to 24.7 s (was 23.1): the first step 2.6 s (1.5 s of rest), the others 1.05 s, rests 0.35 s
  (`join-pace.log`, `a-after-t15_nest_rests.log`: rests 350 to 367 ms). Fast 12.2 s, Slow 46.9 s.
- 2D play: 16.7 ms between frames in the middle, 95 of 100 under 16.8; the page's own redraw 1.0 to 1.4 ms
  (`join-play.log`).
- 3D play, the joiner's list on this page (`join-play.log`), the card per picture, middle / 95th of 100 / slowest:
  opening approach 9.4 / 10.5 / 44.7 ms; Julia 7.9 / 10.3 / 35.4; Both 7.9 / 9.7 / 34.7; two planes, Both
  8.8 / 11.1 / 40.4; Pillow, Both 13.6 / 20.7 / 24.5. Between frames 16.7 ms in the middle in all of them; frames
  over 20 ms: 0 to 10 of about 1,480, Pillow 15 and 62.
- The same play (Mandelbrot shape, 3D, opening approach) on the page as joined and on this page, the card per
  picture in the middle: as joined 5.2 and 6.7 ms (two plays), mended 6.3, 6.7, 9.3 and 9.4 ms (four plays)
  (`checkb-t7b-feel-*.log`, `checkb-t7-feel*.log`, `join-play.log`). So a moving 3D picture costs the card
  somewhat more now, and the figure swings by 40 % from one play to the next. The slider swept by hand costs the
  same on both (7.1 and 7.0 ms). With the same view and the same skins a picture costs the same on both pages
  (`builds-before-1/2.log`, `builds-after-1/2.log`, nine approaches, 600 x 450: for example Pillow 'still' 46.8
  and 48.4 ms before, 46.9 and 48.4 after). So what costs more is what I changed on purpose: the view from higher
  up shows more of the shape, and the body that stays is drawn at full strength through the step. I did not
  measure the two apart. All of it stays under one frame (16.7 ms).
- Building a program takes longer, mostly 15 to 30 ms (opening approach 102 and 112 ms before, 123 and 141
  after; Pillow 170 and 176 before, 201 and 219 after). Once for each approach in a visit.
- Long frames in five 3D plays (`longframes.log`, as joined `longframes-before.log`): the first frame after Play,
  23 to 29 ms (as joined 21 ms); nothing else for the opening approach and for two planes; Pillow, Both: frames
  of 33 ms from 15.5 s on, 1,373 frames in the play (as joined: frames of 33 to 67 ms from 5.3 s on, 1,196
  frames). In the checker's longer list, seven plays on each page, one frame of about a tenth of a second turned
  up in four plays: once on the mended page (a 2D play, 109 ms) and three times on the page as joined (a 2D play
  and two 3D plays, 94 to 116 ms) (`checkb-t7-feel.log`, `checkb-t7-feel-before.log`). A 2D play does not use
  the card for its pictures, so I take these for the machine's, not the page's.
- A resting 3D picture after zooming in (`join-stall.log`, as joined `join-stall-before.log`): opening approach,
  zoom 2.5: 62 ms (125 as joined); zoom 6: 64 (65). Two planes, zoom 6: 75 (75). Pillow, zoom 2.5: 85 (118);
  zoom 6: 213 (261).
- Phone 390 x 800: stage 358 x 242, transport 222 high, together 464 px, 59 % of the window, page width 390: as
  before (`after-phone.log` step 3).

## 7. Not cured, and open

- **M6:** "Unpin picture" and "Reset view" still stand in the corners of the right picture of Both on a phone.
  "Unpin picture" belongs to the pin module, which is not mine.
- **M7:** the tick numbers are 16 x 18 px (seventeen numbers on 342 px cannot be wider), the Speed box is 23 px
  high (the same box as One point's).
- **M11:** the late shapes are still small on the stage. A zoom that moves by itself as the steps go on would be
  a new feature; the sentence says "Zoom in" instead. This is for the lead.
- **M2:** I cannot tell the rule's own raggedness from the drawing's any better than the checker could.
- Seen from higher up, the flat top of the opening approach's late shapes carries a pale patch with a straight
  edge (`after-M11-3d-m-16.png`). It was there before and showed less from the side.
- The joiner's open point stands: a resting picture of Pillow zoomed to 6 holds the page for about 0.2 s.
- The look from above (`columns()`) makes the page wait for the card once for each rule, kind and c: when the
  picture comes to rest, or 0.15 s into a play if it is not known by then (that is, during the rest on the
  start). In the plays I timed it was already known when Play was pressed, so I have not seen what the wait does
  to a play; it is 3 to 27 ms.
- "Nothing is left to see" in 3D is not said when zoomed in beyond 1.5; there the sentence stays "What is left
  after k steps." over an empty picture.
- With the page's change of the look from step 5 on, a deep 3D shape is no longer glass but a nearly solid body.
  The user asked for "a transparent shaded ball or something"; steps 0 to 5 are that. This is for the lead to
  look at (`pair-M2-step-16-rough-approaches.png`).
- Not run: a real phone, a finger, Safari, Firefox, a sharp screen.

## 8. Where the contract of section 4 is not followed to the letter

Mine:
- `view.draw`: a pane may carry `levels` of its own, which the module then uses for that pane in place of
  `o.levels`. The page always sends them; `o.levels` is the first picture's.
- A level may carry `solid` (0 to 1), and `o.solid` is the same for every level without one: that skin's near side
  more opaque, its far side fainter. The page sends it for the body from step 5 on. So "the skin of shape k drawn
  with this opacity" no longer has one look at every step.
- New: `view.columns(kind, c, { size, half, stops, maxK })`, the highest number `slice()` gives anywhere on each
  upright line through the ball. The page calls it.
- Item 5 of the round (between two steps, in 3D): the skin of shape k + 1 comes up in the first eighth of the step,
  not through the whole of it; the skin of shape k thins to a peel (strength 0.42, less for a thin bite) and is
  tinted only then. For a Mandelbrot shape whose first step throws nothing out, step 1 is drawn as one skin and
  no ghost follows it.
- `LEARN.shape.play()` and Play rest on step 0 before the first move (1.5 s at Normal).
- `state().sentence` is the one play sentence while a play from end to end is under way.
- `state()` returns more: `three.paneLevels`, `gone`, `thin`, `thick`, `above`, `where`. `diamonds` is `null` for
  a diamond that is out of its picture in 3D too.
- `out2` multiplies for the whole powers 2 to 8 (before: always the polar form).
- The 3D picture opens at yaw -0.62, pitch 0.9 (a constant of its own), not at the values of `LEARN_V_VIEWS.s3`.
- "At zoom 1 the big circle fills 84 % of the smaller side" is 76 % for two pictures smaller than 260 px.
- The sentences, helps, note and named values differ from the round's examples as listed in section 3.
- A visible word "Shape" stands before the row of shapes in the transport.
- One point's place (step, move, how far) is kept by 67 while the whole shape is on, and put back on return when
  the space is the same again.

Still true from the joiner's report: the page asks for 'move' at every change of a 3D picture and for 'still'
180 ms later; the module may start a 'still' picture one or two steps coarser and comes back up; the page listens
for the two graphics events; `mask2` and `slice()` put their outer points on the edge of the square (`centres:
true` for cell centres); "thrown out" is asked as x*x + y*y > 4; `colours.warn` is the token `--bad`; a level may
carry `ghost`; `o.flat` is always false; `set({ on: true })` also switches Learn on and never starts the play by
itself; the whole shape has a c of its own; the 1D choice is hidden by the style sheet; alpha is a strength, not
a literal opacity; `draw()` returns before the card has finished; a program is built at the first draw of its
approach; `slice()` gives null without a program; `dispose()` removes the canvas; of more than three levels the
three strongest are drawn.

## 9. Files in this folder

- Driver: `frun.py` (`go`, `a`, `sheet`, `build`), `f_prelude.js`, `final.sh`, `smoke_fix.py`, `compare.py`,
  `pairs.py`.
- My lists: `defects.js`, `defects_phone.js`, `panel.js`, `more.js`, `thick.js`, `motion.js`, `builds.js`,
  `trylook.js` (the M2 trial; it needs a hook that is no longer in the page).
- Before and after: `before*.log`, `after*.log`, `before-*.png`, `after-*.png`, and the 18 pairs `pair-*.png`.
- Sheets: `sheet-steps-dark.png`, `sheet-steps-light.png` (a 3D step place by place), `sheet-trylook-*.png`.
- Runs of others' lists: `checkb-*`, `a-after-*`, `join-*`, `core-*`, `three-*.log`, `smoke-fix.log`, `smoke/`.
- Timings: `checkb-t7*-feel*.log`, `join-pace.log`, `join-stall*.log`, `join-play.log`, `builds-*.log`,
  `longframes*.log` (list `longframes.js`).
- About 100 logs, 830 pictures here and 54 in `smoke/`.
