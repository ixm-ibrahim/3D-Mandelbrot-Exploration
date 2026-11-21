# Round 22, section "entrycheck", second pass: the repaired page dist/r22-entry.html, checked from scratch

2026-11-19, 16:13 to about 17:00. I wrote none of the code and did not edit `src/`. Every statement is marked
**measured** (a number I computed), **seen** (a picture I opened) or **reasoned**. Paths are relative to the project
root; everything of mine is in `out/r22/entrycheck2/`. Test pages I built: `dist/r22-entrycheck2.html`,
`dist/r22-entrycheck2-base.html`.

## 0. Verdict: fix first (three sentences), then ship

The seven earlier defects are gone, six of them outright and one (the c out of the flat plane) by the text cure that
was asked for. The program is right: lab = library point for point, in JavaScript and in the shader; the Learn tab now
follows the library's orbit; the five untouched entries draw the same pixels as base17a; 90 of 90 smoke steps pass;
nothing broke in my break attempts or at phone size.

What is left is three sentences a user will read that are not true as they stand. One was written in this second
pass, two are from the first pass and were on the first checker's "not checked" list. All are text in
`src/js/10-approaches.js`; nothing that draws needs touching.

| # | severity | what |
|---|---|---|
| A | minor | Pulled plane, note and About: the example "c = (−1, 0, 0.3): a thin branching thread, where 66 of 400,000 stayed" is offered as a picture of "what is not there". It is there. It is the flat picture of c = −1 + 0.3i standing in the plane y = 0. |
| B | minor | Pulled plane, help of the second dial: "at 1 a third of the set is lost". With the lab's other dials where they start, 8 % is lost. |
| C | minor | Pulled plane, About: "For c = −1 + 0.2i nothing is left in the plane y = 0". The body still crosses that plane; what is gone are the buds there. |

Still drawn, as the builder says (not cured, now said in the texts): the shards of Along once for a c out of the flat
plane (section 5).

## 1. The page is the build of the current src (measured)

- `build.py --name r22-entrycheck2 --base base17a --use` the six changed files: byte-identical to `dist/r22-entry.html`
  (checked again at the end of my work: still identical). `--name r22-entrycheck2-base --base base17a`: byte-identical
  to `dist/r22-base17a.html`.
- `diff -ru base17a/js src/js` (`my-changes.diff`): 564 lines, 308 added, 21 removed; the same hunks as the builder's
  `changes.diff`. Six files differ: 10-approaches, 30-shaders, 60-measure, 65-learn-steps, 66-learn-view, 90-boot.
  `80-ui.js`, `75-presets.js` and everything outside `js/` are base17a's.
- What the second pass changed (`pass1-to-pass2.diff`, my first-pass diff against my new one): no hunk of
  `30-shaders.js`; in `10-approaches.js` only `usesC: true`, the texts and the dial label. The GLSL of both entries
  and the orbit code are the first pass's, letter for letter.

## 2. Smoke (measured)

