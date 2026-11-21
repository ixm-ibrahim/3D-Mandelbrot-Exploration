# approaches: what was built, what it is called, what the UI has to wire

Files: `src/js/10-approaches.js`, `src/js/20-formula.js`. Companion note: `notes/inversions.md` (the derivation,
the numbers, and sentences for the page). Tests: `tests/approaches.html` + `tests/approaches.json` (maths and
shader parity, runs on its own) and `tests/approaches-page.json` (drives a built page).

## What changed

1. **"Mercator" is now "Sphere inversions"** (`id: 'mercator'` unchanged). Its texts are written around the
   sum of inversions; "rebuilt by eye" is gone. `formula(p, n)` shows the inversion form with the real numbers
   in it (v⁸ = |v|⁸ · [1 + 8·inv(Σₖ Rₖ·inv(d − ωₖ))] with d = v/|v| and k = 0 … 7), the one-more-inversion
   form for negative whole n, and the closed form for fractional n.
2. **Planes** go from 1 to 8, with a note that the count is a free choice (2p fins whatever the power).
3. **Turn and lift** for the sphere-inversion approach: ζ → e^lift · e^(i·turn) · ζⁿ. The turn works with one
   plane only (its dial is hidden otherwise, and the value is ignored); see "Decisions" below.
4. **Phases for both Mandelbulbs**, in degrees, added after the angle is multiplied: `lat`, `lon` for the
   equator version, `theta`, `phi` for the classic. A classic θ phase of (1 − n)·90° turns the classic
   formula into the equator one exactly; the page says so and the test checks it.
5. **Negative and fractional powers** in `pw`, `sqr`, `mul` and `MATH` for every approach. Everything stays
   finite: lengths stop at e⁴² ≈ 1.74e18, the origin under a negative power lands there along +x.
6. **All approach texts** (`formula`, `roundNote`, `crush`, `smooth`, `slice`) depend on n and on the offsets.
7. **Formula compiler**: understands pasted glyphs (z², z⁻ⁿ, ·, ×, −, ÷, π), refuses a division by a typed
   zero in words, and keeps scalar powers and scalar divisions finite.
8. **Two negative-power presets**, with camera hints, an optional cut and a short note each.
9. **The "fixed spheres" variant was investigated and left out** (it is not a stable object; numbers in
   `notes/inversions.md`, script `notes/fixed_spheres.py`).

## Names added or changed

In `10-approaches.js` (JavaScript, top level):

| Name | Meaning |
|---|---|
| `APR_LOGCAP` | 42: the log of the largest length a power may return |
| `aprPow(r, n)` | r to the power n, finite: never above e⁴², and r is never taken below 1e-30 |
| `aprRad(deg)` | degrees to radians, treating a missing value as 0 |
| `inversionPower(v, n)` | the sphere-inversion power written as the literal sum (whole n, either sign); for checks |
| `GL_APR` | shader text shared by every approach: `aprPow`, `aprCap`, `aprDiv`, `aprSPow`, `APR_LOGCAP`, `APR_CAP` |
| `aprIs, aprWhole, aprNum, aprDeg, aprSup, aprWrap, aprPlus, aprPole, aprTear, APR_HALF, APR_LINE, aprPasses, aprTurned, aprMercTurn, APR_INVERSION` | private wording helpers |
| `MATH[id](v, n, q)` | unchanged signature; `q` may now carry `turn`, `lift`, `lat`, `lon`, `theta`, `phi`; `q` is optional |
| `foldk` | unchanged |

Shader function names inside the approach code were given the prefix `apr` so they cannot collide with other
modules: `aprFold, aprMmul, aprMpw, aprMsq, aprTurn` (sphere inversions), `aprSpin` (lathe), `aprSph` (both
Mandelbulbs). The four contract functions `mul, pw, sqr, cmap` are unchanged in name and signature.

Approach parameters (`S.param[id][key]`, and the order is the order in `uA`):

