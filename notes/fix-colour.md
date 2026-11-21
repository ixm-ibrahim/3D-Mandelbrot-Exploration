# colour fixes (`src/js/25-colour.js` only)

Test page: `python build.py --name fix-colour --base base2 --use src/js/25-colour.js` -> `dist/fix-colour.html`.
Pictures and scripts: `out/fix/colour/` (`sheet.py <plan>` renders a contact sheet; the plans are listed in it).
`dist/fix-colour-base.html` is base2 untouched, for "before" pictures.

## What changed, and why

1. **The page opens with what the user asked for.** `COLOUR_CONTROLS` defaults: colour by orbit trap, trap shape
   sphere shell, "how near it came, as a glow", palette Rainbow, reversed. (`mode 0, trap 5, by 4, pal 8, rev true`.)
2. **Shell radius default 0.7 -> 1.** Tuned by picture (`sheet-tuneA-dark.png`: radius 0.7 / 1.0 x glow width
   1 / 2.5 on the Mandelbrot, the Basilica, the Cauliflower and the Kleinian view). At 0.7 the rounder Julia sets
   (Cauliflower) came out one flat blue, because their orbits stay about 0.3 away from that shell. At 1 the
   orbits of all three sets keep crossing it, which draws rings and seams everywhere. Centre stays at the origin
   (both families are centred there) and the glow width stays at 1 (2.5 washed the Mandelbrot out to yellow).
   Opening pictures: `sheet-open-dark.png` (after) against `sheet-user-base-dark.png` (the same settings on the
   old build).
3. **Glow no longer one flat colour (p3-1).** Cause: the glow had one fixed width, `exp(-2.4 * sqrt(d))`, which is
   right for a trap the orbits keep crossing (planes, shell; in a flat slice any line or circle) and has long
   since faded at the distances a thin trap is ever passed at (a point anywhere; a line, ray, cross or ring in
   3D). Fix, two parts:
   - a new dial **Glow width** (`S.colour.glow`, default 1, shown only for glow). The distance is divided by it.
   - thin traps get their own profile, chosen in `setColourUniforms`: width times `COL_GLOW_THIN` (1.5) and the
     fall-off `exp(-2.4 * (d / w)^0.75)` instead of `^0.5`. Planes and shell in 3D, and everything except the point
     in the flat slice z = 0, keep exactly the old formula at width 1, so those pictures have not moved.
   Before / after, every trap shape with glow: `sheet-glow-all-before.png`, `sheet-glow-all-after.png`
   (rows: Mandelbrot, Basilica Julia, Kleinian), `sheet-glow-2d-before-dark.png`, `sheet-glow-2d-after-dark.png`.
   Still weak, and why: **Point + glow on the Basilica Julia** with the trap left at the origin. Every orbit
   on that solid makes its nearest pass to the origin at nearly the same distance (about 0.62, the set's own
   nearest point), so there is nothing to show whatever the width; moving the trap centre (x = -1) or raising
   "Colour bands, how many" brings it to life. A real cure would be to measure the range of nearest distances
   in the picture and stretch the glow over it, which needs a read-back in the renderer.
4. **`trapDist(vec3 v)` is now a pure function of the orbit point** (it used to take the offset from the centre),
   and `trapAdd` uses it. See "Names" for its exact meaning. This is the hook for next round's "the trap shapes
   the solid".
5. **Ray differs from Line as soon as it is chosen (p3-2).** Default direction +x instead of -x.
6. **"The side it came nearest on" with Line or Ray (p3-5).** Cause: the side was read from the whole offset to
   the trap centre, which for a line is mostly the position along the line. New `colSide()`: around a line or a
   ray the side is the angle round its axis (one turn = one palette period, no seam). Other shapes unchanged.
7. **Three tones (p3-4).** The fourth tone took over wherever the orbit stayed more than 1 from the origin, which
   is everything outside the unit ball. It now comes in gently (`0.5 * smoothstep(0, 2, w)`).
8. **Planes = Cross and Ring = Shell in the flat slice (p3-3).** A note in the Colour section says so and how to
   tell them apart. The picture is untouched.
9. **Direction of the last step is speckle on a solid (p3-6).** A note says so and points to the 2D view and
   the Kleinian set, where it works. The colouring itself is unchanged.
10. **Palette menu order (p3-7).** Warm and cool take turns at the top (Sunset, Electric, Fire, Ocean, Aurora,
    Ember, ...). Palette numbers are unchanged.
11. **2D view far out (p8c-3).** `flatColour` fades the outside colour into the stage between 40 and 120 units
    from the centre. The 2D view's own range ends before that (40 units top to bottom at its farthest), so no
    picture inside the default zoom range changes; only a widened limit shows it.
12. **2D view of "Leaning 30 degrees, seen across" (p8b-6).** With the new opening colours the outside is blue
    to violet with rainbow arcs against the cream solid (`sheet-k16-dark.png`, first tile). See "Not fixed" for
    the old combination.

Nothing else in the 2D view was restyled: for every trap except the point, the glow, the bands and the other
"colours by" choices compute what they computed before.

## Names

JavaScript, top level (all new ones prefixed `col` / `COL_`):
- `colGlowOn(c)`: `when` test, glow is the chosen "colours by".
- `colOrbitsFlat()`: true when every orbit stays in the plane z = 0 (2D view, slice height 0, and for the Kleinian
  set `k.cz === 0 && k.mz === 0`). Used for the planes switch (as before) and to tell thin traps from crossed ones.
- `COL_GLOW_THIN` = 1.5: how much wider a thin trap's glow is.