`e2_smoke.py` -> `smoke.log`: **90 steps ran, 90 results, exit 0, "no console errors"**, 290 s, 1400 x 950.
62 of `tools/smoke-v14.json`, 5 of round 20 (the one line about windsq's place changed, as before), 19 + 1 of the first
pass, 3 of the second pass. The steps are read from their files, not copied; pictures in `smoke/`.

## 3. Parity with my own script (measured; pictures seen)

`e2_parity_page.py` (page) and `e2_parity.py` (library): other start points, other c, other slices, other cameras
than the builder's and than the first checker's. Result in `parity.txt`.

- **A. JavaScript rule (L.CARRY) against the library**, 10,000 orbits, 50 steps, c = −1, rabbit, −0.75,
  (−0.3, 0.4, −0.25) and the Mandelbrot orbit, both entries: **0 verdicts and 0 stay counts differ in 100,000 orbits.**
- **B. Shader point by point** (sampleSlice), 18 level slices of 144 x 144: rabbit z = 0 and −0.18; c = −0.75 z = 0
  and 0.22; airplane z = 0 and 0.12; the off-plane c at z = 0.05; Mandelbrot z = 0 and −0.15; both entries:
  **0 of 373,248 points differ.** All eight cuts at z = 0 equal my own flat (complex) iteration: 0 differ
  (`parity-slices.png`, seen).
- **C. The 3D picture**, 36 x 27 probes, against the library on the same lines of sight (a test every 0.004):

| picture | lab stops | library | lab only | library only |
|---|---|---|---|---|
| Along once, c = −1 / rabbit | 138 / 165 | 138 / 162 | 0 / 3 | 0 / 0 |
| Along once, Mandelbrot | 148 | 119 | **29** (the wings) | 0 |
| Pulled plane, c = −1 / rabbit / Mandelbrot | 131 / 122 / 135 | 130 / 121 / 130 | 1 / 1 / 5 | 0 / 0 / 0 |

  The lab stops 0.8 to 1.5 px in front of the library's first point (median), stops lie at most 5.5e-7 off the lines
  (`parity-rays.png`, seen: the 29 are the arcs off the left end, the others single probes on the rim).
- **A power in the start value** (the new sentence of both notes), Mandelbrot from c², slice z = 0.12, 9,216 points
  (`break1.log`): shader against "the start value is taken by the flat one-plane square and not
  counted": 0 differ for both entries; against "counted as a first squaring": 14 and 58 differ. The sentence is true.

## 4. Untouched entries (measured)

`e2_untouched.py` -> `untouched.txt`. mercator, lathe, turnalong, windsq, bulb x four scenes of my own (Siegel disc
in 3D; Mandelbrot solid with the cut plane on; the 2D view for c = (−0.75, 0.1, 0.2); c = −1 with |x| ticked), the
stage as the page shows it: **0 of 12,147,840 pixels differ in 20 pictures** (largest difference 0 of 255). One of
the 2D pictures opened: a real picture, not blank (seen).
Because the second pass changed JavaScript only, also the words: the card in the Julia view, after c is moved by
`touch()` only, in the Mandelbrot view and at power 3, the formula line, the names of the remembered measurements:
the same text in both pages for all five; the card of none of them changes when only c moves. Learn tab, three times
"Next step": orbit identical (difference 0), notes and move names the same, and the only sentences that differ are the
Stretch ones (as intended). Time to draw the 20 scenes: 17.7 s against 17.8 s (one run each).

## 5. The earlier defects, one by one

**1. Card of Pulled plane stale after "Jump to a point": GONE** (measured, `defects.log.json` steps 1 and 2,
`break2.log`). Through the page's own controls: the Julia list ("Douady rabbit"): the card changes and equals the card
after a full refresh. A real saved point: c typed to (−1, 0.3, 0), "Save this point" clicked, jumped to the rabbit,
jumped back to the saved point: the card is the card of that c again, equals a fresh one; point deleted afterwards.
In the 2D view: the same. Six entries of the Examples list: card up to date each time. 25 values of c, one a frame:
final card equals a fresh one, one remembered measurement with a c. Entry changed while a measurement runs; the
Kleinian view with c moved there and back; z² + z³ + c; Mandelbrot from c²; powers 1, −2, 2.5, 3: equal to a fresh
card each time. In the Learn tab the Julia list and the c dials are not on show, and on leaving it the card is right.
How it is done (read in `60-measure.js`): the view hook `drawStep3d` compares the c the card was made for with the c
in use; every way of moving c ends in `touch()`, which runs the hooks. A sweep of c costs nothing visible: 121 frames
in 2 s for Pulled plane and for Turning plane, along (`misc.log`).

**2. A c out of the flat plane: the TEXTS now say it; the drawing is unchanged; one of the new examples is wrong
(defect A).** The sentences are in both notes, both About texts and at the foot of the sheet. Measured again with
the library and other random points (`offplane.txt`, `claims.txt`): rabbit c turned 10°: Along once 0 of 400,000 stay
40 steps (text: none), Pulled plane 119 (text: 94; another sample of mine 99, 73 of 300,000); c = (−1, 0, 0.3):
Along once 0, Pulled plane 70 (text: 66). Rabbit c turned 10°, 30°, 45°: nothing stays 80 steps for either entry
(text: no point left). The lab's pictures at Iterations 40 (`break-sheet.png`, seen): jagged shards and two flakes
for Along once (14 and 12 of 165 probes), a slab with buds along its edges and a thin branching thread for Pulled
plane (22 and 2). For Along once with c = (−1, 0, 0.3) I also looked IN the plane y = 0, which every step keeps and
random points cannot see: 0 of 403,200 stay 30 steps, also lifted off it by 1e-9 to 0.01 (`flakes.txt`). So for
Along once the sentences hold: the picture shows flakes where nothing stays.

**3. Stretch "2 would become 4": GONE** (measured, `defects.log.json` step 4: every Stretch sentence of all 21
entries at powers 2, 3, 4, 7, 2.5, −2, 1, 0.5 and four lengths). "Its length is multiplied by itself, not doubled:
0.80 becomes 0.64, and 3 would become 9, not 6. A length under 1 gets shorter, a length over 1 gets longer." Power 3:
"twice, not tripled ... 27, not 9"; power 4: "3 times, not multiplied by 4 ... 81, not 12"; power 7: no example;
2.5, −2, 1, 0.5 and length 1: the old sentences; Pillow at 2.5: "the rule's length". The written-out plans
(Sphere inversions, Lathe, the Mandelbulbs, Split) carry the same contrast. No "2 would become 4" anywhere.

**4. Learn, "Next step": GONE** (measured). Nine runs, up to six steps: both entries, a start at the origin, the
dials at 0.6 / 0.1 / 40, powers 3 and −2: the orbit on show is at most 2e-14 from the entry's own (`L.CARRY`), and the
moves end where the orbit goes next. Against the LIBRARY's rule, stepped one squaring at a time (`e2_learn_lib.py`,
`learn-lib.txt`, the five runs at power 2): at most 9e-15. Under stress (`break1.log`, `break2.log`):
the entry changed at step 3 and back, a dial typed at step 3, the power changed at step 3, |y| ticked, the first
dial at 0 with a start on the x-axis, powers 1, 0, 0.5, the "Julia c" button, an orbit that leaves: each time the
orbit is the entry's own (under 1e-14), no fault, no stray word. On a page and on a line both follow the flat rule
(1e-16). Companions (circle, cloud): at the first step each is a fresh orbit of its own (1e-15); at a later step they
take what the MAIN orbit carries and then this step (1e-15): as the builder says, a choice, not a history of their own.