| Approach | key | uA | Range, default | Meaning |
|---|---|---|---|---|
| mercator | `planes` | x | whole 1 to 8, 2 | planes through the x-axis that carry the flat set |
| mercator | `turn` | y | −180 to 180 (typed −360 to 360), 0, animate, shown when planes < 2 | degrees added to the longitude at every power |
| mercator | `lift` | z | −2 to 2 (typed −6 to 6), 0, animate | added to the Mercator latitude at every power |
| lathe | `spin` | x | odd −7 to 9, 1 | unchanged |
| bulb | `lat` | x | −180 to 180, 0, animate | degrees added to the latitude at every power |
| bulb | `lon` | y | −180 to 180, 0, animate | degrees added to the longitude at every power |
| classic | `theta` | x | −180 to 180, 0, animate | degrees added to the angle from the z-axis |
| classic | `phi` | y | −180 to 180, 0, animate | degrees added to the angle around the z-axis |

The sphere-inversion `params` list also holds two `note` specs: one always shown (the planes explanation) and
one with `when: p => p.planes >= 2` (why there is no turn dial).

Approach object fields, as the scorecard calls them:
`formula(p, n)`, `roundNote` (a string for split, a function `(p, n)` for the others), `crush(p, n)`,
`smooth(p, n)`, `slice(ok, p, n)`. `n` defaults to `S.n` when left out, so the baseline scorecard still works.

In `20-formula.js`:

| Name | Meaning |
|---|---|
| `PRESETS` | eight entries now. Optional fields: `target`, `dist`, `yaw`, `pitch` (camera, radians), `cut` (number: open with the solid cut at that height), `note` (one to three sentences about the picture) |
| `aprPlain(text)` | puts pasted glyphs back into typed form; `compileFormula` calls it first |
| `APR_SUPER`, `APR_TYPED` | the glyph tables it uses |
| `compileFormula(text, allowZ, n2)` | same signature. Its output may now call `aprDiv(a, b)` and `aprSPow(a, b)`, which every approach's shader text defines |

New presets:

| name | eq | z0 | hints |
|---|---|---|---|
| z⁻ⁿ + c  (negative power) | `z^-n + c` | `c` | target (0,0,0), dist 6.5, note |
| z² + c·z⁻²  (power against pole) | `z^2 + c*z^-2` | `4*c + 0.25` | target (0,0,0), dist 1.7, yaw −1.0, pitch 1.1, cut 0, note |

## What the UI integrator must wire

1. **Approach panel.** Keep building each approach's controls with
   `buildControls('pd-' + id, a.params, S.param[id], () => refresh(true), { idPrefix: 'par-' + id + '-', group: 'approach' })`.
   The specs use `when` on a dial and on a note, `animate`, `help`, `lo`/`hi` and `int`; nothing else is needed.
   The formula line (`a.formula(S.param[id], S.n)`) is now up to three sentences: it has to wrap.
