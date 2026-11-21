# fix-maths: what changed in `10-approaches.js`, `20-formula.js`, `60-measure.js`

Test page: `python build.py --name fix-maths --base base2 --use src/js/10-approaches.js src/js/20-formula.js src/js/60-measure.js`.
Scripts, logs and pictures: `out/fix/maths/` (`checks.json`, `split-before.json` / `split-after.json`, `presets-j.json`,
their `.log` files, `sheet-split.png`, `sheet-presets.png`, `panel-mercator.png`, `panel-split.png`, `card-*.png`).
The `edit*.py` files there are the one-off scripts that made the edits; they are not needed again (and `edit20b.py`
wrote one regular expression wrongly, which was then corrected in the source by hand: do not rerun it).

Final runs on the finished build: `tools/smoke.json` exit 0 with no console errors (`smoke.log`), `checks.json` 10 steps
exit 0 (`checks.log`), `tests/approaches.json` 76 of 76 (`parity.log`).

## 1. Split approach at negative powers (p15-4, p15-3)

**Cause.** The old rule took the two reciprocals side by side: `v^-n = (1/(x + iy)^n, 1/z^n)`. `1/z^n` has no value
on the plane z = 0, so every point near that plane was thrown to infinity (with a special case that kept the plane
itself at 0). Two things followed:
- Mandelbrot mode: the whole slab |z| < 1/8 counted as "thrown out", which is the solid at a negative power. That
  is the endless floor, with the flat star standing on it as towers.
- Julia mode: the far-away test point the shader uses to decide which side is solid was itself thrown out after two
  steps (its z part goes small, then huge). So the split approach drew the other side from every other approach:
  hairlines in 3D, and an inverted 2D slice at n = -3 and -2.5 (p15-3). At n = -2 with c = -1 all approaches agree
  only because the test point lands on 0 there under every rule.

**Fix.** For n < 0 the split power is now the positive power followed by one sphere inversion with a mirror:
`v^-n = (X, -Y, Z) / (X² + Y² + Z²)` with `(X + iY, Z) = ((x + iy)^n, z^n)`. This is what a negative power already is in
the other four approaches (positive power, then one inversion). It is finite everywhere except the origin, continuous
across the plane z = 0 (no special case left), equal to complex z^n on that plane, and far points now come back to c
as they do under the other rules, so the shader's decision is the same for every approach.
`MATH.split` and the shader `pw` in `GL_SPLIT` were changed together; `mul` and `sqr` are untouched; positive powers
are untouched.

**Evidence.**
- `checks.json` step 1: split on z = 0 against complex z^n for n = -8, -3, -2.5, -2, -1, -0.5 (300 points each): worst
  relative error 1.8e-15. Stepping from z = 0 to z = ±1e-6 moves the result by at most 1.1e-5 (it used to jump to 1e12).
