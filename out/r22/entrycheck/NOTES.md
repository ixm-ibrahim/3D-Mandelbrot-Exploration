# Round 22, section "entrycheck": the page dist/r22-entry.html, checked

2026-11-19, 15:05 to about 15:45. I did not write the code. Every statement is marked **measured** (a number I
computed), **seen** (a picture I opened) or **reasoned**. Paths are relative to the project root; everything of mine
is in `out/r22/entrycheck/`. `src/` was not edited.

## 0. Verdict: fix first (small fixes), then ship

The two entries are built correctly: the lab's rule, the library's rule and my own writing-out of the briefing give
the same answer point for point, in JavaScript and in the shader, also where the builder did not test (a c out of the
flat plane, the dials moved, power 3, two powers in one step, |x||y||z|). The five untouched entries draw the same
pixels as base17a. All 87 smoke steps pass. Nothing crashed in 80 break scenes, at phone size, or through the page's
own controls.

What I found wrong, worst first (section 6 has the detail and how to see each):

1. **major** The card of Pulled plane shows the numbers of the OLD c after "Jump to a point" (the Julia list).
2. **major** For a c out of the flat plane both entries draw shards or a slab where no point of the set is. The
   entries' texts are true as far as they go ("no ray stopped where the set has no body" was measured for four c in
   the flat plane; "no point of the set was left" is about the set), but they do not say that the PICTURE then shows
   shards. (The published one-plane entry draws the same ghosts: inherited, not new. The cure is a sentence.)
3. minor The new Stretch sentence at power 2 uses the one example where doubling and squaring agree: "2 would become 4".
4. minor Learn, "Next step": the point shown after the second step is not the entry's orbit (said in the Learn note).
5. minor The dial "Ease of a pull" is named with a word coined during the work.
6. minor In the Mandelbrot view the card of Pulled plane depends on the hidden Julia constant.
7. minor Small things: a measured sentence shown at every power; the card of Along once is measured again for every c.

## 1. What I ran

| what | script | result file |
|---|---|---|
| the page is the build of the current `src/` | `build.py --name r22-entrycheck ...` then `cmp` | byte-identical to `dist/r22-entry.html` (measured). `dist/r22-entrycheck-base.html` (base17a, nothing swapped) is byte-identical to the builder's `dist/r22-base17a.html` and to `dist/v17check.html` |
| `changes.diff` is the whole difference | `diff -ru base17a/js src/js` | same hunks as the builder's file; six files differ, nothing else (measured) |
| smoke lists | `ec_smoke.py` | `smoke.log`, `smoke/` |
| parity | `ec_parity_page.py` (page), `ec_parity.py`, `ec_rules.py` | `parity.txt`, `parity-slices.png`, `parity-rays.png` |
| the wings | `ec_wings.py` | `wings.txt` |
| a c out of the flat plane | inline | `offplane.txt` |
| shape sentences | inline | `claims.txt` |
| untouched entries | `ec_untouched.py` | `untouched.txt`, `untouched/` |
| break scenes, switching | `ec_break.py` | `break.log`, `break/`, `break-sheet-*.png`, `break-switch.txt`, `switch/` |
| phone-sized window | `ec_break.py phone` | `phone.log`, `phone/` |
| texts, card, Learn | `ec_texts.js` | `texts.log.json` |
| the page's own controls | `ec_dom.py` | `dom.log` (`dom.first-run.log`: my typing helper was wrong in the first run, nothing else) |

`ec_parity.js` is my first, one-piece version of the page part: it timed out (a step of `tools/shot.py` may not take
120 s). `ec_parity_page.py` is the same work cut into 39 steps.

## 2. Smoke (measured)

`smoke.log`: 87 steps ran, 87 results, exit 0, "no console errors", 645 s. The steps are read from
`tools/smoke-v14.json` (62), `out/r20/entry/smoke.py` (5) and the builder's `out/r22/entry/smoke.py` (20), not copied.
One line of round 20's steps is changed, as the builder said: it asked that `windsq` is the last entry; with the two
entries placed after it (as the briefing orders) that line cannot pass, so it now asks that `windsq` follows
`turnalong`. I did not run the unchanged line.

