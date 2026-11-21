# Round 14: three more rules to try, and the approach as a menu

The user is searching for the right way to carry z → z² + c into 3D. They are not a mathematician; they
judge by pictures and plain words. **This round is about trying rules, not about polish**: build, draw, say
honestly what came out. No long test campaigns.

## What the user asked (2026-11-18, verbatim)

> yes try it as a new approach.
> and then changes for what I see now:
> * the approaches section should also be a menu, and consolidated with the equation section, in which the
>   section under the menu has the unique parameters for that approach (the explanation can just be visible
>   when hovering on an approach)
> * add the pure quaternion approach, like the 4d mandelbrot and us seeing slices of it in 3d
> * see the attached image for my conversation with the google ai in squaring a 3d vector (seems like it's
>   only defined in the 1, 2, 4, and 8 dimensions). explore this as yet another approach

"it" in the first line = the road of Kučera's paper (`notes/paper-kucera.txt`, read it): squaring replaced by
sphere inversions, a different one in each region of the sphere of directions. The attached image is a recipe
from geometric algebra: "pick a reference direction (like the z-axis, e3); find the rotor R that rotates e3
onto v; square the rotor; apply R² to the reference axis and scale by |v|²".

## Base

`base14a/` (page `dist/v14a.html`) = the published Version 13 plus the finished shader fixes. Build only
with `python build.py --name r14-<you> --base base14a --use <your files in src/>`. Never plain
`python build.py`. No git, no publishing. Scripts, logs, pictures under `out/r14/<you>/`.
`tools/shot.py` drives headless Chrome on the real GPU (`--help`); set `PYTHONIOENCODING=utf-8`; one run at a
time; write scripts to files; run from the project root. `tools/smoke-v12.json` is the page's test (60 steps).

Words on the page: plain, sentence case, no em dashes, a control is called by its label, nothing is claimed
that was not measured. Every entry says honestly what it is and where it falls short.

| who | files |
|---|---|
| rules | `src/js/10-approaches.js`, `src/js/30-shaders.js` (one small hook only), `src/js/65-learn-steps.js` if needed |
| menu | `src/body.html`, `src/js/80-ui.js`, `src/css/00-base.css`, `src/css/65-learn.css`, `src/js/66-learn-view.js` if needed, `out/r4/page/make_smoke.py` (writes `tools/smoke-v14.json`) |
| turns | nothing in `src/`: a stand-alone trial under `out/r14/turns/` |

---

## rules: five new entries in the Approach list

Read `src/js/10-approaches.js` top to bottom first: every entry has id, name, group, glsl (defining `mul`,
`pw`, `sqr`, `cmap`), axis, tag, params (at most 4 dials: the shader gets them as `uA` in spec order), formula,
about, roundNote, crush, smooth, slice; `MATH[id]` mirrors the shader's power in JavaScript; `APPROACH_GROUPS`
gives the headings. Add a group `{ id: 'kleinian', title: 'Inversions by region (the paper’s road)' }` after
'inversions'. For each new entry check `MATH` against the shader (probes of the picture or `sampleSlice`), and
the claims below by numbers. Report what you measured.

### 1. `quat4`: "Quaternions, 4D (slices)", group quaternion

The quaternion Mandelbrot set lives in 4D: q → q² + c with q and c quaternions (a, b, c, d) = real, i, j, k.
The picture shows a 3D slice of it. Dials: `w` "Slice position on the fourth axis" (−1.5 to 1.5, starts 0),
`tilt` "Slice tilt toward the fourth axis, degrees" (−90 to 90, starts 0), `cw` "The point c on the fourth
axis (Julia sets)" (−1.5 to 1.5, starts 0).

- A picture point P = (x, y, z) stands for the 4D point E(P) = (x cos t − w sin t, y, z, x sin t + w cos t).
- A quaternion orbit never needs more than three numbers: with A the real part, and the imaginary part split
  into its part β along the imaginary part of c and its length μ across it, one step is
  (A, β, μ) → (A² − β² − μ² + Re c, 2Aβ + |Im c|, 2Aμ): the Lathe rule with c = (Re c, |Im c|, 0).
- Mandelbrot picture: c = E(P), z starts at 0. So `cmap(P)` = (E.a, length of (E.b, E.c, E.d), 0).
- Julia picture: c = (cx, cy, cz, cw) from the page's c and the dial; z starts at E(P), reduced:
  u = Im c / |Im c| (any unit vector when Im c is 0), β = Im E · u, μ = |Im E − β u|, start (E.a, β, μ);
  `cmap` gives (cx, |Im c|, 0). The shader reads `uJulia` (> 0.5 in a Julia picture).
- The shader starts a Julia orbit at the picture point itself. Add ONE hook in `src/js/30-shaders.js`: when an
  approach's GLSL defines the macro `APR_ZMAP`, the Julia start is `zmap(point)` (the neighbouring orbits of
  the distance estimate too); otherwise nothing changes for any other approach (their pictures must stay
  identical: compare a few before and after).