**5. Mandelbrot card and the hidden Julia c: GONE** (measured). The card reads the same with the hidden c at −1, at
the rabbit and at (−0.5, 0.3, 0.4). "c = the point" is the first squaring that counts of the Mandelbrot orbit by the
page's own rule: 2,000 points, difference 0. Back in the Julia view the card is that c's (slice line: "does not
follow complex arithmetic here: a c that lies out of that plane pulls the page out of it", and so it is: with
c = (−0.5, 0.2, 0.4) flat points land up to 2.9 off the complex square, `break2.log` step 7).

**6. "Ease of a pull": GONE.** The label is "How little a thing near the page turns it"; "Ease of a pull" is nowhere
in the built page (measured as text). In a 390 x 844 window it wraps to two lines, nothing is wider than the window
(`phone.log`; `phone-pulledplane.png` seen).

**7. Small things: GONE** (measured). (a) The bracketed measurement stands only at power 2 with the first dial at
0.05; at power 3, 2.5, dial 0.2, dial 0.0500001: "(read off the rule)"; dial 0: its own sentence, which I checked by
hand (reasoned: with nothing held, the first pull alone sets the page, and the half-turn jump of the doubled angle
is no jump of the plane). (b) Along once: card and remembered measurements unchanged when c moves ("alongonce 2 {}",
3 -> 3); Pulled plane: one remembered measurement with a c. (c) The start-value sentence is in both notes and is
true (section 3).

