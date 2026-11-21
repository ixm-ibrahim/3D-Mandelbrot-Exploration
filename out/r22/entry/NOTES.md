# Round 22, section "entry": the lab entries "Along once, then one plane" and "Pulled plane"

2026-11-19, about 14:00 to 15:10. Every statement is marked **measured** (a number I computed), **seen** (in a
picture I opened) or **reasoned**. Paths are relative to the project root.

## 0. In short

- `dist/r22-entry.html` has 21 entries. The two new ones stand at the end of the list, group `inversions`:
  `alongonce` "Along once, then one plane" (no dials) and `pulledplane` "Pulled plane" (three dials: 0.05, 0.7, 16).
- They are the first entries whose ORBIT CARRIES SOMETHING. The shader got four hooks for that, all between
  `#ifdef APR_CARRY` and `#endif`; an entry that carries nothing compiles the program it compiled before
  (measured as text and as pictures, section 5).
- Both entries agree with the library's rules exactly, point for point (section 4): 0 of 120,000 orbits in
  JavaScript, 0 of 560,000 points in the shader with three neighbouring orbits running beside each point.
- **One thing nobody knew (section 6): the lab's picture of the Mandelbrot solid of "Along once" has thin curved
  wings.** Round 21 said that solid is "the one-plane solid exactly" (0 of 200,000 random points differ). The body is.
  But there are films with no thickness beside it, and the lab draws them. The entry's texts say so.
- The Stretch wording is fixed for every entry that uses the generic Learn moves (section 3).

## 1. What was changed, file by file (`changes.diff`, against `base17a`)

Six files of `src/` changed (`diff -rq base17a src` names these six and nothing else); 14 lines of `base17a` were
changed or removed, 248 lines are added.

| file | what |
|---|---|
| `src/js/10-approaches.js` | `carOrigin`, `ppPull`, `ppPower`, `ppDial`, `CARRY`, `carFirst` after `wsPower`; `MATH.alongonce`, `MATH.pulledplane`; `glTurning` split into `glTurningCore` + the four names (the text it puts together is the same, letter for letter: measured, section 5); `GL_CARRY`, `GL_ALONGONCE`, `GL_PULLEDPLANE`; the texts between `R22-TEXTS-BEGIN` / `R22-TEXTS-END`; the two entries at the end of `APPROACHES`, both `deMax: 0`. |
| `src/js/30-shaders.js` | `GL_ORBIT` only: `carStep(z, c)` inside `f`; `carStart()` at the top of `orbitDE` and where an orbit begins again from a pole; `gCarI = i` before the one call of `f`; `carFit(i, s)` after a neighbour is pulled back. All between `#ifdef APR_CARRY` and `#endif`. |
| `src/js/65-learn-steps.js` | `learnSayPower` and `learnStretchTo(F, n)` (the Stretch wording); the plan hands its own c to the rule (`MATH[id](v, n, q, c)`); `learnOdd` probes with c = 0; one more sentence in the note of the generic plan for an entry that carries something. |
| `src/js/60-measure.js` | the card and the two step figures hand the Julia constant to the rule, and the card remembers a measurement of a carrying entry under its c as well. Nothing changes for the other entries (their rules do not look at the fourth argument, their key is the old key). |
| `src/js/80-ui.js` | one line: a c dial that moves redoes formula text, step figure and card when the chosen entry carries something (otherwise `touch()` as before). |
| `src/js/90-boot.js` | one line: `window.squaringLab.CARRY` for the tests. |

Build: `python build.py --name r22-entry --base base17a --use src/js/10-approaches.js src/js/30-shaders.js src/js/60-measure.js src/js/65-learn-steps.js src/js/80-ui.js src/js/90-boot.js`.
`dist/r22-base17a.html` is `base17a` untouched, built for the comparison. Nothing was published; `squaring-lab.html`,
`base*/`, `tools/`, `docs/` were not touched.

Scripts here: `patch_shaders.py`, `patch2.py` ... `patch6.py`, `patch_learn.py` (how the edits were made; each runs
once), `run.py`, `first.js`, `smoke.py`, `parity.js` / `parity.py`, `detest.js` / `detest_run.py` / `detest.py`,
`wings.py`, `untouched.py`, `card.js`, `sheet.py`.

## 2. The two rules as built, and what I decided

`CARRY[id]` in `10-approaches.js` is the rule in JavaScript; the GLSL has the same three pieces.

- `start(q)`: what a fresh orbit carries. `step(st, z, c, q)`: called ONCE per step, before any power of that step is
  taken, with the orbit point z the step starts from and the constant c. `pw(st, v, n)`: the power in that step.
- **alongonce**: carried = how many steps have counted, this one included. `pw` is `tpPower(v, n, true)` when the count
  is 1, else `tpOne(v, n)` (= `MATH.mercator` with no turn and no lift).
