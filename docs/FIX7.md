# Fix pass after the check of Version 6

Ten testers checked Version 6 (`dist/v6.html`, source frozen as `base6/`) against the 27 points the user
raised. Their reports are in `notes/_t6_reports.json` (verdict and "user view" per point, the checks, the best
settings they found, what they did not reach) and their 36 defects in `notes/_t6_defects.json` (id, title,
severity, group, exact reproduction, expected, actual, evidence, suggested fix). No blockers, 8 major, 28 minor.
All 15 points of the second round pass; of the third round N2, N4, N5, N7, N8, N9 and N11 pass, and N1, N3, N6
and N10 are partial; N12 is known to be half cured and has its own engineer.

Each engineer below fixes the defects of one group of files. Read your defects in `notes/_t6_defects.json`
(print them with `python -c` or open the file; the `tester` field names the report in `notes/_t6_reports.json`
that has the context, and the evidence paths are under `out/t6/<tester>/`). Reproduce each one on `dist/v6.html`
before you change anything, fix it in your files, and show it fixed on your own page with the same reproduction.

## Rules

- You own only the files named for you. Four other engineers are editing other files of `src/` at the same
  time, and one more is rewriting the colour and shader code (`src/js/25-colour.js`, `src/js/30-shaders.js`,
  parts of `src/js/40-render.js`): do not touch those, do not depend on their state, report what you need.
- Build your page from the frozen copy plus your live files, never with plain `python build.py`:
  `python build.py --name r7-<you> --base base6 --use <your files>`. `src/js/00-core.js` has one change since
  `base6` (see "The save helper"); the export and mesh engineers add it to `--use`.
- Test with `PYTHONIOENCODING=utf-8 python tools/shot.py --url dist/r7-<you>.html ...` (read the comment at its
  top). One GPU is shared: one `tools/shot.py` at a time, raise timeouts rather than assuming a hang.
- The smoke test for everyone except the page engineer is the frozen copy `tools/smoke-v6.json` (42 steps): it
  must pass on your final page, exit 0, no console errors. `tools/smoke.json` is the page engineer's to
  regenerate.
- Scripts, logs, pictures under `out/r7/<you>/`; notes in `notes/r7-<you>.md` (what you did per defect id, every
  name you added or changed, what the person joining the files must know).
- User-facing text in plain words, sentence case, no em dashes, no jargon. Colours through the CSS tokens only.
- No git, no publishing, no servers.
- Time: run `date +%H:%M` first. Aim for 35 minutes, stop at 50 whatever the state, with your page building and
  the smoke test passing. Majors first. A defect you cannot fix in the time gets an honest line in the page's
  own words where the user meets it (a hint, a warning), or goes under not_fixed with what you learned.

## The save helper (already changed, `src/js/00-core.js`, orchestrator's file)

`saveFile(filename, data)` no longer throws and no longer remembers a failed attempt to reach the host. On
failure it returns `{ ok: false, code, message, again }`: `message` is a plain sentence, `again` is true when
pressing the button once more can help (`declined`, `rate_limited`, `failed`) and false when it cannot
(`unavailable`, `too_large`, `rejected_extension`, `extension_not_enabled`). A test hook that throws now gives
`{ ok: false, code: 'failed', ... }`.

## export: `src/js/45-export.js`, `src/css/45-export.css`

Defects: export-1 (major), export-2, export-3. For export-2 and export-3 use the new `again` field: say "you
can try again" only when it is true, and make sure the Save button works again after any failure. For export-1
the estimate has to be roughly right from early on and must not rise while the job runs; the tester's
suggestion (time a small patch of every tile first, or weight by what the finished tiles cost) is a start.
Show no number until there is one worth showing. Also from the report's "unverified" list, if time is left:
frame gaps at the very end of a 4K job (writing the file and the preview); the step at one tile border of a 4K
Fine picture of the 2D view (`out/t6/export/C-flat4k.png`, x = 2048).

