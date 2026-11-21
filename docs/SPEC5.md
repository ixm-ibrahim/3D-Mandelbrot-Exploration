# Round 5: join, speed, texts

Read first: `docs/SPEC4.md` (the user's twelve points N1 to N12, verbatim, and the decisions), `docs/CONTRACT.md`
and `docs/CONTRACT4.md` (names and rules; still binding), and the round 4 reports in `notes/_r4_reports.json`
(five engineers: what they built, what they left, the names they added, their answers for the user) with their
write-ups `notes/r4-*.md`. The second prototype round for the 3D rule is in `notes/_lab2.json`.

## Where things stand

- `base5/` is the joined source of round 4, frozen: the five engineers' files, the Kleinian engineer's `GL_KLEIN`
  pasted into `30-shaders.js`, both preset lists re-embedded (26 Julia points, 34 Kleinian entries), and
  `tools/smoke.json` regenerated (`out/r4/page/make_smoke.py`: the wait for the picture job moved to the step that
  starts it; step 3 now waits up to 64 s for a new program).
- The joined page passes the smoke test: 27 steps, exit 0, no console errors, a real picture job and a real model
  job delivered (`out/me/smoke-v6a.log`). Test page: `dist/v6a.html`.
- It is NOT published, because it is much slower than the published Version 5 (which is `base4/`). Measured on a
  quiet GPU with `python out/me/perf.py <page> ...` (compile = a fresh scene program, least of 3; draw = the
  finished opening picture, least of 5; M Mandelbrot, J Julia c = -1, K Kleinian):

| Page | M compile | M draw | J draw | K compile | K draw |
|---|---|---|---|---|---|
| `base4` (published) | 1.7 to 1.9 s | 443 to 605 ms | 867 to 1422 ms | 0.60 to 0.63 s | 188 to 221 ms |
| `v6a-oldsh` (base5 with base4's shader and colour files) | 1.9 s | 695 ms | 1466 ms | 0.73 s | 183 ms |
| `v6a-si` (base5 with the shader engineer's small stand-in colour file) | 2.7 s | 1372 ms | 1922 ms | 1.1 s | 299 ms |
| `v6a-ts0` (base5 with `TRAP_SOLIDS = false` written into the shader source) | 9.0 s | 766 ms | 2518 ms | 7.7 s | 376 ms |
| `v6a` (base5 as it is) | 8.5 to 9.9 s | 1541 to 1548 ms | 1967 to 2289 ms | 6.0 to 8.5 s | 316 to 378 ms |

  What this says: the compile time is in the colour module (2.7 s with the stand-in, 9 s with the real one, in
  both programs); the trap solid code in the orbit loop doubles the Mandelbrot drawing time even while the trap
  solid is switched off by its uniform; the Kleinian picture draws about 70 percent slower.

## Decisions (orchestrator)

- **N1.** No new 3D rule ships. Two prototype rounds, six rules, none beats the one-plane rule (see
  `notes/_lab2.json`, `judge`). The default stays Sphere inversions with one plane. The two-plane setting stays
  as "earlier version" and is the picture of Figure 4 for a Julia set with c on the x-axis. The page says all of
  this plainly (text below) and offers a one-click way to that picture. No experiment approach is added to the
  list: the blended planes add nothing the planes dial does not already give.
- **Speed comes before anything else in the shader and colour files.** The page is published only when it is
  back near Version 5.
- **Programs may be specialised.** A scene program may be built for the colour settings in use (for example with
  or without trap solid code, with or without inside colouring), with those settings in the program key, so that a
  change of such a setting compiles a new program (shown as "Preparing the formula"). Rule: moving a dial never
  compiles; changing a drop-down or a tick box may, if the new program takes about 2.5 s or less.

## Owners this round

| Files | Owner |
|---|---|
| `src/js/25-colour.js`, `src/js/30-shaders.js`, and in `src/js/40-render.js` only what builds and keys scene programs (`sceneWant`, `sceneNow`, `sceneEntry` and what they need) | speed |
| `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`, `src/js/90-boot.js`, `data/julia-presets.json` (group headings only), the two notes of the Sphere inversions panel in `src/js/10-approaches.js` (`par-mercator-note1`, `par-mercator-note2`: text only), `out/r4/page/make_smoke.py` and `tools/smoke.json` | page |
| everything else, including `src/js/00-core.js` | nobody: leave alone, report what you need |

Build and test against the frozen copy, never with plain `python build.py`:

```
python build.py --name r5-<you> --base base5 --use <your live files>
PYTHONIOENCODING=utf-8 python tools/shot.py --url dist/r5-<you>.html --actions tools/smoke.json
```

Keep scripts, logs and pictures under `out/r5/<you>/`; write `notes/r5-<you>.md`. No git. The other engineer is
working at the same time on other files and uses the same GPU: run one `tools/shot.py` at a time, and take every
timing as the least of several, old and new back to back.

## Speed (engineer "speed")

Targets, measured with `python out/me/perf.py base4 r5-speed base4 r5-speed` (two rounds, back to back):

1. **Compile:** M at most 2.6 s, K at most 1.1 s, with the page's opening settings. With every new feature
   switched on (trap solid, inside colouring, cut face coloured) at most about 4 s.
2. **Draw, new features off:** M, J and K each within a quarter of `base4` measured in the same run.
3. **Nothing changes in the pictures.** The 2D view at the opening settings stays pixel-identical to `base4`
   (`python out/r4/shaders/flat.py` and `python out/r4/colour/run.py id` did this check in round 4). Every 3D
   picture stays the same as `dist/v6a.html` draws it, to within 2 of 255 per channel, for a set of at least 16
   scenes that you fix first and that covers: the opening view, a Julia set and the Kleinian view; trap solid off,
   "is the solid" and "is added"; three trap shapes; inside colouring on in the 2D view; the cut face coloured;
   Ultra fast and Fine; the mosaic. Make the pictures from `dist/v6a.html` BEFORE you change anything.
4. The smoke test passes on your final page.

What is known, to start from (the reports have the detail: `notes/r4-shaders.md` section 3, `notes/r4-colour.md`):

- Compile: every call from `main()` to a colour hook is one more copy of that hook's code for the compiler (ANGLE
  hands the whole program to the D3D compiler with every function inlined). `surfaceColour`, `flatColour` and
  `cutFaceColour` each pull in `colPick` or `colInside`, and through them `colTrapPick`, which is reached by four
  paths; `pal()` is written out about 34 times. `cutFaceColour` alone costs about 2 s. The orbit loop is not the
  problem (base4's whole `trapAdd` put back changed nothing). Ways out, yours to choose and measure: one call per
  pixel to one colouring function that every kind of pixel (lit hit, flat, cut face, raw) shares, with the
  cheap differences applied afterwards; one `pal()` per path, with the palette position chosen in the branches;
  compile-time switches (a `const bool` written into the source, as `TRAP_SOLIDS` already is) for inside
  colouring, the cut face and trap solids, so that a program without them does not carry their code. The tools
  `out/r4/shaders/variant.py` (build a page with a piece of the source replaced) and `out/r4/shaders/compile.py`
  are there to find which construct costs what before rewriting; use them first.
- Draw: with `TRAP_SOLIDS = false` the Mandelbrot picture draws in half the time, so build the program that way
  whenever `S.colour.solid` is 0 (the shader engineer's note says how: `sceneWant`, the program key, the
  signature in `sceneNow`), and do the same for the trap solid code in `GL_KLEIN`. Then find what is left of the
  gap to `base4` in J and K (suspects: the two extra queries per lit pixel for the fading tail, the extra turn of
  the loop, the exact pearl distance) and say what each costs; do not remove the ring cure or the exact estimate.
- Keep: one call site of `de()`; `gFade`, `gPix`, `gOnTrap` with their meanings; the 0.5 cap on the Kleinian step
  share; every uniform and control name.

After the targets are met, and only then, in this order: (a) the shader engineer's request that the colour module
decide "this hit is on the trap's part" from `gOnTrap` (copied in `colourCapture()`), so that trap solids keep
their colours at Fast and Ultra fast; (b) set `gOnTrap` and use `gPix` in the Kleinian trap solid; (c) the
Kleinian engineer's cure for colours that change with the quality setting (sketch in `notes/r4-kleinian.md`,
defect p5-6). Each of these needs before and after pictures.

Time: aim for 60 minutes, stop at 80 whatever the state, and say exactly what state that is. If the compile
target cannot be met in the time, deliver the best measured state that keeps the pictures the same; do not
deliver a faster page whose pictures changed.

## Page (engineer "page")

1. **Closing texts, "Questions from testing, answered".** Every paragraph marked `data-needs` now has its part:
   switch them on for good (remove the hiding machinery where a part can no longer be missing) and rewrite each
   answer so that it is true of the joined page and uses the labels the controls really have (read them from
   `dist/v6a.html`). Sources: `answers_for_user` of all five reports, and for N1 the text below. Corrections that
   must be in: the "stack of slices" (N12) was in the colouring, not the shape, and is cured for Mandelbrot and
   Julia pictures (the Kleinian view never had it); trap solids work in all three kinds of picture; a new
   approach or equation takes a moment to prepare; the first real test of saving a file from the published page
   is the user's (it could not be tried from the test bench). Plain words, short sentences, no jargon: the user is
   not a mathematician and judges by the pictures.
2. **N1, in the user's terms.** Replace the three answers on the Sphere inversions solid, the number of planes and
   the third map (and drop the pillow paragraphs and their hiding) with text that says:
   - The version tested had Planes at 2: the flat rule copied onto a second plane at right angles. The rule jumps
     across the plane y = 0, and the jump tears the solid unless c lies on the x-axis.
   - The page opens with one plane. That rule is forced in this sense: ask that lengths are squared, that the
     slice at z = 0 is the flat set, and that the rule keeps angles true on the sphere of directions, and one rule
     is left (with its mirror image), and it is this one. (A short argument of ours, not a published theorem.) It
     gives the "inflated" sets of Figure 3 in the paper: one smooth piece at every height, detail around one
     plane only.
   - "The plane should come from where the point starts" is the Lathe approach: every point uses the plane
     through the x-axis and itself. It is forced too, and clean, and it gives rings where one hopes for beads.
   - Figure 4 (beads around two circles) exists in the paper only for c on the real axis, and the paper says so
     ("so far the second construction is unfortunately limited to c ∈ R", page 444). Here the same picture
     appears with Planes at 2 and c on the x-axis, because a mirror symmetry of the set hides the jump.
   - Six new rules were tried in two rounds to get that look for every c without a jump: three "pillow" rules, a
     smooth blend of the two planes, bulbs about the x-axis and an angle-true pillow. None works. A rule that is
     exact on two planes at right angles and never jumps has to fold the sphere of directions over itself or wind
     it three times round the negative x-axis; the first gives a swollen mass and dust, the second rocks and
     fibres. So a Figure 4 for every c, and with it a Figure 4 Mandelbrot solid, is an open problem.
   - "Use third map" in the Kleinian section is the same kind of move as the paper's third generator: it is what
     lets a Kleinian group fill space instead of one plane. It is not the paper's group, and the squaring rules
     have no such switch.
3. **A one-click Figure 4.** Next to that answer, a button "Show Figure 4" that puts the page in Julia mode with
   c = (-1, 0, 0), power 2, Sphere inversions with Planes 2, Turn 0 and Lift 0, and frames the set; and a button
   "Back to one plane" that sets Planes to 1. Both go through the page's own setters, so every control shows the
   new state. Add one sentence to each of the two notes under the planes dial (`par-mercator-note1`,
   `par-mercator-note2`) that points the other way ("For the look of Figure 4 ..." / "... whole only while c is
   on the x-axis").
4. **Julia list.** The six entries that were found with two planes (Cracked Basilica, Split conch, Flint, Plated
   egg, Plated ball, Cracked gourd) move under their own heading, "Found with two planes", after the others. An
   entry still sets only c. Next to "Frame it" add a button "As it was found" that sets the planes and iterations
   the entry records (`planes`, `iter`); it is shown only for entries that record a value different from the
   current one. Nothing is removed from the list.
5. **A look-over of the new controls** at 1400 x 950 and at 375 x 812, dark and light: Save a picture, Save a 3D
   model, the new colour controls (trap solid; the 2D view's outline, glow and inside colours; cut face), the
   Kleinian list with its new group. Fix what is in your files; list the rest with file and line.
6. **Smoke test.** Add steps for: a trap solid ("Is the solid") drawing a picture that is not empty in Mandelbrot
   and in Kleinian mode; an inside colouring in the 2D view; "Show Figure 4" and "Back to one plane"; "As it was
   found". Keep the whole run under about four minutes. `tools/smoke.json` must pass on your page.

Time: aim for 45 minutes, stop at 65.

## Reports

Both engineers return the same fields as in round 4: summary, files_changed, done, not_done, names_added,
needs_from_others, answers_for_user, risks. Say what you measured and what you only reasoned; give the path of the
evidence for each claim.

## Found while round 5 ran: the mirror twins (orchestrator)

Every rule has a mirror twin: the same step followed by z -> -z. The page already offers it as the modifier
"flip z" (`S.flip = [0, 1]`; it is applied to z before each step, which is the same thing for a rule that is
mirror-symmetric in z). Points of the plane z = 0 do not notice, so the slice at z = 0 stays the flat set.

- For Sphere inversions (one plane, Turn 0, Lift 0) and the Lathe, a Julia set whose c lies in the plane z = 0 is
  the very same solid with and without the flip: the pictures match pixel for pixel (basilica and rabbit,
  `out/me/twin4/`, largest channel difference 0). For the Mandelbulb approach they differ a little.
- The Mandelbrot solid changes, because there c leaves the plane (`out/me/twin2-*.png`, `out/me/twin3-a.png`):
  - Sphere inversions: the thin lens becomes a tall body, and its slices at z = 0.15, 0.2, 0.3 and 0.5 keep a
    smoothed outline of the Mandelbrot set where the plain rule gives a round disc. Reason: beside the plane a
    height w grows as w' = 2|v| w + w0 with the plain rule and as w' = -2|v| w + w0 with the twin, so the plain
    solid thins to nothing at the edge of the flat set and the twin does not. This twin is the other rule of
    the "forced" pair (angle-true on the sphere of directions: 1 / conj(zeta)^2 in place of zeta^2).
  - Lathe: the Mandelbrot set in the plane z = 0 and the tricorn (the set of conj(w)^2 + c) in the plane y = 0,
    joined without a seam: three fins.
  - Mandelbulb: an intricate solid, fractal in every direction.
- In the paper's terms: its generator g1 is a sphere inversion followed by a mirror image, and in 3D that mirror
  image can be made in two ways that agree on the plane and differ by z -> -z.

None of this is Figure 4 (which needs the flat set in two planes for the same c). It is the nearest thing found
to "a seam-free solid that is 3D all the way through", so the page says so under N1 and offers it in one click.
The opening picture stays the plain rule: seen from above it is the recognisable Mandelbrot set.
