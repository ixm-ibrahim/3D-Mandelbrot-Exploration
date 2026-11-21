# Round 7, engineer "page": the fix pass after the check of Version 6

Started 03:25. Source files final at 03:51, `tools/smoke.json` replaced at 03:53:46. Test page: `dist/r7-page.html`
= `base6` plus my five live files. Scripts, logs and pictures: `out/r7/page/`.

```
python build.py --name r7-page --base base6 --use src/body.html src/css/00-base.css src/js/75-presets.js src/js/80-ui.js src/js/90-boot.js
PYTHONIOENCODING=utf-8 python tools/shot.py --url dist/r7-page.html --actions tools/smoke.json
python out/r7/page/repro.py after      # the testers' reproductions as one step file (before: the same on dist/v6.html)
python out/r7/page/examples.py d       # every example through its list, with pictures (add --size 375x812 to shot.py for the phone)
```

Files changed: `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`,
`src/js/90-boot.js`, `data/klein-presets.json` (nine names), `out/r4/page/make_smoke.py`, `tools/smoke.json`.

## Per defect

Each was first seen on `dist/v6.html` (`out/r7/page/repro-before.log`, pictures `before-*.png`) and then run the
same way on the final page (`repro-after.log`, `after-*.png`). Before and after side by side: `sheet-words3.png`.

| Id | Before, on v6 | What was done | After, on r7-page |
|---|---|---|---|
| words-1 (major) | Both answers said "one smooth piece at every height"; the 2D slice of the Julia set for c = -1 at z = 0.156 is three discs (`before-words1-slice-0156.png`). | `body.html`, the first two answers: say what is seen. Nothing is torn; a slice away from z = 0 shows rounded shapes with clean edges and can show more than one; the Mandelbrot solid and the Douady rabbit "came out as one piece at every height that was tried"; a string of beads is joined only at its necks near z = 0, and a slice higher up shows separate discs. | The sentences are on the page (`repro-after.log` step 6); the picture is the same three discs, which the text now describes. The old wording is gone (smoke step 7 fails if "one smooth piece at every height" comes back). |
| words-3 | Far zoom limit 3: camera held at 3.0, 54 of 165 probes hit, 5 on the outer ring (115 and 11 with 5 iterations as well); twins 155 to 158 hit, 39 to 42 on the ring. Field of view 100: camera at 1.29, the left end out of the picture. | `75-presets.js`: `presetRoom` moves a zoom limit, or raises the drawing radius, just far enough when it is in the way; `presetDist` scales a list distance by the sine of half the field of view (it went by the tangent, which put the camera inside the solid at a wide angle). `uiFigure4` and `uiTwin` use them. The text under both button rows says so, and says that iterations, quality and colours stay. | Zoom limit 3: camera 4.8, far limit moved to 4.8, 24 of 165 hit, 0 on the ring (48 and 0 with 5 iterations). Twins: 63 and 47 hit, 1 and 0 on the ring. Field of view 100 with drawing radius 1.5 and the fly camera: camera 1.91, radius raised to 2.5, 13 hit, 0 on the ring. |
| kleinian-2 | Radius 10: black picture, 165 of 165 probes hit, no sentence. Radius 3: 164 of 165, no sentence. | `kleinTrouble()` has a new case (`kleinSwallowed`, `kleinReach`). The sentence shows for the user's own values when the solid has grown past the camera, goes when the camera is far enough away, and has one more sentence when the solid also reaches past the Drawing radius. It does not show when the camera has merely come in close on a solid of ordinary size. | Radius 10 and 3: the sentence shows. Radius 1.5 (62 probes, 0 on the ring): no sentence. Smoke step 15 checks all four cases. |
| layout-2 | 7 of 35 names wider than the closed list at 1400 wide (room 324 px, widest 518), 9 at 375. | Nine names of the group "Turning-out sphere" shortened in `data/klein-presets.json` (`out/r7/page/klein_names.py`; the copy before is `klein-presets.before.json`), then `python notes/ui_embed.py`. Only `name` changed; the first nineteen entries are untouched. | 0 of 35 too wide at 1400 (room 324) and at 375 (room 307, widest 300): `repro-after.log` step 2, `names-375.log`. Smoke step 15 measures it. |
| layout-4 | 1400 x 950: picture from 285 to 988 of 950. 1024 x 768: 284 to 852 of 768. | `00-base.css`: from 921 px wide the title and the opening paragraph stand side by side, so the masthead is short; the picture's height also stops short of the window's lower edge (`--stage-top`, measured in `boot()`). The picture keeps its height of 74% of the window at both sizes. | 1400 x 950: 150 to 853, buttons 811 to 842. 1024 x 768: 173 to 741, buttons 699 to 730. Pictures `after-open-1400.png`, `after-open-1024.png`. Smoke step 1 checks it. |

## The five items of the assignment

