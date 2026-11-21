# Round 20, section "entry": the lab entry "Wind, then square" (id `windsq`)

Started 00:21, finished about 01:10 (2026-11-19). Julia sets only. No Mandelbrot picture of the rule was looked at
or described (see "Risks" for what the smoke list does on its own).

## What was built

- `src/js/10-approaches.js`: 81 lines added, no line of `base16a` changed or removed (`10-approaches.diff`).
  No other file of `src/` was touched (checked file by file against `base16a/`).
  - helper `wsCount(n)`, `wsPower(v, n)` after `tpPower`; `MATH.windsq`; shader `GL_WINDSQ`; texts between
    `R20-TEXTS-BEGIN` / `R20-TEXTS-END`; the entry at the end of `APPROACHES`, group `inversions`, no dials,
    `deMax: 0`.
  - k for the power n: m = whole number nearest to |n| (at least 1); k = m if m is odd, m + 1 if even. k = 1 is
    the one-plane rule itself (powers that round to 1).
  - cos and sin of the wound angle come from multiplying (y + iz)/rho by itself k times and
    sin(2ka) = 2 sin(ka) cos(ka): no atan in the rule, in JavaScript or in the shader. A point with z exactly 0
    takes the one-plane power as it stands.
- `dist/r20-entry.html`, built with `python build.py --name r20-entry --base base16a --use src/js/10-approaches.js`.
- Scripts here: `patch1.py` (the code), `put_texts.py` (the words; idempotent), `run.py`, `checks.js`, `rule.py`,
  `stretch.py`, `thick.py`, `measure.py`, `brute.py`, `flatcmp.py`, `pics.py`, `make_sheet.py`, `card.js`, `smoke.py`.

## What I expected before testing, and what came out

| expected (written down before the run) | result |
|---|---|
| MATH.windsq = the bench rule `m_w3` at power 2 to about 1e-14 | measured: largest difference 3.3e-15 (6,000 points in a ball), 2.6e-15 (7,000 points beside the planes and axes). Holds. |
| z = 0 in gives z = 0 out, same x, y as one plane, at every power | measured: 0 of 4,000 points with z not zero, at powers 2, 3, 4, 5, -2, 2.5, 1, 0.5. Holds. |
| half-planes sent INTO the flat plane: 6 at powers 2, 3; 10 at powers 4, 5 | measured: exactly those (0, 60, ..., 300 degrees; 0, 36, ..., 324 degrees), to 6e-15; all others miss by 0.8 to 1.5 of the length. Holds. |
| no jump; gap / step steady | measured: 14.4 to 14.7 at power 2 over steps 1e-3 to 1e-6 (32, 110, 205 at powers 3, 4, 5). Holds. |
| mirrors commute; a turn by 360/k leaves the answer unchanged; a turn by 180/k gives the answer half-turned | measured: 0, 0, 2.4e-15, 2.4e-15 at power 2 (up to 1e-14 at power 5). Holds. So for c on the x-axis the set repeats every 60 degrees, for other c every 120 degrees. |
| shader = MATH to GPU accuracy | measured: largest 6.8e-5 of the length at power 2 (median 1.2e-7), 1.9e-4 at power 5; z exactly 0 kept; mul = one-plane product (difference 0). Holds. |
| bud directions arrive with stretch exactly 2; crushed directions half way; nothing folded | measured (`stretch.txt`): ratio to the plane 1.000000 at the 2k bud directions, powers 2 to 5; two stretches fall to 0 (under 2 %) at the 2k directions half way; 0 of 400,000 directions mirror-reversed at powers 2, 3, 4 (2 at power 5, at the crush, rounding). The page's own scorecard: "wraps the sphere of directions 6 times and never reverses it" at power 2, 9 times at power 3. Holds. |
| Exact distance estimate would be fine (no fold, one formula) | WRONG. Exact and One neighbour draw a spindle of fog. Only Rough draws nothing false. See below. |
| the skin between the planes is clean (I first cut it at x = 0 and it was) | WRONG away from x = 0: ragged with thin needles at x = 0.2, spikes at x = -0.3. x = 0 is a special place. |
| off the x-axis the copies in the three planes make a body | WRONG: only the part near the x-axis is a body; the rest is thin plates (rabbit) or sheets (Siegel disc). |

## deMax: Rough (0), measured

`measure.py`: for a scene and an estimate the lab draws the set; 33 x 25 rays are sent through the picture with the
lab's own pick; every stop is compared with the set itself worked point by point (page's MATH, 64-bit, same number
of steps, escape radius 64). "False" = a stop with no point of the set within 8 pixels. `measure-main.txt`,
`measure-skin.txt`, `measure-step.txt`, `measure-calib.txt`; pictures `_look-de-*.png` (looked at).