## 3. Parity (measured; pictures seen)

Three writings of each rule: the lab (`L.CARRY` in JavaScript, and the shader), the library (`alongmem.c_wake1`,
`sheet.evc005e70k16`), and `ec_rules.py`, which I wrote from section 4 of the briefing without looking at either.

- **Library against my writing-out**: 8,000 points, 60 steps, c = -1, rabbit, c = (-0.6, 0.2, 0.15), Mandelbrot,
  for both rules and for `oneplane` and `along`: 0 stay counts differ in all 16.
- **A. JavaScript rule**, 12,000 orbits, 60 steps, Julia c = -1, Siegel disc, **c = (-0.6, 0.2, 0.15) (out of the flat
  plane)**, Mandelbrot; Along once, Pulled plane, and **Pulled plane with the dials at 0.2 / 0.4 / 5**: 0 verdicts and
  0 stay counts differ, lab against library and lab against mine, in all 12 (144,000 orbits).
- **B. Shader, point by point** (`sampleSlice`, three neighbouring orbits beside each point), 23 level slices of
  160 x 160: Siegel disc at z = 0, 0.1, -0.27; the off-plane c at z = 0, 0.33; c = -1 at z = 0, 0.31; Mandelbrot at
  z = 0, 0.1, -0.33; and three slices with the dials moved. **0 of 25,600 differ in every slice** (588,800 points),
  against the library and against mine. The cuts at z = 0 for c in the flat plane equal the flat (complex) picture.
- **B2. Shader against the page's own JavaScript rule** where the library has none: power 3 (c on the axis and off
  the plane), z^2 + z^3 + c (both), |x||y||z| ticked; both entries, 10 slices off the flat plane: 0 of 25,600 differ
  in each. So "all powers of a step read the same carried state" and "the carried state changes after the
  modifiers" are what the shader does.
- **C. The 3D picture**, 40 x 30 probes, my rule along the same lines of sight (a test every 0.003):

| picture | lab stops | mine | lab only | mine only |
|---|---|---|---|---|
| Along once: Siegel / c = -1 | 226 / 145 | 226 / 145 | 0 / 0 | 0 / 0 |
| Pulled plane: Siegel / c = -1 / off-plane c | 197 / 143 / 317 | 197 / 142 / 317 | 0 / 2 / 0 | 0 / 1 / 0 |
| Pulled plane: Mandelbrot, two cameras | 143 / 180 | 139 / 171 | 5 / 10 (4 / 8 of them within 0.02 of the set) | 1 / 1 |
| **Along once: Mandelbrot, two cameras** | 139 / 154 | 87 / 70 | **52 / 84** | 0 / 0 |
| **Along once: c = (-0.6, 0.2, 0.15)** | 215 | **0** | **215** | 0 |
| yardstick, Sphere inversions one plane: Mandelbrot x 2 / the same off-plane c | 93 / 74 / 244 | 87 / 70 / **0** | 6 / 4 / **244** | 0 |

  The lab stops 0.6 to 2.7 pixels in front of the set (median), stops lie at most 4e-7 off my lines of sight.
  The two bold rows of Along once are sections 4 and 6.2.

No carried state leaks: a neighbour writing into the point's slot, or a state left from the pixel before, would
change verdicts off the flat plane in B (reasoned from 0 differences in 33 slices with three neighbours running).

## 4. The wings of Along once in the Mandelbrot view: the builder's finding holds (measured, seen)

- Body: 200,000 random c, Along once against the one-plane rule: 1 verdict differs at 80 steps, 21 at the lab's 27.
- 52 and 84 lab-only stops from my two cameras (`parity-rays.png`: red arcs off the left end, seen). The stop points
  themselves leave after 8 to 10 steps (median); the lab asks for 27.