## mesh: `src/js/46-mesh.js`, `src/css/46-mesh.css`

Defects: mesh-2 (major), mesh-3, mesh-4, mesh-5, mesh-6, walk-1. mesh-4 first, because mesh-2 probably hangs on
it: the surface offset is applied to a distance estimate that reads short, so the standard model is fatter than
the picture. Make offset 0 mean "where the picture has it" and a positive offset a true distance (divide by the
slope, or push the finished points along their normals), and choose the starting offset so that the standard
model matches the picture's outline at 128 cells as well as at 512. Then mesh-2: find out with offset 0 whether
the negative-power model is right; if the raw distance itself is wrong for inside-out solids, say so (that is
the shader engineer's) and make the panel warn in plain words instead of handing over a wisp. mesh-1 belongs to
the shader engineer, but one part is yours: a mesh point takes the colour of "the outside end of its grid
edge"; take the colour between the two ends by the point's place on the edge instead, so that when the samples'
colours become right the model's are too.

## camera: `src/js/50-camera.js`, `src/css/50-camera.css`

Defects: layout-1 (major), layout-5, solids-7, words-2. layout-1: on a stage narrower than about 500 px the
picture's own controls must stay clear of the picture's content; the tester suggests a slimmer column with the
limit boxes shown only while the slider is in use, or the zoom laid out as a row under the picture. Whatever
you choose, the zoom slider, its two limit boxes and the fly/arcball switch must all stay usable by finger, and
the desktop layout must not change. Then words-2 (framing on a phone should allow for whatever still lies over
the picture). solids-7: when a trap is the solid or is added to it, the start view and "Reset view" should
stand far enough back for the trap's own size (its radius and thickness, where the trap shape has one) so the
object is not cut off by the frame; the dials themselves must not move the camera.

## dial: `src/js/70-dial.js`, `src/css/70-dial.css`

Defects: controls-1, layout-3. Small: do them, then check all 50 number boxes still behave as the "controls"
tester found (typed values, refusals, arrows, the toggle).

## page: `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`, `src/js/90-boot.js`, names in `data/klein-presets.json`, `out/r4/page/make_smoke.py`, `tools/smoke.json`

Defects: words-1 (major), words-3, kleinian-2, layout-2, layout-4. And from the reports:

1. **Plain words in the closing text.** The "words" tester marked: "keeps angles true on the sphere of
   directions" (three times), "fold the sphere of directions over itself, or wind it three times round the
   negative x-axis", the unexplained "pillow" rules, "a mirror symmetry of the set hides the jump". Say each in
   words a non-mathematician can picture (for example: think of every direction from the centre as a point on a
   ball; the rule moves those points about; "keeps angles true" means a small circle drawn on that ball stays a
   circle). Keep every claim exactly as strong as it is now. The paper's quotation stays word for word.
2. **words-1.** The Mandelbrot solid and the rabbit are one piece at every height; a string of beads such as the
   Julia set for c = -1 shows separate discs when sliced above the necks. Say what is seen, in both answers.
3. **One-click examples for trap solids (N3).** The "solids" tester: "there are no one-click examples, so the
   good settings have to be found by luck." Add a small drop-down or row of buttons, "Examples", close to "In
   the 3D view the trap" in Colour and light, with the nine settings under `best_of` of the solids report (three
   for each kind of picture), each with a short name ("Spiky coral", "Chain of bubbles", "Sea urchins", ...).
   An example sets the mode, the Julia point where it needs one, the trap shape, what the trap does, thickness,
   skipped steps, radius, and a camera that shows the object whole; nothing else. In Mandelbrot mode the
   examples use skipped steps 2 today: put the three Mandelbrot values in one constant with a comment, because
   the colour engineer is changing what that count means there (it will become 1 for the same picture) and the
   person joining the files will adjust it.
