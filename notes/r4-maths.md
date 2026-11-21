# r4-maths: the maths module in round 4

Files edited: `src/js/10-approaches.js`, `data/julia-presets.json`. `src/js/20-formula.js` and `src/js/60-measure.js`
needed no change this round (they are identical to `base4/`). Nothing else was touched.
Scripts, logs and pictures: `out/r4/maths/`. Worked 23:29 to about 00:20.

Test pages (all from `base4/`):

```
python build.py --name r4-maths --base base4 --use src/js/10-approaches.js src/js/20-formula.js src/js/60-measure.js
python out/r4/maths/embed_private.py      # private copy of 75-presets.js with the new Julia data embedded
python build.py --name r4-maths-data --base base4 --use <the three files> --swap js/75-presets.js=out/r4/maths/75-presets.js
```

Last state, after the last source edit:
- `python tools/shot.py --url dist/r4-maths.html --actions tools/smoke.json`: exit 0, 27 steps, no console errors (`smoke.log`).
- The same on `dist/r4-maths-data.html` (my files plus the new Julia data embedded): exit 0, no console errors (`smoke-data.log`).
- `out/r4/maths/checks.json` (12 steps of my own, written by `make_checks.py`): exit 0, no console errors (`checks.log`).
- The approaches' own parity page, `tests/approaches.html` with `out/r4/maths/parity.json`: 76 of 76 (`parity.log`).

There is no pillow (SPEC4, "What N1 turned out to be"), so no `pillow` approach, no `integerOnly`, and no `notes/pillow.md`.

## 1. Sphere inversions now reads as a one-plane rule with an earlier version behind a dial

Texts only, plus two dial fields. The rule, its keys and their order (`planes`, `turn`, `lift` = uA.x, y, z) are unchanged.

- `about` holds only what is true at every setting: the recipe (circle inversions added up, spheres for circles),
  the two angles, and "Cut the solid at z = 0 and the slice is exactly the ordinary 2D Mandelbrot or Julia set".
  It no longer says "Slices at other heights are different shapes" or "two planes his fully 3D figure".
- Planes dial: label "Planes (2 or more: earlier version)", still 1 to 8, starts at 1.
- Under it one of two notes, switched by `when`:
  - one plane: "One plane is the rule itself. For whole powers it is smooth and has no seam, so nothing tears the
    solid. The fine detail lies around the plane z = 0 only: these are the “inflated” sets in Václav Kučera’s paper
    (Bridges 2019, Figure 3). Two or more planes bring back an earlier version."
  - two or more: "An earlier version, kept so the history stays visible: an attempt to copy Figure 4 in Václav
    Kučera’s paper (Bridges 2019). It looks right for a Julia set whose c lies on the x-axis, such as the Basilica.
    Everywhere else, the Mandelbrot solid included, the rule jumps on the seam of its fold, which tears the solid.
    The count is a free choice: p planes give 2p fins around the x-axis, whatever the power is."
- The note shown at two or more planes in place of the Turn dial now reads as the page engineer asked (text-5):
  "Set the planes to 1 to get a Turn dial as well. With two or more planes a turn tears the solid into sheets."
- Scorecard texts checked for one plane (`card-1plane.png`): crush "Crushes the z-axis only: a line where the plane
  has a point", smooth "Smooth everywhere except the origin...", slice "The plane z = 0 follows complex arithmetic
  exactly...", roundNote "Circles on the sphere stay circles...". All four are true for one plane, and the measured
  rows agree (plane exact, wraps the sphere of directions 2 times, never reversed). Two small corrections:
  - `roundNote` gave the n = −1 sentence ("a single sphere inversion ... keeps every shape") also with a lift set.
    Measured roundness there is 78% (one plane, lift 0.5), so the sentence now needs lift = 0.
  - `smooth` at two or more planes now names where the jump is: "across the plane y = 0".