- Along 24 lines of sight through such stops I looked for the longest stay in a stretch of 0.1 and narrowed 20-fold
  eight times: on 14 lines the longest stay grows by about 3 steps each time (for example 14 17 20 23 27 28 31 34 39;
  26 30 36 43 52 54 62 66 74) and never reaches "for good"; the one-plane rule leaves those places after 1 or 2 steps.
  No stretch as wide as 0.000025 stays the lab's 27 steps. On 10 lines nothing grew (my search follows the first best
  place and can sit on a plateau; that is not evidence against a film).
- So: films without thickness, as the builder wrote. The lab draws them as large blades (seen:
  `break/alongonce-04-mandel.png`), also at 14 and at 100 iterations (`-29-`, `-28-`), and at power 3
  (`-08-pow3-mandel.png`: blades above and below the body). At the page's opening Iterations (14) they fill a third of
  the picture. The entry's tag and About say "thin wings ... that have no thickness"; that is true and visible.

## 5. Untouched entries (measured)

mercator, lathe, turnalong, windsq, bulb x four scenes of my own (the rabbit in 3D, the Mandelbrot solid from another
camera, the 2D view of c = -1 at height 0.15, power 3), the page's default quality (three neighbouring orbits where
the entry allows): **0 of 604,262 pixels differ in all 20 pictures.** Every fragment shader the page handed to the GPU
while these were drawn (5 were compiled) is, with comments out and the `#ifdef APR_CARRY` blocks resolved for "not
defined", the same text in the two pages, and none defines APR_CARRY. Time to draw all 20 again: this build 13.1 s,
base17a 13.5 s (one run each; not a proof, the text is). Reading `changes.diff`: every change in `30-shaders.js`
stands between `#ifdef APR_CARRY` and `#endif`, and each `#else` branch is the old line (reasoned from the diff).

## 6. Defects

### 6.1 major: the card of Pulled plane is stale after "Jump to a point" (measured)
How to see: Julia view, Pulled plane, c = -1. The card says "Keeps shapes ... Roundness 51 % ... Wraps without
folding: FAILS, 38 % of directions land mirror-reversed". Choose "Douady rabbit" from "Jump to a point". The picture
changes, the card does not. Now touch anything that redraws the card (a mode button, a dial of the entry): it becomes
"Roundness 64 % ... HOLDS, never reverses". Two verdict cells were wrong in between. (`texts.log.json`, key `card`:
`afterMenu` against `afterMenuAndRefresh`; the same through `L.applyJuliaPreset`.)
Cause: the builder made the c DIALS redo the card (`80-ui.js`), but `applyJuliaPreset` in `75-presets.js` calls only
`touch()`. Saved points go the same way (reasoned). Cure: in `applyJuliaPreset`, do what the c dials do
(`uiApproachParam()` when the entry carries something). Through the c dials the card does follow (measured, `dom.log`).

### 6.2 major: a c out of the flat plane: the picture shows what the texts say is not there (measured, seen)
- Along once, the rabbit's c turned 10 degrees about the x-axis: of 400,000 random points none stays 40 steps (504
  stay 20, 2,503 stay 15). The lab's picture: jagged shards, 20 of 165 probes stop (`break/alongonce-20-...png`, seen).
  c = (-1, 0, 0.3): none of 400,000 stays 30 steps; the picture shows two flat flakes (`-19-`, seen).
  c = (-0.6, 0.2, 0.15): the set is empty in every test (0 of 12,000 orbits, 0 of 51,200 slice points, 0 on 1,200
  lines of sight); the lab stops on 215 of 1,200 lines.
- Pulled plane, the rabbit's c turned 10 degrees: 94 of 400,000 points stay 40 steps (0.02 %); the lab draws a smooth
  slab with buds along one edge, 17 probes (`break/pulledplane-20-...png`, seen).
