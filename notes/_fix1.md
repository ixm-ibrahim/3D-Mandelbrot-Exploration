# What the fix pass asks of other files, and what it left open

From the six engineers of the fix pass (their own notes: notes/fix-*.md). "NEEDS" lines are changes they ask for in files they did not own. "LEFT" lines are defects they did not fix.

## maths

Maths group: 13 of the 16 items are fixed in my three files, 2 are partly fixed, and p10-1 was left alone as instructed. The final build passes the smoke test (exit 0, no console errors), my own 10-step page check, and the approaches parity page (76 of 76).

Workspace root for every path below: C:/Users/IbrahimMahmoud/AppData/Local/Claude-Data/claude_pzs8sxrjxfjjc/scratch-workspaces/18144097-1788-4c0f-b3ad-8a91f920f07b/76933351-09da-4379-8bd1-1c64ac9b94d1/scratch-2026-11-17-a06af1

- **Split at negative powers (p15-4, p15-3):** the cause was in my files. The old rule took 1/(x + iy) and 1/z side by side, and 1/z has no value on the plane z = 0. That gave the endless floor in Mandelbrot mode, and in Julia mode it made the shader pick the opposite side as solid. A negative power is now the positive power followed by one sphere inversion with a mirror, as in the other four approaches. The solid is bounded, and the 2D slice matches the other approaches pixel for pixel.
- **The split solid is no longer a prism at negative powers.** That is the price of a bounded picture: side by side, the thrown-out set is unbounded whatever is done at the plane.
- **Sphere inversions panel:** wording only; the rule and its parameters are untouched. It now says plainly that the slice at z = 0 is the ordinary 2D set. I also added one sentence nobody asked for: "Slices at other heights are different shapes", in answer to the user's new remark. Drop or change it when the replacement approach lands.
- **Scorecard (p15-7):** the card and both step figures now describe the power the equation actually takes, with a one-line note when that differs from the dial. This needed a small addition to the formula parser (`formulaPowers`).
- **Presets:** the comment above `PRESETS` and notes/fix-maths.md mark `name`, `eq`, `z0`, `note` as the preset and `target`, `dist`, `yaw`, `pitch`, `cut`, `julia` as suggestions only.

Not fixed inside my files: the Julia-mode framing of `z² + c·z⁻²` needs the camera file, and the Julia-mode noise of `z⁻ⁿ + c` is engine defect p15-2.

Notes are in notes/fix-maths.md; scripts, logs and pictures are in out/fix/maths/.

### maths: needs from others
- NEEDS: src/js/50-camera.js, resetCam(preset): in Julia mode do not apply an equation preset's dist, yaw or pitch (they are tuned for the Mandelbrot solid); use preset.julia.dist when the preset has one. Not needed if the page stops applying camera hints from presets.
- NEEDS: src/js/80-ui.js, the eqPreset change handler: decide which suggestion fields to apply. name, eq, z0 and note are the preset; target, dist, yaw, pitch, cut and julia are suggestions only (table in notes/fix-maths.md section 7).
- NEEDS: src/js/80-ui.js, refresh(): optionally pass cardPower() instead of S.n to x.formula(S.param[x.id], ...) so the approach panel's formula line matches the scorecard under a preset such as z^-n + c.
- NEEDS: src/js/90-boot.js, window.squaringLab: optionally add formulaPowers and cardPower so tests can reach them.
- NEEDS: src/body.html, footer paragraph on planes (about line 193): add 'Fins come in pairs, so an odd power has no exact match.' (the footer half of p10-2).
- NEEDS: src/body.html, about line 176: 'at the current n' could read 'at the power the equation takes'. The card's own note already covers the difference.
- NEEDS: tools/smoke.json (orchestrator): no change needed; it passes as it is.

### maths: left open
- LEFT p10-1: Ruled out for this round by the task: a replacement rule is being prototyped under out/proto/, and the present approach is kept as an earlier version. Nothing was restructured. The planes note still says the count is a free choice, because in this rule it is.
- LEFT p15-8: Partly done; the rest cannot be fixed inside my files. The preset z² + c·z⁻² now carries julia: { dist: 4.8 }, and rendered at that distance its Julia set is framed (out/fix/maths/sheet-presets.png, top left, with cam.dist set by hand). Applying it needs src/js/50-camera.js, which still uses the Mandelbrot distance 1.7 in Julia mode. The speckled lump of z⁻ⁿ + c in Julia mode is engine defect p15-2 and fills the frame at any distance, so it has no Julia hint. If the page stops applying camera hints, as the user asked, the framing half goes away by itself.

### maths: names added
- APR_MIRROR (10-approaches.js): the n = -1 sentence for a rule that is one sphere inversion with a mirror; used by Split
- aprNone() (10-approaches.js): the crush cell at n = 0, ['no', 'Everything is crushed onto one point.']
- aprConstant() (10-approaches.js): the smooth cell at n = 0, ['ok', 'A constant.']
- APR_SLICE_TURNS (10-approaches.js): the sentence the turn and longitude-phase hints end with
- MATH.split(v, n) and shader pw in GL_SPLIT (changed, same names and signatures): for n < 0, the positive power then one sphere inversion with a mirror, (X, -Y, Z)/(X² + Y² + Z²)
- Split roundNote (changed): now a function (p, n), as the contract allows
- aprParse(text, allowZ, n2) -> { code, powers } (20-formula.js): the formula parser; powers holds one function of n, or null, per power taken of z
- formulaPowers(text, n) -> number[] (20-formula.js): the exponents a formula applies to z, as numbers; empty when there are none or it does not parse
- compileFormula (changed, same signature and output): now aprParse(...).code; refuses typed numbers above 1e30
- PRESETS[i].julia (20-formula.js): optional { dist }, a suggested camera distance for Julia mode; only z² + c·z⁻² has one (4.8)
- PRESETS names (changed): 'zⁿ + c/z  (with a division by z)' and 'z² + c·z⁻²  (square against division)'
- cardPower() (60-measure.js): the power the scorecard and step figures describe (first power the equation takes of z, else S.n)
- cardPow (60-measure.js): cache for cardPower, { key, n, several }
- cardRun.pow (60-measure.js): the power the card last described
- #cardPowNote (element created by buildCard): the line saying which power is described when it differs from the dial

