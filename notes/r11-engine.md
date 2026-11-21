# Round 11, engine (`src/js/25-colour.js`, `src/js/30-shaders.js`; `40-render.js` untouched so far)

Started 10:07. Base `base11/`, page `dist/r11-engine.html`, compared with `dist/v11.html`. Scripts, logs and pictures:
`out/r11/engine/` (`scenes.py` = the earlier engineer's fixed scene list, pointed at this folder; `ref/` = the 68
scenes on `dist/v11.html`, made 10:08 to 10:10 before any source change; `mesh/run.sh <page> <subject> ...` = the mesh
tester's drive.py and check.py at 128 cells).

## t9-mesh-2, colours of a trap solid's model (measured, 10:12 to 10:14)

Hue difference picture to model, 128 cells (`mesh/check-v11.txt`, `mesh/check-r11-eng-b.txt`):

| Job | v11 | with the new sample rule |
|---|---|---|
| Chain of bubbles | 21.5 deg, 58 % within 30 | 5.9 deg, 95 % |
| Sea urchins | 69.1 deg, 26 % | 24.9 deg, 54 % |
| Arches and hoops | 6.5 deg, 85 % | 4.4 deg, 91 % |
| trapsolid (shell 1) | 6.9 deg, 88 % | 5.7 deg, 95 % |

Shapes unchanged (same triangle counts and overlap). Pictures: `mesh/pair-exbubbles.png`, `mesh/pair-exurchins.png`
(v11 above, new below): the bubbles carry the rainbow swirl; the urchins are no longer confetti, the spikes have
their colours, but the balls are teal where the picture is green.

What the rule is (the earlier engineer's variant "b", taken from `dist/r10-engine-b.html`, checked and measured
again here): a sample beside the trap's part of a trap solid takes four more readings round itself (the slope),
steps down the slope to the surface, and reads the colour there with the picture's own pixel size (`gPix`), so the
colour module picks the touching step as it does for the picture. While it looks for the surface, layers the picture
does not draw are pushed away (`gThinK`, `RAW_GONE`). All in the RAW_FIT program. The earlier engineer's last,
unmeasured step (aiming 0.8 pixel above the surface, as a ray does) measured no better (24.8 deg urchins) and is
left out.

## t9-solids-4 and t9-words-4, fine lines in folds

The earlier engineer's diagnosis pictures (`out/r10/engine/diag-side-a.png`, `diag-rabbit-a.png`, looked at again):
the lines go with Shadows off and stay with Shade crevices off. It is the shadow ray.

**Cause (measured, 10:20 to 10:35).** The shadow ray asked for its distance with one neighbouring orbit along the
ray (`qn = min(nt, 1)`). Where the equation stretches space more across the ray than along it, that read too long,
the ray strode through the fold it should have stopped at, and the shadow came out as fine lit and dark lines.
Tried on the tester's scenes (`rabbit-t789.png`, `side-t789.png`, `rabbit-t1011.png`, `side-t1011.png`, and the
earlier engineer's `out/r10/engine/var/rabbit-t.png`, `side-t.png`):
- a shorter stride, a start further off the surface: lines stay;
- all the neighbours only for the first 4 or 8 steps, or one neighbour along (normal + light): lines stay;
- all the neighbours only where the light grazes: lines go, but a seam appears where the rule switches;
- **all the neighbours the picture has, for the whole ray: lines gone, shadows smooth.** That is what is in.

Before and after at full size: `rabbit-crops.png` (the tester's three places, 3 times: v11, new, v11 without
shadows) and `side-crops.png` (v11 Exact, new Exact, v11 Rough). Ordinary pictures: `pair-ordinary.png`,
`pair-open.png`; numbers in `cmp-new.txt` (v11 against the first build): scenes with shadows off, Rough or Ultra
fast, the 2D view and the Kleinian view are identical; pictures with the Exact estimate and shadows change only in
their shadows (0.1 % of pixels on the opening Mandelbrot, 12 % on power -2, 8 % on the Mandelbulb approach).

**Speed.** The fuller shadow query cost about a tenth of the drawing time (10:24, quiet GPU: Mandelbrot 616 ms
against 483 for base4, over the quarter). So the shadow ray now also takes longer strides in the open, where they
cannot change the soft edge (`(10 d - ts) / 11`, see the comment at PH_SHADOW; not with the fastest estimate).
Pictures against the build before: identical except power -2 (0.13 % of pixels, at most 31), the Mandelbulb
approach (0.005 %) and one Kleinian trap solid (0.004 %).

## t9-solids-2: help of "Orbit steps the trap reads" reworded (the earlier engineer's wording, read and kept)

## t9-kleinian-1 and t9-flat-1: drawn again on this base (`sheet-rest.png`), both still there

- Trap centre y = 0.5: black picture; 0.25: two huge balls; 1: a swirl fills the picture. New note under the solid
  choice when y is not 0 (`colKleinHigh`).
- 2D Kleinian view, inside by orbit trap: upper big disc plain, lower one banded. New note beside the choice.
No cure in the shader for either.

## A fault of the taken-over code, found and cured (10:51 to 10:55, measured)

The first run of all nine model jobs on my page gave no Kleinian model: "The picture could not be read just now".
`gThinK` was declared inside the orbit code, and `main()` (shared with the Kleinian program) sets it: the Kleinian
model's program did not build, and nothing showed in the console. The earlier engineer had run only the four trap
jobs. `gThinK` is now declared with the other query switches in GL_HEAD. After that, all nine jobs
(`mesh/final.log`, `mesh/check-r11-engine.txt`): mandel 3.3, rabbit 2.8, julia1 7.3, cut 6.3, klein 3.5 (all as on
v11, same triangle counts), trapsolid 5.7, bubbles 5.9, urchins 24.9, arches 4.4.
The smoke test does not make a Kleinian model, so it did not see this. Worth a step in the smoke test.

## Not done

- **Sea urchins, the rest (24.9 deg).** The balls of the model are teal where the picture is green. Reasoned, not
  measured: the balls are the Julia set itself wrapped in layers thinner than a pixel; the picture colours such a
  place by how near the first few orbit steps come to the trap, which changes within a pixel of height, and the
  sample does not land on the picture's own surface to within that.
- **Samples with the picture's thin-layer rule for the shape** (a pixel size in place of `gPix = 0` for the distance
  a sample hands back): not tried. The colour readings do use it. The shape is as on v11.