**A fact the brief had slightly differently.** The brief and SPEC4 say the folded rule "jumps on the seams between
the planes". Measured (`checks.json` step 1, walking round the x-axis in 7200 steps for 2, 3, 4, 5 and 8 planes):
the rule jumps in exactly one place, across the plane y = 0, whatever the number of planes. The other fold lines
(between neighbouring planes) are creases: the result bends there but does not jump. The reason is in `foldk`: the
half y > 0 of space is folded onto one side and the half y < 0 onto the other, mirrored. So the panel says "the
rule jumps on the seam of its fold", which is true, and the scorecard says where. The footer sentence in
`src/body.html` ("its result jumps where two folds meet") is close enough; "jumps across the plane y = 0" is exact.

Evidence that one plane answers N1 (`sheet-oneplane.png`, each row one plane on the left, two on the right):
the Mandelbrot solid at n = 2 and n = 3 from the testers' camera (p9-1, p9-2: clean with one plane, shredded and
streaked with two); the solid cut open at z = 0.3; the 2D view of the slice z = 0.3 (one smooth piece against a
jagged one with a straight tear along y = 0); the same for the Julia rabbit at z = 0.2; and the Basilica at z = 0.3,
where both are whole because c is on the x-axis.

## 2. Lift

- `animate: 'bounce'` (notes/fix-dial.md): the sweep runs to the end of the slider and back. Checked on the page:
  from 1.9 it reaches 2.0, turns round and comes down, largest change between samples 0.017 (it was a jump of 3.98).
- Help text no longer promises a pulse: "The nearest thing this approach has to the Mandelbulb’s latitude phase: it
  pushes every direction toward one pole each time a power is taken. It is an offset where the phase is an angle, so
  play sweeps it to one end and back. Away from 0 the flat set leaves the plane z = 0."
  This agrees with the closing text in `src/body.html`. `sheet-lift.png` shows lift −1, 0, 1 at n = 2 and n = 8: at
  power 8 the ring of bulbs slides up and down the dome, as the closing text says.

## 3. Wide (extreme) ranges on approach dials

| Dial | Ordinary slider / typed | With extreme ranges on |
|---|---|---|
| Sphere inversions, planes | 1 to 8 / 1 to 8 | 1 to 16 / 1 to 64 |
| Sphere inversions, lift | −2 to 2 / −6 to 6 | −6 to 6 / −20 to 20 |
| Lathe, spin (odd numbers) | −7 to 9 / −7 to 9 | −31 to 33 / −99 to 99 |

The degree dials (turn, latitude and longitude phase, θ and φ phase) get none: they are angles and come back round.
Checked on the page (`checks.json` steps 10 to 12): the three dials show "wide", typed values are taken, an even
spin is refused, switching the switch off pulls 12 planes back to 8, lift 15 to 6 and spin 21 to 9, and the Approach
reset puts back 1, 0, 1. The smoke test's "planes dial goes to 8" still holds (it looks with the switch off), and
its count of widening dials is now 30 (27 before). Pictures: `wide-12planes.png`, `wide-spin.png`.
Not timed. A lift beyond about ±9 sends every direction to a pole, so the solid turns into a plain lump.

## 4. Julia list: `data/julia-presets.json`

Written by `python out/r4/maths/julia_notes.py` (the notes live in that script; the file before is kept as
`out/r4/maths/julia-presets.before.json`). All 26 entries are still there, in the same order, with the same
`name`, `c`, `source`, `planes`, `iter`. Changed: every `note`, and `cam.dist` of three entries.

- Notes are in plain words for someone who knows the picture of the Mandelbrot set but not the names of its parts:
  "the heart-shaped body" (main cardioid), "the round bulb on the left" (period-two disc), "the largest bulb on
  top" (the rabbit's bulb), "the dent on its right", "its left spike", "a thin hair". No "period", "cusp", "disc".
  Each says where the point is and what the solid looks like as the page opens (one plane).
- The old endings "Best with one plane..." are gone. Where a picture really needs a setting the entry does not
  change, the note ends with that as a hint (see the table).
