# Round 26, the final look: notes

Everything here was run by me on `dist/r26-final.html`, built at 06:00 on 2026-11-20 with
`python build.py --name r26-final` from `src/` as it stood (md5 `8ebc92be894d155cf2e236362e71ad6b`, 985,895 bytes:
byte for byte the fixer's `dist/r26-fix.html`). I changed no file under `src/`. Nothing was published.
`squaring-lab.html` is untouched (md5 `661807c8e289fec844284e01f2b1e4b6` before and after). Nothing was written
outside `out/r26/final/` and `dist/r26-final.html`.

My lists are my own (`defects.js`, `spot.js`, `plays.js`, `point.js`, `phone.js`, `use.js`, `more.js`, `extra.js`,
`strips.js`, `strips_both.js`), driven by `run_final.py` with `p_prelude.js`. I did not rerun the checkers' or
the fixer's scripts: their runs on `r26-fix.html` hold for this build, since the two files are the same bytes.
15 logs, every one ends "no console errors" and "exit code 0".

## 1. The old smoke list of Version 18

`out/r22/entry/smoke-all-steps.json` (90 steps: the 62 of `tools/smoke-v14.json`, round 20's 5, round 22's 20 + 3;
the list logged in `out/r22/entry/smoke-all.log`, "PUBLISHED: Version 18" in `notes/_state.md`).

- `smoke-final.log` (driver `smoke_final.py`, 326 s): **90 of 90 steps give their result, no time-out, no console
  error, exit 0.**
- 87 result lines are word for word those of the Version 18 run. The other three: step 2 and step 24 carry a
  number that depends on the clock (a zoom caught in mid-ease 5.279 for 5.423; a fly camera's path 0.699 for
  0.690), step 7 counts the controls (76 dials and 25 selects for 73 and 24: the three c dials and the Speed select
  of the whole shape).
- Pictures the steps took: `smoke/` (54).

## 2. Each defect of the list, looked for again

Lists `defects.js` (dark: `d-dark.log`, light: `d-light.log`; the two logs agree in every field that is not a
timing), `phone.js`, `more.js`, `plays.js`. "Picture" = a file `d-dark-*.png` unless it says otherwise.

| id | gone? | what I saw on the final build |
|---|---|---|
| A1 | yes | Power dial at 1, Julia shape, 3D: "After 8 steps nothing is left to see: every point of the picture has been thrown out." (and at 9, 12, 16), the picture empty from step 9 (0 % not stage colour); a 0.1 grid of the ball keeps 740 points at step 7, 1 at step 8, 0 from step 9. The 2D page says the same at step 12. c = (7, 0, 0): "After 1 step nothing is left ..." (`A1-power1-3d-j-12.png`, `A1-c7-3d-j-02.png`). Still open: zoomed in to 2.05 the same empty picture gets "What is left after 2 steps." (`A1-zoomed-2-empty-3d.png`). |
| A2 | yes | "Quaternions, 4D (slices)". w = 0: 17,077 of 17,077 grid points left after step 1, words "the whole big ball is still there". w = 0.3: 16,663 left, words "What is left after 1 step." and "Step 1: every point ... are thrown out". w = 1.5: 4,945 left, same true words; Julia at the start "the shape begins smaller" (4,945 of 17,077 start inside). The Mandelbrot shape at the start is the whole ball for w = 1.5 too (17,077 of 17,077), as its sentence says (`more-dark.log` step 6). |
| A3 | yes | `out2([-2, 0])` = 17 and `mask2` = 17 (41 and 41 with 40 steps). See also section 3. |
| A4 | yes | One point at step 1, move 1, 0.4; whole shape, 3D, 2D, back: step 1, move 1, 0.4, z and c the same. Ending in 3D starts afresh in 3D (as designed). |
| A5 | yes | c = (-1.8, 0.9, 0), zoom 6: neither diamond nor letter (`A5-3d-zoomed-lone-c.png`); back at zoom 1 both are there. |
| E1 | yes | 3D, step 1 held at 0.4 and at 0.8: the Mandelbrot ball is asked as one brass skin; on the screenshot 0.0 % of the picture is in the warning colour, 35.3 % in the body colour. Both: left picture 0.0 % warning, right picture 14.0 % (a red peel round a brass body) (`E1-3d-m-00.4.png`, `E1-3d-both-00.4.png`, `red-share.txt`). Same in light (`look-light-3d.png`). |
| W1 | yes | The first play rests on the start: at 500 ms the page still says "The big circle: every point no further than 2 from the centre. Each point is tried as the number c; its dot starts at the centre."; first move at 1,536 ms (dark), 1,551 ms (light); 1,518 to 1,534 ms in twelve more plays. |
| W2 | yes, by my reading | The note now says what a step is ("A step is the lab's rule: square, then add c."), the helps say "tried as the number c, the one that is added at every step" and "The number c is the same for all: the diamond." The full words as read from the page: `d-dark.log` step 8. None of the fifteen forbidden words in 25,343 letters of panel, transport, hints, tooltips and labels, 2D and 3D. |
| E2 | yes | Step 3 at 0.4: the body brass at full strength, the part that goes a red glass peel round it (3.2 % of the picture warning colour, 9.1 % body colour); step 7 at 0.4: 0.1 % and 5.3 %; step 10 at 0.4: 0.0 % and 4.4 %, so the late lump no longer blinks red (`E2-3d-m-02.4.png`, `-06.4`, `-09.4`). |
| M1 | by the sentence only | In a play the sentence "The bites are now too fine to see at this size. Zoom in." comes at step 8 and stays 11.7 of 24.7 s; by hand at 12.4: "Step 13: this bite is too fine to see at this size. Zoom in." Zoomed in 6 times the plain sentence is back and the red bite shows along the rim (`more-dark-1-2d-m-12.4-zoomed.png`). The picture itself still stands still for the second half of a play. |
| M2 | partly | At step 16 "Turning plane, along" and "Sphere inversions, two planes" are rough gold lumps: one sees a body with strands and a crease, not what it is made of (`M2-turnalong-16.png`, `M2-fold-16.png`). The Lathe's rings, the Mandelbulb and the opening approach read (`look-M2-row.png`). I held the lab's own solid of the same two rules beside them (`look-more-b.png`): it is ragged and layered in the same way, so most of the roughness is the rule's own; the whole shape's picture is grainier on top of that. |
| M3 | yes | "Start again" in 3D: tooltip "Back to the big ball". |
| M4 | yes | 3D with a diamond: "Drag to turn, scroll or pinch to zoom. Move c with its dials." |
| M5 | yes | The word "Shape" stands before the row. On the phone the lab's own tabs begin 171 px below the row. |
| M6 | partly | Phone, Both: labels and "Unpin picture" stand clear of the two circles (circle top at y = 379, button and labels end above it), but "Unpin picture" still lies over the top right corner of the right picture (`look-phone-dark-a.png`). |
| M7 | partly | Phone: 2D and 3D 44 x 40 px, Play 125 x 40, step buttons 40 x 40. Tick numbers 16 x 18 and Speed 73 x 23, as before. |
| M8 | yes | The figures 1 and -1 stand to the right of the upright axis, off the tips (`2d-m-16-whole-window.png`). |
| M9 | yes | The right picture is named "Julia shape for the diamond's c" (on the phone "Julia": no room). |
| M10 | yes | A play shows 4 sentences (16 plays, each 4). Label "Step 3 of 16: under way". Lines at 1400 wide: 755 + 145 px and 742 + 85 px, no single short word alone. |
| M11 | partly | 3D opens at pitch 0.9: the shape is seen from above. The step-16 shape is as small as before (about a quarter of the stage's width). |
| M12 | yes | "Slice this 3D shape level through its middle, where the dotted ring runs, and the cut is exactly the 2D picture of the same step."; named values "the basilica (c at x −1, y 0)", "the rabbit (c at x −0.12, y 0.74)", "a bare twig (c at x 0, y 1)", "a plain disc (c at x 0, y 0)". |
| M13 | not seen | 14 plays at 1400 x 950 (dark and light) and 2 on the phone: no gap between frames over 34 ms in any of them (worst 23.8 ms); the card needed 6.7 to 9.1 ms a 3D picture in the middle, 8.4 to 10.2 ms at the 95th of 100, worst single picture 39.8 ms. |

The fixer's open points, as I found them: the pale patch on the flat top (seen, section 5); deep 3D bodies solid
instead of glass (seen: `M11-3d-m-16.png`, the body is asked with `solid` 0.50 at step 8 and 1.00 at step 16);
"nothing is left" not said beyond zoom 1.5 (seen, A1 above). The costs of building and of `columns()` I did not
measure again.

Small things of my own finding, none of them a blocker:
- When a 3D shape has just gone, the grey ghost of the shape before is still drawn under "nothing is left to see"
  (`more-dark-6-quat4-w1.5-j-01.png`: a grey ball, 13 % of the picture; power 1 at step 8: 1.6 %).
- "Step 1: every point that is still here takes one more step" is said of the very first step of a Julia shape,
  before any step has been taken.
- Zoomed in to 4.6 in 3D the highlight on the opening approach's body is a large white blot
  (`more-dark-2-3d-m-12.4-zoomed.png`).
- `d-dark-M1-2d-m-12.4-zoomed.png` and its light twin are wrongly named: my list put the view back before the
  picture was taken, so they show the unzoomed picture. The zoomed one is `more-dark-1-2d-m-12.4-zoomed.png`.
- My in-page counter of warning-coloured pixels (`look3().red` in the logs) never fired and proves nothing; the
  shares above were counted on the screenshots (`red-share.txt`).

## 3. Spot checks of my own

- **mask2 against out2** (`spot.log` step 2): 257 x 257 points, 16 steps, eleven cases (power 2: Mandelbrot shape,
  Julia shape of the rabbit and of c = -1; power 3; power 2.5; power 2 with |x|; power -2): **0 of 66,049 differ in
  every case.** At one step, shape 5: 11,468 points by both for the Mandelbrot shape, 9,379 by both for the rabbit.
- **slice against out** (`spot.log` step 3): 129 x 129 points at z = 0.3 and z = -0.7, both kinds (Julia c off the
  flat plane), for "Sphere inversions, one plane", "Turning plane, along", "Pulled plane" and "Mandelbulb":
  **15 of 266,256 differ, every one within 1e-4 of a skin** (0 not on a skin).
- **The cut at z = 0 against the flat picture** (`spot.log` step 4): one plane, along, Mandelbulb: 0 of 66,049 for
  the Mandelbrot shape, 4 of 66,049 for the Julia shape of c = -1; the page shows the cut sentence for all three.
- **Full plays from step 0 with the Play button** (`plays-dark.log`, `plays-light.log`): 2D and 3D, Mandelbrot
  shape, Julia shape and Both, six plays in each theme. Each: 24.6 to 24.7 s, first move after 1.52 to 1.53 s,
  15 rests of 348 to 369 ms (none skipped), 4 sentences, the 3D picture in sight in every frame, no console error.
- **Follow = One point against the frozen page** (`point-base.log` on `dist/r26-base.html`, `point-final.log`,
  `point-compare.txt`): three states (2D as it opens at move 2, 0.4; 3D "Turning plane, along" at step 3, move 3,
  0.6; the 1D line at power 3): stage 864 x 513 and transport 864 x 178, **0 pixels differ in all six pictures**,
  and the state the handle gives is word for word the same.
- **Phone, 390 x 800** (`phone-dark.log`, `phone-light.log`): page width 390, no sideways scroll; stage 358 x 242
  and transport 222 high end at y = 799 of 800; 48 sentences, none over three lines; a scripted pinch zooms a flat
  picture 1 to 3.13; a whole 3D play of Both: 24.5 to 24.6 s, no gap over 34 ms. Pictures looked at:
  `look-phone-dark-a.png`, `look-phone-dark-b.png`, `look-phone-light.png`.
- **Light theme**: the whole defect list again (`d-light.log`), six plays, the phone list. Pictures looked at:
  `look-light-3d.png`, `look-light-2d.png`.
- **Using it** (`use-dark.log`, `extra-dark.log`, `more-dark.log` step 12): the first switch plays by itself, the
  second does not; with reduced motion asked for it does not play and the one-step button jumps; space bar, plus,
  arrows; the diamond dragged (c follows and the right picture changes while the button is down); a 3D drag;
  leaving for the Julia tab in mid-play and coming back (stopped, place kept); the theme switched under a 3D
  picture; "Reset everything" and the panel's "Reset this section" (both: Follow = One point, inside it the
  Mandelbrot shape, 2D, step 0, c as Learn opens); from the 1D line the space becomes 2D and the 1D choice is put
  away; the stage made narrow and wide; "Use the c of the Julia tab"; power 3 (the note says "take to the power
  3", the names of the named values go); Play at the end starts again; ten quick changes of approach, shape,
  space, speed and slider during a 3D play; c lifted off the plane (the cut sentence is taken back for Both and
  kept for the Mandelbrot shape). No 3D canvas is made before 3D is first asked for.

## 4. `src/` against `base18a/`

`diff -r base18a src` (kept as `src-against-base18a.diff`): 0 lines removed, 10 added, three files new.

- `src/css/67-learn-shape.css`: new
- `src/js/67-learn-shape.js`: new
- `src/js/68-learn-shape3d.js`: new
- `src/js/66-learn-view.js`: 7 lines added, none changed: the field `follow`, and six hand-overs each behind
  `typeof ... === 'function'` (draw, paint, defaults, set on, wheel, init).
- `src/js/90-boot.js`: 3 lines added (two of comment): `learnShape3d` is put on `window.squaringLab`.

Beyond what the feature needs: nothing in 66. The line in 90-boot serves test scripts only (the page reaches the
module by its own name); it is the line section 3 of the round names.

## 5. The pictures for the user

Each is made of screenshots of the stage of the real page (clip `#stage`; `strips.js` at 1100 x 1000,
`strips_both.js` at 1400 x 950, dark theme, the opening approach, power 2), cut 30 px (33 for the pairs) at the
bottom just above the hint line, set side by side by `make_strips.py`. Nothing is drawn into a screenshot. The six
of pictures 1 and 2 are set three to a row, in reading order, not six in one line.

1. `user-c-both-rabbit-2d.png` (best: it answers the wish for a Julia option beside the Mandelbrot shape). Reads at
   once. At step 16 the diamond covers a little of the top bulb on the left and of the rabbit's middle on the right.
2. `user-a-circle-to-mandelbrot-2d.png`. Reads at once. The first two pictures are the same disc, which is the truth
   (the first step throws out none) and the words under it say so.
3. `user-d-julia-ball-3d.png`. The best-looking 3D one: a ball, a lens in grey glass, a folded body, a row of beads.
   The beads of step 16 are solid gold, not glass.
4. `user-b-ball-to-mandelbrot-3d.png`. Steps 0 to 5 read. **Step 16 is the weak picture: a small flat gold piece with a
   pale patch that has a straight edge across its top.** Turned to the side the patch is gone and the body is a
   low dome over a flat rim (`look-more-a.png`), so it is a highlight, not a face; but in the opening view it looks
   like a flaw. The ball at the start is a shaded gold ball; that it is see-through shows only from step 2, when
   something is inside it.

## 6. Verdict

**Ready to be shown.** Smoke 90 of 90; One point untouched to the pixel; every play runs to its end in both
themes and at both sizes without a console error; the arithmetic agrees; the three defects called major (E1, W1,
W2) are gone.

Left, for the lead to weigh:
1. The second half of a play (11.7 of 24.7 s) shows a still picture under "The bites are now too fine to see at
   this size. Zoom in." (M1, cured by words only).
2. From about step 8 a 3D body is solid gold, not glass; the user asked for a see-through shaded ball. Steps 0 to
   5 are glass.
3. The pale straight-edged highlight on the opening approach's 3D shape at late steps, in the view the page opens
   with (user picture b).
4. "Turning plane, along" and "two planes" at step 16 are rough lumps (mostly the rule's own).
5. M6, M7, M11 partly cured, as in the table; "nothing is left" not said beyond zoom 1.5; the ghost under
   "nothing is left to see"; "one more step" said of a Julia shape's first step.

## 7. Not run

A real phone, a finger, Safari, Firefox, a sharp screen; a coarse pointer (this headless Chrome reports none);
the page without the 3D module; the graphics taken away and given back; the checkers' and the fixer's own
scripts on this build (same bytes as the build they ran on); the cost of building a 3D program.

## 8. Files in this folder

- Drivers: `run_final.py`, `p_prelude.js`, `smoke_final.py`, `compare_point.py`, `make_strips.py`, `readlog.py`.
- Lists: `defects.js`, `spot.js`, `plays.js`, `point.js`, `phone.js`, `use.js`, `more.js`, `extra.js`,
  `strips.js`, `strips_both.js`.
- Logs: `smoke-final.log`, `d-dark.log`, `d-light.log`, `spot.log`, `plays-dark.log`, `plays-light.log`,
  `point-base.log`, `point-final.log`, `phone-dark.log`, `phone-light.log`, `use-dark.log`, `more-dark.log`,
  `extra-dark.log`, `strips-single.log`, `strips-both.log`; `point-compare.txt`, `red-share.txt`,
  `src-against-base18a.diff`.
- Pictures: the four for the user (`user-a-` to `user-d-`, the letters of the task), their screenshots in `strip/`, `d-dark-*`, `d-light-*`,
  `phone-*`, `use-dark-*`, `more-dark-*`, `extra-dark-*`, `plays-*`, `point-*`, the sheets `look-*.png`, `smoke/`.