State: `S.colour.glow` (number, default 1). Created by `specDefaults(COLOUR_CONTROLS)` like the rest. A missing
or non-positive value is read as 1, so older saved colour settings still work.
Changed defaults: `trap 5, by 4, ray 0, radius 1, pal 8, rev true`.

Controls: `col-glow` (dial, with `col-glowNum`), three new notes.

Shader:
- uniforms `uGlowK` (1 / sqrt(width)) and `uGlowP` (1 = the old fall-off, 1.5 = thin traps), set in `setColourUniforms`.
- `float colSide(vec3 q)`: private.
- `float trapDist(vec3 v)`: **the plain distance from the orbit point `v` to the trap shape in use.** `v` is in the
  orbit's own coordinates, the same point the renderer hands to `trapAdd`. It reads only `v` and the uniforms
  `uTrap, uTrapC, uTrapR, uTrapAx, uTrapOff`, writes nothing, and those uniforms are set for every colour mode, so
  it can be called from anywhere at any time. With q = v - centre (`tx, ty, tz`):
  - Point: |q|.
  - Cross: distance to the nearest of the three lines through the centre along x, y and z.
  - Line: distance to the line through the centre along the chosen axis (`axis`).
  - Ray: distance to the half line from the centre toward the chosen direction (`ray`); behind its start that
    is the distance to the centre.
  - Planes: distance to the nearest of the three planes through the centre parallel to the coordinate planes.
  - Sphere shell: | |q| - radius |, distance to the sphere surface, inside or outside.
  - Ring: distance to the circle of that radius around the centre, lying parallel to the xy-plane.
  - Three tones: no shape of its own; the three coordinate planes through the ORIGIN (the centre is ignored).
  In 3D `uTrapOff` is zero. In the 2D view of the slice z = 0 with trap centre z = 0 it removes the plane z = 0
  from Planes and Three tones (that plane is the picture), exactly as before.

## For whoever builds "the trap shapes the solid"

- `trapAdd` returns at once when the colour mode is not "Orbit trap" (`uColMode > 1`), and `gNear.w` holds the
  nearest distance only in trap mode. Call `trapDist(v)` yourself inside the orbit loop and keep your own minimum.
- `trapDist` has ifs on a uniform but no loops: about one square root per call.
- The solid "orbit comes within thickness t of the trap" is `min over steps of trapDist(v_k) - t <= 0`, but that
  is not a distance estimate in space: it needs dividing by the orbit's stretch (the `dr` the engine carries).

## Not fixed / left as it is

- Point + glow on a Julia set with the trap at the origin (see 3).
- Kleinian view, shell glow: the two wall spheres stay one colour (violet), as they did when the user chose
  these settings. Their orbits are recorded near y = my (about 2), far from a shell around the origin. Setting
  "Trap centre, y" to 1 brings the glow onto the walls (`sheet-tuneK-dark.png`). Not made the default: the centre
  dials are shared by all three kinds of picture, and shifting the centre only in Kleinian mode would also move
  the planes trap there.
- p8b-6 with the OLD colours (planes, bands, Sunset): still pale yellow on cream for that one preset. The orbits
  in its open gaps end on a trap plane, so "touching" is the true reading. Not chased further because the user
  asked for the 2D view to stay as it is.
- p3-6: the colouring is still speckle on a solid; only the note is new.
- p3-4, three tones: the 2D view now shows its tones (`sheet-minor-all.png`, fifth row), but on a 3D solid it is
  still a muted mauve and on the Kleinian set still one flat orange. Its thresholds assume orbits that circle
  the origin; a livelier version needs a redesign of that mix, not a tweak.

## Checked

- `tools/smoke.json` on `dist/fix-colour.html`, run after the last edit: 20 steps, exit 0, no console errors
  (`out/fix/colour/smoke.log`).
- Colour section rules through the real drop-downs (`panel.json`): the glow dial hides for bands and returns
  for glow; the speckle note shows for "Direction of the last step" on a solid; the planes / ring note shows in
  the 2D view only, and not for the shell; "Reset this section" restores the new defaults. `panel-open.png`.
- 2D view at its farthest default zoom (height 40), old colours: pixel-identical to base2 (largest channel
  difference 0). At height 400 the stripes now fade into the stage (`sheet-far.png`: left before, right after;
  top row height 400, bottom row height 40).
- Sheets in `out/fix/colour/`, all at the page's Fast quality unless named otherwise: `sheet-open-dark.png`,
  `sheet-open-light.png`, `sheet-open-balanced-dark.png` (Balanced quality), `sheet-user-base-dark.png`,
  `sheet-tuneA-dark.png`, `sheet-tuneK-dark.png`, `sheet-glow-all-before.png`, `sheet-glow-all-after.png`,
  `sheet-glow-2d-before-dark.png`, `sheet-glow-2d-after-dark.png`, `sheet-minor-all.png` (rows: side, ray,
  three tones, preset 16 in 2D, the old default colours).

- `sheet-more-dark.png`: the opening colours on the classic Mandelbulb at n = 8 (green and cyan with orange
  rings, good), on a negative power (good) and on the Julia mosaic. In the mosaic most cells are plain violet
  balls: where a cell's Julia set is larger than its cell it is cut off by a ball, the points on that ball are
  inside the set, and their orbits fall inward, far from the shell. Not looked into further.

Not checked: the phone layout of the Colour section with the new dial and notes; Fine and Ultra fast quality;
the glow dial moved by real mouse input; trap shapes with glow in the light theme.