- Pulled plane, c = (-1, 0, 0.3): 66 of 400,000 stay 40 steps; the picture is a thin branching thread of dust
  (`break/pulledplane-19-...png`, seen).
- Sphere inversions, one plane does the same (244 of 1,200 lines for an empty set), so the page already drew such
  ghosts before this round. The new texts are true as scoped: both notes say "with Rough no ray stopped where the
  set has no body" for four named c, all in the flat plane, and both About texts say of a turned c "no point of the
  set was left", which is about the set. But neither says what the picture then shows. A user who moves "c along z"
  sees shards and reads that there is nothing; and shards are one of the user's five tests.
- Cure (text only): one sentence in each note, for example "For a c out of the plane z = 0 the picture shows the
  places that hold out longest, as shards or a slab; no point there stays for good." and limit the Rough sentence to
  "c in the flat plane".

### 6.3 minor: the Stretch sentence (measured: `texts.log.json`, key `stretch`)
At power 2 with a length under 1 it reads "Its length is multiplied by itself, not doubled: 0.80 becomes 0.64, and 2
would become 4." 2 doubled is 4 as well: the one example that cannot tell the two apart. (The briefing suggested this
wording; the fault is in the briefing.) Cure: `const ex = r < 1 ? 3 : 0.5` gives "3 would become 9"; better still
"and 3 would become 9, not 6". The other cases read well: "1.50 becomes 2.25, and 0.5 would become 0.25"; power 3
"multiplied by itself twice, not tripled ... 2 would become 8"; power 2.5, -2, 1 and length 1 keep the old sentences;
Pillow at power 2.5 keeps "the rule's length". The written-out plans (Sphere inversions, which the page opens with;
Lathe) still say "Its length, 0.80, is squared: 0.64." with no contrast, as the builder noted.

### 6.4 minor: Learn, "Next step" (measured)
For Along once the Learn tab's second point is (-0.92, -0.03, -0.10), which is the second point of Turning plane,
along; the entry's own orbit goes to (-0.50, 0.05, 0.74). For Pulled plane: shown (-0.62, -0.08, 0.55), own
(-0.64, -0.10, 0.52). The Learn note says the moves after "Next step" are those of a first squaring; it does not say
that the point is then somewhere the entry never takes it. The briefing allowed the first squaring only.

### 6.5 minor: wording
- Dial label "Ease of a pull": "easing" is on the briefing's list of coined words. The help text explains it well; a
  plain label would be for example "How little a nearby point turns the page".
- `ppSmooth` shows "(measured with c = -1 at x = -0.8: two points 0.000000002 apart ... 0.70 apart)" at every power
  and for every setting of the first dial, though it was measured at power 2 with the dial at 0.05 (reasoned from the
  code; seen in the texts at power 3, 2.5, -2, 1). The numbers themselves are right at power 2 (worked by hand:
  0.597, 0, 0.346 against 0.59, 0, -0.358).
- The About of Along once carries "39 to 57 steps when the search is narrowed to a stretch of 0.000000000003": true,
  heavy for this reader. The neighbouring entries' texts are as dense, so I count it as house style.

### 6.6 minor: the card
- Mandelbrot view, Pulled plane: the card is measured with the Julia constant, which that view hides. With the hidden
  c at -1 it says "Roundness 51 %, FAILS"; with the hidden c at the rabbit "64 %, HOLDS" (measured). The note says
  "taken with the c of the Julia dials"; in the Mandelbrot view there are none on show.
- Along once: a c dial that moves has the card measured again (remembered measurements 13 -> 14), though nothing on
  it depends on c; and for both entries every c value adds a remembered measurement that is never dropped (measured
  growth; "never dropped" reasoned from the code).

## 7. Orbit loops: none missed (reasoned from reading; supported by section 3)