- `tests/approaches.json` (the approaches' own parity page, run on the edited files): 76 of 76, including "shader pw()
  agrees with MATH.split: 9.2e-5 over 10 powers" and "stays finite at the origin, on the axes and at 1e18".
- 2D slice, Julia c = (-1, 0, 0), n = -3, split against sphere inversions: 92.9% of pixels differed before, 0 differ now
  (`before-split-j-n-3-flat.png`, `after-split-j-n-3-flat.png`, `after-merc-j-n-3-flat.png`).
- 3D Mandelbrot n = -2 and -3: a bounded solid (a rounded block at the centre with curved fins) where the floor was
  (`before-split-m-n-2.png`, `after-split-m-n-2.png`, `sheet-split.png` right column).
- 3D Julia n = -3: solid rounded pieces where there were hairlines. At n = -2 and -4 the split picture now shows the
  same speckle and dust the other approaches show there. That is defect p15-2 (engine), not the split rule.

**Texts** of the split approach follow the new rule: formula line (`v⁻¹ = (x, −y, z)/|v|²`, and the general negative
form), about, roundNote (now a function: at n = -1 it is a single inversion with a mirror and the scorecard reports
roundness 100%), crush, smooth, slice. "ℂ × ℝ", "commutative", "zero divisors" are gone (text-12).
`notes/approaches.md`, section "Decisions worth knowing", last bullet ("Split at a negative power ... sent away") is
no longer true.

## 2. Sphere inversions panel wording (text-1, text-2, text-3, text-6, p9-3, p10-2, maths-1)

Texts only. The rule, its parameters, their keys and order (`planes`, `turn`, `lift` = uA.x, y, z) are unchanged.
- `about`: no symbols. Says in one sentence that the slice at z = 0 is exactly the ordinary 2D Mandelbrot or Julia set
  and that the 2D view shows it (p9-3), and in one more that slices at other heights are different shapes (the
  user's new remark; change or drop this sentence when the replacement approach arrives). Kučera kept, shortened.
- `formula`: every symbol on the line is named on the line (d, inv, ωₖ, Rₖ). "Mercator latitude" is now "the latitude
  as a Mercator map stretches it". The sentence still starts with three spaces and "with", which the approaches' own
  text test expects.
- Planes note: plain words, the user's own cases (4 planes for n = 8, 3 for 6, 2 for 4), "Fins come in pairs, so an odd
  power has no exact match" (p10-2), "No value is the correct one". It still says the count is a free choice, because
  in this rule it is. p10-1 (planes following the power) was not touched, as instructed.
- Lift hint: says it is this approach's version of the Mandelbulb's latitude phase and to press play (text-6).
- Turn hint (sphere inversions) and Longitude phase hint (Mandelbulb): now end with "Away from 0 the slice at z = 0 is no
  longer the plain 2D picture: it is that picture turned (Mandelbrot) or a different set (Julia)." (maths-1). The classic
  Mandelbulb's φ hint was left alone: its z = 0 slice is not the 2D picture to begin with, and its panel says so.

## 3. Other wording

- text-7: the scorecard sentence for a turned slice no longer prints "(it carries e^{iφ}·zⁿ)".
- text-11: preset names "zⁿ + c/z (with a division by z)", "z² + c·z⁻² (square against division)"; both notes rewritten
  without "pole", "orbit", "critical orbit".
- text-12: scorecard "Only the origin is crushed. That is why following the single point 0 is enough to decide whether c
  is in the set."; Lathe about: "the power of a quaternion (a number with three imaginary parts) with one part held at zero".

## 4. Scorecard at n = 0 (code-5)

Every approach's `crush` returns `['no', 'Everything is crushed onto one point.']` and `smooth` returns
`['ok', 'A constant.']` at n = 0, matching the "In the plane" column. Checked on the page for split
(`checks.json` steps 9, 10) and for all five approaches by calling the functions (step 1).

## 5. Large numbers in a formula (code-6)

`flt()` writes whole numbers of 1e15 and more as `1e+15` (a float literal the shader accepts). A typed number above
1e30 (including one that overflows to infinity) is refused with "The number 1e40 is too large. Numbers up to 1e30
work." Checked: `z^n + 1e15` compiles to `(pw(z, uPow) + vec3(1e+15, 0.0, 0.0))`.

## 6. The scorecard describes the power the equation takes (p15-7)

With the preset `z^-n + c` at n = 2 the picture is z⁻² + c, but the card and both step figures described squaring.
- `20-formula.js`: the parser now also reports the powers a formula takes of z. `aprParse(text, allowZ, n2)` returns
  `{ code, powers }`; `compileFormula` is `aprParse(...).code` (same signature, same output as before);
  `formulaPowers(text, n)` returns the exponents as numbers (`z^-n + c` at n = 3 gives [-3], `z^2 + c*z^-2` gives
  [2, -2], `z^n + c/z` gives [3, -1], `c*z*(1 - z)` gives [], `abs(z)^(n/2) + c` gives [1.5]).
- `60-measure.js`: `cardPower()` is the power the card and the figures describe: the first power the equation takes of
  z, or the dial's n when it takes none. `updateCard`, `powerF`, `drawStep2d`, `buildStep3d` use it instead of `S.n`.
  When it differs from the dial, a line at the top of the card says so (`#cardPowNote`, a `p.note` created by
  `buildCard()`): "The equation takes z to the power −2, so that is the power described here and in the two figures
  above. The dial shows n = 2."
- The page changes an equation without calling `refresh()`, so `drawStep3d` (already on `hooks.view`, which runs after
  every `touch()`) notices that the described power changed and rebuilds the figures and the card. Nothing is needed
  from the page for this.
- Checked on the page (`checks.json` steps 2 to 5, `card-preset-neg.png`): the card under the preset reads "A negative n
  turns the plane inside out", "The origin is thrown out to infinity", the 2D caption says "Angles are multiplied by −2",
  and going back to `z^n + c` hides the note and restores the n = 2 card.
- Not changed: the formula line in the approach panel (`f-<id>`, written by 80-ui.js with `S.n`) still shows the rule
  for the dial's n.

## 7. Equation presets: what is the preset and what is only a suggestion

The user asked that presets stop touching the camera, the iteration count and other settings. In `PRESETS`:

| Field | Status |
|---|---|
| `name`, `eq`, `z0` | **the preset**: the formula and its start value. Always applied. |
| `note` | text shown under the drop-down. Belongs to the formula. |
| `target`, `dist`, `yaw`, `pitch` | **suggestion only**: a first camera, tuned for the Mandelbrot solid at n = 2 with the default approach |
| `cut` | **suggestion only**: a height at which the solid is worth cutting open |
| `julia: { dist }` | **suggestion only, new**: camera distance for Julia mode. Only `z² + c·z⁻²` has one (4.8) |

No preset carries an iteration count, a power, a quality setting or a colour, and none should. The comment block above
`PRESETS` says the same. The page engineer decides which suggestions to apply; a preset is complete without them.
The note of `z² + c·z⁻²` used to say "It opens cut at z = 0"; it now says "It is worth cutting open at z = 0", which
stays true whether or not the page applies `cut`.

p15-8 (the two negative-power presets in Julia mode): the camera distance 1.7 of `z² + c·z⁻²` is a Mandelbrot hint that
`resetCam()` also applies in Julia mode. With `julia.dist` = 4.8 that Julia set is framed (`sheet-presets.png`, top left,
rendered by setting `cam.dist` by hand). `z⁻ⁿ + c` in Julia mode at c = (-1, 0, 0) is the speckled mass of p15-2 at
any distance (top right), so it has no Julia hint.

## Names added or changed

`10-approaches.js`
- `APR_MIRROR`: the n = -1 sentence for a rule that is one inversion with a mirror (split).
- `aprNone()`, `aprConstant()`: the crush and smooth cells at n = 0.
- `APR_SLICE_TURNS`: the sentence the turn and longitude-phase hints end with.
- `MATH.split(v, n)`, shader `pw` in `GL_SPLIT`: new rule for n < 0 (section 1). Same names and signatures.
- Split's `roundNote` is now a function `(p, n)` (the contract allows either).

`20-formula.js`
- `aprParse(text, allowZ, n2) -> { code, powers }`: the parser. `powers` holds one function of n (or null) per power taken of z.
- `formulaPowers(text, n) -> number[]`: those powers as numbers; empty when there are none or the formula does not parse.
- `compileFormula`: unchanged signature and result; now refuses numbers above 1e30.
- `PRESETS[i].julia`: optional `{ dist }` (suggestion only). Two preset names and two notes reworded.

`60-measure.js`
- `cardPower()`: the power the card and figures describe. `cardPow`: its cache `{ key, n, several }`.
- `cardRun.pow`: the power the card last described.
- `#cardPowNote`: element created by `buildCard()`.

No new fields in `S`, no new uniforms, no new controls.

## Needed from other files (all optional: everything above works without them)

- `src/js/50-camera.js`, `resetCam()`: apply an equation preset's `dist`, `yaw`, `pitch` only in Mandelbrot mode, and in
  Julia mode use `p.julia.dist` when the preset has one (p15-8). If the page stops applying camera hints altogether, as the
  user asked, nothing is needed here.
- `src/js/80-ui.js`, `refresh()`: `x.formula(S.param[x.id], S.n)` could pass `cardPower()` so the approach panel's formula
  line matches the card under a preset like `z^-n + c`.
- `src/js/90-boot.js`: add `formulaPowers` and `cardPower` to `window.squaringLab` if tests should reach them.
- `src/body.html` line 176 says the card is measured "at the current n". With section 6 it is "at the power the
  equation takes"; the card's own note covers the difference, so this is only a nicety.
- `src/body.html` footer paragraph on planes (p10-2, page group): add "Fins come in pairs, so an odd power has no exact match."

## Not done, and why

- p10-1 (planes following the power): ruled out for this round; the approach is being replaced.
- p15-8, noise of `z⁻ⁿ + c` in Julia mode: that is p15-2 (the shader's estimate for the inside-out solid).
- Classic Mandelbulb φ hint (part of maths-1): left as it is, see section 2.

## Things the next person should know

- The split solid at a negative power is no longer a prism: the inversion couples the height to the other two
  coordinates. That is the price of a bounded picture. Taken side by side, the "thrown out" set of ℂ × ℝ is unbounded
  whatever is done at the plane (slabs across, or an endlessly tall column), because a point is thrown out as soon as
  either factor is.
- `cardPower()` takes the first power written. For `z^2 + c*z^-2` that is 2, so no note shows at n = 2.
- `formulaPowers` only sees powers and divisions. A product such as `c*z*(1 - z)` squares z without a power sign and
  reports nothing, so the card keeps the dial's n there.
- The panel sentence "Slices at other heights are different shapes" was added because of the user's remark about the
  fractal coming apart away from z = 0. It describes; it does not fix. The fix is the replacement approach.
