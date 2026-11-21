# Round 12: every approach is an entry of its own, and the twisted quaternion square

## What the user asked (2026-11-18, verbatim)

> yes try it, and add all these approaches btw (like have the current approach be distinct from the old one,
> rather than have it as a manifestation of the old one). Also, why can't we try to figure out the 2d analog?
> like, a rotation is about an axis. for the 2d mandelbrot, the rotation axis is always the z axis (or whatever
> is correct here). that means mandelbrots are actually 3d, requiring that hidden z-axis. if there was a "why"
> the rotation axis is the z axis, then couldn't we extend that into the 3d one? like why not rotate about the
> w axis, in which the xy plane (ie. the 2d version) just so happens to be where it's identical (or perhaps
> works the same as) the z-axis?

"it" = the twisted quaternion square. "the current approach" = Sphere inversions with one plane; "the old one"
= Sphere inversions with two planes (the Figure 4 look). Until now the old one was the Planes dial of the same
entry set to 2. The user is not a mathematician and judges by pictures and plain words.

## Done already by the orchestrator: `src/js/10-approaches.js` (frozen as `base12a/`, page `dist/v12a.html`)

`base12a/` = `base11/` (published Version 11) + the new `10-approaches.js`. Nothing else is changed yet, so
in `dist/v12a.html` the page code still talks to a Planes dial that no longer exists (see "page" below).

The list is now, in this order (array order is display order):

| id | name | group | dials (in uA order) |
|---|---|---|---|
| `mercator` | Sphere inversions, one plane | inversions | turn, lift |
| `fold` | Sphere inversions, two planes | inversions | planes (2 to 8, starts at 2), lift |
| `lathe` | Quaternion square (Lathe) | quaternion | spin |
| `tilt` | Quaternion square, twisted | quaternion | tilt (degrees, starts at 40) |
| `bulb` | Mandelbulb | angles | lat, lon |
| `classic` | Mandelbulb, classic | angles | theta, phi |
| `split` | Split | other | none |

- `S.param.mercator.planes` is gone. `S.param.fold.planes` is the planes of the earlier version.
- `APPROACH_GROUPS` (in `10-approaches.js`) gives the headings: inversions "Sphere inversions", quaternion
  "Quaternions", angles "Angle rules", other "Side by side", tried "Tried, and kept for the record". Every
  entry has a `group`.
- `MATH.fold`, `MATH.tilt` mirror the shader (`GL_FOLD`, `GL_TILT`). The one-plane shader code is shared
  (`GL_MERC_CORE`).

### The twisted quaternion square (what is true about it; measured in `out/me/tilt/`)

- Rule: with A the turn by the tilt t about the z-axis and L the quaternion power (the Lathe),
  v^n = A^(-n) L^n A (v). For n = 2, writing the first two coordinates as one complex number:
  v² = ((x + iy)² − z²·e^(−2it), 2z·(x cos t − y sin t)). Checked against `MATH.tilt` to 3e-15.
- In 4D it is q times a twisted copy of q: for q = z + w j the copy is z + e^(2it) w j.
- The plane z = 0 follows complex arithmetic exactly for every whole power at every tilt (1e-15 on 2,000
  points for tilts 0, 15, 40, 90, 137, 180, −60 and powers 2, 3, 5, −1, −2). For a power that is not whole the
  tear of the power lies along the tilted axis, so the slice differs from the plain complex power in a wedge.
- Tilt 0 is the Lathe. Tilt 180 is the Lathe with z mirrored (its mirror twin) for EVEN powers (4e-15 at
  power 2); for odd powers a tilt of 180 is the plain Lathe. A minus sign gives the mirror image in y.
  CORRECTED 2026-11-18 after the maths check of round 12: an earlier line here said that at tilt 90 and −90
  the Mandelbrot solid has no end. That was wrong (my slip: the orbit of x starts at c_x, not at 0, so x must
  also lie in the filled Julia set of x² + k). The solid ends inside radius 2 at every tilt; at 90 and −90
  it is a fat body with spikes, farthest point about 1.8 (`out/r12/check-maths/`, `out/r12/fix/`).
- A Julia set whose c is in the plane z = 0 is a true slice of the 4D set (the 4D orbit depends on the
  hidden part only through its length). The Mandelbrot solid adds c as a 3D point: the page's own choice.
- Pictures: `out/me/tilted-quaternion.png` (sent to the user), `out/me/tilt/sheet-c.png` (close-ups). The
  rings of the Lathe break up into one body with tunnels. Up close the skin is smooth (no fine bumps): the
  close-up pictures show smooth sheets and folds (the checker found fine layering at many places away from
  z = 0, so do not say the plane is the only place with fine structure). Say so; do not oversell it.

## Rules for everyone

- Three files in `src/js/` belong to another engineer who is at work right now: `25-colour.js`,
  `30-shaders.js`, `40-render.js`. Do not edit them and never build with them.
- Build only like this: `python build.py --name r12-<you> --base base12a --use <your files in src/>`.
  Never plain `python build.py`. No git. No publishing.
- Scripts, logs and pictures under `out/r12/<you>/`; notes in `notes/r12-<you>.md`.
- `tools/shot.py` drives headless Chrome on the real GPU (`python tools/shot.py --help`). Set
  `PYTHONIOENCODING=utf-8`. Run one at a time. Write scripts to files; do not pass JavaScript with
  backslashes on a bash command line.
