# Round 5, engineer "page": closing texts, Figure 4 buttons, Julia list, look-over, smoke test

Started 01:20, source files final at 01:45, `tools/smoke.json` replaced at **01:47:21**, last smoke run ended
01:48:36. Test page: `dist/r5-page.html` = `base5` plus my six live files (so it has base5's slow shaders).
Scripts, logs and pictures: `out/r5/page/`.

```
python build.py --name r5-page --base base5 --use src/body.html src/css/00-base.css src/js/75-presets.js src/js/80-ui.js src/js/90-boot.js src/js/10-approaches.js
PYTHONIOENCODING=utf-8 python tools/shot.py --url dist/r5-page.html --actions tools/smoke.json
python out/r5/page/run.py fig4            # the three new features, with pictures
python out/r5/page/run.py look 375x812 light   # the look-over, any of 1400x950 / 375x812 and dark / light
```

## What was done, item by item

1. **Closing texts.** `src/body.html`, section "Questions from testing, answered", rewritten. No paragraph is held
   back any more: every `data-needs` attribute is gone from the markup and the block in `boot()` that hid them is
   deleted. (Kept on purpose: the fallback sentence in `boot()` for a missing export or mesh panel and the
   `typeof` guards in `90-boot.js`. They cost nothing and are not about texts.) The labels in the texts were read
   off the built page first (`out/r5/page/labels.py`, result in `labels.log`); the smoke test now checks that every
   control the closing text names exists on the page under that very label (step 7). Corrections that are in:
   the slices were in the colouring and are cured for Mandelbrot and Julia pictures, the Kleinian view never had
   them; trap solids work in all three kinds of picture; a new approach or equation takes a moment
   ("Preparing the formula"); the first real test of saving from the published page is the user's. New short
   answers: what the page opens with (N2), the Kleinian entries that move the turning-out sphere (N9).
   Also changed, because it contradicted the new N1 text: the heading "One formula, nothing placed by hand, and
   the planes are a free choice" is now "One formula, nothing placed by hand" and its second paragraph no longer
   says "No value is the correct one".
2. **N1.** Four answers replace the old three: why the solid came apart, whether the planes are forced, whether
   the plane should come from where the point starts (the Lathe), where the look of Figure 4 is; then the third
   map. The pillow paragraphs and their hiding are gone. Kept to what SPEC5 says: the argument for "forced" is
   called "a short argument of ours, not a published theorem"; the six rules are "judged by their pictures"; the
   limit to c on the real axis is given as the paper's own words with the page number.
3. **Show Figure 4 / Back to one plane.** Two buttons under that answer (`fig4Show`, `fig4Back`), wired in
   `80-ui.js` (`uiFigure4`, `uiOnePlane`). The dial kit has no call that sets a control to a value (only "reset to
   default"), so the buttons work the way `uiResetAll` does: the page's own functions where there is one
   (`applyJuliaPreset` for c, `applyEquation`, `presetFrame` for the camera), plain state for the rest, then
   `syncControls()` and `refresh(false)`, which is exactly what each control's setter ends in. A sweeping Turn or
   Lift dial is stopped first (`uiApQuiet`), or it would write its value back on the next frame. Both buttons scroll
   the picture into view (`uiShowStage`), because they sit at the end of the page.
   - Show Figure 4 sets: Julia, c = (-1, 0, 0), power 2, the plain equation z^n + c with z0 = 0, Sphere inversions
     with Planes 2, Turn 0, Lift 0, the camera (yaw -1.9, pitch 0.55, dist 4.8, backed off on a narrow stage). It
     also switches off what would hide that solid or show another one: the 2D view, the cut, the modifiers, and a
     trap that is the solid (`S.colour.solid = 0`). Iterations, quality and the other colours are left alone. The
     text under the buttons says all of this.
   - Back to one plane sets Planes to 1 and makes Sphere inversions the chosen approach. c, camera and the rest
     stay. **A decision of mine:** from the Kleinian view it also goes to the Julia set (planes mean nothing to a
     Kleinian group, and a button that changes nothing visible feels broken). From the Mandelbrot view it stays there.
   - The two notes under the planes dial (`par-mercator-note1`, `par-mercator-note2` in `10-approaches.js`, text
     only) each got one sentence that points the other way.
4. **Julia list.** `data/julia-presets.json`: the `source` of Cracked Basilica, Split conch, Flint, Plated egg,
   Plated ball and Cracked gourd went from `"explored"` to `"two planes"`; nothing else in the file changed
   (`out/r5/page/julia_headings.py` did it and checks it; the copy before is `out/r5/page/julia-presets.before.json`).
   `python notes/ui_embed.py` was run. `uiJuliaOptions()` takes the heading from `source`: saved points first as
   before, then "Classic sets" (18), "Found by exploring" (2: Thorn crystal, Pitted gourd), "Found with two
   planes" (6). New button `juliaFound`, "As it was found", beside "Frame it": sets the `planes` and `iter` the entry
   records and nothing else; hidden when it would change nothing. **A decision of mine:** the planes count only
   while Sphere inversions is the chosen approach (under another approach its planes dial is out of sight and
   changes nothing in the picture); the iterations count under every approach. Its tooltip says what it will set
   ("Sets Planes to 2 and Iterations to 24, ..."). The buttons of both lists now sit under their list
   (`.pick-row-under`), so the list keeps its full width and does not jump when the second button comes and goes.
5. **Look-over** at 1400 x 950 and 375 x 812, dark and light: see below.
6. **Smoke test.** `out/r4/page/make_smoke.py` now writes 38 steps (27 before). New: "As it was found" (2 steps);
   a trap that is the solid in the Mandelbrot and in the Kleinian picture (4 steps: 49 probes with `L.pick` must
   hit, and not in the same places as on the plain set); an inside colouring in the 2D view (3 steps: the controls
   appear, then a 256 x 256 picture job of that view is saved and the colours at seven places inside the set must
   be at least three clearly different ones); Show Figure 4 from the Kleinian 2D view with a cut, a modifier, a trap
   solid, power 3 and a sweeping Lift dial, then Back to one plane, also from the Kleinian view (3 steps). Step 7
   checks the new texts and labels; step 16 expects the three Julia headings. `--mine` now writes to
   `out/r5/page/`. Step 3 still allows 64 s.

## Names added or changed

| Name | Where | Meaning |
|---|---|---|
| `fig4Show`, `fig4Back` | body.html (ids) | the buttons "Show Figure 4" and "Back to one plane" in the closing text |
| `juliaFound` | body.html (id) | the button "As it was found" in the Julia section |
| `.pick-row-under` | 00-base.css, body.html | a list row whose buttons go under the list (both lists use it) |
| `uiFigure4()`, `uiOnePlane()` | 80-ui.js | what the two buttons do |
| `uiApQuiet(id)` | 80-ui.js | stop the sweeps of one approach's dials |
| `uiShowStage()` | 80-ui.js | scroll the picture into view |
| `UI.ap` | 80-ui.js | the control set of each approach by id (what `buildControls` returns) |
| `UI_FIG4` | 80-ui.js | c and camera of the Figure 4 picture |
| `UI_JULIA_HEADS`, `uiJuliaHead(p)` | 80-ui.js | the three headings of the shipped Julia entries and which one an entry stands under |
| `juliaFoundDiff(p)`, `applyJuliaFound(p)` | 75-presets.js | which of an entry's recorded planes and iterations differ from the page's; set them |
| `"source": "two planes"` | data/julia-presets.json | new value of `source`, on six entries |
| `squaringLab.showFigure4`, `.onePlane`, `.juliaFoundDiff`, `.applyJuliaFound` | 90-boot.js | the same four functions for tests |
| removed: `data-needs`, `#pillowText` | body.html, 80-ui.js | the hiding of closing texts |
| `probes()`, `hits(s)`, `__EXPORT_BLOB__` | make_smoke.py | 49 picks over the picture; count of hits; the saved picture as `bm` |

No state field of `S` was added. No control id, label or state field of another module was touched.

## Measured (with evidence)

- Smoke test, final: `tools/smoke.json` on `dist/r5-page.html`, 38 steps, exit 0, "no console errors", 75 s by the
  clock, waits add up to 44 s: `out/r5/page/smoke-final.log`. The same steps as `--mine` passed twice before
  (`smoke-mine-1.log`, `smoke-mine-2.log`).
- Show Figure 4 from the Kleinian 2D view leaves mode buttons, c dials, approach list, planes, turn, lift, power,
  cut, modifiers and the Julia list showing the new state, and stops a running Lift sweep: asserted in
  `out/r5/page/fig4-dd.log` and in smoke step 34. The picture is the row of bodies with beads around two circles:
  `out/r5/page/fig4-dd-fig4.png` (and one plane beside it: `fig4-dd-oneplane.png`); at phone width
  `look-pd-8-fig4.png`. After the click the picture is in view at both widths (stage at 0 to 703 of 950, and 0 to
  325 of 812: `look-dd.log`, `look-pd.log`, last step).
- The same two buttons with the fly camera on, flown away, extreme ranges on and the mosaic ticked: the picture
  is framed the same (9 of 49 probes hit, as with the arcball camera), the fly camera stays on:
  `out/r5/page/fly.log`, `fly-fig4.png`.
- Trap as the solid is not empty: Mandelbrot 20 of 49 probes hit (6 on the plain set), Kleinian 13 of 49 (10 on
  the plain set), different places in both: `smoke-final.log` steps 28 to 31, pictures
  `out/smoke-21b-trap-solid-m.png`, `out/smoke-21c-trap-solid-k.png` (copies that stay: `out/r5/page/smoke/`).
  Julia: `out/r5/page/extra-solid-j-r1.png`.
- Inside colouring draws: 5 clearly different colours at 7 places inside the set in a saved 256 x 256 picture:
  `smoke-final.log` step 33, picture `out/smoke-21d-inside-2d.png`.
- Julia list: three headings with 18, 2 and 6 entries, 26 in all: `fig4-dd.log` last step.
- Kleinian list: 15 entries under "Turning-out sphere": `look-dd.log` step 12.
- "A Glow width of 2 or 3 brings more colour back" (in the N12 answer): `out/r5/page/sheet-extra-stage.png`,
  first two pictures (glow 1 and 2.5).
- No sideways scrolling at 375: scrollWidth 375 = innerWidth 375 (`look-pd.log` step 1).

Reasoned, not measured: everything the texts say about the published host (saving a file), about N11 (taken from
the shader engineer's report), and the sentence "A trap that is the solid needs one too, and so do colours for the
inside of the set" in the last answer. That sentence is true of the speed engineer's live `sceneWant`
(`colProgramNeeds()` in `src/js/25-colour.js`, read at 01:44), not of base5. **If that specialisation does not
ship, delete that one sentence from `src/body.html`** (last paragraph of the footer).

## Look-over (item 5)

Sheets per width and theme, `out/r5/page/sheet-look-<dd|dl|pd|pl>-<a..e>.png` (d/p desktop/phone, d/l
dark/light): a = Save a picture (finished job), Save a 3D model (finished job), Colour and light with the trap
solid, its lower part with the cut face tick box; b = the 2D colour controls, the Kleinian list, the Julia list
with "As it was found", the page after Show Figure 4; c = the pictures (trap solid, cut face coloured, inside
colouring, a Turning-out sphere entry, Kleinian trap solid); d, e = the closing texts.

Seen wrong and fixed (mine):
- The Kleinian list cut its long new entry names short because "Frame it" shared its line; the buttons now sit
  under the list at every width.
- "c = (-1, 0, 0)" broke across two lines at phone width; it is held together now.

Seen and not mine:
- `src/css/50-camera.css:12` (`.cam-zoom`, 56 px wide at right 10 px): at 375 wide the zoom slider and its two
  boxes lie over the right fifth of the picture, so the right end of a framed set runs under it
  (`look-pd-8-fig4.png`, `sheet-look-pl-c.png`).
- `src/js/25-colour.js:97` (Trap radius, default 1) with `:83` and `:85`: at the opening settings "Is the solid"
  turns the Mandelbrot picture into two plain balls (`look-dd-s1-solid-m.png`); it is not empty and it is what the
  rule gives, but as a first click it looks plain. The Julia set for c = -1 gives the chain of bubbles
  (`extra-solid-j-r1.png`, `extra-solid-j-r07.png`). Nothing to fix in my files.
- The default camera does not back off for a trap solid, which is larger than the set, so at 375 wide the ball
  is cut off at the right edge (`sheet-look-pl-c.png`, first picture). Camera module, nobody's this round.
- `src/js/45-export.js` facts box: the file name wraps in the middle ("squaring-lab-mandelbrot-" / "256x256.png",
  `sheet-look-dd-a.png`). Harmless.
- Nothing wrong seen in Save a 3D model, the trap solid controls, the outline, glow and inside controls or the
  cut face tick box, in either theme or width.

## For whoever joins the two halves

- My files: `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`, `src/js/90-boot.js`,
  `data/julia-presets.json`, two note texts in `src/js/10-approaches.js`, `out/r4/page/make_smoke.py`,
  `tools/smoke.json`. The Julia list is already embedded; no need to run `notes/ui_embed.py` again unless a data
  file changes.
- `tools/smoke.json` is the new one since 01:47:21. It fails on any page without my files (step 7 asks for the
  new texts and buttons), so a page built from base5 plus only the speed engineer's files cannot pass it. The file
  as it was before is kept at `out/r5/page/smoke-base5.json` for such pages.
- **A first try of the join, measured:** at 01:51 I built `dist/r5-page-join.html` from base5, my files and the
  speed engineer's three live files as they stood at that minute (`src/js/25-colour.js`, `30-shaders.js`,
  `40-render.js`; they were still being worked on) and ran the same 38 steps: exit 0, no console errors, 45 s by
  the clock (`out/r5/page/join-try.log`). Switching the trap to "Is the solid" waited 2.8 s there, which is the
  new program being prepared. This says the two halves fit as of 01:51, nothing more: run it again on the final files.
- New smoke steps that lean on the speed engineer's files: `L.pick` must keep working with the specialised
  program keys (steps 28 to 31 and 35), and a change of "In the 3D view the trap" or of the inside colouring may now
  prepare a program; those steps wait for the picture with the usual 240 s limit, so no change is needed.
- The N3 answer says trap solids work in all three kinds of picture and does not mention the shader engineer's
  round 4 caveat (at Fast and Ultra fast a trap solid loses most of its colour). If the speed engineer's follow-up
  (a) is not delivered, consider adding after "This works in Mandelbrot, Julia and Kleinian pictures.": "At Fast
  and Ultra fast such a solid is complete but loses most of its colour."
- Old pictures `out/smoke-22-collapsed.png` and `out/smoke-23-expanded.png` keep their names; the new pictures are
  `out/smoke-15b-...` and `out/smoke-21b-...` to `21f-...`.
- Not done: defects of group "page" from round 4 were not revisited; Firefox and Safari not tried.