GLSL: `f(` has one call site (`orbitDE`), `start(` one, `orbitDE(` one (`de`), `de(` one in the scene's `main()`;
`__F__` and `__Z0__` are filled in only in `40-render.js:77`. No other file holds a GLSL loop over the rule
(`10-approaches.js` has the rules, `30-shaders.js` the rest). JavaScript: `MATH[` is used in `60-measure.js` (card,
step figures) and `65-learn-steps.js` (plan, odd-entry probe) only; `66-learn-view.js` iterates the plan (section 6.4).
One thing not said in the entries' notes: a power written into the START VALUE (for example "c^2") is taken before
any step, with the fresh state (the one-plane power for Along once, the flat page for Pulled plane), and is not
counted (reasoned from the code; "draws something" measured: 2 and 5 probes).

## 8. Break attempts (measured: no console error, no failed program, no stray "undefined" in 80 + 14 scenes; seen)

Power 1 (Julia empty, Mandelbrot a ball of radius 64/30: right for z + c), 3, -2 (inside out), 2.5 (smoke);
z^2 + z^3 + c; (z + 1)^2 + c, conj(z)^2 + c, z^2 + c*z, c*z*(1 - z) from 0.5; Mandelbrot from c and from c^2; mosaic in
3D and 2D; the 2D view at height 0 and 0.3 (the flat rabbit and the flat Mandelbrot set, seen); the cut plane; a c
out of the plane; trap solid ("is the solid", "is added"); escape-count colouring; flips and |x| |z|; Iterations 1,
14, 100, 200; fly mode; the Kleinian view and back (same picture); Pulled plane's dials typed into the page (clamped
to 0..1 and 0..64, to 100 and 10,000 with extreme ranges; letters ignored; the formula text follows), all three at 0,
hold 4, cpull 256. Switching among alongonce, pulledplane, turnalong, mercator, windsq, lathe and back: each entry's
picture is the same to the pixel every time (0 of 604,262, 3D and 2D; `break-switch.txt`). Phone-sized window
(390 x 844): both draw (24 and 23 probes), no sideways scroll, nothing wider than the window, the three dials 358 wide
(`phone.log`; pictures seen).

## 9. Sentences

Read all of them (`texts.log.json` has them as the page shows them at the powers 2, 3, 2.5, -2, 1, 0). No stray
marks. Both tags name faults. Re-measured with my own rule (`claims.txt`): c = -1, circles round the x-axis at x = 0:
Along once 8 separate stretches (along 8, one plane 2), Pulled plane 4 (16 at radius 0.58, as round 21 says); the
rabbit of Along once on a 120-cube grid: pieces of 75.4, 10.0, 7.2 and 7.2 % with the two small ones at
(0.04, -0.30, +-0.65) (the 10 % piece hangs on a point the coarse grid cannot see; round 21 had 85.2 / 7.2 / 7.2);
the rabbit of Pulled plane is one piece. The tear of Pulled plane at z = +-0.22: right (worked by hand). "Rough": on
c = -1 and the Siegel disc no false stop for either entry (section 3, C). Wrong or too wide: section 6.2.
The sheet for the user (`out/r22/entry/sheet-for-user.png`, seen): plain captions, no coined names, and it shows what
they say; the pictures match my own of the final build (seen).

## 10. Not checked

- The shape sentences taken from round 21 other than the three in section 9 (c = -0.75 fused, the flakes of Pulled
  plane, the ledge, 104 of 84,000, the dial effects, the Siegel disc's 15 %).
- Whether the 3D model of a Mandelbrot solid of Along once has the wings (reasoned: it cannot, they have no inside).
  The smoke only shows that a model of c = -1 ends with a file.
- Picture export, inside colouring other than escape count, the far zoom, a real phone (only a small window).
- Speed of the two new entries. "No slower" for the old ones rests on identical program text plus one timed run.
- Why the Mandelbrot picture of Along once started from c shows thinner wings than the one started from 0 (seen;
  the sets agree by the builder's JavaScript test, which I did not repeat).
- Round 20's smoke step in its unchanged form.