| view (40 iterations) | Rough: false | One neighbour: false | Exact: false |
|---|---|---|---|
| basilica whole | 0 of 128 | 351 of 359 (98 %) | 194 of 215 (90 %) |
| basilica, touching point close | 1 of 667 | 99 % | 99 % |
| basilica, bud close | 3 of 306 (1.0 %) | 98 % | 92 % |
| basilica, skin at 30 degrees from outside | 0 of 825 | 92 % | 88 % |
| basilica, bud at 60 degrees from outside | 3 of 773 | 90 % | 87 % |
| rabbit whole | 1 of 213 | 75 % | 21 % |
| Siegel disc whole | 1 of 215 | 84 % | 29 % |

Seen: with Exact and One neighbour the basilica is a lens of fog, the rabbit and the Siegel disc a lumpy rock that
is not there. Yardstick (`measure-calib.txt`): Sphere inversions, one plane with Exact stands 4 to 8 pixels off the
set (0 stops further than 16), so the test is fair. Left out of the table: one basilica view whose camera sat inside
the body (my mistake), and the dendrite at 20 steps (almost no inside: 5 of 825 rays meet the set; the lab stops 35
rays, 13 of them with no point of the set within 8 pixels even with Rough: its flecks are drawn a little fat).

Rough's own fault (measured): it steps over thin sheets. Rays that meet the set but stop at nothing, with ray step
0.8 / 0.4 / 0.2: basilica 3 / 1 / 0 of 128; rabbit 58 / 15 / 1 of 254; Siegel disc 60 / 15 / 1 of 265. Smaller
steps cost false stops instead (basilica 0 / 5 / 35). The entry's note says this with the numbers. The page opens
with 0.8 and the entry cannot change that (it would need a change in `40-render.js`; not made).

## What the pictures show (all looked at)

`sheet-for-user.png` (the lab, 40 iterations, three rules, two cameras, seven sets), `close.png` (basilica and
rabbit close, with point-by-point cuts under them), `look-bas-14.png`, `_look-*.png`.

- **Basilica (c = -1): the good one.** A row of separate bodies with six buds round each (seen in the lab picture
  along the x-axis and in the cut across x = 0), smaller buds on those. Cut across the touching point, 0.2 wide,
  40 steps: 0 of 129,600 points in the set (measured). The bud at 60 degrees is a body: an oval 0.133 by 0.121
  when cut along the x-axis (measured). BUT the skin is not clean: the lab draws it streaked and grainy, bristly
  like a sea urchin seen along the axis; point by point the outline between two planes is smooth at x = 0 and
  ragged with thin needles at x = 0.2 (`brute-bas-x02-skin.png`), with a dozen spikes and specks at x = -0.3, and
  the bud has a fringe of 197 loose specks. Next to Turning plane, along in the sheet it has the same kind of
  bodies and buds and a busier, rougher skin. At 14 iterations the bodies are still joined by short necks (seen).
- **San Marco, cauliflower:** ribbed from end to end. Cut across the x-axis the cauliflower has twelve lobes (a
  pumpkin), San Marco six sharp ridges and a hairy rim at x = -0.3 (seen in `_look-brute-ribs.png`).
- **Airplane:** a thin spine with small bodies and spikes, much as the other two rules draw it (seen, whole view only).
- **Rabbit: fails as a body.** The cut at z = 0 is the flat rabbit, the cut at 120 degrees is the flat rabbit point
  for point and the cut at 60 degrees the flat rabbit turned over (0 of 129,600 points differ, measured). But off
  the planes the ears are gone: turned 1 / 4 / 8 / 15 / 30 degrees about the x-axis, 78 / 52 / 35 / 19 / 14 % of
  the flat set's points are still in the set (same at 40 and 80 steps; `thick.txt`). The basilica keeps 97 / 91 /
  88 / 88 / 91 %. The lab shows a feathery mass, a six-armed burst of blades seen along the x-axis, no bodies
  meeting at points. One plane (right-hand columns of the sheet) is the only one of the three with clean bodies.
- **Siegel disc: three sheets.** A quarter of a degree off its planes 79 % of the points are in the set at 40 steps
  and 64 % at 80; at 4 degrees 18 % and 9 %. It thins with the step count: no body. The lab shows feathers.