1. **Plain words in the closing text.** "Keeps angles true on the sphere of directions" is now a ball of directions
   on which "a tiny circle drawn on the ball is still a circle after the move" (and "keeps tiny circles round"
   in the two later places). The pillow rules "press the ball of directions flat like a cushion with a front and
   a back and do the doubling on that flat shape". Fold or wind became two sentences with a crease in cloth and
   thread round a finger. "A mirror symmetry of the set hides the jump" became: the jump is still in the rule,
   but for such a c the set on one side of the plane y = 0 is the mirror image of the other side, so no tear
   shows. No claim was made stronger or weaker; the paper's quotation is word for word. Not touched, as told:
   the answer on the stack of slices and the sentences on trap solids.
2. **words-1:** see the table.
3. **Examples.** A drop-down "Examples" right under "In the 3D view the trap" in Colour and light, with nine
   entries under the headings Mandelbrot, Julia and Kleinian: Spiky coral, Discs and arches, Rings around the set;
   Chain of bubbles, Sea urchins, Arches and hoops; Pearls and balls, Rings in the lace, Discs under the set. They
   are the nine of the solids tester's `best_of`. An example sets the kind of picture, the Julia point (the
   list's own Basilica and Douady rabbit points, so the Julia list names them), the trap shape, what the trap
   does, thickness, skipped steps, radius and the camera. Like the other two lists it names an example only while
   the page stands on it, and reads "Choose one to try" otherwise. It is on show exactly when "In the 3D view the
   trap" is, and belongs to no reset group. Pictures of all nine: `sheet-ex-d.png` (1400 x 950, with
   `sheet-ex-d2.png` for the two that were then moved back) and `sheet-ex-p.png` (375 x 812).
   - **The three Mandelbrot skip values are in one constant, `EXAMPLE_SKIP_M = [2, 2, 1]` in `75-presets.js`,**
     with a comment. When the colour module stops counting the starting value as a step, each drops by one.
     The smoke test reads the skip from the page's own table (`L.EXAMPLES[i].skip`), so only that line changes.
   - **Two decisions of mine that go past "nothing else":** a Kleinian example also sets the group and its
     turning-out sphere to the starting entry (what a Kleinian list entry sets; the depth of the search stays).
     The testers found trap solids broken-looking on entries without the third map, so the example would not be
     the named picture otherwise. And the camera step may move a zoom limit or raise the drawing radius when one
     is in the way (`presetRoom`), as for Figure 4.
   - Not set, as told: the approach, power, equation, iterations, quality, colours, the mosaic, the cut, and the
     trap centre. The hint under the list says that another approach, power or equation gives a different object.
4. **layout-4, layout-2, kleinian-2, words-3:** see the table.
5. **Smoke test:** 52 steps (42 before). New: ten steps for the examples (each through the list; state and
   controls read back; iterations, depth, approach, power, quality and colouring unchanged; the picture not
   empty and whole, by 165 probes with at most 4 on the outer ring; the list reads "Choose one to try" once a
   dial moves, and is put away in the 2D view). Added to old steps: the first screen (step 1), the new and the
   retired wordings and the Examples list (step 7), the radius sentence and the name widths (step 15), Show
   Figure 4 and the first twin with a far zoom limit of 3 (and a drawing radius of 1.5) in the way, and "whole in
   the frame" for Figure 4 and the twins. `--mine` now writes to `out/r7/page/`.

## Names added or changed

| Name | Where | Meaning |
|---|---|---|
| `trapExamples` (id), `exampleHost` (id) | built in `boot()` | the Examples drop-down and the element that holds it, placed after the `col-solid` control |
| `EXAMPLES`, `EXAMPLE_SKIP_M`, `EXAMPLE_KEYS` | 75-presets.js | the nine examples; the three Mandelbrot skip values; the fields of `S.colour` an example sets (trap, solid, thick, skip, radius) |
| `exampleFits(e)`, `exampleAt()`, `applyExample(e)` | 75-presets.js | whether the page stands on an example; its index or -1; set it |
| `presetFit(f)`, `presetDist(dist, back)` | 75-presets.js | sine of half the field of view; a list distance at the field of view in use |
| `presetRoom(dist, radius)` | 75-presets.js | move a zoom limit or raise the drawing radius just far enough for a promised view |
| `presetFrame(hint, back, flatH, room)` | 75-presets.js | new fourth argument: make room (Figure 4). Without it the distance is held to the user's limits as before ("Frame it") |
| `presetCam(hint, back, room)`, `presetHome(mult, room)` | 75-presets.js | 3D camera only, with room made (examples); the starting view times `mult`, with room made (twins) |
| `kleinReach()`, `kleinSwallowed()`, `KLEIN_NEAR`, `KLEIN_START` | 75-presets.js | how far the turned-out solid reaches; whether it has grown past the camera; the measured share 0.6 and the starting distance 7 |
| `UI.ex`, `UI_FIG4.room`, `UI_TWIN_ROOM` | 80-ui.js | the Examples control; the radius the Figure 4 solid and the twins reach to |
| `--stage-top` | 00-base.css, set in `boot()` | where the picture starts on the page plus 12 px; `.stage` uses it in its height |
| `squaringLab.EXAMPLES`, `.applyExample`, `.exampleAt`, `.kleinReach`, `.kleinSwallowed` | 90-boot.js | the same for tests |
| nine `name` values | data/klein-presets.json | "0/1 cusp, third map: moved back", "0/1 cusp, third map: across and back", "0/1 cusp, third map: close to a wall", "1/2 cusp, gap under the upper wall", "1/2 cusp, small sphere, narrow gap", "1/3 cusp, beside the large pearls", "1/4 cusp, between the strings", "Leaning 30°, lifted off the plane", "Leaning 30°, third map: moved back" |
| `grid()`, `EXAMPLES`, `EX_CHECK` | make_smoke.py | 165 probes with the outer ring counted; the examples as the test expects them |