### maths: answers for the user
- Slicing the Sphere inversions solid away from z = 0: the rule is built so that the slice at z = 0 is exactly the 2D set, and nothing in it promises the same at other heights. I did not change the rule this round, because a replacement is being prototyped separately and will be added as a new approach, with this one kept as an earlier version. The panel now says plainly that z = 0 is the ordinary 2D set and that slices at other heights are different shapes.
- Whether the number of planes should be forced: in this rule it is not. The planes come from a fold added on top of the inversion sum, and the count only sets the number of fins (two per plane), whatever the power is. So it is a free choice here, which is the weakness you spotted; the panel says so and lists your own cases (4 planes for n = 8, 3 for 6, 2 for 4). The replacement approach is where a forced answer would come from.
- Quaternions and the "use third map" checkbox: the reciprocal inside the inversion sum is the quaternion reciprocal, but that does not fix a number of planes. The third-map checkbox belongs to the Kleinian view only and has no effect on this approach.
- Presets independent of camera and other settings: for the equation presets, only the formula, its start value and its note are the preset. Camera position and the cut height are now marked as suggestions only, and no preset carries an iteration count, power, quality or colour. Whether the page still applies the suggestions is the page engineer's decision.
- Negative powers under the Split approach: the endless floor and the nearly empty Julia pictures are gone. A negative power there now ends with one sphere inversion, as it does in the other approaches, which gives a bounded solid whose z = 0 slice is still the exact 2D picture. It is no longer a straight extrusion at negative powers.

### maths: risks
- The Split solid at negative powers is a new shape. I looked at Mandelbrot n = -2 and -3 and Julia n = -2, -3, -4 at Fast quality in a 1100x800 window only. Julia n = -2 and -4 show the same speckle and dust as the other approaches (engine defect p15-2). Fractional negative powers were checked numerically, not rendered.
- The scorecard and step figures now follow the equation's power for every formula. Only z^-n + c and the return to z^n + c were checked on the page; for z^3 - z + c the card now describes cubing whatever the dial says (with the note), and that was not looked at.
- The new note line sits inside #card as a p.note. Seen at 1400 px wide in the dark theme only; phone width and light theme not checked.
- drawStep3d now rebuilds the figures and restarts the card when the equation's power changes. The measure module's own timing and behaviour scripts (out/measure/) were not rerun.
- formulaPowers decides 'holds z' by the bare name z in the generated shader code. If another module ever emits a bare z in a formula's code for something else, it would over-report.
- compileFormula now refuses numbers above 1e30. Such a formula used to compile or fail on the GPU; now it gets a plain message.
- The Sphere inversions panel is long even after trimming (about 75 words for the about text, 75 for the planes note). Not checked at 375 px. The picture panel-mercator.png predates the last trim.
- The Turn hint and the scorecard sentence for a turned slice were verified as strings, not on screen with one plane and a turn set.
- notes/approaches.md still describes the old Split rule at negative powers in its 'Decisions worth knowing' section; I did not edit that file.
- Running tests/approaches.json rewrote out/approaches/parity.png, and the smoke runs rewrote out/smoke-*.png, as the tools are built to do.

## dial

Dial group: the kit's side of "extreme values" is in, two of the three tester defects are fixed on the test page, and the major one (Lift snapping) is fixed in the kit but still shows on the page until one word changes in the approaches file.

Checks run on the final files:
- Kit checks (tests/dial.html): 71 of 71 pass (59 before; 2 rewritten, 12 new).
- Real mouse, keyboard and touch (notes/dial_real.py --lab=dist/fix-dial.html): 42 of 42 lines pass, including the 71 checks in a focused desktop window and on an emulated 375 px touch phone.
- Smoke test on dist/fix-dial.html: exit 0, 20 steps, no console errors.

Two things you should know before merging:
- I edited the kit's own regression tests (tests/dial.html, tests/dial.json, notes/dial_real.py) although they are not in my two owned source files. Two old checks asserted exactly the behaviour that p2-1 and p13-4 report as defects, so they had to change. Copies of the originals are in out/fix/dial/ (dial.html.before, dial.json.before).
- 00-core.js in src/ already has S.extreme, so I made that the single copy of the switch: setExtreme writes it and isExtreme reads it. Setting S.extreme from code and calling syncControls() also moves the ranges, but only setExtreme(false) pulls values back.

One deliberate departure from the brief's wording: when xmin or xmax is given without xlo or xhi and reaches past the normal typed limit, the typed limit moves out with the slider. Otherwise { xmax: 1000 } on a dial with a typed limit of 400 would leave most of the slider dead.

Because the functions sit inside the page's closure, I tried extreme values and the there-and-back sweep inside the lab on a second page, dist/fix-dial-x.html. It uses throwaway copies of 10-approaches.js, 80-ui.js and 90-boot.js kept under out/fix/dial/; nothing in src/ beyond my two files was touched.

Everything is in C:/Users/IbrahimMahmoud/AppData/Local/Claude-Data/claude_pzs8sxrjxfjjc/scratch-workspaces/18144097-1788-4c0f-b3ad-8a91f920f07b/76933351-09da-4379-8bd1-1c64ac9b94d1/scratch-2026-11-17-a06af1; notes/fix-dial.md has the full write-up, and scripts, logs and screenshots are under out/fix/dial/.