- Do not touch `tools/smoke.json`, `tools/smoke-v9.json`, `tools/smoke-v9m.json`: the other engineer runs them.
- Text on the page: plain words for a reader who is not a mathematician, sentence case, no em dashes, no
  internal names (a dial is called by its label). Never claim what was not measured.

## page: `src/body.html`, `src/js/80-ui.js`, `src/js/75-presets.js`, `src/js/90-boot.js`, `src/css/*.css` as needed, `out/r4/page/make_smoke.py`

1. **The list.** Headings from `APPROACH_GROUPS`, each before the first entry of its group; a group with no
   entry shows nothing. Ids stay `ap-<id>`, `f-<id>`, `pd-<id>`, `par-<id>-<key>`. The list must stay easy
   to scan at phone width (375 px). Keyboard use as before.
2. **Everything that used the Planes dial of Sphere inversions** (`grep -n planes src/js/80-ui.js
   src/js/75-presets.js src/body.html`): "Show Figure 4" picks the entry `fold` (planes 2, lift 0); "Back to
   one plane" picks the entry `mercator` and changes nothing else; "As it was found" for an entry found with
   two planes picks `fold` with the recorded planes (offered while one of the two Sphere inversions entries is
   in use and it is not already so), and for an entry found with one plane while `fold` is in use it picks
   `mercator`; the button's words say what it will do; the notes of the six entries under "Found with two
   planes" name the entry instead of a dial; the key in `uiOnce('julia', ...)`.
3. **Buttons for the new entry**, built like the twin buttons (`uiTwin`): "Show the quaternion square" (entry
   `lathe`, Mandelbrot solid, spin 1) and "Show the twisted quaternion square" (entry `tilt`, Mandelbrot solid,
   tilt at its starting value), each framing the whole solid. Expose them on `window.squaringLab`.
4. **Closing text.** Rewrite what speaks of "Planes at 1" or a Planes dial with two settings: there are two
   entries now. Rename "Lathe" where the text means the entry (its name is "Quaternion square (Lathe)"). In the
   twin answer, add that the twin of the Lathe is also the twisted square at a tilt of 180. Add two answers,
   in the user's order of asking, using only the facts in this file:
   - **"Is there a quaternion rule that works everywhere in space?"** Yes, one: the quaternion square. Sphere
     inversions with no plane chosen give exactly that rule (for the square the two centres are the points 1
     and −1 on the x-axis and need no plane; checked on 200,000 points, `notes/plane_free_check.py`). It spins
     the flat set about the x-axis, which gives rings, because squaring a quaternion never leaves the flat
     plane through the x-axis and the point itself. The twisted square (above) is the same product with its
     second factor twisted: the rings break up, the slice stays exact, the skin is smooth up close. The two
     buttons go here.
   - **"Could the hidden rotation axis of the flat picture show the way?"** In the flat picture, multiplying
     turns the plane, and seen from 3D that is a turn about the z-axis, so the question is a good one. A turn
     needs a plane to turn in; an axis is what is left over, and only in 3D is that a line. To carry the
     x-axis to a point v, the plane to turn in is the one that holds the x-axis and v. Its axis is the z-axis
     exactly when v lies in the flat plane, and another line for every other v. Doing that turn to v itself
     doubles the angle from the x-axis, and that is the quaternion square again. In 4D a turn leaves a whole
     plane in place, not a line, so "about the w-axis" names the same turn. What 4D adds is a second turn in
     the hidden plane at the same time, and the twisted square is what makes that second turn count.
5. **Smoke test.** Update `out/r4/page/make_smoke.py` for the new list and write the result to
   `tools/smoke-v12.json` (screenshots under `out/r12/page/smoke/`). It must pass on your page. Add steps for:
   the headings, each entry drawing, Show Figure 4 landing on `fold`, the two new buttons, "As it was found"
   switching the entry.

Time: aim for 50 minutes, stop at 70.

## tried: `src/js/10-approaches.js` (and `src/js/60-measure.js`, `src/js/20-formula.js` only if an entry needs it)

Port the rules that were tried and failed as entries with `group: 'tried'`, so the history can be seen:
`out/lab2/softfold/` ("Blended planes"), `out/lab2/axisbulb/` ("Bulbs about the axis"), `out/lab2/pillow2/`
("Pillow"). Each folder has its own `10-approaches.js` (written against an older base) and `NOTES.md` with the
verdict. For each: shader and `MATH` mirror, at most 4 dials (uA has 4 slots), and a note directly under the
name that says in plain words what it was tried for and why it fails, taken from the verdict. Say whether the
plane z = 0 is exact, from your own numbers. Do not change the seven entries that are there, except for a
defect you can show.

Check: every entry compiles and draws (Mandelbrot solid and the Julia set for c = −1) with no console errors;
`MATH` against the flat complex power on z = 0 for powers 2, 3, −1; the time the page needs until it is idle
after loading, against `dist/v12a.html` (the page compiles every approach in idle time, so three more entries
cost something: report the numbers). A prototype that cannot be ported in the time is left out and named in
the report. Never leave half an entry.

Time: aim for 40 minutes, stop at 55.

## Report (every engineer)

summary; files_changed; done (what, evidence); not_done (what, why); names_added; needs_from_others; risks.
Say what you measured and what you only reasoned.