4. **layout-4:** when the page opens at 1400 x 950 or 1024 x 768 the whole picture with its own buttons should
   be in view. **layout-2:** shorten the long names in `data/klein-presets.json` (then `python
   notes/ui_embed.py`); the group heading already says the sphere moved. **kleinian-2:** a sentence when the
   turning-out radius has grown past the camera. **words-3:** the Figure 4 and twin buttons should frame the
   solid even when the user's zoom limits or field of view stand in the way, or the text beside them should
   say what they leave alone.
5. **Smoke test:** steps for the examples (each sets what it says; the picture is not empty) and for anything
   else you add. Regenerate `tools/smoke.json` only when it passes on your page.

The closing text's answer on the "stack of slices" and the sentences on trap solids will be corrected by the
person joining the files once the colour engineer has finished; leave them.

## Report

Return: summary; files_changed; fixed (id, what, evidence); not_fixed (id, why, what you learned);
names_added; needs_from_others (exact changes in files you do not own); risks.

## engine (second part, after the colour engineer of round 6): `src/js/25-colour.js`, `src/js/30-shaders.js`, `src/js/40-render.js`

This engineer starts when the colour engineer of round 6 has returned and its files have been joined; the base
for this part is `base7a/` (= `base6/` plus those files) and the page to compare with is `dist/v7a.html`. Read
`notes/r6-colour.md` and `notes/r5-speed.md` first: the structure they describe protects the compile time (one
call to the colour code from `main()`, few reads of the palette, programs built for what the settings need).
Measure with `python out/me/perf.py base4 r7-engine base4 r7-engine` before and after: opening settings under
2.6 s (Mandelbrot) and 1.1 s (Kleinian) to compile, drawing within a quarter of `base4`.

Defects, majors first; reproduce each on `dist/v7a.html` first, because round 6 may already have cured or
changed some (solids-1 through the new meaning of the skip count, mesh-1 through the colour rule for volume
samples):

- **kleinian-1 (major):** a trap that is the solid gives sliced, torn balls on Kleinian entries without the
  third map. Find the cause (the tester suspects the trap-solid distance jumping where the search changes map
  or cell while `uK3` is off) and cure it, or shorten the step there. Entries 3 and 24 show it; 0 and 21 do not.
- **solids-2 (major):** Trap thickness at the low end of its dial makes the solid vanish instead of thinner
  (the rule that fades layers thinner than two pixels takes the large first pieces too). A thin shell must stay
  a thin shell; only the late, fine layers may fade.
- **solids-1 (major):** black picture at skipped steps 0 in Mandelbrot mode. Must be gone.
- **mesh-1 (major):** a model's colours must match the picture's (the mesh tester's scripts
  `out/t6/mesh/drive.py` and `check.py` measure the hue difference; the Kleinian view and trap solids already
  match). The cut face too: one colour rule for the picture and for the model.
- solids-5 (ragged holes at higher skips, off-centre traps, small radius), solids-4 (Point, Line and Ray look
  alike), solids-3 and solids-6 (hints that say what really changes the object; a note for the thin shapes),
  flat-2 (leave "How quickly the orbit settles" out in Kleinian mode or give it a measure), flat-3 (the cut
  face's "How deep inside" should match the 2D view or the label should not promise it), flat-5 (the first
  inside colouring should not make the set look like a hole), flat-4 (find out whether it is the iteration
  limit; if so a hint), words-4 and words-5 (rays that run out of steps with the rough estimate), walk-2 (a
  plain sentence while the graphics context is lost).
- flat-1 is accepted: the Kleinian 2D outline changed because the pearl distance is now exact. No action.

Same rules as above (own files only; `--base base7a`; scripts under `out/r7/engine/`; notes in
`notes/r7-engine.md`; the smoke test that is current when you finish must pass). Reference pictures from
`dist/v7a.html` first, for everything that must not change: the 2D view at the opening settings and every 3D
picture not named in a defect. Time: aim for 60 minutes, stop at 80.