### dial: needs from others
- NEEDS: approaches, src/js/10-approaches.js, APPROACHES entry with id 'mercator', params, the spec with key 'lift': change animate: true to animate: 'bounce'. Leave the five degree dials (turn, lat, lon, theta, phi) and the colour shift on animate: true. Until this lands, p14-1 is still visible.
- NEEDS: ui, src/js/80-ui.js: add the switch, for example in the top row beside the 2D view box: addCheck('flatHost', 'extreme', 'Extreme values', isExtreme, setExtreme, { def: false });
- NEEDS: ui, src/js/80-ui.js: give wide ranges to the dials that should have them by adding fields to their opts. Values tried on dist/fix-dial-x.html: iter { xmax: 1000, xhi: 100000 }, kiter { xmax: 2000, xhi: 100000 }, qsteps { xmax: 5000 }, Julia c dials { xlo: -100, xhi: 100 }. The numbers are the page's choice; nobody measured how slow very high counts are. Spec-built dials (approach params, colour) take the same fields in their specs.
- NEEDS: ui, src/js/90-boot.js: add setExtreme, isExtreme to the window.squaringLab object so test scripts can reach them.
- NEEDS: ui, any code that must leave extreme mode (a reset, a preset): call setExtreme(false), not S.extreme = false alone. Only setExtreme pulls out-of-range values back; S.extreme = x followed by syncControls() moves the ranges without writing values.
- NEEDS: ui, optional, src/js/80-ui.js: UI_FOV_DEG is 35.49, so Field of view starts on a fraction. With the new step rule the first arrow press lands on 35 or 36; a whole default would look tidier (the tester's side remark in p2-1).

### dial: left open
- LEFT p14-1 (as seen on the page): Cannot be finished inside my files. The Lift spec lives in src/js/10-approaches.js and still says animate: true, so on dist/fix-dial.html Lift still jumps from 1.98 to -1.95 once per sweep. The kit half is done and verified; the remaining change is one word, given under needs_from_others.

### dial: names added
- setExtreme(on): top-level function in 70-dial.js. Switches extreme values on or off for every dial, present and future; writes S.extreme when the page state exists; switching off pulls values beyond the normal typed limits back through each dial's setter (one onChange per spec-built set).
- isExtreme(): top-level function. Returns the switch: S.extreme when the page state has it, otherwise the kit's own copy.
- dialExtremeOwn: private top-level variable, the kit's copy of the switch for pages without S.extreme (the kit's test page, base2).
- dialGone(el): private top-level function, true when an element is hidden by the hidden attribute or display none on it or any ancestor; a closed details does not count. Replaces dialVisible, which is removed (no other module used it).
- xmin, xmax (dial spec or addDial opts): the slider's range while extreme values are on. Missing: the normal min or max.
- xlo, xhi (dial spec or addDial opts): the typed limits while extreme values are on. Missing: the normal lo or hi, except that the limit moves out with the slider when xmin or xmax is given and reaches beyond it.
- animate: 'bounce' (dial spec or addDial opts): the play button sweeps there and back, 8 seconds each way, instead of wrapping.
- rerange(pull) on a dial's control object: re-reads the switch and applies the matching range; with pull true a value beyond the typed limits in use goes back to the nearest one. Called by setExtreme; not meant for page code.
- S.extreme (state field, already added to src/js/00-core.js by the orchestrator): now read and written by the kit.
- <span class="dial-wide" id="<id>Wide">: the "wide" tag, present only on dials that have a wide range, hidden while it is not in use.
- is-wide: class on the .dial element while its wide range is in use.
- <id>Step toggle: now also present on dials with step 1 that can hold decimals (it reads ±1 at first, ±0.1 after a press).

### dial: answers for the user
- Extreme values: the controls are ready for it, and the button itself arrives with the next page update. When it is on, the sliders that have a wider range (for example iterations and the Kleinian search depth) stretch to that range, their number boxes accept much larger values, and each of them shows a small "wide" tag so you can see which ones changed. When you switch it off, any value that is too large for the normal range goes back to the normal limit and the picture follows.