No state field of `S` was added. No id, label or state field of another module was changed.

## Measured, with evidence

- Smoke test, final: `tools/smoke.json` on `dist/r7-page.html`, 52 steps, exit 0, "no console errors", 91 s by the
  clock (03:54:06 to 03:55:37): `out/r7/page/smoke-final.log`. The same steps as `--mine` passed twice before
  (`smoke-mine-1.log`, and `smoke-mine-2.log` on the final sources). The frozen `tools/smoke-v6.json` (42 steps)
  also passes on this page: exit 0, no console errors (`smoke-v6-on-r7.log`).
- Radius sentence, where it starts: on the starting group from camera distance 7, of 165 probes: radius 1.5 62 hit
  (0 on the ring), 1.7 103 (11), 1.9 131 (27), 2.1 148 (35), 2.3 157 (44), 3 164 (47): `kleincal.log`. The
  sentence starts at radius 2.1. With radius 3 from 45 away and the drawing radius at 8 only the middle is drawn,
  cut off flat on its sides; with the drawing radius at 40 the solid is whole (`sheet-kleincal.png`, lower row;
  upper row: radius 2 and 2.3 from the starting distance).
- Examples at 1400 x 950: 15 to 43 of 165 probes hit, none on the outer ring (`examples-d.log`, `examples-d2.log`);
  at 375 x 812: 11 to 30 hit, none on the ring (`examples-p.log`).

Reasoned, not measured: that the sentences on mirror symmetry and on fold and wind say the same as before in
plainer words (I rewrote from `docs/SPEC5.md` and the lab notes; no new check of the maths). "Came out as one
piece at every height that was tried" rests on the words tester's numbers, not on a run of mine.

## For whoever joins the files

- `EXAMPLE_SKIP_M` (above). After the colour engineer's change look at the three Mandelbrot examples again; the
  cameras were chosen for today's pictures.
- The closing text does not mention the Examples list yet, because the sentences on trap solids are yours to
  correct. A sentence that fits the N3 answer: "The list Examples under it has nine such objects to start
  from." Then add 'Examples' to the list of names in step 7 of `make_smoke.py`.
- The camera engineer is changing the picture's controls on a narrow stage. The examples, Figure 4 and "Frame
  it" back off on a narrow stage through `presetNarrow()` (75-presets.js, mine). At 375 wide the examples are
  whole in the picture, but their right ends still run under the zoom column as it is in base6
  (`sheet-ex-p.png`). If the new layout needs another back-off, that line is the place.
- `presetRoom`, `presetHome` and `kleinSwallowed` use the camera module's `CAM_LIM`, `resetCam`, `cam` and
  `basis`. If one of those is renamed, these three follow.
- A bug of mine found and fixed on the way: the first version measured `--stage-top` on the picture, which stays
  put while the page scrolls, so a masthead that changed height while the page was scrolled squeezed the picture
  to 340 px. It is measured on `.bench` now. Every number and picture named in this file is from runs after that fix.
- `tools/smoke.json` fails on a page without my files (the Examples list, the new wordings, the first screen).
  The file as it was is `tools/smoke-v6.json` (identical to the old `tools/smoke.json`; a copy is also at
  `out/r7/page/smoke-before.json`). The frozen file passes on my page too (`out/r7/page/smoke-v6-on-r7.log`).
- `out/r7/page/smoke_patch.py` and `smoke_examples.txt` record how `make_smoke.py` was changed; one more check
  (the camera coming in close) was added by hand afterwards. `make_smoke.py` is the source.

## Not done, not checked

- Looked at by eye: the first screen at 1400 x 950, 1024 x 768 and 940 x 768 (dark), the Examples list with its
  hint at 1400 wide (dark, `look-examples.png`) and at 375 wide (light, `look-examples-phone-light.png`), the
  rewritten answers at 1400 wide (`look-text-a.png`, `look-text-b.png`). Not looked at: the masthead in the light
  theme, the closing texts at phone width.
- The Examples list was driven with change events from script, not with a real mouse or keyboard.
- Windows between 921 and about 1000 px wide: the two-column masthead leaves the opening paragraph a narrow
  column there. Not looked at.
- Firefox and Safari not tried.