2. **Wording.** Anything on the page that still says "Mercator" as the name of the approach should say
   "Sphere inversions". The lede and the closing section can take their sentences from the end of
   `notes/inversions.md`. The last paragraph of the footer ("cannot be built from inversions near that
   plane") is now false and has to go.
3. **Presets.** When a preset is chosen: set the equation and start value as now and call `resetCam(preset)`
   (the camera module already reads `target`, `dist`, `yaw`, `pitch`). Then, new:
   - `cut`: `S.cutOn = preset.cut !== undefined; if (S.cutOn) S.cut = preset.cut;` and sync the slice controls.
   - `note`: show `preset.note` under the preset drop-down, hide that line when there is none.
4. **Equation hint text.** Worth adding one sentence: "Turn, lift and phase dials act wherever the formula
   takes a power, a division included." The formula box also accepts z², z⁻ⁿ, · and − as printed.
5. **Power dial.** −8 to 10 as planned. No approach needs anything special at negative n.
6. **Tests.** `tests/approaches.html` needs nothing from the page. `tests/approaches-page.json` drives a built
   page through these ids: `ap-<approach id>`, `mode-m`, `mode-j`, `eqPreset` (option values are preset
   indices, a negative value is "My own formula"), `glfail`, `eqErr`, and `window.squaringLab.{S, refresh, idle}`.
   If any of those change, change the script with them. Optional: add `MATH, APPROACHES, PRESETS,
   compileFormula, inversionPower` to `window.squaringLab` so the console can reach them.

## Decisions worth knowing

- **Turn with one plane only.** With two or more planes the folds glue together points that are mirror images
  in y. That is invisible only while the power itself has that mirror symmetry, and a turn removes it. The
  result was a solid torn into striped sheets (`out/approaches/08-merc-turn15.png`, `02-merc-turn60.png`), so
  the dial is hidden and ignored unless planes = 1. The lift keeps the symmetry and works everywhere.
- **Offsets act on powers, not on products.** `mul` is unchanged. A division is a product with the power −1,
  so it does pick up the offsets. `c·z·(1 − z)` has no power in it and ignores them.
- **In Mandelbrot mode with zⁿ + c, a turn or a longitude/φ phase only turns the whole solid** about the
  z-axis (by −φ/(n − 1)). It changes shapes in Julia mode and in formulas with more than one term in z.
  The dials that reshape the Mandelbrot solid are the lift, the latitude phase and the θ phase.
- **A lift, latitude phase or θ phase takes the flat set out of the plane z = 0.** The slice text says so and
  tells the user how to get it back.
- **Split at a negative power.** The plane z = 0 is made of zero divisors, which have no reciprocal. The real
  factor is kept at 0 exactly on the plane so the flat slice survives; any point just off it is sent away.

## Checks run

- `python tools/shot.py --url tests/approaches.html --actions tests/approaches.json`: 76 of 76 pass. Plane
  parity for n in {−3, −2, −1, 2, 3, 8} (worst 2.6e-15), the inversion sum against `MATH.mercator` (table in
  `notes/inversions.md`), offsets, the turned flat set, 1,035 text strings, every preset through
  `compileFormula`, and the shader against `MATH` on a float render target (worst 2.4e-4, all finite, largest
  component 1.91e18). Output: `out/approaches/parity.txt`.
- `python tools/shot.py --url dist/approaches.html --actions tests/approaches-page.json`: all 40 approach and
  preset pairs compile and draw, and zⁿ + c draws at ten powers from −8 to 10 in both modes under every
  approach, with no console errors. The same passes with the shader module as it stood mid-round
  (`out/approaches/page.txt`, `page-s.txt`).
- Pictures in `out/approaches/`: `05`/`06` (4 and 8 planes at n = 8: 8 and 16 fins), `03`, `04` (lift),
  `20` to `25` (phases; `22` and `24` are the same picture, as claimed), `60` to `67` (the panel at 1400 and
  375 px), `63` (scorecard at n = −2 with the in-progress measure module), `70` to `79` (negative powers on the
  in-progress shader), `smoke-*.png` (the standard smoke script on my build).

## Known limits

- Above n = 10 a step can exceed 1.74e18 before the orbit has left the escape radius; such values are held at
  the cap, where the baseline let them overflow. Neither gives a good distance there. n up to 10 is clean.
- `inversionPower` needs a whole n. The drawn rule is its closed form and takes any n.
- For fractional n every approach tears along the half-plane behind the z-axis (the lathe: along the negative
  x-axis), as zⁿ does in the plane. The texts say so; nothing hides it.
- Under a lift, a Julia set can turn to dust because its c falls outside the lifted Mandelbrot solid
  (c = (−1, 0, 0) is empty from a lift of about 0.2). That is the maths, not a drawing fault.
- What a negative power looks like is decided by the shader module's rule for which side is solid. On the
  baseline shader zⁿ + c from 0 with n < 0 draws nothing and the preset from c fills the view. On the shader
  as it stood mid-round both draw a compact star, which is what the preset's camera hint is tuned for.