- The arithmetic (`mul`, `pw`, `sqr`, `MATH`) is the Lathe's with spin 1.
- Check against the real thing: write the 4D iteration with plain quaternion multiplication in a test script
  and compare, for thousands of points, which stay bounded: Mandelbrot at several w and tilt; Julia with cw
  not 0 and a tilted slice. Expected and to be said on the page: at w = 0, tilt = 0, cw = 0 this is exactly
  "Quaternion square (Lathe)". With w not 0 the Mandelbrot solid is still made of rings (a solid of
  revolution about the x-axis) and its slice at z = 0 is no longer the flat set. With tilt at 90 it is
  nested shells. Julia sets with cw not 0, or a tilted slice, are the classic quaternion Julia shapes.

### 2. `rotor`: "Rotor square (geometric algebra)", group quaternion

The recipe of the user's image. Dials: `lon` "Reference axis, longitude, degrees" (−180 to 180, starts 0) and
`lat` "Reference axis, latitude, degrees" (−90 to 90, **starts 90: the z-axis, as in the recipe**). Reference
axis a = (cos lat cos lon, cos lat sin lon, sin lat). The rotor that takes a onto the direction of v turns by
the angle α between them, in the sheet that holds both; squaring it doubles α (power n: n·α):
vⁿ = |v|ⁿ (cos nα · a + sin nα · u), u = the unit vector in that sheet square to a, on v's side.
- This is the Lathe rule about the axis a. Expected, to be checked by numbers and said plainly: with the
  reference along the x-axis (lat 0, lon 0) it is exactly "Quaternion square (Lathe)"; for any other axis the
  solid is the same solid turned in space (the rule about axis a = turn ∘ Lathe ∘ turn back). Rotors are
  unit quaternions, which is why. The plane z = 0 carries the flat set only with lat 0 and lon 0 (with lat 0
  and another lon it carries the flat picture turned by lon).
- "Quaternion square, twisted" is this rule with the reference axis tilted inside the flat plane and the
  result turned back; say so in the note.

### 3. `rotorframe`: "Rotor square with a frame", group quaternion

The natural next step of the same recipe: one reference axis leaves the rotor one number short (a spin about
the axis is free), so take a whole reference frame: x forward, z up. The rotor that takes the frame to the
point's own frame without any roll is R = turn about z by the longitude φ, after a tip up by the latitude β:
R = Rz(φ)·Ry(β) (as a rotation: e_x ↦ (cos β cos φ, cos β sin φ, sin β)). Rule: vⁿ = |v|ⁿ · Rⁿ e_x (Rⁿ = the
rotation about R's own axis by n times its angle). For n = 2 this is "do to the point the same turn that
carried the x-axis to it". No dials (or one, if you find a meaningful one).
- To check and say: the plane z = 0 is exact (β = 0: longitude doubles). The half of the plane y = 0 with
  x > 0 is exact too (latitude doubles), the half with x < 0 is not. Where does it tear or crush (the z-axis,
  where the longitude means nothing; the half-plane y = 0, x < 0)? It is a different rule from the Lathe and
  from the Mandelbulb (which doubles the two angles separately: Rz(2φ)·Ry(2β)): show one picture pair.

### 4. `kleinsq`: "Kleinian squaring, one plane", group kleinian

The paper's first construction, as far as its text lets it be rebuilt (the paper leaves out the details; say
on the page that this is a reading of it). For a whole power n ≥ 2: n + 1 caps on the sphere of directions,
centred on the equator at longitudes θ_k = (2k + 1)·180°/(n + 1), each of angular radius 180°/(n + 1)
(direction d is in cap k when d·a_k > cos(180°/(n + 1)), a_k = (cos θ_k, sin θ_k, 0)). Sphere k has centre
a_k / cos(180°/(n + 1)) and radius tan(180°/(n + 1)); it meets the unit sphere at right angles. For n = 2
these are the paper's spheres: radius √3, centres (1, √3, 0), (−2, 0, 0), (1, −√3, 0).
- Direction rule: H(d) = mirror_y(inversion in sphere k of d) when d is in cap k; H(d) = mirror_y(d) outside
  all caps (mirror_y: y → −y). This H is continuous on the whole sphere (an inversion leaves its own sphere
  in place, so both formulas agree on a cap's rim) and keeps shapes on every piece.
- Power: vⁿ = |v|ⁿ · H(v/|v|). For a power that is not a whole number ≥ 2 use the nearest whole number ≥ 2
  for the caps (and a final inversion for a negative power, as the other entries do); say so. `mul`: use the
  product of "Sphere inversions, one plane" and say so.
- To check and say: on the equator H copies the pattern of zⁿ (it agrees with zⁿ at the n + 1 points where
  the caps touch, and takes each arc onto the n other arcs) but not its numbers, so **the slice at z = 0 is
  a cousin of the flat set, not the flat set**. Measure how far H is from true angle doubling on the equator
  (largest difference in degrees). Dial: none needed; if useful, a "Planes" choice is entry 5.

### 5. `kleinsq2`: "Kleinian squaring, two planes", group kleinian

The paper's second construction (its Figure 4): the same caps also round the equator of the plane y = 0 (the
first family turned 90° about the x-axis, with mirror_z). A direction with |z| ≤ |y| uses the first family,
one with |z| > |y| the second. Expected, to be checked by pictures: the Julia set for c = −1 shows beads
round two circles (compare with the entry "Sphere inversions, two planes"); with c off the x-axis the solid
tears along the planes |y| = |z|, which is the limit the paper itself states ("limited to c ∈ R").

