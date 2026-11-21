# Round 27, checker "eyes" (Track A): Balls on balls as the user meets it

Page checked: `dist/r27-checkb.html`, built by me with the command in `out/r27/entry/BUILD.txt` (886980 bytes, the same
size as the builder's `dist/r27-entry.html`). Frozen page for comparison: `dist/r27-checkb-base.html`
(`build.py --name r27-checkb-base --base base18a`). Everything was driven through `tools/shot.py`; 28 runs, every one
ended with "no console errors" and exit 0. Windows: 1400x950 and 390x800, dark and light. Clicks, slider moves and typed
values were made by script (events on the page's own controls), not by a real mouse or finger.

## In plain lines

- The object is there and it looks like round 25's picture: a chain of balls with smaller balls all over, four-fold
  end-on with the square grid, six-fold with the honeycomb grid, and a chain of circles in the 2D view.
- Both ways in work: one click on the row in the open Approach list, or Kleinian and then the choice "Balls on balls".
- The three dials do what their labels say between their ends. At the two ends the picture surprises (see 3).
- No forbidden word and no false claim about c = -1 or a basilica on the screen. One untrue sentence does appear (the
  "Three tones" sentence, see 5).
- Going back (a real approach, Julia, the old Kleinian group, Mandelbrot again) gives the frozen page's pictures, 0
  pixels different.
- What a user would stumble over: after the click in a wide window the dials are scrolled out of sight; on the phone the
  Approach list has shrunk to one and a half rows; the Examples list throws the user out of the object without a word;
  the scorecard under the picture belongs to another entry.

## 1. Finding it

- From the lab as it opens: click the Approach button (the list opens), then click the row. The row "Balls on balls /
  a cousin of the flat picture: no c, no power" stands under the heading "A COUSIN, NOT A RULE" at the foot of the open
  list and is inside the window without scrolling the list, wide and phone (`shots/s1-wd-1-menu-open.png`,
  `shots/s1-pl-1-menu-open.png`). One click on it gives the Kleinian view, the group and the framed camera; finished
  picture 1016 to 1021 ms after the click (wide), 764 ms (phone).
- From Kleinian: the choice "Group" stands at the top of the panel, "Pearls between two walls" (chosen) and "Balls on
  balls" (`shots/s2-wd-0-kleinian-old.png`); one click, picture after 1014 ms (`shots/s2-wd-2-after-choice-panel.png`).
- DEFECT A (wide window). Right after the click on the row, with no scrolling by the script, the window shows the
  picture with its top 175 pixels cut off, the button "APPROACH: Balls on balls", the closed sections and then the
  scorecard of "Sphere inversions, one plane". The choice of group, the note and the three dials are above the window
  (measured tops: choice -568, note -461, size dial -328). `shots/s11-wd-1-right-after-the-row.png`,
  log `logs/s11-land-wd.txt`. On the phone the same click lands on the size dial; the choice and the note are hidden
  under the pinned picture (`shots/s11-pl-1-right-after-the-row.png`).
- DEFECT B (phone). The open Approach list shows one whole approach and half of the next; the frozen page shows four.
  The list's own height went from 170 to 89 pixels (21 approaches scroll in it).
  `shots/s7-pl-pair-9-menu-new-left-base-right.png` (new page left, frozen page right).
- DEFECT K (wide, pointer events made by script). With the pointer on the row, the explanation box beside the list
  keeps the text of the last approach the pointer crossed, for example "Mandelbulb, classic ... the one approach whose
  z = 0 slice is not the flat set". `shots/s9-wd-hover-on-balls-row.png`.

## 2. Does the first picture look like the object?

Yes. Start view, front, above, end-on from both ends, 2D view: `shots/s2-wd-3-first-stage.png`, `s2-wd-4-front.png`,
`s2-wd-5-above.png`, `s2-wd-6-end-on.png`, `s2-wd-7-end-on-other.png`, `s2-wd-8-flat-window.png`; the same on the phone
and in the light theme (`shots/sheet-s1s2-pd.png`, `shots/sheet-s1s2-wl.png`). Beside `out/r25/klein/tree-big.png`: the
same three big balls with a small one at each end, a bud on top and below, buds of every size on every ball; end-on
four-fold. The lab's picture is coloured by the orbit trap, the reference is plain.

Seen and not counted as defects: from the front and from above the middle ball reads as a rounded box, because the buds
crowd round each kiss (enlarged: `shots/s2-wd-4-front-zoom-left.png`; the balls themselves are round and do kiss). In the
2D view the colours outside the object show straight-edged bands and one large arc on the left only; the first Kleinian
group's 2D view has smooth, mirror-symmetric bands (`shots/sheet-s7-old-group.png`).

## 3. The dials

All stops: `shots/sheet-s3-wd-size-1.png`, `-size-2.png`, `-size-3.png`, `sheet-s3-wd-grid.png`,
`sheet-s3-wd-depth-3d.png`, `sheet-s3-wd-depth-flat.png`, `sheet-s3-wd-corner.png`, phone `sheet-s3-pl.png`.
Slowest change of a dial in the three runs (wide dark, wide light, phone light): 602 ms (neighbours 100, square grid,
depth 40). Nothing went empty. Grain was seen only at 100 (defect F).

- Size of the neighbours (slider 10 to 100, typed 2 to 100; stops 2, 10, 30, 55.56, 80, 95, 100): the neighbours grow
  and the chain gets longer, as the help says. At 80, 95 and 100 the chain runs out of the picture until "Frame it" is
  pressed; Frame it then shows it whole (at 100 a stretch of it). Typed 1, 0, -5 give 2; 150 gives 100; letters are
  refused.
- DEFECT F. At 100 with the square or the honeycomb grid no ball can be seen any more: the picture is a square
  (honeycomb: six-sided) bar with round holes, with a grainy skin (`shots/s3-wd-size-100-b-framed.png`,
  `shots/s3-wd-size-100-c-flat.png`). The help says "At 100 they are as big as the middle ball and the chain never
  ends." With "A line only" the same stop does show a row of equal balls (`shots/s3-wd-corner-100-line-200.png`). The bar
  is the object, not a fault of the depth: with the page's own inside test, 98 of 20000 random points of the start box
  change their verdict between 16 and 400 rounds (10 between 40 and 400). The warning "The chain of balls runs out past
  the Drawing radius in the View section, so its far ends are not drawn." stays whatever the user does, Frame it
  included (`shots/s4-wd-3-warning.png`).
- Whole numbers (three stops): square four-fold, honeycomb six-fold, a line only with buds only round the flat
  picture; the three 2D views are the same picture. As the help says.
- Depth of the search (slider 2 to 40, typed 1 to 200; stops 1, 2, 3, 4, 5, 6, 8, 16, 28, 40, 200): from 5 upward I
  see no change in the start view.
- DEFECT G. At the slider's lowest stops the picture looks broken, not "swollen": at 2 cut-open shells with saw-tooth
  edges fill the left half (`shots/s3-wd-depth-02-a-3d.png`), at 3 the left neighbour is a spiky lump, at typed 1 half
  the picture is one wall (`shots/sheet-s3-wd-depth-3d.png`, `shots/sheet-s8-depth-low.png`).
- DEFECT H. "Raise it when you zoom far in": at the starting size I found no place where it matters. Inside test, 16
  rounds against 400: 0 of 20000 points differ in each of five boxes (the start box, three boxes round the kiss of the
  chain down to half-width 0.0002, one beside the bud on top); even 8 rounds differ in none. Pictures at 16, 40 and 200
  rounds zoomed in on a kiss look the same (`shots/sheet-s8-zoom3d-c.png`). The depth matters near size 100 instead
  (numbers above), which the help does not say. Log: `logs/s10-warn-depth-wd.txt`.

## 4. The words

Every new text on the screen (read from the page, `logs/s4-words-wd.txt`): "A cousin, not a rule"; "Balls on balls";
"a cousin of the flat picture: no c, no power"; tooltip "Shows this object in the Kleinian view, where its dials are.";
"Group"; "Pearls between two walls"; the note "Made only of slides by whole numbers and sphere inversions, so every body
is an exact ball. It is a cousin of the flat picture: its flat cut is a chain of circles. It has no c and no power.";
"Size of the neighbours, % of the middle ball" with "How wide the two big neighbours are, next to the middle ball. At
100 they are as big as the middle ball and the chain never ends. Smaller neighbours give a shorter chain."; "Whole
numbers" with "Square grid (four-fold)", "Honeycomb grid (six-fold)", "A line only (buds only round the flat picture)"
and "The slides go by the whole numbers of this grid. The square grid sets the buds four-fold round the chain, the
honeycomb grid six-fold. With a line only, buds grow only round the flat picture. All three have the same flat cut.";
"Depth of the search" with "How many rounds of the recipe a point may take: a slide, then a sphere inversion. A point
that is still undecided after that counts as inside, so with too few rounds the balls look swollen. Raise it when you
zoom far in."; "Frame it" with tooltip "Move the camera to a view that shows the whole chain. Nothing else changes.";
the warning quoted in 3; "Balls on balls has no trap solid: in this view the trap only colours the balls."; in the saved
model "Made from: Balls on balls (slides by whole numbers and sphere inversions), neighbours 55.56 % of the middle ball
(t = 1.4), square grid, depth of search 16."

- Forbidden words of section 4: none found (searched by script and read by me). No "pearl tree", no "basilica", no
  claim for c = -1 or a rabbit.
- DEFECT L. The helps are three, four and three sentences; decision 5 asks for one sentence each, and the builder's
  report says "one-sentence help". "The slides go by the whole numbers of this grid." cannot be followed by someone
  who does not know the recipe: nothing on the screen says what a slide is.
- DEFECT M. "(t = 1.4)" in the saved model's readme.txt and in the first line of the OBJ file: t is a letter the page
  never shows (`logs/s8-extra-wd.txt`, step 5).
- DEFECT N. "Nothing else changes." (Frame it): with the Drawing radius at 1 a press moved it to 1.69, and with the
  farthest zoom at 2 it moved that to 3.76 (`logs/s8-extra-wd.txt`, steps 111 and 113). Helpful, but not what the
  sentence says.
- Remarks: under the label "APPROACH" the button reads "Balls on balls" while the list calls it "not a rule". The old
  group has a new name, "Pearls between two walls", and one of its examples is called "Pearls and balls".

## 5. Everything decision 7 lists, tried in Balls on balls

| thing | result |
| --- | --- |
| 2D view | works (`shots/sheet-s5a-f1f2.png`) |
| height of the slice | works: circles shrink with height, +0.3 and -0.3 look the same, label "(slice at z = 0.3)" follows |
| cut the solid open, painted cut face | works |
| colour by, 7 choices, 3D and 2D | all draw; one washed out (defect I) |
| inside colours, 5 choices | all draw; one not symmetric (defect J) |
| trap shapes (8), trap colours by (6) | all draw, each different (`shots/sheet-s5a-f4f5.png`) |
| trap solids | switched off with its sentence, thickness and skipped-steps dials hidden, plain balls drawn; but a second, untrue sentence appears (defect C) |
| picture export | works: squaring-lab-kleinian-862x701.png, 1007 kB, shows the object (`shots/s5b-wd-f8-exported-picture.png`) |
| 3D model export | works at 96 cells: 31,976 triangles, 1 piece, 100 x 61.7 x 61.7 mm, zip 3.4 MB (`shots/s5b-wd-f9-model-section.png`); the files were not opened in another program |
| scorecard | shows another entry's card, no sentence (defect E) |
| camera start view, Reset view (3D and 2D), Frame it | work |
| Examples list | neither works nor is switched off (defect D) |
| "Start from" list | not shown in the new group |
| Reset this section | dials back to 55.56 / square / 16; the camera stays where it was |
| Reset everything | back to Mandelbrot, first group, dial defaults |
| Learn | goes on and off; Kleinian afterwards brings Balls on balls back; differs from the first group in one point (defect O) |
| old group's warnings | silent in the new group, back when the old group is chosen again (`logs/s10-warn-depth-wd.txt`) |

- DEFECT C. With any trap shape other than "Three tones" (seen with "Sphere shell") and "In the 3D view the trap" set
  to "Is the solid" or "Is added to the solid", two sentences stand under the Examples list: "Balls on balls has no trap
  solid: in this view the trap only colours the balls." and "Three tones has no shape of its own, so no solid can be
  made from it. Pick another trap shape." The second is not true here. `shots/s5a-wd-f6-solid-is-the-solid-section.png`.
- DEFECT D. The Examples list ("Trap solids that came out well in testing...") stays in the Colour section. Choosing
  "Pearls and balls" from Balls on balls switches to the first group with no word about it
  (`shots/s5a-wd-f7-examples-list.png`, `shots/s5a-wd-f7-after-kleinian-example.png`); a Mandelbrot or Julia example
  leaves the Kleinian view. Afterwards "Is the solid" is still set when the user comes back.
- DEFECT E. Under the picture of Balls on balls the page shows "What survives the move to 3D" for "SPHERE INVERSIONS,
  ONE PLANE", with the row "Contains the flat set: HOLDS ... that slice is the flat set"
  (`shots/s5b-wd-f10-scorecard-area.png`). The same card stands under the first Kleinian group (measured: identical
  texts), so nothing changed; but here the Approach button above it reads "Balls on balls", and after the click of
  defect A it is the first thing under the picture.
- DEFECT I. Colour by "Direction of the last step" paints the whole object one pale pink in the 3D view
  (`shots/s5a-wd-f3-3d-4-laststep.png`); the first group gets a clear pattern from the same choice
  (`shots/sheet-s7-old-group.png`). The lab's sentence for this case ("...looks speckled. It is at its best in the 2D
  view...") is not shown in the Kleinian view.
- DEFECT J. Inside colours by orbit trap, 2D view: the two neighbours of equal size come out in different colours, left
  pink and red, right yellow and green (`shots/s5a-wd-f4-inside-1-trap.png`). The sentence that says so for the first
  group is switched off for the new one.
- DEFECT O. Under Learn the Approach section is hidden when the first Kleinian group is behind (frozen page: the same)
  and shown when Balls on balls is behind (`logs/s5b-feat-wd.txt` steps 32 and 34, `shots/s5b-wd-f12-learn-menu.png`).

## 6. Layout

Boxes of the 17 new pieces measured in all four windows: none outside the window, none with cut-off text, no two
overlapping, page never wider than the window (`logs/s4-words-*.txt`). Looked at: `shots/sheet-s4-wd-panel.png`,
`shots/sheet-s4-pl-panel.png`, and the light wide and dark phone sheets. Defects of layout are A and B above. Small: in
the wide list the last visible approach row is cut in half by the heading "A cousin, not a rule".

## 7. Going back

New page: into Balls on balls by its row, neighbours 80, honeycomb, depth 30, Frame it, camera turned; then the approach
"Blended planes" from the open list, Julia, Kleinian, the first group, its 2D view, a colouring, Learn, Mandelbrot with the
first approach. Frozen page: the same places directly. `logs/s7-back-*.txt`, `logs/s7-base-*.txt`, compared by
`cmp_back.py`.

- State (camera, view limits, 2D frame, colours, quality, the first group's numbers, which sections are shown): the
  same in every place, wide and phone.
- Pictures (the stage alone): 0 pixels differ in all seven places, wide and phone, once both pages had been scrolled
  the same way. Before that, three places showed 2501 differing pixels, all in the hint text and the camera buttons
  shifted by one pixel; the frozen page shows the same shift against itself after one scroll, so it comes from the
  test, not from the page (`logs/s7-base-scrolled-*.txt`).
- The Kleinian button after an approach and Julia brings Balls on balls back with the dials as they were left. From
  Julia by the Kleinian button into Balls on balls, an approach leads back to Julia; from the row, back to where the
  row was chosen. The arrows beside the Approach button go from Balls on balls to the first or the last approach and
  never arrive at it.
- First picture of the first group on the frozen page 1144 ms (wide), 916 ms (phone); of the new group about 1015 ms
  and 764 ms.

## Not checked

A real mouse, a finger, the keyboard path to the row; the fly camera; Extreme ranges; the Fine, Fast and Ultra fast
settings; picture export larger than the screen or at Fine; models above 96 cells and opening a saved model elsewhere;
palettes and the band dials; each of the features in the light wide and dark phone windows (features were run wide dark
and phone light); other window sizes; a slow graphics card; the published host; the shader against tree.py, the list of
twelve unchanged states and the smoke lists (another checker's part); Learn with round 26's files in the page; whether
a black picture with the camera inside a ball is the same as for the lab's other solids (seen at two zooms, not
compared).

## Files

`drive.py` runs a steps file for the chosen windows; `gen_dials.py`, `gen_words.py`, `gen_feat.py`, `gen_back.py`,
`gen_extra.py` write the steps; `read_words.py`, `read_log.py`, `cmp_back.py` read the logs; `contact.py` puts pictures
side by side. Steps in `steps/`, logs in `logs/`, 618 pictures in `shots/` (the sheets start with `sheet-`).
