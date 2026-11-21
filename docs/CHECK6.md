# The check of round 6: every point the user raised, on the joined page

The user has raised 27 points: 15 in their second round of feedback (quoted at the top of `docs/SPEC.md`) and 12
in their third (N1 to N12, quoted at the top of `docs/SPEC4.md`). Each tester below takes a group of them and
finds out what the user gets for them today.

## Rules for every tester

- **You test and report. You do not fix.** Edit nothing under `src/`, `base*/`, `docs/`, `tools/`, `data/` or
  `notes/`. Do not run `python build.py`, git, a server, or anything that publishes.
- **The page under test is `dist/v6.html`** (the joined build). `dist/v5.html` is the build the user has now, for
  comparisons.
- Keep every script, log and picture under `out/t6/<your key>/`.
- Drive the page with `python tools/shot.py` (read the comment at its top; `tools/smoke.json` is a worked
  example of a step file; set `PYTHONIOENCODING=utf-8`; pass `--url dist/v6.html`). It runs headless Chrome on
  the real GPU and prints console errors and uncaught exceptions. For real mouse, wheel, touch or keyboard input
  copy `notes/dial_real.py` or `notes/camera_real.py` into your folder and adapt it.
- `window.squaringLab` exposes the state and the functions (`src/js/90-boot.js`); control ids are in
  `notes/ui.md`, `notes/r4-page.md` and the notes of the module concerned (`notes/r4-*.md`, `notes/r5-*.md`).
  A file handed to `saveFile` can be caught with `window.squaringLabSaveHook = (name, blob) => { ... }`.
- Open pictures with the Read tool and judge them the way the user would. The user is not a mathematician. They
  explore by moving controls, judge by how the pictures look and how the controls feel, and notice anything that
  behaves inconsistently.
- About ten testers and one engineer share the GPU. Raise timeouts instead of concluding that something hangs,
  and do not report slowness as a defect: speed is measured separately on a quiet machine.
- A **defect** is something the user would notice or be misled by, a console error, a control that does not do
  what its label says, or a text on the page that is not true. A preference of yours is not a defect, and
  neither is something the user's words do not ask for. Give each: an id starting with your key and a dash, a
  one-line title, a severity (blocker: the point does not work; major: it works but is clearly wrong or ugly in
  ordinary use; minor: edge case or cosmetic), the group that owns the fix, an exact reproduction, what you
  expected, what happened, the path of the evidence, and a suggested fix naming file and function when you can.
- Cover your whole assignment once before digging into any single defect. Run `date +%H:%M` when you start; aim
  to return after about 30 minutes; at 40 minutes stop and return what you have, with what you did not reach
  under `unverified`.

Groups (who owns a fix):

- `engine`: `src/js/30-shaders.js`, `src/js/40-render.js` (drawing, distance estimate, trap solids' shape,
  busy and progress signals, the 2D view, the mosaic, snapshots and sampling).