Pictures to deliver for every new entry (contact sheet under `out/r14/rules/`): Mandelbrot solid, the Julia
sets for c = −1, for the rabbit (−0.1226, 0.7449, 0) and for c = (−1, 0.15, 0.1), and the cut at z = 0.

Time: aim for 70 minutes, stop at 90. Order: 1, 2, 4, 5, 3. An entry that does not fit is left out whole.

---

## turns: both rules at every step (stand-alone trial, `out/r14/turns/`)

The paper's second construction has a rule for the plane z = 0 and the same rule turned 90° for the plane
y = 0. Any way of choosing between them region by region leaves a seam (entry 5 above). A Kleinian limit set
has no such choice: every generator is applied in turn. The trial: **let both rules apply at every step.**
A point is then in the set when its orbit stays bounded for SOME order of the two rules (the "union" set), or
for EVERY order (the "common" set). No region is chosen by hand, so there can be no seam.

Try it for two pairs of rules:
- K: the Kleinian squaring H of "rules" entry 4 for the plane z = 0, and the same turned 90° about the
  x-axis (swap y and z before and after).
- E: the exact rule of "Sphere inversions, one plane" (`MATH.mercator` in `src/js/10-approaches.js`: longitude
  doubles, Mercator latitude doubles), and the same turned 90° about the x-axis.

For each: the Julia sets for c = (−1, 0, 0), (−1, 0.15, 0.1), the rabbit (−0.1226, 0.7449, 0) and
(−0.6, 0.3, 0.3); and the Mandelbrot solid (z starts at 0; c is the picture point). Union and common set.
Orders are tried to a depth you can afford (say 8 to 12 steps: up to 2^depth orders, with early exits: an
order whose orbit has left radius 4 is dropped; for the union set one bounded order is enough at the last
step). Build it as your own small WebGL 2 page or as a numpy voxel job, whichever gets pictures soonest;
lighting can be simple. Nothing in `src/` is edited.

Report with pictures (contact sheets) and plain words: Is the set whole for c off the x-axis (no tear)? Does
it show beads round two circles for c = −1? Is it a fat blob, dust, or something with fine structure? What is
its slice at z = 0 compared with the flat Julia set (the same, bigger, smaller)? How does K differ from E?
Which of the four (K or E, union or common) is worth building into the lab, and what would it cost per
picture point? Say what you measured and what you only saw by eye.

Time: aim for 60 minutes, stop at 80.

---

## menu: the approach is a menu, in one section with the equation

Today "Approach" is a long list of radio entries, each with tag, formula, explanation and its dials, in its
own section above "Equation". Wanted:

- **One section**, "Approach and equation", in place of the two. First in it: the approach as a **menu** (a
  compact control that shows the chosen approach and opens a list of all of them under their group headings).
- **Under the menu: only the chosen approach's own dials** (and its notes that depend on the dials).
- **The explanation shows when hovering on an approach** in the open menu (name, the one-line tag, the formula,
  the explanation), and on keyboard focus. A finger cannot hover: on a touch screen a small "About this
  approach" control under the menu opens the same text for the chosen approach. Keep it out of the way.
- Then the equation controls as they are (Start from, Each step z becomes, The Mandelbrot set starts z at, the
  power dial, notes, reset). One reset for the approach dials, one for the equation, as today, or one for
  the section if that reads better.
- Works for any number of entries and groups (another engineer is adding five entries and a group now).
- Keep the ids the tests and the other modules use: the radio inputs `ap-<id>` (they may live inside the
  menu's list; `$('ap-lathe').click()` must still choose that approach), `f-<id>`, `pd-<id>`,
  `par-<id>-<key>`, `secEq` and `secApproach` (one of the two may stay as an empty hidden element if some
  code or style needs it; search for both names, `src/css/65-learn.css` and `src/js/66-learn-view.js`
  included: the Learn tab shows the approach and the power, and must still do so).
- Phone width (375 px): the menu and its list fit the window; the list scrolls inside itself if long.
- Update `out/r4/page/make_smoke.py` so that it writes `tools/smoke-v14.json` (leave `tools/smoke-v12.json`
  as it is) and passes on your page.

Time: aim for 50 minutes, stop at 70.

---

## Report (everyone)

summary; files_changed; done (what, evidence); not_done (what, why); names_added; needs_from_others; risks.