- `planes` and `iter` are kept in the data only as a record of what each entry was tuned with. The page ignores them.
- Cameras: Airplane 4.0 to 5.2 (asked). Also Feigenbaum point 5.2 to 5.6 and Thorn crystal 5.0 to 5.4, because their
  right tips reached the zoom slider at the usual window size (the tester's side remark in p6-1). `sheet-list2.png`.

### All 26 entries with the page as it is now

Contact sheets `julia-sheet-a-1.png` to `-6.png`: per entry, one plane at 14 iterations, one plane at 24, and (for
the 15 entries tuned for two planes) two planes at 14. Opening colours, Balanced quality with 4 refining passes,
1000 x 640 window, dark theme, each entry framed with its own camera. Nothing is broken: no speckle, no tears, no
empty or cut-off picture with one plane.

| # | Entry | One plane, 14 iterations | At 24 | What it needs |
|---|---|---|---|---|
| 1 | Basilica | good: a string of rounded beads (the paper's Figure 3) | same | nothing |
| 2 | San Marco | good: one scalloped shell | same | nothing |
| 3 | Douady rabbit | fair: the lobes run together | good | about 24 iterations (hint in the note) |
| 4 | Airplane | good but thin and small: a spine with spiky beads | same | nothing; whole in the frame at 5.2 |
| 5 | Cauliflower | plain: a smooth gourd, the cauliflower only at its rim | same | a view from higher up would show the rim better |
| 6 | Siegel disc | fair: a smooth slab with a frilled edge | same | nothing |
| 7 | Dendrite | good: thin branching coral | same | nothing |
| 8 | Kokopelli | good: beaded coral | same | nothing |
| 9 | Fat rabbit | fair: a slab with a frilled edge | same | nothing |
| 10 | Feigenbaum point | good: a flat spiny rod | same | camera backed off to 5.6 |
| 11 | Golden ratio | fair: a smooth lens with a scalloped rim | same | nothing |
| 12 | −0.8 + 0.156i | poor: one fused lump | good: a row of bulbs | about 24 iterations (hint) |
| 13 | 0.285 + 0.01i | plain: cannot be told from the Cauliflower | same | far more iterations, not tried |
| 14 | −0.4 + 0.6i | fair: a slab with a frilled edge | same | nothing |
| 15 | −0.70176 − 0.3842i | poor: fused | good: buds on a chain | about 24 iterations (hint) |
| 16 | −0.835 − 0.2321i | poor: fused | good: curled ribbons | about 24 iterations (hint) |
| 17 | −0.7269 + 0.1889i | fair: a scalloped shell | same | nothing |
| 18 | 0.45 + 0.1428i | good: rings of islands | thinner, with holes | nothing; best near 14 |
| 19 | Cracked Basilica | a near copy of the Basilica, no cracks | same | 2 planes (hint) |
| 20 | Thorn crystal | good: flat blades with thorns | the middle blade dents in | camera backed off to 5.4 |
| 21 | Split conch | fair: a smooth conch, no crack | same | 2 planes for the crack (hint) |
| 22 | Flint | plain: a smooth egg with a frilled band | same | 2 planes (hint) |
| 23 | Plated egg | poor: a plain egg | same | 2 planes (hint) |
| 24 | Plated ball | poor: a plain ball | same | 2 planes (hint) |
| 25 | Cracked gourd | plain: a smooth gourd with a few dimples | same | 2 planes (hint) |
| 26 | Pitted gourd | fair: a gourd with a few pits | bigger pits | more pits with 2 planes (hint) |

In short: the 18 classic entries are fine with one plane; three of them (12, 15, 16) need about 24 iterations and say
so. The eight "found by exploring" entries were found with the two-plane rule. Thorn crystal and Pitted gourd
survive; the other six lose what their names describe and say "set Planes to 2 under Sphere inversions". A decision
for whoever owns the list: keep them with the hint (done), or move those six under a heading of their own such as
"Earlier two-plane version" (the page takes the heading from `source`; I did not change `source`).

## Names added or changed

No new top-level names in any JavaScript file, no new state in `S`, no new uniforms.

`APPROACHES`, id `mercator`:
- `params`: spec `planes` label changed, `xmax: 16, xhi: 64` added; the old planes note is replaced by two notes
  with `when` (element ids `par-mercator-note1`, shown at one plane, and `par-mercator-note2`, shown at two or
  more); the Turn note is now `par-mercator-note4` with new text; spec `lift` has `animate: 'bounce'`,
  `xmin: -6, xmax: 6, xlo: -20, xhi: 20` and a new `help`.
- `about` rewritten; `roundNote` and `smooth` corrected as said above.

`APPROACHES`, id `lathe`: spec `spin` has `xmin: -31, xmax: 33, xlo: -99, xhi: 99`.

`data/julia-presets.json`: `note` of all 26 entries; `cam.dist` of Airplane (5.2), Feigenbaum point (5.6), Thorn
crystal (5.4).

Scripts under `out/r4/maths/`: `julia_notes.py` (writes the data file), `julia_sheet.py` (the contact sheets),
`sheet.py` with `make_plans.py` and `make_plan_list.py` (other sheets), `make_checks.py` (writes `checks.json`),
`embed_private.py` (the private `75-presets.js`), `make_phone.py` (phone screenshots).

## For whoever joins the parts

1. Run `python notes/ui_embed.py` so `src/js/75-presets.js` carries the new Julia data. I did not: the file is the
   page engineer's. With my private copy the smoke test passes, including its check that the Douady rabbit's note
   starts with "The centre of" (the new note still does, on purpose).
2. After that, in `75-presets.js`: `JULIA_FRAME_DIST` can go (the Airplane's own distance is 5.2 now), and
   `juliaNoteFor` finds no "Best with ..." ending any more, so it can return `p.note`. Both are harmless if left.
3. No approach has the id `pillow`, so everything marked `data-needs="pillow"` stays hidden and `#powWhole` never
   shows. That is the honest state for now.
4. Closing texts in `src/body.html` to check against what is true now: "The dial goes up to 8 planes" (16 with
   extreme ranges on, 64 typed); "its result jumps where two folds meet" (exactly: across the plane y = 0); the
   paragraph "The number of planes has nothing to do with the power..." still reads as if the planes were part of
   the rule, where the panel now calls two or more planes an earlier version.
5. The smoke test's maths assertions hold unchanged: the play buttons, planes to 8, Turn hidden at two planes, the
   formula following the Turn dial, the Approach reset going back to the default plane count.
6. Seen at 00:11, with the other engineers' files as they stood then (`25-colour.js` 00:07, `30-shaders.js` 00:08,
   `40-render.js` and `45-export.js` 00:09, all still being edited): `dist/r4-maths-all.html` (base4, my files,
   theirs, the private presets) passes my 12 checks with no console errors (`checks-all.log`), but the smoke test
   stops at step 3, "the progress bar never showed while drawing" (`smoke-all.log`). It is not from the maths
   files: base4 plus only their four files stops at the same step (`smoke-others.log`), and base4 plus only mine
   passes it (`smoke-mine-first3.log`). The step switches to the classic Mandelbulb at n = 8 and expects to see
   `#drawProgress` while the picture is drawn, so look in `40-render.js`, or at whether the picture is now finished
   before the step's first look.

## Not done, or not checked

- p15-8 (the two negative-power equation presets in Julia mode) still needs the camera file; p10-1 (planes that
  follow the power) is moot now that two or more planes are the earlier version.
- The contact sheets were not repeated at Fine, at phone width or in the light theme, and the entries tuned for one
  plane were not drawn with two. Iteration counts above 24 were not tried.
- The panel was looked at in the dark theme at the usual width (`panel-1plane.png`, `panel-2planes.png`) and in the
  light theme at 375 px (`phone-1plane.png`, `phone-2planes-wide.png`: no sideways scroll, the planes label wraps to
  two lines, three with the "wide" tag). The other approaches' panels were not looked at again; only the Lathe's
  spin dial changed there.
- Wide ranges were tried for function, not for speed or for how good the pictures are.
