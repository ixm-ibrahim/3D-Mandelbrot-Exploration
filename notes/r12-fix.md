# Round 12, fixer

Page: `dist/r12-fix.html`, built with `--base base12a` and the round's files (never 25-colour, 30-shaders, 40-render).
`dist/r12-fix-before.html` is the same build before any change (byte for byte the checkers' page).
Scripts, logs and pictures: `out/r12/fix/`.

## Reproduced before changing anything (on `r12-fix-before.html`)

`out/r12/fix/before-maths.log`, `sweep.log`, `before-buttons.log`, `before-tilt90.png`, `tilt-90.png`.

- M1 real. Twisted square, Mandelbrot solid: at tilt 90, 1,411 of 60,000 random c in the ball of radius 2.6 stay
  bounded, the farthest at 1.80, none beyond 2, 0 of 20,000 between radius 3 and 300 (tilt -90: farthest 1.75).
  Sweep over 13 tilts, 80,000 points each: none beyond radius 2 at any tilt; farthest 1.33 to 1.38 at tilts 0 to 40
  and 120 to 180, 1.76 to 1.81 at tilts 60 to 105. Picture at 90: one fat body with one spike, whole in the frame;
  at -90 a fat body with three spikes. The highest point is not at 90 (1.07) but near 105 (1.37), so the page does
  not say "tallest".
- m1 real: tilt 180 equals the quaternion square with z mirrored at n = 2, 4, -2 (1.5e-15) and the plain one at
  n = 3, 5, -1 (2.4e-15).
- m3 real: at tilt 40 the plane y = 0 misses the complex square by 3.06 and leaves the plane by 2.2.
- m4 real: Bulbs about the axis, 455 grid points of the flat Mandelbrot set lifted by 1e-8: 217 still bounded at
  multiplier 5, 300 at -3 (449 at 1).
- m5 real: pinch, 2 planes, n = 3 and 5: all 500 seam points land in the seam plane, off the x-axis; n = 2 and
  3 planes n = 4: all on the x-axis.
- m6 real: Pillow smooth 2,500 of 2,500 points off (0.80); Bulbs multiplier 2 and 4 off (1.6).
- m8, the hidden pair: q times the copy with its two hidden directions turned together by +2 x tilt gives the rule
  to 3.6e-15.
- W1 real: from the Kleinian view Back to one plane goes to the Julia set and resets the camera.
- W2 real: with two planes in use and Planes at 4 the button read "As it was found: two planes".
- m2 and m7 not measured again by me: the texts now say what the checkers measured (check3.json, probe2.log).

## What changed

`src/js/10-approaches.js` (texts only, no rule or shader touched)
- Twisted square: tag, help of the Tilt dial, note, about, crush and smooth rows, slice sentence (M1, m1, m2, m3,
  m8, W4).
- Blended planes: "for an even power" in note, help and about (m5); the options of Blend curve are called
  "Gentle start and end" and "Gentler start and end"; the formula line says "a weight" (m8); about says the 3D
  skin stands a little outside the true set (m7, the checker's number).
- Bulbs about the axis: "sheet with no thickness" is now "over about half of the flat Mandelbrot set at 5 (or 3),
  about a third at -3" (m4); the two sine sentences of the helps are in words (m8).
- Pillow: note and rows in plainer words (m8); about says the 3D skin stands off by up to 0.3 (m7).
- Mandelbulb, classic: "with every dial at its starting value" (m6, W3).

`src/body.html`
- Lede (m6, W3); "Sphere inversions, one plane" where the entry is meant (W5); Back to one plane sentence (W1);
  twin buttons renamed "Twin of Sphere inversions, one plane" and "Twin of the quaternion square" (W4, W5);
  twin answer "at power 2" (m1); the two new answers (M1, m1, m2, m8, W6).

`src/js/75-presets.js`: `juliaFoundWords` says "As it was found: Planes at 2" when the two-planes entry is
already in use (W2).

`out/r4/page/make_smoke.py` -> `tools/smoke-v12.json` (60 steps, was 58): expected words follow the page; old
wordings are searched for; and for T1: the every-entry step compares 408 probes between all entries and fails when
two are the same (one pair left out by design: the Julia set c = -1 of the quaternion square and of Bulbs about
the axis); the Approach reset step moves the drop-downs first and reads what every control shows; the Figure 4 step
reads 660 probes before and after Back to one plane; a new pair of steps tries every choice of every drop-down
in the Approach list. Edits are in `out/r12/fix/edit_smoke.py`, `edit_smoke2.py`, `edit_smoke3.py`; the file as it
was is `out/r12/fix/make_smoke.before-fix.py`.

Found while doing T1: the 165 probes are too coarse. In the test's camera the Julia sets for c = -1 of Sphere
inversions, one plane and of the twisted square hit the same 165 probes, while 54 of 1,320 differ
(`out/r12/fix/pair.log`, `pair-julia-mercator.png`, `pair-julia-tilt.png`). A probe costs about 20 ms.

## Left as it is

- W7 (group "Found with two planes" holds 6 entries, 15 record two planes): old behaviour, follows ROUND12 item 2.
- m7, the skin itself: belongs to the shader files.
- `docs/ROUND12.md` still holds the wrong facts (lines 50 to 52 and 56 to 57). Not my file.
- "A polynomial." in the scorecard rows of the older entries (Lathe, Split, Bulbs) is unchanged; the twisted
  square's row adds "built from plain multiplying and adding".