### dial: risks
- Eight more dials now have a step toggle and their arrows go to the next whole number. Any script of another group that expected those arrows to add exactly 1 to a fraction, or expected no <id>Step element there, would now differ. The smoke test passes.
- A sweep in a folded section keeps calling its setter every frame. For approach parameters that means refresh(true) every frame while the section is closed. This is the intended fix for p13-4, but its cost with the section closed was not measured.
- Everything was tested against base2 only, not against the files the other five engineers are editing now. The src/ copy of 00-core.js (with S.extreme: false) was not in any page I ran; the S.extreme path was exercised through setExtreme on base2 and through a stand-in S object in the kit checks.
- The extreme switch was tried in the lab only with my throwaway copies of 80-ui.js, 90-boot.js and 10-approaches.js. The real button, the real ranges and their effect on drawing time are untested.
- With a very wide slider range the slider keeps its step, so one pixel covers several steps (Iterations 3 to 1000). The typed box and arrows still reach every value.
- Only Chrome was run. The tag and the there-and-back sweep were not tried in Firefox or Safari or on a real phone (phone checks used Chrome's touch emulation).
- The step toggle is still not put back by "Reset this section" (a tester noted it without filing it); not changed.

## colour

Colour group, 43 minutes (22:06 to 22:49). Only src/js/25-colour.js was edited. The page now opens with the colours the user asked for, and 5 of the 9 listed defects are fixed, 3 partly, 1 not in the form reported.

Smoke test on dist/fix-colour.html, run after the last source edit: 20 steps, exit 0, no console errors (out/fix/colour/smoke.log).

Pictures are under C:/Users/IbrahimMahmoud/AppData/Local/Claude-Data/claude_pzs8sxrjxfjjc/scratch-workspaces/18144097-1788-4c0f-b3ad-8a91f920f07b/76933351-09da-4379-8bd1-1c64ac9b94d1/scratch-2026-11-17-a06af1/out/fix/colour/ :
- sheet-open-dark.png: how the page opens now, on the Mandelbrot, three Julia presets, two Kleinian views and four 2D views.
- sheet-open-balanced-dark.png: the same at Balanced quality (Mandelbrot, Basilica, Kleinian, 2D).
- sheet-open-light.png: light theme.
- sheet-user-base-dark.png: the same settings on the old build, for comparison.
- sheet-tuneA-dark.png and sheet-tuneK-dark.png: the radius and glow-width trials.
- sheet-glow-all-before.png and sheet-glow-all-after.png: glow with every trap shape.
- sheet-minor-all.png: side, ray, three tones, preset 16 in 2D, and the old default colours.
- sheet-far.png, sheet-more-dark.png, panel-open.png.

The user's new items:
1. Defaults are orbit trap, sphere shell, glow, Rainbow reversed. I raised the shell radius from 0.7 to 1 and kept the centre at the origin and the glow width at 1. At 0.7 the rounder Julia sets (Cauliflower) were one flat blue; at 1 the Mandelbrot, Basilica, rabbit, Cauliflower and the classic bulb at n = 8 all show rings and seams. The 2D views are vivid. In the Kleinian view the pearls are rainbow but the two wall spheres stay plain violet, as they were when the user chose these settings.
2. The 2D view was not restyled. With the old colours at height 40 it is pixel-identical to base2 (largest channel difference 0).
3. trapDist(vec3 v) is now a pure function of the orbit point, and trapAdd uses it.

Not as good as asked: Point plus glow on a Julia set with the trap at the origin is still nearly one colour, three tones is still dull in 3D and flat on the Kleinian set, and the Julia mosaic opens as mostly violet balls.

Notes for the next person: notes/fix-colour.md.

### colour: needs from others
- NEEDS: Nothing is required for these fixes to work on the page: no new markup, no state the page must set, and the two new uniforms are set inside setColourUniforms.
- NEEDS: docs/CONTRACT.md, section '25-colour.js' (orchestrator): add trapDist(vec3 v) to the promised shader names with the meaning in notes/fix-colour.md, and mention S.colour.glow.
- NEEDS: src/js/30-shaders.js, next round (trap shapes the solid): call trapDist(v) yourself inside the orbit loops, next to the existing trapAdd(v, it) calls in orbitDE and kde, and keep your own running minimum. Do not read gNear: trapAdd fills it only when the colour mode is orbit trap. The minimum is a distance in orbit space, so divide by the orbit's stretch to get a step length.
- NEEDS: Any module that saves or restores S.colour (history, presets, links): restore with Object.assign(specDefaults(COLOUR_CONTROLS), saved) so that older snapshots get glow = 1; the shader copes with a missing value but the dial would have nothing to show.
- NEEDS: src/js/40-render.js, only if Point plus glow on Julia sets must be cured properly: a small read-back of nearest trap distances over the picture, so the colour module can stretch the glow over the range that occurs. I can specify the uniform pair (lowest and highest distance) on request.
- NEEDS: src/js/75-presets.js or 80-ui.js, optional and only if the user wants livelier Kleinian walls: applying a Kleinian preset could set S.colour.ty = k.my / 2 (sheet-tuneK-dark.png shows the effect). Not needed otherwise.

### colour: left open
- LEFT p3-1 (remainder): Point plus glow on a Julia set, trap at the origin: Still close to one colour on the Basilica (sheet-glow-all-after.png, second block, first tile). The picture is flat at every width I tried, so width is not the cause. My reading, not measured: every orbit on that solid makes its nearest pass to the origin at about the same distance, roughly 0.62. A real cure is to measure the range of nearest distances in the picture and stretch the glow over it, which needs a read-back in the renderer (40-render.js). Likely remedies for the user, not tested: move the trap centre (x = -1), or raise 'Colour bands, how many'.
- LEFT p3-4 (remainder): three tones on 3D solids and on the Kleinian set: Still muted mauve in 3D and one flat orange on the Kleinian set. The mix's thresholds assume orbits that circle the origin; Kleinian orbits sit near y = 2. It needs a redesign of the mix, which I did not start in the time.
- LEFT p8b-6: Not fixed in the form reported. With the new opening colours the 2D view of 'Leaning 30 degrees, seen across' is blue to violet with rainbow arcs against the cream solid (sheet-minor-all.png, sixth row, first tile). With the old colours (planes, bands, Sunset) it is still pale yellow on cream (same row, second tile). The cause was not traced: the colour is the palette's last stop, which is what a nearest distance of zero gives, so the orbits in the open gaps seem to end on a trap plane. I left that combination alone because the user asked for the 2D view to stay as it is.
- LEFT p3-6 (remainder): The colouring itself is still speckle on a solid. Reading the direction from an earlier step would give structure but would no longer be 'the last step'; I added the note and did not change the meaning.
- LEFT Kleinian wall spheres under the opening colours: Not a listed defect, but short of 'really good': the two wall spheres are plain violet. A shell around the origin is far from the points their orbits are recorded at (near y = 2). Setting 'Trap centre, y' to 1 brings colour onto them (sheet-tuneK-dark.png). I did not make that the default because the centre dials are shared by all three kinds of picture, and shifting the centre only in Kleinian mode would also move the planes trap there.

### colour: names added
- S.colour.glow: number, default 1. Glow width; the trap distance is divided by it before the glow fall-off. Missing or non-positive is read as 1.
- COLOUR_CONTROLS, new dial spec key 'glow' (control ids col-glow, col-glowNum): label 'Glow width', slider 0.1 to 8, typed 0.01 to 100, shown only when 'Trap colours by' is glow.
- COLOUR_CONTROLS, three new note specs: last-step speckle on a solid; planes = cross and ring = shell in the 2D view; (the existing notes are unchanged).
- COLOUR_CONTROLS changed defaults: trap 5 (was 4), by 4 (was 0), ray 0 (was 1), radius 1 (was 0.7), pal 8 Rainbow (was 7 Sunset), rev true (was false).
- PAL_MENU: order changed to [7, 6, 5, 9, 13, 1, 2, 12, 15, 8, 14, 10, 11, 16, 18, 0, 3, 17, 4]; palette indices unchanged.
- colGlowOn(c): 'when' test, true when a shaped trap is coloured as a glow.
- colOrbitsFlat(): true when every orbit stays in the plane z = 0 (2D view, slice height 0, and in Kleinian mode k.cz === 0 && k.mz === 0).
- COL_GLOW_THIN = 1.5: how much wider the glow of a thin trap is drawn.
- uniform float uGlowK: 1 / sqrt(glow width, times COL_GLOW_THIN for a thin trap). Set in setColourUniforms.
- uniform float uGlowP: power applied to (uGlowK * sqrt(distance)) in the glow; 1 = the old fall-off, 1.5 = thin traps. Set in setColourUniforms.
- GLSL float colSide(vec3 q): private. The side an orbit passed the trap on; beside a line or ray it is the angle round the axis divided by pi, otherwise colDir(q).
- GLSL float trapDist(vec3 v): CHANGED MEANING, now public. The plain distance from the orbit point v (the same point the renderer passes to trapAdd) to the trap shape in use. Reads only v and uTrap, uTrapC, uTrapR, uTrapAx, uTrapOff; writes nothing; valid in every colour mode. With q = v - trap centre (tx, ty, tz): Point = |q|. Cross = distance to the nearest of the three lines through the centre along x, y, z. Line = distance to the line through the centre along the chosen axis. Ray = distance to the half line from the centre in the chosen direction (behind its start, the distance to the centre). Planes = distance to the nearest of the three planes through the centre parallel to the coordinate planes. Sphere shell = | |q| - radius |. Ring = distance to the circle of that radius about the centre, parallel to the xy-plane. Three tones = no shape of its own: the three coordinate planes through the ORIGIN, centre ignored. In 3D uTrapOff is zero; in the 2D view of the slice z = 0 with trap centre z = 0 it removes the plane z = 0 from Planes and Three tones, as before.
- GLSL trapAdd(v, it): same signature; now calls trapDist(v) and stores v - uTrapC in gNear.xyz. It still returns at once when the colour mode is not orbit trap.

### colour: answers for the user
- Opening colours: the page now opens coloured by orbit trap, with the sphere shell as the trap, shown as a glow, in the rainbow palette reversed. I made the shell slightly larger (radius 1 instead of 0.7) because the rounder Julia sets were coming out one flat blue; everything else is what you picked.
- 3D orbit traps changing the shape: today a trap only paints the surface, which is why the shape never changed. Nothing in this round changes that yet. I prepared the one piece the next step needs, a single function that gives the distance from an orbit point to whichever trap shape is chosen, so the solid can be carved from the trap in the next round.
- Colouring the inside in 2D, and separate choices for inside and outside: yes, that can be done. At the moment the inside of the 2D set is one plain colour. The trap colourings could be applied to the inside as well, with a separate menu for it. I did not build it this round because you asked for the 2D view to stay as it is.
- Crisper 2D edges from distance estimation: the 2D view already uses the distance estimate to draw the edge of the set one pixel wide. Using the same estimate as a colouring of its own, which makes thin filaments stand out, would be a new 'Colour by' choice and is not built yet.
- A new 'Glow width' dial appears whenever the trap is shown as a glow. If a trap shape gives a picture that is all one colour, try another width.

### colour: risks
- Shell radius default changed from 0.7 to 1: the opening picture is not exactly the one the user saw when choosing these settings (compare sheet-user-base-dark.png with sheet-open-dark.png).
- Glow with Point, Cross, Line, Ray or Ring in 3D, and with Point in 2D, looks different from the old build (brighter, wider). The smoke picture 'trap-cross' (Cross, glow, Electric) therefore changed; I did not look at it after the change beyond the Kleinian row of sheet-glow-all-after.png.
- Three tones changed in every view, including 2D.
- The 2D far fade applies to anything more than 40 units from the centre, so a 2D picture panned that far, or a Kleinian slice larger than that, loses its outside colour there. Not tested on such a picture.
- Julia mosaic under the opening colours: most cells are plain violet balls (sheet-more-dark.png). I think these are cells cut off by their ball, whose points lie inside the set, but I did not confirm it or compare with the old colours.
- Not looked at: phone layout of the Colour section with the new dial and notes, Fine and Ultra fast quality, the glow dial moved by real mouse input, trap shapes with glow in the light theme, and most smoke pictures by eye (the smoke run was judged by its output).
- All pictures except sheet-open-balanced-dark.png were taken at the page's Fast quality in a 1000x640 window, on base2 plus my file only, so they do not show other engineers' changes.

## shaders

Time ran out after the user's two new items: the glow with the rough estimate is fixed, the slices at Fine are not, and none of the testers' shader items was started.

Only `src/js/30-shaders.js` changed, and only the ray march in `main()` of `GL_TAIL`. `dist/fix-shaders.html` builds, and the smoke test exits 0 with no console errors (`out/fix/shaders/smoke.log`).

- **(a) Glow around the rabbit with the rough estimate: fixed.** It was a bug. Rays running alongside the solid crawled at half a pixel per step, ran out of steps in mid-air and were shaded as hits. They now lengthen their stride while crawling, and an out-of-steps ray counts as a hit only when the surface is within a few pixels. Before and after pictures at Balanced confirm it, from the default camera and close up.
- **(b) Slices at Fine: not fixed.** With the exact estimate no ray lands inside the solid or runs out of steps, so both suggested causes are ruled out. Rays stopped anywhere between 0.2 and 1 pixel under the threshold; I brought every hit onto one level at no extra query cost. The chequered patches in the rabbit's shaded hollows look the same afterwards. The rings on smooth flanks with the rough estimate also remain.
- **Speed, old against new in one page, least of 3 passes:**

| Scene | old ms | new ms | new / old |
|---|---|---|---|
| Rabbit, Balanced | 75.1 | 72.4 | 0.96 |
| Rabbit, Balanced, rough estimate | 75.7 | 56.7 | 0.75 |
| Rabbit, Balanced, close up | 267.9 | 244.0 | 0.91 |
| Default Mandelbrot, Balanced | 60.5 | 63.9 | 1.06 |
| Default Mandelbrot, Ultra fast | 8.9 | 6.9 | 0.78 |

  These were measured one edit before the final file; the last edit only changed where a rough-estimate hit ends, and was not re-timed.
- **Checked on the final build:** Basilica and the classic Mandelbulb at power 8 at Balanced, and the default Kleinian view, draw as clean solids. The default Mandelbrot at Ultra fast looks dustier round the edge than the testers' picture (taken at another window size).

Everything is written up in `notes/fix-shaders.md`; scripts and pictures are in `out/fix/shaders/` (`dbg.py` tints pixels by how the march ended, `ab.py` builds the timing page).

### shaders: needs from others
- NEEDS: None for what was changed: no new uniform, state field or control.
- NEEDS: src/js/40-render.js, setScene(): keep `uStepK` at `Math.min(S.q.stepk, 0.5)` in Kleinian mode. The exact Kleinian estimate was not adopted, so the cap is still needed.

### shaders: left open
- LEFT user-b (slices at Fine and Balanced): Not cured. Experiments ruled out both suggested causes for the exact estimate: at Fine and Balanced no ray lands inside the solid and none runs out of steps (debug tint all blue, t2-fine-close.png). I put every hit on one level (estimate reads 0.8 pixel, slid along the line between the last two samples), but the chequered patches in the shaded hollows are unchanged (c-b0-terr.png before, c-f-terr.png after). They sit only in shadow, so the next thing to test is the shadow and crevice queries: switch each off on the close-up. With the rough estimate, rings on smooth flanks remain (c-f-rabbit.png): hits declared from outside and hits closed in from both sides alternate in bands. Removing the `ahead < e` rule would even them out but lose more thin parts (p5-1), so I kept it.
- LEFT p5-1: Not started (time). Learned: the rough estimate only stops inside the solid, so sheets thinner than a stride are lost; the exact estimate reads many times too short near them, which is what keeps them fat at Fine.
- LEFT p5-2: Not started (time). Not re-run on the classic Mandelbulb or the mosaic at Ultra fast. The default Mandelbrot at Ultra fast is still grainy, and looks dustier round the edge than the testers' picture.
- LEFT p5-3: Not re-run. Probably helped by the new out-of-steps rule (stray dots were rays out of steps far from the surface), but unverified.
- LEFT p5-6: Not started (time).
- LEFT p5-7: Not started (time).
- LEFT p8b-1: Not started (time). notes/klein-kde-exact.glsl was not adopted or tested, so the 0.5 cap on the step share in 40-render.js must stay.
- LEFT p8b-2: Not started (time).
- LEFT p9-1: Seams with planes = 2 are ruled out by the task (the rule is discontinuous). Sphere inversions with planes = 1 was not rendered on its own in Mandelbrot mode; the rabbit and Basilica Julia sets do draw as clean solids at Balanced.
- LEFT p9-2: Same as p9-1: not checked at n = 3 with planes = 1.
- LEFT p11-1: Not started (time). 2D mosaic ground is still painted with full colour bands.
- LEFT p15-2: Not started (time).
- LEFT p15-3: Not started (time).
- LEFT p15-5: Not started (time).
- LEFT perf-1: Belongs to render (band sizing in 40-render.js).
- LEFT perf-2: Belongs to render (the 170 ms wait).
- LEFT perf-3: Belongs to render (preview hand-off).
- LEFT perf-4: Belongs to render (busy label timing).
- LEFT perf-5: Belongs to render (when warming starts).
- LEFT perf-6: Belongs to render (preview estimate and size).
- LEFT p4-3: Belongs to render (preview drawn without shadows and crevice shading).
- LEFT p1-1: Belongs to render or core (busy label priority).
- LEFT text-17: Belongs to render (message text in sceneFail).

### shaders: names added
- LEVEL (constant in GL_TAIL, 0.8): with neighbouring orbits, the distance estimate in pixels at which a ray counts as having hit
- crawl (int in main()): strides in a row held at the least stride; lets the next stride be longer (rough estimate only)
- near (bool in main(), per march step): the surface is within a few pixels of this sample, so an out-of-steps ray may count as a hit

### shaders: answers for the user
- Glow around the fractal with the rough distance estimate (Douady rabbit): this was a bug, not a natural limit, and it is fixed. Rays that skim past the solid were moving half a pixel at a time, ran out of steps in empty space, and were then painted as if they had hit something. They now speed up while skimming, and a ray that never reaches the surface shows the background. The rough setting still draws the rabbit thinner and more ragged than Balanced or Fine.
- The 'set of slices' look at Fine: not fixed yet. On the rabbit I can see it as chequered and striped patches in the shaded hollows at Fine, and as faint rings on smooth sides with the rough setting. The two likely causes I was given turned out not to apply: at Fine no ray lands inside the solid and none runs out of steps. I made every ray stop at exactly the same depth, and the patches did not change. They only appear in shadow, so the shadow and crevice shading are the next suspects. I cannot yet say whether it is a bug or a natural limit.

### shaders: risks
- The final edit (where a rough-estimate hit ends, `if (!rough) t = tOut`) passed the smoke test, but its pictures were only looked at briefly and it was not re-timed.
- Ultra fast (90 steps): rays that run out of steps away from the surface now show the background where they used to be filled in. The default Mandelbrot at Ultra fast looks dustier round the edge than the testers' picture (different window size, not like for like). If judged worse, loosen `near` for the rough estimate.
- The moving preview (at most 120 steps) uses the same out-of-steps rule and was not looked at.
- The one-level change for the exact and one-neighbour estimates (`LEVEL`) showed no visible benefit. It is harmless in the pictures and timings I checked, but can be taken out, leaving `crawl` and `near`.
- Not re-tested with the new march: Fast preset, Fine away from the rabbit, the one-neighbour estimate, mosaic (3D), cut plane and its hatching, negative powers, picking by double-click, Kleinian presets other than the default. The smoke test covers several of these for errors only, not for looks.
- Timings were taken on a GPU shared with other engineers; each figure is the least of 3 runs alternating old and new.

## camera

All 12 camera defects (11 after merging code-2 with p8c-1) are fixed in src/js/50-camera.js and src/css/50-camera.css, plus the framing work the user's new remark asks for. Checks on dist/fix-camera.html (base2 + my two files): 54 page-script checks for the defects pass, real-input checks for the two majors pass (13 of 13), the module's own regression suite passes (148 checks, expectations updated where behaviour changed on purpose), notes/camera_real.py passes 41 of 41, and tools/smoke.json exits 0 with no console errors. Not built: automatic re-framing when the picture is empty or off the frame, and a size-aware Kleinian start distance for settings that are not on a list entry. Notes are in notes/fix-camera.md. Time used: about 49 minutes (22:06 to 22:55).

### camera: needs from others
- NEEDS: src/js/75-presets.js, applyJuliaPreset() and applyKleinPreset(): when the lists stop moving the camera, drop the resetCam({ cam: ... }) calls and the S.view.fly = false lines. Nothing else is needed for Reset view to frame a list entry: resetCam() and resetView() find the entry themselves through juliaPresetAt() and KLEIN_PRESETS[kleinPresetAt()] and read its cam { yaw, pitch, dist }. Keep those two functions and the cam field under these names, or tell the camera owner the new names.
- NEEDS: src/js/75-presets.js, kleinPresetAt(): if it keeps comparing iter (depth of the search), a list entry stops being recognised as soon as the user changes the depth, and Reset view then falls back to the plain Kleinian framing (distance 7). Leave iter out of the comparison if entries become independent of depth.
- NEEDS: src/js/80-ui.js (optional): a 'Frame it' button only needs to call resetView(). To reset just one view from page code, use resetCam(undefined, '3d') or resetCam(undefined, '2d').
- NEEDS: src/js/80-ui.js, the 'pow' dial setter: no change needed. The camera deliberately does not re-frame when the power changes sign; Reset view does it.
- NEEDS: src/css/00-base.css (optional): the stage note #camNote sits at left 10px, bottom 62px inside the stage. Keep that corner free of other overlays.

### camera: left open
- LEFT auto re-framing when the picture is empty or wholly off the frame (optional part of the new instruction): Not built, for time. The camera cannot tell an empty picture without the renderer: pick() returns null both for 'nothing hit' and for 'shader not ready', and a probe of about 100 pick() calls costs 1 to 1.5 ms each on this GPU. It needs either a 'nothing was hit' signal from the renderer or a sliced probe after renderIdle().
- LEFT Kleinian start framing for settings that are not on a list entry: Still the fixed distance 7. The solid's size is the square of the turning-out radius divided by the gap between the sphere's centre and the nearest pearl, which needs the shader's distance estimate. All 19 shipped entries fit at 4 to 7, and on a list entry Reset view uses that entry's own camera. A JavaScript port of kde() would give the size for any setting.

### camera: names added
- resetView(): what the Reset view button does. Fresh framing of the view on screen only (2D picture or 3D camera), then touch(). A 'Frame it' control should call this.
- resetCam(preset, only): new optional second argument '3d' or '2d' resets just that view; without it both, as before. The start distance is now held to the zoom limits.
- camHome(preset): returns the start framing { yaw, pitch, dist, target, h } for what is on show, without applying it.
- CAM_STEP = 0.8: one press of a zoom button or of the plus and minus keys.
- CAM_SHARP = 0.0005: 2D span below which the picture loses sharpness.
- CAM_FOV0 = 0.32 and CAM_FIT0: the field of view the start framings were chosen at, and the sine of its half angle.
- CAM_EASE changed from 0.035 to 0.07 (seconds).
- Private helpers: camFit, camListed (asks the page's lists for the entry the dials stand on), camHoldDist, camFitSpeed, camNote.
- CV.noteTmr and CV.ui.note: timer and element of the stage note.
- CAM_TEXT fields: names and stop (arc and flat), soft (flat); flat.word is now 'Span'.
- Element #camNote (class cam-note, role status) inside #stage, bottom left above the hint line; CSS class .cam-note in 50-camera.css.

### camera: answers for the user
- Presets and the camera: the camera no longer needs the lists to move it. Pressing Reset view now gives a fresh framing of whatever is on show. For a Julia or Kleinian list entry it uses the view that was chosen for that entry; for a negative power it backs off far enough to show the whole solid. The lists themselves stop moving the camera once the page side removes its two calls (listed for the page engineer).
- Reset view now only resets what you are looking at. Pressed in the 2D view it re-centres the flat picture and leaves your 3D camera where it was, and the other way round.

### camera: risks
- Reset view in Julia mode with c on a shipped list entry now gives that entry's camera instead of the plain Julia default; the mode switch does too, because the page calls resetCam(). Checked only that the lookup is guarded and that the smoke test passes; I did not look at each of the 26 Julia entries after Reset view.
- Start distances are now scaled for the field of view (unchanged at the default 0.32). Checked by numbers at a field of view of 1 for one case; not looked at as pictures.
- The negative-power distances fit what the shader draws today. If the engine group changes negative-power solids this round, the one line in camHome needs re-checking against out/fix/camera/a*.png. Julia mode at negative powers was not framed separately; it uses the same distances and the pictures there are still noise (an engine defect).
- The zoom easing is slower (a notch settles in about 330 ms instead of about 165 ms). This follows the tester's 5% per frame bar and departs from the spec's 'roughly 120 ms'. The per-frame figures were measured with wheel events sent from page script, not with the perf tester's real-wheel script.
- The stage note (#camNote) is new. It was looked at in the dark theme at 1400 px only; not checked in the light theme or at 375 px, where it could overlap the stage buttons if the text wraps to three lines.
- Typed limits on the wrong side of the other limit are now refused rather than adjusted. The 2D boxes share the code, but the refusal wording there ('closest zoom', 'widest zoom') was only checked for the hard-range case.
- Light theme, phone width and touch were not re-run with my own new checks; the older suite (notes/camera_real.py, which includes tablet and phone touch) passes 41 of 41 on the fixed page.
- out/smoke-*.png were overwritten by my smoke runs, as expected for a shared path.

## render

Renderer scheduling fixed in src/js/40-render.js (CSS untouched). On the shared GPU, base2 against the new file back to back: Balanced default picture 2.1 to 4.7 s before, 0.8 to 2.0 s now; Ultra fast finished 61 to 66 ms after a move (tester: 200 to 300 ms); dragging at Fast and Balanced 59 to 60 pictures a second. tools/smoke.json on dist/fix-render.html exits 0 with no console errors, and 18 of 19 smoke pictures are pixel-identical to base2 (the other is the fly-camera step, which moves by the clock). One thing is not proven: the 20 to 30 times slowdown the tester saw on a quiet GPU never appeared here, so that fix rests on reasoning plus the measured speed-up. Notes: notes/fix-render.md; scripts and logs: out/fix/render/.

### render: needs from others
- NEEDS: None required: no new state in S, no new uniforms, no new markup.
- NEEDS: Optional, src/js/80-ui.js UI_QUALITY (ui owner): the tester's idea of Fast with aa 2 and de 1 was not evaluated; the renderer needs nothing for it.
- NEEDS: For the next round's background picture job (whoever builds it): setScene(P, o) in src/js/40-render.js is still the one place uniforms are set, but it reads S, theme, basis() and apVec() directly. A frozen-settings job needs those passed in as an argument; nothing in this round's change stands in the way.

### render: left open
- LEFT perf-6: Not fixed, and slightly worse in one respect. The preview still uses the chosen distance estimate, as the spec decides. A cheaper estimate for the moving picture is one value in preview() (nt), but it changes the outline while moving and depends on the rough and one-neighbour estimates being repaired in 30-shaders.js first. Lighting the preview for p4-3 made it 19 to 25% smaller across at Fast and Balanced (for example 161x131 against 214x174 of 862x701).
- LEFT p9-1: Belongs to shaders or maths: torn surface of the sphere-inversion solid at n = 2 (distance estimate or the rule itself).
- LEFT p9-2: Belongs to shaders: black streaks at n = 3 (distance estimate across the fold).
- LEFT p11-1: Belongs to shaders or colour: what the 2D mosaic paints outside each Julia shape.
- LEFT p5-1: Belongs to shaders: the rough estimate loses thin parts.
- LEFT p5-2: Belongs to shaders: speckle with the rough estimate at a 2-pixel threshold.
- LEFT p5-3: Belongs to shaders: stray dots when the ray runs out of steps.
- LEFT p5-6: Belongs to shaders: Kleinian colour taken at the stopping point.
- LEFT p5-7: Belongs to shaders: the one-neighbour estimate.
- LEFT p8b-1: Belongs to shaders: kde() in GL_KLEIN. The 0.5 step cap in setScene() is kept as it was; a lower cap would be one line in setScene() if the shader owner wants it.
- LEFT p8b-2: Belongs to shaders or preset data: pearls the search never meets.
- LEFT p15-2: Belongs to shaders: distance estimate for the swapped solid at negative powers.
- LEFT p15-3: Belongs to shaders: the decision which side is solid is made inside the shader (the probe); the renderer passes nothing for it.
- LEFT p15-5: Belongs to shaders: same swap rule at n = 1. The 48 s the tester waited there was not re-timed.

### render: names added
- R.pend2: a second band handed to the GPU behind R.pend
- R.pipe: bands are GPU-timed and cheap, so two may be in flight
- R.quick: the first pass will be over within about 250 ms and is shown whole, not band by band
- R.gain: cost of a full-size row over a preview row, learnt from each first pass (starts at 3)
- R.rowPrev: cost of a full-size row at the preview's settings, from the last preview
- R.p0: the first pass under way { ms, rows, row }, used to learn R.gain
- R.busyP: the program whose first picture the busy label is waiting for
- bandFloor(): fewest rows a band may have (height/32, at least 2)
- busyOff(): clear the renderer's busy label
- warmSoon(ms): schedule preparing programs ahead
- drawDone(): status 'Done', hide the bar, schedule warming
- jobDone(job, cost): what happens when a preview or band comes back from the GPU
- prevTarget(exact): now one argument (the 2D allowance is gone); 55% of a frame, 8 to 20 ms
- bandTarget(exact): now 50% of a frame (6 to 20 ms) when GPU-timed, 0.7 frame + 4 ms by the clock
- fence(job): files the job as R.pend or R.pend2; jobs carry P, and bands also rows, p0, last, show, behind
- Status and failure texts changed: 'Nothing drawn: these settings could not be prepared' and the #glfail sentence 'This combination of approach and equation could not be prepared on this device. Try another approach or equation.'

### render: answers for the user
- On speed ('even fast is still slow', 'the zoom steps are jumpy'): the picture now updates on every frame while you drag or zoom instead of every second frame, Ultra fast shows its finished picture about 60 ms after you stop instead of 200 to 300 ms, and Balanced finished in 0.8 to 2.0 s here against 2.1 to 4.7 s before. One caution: a tester saw the old build sometimes take 20 to 30 times longer on a quiet machine; I could not make that happen on the shared test machine, so the fix for it is reasoned rather than observed and is worth one check on your own machine.
- While moving, the quick picture is now lit like the finished one, so it no longer pops about 10% darker each time the zoom rests (the gap is now about 3.5%). The price is that the moving picture is a little softer at Fast and Balanced.

### render: risks
- The quiet-GPU slow mode (perf-1) was never reproduced, so its fix is unverified. Check on a quiet GPU with: python out/fix/render/run.py dist/<page>.html out/fix/render/e2.js --argfile out/fix/render/arg-lambda-fast.json (prints rows, GPU ms and wall ms per band).
- The band floor of height/32 means a very heavy setting (Fine on a slow GPU) can hold the GPU longer than a frame per band, so the first preview after you start dragging during such a drawing may come later than before. Not measured.
- With two bands in flight the first preview after a touch waits for up to two bands (about one frame) instead of one. Not measured separately.
- Warming now runs during refining. One run showed no frame gap above 17 ms; the tester's one-off 516 ms presentation stall after a compile could now fall during refining. Not measured over many loads.
- Timings were taken on a GPU shared with five other engineers, some while my own test pages ran in parallel; absolute figures are noisy and only the back-to-back comparisons are meaningful.
- Not re-tested after the change: context loss and restore, the path without parallel compile (R.par = null), picking, stage resize mid-drawing, light theme, phone width, high-refresh displays, and real mouse or wheel input (drags were simulated in page script).
- Clock-only path (no GPU timer, as in Firefox and Safari) was run once with R.tq = null: 56 pictures/s dragging, Balanced finished in 4.6 s. Real Firefox or Safari not tried.
- The 2D view's preview no longer gets a double time allowance, so a 2D picture costing more than about 9 ms is shown slightly reduced while moving (and then is not kept as the first pass).