- **pulledplane**: carried = w, start `(hold, 0)`. `step`: c pulls (weight `cpull`, ease `ease`), then z pulls (weight
  1), exactly the formula of the briefing. `pw`: the one-plane power about the plane at `atan2(w2, w1) / 2`.
  Dials: `hold` 0.05 ("Hold of the flat page at the start"), `ease` 0.7 ("Ease of a pull"), `cpull` 16 ("Pull of c,
  times"); they reach the shader as `uA.x, uA.y, uA.z`.

Decisions (all said in the entries' notes in plain words):

1. **A step that starts at the exact origin changes nothing** (|z|^2 < 1e-30). So the Mandelbrot orbit (start value
   0) counts from its point c. Measured: started at 0 the JavaScript rule gives the same stay counts as started at c,
   20,000 of 20,000, both entries.
2. **The point at infinity counts for nothing either** (|z|^2 >= 1e17). The orbit code puts an orbit at 1e9 on the
   x-axis when a negative power throws its start onto the pole, and begins again from there; `carStart()` is called
   at that place too. So `z^-n + c` from 0 counts from c, as the orbit code's own comment promises. Not in the
   briefing; reasoned. Smoke: the pictures of `z^-n + c` from 0 and from c both draw (not compared with anything).
3. **Several powers in one step** (`z^2 + z^3 + c`): they belong to one step. The carried thing is changed once, by
   `carStep` in `f()` before the equation is worked, with the orbit point as the modifiers leave it (|x| |y| |z|,
   flips); every power of the step reads it. For alongonce: in the first counted step every power is along's. For
   pulledplane: one pull by c and one by z, every power about the same plane. A power of something that is not z
   (`(z + 1)^2`, `conj(z)^n`) is taken about the plane pulled by z itself. This is the simplest reading and it does
   not depend on the order in which the GPU works out the terms.
4. **c is made visible** by the hook in `f(z, c)`, which has it. Nothing else changed for that.
5. **Neighbouring orbits.** For pulledplane each of the three neighbours has its own w (`gPp1..3`); after each step
   the orbit code pulls a neighbour back to a fixed small distance from the point (factor s), and `carFit` pulls its
   w back toward the point's w by the same factor, so that point and w stay one small push of the same orbit
   (reasoned). A neighbour that landed across a seam is given the point's own w (`carFit(i, 0)`). For alongonce the
   count belongs to the point's orbit only: a neighbour stands for a small push of that orbit and takes the same rule
   at every step (reasoned; a count cannot be "pulled back").
6. **`deMax: 0` (Rough) for both, by measurement** (section 4, D): with Rough no ray stopped where the set has no
   body on four Julia sets each; Exact and One neighbour stop at nothing in up to 44 % / 82 % of the stops.
7. **The card and Learn show the first squaring** (`MATH[id](v, n, q, c)`: fresh orbit, one `step`, one `pw`). For
   alongonce that is along's squaring: `MATH.alongonce` = `MATH.turnalong` to the last digit (measured at one point,
   and the card's numbers are those of Turning plane, along). For pulledplane it depends on c: the card takes the
   Julia dials' c and is measured again when a c dial moves (measured, `card.log`: the card changes when c along z
   goes to 0.3, its slice line turns to "does not follow complex arithmetic here", and comes back at 0; the cards of
   alongonce and turnalong do not change). The Learn tab takes its own c. Learn's "Next step" still shows the moves
   of a FIRST squaring; the Learn note says so. No written-out Learn moves were added.

## 3. The Stretch wording

`learnStretchTo(F, n)`: where |F(v)| = |v|^n to rounding (tested at the point on show), the move says for a whole
power above 1: "Its length is multiplied by itself, not doubled: 0.80 becomes 0.64, and 2 would become 4. A length
under 1 gets shorter, a length over 1 gets longer." (power 3: "multiplied by itself twice, not tripled ... 2 would
become 8"; power 5: "multiplied by itself 4 times, not multiplied by 5"; a length over 1 gets the example 0.5).
Other powers (2.5, -2, 1) and the special cases get the sentence of `learnSayStretch`. A rule whose length is not the
plain power keeps the old sentence: measured for `pillow` at power 2.5 ("Then the length goes from 0.80 to the rule's
length, 0.51."). Seen in `first.log.json` for turnalong, windsq, rotorframe, sqpillow, kleinsq, softfold, pillow,
axisbulb, quat4, rotor at the powers 2, 3, 5, 2.5, -2, and for the two new entries.
NOT changed: `learnSayStretch` itself, which the written-out plans use (Sphere inversions, Lathe, Mandelbulb, ...):
there the Stretch still reads "Its length, 0.80, is squared: 0.64. A length under 1 gets shorter." The briefing named
the generic move only. If the user reads Stretch as doubling there too, the same contrast could be put in that
function (one line).

## 4. Every place an orbit is iterated, and what I did there

Searched: every call of `f(`, `start(`, `cmap(`, `zmap(`, `pw(`, `sqr(`, `mul(` in the GLSL of every file; every use
of `MATH[` / `MATH.`; every `for` / `while` over orbit points in the JavaScript.

| where | what it is | what I did |
|---|---|---|
| `30-shaders.js` `orbitDE`, the loop `for (k ...)` with the inner `for (i = 0; i <= nt; i++)` around the ONE call of `f` | the only orbit loop of the scene program. Through the one call of `de()` in `main()` it serves: the picture's march, the slope samples, shadow, crevice light, the cut face, the trap-colour fit (PH_FIT), the colour query, the 2D view, the far-away probe, a mosaic cell and its Julia set, a pick, and the volume samples of a 3D model (`sampleSlice`, used by `45-export.js` / `46-mesh.js`). Neighbour orbits (i = 1..3) run interleaved with the point's own (i = 0). | `carStart()` at the top of `orbitDE`: every query starts every slot fresh. `gCarI = i` before `f`: each orbit reads and changes its own slot. `carFit` after a neighbour is pulled back. `carStart()` again where the orbit begins again from a pole. |
| `30-shaders.js` `f` | the step. One call site. | `carStep(z, c)` after the modifiers, before the equation. |
| `30-shaders.js` `start` | the start value. One call site, no squaring that counts (the start value 0 squares to 0, which counts for nothing; a start value that is not 0 is the first point that counts). | nothing |
| `30-shaders.js` `kde` (Kleinian) | not an orbit of `f`. | nothing |
| `25-colour.js` (GLSL) | reads the orbit points `orbitDE` hands over (`trapAdd`, `gLast`, `gIt`); iterates nothing. | nothing |
| `deMax: 0` does NOT switch all neighbours off: the 2D view always asks with three, a trap colour's fit with one, the cut face with three when it shows "how deep inside", a trap solid with one, a model's samples with three. | | so the neighbour slots are needed and are tested: section 4 B runs the shader with three neighbours. |
| `66-learn-view.js` `learnVBuild`: `while (orbit.length <= L.k ...)`, and the companions pushed through the moves | the Learn tab's steps, each made of the moves of `learnPlan` | not changed: every step is shown as a first squaring; the Learn note says so (section 2, 7). |
| `65-learn-steps.js` `learnRun`, `learnCheck`, `learnOdd`, `learnAgree` | one squaring each | the plan's c is handed to the rule; `learnOdd` probes with c = 0. |
| `60-measure.js` `powerF`, `updateCard` / `measureBegin` | one squaring each (card, step figures) | the Julia constant is handed to the rule; see section 2, 7. |
| `45-export.js`, `46-mesh.js`, `50-camera.js`, `70-dial.js`, `75-presets.js`, `85-pin.js`, `40-render.js` | no orbit in JavaScript: they draw or sample through the scene program. | nothing |

## 5. Tests

### A. The rule in JavaScript against the library (`parity.txt`, measured)
20,000 start points in a box, 40 steps, leaving at |v| >= 6; `CARRY` against `alongmem.c_wake1` and
`sheet.evc005e70k16`: Julia c = -1, Julia rabbit, Mandelbrot. **0 stay counts differ** in all six (120,000 orbits).
Inside: alongonce 580 / 553 / 240, pulledplane 543 / 413 / 728, the same in both.

### B. The shader, point by point (`parity.txt`, `parity-slices-*.png`, measured and seen)
Level slices of 200 x 200 points through `sampleSlice` (the picture's own program; three neighbouring orbits run
beside every point), against the library on the same points with the same number of squarings and the lab's escape
radius 64. Julia c = -1 at z = 0, 0.2, 0.45; rabbit at z = 0, 0.2; Mandelbrot at z = 0, 0.2 (the lab's orbit starts
at 0, the library's at c with one step fewer). z = 0.2 and 0.45 are not mirror planes of either rule.
**0 of 40,000 points differ in each of the 14 slices.** At z = 0 the lab equals the flat (complex) picture in all six
(0 differ). The pictures show the same shapes left and middle and an empty difference panel (seen).
This is the test that a carried state does not leak: a neighbour that wrote into the point's slot, or a state left
over from the pixel before, would change verdicts off the flat plane.

### C. The 3D picture, ray by ray (`parity.txt`, `parity-rays.png`, measured and seen)
48 x 36 probes (the lab's pick) from one camera, Rough; library: the same lines of sight, a test every 0.004.

| picture | lab stops | library has the set | both | lab only | library only | depth (lab minus library, median; 95 %) |
|---|---|---|---|---|---|---|
| alongonce c = -1 | 244 | 243 | 243 | 1 | 0 | -1.4 px; 2.1 px |
| alongonce rabbit | 324 | 323 | 319 | 5 | 4 | -1.4 px; 2.8 px |
| alongonce Mandelbrot | 195 | 124 | 124 | **71** | 0 | -0.8 px; 1.8 px |
| pulledplane c = -1 | 227 | 226 | 225 | 2 | 1 | -0.9 px; 2.1 px |
| pulledplane rabbit | 204 | 203 | 203 | 1 | 0 | -1.4 px; 2.6 px |
| pulledplane Mandelbrot | 208 | 195 | 195 | 13 | 0 | -1.6 px; 2.7 px |
| (yardstick) mercator c = -1 / rabbit / Mandelbrot | 234 / 188 / 128 | 233 / 188 / 124 | | 1 / 1 / 5 | 0 / 1 / 1 | -1.4 / -1.4 / -0.8 px |
| (yardstick) turnalong c = -1 / rabbit / Mandelbrot | 253 / 603 / 327 | 251 / 614 / 294 | | 4 / 2 / 34 | 2 / 13 / 1 | 95 %: 4.7 / 14.4 / 47.3 px |

The lab stops a pixel and a half in front of the set. The Julia pictures of the two entries match the library as
well as Sphere inversions, one plane does, and better than Turning plane, along. The 71 rays of alongonce's
Mandelbrot picture are the wings (section 6).

### D. Which distance estimate (`detest.txt`, `detest.png`, measured)
The cap lifted in the page; the same probes with Rough / One neighbour / Exact; "false" = a stop with no point of
the set within 0.03 (300 random test points); "missed" = the library has the set on the line, the lab does not stop.

| | Rough: false, missed | One neighbour: false | Exact: false |
|---|---|---|---|
| alongonce c = -1 / rabbit / Siegel / c = -0.75 | 0, 0 / 0, 4 of 323 / 0, 0 / 0, 0 | 0 / 3.7 % / 8.2 % / 1.1 % | 0 / 31 % / 44 % / 11.5 % |
| alongonce Mandelbrot | 68 of 195 (35 %), 0 | 33 % | 88 % |
| pulledplane c = -1 / rabbit / Siegel / c = -0.75 | 0, 1 / 0, 0 / 0, 0 / 0, 0 | 0.8 % / 82 % / 33 % / 0.6 % | 0 / 26 % / 1.1 % / 0.3 % |
| pulledplane Mandelbrot | 6 of 208 (2.9 %), 0 | 79 % | 52 % |

So Rough is the setting for both. (This test cannot tell fog from a film with no thickness: both are "no point
within 0.03". For alongonce's Mandelbrot solid they are films, section 6. What the finer estimates draw on the Julia
sets was not looked into.)

### E. The five untouched entries against `base17a` (`untouched.txt`, measured)
- As text: `GL_HEAD`, `GL_KLEIN`, `GL_TAIL`, `VERT`, `BLIT` identical as written. `GL_ORBIT` with comments taken out
  and the `#ifdef APR_CARRY` blocks resolved for "not defined" is identical to base17a's, line for line (163 lines).
- `approach.glsl` of all 19 old entries: same hash and length in the two pages.
- Pictures, 862 x 701 pixels of the stage's canvas with the stage's buttons hidden: mercator, lathe, turnalong,
  windsq, bulb, each as Julia set of c = -1 (3D), Mandelbrot solid (3D) and the 2D view of the rabbit:
  **0 pixels differ in all 15.** (A first run with the buttons showing had 106 differing pixels in two pictures and
  24 in two: all inside the zoom slider's strip at the right edge, x 778 to 833, not in the picture.)
- Speed: the programs are the same text, so the GPU does the same work. The clock adds nothing to that: time to draw
  the same settings a second time, all 15 pictures together, this build / base17a: 10.9 s / 9.0 s in the first run and
  10.9 s / 12.1 s in the second (the same page differs more between two runs than the two pages differ; other
  sections were computing on the machine). The 2D pictures, which are not held up by anything, took 263 to 268 ms
  in both pages, both runs. Per picture: the end of `untouched.txt`.
- The pictures and the texts above were taken again on the final build: the same result (0 pixels in all 15).

### F. Smoke (`smoke-all.log`, pictures in `smoke/`)
**Final build: 87 of 87 steps pass, no console errors, exit 0** (SMOKE-FINAL: see the last lines of this file).
`tools/smoke-v14.json` (62 steps) + round 20's 5 steps + 20 new steps, at 1400x950. One line of round 20's steps
was changed: it demanded that `windsq` is the LAST entry; it now demands that it stands right after `turnalong`.
New steps, per entry: chosen from the menu in Julia mode, name, group, place in the list, dials; the picture of
c = -1 whole; the words on the page and in "About this approach"; the same probes at Rough and at Exact (the cap
holds) and twice over; Mandelbrot view; the 2D view in both modes; power 3 (Julia and Mandelbrot), power 2.5,
`z^2 + z^3 + c` (both modes), `z^-n + c` from 0 and from c, |x| |y| |z|, flips, mosaic, the cut plane; for
pulledplane the three dials (each changes the picture; the starting values bring the first picture back exactly);
the Learn tab (moves Turn, Stretch, Add c; the Stretch sentence; Next step; the note); a 3D model of c = -1 (48
cells) ends with a file to save. Last step: back and forth between alongonce, pulledplane, turnalong, mercator: each
draws the same picture every time it is chosen.

### G. Other checks
- `first.log.json`: texts of both entries at power 2 and 3, card text, Learn plan (3 moves, chain ends where MATH
  ends: 1.6e-16 and 3.7e-16), no "undefined" / "NaN".
- `jump.txt` (measured): the tear of pulledplane's first squaring on the lines y = 0, z = +-sqrt(hold): with c = -1
  at x = -0.8 two points 2e-9 apart, one on either side, get answers 0.70 apart (the answers are 0.69 long); away
  from the line two points 2e-6 apart get answers 2.3e-6 apart.
- `card.log`: section 2, 7.

## 6. The wings of "Along once" in the Mandelbrot view (new; measured and seen)

Seen (`smoke/r22-alongonce-2-mandelbrot.png`, `sheet-for-user.png`): the flat cushion of the one-plane rule, and
thin curved wings standing off its left end.
Measured: 71 of 195 stops have no library point on their line of sight (a test every 0.004); 68 have no point of the
set within 0.03; at those stops the orbit of the stop point itself leaves after about 11 of 29 steps. The level
slices (B) agree with the library exactly, so the SET is drawn from the right rule.
`wings.txt`: I followed the line of sight through 8 such stops with the library's rule and 300 steps allowed, and
narrowed the search 20 times at a go round the place where the orbit stays longest. Two of the 8 stops are at the rim
of the solid itself (the one-plane rule stays as long there: 16 and 51 steps). Of the other six: on three lines the
longest stay grows as far as I narrowed (18, 21, 24, 27, 29, 32, 37, 38, 39 steps for windows from 0.08 down to
3e-12 wide; the other two end at 45 and 57), and no place stays for good; on one it grows from 24 to 34 and then
stops growing; on two nothing grows (10 and 11 steps: the film does not cross those lines within 0.08 of the stop,
or those stops are not on a film). Under the one-plane rule the same places leave after 2 or 3 steps. In a first
run of the same search (not kept as a file) one such place had an orbit that runs into a cycle of two points off the
flat plane, about (-1.313, -0.051, 0.837) and (0.02, 0.05, 1.263), and hovers there for the 8 steps printed.
Reading (reasoned): the wings are the points c whose first square, taken by along, lands exactly on a thin skin from
which the one-plane orbit of that c never falls off: a film with no thickness. A random test point never lies on it,
which is why round 21 found "0 of 200,000 differ" and called the solid "exactly the one-plane solid". The lab's ray
feels the film (the orbit stays longer and longer near it) and stops there, with every estimate.
So for the user: the Mandelbrot view of this entry shows a body that is the one-plane cushion, plus thin shards.
That fails the user's test 3 in the Mandelbrot view. The tag and the About text say it.
Not measured: whether the Julia sets of this entry have such films too. With Rough none showed on four Julia sets
(0 false stops); Exact stops at nothing in 31 to 44 % of the stops on the rabbit and the Siegel disc, which may be
films of the same kind or fog.

## 7. Where the sentences of the two entries come from

- "eight buds / eight separate stretches", "bare off the flat plane at 45 and 90 degrees", "c = -0.75 fused", "three
  pieces, 7.2 %, 0.11", "rabbit's c turned 10 degrees: nothing left", "0 of 200,000", buds close up (bare / along's /
  lens): `out/r21/judge/NOTES.md` (sections 0, 2 and its picture table), for `alongmem.c_wake1`. I did not re-measure them.
- "four directions, 19 and 15 degrees wide, along has eight of 13", "y = 0 cut looks like the flat picture", "one
  piece", "c = -1 + 0.2i nothing left in the plane y = 0", "a ledge", "one point in eight" (12.8 %), "336 of 720
  directions, still at 600 steps", "no bud at 45 degrees, a thin loose crescent", "Siegel disc loses 15 % between 30
  and 200 steps", "turned by 10, 30, 45 degrees nothing left", "104 of 84,000", the dial notes (4 instead of 16
  fuses; ease 1 loses a third; ease 0.5 fuses): the same file, for `sheet.evc005e70k16`. Not re-measured.
- The Rough paragraph: `detest.txt`. The wings: `wings.txt`, `parity.txt`. The tear: `jump.txt`.
- "a point belongs to a Julia set of this entry exactly when its first step lands in the solid that Sphere
  inversions, one plane draws for the same c": read off the rule (reasoned).
- The book with the x-axis as its spine: the orchestrator's comparison, briefing section 2.
- Card lines of alongonce: the measured lines of Turning plane, along (`TP_CRUSH_ALONG`, `TP_SMOOTH`), with a
  sentence in front that says the card measures the first squaring.
- "Powers other than 2 have not been looked at for this entry": true; power 3 and 2.5 were only smoke-tested for
  "draws something".

## 8. Not done, and risks

- **Speed.** "No slower" is shown by the programs being the same text, not by a clock. The wall-clock times in
  `untouched.txt` vary by a factor of two between two runs of the same page and go both ways.
- **Learn.** "Next step" shows first-squaring moves at every step for the two entries. Said in the Learn note, not cured.
- **The finer estimates** are capped away, not examined: what Exact draws wrongly on the Julia sets (fog or films) is open.
- **Powers other than 2**: the rules are defined for every power (along's planes follow the power; the pull does not
  depend on the power); only "draws something" was tested.
- **`z^-n + c`**: my reading of the pole (section 2, 2) is reasoned and smoke-tested only.
- **Trap solids, inside colouring, fly mode, phone-sized window**: not tried with the two entries (the smoke list
  runs them with other entries).
- **The dials of pulledplane off their starting values**: only "the picture changes and comes back". Every sentence
  about the entry is for 0.05 / 0.7 / 16; the note says so. With `hold` at 0 the first pull decides the plane alone
  (w starts at (0, 0); the shader reads its direction as 0 there, as the JavaScript does).
- **The sentences taken from round 21** were not re-measured here, and round 21 worked with 80 steps and the escape
  radius 6 where the lab's pictures have 40 iterations and 64.
- **The sheet for the user** says "two of them stand free, one above and one below" from round 21's measurement; in
  the lab's picture from this camera the lower one is clearly apart, the upper one overlaps the rest (seen).

## 9. Order of the runs (for whoever checks this)

- 14:24 first.js; 14:27 and 14:29 the 20 new smoke steps (first run: my own test of the Learn tab was wrong, fixed);
  14:31 parity (first); 14:36 to 14:39 the distance estimates (one step timed out at 120 s in one piece; split into 10
  steps); 14:42 untouched, sheet, parity (texts changed in between: the Rough paragraph, the wings, the tear).
- 14:45 the card test and the full smoke list, 87 steps: pass (kept as `smoke-all.before-last-sentence.log`). After
  that ONE sentence of the About text of alongonce changed (the numbers of the wings, to match `wings.txt`).
- 14:50 the final build. On it: untouched (15 pictures, 0 pixels), the 20 new smoke steps (pass), parity (A: 0 of
  120,000; B: 0 of 560,000), the card test (pass), and SMOKE-FINAL.
- The sheet's nine pictures were taken at 14:43, before the last text changes; no code that draws changed after.

SMOKE-FINAL (15:03, `smoke-all.log`, on the final build of 14:50): 87 steps ran (62 of `tools/smoke-v14.json`, 5 of
round 20, 20 new), 87 results, exit 0, "no console errors".

---

# Second pass

2026-11-19, 15:42 to about 16:20, by a second builder. The checker (`out/r22/entrycheck/NOTES.md`, section 6) found
seven defects in the first build. All seven are repaired here; none was disputed. Every statement is marked
**measured**, **seen** or **reasoned**, as above. Where this section and sections 0 to 9 disagree, this section holds.
The first pass's page, diff, sheet and logs are kept in `out/r22/entry/pass1/`.

## S0. In short

- `dist/r22-entry.html` is rebuilt (15:56) and is the build of the current `src/` (measured: built again under
  another name, byte-identical). Nothing that DRAWS changed: the GLSL of the two entries and the orbit code are the
  same text as in the first pass's page (measured, S4). What changed is the card, the Learn tab and the words.
- Smoke: **90 of 90 steps pass, exit 0, no console errors** (16:02): the 87 of the first pass plus 3 new steps, one
  per group of defects (`second.py`).
- Parity and the five untouched entries were run again on this build: the same numbers as before (0 of 120,000
  orbits, 0 of 560,000 shader points, 0 pixels in 15 pictures).
- Files of `src/` that differ from `base17a` now: `10-approaches.js`, `30-shaders.js`, `60-measure.js`,
  `65-learn-steps.js`, `66-learn-view.js`, `90-boot.js`. **`80-ui.js` is base17a's again** (its one changed line is
  no longer needed); **`66-learn-view.js` is new on the list.** `changes.diff`: 564 lines, 308 added, 21 changed or removed.

## S1. The defects and what was done

| # | defect (checker's words, short) | cure | proof |
|---|---|---|---|
| 1 major | card of Pulled plane stale after "Jump to a point" | The card now watches the c it was made for. `60-measure.js`: `cardCKey(a)` is what the card depends on besides entry, dials and power (empty for every entry but Pulled plane); `updateCard` remembers it in `cardRun.ck`; the hook `drawStep3d`, which runs whenever a new picture is asked for and already followed the power, now also redoes card and step figure when that key has changed. So every way of moving c is covered at once (dials, "Jump to a point", a saved point, an example), not one caller at a time. The first pass's patch of the c dials in `80-ui.js` is taken out. | measured, `second.log` step 2: card at c = -1 "Roundness 51 %, 38 % of directions land mirror-reversed"; the rabbit chosen from the menu, nothing else touched: "Roundness 64 %, never reverses", and the same text after a full refresh; back to c = -1 through `applyJuliaPreset` with a point that is in no list (what a saved point calls): the first card again. The builder's `card.js` (c dials) passes again (`card.log`). A real saved point was not clicked. |
| 2 major | a c out of the flat plane: shards or a slab where no point of the set is, and the texts do not say so | Text only, as the checker asked. Both notes: the Rough sentence now says the four c "all lie in the flat plane", and goes on: "For a c out of the flat plane (the dial "c along z" away from 0) that does not hold, and the picture can show what is not there: ..." with what the picture shows and how many of 400,000 points stayed, and that Sphere inversions, one plane does the same. Both About texts: "The picture does not show that emptiness. It shows ..." right after the sentence that no point was left. The sheet for the user got a line at the foot saying the same. | The numbers are the checker's (`out/r22/entrycheck/offplane.txt`, `parity.txt` there: 0, 0, 94, 66 of 400,000; 244 of 1,200 rays for the one-plane entry on an empty set): measured by the checker, not by me. The shapes: seen, I opened the checker's four pictures `break/*-19-*.png`, `break/*-20-*.png`. Measured by me on this build (`second.log` step 4): the lab stops 13 and 12 of 165 probes for Along once (rabbit's c turned 10 degrees; c = (-1, 0, 0.3)) and 21 and 2 for Pulled plane, so the pictures are indeed not empty. **The drawing itself is NOT cured**: see S5. |
| 3 minor | Stretch: "2 would become 4" is the one number where doubling and squaring agree | `65-learn-steps.js`: the example is now 3, with what doubling would give: "Its length is multiplied by itself, not doubled: 0.78 becomes 0.61, and 3 would become 9, not 6." (power 3: "3 would become 27, not 9"; above power 6 no example). And the written-out plans (Sphere inversions, which the page opens with, Lathe, the Mandelbulbs, the flat part of Split), which had no contrast at all, now say: "Its length, 0.78, is squared: 0.61. Squared means multiplied by itself, not doubled: 3 would become 9, not 6. A length under 1 gets shorter." | measured, `second.log` step 3 (turnalong, alongonce, pulledplane, mercator, lathe at power 2; mercator at power 3; power 2.5 keeps the old sentence), `extra.log` (power -2 keeps the old sentence). This goes beyond the one function the briefing named: `learnSayStretch` serves every written-out plan. The 67 old smoke steps pass with it. |
| 4 minor | Learn, "Next step": the point shown is not the entry's orbit | Cured, not only said. `learnPlan` takes `carry`, what the orbit carries when the step begins (left out: a fresh orbit), and hands back `plan.carry(v)`, what it carries after the step that starts at v. `learnVBuild` (`66-learn-view.js`) makes a new plan for each later step of an entry that carries something; every other entry keeps its one plan (same code path as before). The Learn note now says: "The moves on show are those of the step on show: the first step is the first squaring of an orbit, and after "Next step" they are the moves of the squaring the orbit has come to." | measured, `second.log` step 3: from (0.6, 0.3, 0.4) with c = (-0.3, 0.2, 0.1) the Learn tab's second point is (-0.50, 0.05, 0.74) for Along once and (-0.64, -0.10, 0.52) for Pulled plane, which are the checker's "own" points; over 4 steps Learn is 6e-16 and 1e-16 away from the orbit worked with `CARRY`, also with \|x\| \|y\| \|z\| ticked (2e-16), and the moves on show end where the orbit goes next. turnalong, mercator, lathe: Learn equals plain iteration (under 1e-15), as before. `extra.log`: the same at power 3 and -2 and with Pulled plane's dials at 0.2 / 0.4 / 5 and 0 / 1 / 0; on a page and on a line both entries follow the flat rule. |
| 5 minor | Mandelbrot view: the card of Pulled plane depends on the hidden Julia constant | In a Mandelbrot picture every point is its own c and the first squaring that counts is the squaring of c. So there the card (and the step figure) take c to be the point that is squared: `cardRule` calls `MATH.pulledplane(v, n, q, v)`. The note says so: "taken with the c of the picture: in a Julia picture the c of the Julia dials, and in a Mandelbrot picture, where every point is its own c, the point that is squared." | measured, `second.log` step 2: the Mandelbrot card reads the same with the hidden c at -1 and at the rabbit ("Roundness 51 %, 40 % of directions land mirror-reversed", slice line "follows complex arithmetic exactly"); `extra.log`: unchanged after the Kleinian view and after another entry was chosen and left. The choice "c = the point" is mine (reasoned from the briefing's convention for the Mandelbrot orbit); a start value other than 0 or c is not taken into account. |
| 6 minor | dial label "Ease of a pull" | Now "How little a thing near the page turns it". The key stays `ease` (the smoke steps and saved settings use it); the help text was already plain. | measured: on the page, the old label nowhere (`second.log` step 2). Phone-sized window 390 x 844: the label wraps to two lines like its neighbours, nothing wider than the window, page scroll width 390 (`phone.log`; `phone-pulledplane.png` seen). |
| 7a minor | a power-2 measurement quoted at every power | `ppSmooth` quotes "measured with c = -1 at x = -0.8 ..." only at power 2 with the first dial at 0.05, where it was measured; elsewhere "(read off the rule)". With the first dial at 0 it says there is no such line in the first squaring (reasoned: the plane then follows the first pull, which has no jump off the x-axis). | measured, `second.log` step 4 (powers 2, 3, 2.5, -2; first dial 0.2 gives z = ±0.45; first dial 0). |
| 7b minor | the card of Along once measured again for every c; remembered measurements pile up | Only an entry whose FIRST squaring depends on c is keyed by c: `CARRY.pulledplane.usesC`. Along once is called and remembered exactly as every old entry. A measurement that depends on c is remembered for the c in use only (the others are dropped when a new one is stored). (The memory was already capped at 40 entries, so "never dropped" was not quite so; but a sweep of c would have pushed out every other entry's measurement.) | measured, `second.log` step 2: after four values of "c along y" one remembered measurement with a c in its key; Along once: 3 remembered before and after a move of c, card text the same. |
| 7c minor | not said: a power in the start value is taken with a fresh state and not counted | Both notes now say: "A power written into the start value (as in the start value c²) is taken before the orbit begins and does not count as a squaring: it is taken by Sphere inversions, one plane." (Pulled plane: "about the flat page.") | reasoned from the shader (`carStart()` runs before `start()`; `start()` calls no `carStep`), as the checker did; smoke step 4 checks the words are there. |

Also changed, not on the checker's list:
- The entries' notes no longer say that the Learn tab shows the first squaring only (it no longer does); they say
  "The Learn tab follows the orbit: its first step shows a first squaring, and after "Next step" the moves are those
  of the squaring the orbit has come to."
- The sheet's caption for the rabbit of Along once said "two of them stand free, one above and one below" while the
  upper one overlaps the rest from that camera (the first pass's own open point). Now: "two are not joined to the
  rest (one below; one above, seen here in front of the others)." Seen in the new sheet.

## S2. Orbit loops, again

Nothing in the GLSL changed, so section 4 stands for the shader. The one JavaScript loop over an orbit, the Learn
tab's `learnVBuild`, now carries the entry's state from step to step (defect 4). One thing it does NOT do (reasoned):
the companions on show (the circle or the cloud of points pushed through the moves) are pushed through the moves of
the step on show, made with what the MAIN orbit carried before that step; a companion is not given a history of its
own. For the first step that is exact; for later steps it shows "what this step does to points near the orbit's
point", which is what the picture is for.

## S3. Tests on this build (all on the page built 15:56; `src/` not touched after)

- **Smoke** (`smoke-all.log`, 16:02): 90 steps ran, 90 results, exit 0, "no console errors", 1400 x 950: the 62 of
  `tools/smoke-v14.json`, round 20's 5 (with the one line changed as in the first pass), the first pass's 20 (two
  lines of its Learn step changed: it asked for the old Learn note and the old example), and 3 new (`second.py`).
- **Second-pass steps alone** (`second.log`): the three steps pass; the numbers in the table above are from it.
- **Extra** (`extra.log`, `extra.js`): Learn at power 3 and -2 and with the dials moved, on a page and on a line;
  the card through the Kleinian view and through another entry in the Mandelbrot view. All pass, no console errors.
- **Parity** (`parity.txt`, run again 16:04): A 0 of 120,000 orbits differ; B 0 of 40,000 in each of 14 slices, flat
  cuts equal to the flat picture; C the same table as section 5 C to the last digit (alongonce 244/243, 324/323,
  195/124 with 71 lab-only; pulledplane 227/226, 204/203, 208/195).
- **Five untouched entries** (`untouched.txt`, shot again 16:06 on both pages): 0 pixels differ in all 15 pictures;
  approach.glsl of the 19 old entries identical; orbit code identical with APR_CARRY not defined (163 lines). Time to
  draw all 15 again: this build 8.9 s, base17a 9.2 s (one run; the clock still proves nothing, the text does).
- **The two entries draw what they drew in the first pass** (measured as text, not by pictures): `GL_CARRY`,
  `GL_ALONGONCE`, `GL_PULLEDPLANE`, `glTurningCore` and `GL_ORBIT` are letter for letter the same in
  `pass1/r22-entry.pass1.html` and in the new page; `30-shaders.js` was not edited. So the checker's own parity
  runs (off-plane c, dials moved, power 3, 23 slices), the distance-estimate test and the wings test were not
  repeated; they hold for the same program.
- **The sheet** (`sheet-for-user.png`): the nine pictures were shot again from this build (16:07) and look the same
  as the first pass's (seen); two captions changed (S1).

## S4. What the user will read differently

- Stretch, every entry: the length is "multiplied by itself, not doubled", with 3 -> 9, not 6.
- Learn, the two entries: "Next step" now shows the entry's own second, third, ... squaring. For Along once the
  second step visibly changes character (the first is along's swing, the later ones the one-plane move); for Pulled
  plane each step is about the page the orbit has by then.
- Pulled plane: the card follows c wherever c comes from; in the Mandelbrot view it no longer depends on anything
  hidden; second dial renamed.
- Both entries: the note and the About text say that with "c along z" away from 0 the picture can show shards or a
  slab where nothing stays.

## S5. Still open after the second pass

- **False shards for a c out of the flat plane are still DRAWN.** The cure is a sentence, not a better picture. It is
  the page's Rough estimate, and Sphere inversions, one plane (published, version 17) draws the same ghosts and its
  texts do not say so; I did not touch that entry. Why the ray stops there (films with no thickness, as in the wings,
  or plain fog) was not examined.
- The wings of Along once in the Mandelbrot view (section 6): unchanged, still a finding for `mandel` and `judge`.
- The card in the Mandelbrot view takes c = the point: my reading. For Along once and every old entry nothing changed.
- `learnSayStretch` now carries the contrast in every written-out plan; that is more than the briefing named.
- The label "How little a thing near the page turns it" says "page" where the dial's help says "plane" (the About
  text explains that the planes are the pages of a book). Not unified.
- Shape sentences taken from round 21 (other than the three the checker re-measured): still not re-measured.
- Powers other than 2, z^-n + c, modifiers, mosaic, cut plane: the pictures are still only "draws, no error"
  (the checker compared the shader with the page's own JavaScript rule for power 3, z^2 + z^3 + c and |x||y||z|: 0 differ).
- Exact / One neighbour for the two entries: capped away, not examined. Speed of the two entries: not measured.
- A real saved Julia point and the Examples list were not clicked (they go through `applyJuliaPreset` / `refresh`,
  both of which bring the card up to date: the first measured through the function, the second reasoned).
- Left in `dist/`: `r22-base17a.html` (base17a, for the comparison). `out/r22/entry/smoke.py` still patches one
  line of round 20's steps at run time. `out/r22/entry/pass1/` holds the first pass's page and results.

SMOKE-FINAL, second pass (16:02, `smoke-all.log`, on the build of 15:56): 90 steps ran (62 of
`tools/smoke-v14.json`, 5 of round 20, 20 of the first pass, 3 new), 90 results, exit 0, "no console errors".