## 6. New defects (all text, all minor)

### A. Pulled plane: the example c = (−1, 0, 0.3) says the opposite of what is so (measured, seen)
Where: `PP_ROUGH` and `PP_ABOUT` in `src/js/10-approaches.js` (written in the second pass).
The note: "the picture can show what is not there: ... and with c = (−1, 0, 0.3) a thin branching thread, where 66 of
400,000 stayed." The About lists the same c under "a c that lies in neither of the two planes".
- c = (−1, 0, 0.3) lies IN the plane y = 0, the standing page of this entry. In that plane the entry's set is exactly
  the flat picture of c = −1 + 0.3i: 403,200 points of the plane, 40 steps and 80 steps: 0 differ (`thread.txt`).
- c = −1 + 0.3i lies just outside the flat Mandelbrot set (0.3 from −1; the disc there has radius 0.25): the trap the
  briefing names. Its flat picture has no inside, and at 40 steps it is a thin branching thread (9,302 of 403,200
  points of the plane stay 40 steps, 1,242 stay 80, none 300). Lifted 0.01 off the plane 4,107 still stay 40 steps
  (`flakes.txt`), so the thread has a little thickness and the lab draws it honestly.
- In the lab (`thread-sheet.png`, seen; `thread-lab.log`): all 149 stops of that picture lie within 0.051 of the plane
  y = 0. The same c lying in the flat page, (−1, 0.3, 0), draws the same thread lying down (193 stops, within 0.039 of
  z = 0), and there it is plainly the flat picture and no ghost.
- "66 of 400,000" is small because the thing is thin, not because the picture is wrong.
- And "c along z" is not ghost country for this entry: c = (−1, 0, 0.2) has a full row of bodies with buds (seen), and
  6,780 of 400,000 random points stay 300 steps, as many as for (−1, 0.2, 0) (6,757) (`thread2.txt`). The rabbit's c
  turned 90° keeps 5,426 of 300,000 (`claims.txt`).
Cure: drop this example from the Pulled plane texts (the rabbit's c turned 10° is a fair one: 99 points spread
through space, none after 80 steps), or say what it is: "with c = (−1, 0, 0.3) it shows the flat picture of
c = −1 + 0.3i standing in the plane y = 0: a thin branching thread, because that c has no inside in the flat picture
either." The sentence of Along once with the same c is right and should stay.

### B. Pulled plane, second dial: "at 1 a third of the set is lost" (measured)
Where: `PP_HELP_EASE` (first pass). Round 21's row for it (`out/r21/judge/dials.txt`, "evc005" against "evc005e70")
has the weight of c at 1, not at the lab's 16. With the third dial where it starts (16), the second dial at 1 keeps
4,925 of 5,373 inside points of the rabbit at 200 steps: **8 % lost**. With the third dial at 1: 28 % lost
(`dialhelp.txt`). A user who moves that dial to 1 does not see a third go. "at 0.5 the bodies fuse where they meet"
comes from the same row pair (weight 1); I did not measure fusing at 16 (the set is 4 % larger there). The third
dial's "at 4 the bodies fuse" is round 21's row at the lab's own settings (the set is 20 % larger: measured).
Cure: give the numbers for the lab's settings, or say "with the third dial at 1".

### C. Pulled plane, About: "For c = −1 + 0.2i nothing is left in the plane y = 0" (measured)
Where: `PP_ABOUT` (first pass). In the plane y = 0, c = (−1, 0.2, 0): 23,392 of 264,000 points stay 80 steps, 21,684 of
them more than 0.02 off the x-axis (c = −1: 40,128) (`claims.txt`). Round 21 measured that no BUD is left near the
standing page ("0 % inside within 20 degrees of it" on the circles through the buds; its own count of the upright cut
was 5,746). Cure: "no bud is left in the plane y = 0".

## 7. Sentences I measured and found right (`claims.txt`, `texts.txt` holds every sentence as the page shows it)

