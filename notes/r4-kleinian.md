# r4-kleinian: the Kleinian distance estimate, trap solids, and fifteen new list entries

Files I own and changed: `data/klein-presets.json` (19 -> 34 entries), `notes/klein-presets.md` (a section added at
the end), everything under `out/r4/kleinian/`. Nothing in `src/` was edited. Time: 23:29 to about 00:40.

## For whoever joins the parts: three things to do

1. **Paste the constant.** `out/r4/kleinian/GL_KLEIN.js` holds one complete statement, `const GL_KLEIN = \`...\`;`.
   In `src/js/30-shaders.js` replace the whole existing statement (from `const GL_KLEIN = \`` to its closing
   `` `; ``, just above `const GL_TAIL`) with the file's content. Keep the two comment lines above it. Nothing else
   in that file has to change. It uses only: `uFlat`, `uIter`, `uKMu`, `uKInvC`, `uKL`, `uK3`, `uKInvR`, `gEsc`,
   `gIt`, `gLast`, `gGrad` (all in `GL_HEAD` of base4) and the colour module's `trapStart`, `trapAdd`, `trapDist`,
   `uTrapSolid`, `uTrapW`, `uTrapSkip`. It does not read `gFade`, `gPix` or `gOnTrap`.
   `python out/r4/kleinian/mk.py` does the same paste into a copy of base4's shader file and builds the test page.
2. **Keep the 0.5 cap** on the step share in Kleinian mode (`setScene` in `40-render.js`). Measured below: without
   it up to 7% of a rich picture is still lost. The hint under the ray step dial (80-ui.js, `qstepk`) stays true.
3. **Embed the list**: `python notes/ui_embed.py` (it rewrites only between the marker lines of
   `src/js/75-presets.js`). The page already shows the new group: entries carry `"group": "Turning-out sphere"` and
   a `source` that starts with `sphere`. Each new `cam` has a `target` (the page's `presetFrame` passes it on).

Checked with the real files as they stood at 00:24 (`dist/r4-kleinian-real.html`: base4, live `src/js/25-colour.js`,
live `src/js/30-shaders.js` with my constant pasted in, the list embedded in a private copy of `75-presets.js`):
compiles, no console errors, the drop-down shows "Turning-out sphere: 15", an entry leaves camera and depth alone,
"Frame it" frames it, trap solids draw with the real colour controls (`real-*.png`). The smoke test on that page stops
at step 3 ("the progress bar never showed while drawing"), which is in Mandelbrot mode before anything Kleinian is
drawn; see "Smoke test" below for the control run.

## What the constant changes (only `GL_KLEIN`)

| Change | Why |
|---|---|
| Exact distance to every pearl the search meets (`kpearl`, the point `W` carried along) | `notes/klein-kde-exact.glsl`, adopted. The old value was t(1 + t / 2 rho): far too long for a small pearl seen from open space. |
| Trap solids: `bestT`, the smallest over the steps from `uTrapSkip` on of `(trapDist(z) - uTrapW) / DF`; alone when `uTrapSolid` is 1, `min` with the pearls when 2 | CONTRACT4. `DF` is the scale factor the estimate already tracks. |
| `gEsc = 0` whenever the returned distance is zero or negative (before: only inside the two wall spheres) | CONTRACT ("gEsc: 1 when the point is outside the solid"). The march then closes in on a small pearl it has stepped into instead of guessing from one straight line. |
| Inside a wall sphere the function returns the true depth (negative) instead of 0 | The model sampler gets a real signed value; the cut face of the wall spheres is now recognised and hatched (`cut-p0.png`). With `uTrapSolid` 1 the wall spheres are open space and are searched like any other point. |
| `gIt` is reported 8 steps high in the 3D view | So that a fading tail set from it (`gFade = max(count - TAIL, 1)`) never drops a step of the search. "Escape count" colours are unchanged: 8 steps are one full turn of the palette. The live shader file skips the count query for the Kleinian scene anyway, so today this is only a guard. In the 2D view `gIt` is as before. |

Not changed: the choice of maps (the leaning cell and the fitted curve), the 2D picture (same orbit points go to
`trapAdd`, same `gIt`, same solid), the `0.3` cap, the uniforms.

Private stand-ins used for testing, all under `out/r4/kleinian/`: `25-colour.js` (base4's plus the three trap-solid
uniforms, set from `S.colour.solid / thick / skip`), `40-render.js` (base4's without the 0.5 cap, for the
measurement only), `75-presets.js` (base4's with the new list embedded).

## Is the 0.5 cap still needed? Yes.

`python out/r4/kleinian/t6.py PAGE TAG 0.8,0.5 8,14,2,5,0`: Balanced, 3 passes, each picture against a careful one
(share 0.25, 900 ray steps) of the same page. Percent of object pixels lost / drawn in a clearly different colour:

| Entry | old estimate, 0.8 | old, 0.5 | exact, 0.8 | exact, 0.5 (what ships) |
|---|---|---|---|---|
| 8, 5/13 cusp | 9.65 / 7.81 | 3.32 / 4.15 | 6.91 / 3.86 | 1.53 / 2.58 |
| 14, 2/5 leaning in depth | 9.98 / 10.63 | 3.38 / 5.50 | 3.30 / 5.88 | 1.44 / 3.75 |
| 2, 1/15 cusp | 9.70 / 5.69 | 2.60 / 2.71 | 1.79 / 1.99 | 0.46 / 0.76 |
| 5, 2/5 cusp | 8.20 / 8.30 | 2.84 / 3.03 | 1.95 / 3.43 | 0.69 / 1.92 |
| 0, starting view | 0.15 / 3.03 | 0.11 / 0.97 | 0.07 / 0.84 | 0.02 / 0.47 |

So the exact estimate at 0.5 loses about a third to a fifth of what the old one lost at 0.5, and without the cap
it would lose more than the old one does with it. The reason is the next section. (The two runs were made side by
side; the timings the script prints are not usable.)

## The three defects

**p8b-1, hollow and sliced pearls at Fine: fixed as far as I could see.** `fine-p8.png` and `fine-p14.png` (Fine,
through "Frame it") show whole pearls at the places the tester named (right of and below the centre in entry 8,
lower left in entry 14). I looked at these two at full size only, not at 3x crops.

**p8b-2, pearls the search never meets: cause found, not fixed.** The search follows one route through the group
(Jos Leys's rule: back into a leaning cell, then one of two maps chosen by a fitted curve). Pearls that lie off
that route are never measured. `out/r4/kleinian/model2.py` and `model3.py` test this pearl by pearl against the
direct pearl list (`notes/klein_model.py`): for the 5/13 cusp, 124 of 896 pearls of radius 0.004 to 0.01 and 8 of
216 of radius 0.01 to 0.03 are invisible to the shipped rule, and more are cut. The five pearls nearest the
turning-out centre of entry 8 are among them; in the picture they would be up to 50 pixels across. One of them
shows as a sliver: that is the tester's "flat-faced cut pearl" (still there in `fine-p8.png`, lower left). The
flat face is the unit sphere about the origin (where the map stops stretching), which the turning-out sphere
flattens. This also explains the cap: a ray near an unmeasured pearl is told the distance to some other pearl.
What I tried:
- Nearest-centre rule instead of the fitted curve (`model2.py`, rule `near`): fixes entry 14, but loses most of the
  1/15 spirals. Not usable alone.
- "Second wind" (`out/r4/kleinian/v1.js`, a complete alternative constant): when the usual route starts going
  round in a circle, carry on with the nearest-centre rule. It finds many more pearls (entry 14 becomes a full
  disc, `v1-p14.png` against `v1c-p14.png`), costs about twice the steps in open space, and for the 5/13 cusp it
  turns invisible pearls into cut ones (cut pearls of radius 0.004 to 0.01: 8 before, 47 after). A cut pearl looks
  worse than a missing one, and it changes how existing entries look, so I did not ship it.
- A real cure needs a search that can back out of a dead end (try the second-best map for a few steps). Not built.

**p5-6, colours that change between quality settings: cause found, not fixed.** A ray stops a fraction of a pixel
outside a pearl and the colour is read from that hovering point. With the planes trap the wall under the point is
one of the trap planes, so "how near it came" is the hover height itself, and the hover height is the surface
threshold, which every quality setting sets differently (about 0.011 in the cell at Ultra fast, 0.0013 at Fine:
pink-orange against pale yellow). With other traps the same thing happens later in the orbit, once the hovering
orbit has drifted off the wall. The cure is to stop feeding the trap once the search has landed on the pearl the
ray hit, and to put that last point exactly on the wall. "Landed" has to be judged against the size of a pixel,
which base4's shader did not hand to `de()`. The live shader file now does (`gPix`). Sketch for the shader owner,
inside `kde`, 3D view only: pass in `px = gPix * R2 / r2` (a pixel in cell units); after computing the step's
candidate `c = min(kpearl(...), kpearl(...)) / DF`, if `c < 3.0 * px` call `trapAdd` once with `z.y` set to the
wall (`z.y < 0.5 * a ? 0.0 : a`) and call it no more. I did not build it because my test copy has no `gPix`, and
a fixed threshold in its place puts seams on middle-sized pearls. Not having this is no worse than before.

## Trap solids in the Kleinian view

`solid1-p0.png`, `solid2-p0.png`, `solid1-cross-p0.png` (stand-in colours) and `real-solid1.png`, `real-solid2.png`,
`real-solid1-cross.png` (real colour module): the sphere shell (radius 1, thickness 0.05, skip 1) gives a new, clean
solid of large balls and fine lace on the starting group; added to the pearls it sits among them. Silhouettes are
clean at Balanced. Not measured: speed and compile time with the trap off against base4 (one `bool` test per step
was added; nothing else runs).

## The new list entries (N9)

Fifteen entries, group "Turning-out sphere", appended to `data/klein-presets.json`; the first nineteen are
unchanged, byte for byte. Contact sheets, every entry applied and framed with the page's own `frameKleinPreset`:
- `out/r4/kleinian/shots/fine-sheet-0.png`, `fine-sheet-1.png`: Fine quality, 1400x950, default depth 150.
- `out/r4/kleinian/shots/phone-sheet-0.png`: 375x812, Balanced.
- `out/r4/kleinian/shots/d60-sheet-0.png`: depth 60, Balanced. No visible difference from depth 150.
- `out/r4/kleinian/shots/try1-sheet-0.png` to `-3.png`: all 37 candidates, including the rejected ones.

How they were found (`find.py`, `pick1.py`, `fit.py`, `final.py`): for eleven groups the roomiest gaps were listed
from the pearl list, plus hand-made centres (off the plane, off the middle of a gap, close to a wall). Each centre
was checked in the model: it lies in a gap, and every pearl that will look big is whole for the shader's search
(this is the check entry 8 would have failed). 37 were drawn; each was measured in the page with a grid of
`pick()` calls and its radius and camera target set so the hit points sit in a ball of radius 1.25 about the
target. Rejected: pictures that are mostly two plain wall spheres, and one centre that gave an endless string.
Table and per-entry remarks: the last section of `notes/klein-presets.md`.

Limits: looked at as contact sheets, not one by one at full size (except one through the real drop-down,
`real-entry.png`). At phone width every object is inside the stage; the 3D ones come close to the zoom label on
the right. Depths above 150 were not drawn.

## Smoke test

- `dist/r4-kleinian.html` (base4, my constant in a copy of base4's shader file, the stand-in colour file, the list
  embedded): `python tools/shot.py --url dist/r4-kleinian.html --actions tools/smoke.json` exits 0, 27 steps, no
  console errors (`out/r4/kleinian/smoke-standin.log`). Run after the last change to the constant and the data.
- `dist/r4-kleinian-real.html` (live colour and shader files, see the top): exit 1, stops at step 3, in Mandelbrot
  mode, with "the progress bar never showed while drawing" (`smoke-real.log`).
- Control, the same page WITHOUT my constant (`dist/r4-kleinian-control.html`: base4 plus copies of the live
  `25-colour.js` and `30-shaders.js` taken at 00:30): fails at the same step with the same message
  (`smoke-control.log`). So that failure belongs to the live shader and colour files on base4's renderer (the new
  renderer was not in the mix), not to `GL_KLEIN`. The Kleinian steps of the smoke test were therefore not reached
  with the live files; my own run on that page (`real.json`, six pictures) is what covers them.

## Names added

In `GL_KLEIN`: function `kpearl(h, D, kk)`; in `kde`: locals `W` (image of the point at infinity), `z0`, `zw`, `kk`,
`trapSolid`, `bestT`; in `de`: `wall`. No uniform, no state field, no control.
In the data: a `group` field on the new entries and `cam.target`.
Scripts under `out/r4/kleinian/`: `mk.py` (build), `model.py`, `model2.py`, `model3.py`, `trace.py`, `false.py`
(the pearl-list checks), `t6.py` (step-share measurement), `find.py`, `pick1.py`, `fit.py`, `final.py` (entries).