- **t9-solids-3** (Mandelbulb approach, presets): drawn again (`sheet-rest.png`, d06 to d08). Balanced and Fine
  agree by eye; Ultra fast is yellower and its shape smoother. Not traced.
- **t9-export-1**: not run. Reasoned from the code: the thin-layer rule goes by `gPix = pix * t`, a pixel of the
  picture being drawn, so a file twice the size keeps layers half as thick. `gPix = pix * t * uPx` (a pixel of the
  page) would make every size agree, but the moving preview and a high-density screen would then keep or drop
  other layers than now, so it needs its own round of pictures.

## Final checks (10:55 to 11:08), page `dist/r11-engine.html`, md5 09a0dc00299c9268c28776f65ed99ebe

- Scenes (`cmp-final.txt`, v11 against final; `cmp-final-new2.txt`: the final build is identical in all 68 scenes
  to the build before the Kleinian cure and the two notes). Identical to v11: the 2D view (5 scenes), every Kleinian
  picture, every picture at Ultra fast, Fast or Rough, every picture with shadows off. Changed, in the shadows only:
  pictures with the Exact estimate and shadows on.
- Models, nine jobs at 128 cells: see above. Smoke test `tools/smoke-v9m.json`: 52 steps, exit 0, no console
  errors, 11:03 (`smoke-final.log`).
- Trap centre y = 0.5 and 1 with the camera 8 times further out (`far.png`): whole objects, so the new note's
  "zoom out a long way" holds.
- Speed (`perf-final.log`, 11:04 to 11:08, least of three visits): Mandelbrot compile 2253 ms, draw 886 against
  930 for base4; Julia draw 468 against 1719; Kleinian compile 878 ms, draw 100 against 221. **Another job was
  using the GPU the whole time** (base4 drew the Mandelbrot view in 483 ms at 10:25 and in 930 to 1030 ms now), and
  the visits scatter by more than the margin asked for. In the visits under the same load my page drew the
  Mandelbrot view 1.25 to 1.35 times as long as base4, v11 about 1.1 to 1.5 times. The speed needs measuring again
  on a quiet machine: `python out/me/perf.py base4 r11-engine v11 base4 r11-engine v11 base4 r11-engine v11`.
  If the drawing is over: the cost is the one line at PH_SHADOW (`qn = min(nt, 1);` taken out). Putting it back
  brings the lines back.
- The two new notes and the new dial help in the page (`notes-check.log`, 11:09): the y note shows with trap
  centre y = 0.5 and hides at 0; the mirror note shows in the Kleinian 2D view with inside by orbit trap and not in
  the Julia view; the help text is there.

## For the person joining the files

- Files changed: `src/js/25-colour.js`, `src/js/30-shaders.js`. `src/js/40-render.js` is as in base11.
- `src/js/30-shaders.js` now has plain line feeds (base11 has CR LF): compare with `diff --strip-trailing-cr`.
- Names added: `gThinK` (GL_HEAD), `RAW_GONE` (orbit code, RAW_FIT only), `RAW_SLOPE`, `RAW_THIN`, `rawTrap`,
  the state `crawl == 4` in `main()`; `colKleinHigh` and two notes in `COLOUR_CONTROLS` (25-colour.js).
- Test pages left in `dist/`: `r11-eng-b`, `-p`, `-b3`, `-t3`, `-t7` to `-t11` (variants, see above). Not the result.
Stopped 11:10.