- "one point in eight of its inside differs" (Pulled plane rabbit against one plane): one in 7.5.
- "The Siegel disc loses 15% of its points between 30 and 200 steps before it settles": 14.6 %, then 0.0 % to 400.
- "104 of 84,000 places differ" (Mandelbrot, the plane y = 0 against the flat set): 104 of 84,000 at 60 steps
  (92 at 200); the plane z = 0: 0.
- "a point belongs to a Julia set of this entry exactly when its first step lands in the solid that Sphere
  inversions, one plane draws" (Along once): 0 of 300,000 differ, c = −1 and rabbit.
- The off-plane sentences of Along once, and the rabbit-turned ones of Pulled plane (section 5, defect 2).
- The sheet for the user (`out/r22/entry/sheet-for-user.png`, seen): plain captions in the user's words, the
  pictures show what they say; the foot line says "can show", which is true.
Not a defect, noted: the label of the second dial says "page" where its help says "plane"; the formula line of
Along once carries ψ and φ, taken letter for letter from the published entry Turning plane, along; the card's
"Contains the flat set" line of Along once says HOLDS also when c lies out of the flat plane (it describes the rule,
as every older entry's card does).

## 8. Orbit loops (reasoned from reading; supported by sections 3 and 5)

GLSL: `f(` one call site (`orbitDE`, line 232 of `30-shaders.js`), `start(` one (151), `orbitDE(` one (in `de`),
`__F__` / `__Z0__` filled in one place (`40-render.js:77`). All four hooks stand inside `#ifdef APR_CARRY`. JavaScript:
`MATH[` is used in `60-measure.js` (card, step figures) and `65-learn-steps.js` (plan, the odd-entry probe);
`66-learn-view.js` iterates the plan and now hands the carried state on (measured, defect 4). No other loop.

## 9. Break attempts (measured; no console error in any run)

Both entries: power 1 (Julia empty, Mandelbrot a ball), 3, −2, 2.5, the inside-out equation z⁻ⁿ + c, z² + z³ + c in
both views, the mosaic in 3D and 2D, the 2D cut, the cut plane, |x| |z| with a flip, Iterations 1 and 200: all
draw, no failed program, no stray word on the card or the formula line (`break1.log`; `break-sheet.png`
seen). Switching among alongonce, pulledplane, turnalong, mercator, windsq, lathe, 12 choices, rabbit and Mandelbrot:
0 pictures and 0 cards differ from the first time. Phone-sized window: both draw (24 and 23 probes), the Learn tab
steps (second points (−0.50, 0.05, 0.74) and (−0.64, −0.10, 0.52)), scroll width 390. "Reset everything" with
Pulled plane chosen and c moved: card right. The Learn notes for a page and a line do not name the new entries as
exceptions. (My first break run, `break.first-run.log`, timed out in its card step: I had made the step longer than the 120 s
a step of `tools/shot.py` may take. `break1.log` and `break2.log` are the same steps in shorter pieces; both end with
exit 0 and "no console errors", and the numbers are those of the first run. In one Learn case of the first run my own
script set the power wrongly; `break2.log` step 8 has it right.)

## 10. Not checked

- The wings search and the distance-estimate comparison of the first pass (not repeated: the GLSL is unchanged).
- Sentences from round 21 not named in sections 6 and 7: c = −0.75 fused, the 7.2 % pieces 0.11 apart, the bud widths
  19° / 15° / 13°, the flakes (336 of 720), the crescent at 45°, the ledge, "at 0.5 the bodies fuse" at the lab's
  settings, the 1,728 lines of sight of the Rough paragraph, 244 of 1,200 for the one-plane entry.
- Whether the shards of Along once for an off-plane c are films or fog (only: nothing stays in the plane y = 0).
- The numbers on the card themselves (Roundness, mirror-reversed share): the measuring code is base17a's.
- A 3D model and a picture export beyond the smoke step; Exact / One neighbour beyond the smoke's check of the cap.
- Speed of the two new entries (only: a sweep of c holds 60 frames a second).
- A real phone (only a small window). Round 20's smoke line in its unchanged form.
