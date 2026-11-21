# Round 19: one exact plane and angle-keeping pieces, judged on the Julia panel

Read this file, then `docs/ROUND18-PANEL.md` (the user's newest words and the panel), then `docs/ROUND17.md` (the
user's earlier words, the record, the house rules). The house rules of round 17 hold here unchanged: work only in
`out/r19/<your section>/`; rules go in `out/r19/<section>/myrules.py` with your prefix (the bench loads them: the
hook in `out/r16/bench/rules.py` reads `out/r17/*/myrules.py`, and the orchestrator has added `out/r19/*/` too);
never touch `src/`, `base*/`, `dist/`, `squaring-lab.html`, `notes/_state.md`, the bench's or the panel's .py
files, or another section's folder; nothing is published; plain words, numbers, and "measured / seen in the
picture / reasoned" on every statement. Sub-agents cannot write files named report.md: put your long notes in
`out/r19/<section>/NOTES.md` instead and in your returned report.

## The order of work (the user's, 2026-11-18)

A panel of Julia sets, all of which must pass; only then a Mandelbrot solid; only when that passes does anything
else continue. The user's word on the best rule so far: "the turning along approach is the closest we've gotten
so far, the basilica looks almost exactly as people envision, with bulbs growing between things in a natural
way, very nice." **No Mandelbrot solid of a new rule is drawn in this round by anyone.**

## Where things stand (rounds 17 and 18; reports in `notes/_r17_reports.json`, `notes/_r18_reports.json`)

- About fifty rules, no passer. No rule passes ANY panel set with c off the x-axis. `oneplane` is clean on every
  set with c in the flat plane (balls meeting at points for the rabbit, a thin tree for the dendrite) and fails
  only "truly 3D". `twoplane` passes the four sets on the x-axis and falls apart off it. `along` has hair close
  up on the basilica and is a layered lump off the axis.
- Checked independently (round 17 prover and hunter; proofs written out, not reviewed by a mathematician):
  - A tear-free rule that is exact on two mirror planes wraps the sphere of directions 0 or 4 times, never the 2
    of the flat rule: it folds (hair) or over-wraps (whiskers). Closed: the whole reference-plane family
    (`along`, `away` and 25 relatives), averages and great-circle blends of the two one-plane answers.
  - For c off the x-axis no second sheet, flat or curved, can carry a flat picture smoothly.
  - The one-plane rule is the ONLY rule that keeps angles on the sphere of directions and is exact on the flat
    plane. So every clean-skinned candidate is "the one-plane rule near the flat plane, plus something else
    further up", joined without a tear.
- Orchestrator's reasoning, to be used and tested: every rule here is F(v) = |v|^2 D(v/|v|). A body is carried
  to a round body only where D stretches the sphere of directions by exactly 2 (then all three stretches are
  2|v|). Where D stretches by less the bodies it makes are lenses and blades; by more, needles; where D crushes
  (stretch 0, unavoidable for any D that covers the sphere more than once) it makes pancakes of whatever sits
  on the line the crushed directions are sent to. Stretch exactly 2 cannot hold on a patch of directions (a
  sphere cannot be doubled onto itself), only along curves, and "near 2" on a patch is the best there is.
- Counting rule (round 17 blends, measured on 12 rules): buds grow where a direction is sent to -x, long arms
  where a direction is sent to +x. Tools, seconds each, no iteration: `out/r17/blends/count_dirs.py`,
  `turncount.py`, `screen.py` (wraps, share folded, share angle-keeping, largest stretch); the hunter's
  `out/r17/hunter/c2.py` and `core.py`.
- First tries of the open kind, all failed, each for a reason worth knowing:
  - **Fold after squaring** (`out/r17/me/myrules.py`, m_cap15..80: the one-plane answer, steep answers folded
    back by a sphere inversion that sends straight-up to straight-back): the skin between the planes is clean
    and carries small round bodies with no hair (`out/me/r16/closecut-m_cap15.png`), but the basilica fails J2,
    J4, J8: blades and lenses, and a thin sheet standing on every neck (`out/r16/bench/sheets/m_cap15.png`).
    Reason (reasoned): the one direction this fold sends to -x is straight up, which the one-plane rule has
    already crushed (stretch 0). The bud direction must be one that arrives with stretch near 2.
  - **Pole rules** (round 17 blends, b_pcd, b_pcc: smooth angle-keeping maps covering the sphere 4 or 6 times):
    clean skin (0.07, 0.14), fused lump, extra arms.
  - **rat4c** (round 17 profiles, `p_x_ratc15`, `p_x_ratc25`: an angle-keeping map covering 4 times, seen
    through a change of angle that makes the flat circle exact): no hair (0.01, 0.20), lens bodies, fins on a
    cone; its surplus is squeezed round one direction (largest stretch 380 to 3400).
  - **Fold before squaring** (not built; reasoned): if directions above a cone are mirrored below it and then
    squared, a point and its mirror point have the same answer, so the set above the cone is the mirror image
    of the set below: copies of the row of bodies stacked up the sky, joined along the crease wherever a body
    has width there. Point contacts only if the crease runs where the bodies are thin.

## What a rule must do in this round (the design target)

1. Exact on the flat plane, and the one-plane rule in a band round it (so bodies there are round and the skin
   clean). No tear anywhere (creases are allowed: answers must agree on both sides).
2. Off the flat plane, some directions are sent into the flat plane's bud directions (-x first) and arrive with
   stretch near 2, so that the buds they grow are round. Say which directions, and the stretch there.
3. The directions it crushes are sent where nothing happens (for the one-plane rule that is straight up and
   down). Say where they go.
4. Same above and below the flat plane. No count or size that is free: if a size is needed, fix it by a stated
   principle (for example "the stretch at the bud direction is exactly 2") and say so.
5. It must not need the x-axis: the rabbit and the dendrite have to stay clean and in one piece, as they do for
   `oneplane`, and should gain something off the flat plane.

## Gates, in this order (stop a rule at its first failure)

- Seconds: rule checks (length squared, flat plane exact, no jump at gaps 1e-4, 1e-5, 1e-6 AND the cliff at gap
  0.001, `out/r17/profiles/cliff.py`; both mirrors), then the direction screens above.
- One minute: `python out/me/r16/closecut.py <rule>` and LOOK at `out/me/r16/closecut-<rule>.png`. The hair
  number is known to be wrong in one way: it counts ordinary round buds as hair (the flat basilica itself
  scores 1.2 to 2.0). So the eye decides here: fins, combs, tufts, whiskers and films of loose dust fail; round
  buds with clean edges do not. Also cut at 45 degrees and at the rule's own mid angles.
- Two minutes: `python out/r16/bench/bench.py stage1 <rule>`. J2 (bodies part at the meeting point), J4, J5,
  J7 and J8 as they stand.
- Then the panel as a FILTER (`python out/r18/panel/panel.py run <rule>`, 10 to 25 minutes on one core; its
  README says what each line measures; its review `notes/_r18_reports.json` says what it cannot be trusted
  for): the rabbit and the dendrite first. A rule that breaks the rabbit into pieces, swells it into a lump or
  turns the dendrite into a lump or a bush is out.
- A rule that gets through all of that is a CLAIM, not a pass: the workflow hands it to an independent checker.

## foldpost (prefix `f_`): fold the one-plane ANSWER with sphere inversions

Start from `capfold` in `out/r17/me/myrules.py`. Choose the folding spheres so that the direction sent to -x is
not the crushed pole but a direction that arrives with stretch near 2 (the one-plane answer at latitude L' comes
from latitude L with stretch 2s(1 + s^2)/(1 + s^4), s = tan(45 degrees - L/2); the inversion multiplies it by
its own stretch at that point), and so that the crushed pole is sent somewhere harmless. Work out where every
flat bud direction's extra copies sit and with what stretch, before iterating anything. Try one fold and two.

## foldpre (prefix `g_`): fold the DIRECTION first, then square; and mixtures

Mirror directions above a cone (a sphere inversion that keeps the unit sphere, or another angle-keeping fold)
back toward the flat plane, then apply the one-plane rule. Test the reasoning above (stacked copies joined along
the crease), then look for creases that run where the basilica's bodies are thin so that copies meet at points,
and for folds that are not symmetric about the upright axis. Mixtures of a fold before and a fold after are
yours too.

## rational (prefix `q_`): smooth angle-keeping surplus, done properly

Continue the round-17 scouts `rat4c` (in `out/r17/profiles/myrules.py`) and the pole rules (in
`out/r17/blends/myrules.py`): an angle-keeping map of the sphere of directions that covers it 3, 4 or 6 times,
made exact on the flat circle by a change of angle. What round 17 left undone: choose the map so that the extra
directions sent to -x arrive with stretch near 2 and the crushed directions go to the poles; carry the change of
angle off the flat circle smoothly (round 17 carried it along meridians, which crumpled the skin); make the
angle table accurate enough that the jump test passes. Its makers' own caveat stands: on the flat plane this
kind's sideways stretch is not exactly 2, so check that the flat plane's own buds stay round.

## panel2 (in `out/r19/panel2/`): make the panel fit to certify a pass

Copy `out/r18/panel/` and fix what its review found (read both reports in `notes/_r18_reports.json` and
`out/r18/panel/README.md`; pictures in `out/r18/review/`):

1. The hair number must pass the flat set itself and still fail `along`'s fin combs, `away`'s whiskers and
   p_tt1024's film of dust. Count thin fins, needles and loose dust; do not count round buds. Check it on the
   flat basilica, flat San Marco and flat airplane (the one-plane rule cut at 0 degrees), which must score clean.
2. Look in enough places: at least 8 half-planes (including 45 degrees and the rule's own mid angles) and 5 skin
   points; say how the verdict moves with the choice.
3. Add "the solid stays": volume at 80 steps at least 90 % of the volume at 40.
4. Group C is wrong as it stands: rabbit turned 30 degrees is, for every rule but the lathe, a c whose solid
   drains away to nothing, as it must for a c outside that rule's own Mandelbrot solid. (The lab draws a lump
   there because its flat view paints every pixel within one pixel of the set, so a fine dust looks filled:
   read in the shader, `src/js/30-shaders.js` lines 640 to 660; do not report this as a lab fault without
   checking.) Replace group C by sets that test the first step off the x-axis and off the flat plane, chosen so
   that the comparison is fair: the basilica and San Marco nudged off both planes (for example
   c = (-1, 0.05, 0.03) and (-1, 0.03, 0.05)), and the rabbit lifted a little out of the flat plane; and for
   each rule say first whether the orbit of 0 stays bounded for that c (one orbit, not a picture), since a c
   outside the rule's own bounded region should be dust and is then not a failure of the Julia set.
5. Count the airplane's spikes and the cauliflower's dimples from point-by-point cuts across the x-axis; fix or
   drop San Marco's "bodies" line (it passes everything) and the Siegel disc's lump line (it passes a terraced
   lump).
6. Re-run the five calibration rules and the round-17 rules already run, print the old and new table side by
   side, and write `out/r19/panel2/README.md`.

Time for every section: aim for 75 minutes, stop at 95.

## check (run by the workflow only if a searcher claims a rule gets through every gate)

You did not design the rule. Try to fail it: re-run the gates yourself; cut its skin at 120 tiles; look at its
basilica, rabbit and dendrite from several sides and close up, point by point; run panel2 if it exists, else
the round-18 panel; look for the thing its maker did not look at. Say plainly whether it stands.