- **Dendrite:** the cut at 60 degrees is the flat tree; the lab shows a thin dust at 40 iterations.
- **Whole powers 2 to 5:** flat cut against plain complex arithmetic: 0 of 160,000 points differ in each of six
  Julia sets (`brute-powers.txt`). Count round the axis (strongest repeat of the outline of the cut across the
  x-axis, `thick.txt`): 6 at power 2 (c = -1), 6 at power 3 (c = 0.3; second strongest after 24), 10 at power 4
  (c = -1: ten buds, seen), 10 at power 5 (c = 0.3); for c off the axis 3 at power 3 (c = i) and 10 at power 4
  (c = 0.3 + 0.3i). So the count is 2k: it follows the power two powers at a time (2 and 3 share six).

## The lab's 2D view

`flatcmp.txt`: against Sphere inversions, one plane, same page and settings, 604,262 pixels: basilica 586 differ
(none by more than 8 of 255 levels), rabbit 4,015 (189 by more than 8), Siegel disc 5,415 (667), dendrite 2,442
(56). The differing pixels lie on the thin edges of the outline (`_look-flatdiff.png`, looked at). The flat sets
themselves are right. Not explained further (round 16 put the same effect down to the view shading a little to the
side of the plane; for this rule the set is thin there, which would make it stronger: reasoned, not tested).

## Checks on the final build

- `checks.txt` (numbers above), `card.txt` (every text at the powers 2, 3, 4, 5, 2.5, 1, 0.7, 0, -1, -2, -3: no
  "undefined", no "NaN", 0 bad parts; the page's scorecard in Julia mode at powers 2 and 3).
- Learn tab: the plan for `windsq` has 3 moves and its chain ends where MATH ends (3e-16). `65-learn-steps.js`
  not touched: the tab shows the generic moves, not the winding as a move of its own.
- `smoke.log`: `tools/smoke-v14.json`, 62 steps, plus 5 steps for the entry (chosen in Julia mode from the menu,
  picture whole, words on the page and in "About this approach", the cap at Rough holds, 2D view, powers 3, 4, 5
  and the rabbit, Reset everything): all pass, no console errors, exit 0, at 1400x950.

## Where each sentence of the entry comes from

- Rough / fog / ray step numbers: `measure-main.txt`, `measure-skin.txt`, `measure-step.txt`. "at 14 ... short necks": `look-bas-14.png`.
- flat cut, six half-planes, jump, mirrors, 120 degree turn, length, powers: `checks.txt`, `brute-powers.txt`.
- 2D view pixels: `flatcmp.txt`. Rabbit cuts at 60 and 120 degrees, bud size, specks, tear at power 2.5: `small.txt`.
- touching point, smooth at x = 0, needles at x = 0.2, spikes at x = -0.3, lobes and ridges: `brute-basilica.txt`,
  `brute-ribs.txt` and their pictures. Thickness numbers, count round the axis: `thick.txt`.
- stretch, crush, no fold: `stretch.txt`. "An even count would swap the halves", slope 1 and 2k - 1: read off the formula.
- "has not been judged yet": the only sentence about the Mandelbrot solid.

## Not done

- No panel2 run, no hair number: that is the section "check". I only say what the cuts show.
- The exact-band profiles (section "profiles") are not in the lab: the entry is the sinus profile, as briefed.
- The Learn tab does not show the winding as its own move.
- Powers 3 to 5 were measured (flat cut, half-planes, count, jump, stretch) but their 3D pictures were only
  smoke-tested for "not empty", not looked at closely.
- Negative and fractional powers: texts checked, tear measured at 2.5; no pictures.

## Risks

- The required smoke list (its step 11) chooses every entry in Mandelbrot mode and then in Julia mode, so the page
  did draw a Mandelbrot view of the new entry for a moment inside the headless browser. No picture of it was saved
  (the step's screenshot is taken in Julia mode, c = -1) and none was looked at or described. I opened no file in
  `out/r20/entry/smoke/`. `smoke.log` (step 12) holds one line of probe counts per entry and mode, the new entry
  in Mandelbrot mode among them: a count of hits, not a picture; I did not read it and it says nothing about shape.
- A published page lets the user switch this entry to Mandelbrot mode before that solid has been judged. The tag
  and the About text both end with "has not been judged yet".
- The user who opens the entry sees the Rough picture at ray step 0.8, which leaves out about a quarter of the
  rays on the rabbit. The note says so; a default ray step per entry would need `40-render.js`.
- The tag and the About text carry numbers from this round's measurements; if the profile is changed (section
  "profiles"), every number in `R20-TEXTS` has to be measured again (`put_texts.py` holds them in one place).