- `colour`: `src/js/25-colour.js` (palettes, traps, every colour control, the colours of trap solids, the 2D
  view's outline and inside colours).
- `export`: `src/js/45-export.js`, `src/css/45-export.css` (Save a picture).
- `mesh`: `src/js/46-mesh.js`, `src/css/46-mesh.css` (Save a 3D model).
- `maths`: `src/js/10-approaches.js`, `src/js/20-formula.js`, `src/js/60-measure.js`.
- `dial`: `src/js/70-dial.js`, `src/css/70-dial.css`. `camera`: `src/js/50-camera.js`, `src/css/50-camera.css`.
- `page`: `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`,
  `src/js/90-boot.js`, the preset data.

Known and already being worked on, so do not spend time on them (mention only if they block your test): the
colours an orbit trap gives a 3D surface still change with the quality settings, the iterations and the trap
radius, and can show faint rings (`docs/SPEC6.md`); a trap solid in Mandelbrot mode starts as the trap shape
itself; no seam-free rule gives the look of Figure 4 away from the x-axis (`docs/SPEC5.md`, N1).

## Assignments

### controls
Points 1, 2, 4, 5, 7, 8 and 13 of the second round. For each, read the user's words and the decision in
`docs/SPEC.md`, then test on today's page with real input where the point is about feel: the busy sign and the
progress bar show for every action that takes longer than a blink (new approach, new equation, mode change, a
quality preset, a trap shape, switching a trap solid on, starting an export); number boxes take typed values,
refuse nonsense kindly, and each has its whole-step toggle; wheel and pinch zoom glide; Ultra fast exists and is
fast; the fly and arcball switch sits in the picture and both work; every section has a reset that restores its
own values only; the zoom slider with its typed near and far limits; the drawing radius; Collapse all and
Expand all. Also N4: the Extreme ranges switch widens the dials it says it widens (list them, try five, type a
value beyond the normal range, switch off and see it pulled back), and nothing else changes.

### modes
Points 6, 9, 11, 12, 14 and 15 of the second round, and N7 and N8. The standing requirement first: for every
approach in the list except the classic Mandelbulb, the slice at z = 0 is the flat Mandelbrot or Julia set.
Check it by numbers, not by eye: for each approach, in Mandelbrot mode and for two Julia constants, compare the
2D view at z = 0 with a flat set you compute yourself in Python on the same grid (inside or outside per pixel;
report the share of pixels that disagree, which should be the outline only), at powers 2, 3 and -2. Then: the
Julia drop-down (N7) with its groups, the user's saved points on top, saving and deleting a point, "Your own
values"; an entry sets only c, "Frame it" moves only the camera, "As it was found" sets only planes and
iterations (N8); the same for the Kleinian list; the Julia mosaic tick box; the 2D view tick box above Show; the
Mandelbulb's phase offsets and its Mercator relative; negative powers in every approach that allows them. And the
mirror twins: with "flip z" ticked under Modifiers the slice at z = 0 must still be the flat set for every
approach (same numeric check), and for Sphere inversions and the Lathe a Julia set with c in the plane z = 0 must
be the same solid with and without the tick (compare pictures of four Julia sets from two sides).

### solids
N3. The user: "in other 3d fractals, the actual shape of the fractal changes based on the orbit trap selected ...
I've seen so many renders of insane orbit traps on the same fractals that make them look so different". Try
every trap shape with "Is the solid" and "Is added to the solid", in Mandelbrot, Julia (three constants) and
Kleinian mode, moving Trap thickness, Orbit steps skipped, the trap's radius and position, and the iterations.
Judge as the user: does each shape give a clearly different object, are the objects clean (holes, speckle,
missing pieces, flat cut faces that should not be there), do they survive Ultra fast, Fast, Fine, the cut, the
2D view (which must not change), the mosaic. Are the labels and hints enough to find the interesting settings?
Name three settings per mode that look best, with pictures: they may become one-click examples.

### flat
N10, and point 3 of the second round where it concerns the 2D view. The user: "is distance estimation a
technique you can add to make crisper surfaces in 2d ...? and what about internal coloring for 2d? and different
options for coloring inside vs outside?", and separately "the 2d side is great, btw - keep that as it is". So:
at the opening settings the 2D view of `dist/v6.html` must equal that of `dist/v5.html` pixel for pixel
(Mandelbrot, two Julia sets, a slice off z = 0, the Kleinian view, a negative power, the mosaic: report the
largest difference; the mosaic's background was changed on purpose). Then every new control of the 2D view:
outline width from 0 to wide, the glow beside the outline, each inside colouring with three palettes and
reversed, zoomed far in on a thin thread and on a small copy. Are outlines crisp at every zoom? Do inside
colours hold still while zooming and while the picture refines? The cut face coloured like the inside in 3D.

### export
N5. The user: "a high quality render button that exports to a file on disk, with settings like resolution and
whatnot, ideally rendering in the background while you keep going (where if you change settings in the live app
it doesn't affect the settings in the background render)". Run real jobs through the panel and catch the files
with the save hook: three sizes (one typed, one 4K, one 8K), each file type, each quality; open the files in
Python and check size, that they are not blank, and that they show the view that was on screen when Start was
pressed (compare with a screenshot of the stage scaled to size). While a job runs, change everything (mode,
approach, colours, camera, quality) and confirm the file is unchanged. Cancel, start again, Discard, a second
job after the first, a job in the 2D view, in Kleinian mode, with a trap solid, with the cut open, with the
mosaic. Is the estimate of the time left roughly right? Does the page stay usable while a job runs (look at
frames, not at the clock)? What happens at a size the browser cannot hold, and when the save is refused (make
the hook throw, and separately make `window.claude.use` resolve to an object whose `save` rejects with
`{ code: 'declined' }`)?

### mesh
N6. The user: "a 3d export, where I could load the 3d object in blender or rhino or something and put it in
scenes or 3d print it or whatever". Run real jobs through the panel for the opening Mandelbrot, the Julia set for
c = -1, the Douady rabbit, the opening Kleinian view, a trap solid, a negative power and a cut solid, at the
smallest, the standard and the largest resolution offered. Unzip each file in Python and check it for what
Blender, Rhino and a slicer need: STL (binary, triangle count matches the header, no degenerate or duplicate
triangles, every edge shared by exactly two triangles, outward normals, one sensible bounding box in
millimetres), OBJ (vertex, normal and face counts consistent, indices in range, colours if promised), PLY
(header correct, counts match, colours present and plausible against the picture). Does the model look like the
picture: render the vertices in Python from the picture's camera and compare silhouettes. Are thin parts lost or
fused at the standard resolution, and does the panel say so? Is the readme in the zip correct and enough for
someone who has never imported a model? Memory and time at the largest size. Cancel and a second job.

### kleinian
N9, N2 where it concerns the Kleinian view ("highest search depth for klein objects"), and point 8 of the second
round where it concerns the Kleinian list. All 34 entries: pick each through the drop-down and press "Frame it";
make contact sheets at Balanced and say for each whether it is whole, clean and worth having (the fifteen in
the group "Turning-out sphere" are new: the user asked "you also don't have any klein presets that mess with the
turning-out sphere ... please add to the list, rather than take things away", so also confirm that the first
nineteen are all still there and unchanged). What does the page open with for the depth of search, and is that
the top of its ordinary range? Every Kleinian control once, including the quaternion parameter, "use third map",
the turning-out sphere's radius and centre, with Extreme ranges on. Hollow, cut or missing pearls at Fine and at
Ultra fast. The 2D view of three entries. Trap solids on three entries.

### words
N1, N2, N11 and every text of the closing section. Be the user: read "Questions from testing, answered" from top
to bottom and check each sentence against the page (does the control it names exist under that name, does the
thing it promises happen). Mark anything that is not plain words, anything untrue, anything that claims more
than `docs/SPEC5.md` allows for N1. Press "Show Figure 4" and "Back to one plane" from six different states. Do the same for the four twin
buttons ("Twin of Sphere inversions", "Twin of the Lathe", "Twin of the Mandelbulb", "Back to the plain rule"):
does each show what the text beside it says (a tall body whose slices keep the Mandelbrot outline; the tricorn
in the plane y = 0; fins and feathers), framed whole, on a desktop and on a phone?
With one plane, slice the Mandelbrot solid and three Julia solids at five heights (2D view and the cut): is it
one clean piece each time, as the text says? Is the Lathe what the text says it is? N2: open the page fresh
(clear storage) and list what it starts with against the user's list: "balanced performance, color by orbit
trap, trap type is sphere shell, trap colored by how near it came as a glow, a reversed rainbow palette, highest
search depth for klein objects". N11: the Douady rabbit with the roughest distance estimate, at four distances
and from three sides: is there any glow or halo around the solid?

### layout
The whole page at 1400 x 950, 1024 x 768 and 375 x 812, dark and light, every section open, in each of the three
modes and in the 2D view: nothing cut off, overlapping, unreadable or scrolling sideways; controls reachable
with the keyboard in a sensible order; every control has a visible label; text contrast in both themes; the
picture's own controls (fly and arcball, zoom slider, hints) clear of the picture's content on a phone. The new
parts especially: Save a picture, Save a 3D model, the trap solid controls, the 2D view's colour controls, the
Julia drop-down with its buttons, the Kleinian list, the Extreme ranges switch, the closing texts and their two
buttons.

### walk
Regression by wandering. Write a driver that, for at least fifteen minutes of page time in several runs with
different seeds, picks a random visible control (button, tick box, drop-down, dial, typed number, preset entry,
mode, quality, reset, collapse) and uses it, sometimes several quickly, sometimes during drawing, sometimes
while an export or model job runs, and after each action checks: no console error or exception; the page comes
to rest (`idle()` true within a generous time); the picture is not blank when the settings say it should show
something; no NaN or undefined in any number box; the busy sign is not stuck. Log every action so that a failure
can be replayed, and reduce each failure to the shortest sequence that shows it. Also once each: storage
blocked, a window resized mid-draw, the tab hidden and shown again, a lost and restored GL context
(`WEBGL_lose_context`).
