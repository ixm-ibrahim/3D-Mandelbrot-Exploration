# Round 20: "wind, then square": extra planes that borrow the flat plane's arithmetic

Read this file, then `docs/ROUND19.md` (the gates, the design target, what round 19 was), `docs/ROUND18-PANEL.md`
(the user's newest words and the Julia panel) and `docs/ROUND17.md` (the user's earlier words, the record, the
house rules). The house rules of round 17 hold unchanged: work only in `out/r20/<your section>/`; rules go in
`out/r20/<section>/myrules.py` with your prefix (the bench hook in `out/r16/bench/rules.py` now loads
`out/r20/*/myrules.py` too); never touch `base*/`, `dist/` (except the one build named below),
`squaring-lab.html`, `notes/_state.md`, the bench's or the panels' .py files, or another section's folder; only
the section `entry` touches `src/`; nothing is published; plain words, numbers, and "measured / seen in the
picture / reasoned" on every statement. Sub-agents cannot write files named report.md: put long notes in
`out/r20/<section>/NOTES.md` and in your returned report.

## The order of work (the user's, 2026-11-18)

A panel of Julia sets, all of which must pass; only then a Mandelbrot solid; only when that passes does anything
else continue. On the best rule before this round: "the turning along approach is the closest we've gotten so
far, the basilica looks almost exactly as people envision, with bulbs growing between things in a natural way,
very nice." **No Mandelbrot solid of the new rule is drawn or judged in this round by anyone.** (The lab draws a
Mandelbrot view for every entry; the section `entry` must not look at it or describe it.)

The user's own tests for "the right rule" (2026-11-18): the cut at z = 0 is exactly the flat set; the number of
bulbs follows from the power and never from a "number of planes" dial; no disconnected shards, no wrong slice, no
flat set simply spun round the x-axis (rings); the picture of right is a body with smaller round bodies on it in
more than one direction; a principled carry-over of what the flat rule does.

## Where round 19 ended (reports: `notes/_r19_reports.json`, text `out/me/r16/reports19.txt`)

No rule passed. Three kinds are closed, each with a measured reason:

- **Fold after squaring** (`out/r19/foldpost/`): one fold copies every flat direction, the long-arm direction
  too; a pleat's copies cannot be round off the flat plane (stretch 2.4 at 5 degrees up, 3.6 at 15).
- **Fold before squaring** (`out/r19/foldpre/`): a copy made by a mirror in a circle is always thinner than what
  it copies (stretch above 2); creases are fixed in space and cut the rabbit's big bodies. `g_pl` passes all
  eight bench lines on the basilica and still fails the rabbit (a lump) and the dendrite (in pieces).
- **Smooth angle-keeping surplus** (`out/r19/rational/`): a count closes it (round on average needs 4 covers,
  the half turn allows 2 or 6; 6 gives a rock or spears).
- The "thin sheet on the necks" of every pole fold is a film of no thickness in the upright plane y = 0
  (`out/r19/foldpre/neckline.py` tells a film from a real sheet in seconds).
- **panel2** (`out/r19/panel2/`, README there): the Julia panel repaired. A hair number that passes the flat
  sets and fails `along`'s fin combs; 120 skin tiles a set; "the solid stays"; four nudged sets in place of the
  turned rabbits, judged only where the orbit of 0 stays bounded. No rule passes it. Two holes it still has: a
  saw-toothed skin is not counted, and a ball that turns into a dome on a nudged set passes "bodies".

Orchestrator's reading of why everything broke off the x-axis (reasoned, from claim C1 of round 17): every
many-plane rule so far (two planes, `along`, `away`, their 25 relatives) gives each of its planes ITS OWN
arithmetic: a point of the upright plane is squared inside the upright plane. For c on the x-axis that fits
together. For any other c the upright plane sees c as a big push out of itself, its part of the solid no longer
matches the flat part, and the result is shards (a tear) or a lump (a smooth join). C1 says no second sheet can
be KEPT by the rule for c off the axis. It says nothing about a sheet that is not kept.

## The new rule (orchestrator's, `out/r19/me/myrules.py`, bench names `m_w3`, `m_w3lin`, `m_w3f`, `m_w5`)

**Wind, then square.** The other planes get no arithmetic of their own. A point's turn round the x-axis is first
multiplied (wound) by a whole odd number k, and then the one-plane rule P is applied. Nothing is turned back.

    F(v) = P(T(v)),   T: (x, rho, a) -> (x, rho, g(a))
    a = the turn of v round the x-axis, 0 on the side y > 0 of the flat plane; rho = its distance from the x-axis
    g(a) = k a - (k - 1) sin(2 k a) / (2 k)       slope k - (k - 1) cos(2 k a): 1 at the copy planes, 2k - 1 half way

k = 3 is `m_w3`. The half-planes at a = 60, 120, 240, 300 degrees are sent INTO the flat plane by T, and from
there on the point lives in the flat plane, where c lives. So those planes carry copies of the flat picture
without being kept by the rule.

Measured so far (orchestrator; `out/r19/me/check.py rules`, `check.py cuts m_w3`, bench stage 1):

- Length squared to 1e-14; flat plane exact to 1e-14; for a point of the plane at 60 degrees the answer lies in
  the flat plane and is the flat square of the point turned there, to 2e-14; no jump (move/gap steady at about
  32 from gap 1e-3 to 1e-6; bench J6: largest jump 1.3e-8 over a gap of 1e-9).
- `out/r19/me/cuts-m_w3.png`, point by point at 60 steps: the cut in the plane at 60 degrees is the exact flat
  picture for the basilica, the **rabbit**, the **dendrite** and the **Siegel disc** (seen). No lump anywhere
  (seen). Cut across the x-axis the rabbit is a six-pointed body with matter in six directions.
- Bench stage 1 on the basilica (`out/r16/bench/sheets/m_w3.png`): J1 to J7 pass (18 buds on the middle body,
  12 off the flat plane, all 12 round; on one bud 23 smaller ones, 14 round; 0 rings; a ball of 0.02 parts the
  bodies; nothing on the upright line through the neck). J8 FAILS: roundness 0.68, 0.50, 0.67, ribs on the
  outline 0.18, 2.10, 1.56 % of the radius (ribbed like a walnut, seen in close-up 2). 1160 voxel pieces when
  no gap is allowed (99.16 % in the biggest), 1 piece with a one-voxel gap.
- Weak spots seen in the cuts: (1) the Siegel disc is paper-thin: its cuts across the x-axis are thin lines, a
  six-armed star of sheets, not a body; (2) half way between the planes (30 and 90 degrees) the rabbit shows
  thin arcs and specks round the middle body, and the basilica cut across at x = -0.3 shows a dozen short thin
  spikes; (3) the ribs above.
- The whole panel2 run on `m_w3` was started by the orchestrator (`out/r19/me/logs/panel2-m_w3.log`; numbers
  land in `out/r19/panel2/results/`); it may still be running when you start. Do not start a second full run of
  `m_w3`; use its numbers and tiles when they are there.

Orchestrator's claims about this rule, to be attacked (reasoned unless marked):

- **W1.** For every c in the flat plane, on the x-axis or not, the solid's cut by the plane at 60 degrees and by
  the plane at 120 degrees is the flat picture, turned (measured on four sets, reasoned in general: a point of
  those half-planes is in the flat plane after one step).
- **W2.** k must be odd: an even k sends the half y < 0 of the flat plane onto the half y > 0, and the cut at
  z = 0 is then not the flat set. k = 1 is the one-plane rule. So k = 3 is the smallest new one, and for power 2
  it is not a free dial.
- **W3.** F does not change when a point is turned by 120 degrees about the x-axis, so every Julia set of this
  rule, for every c, has that three-fold symmetry (as every flat Julia set has its half turn). The Mandelbrot
  solid does not inherit it.
- **W4.** The rule folds nothing (g rises all the way). It crushes only directions that are sent straight up or
  down: the six directions at right angles to the x-axis half way between the planes. The six directions sent
  to -x (bud directions) arrive with stretch exactly 2, the same in all directions. Only +x and -x are sent to
  +x (no extra arms), each wound three times.
- **W5.** A bud whose centre lies in one of the three planes is as round as its flat twin, at every depth. A
  bud between the planes is squeezed thin in the direction round the x-axis by the slope of g there (up to 5),
  and its own buds by more: between the planes the bodies get thinner with depth without limit. So fins
  between the planes cannot be removed in this kind of rule, only made smaller or fewer.
- **W6.** Wherever g(a) is further from the flat plane than a itself (everywhere, for the sinus profile), a
  body that neither attracts nor repels across the flat plane (the Siegel disc) collapses to a sheet. A profile
  with g(a) = a exactly in a band round the flat plane (and slope exactly 1 in a band round each copy plane)
  would give it the one-plane rule's thickness.

## Sections

### entry (the only section that may touch `src/`): the lab entry

Add the rule to the lab as ITS OWN entry (the user's rule: every variant is its own entry, never a dial of
another), id `windsq`, name "Wind, then square", group `inversions`, placed after `turnalong` at the end of the
list. Follow the pattern of the two round-16 entries in `src/js/10-approaches.js` (`tpPower`, `glTurning`,
`TP_*` texts, the entries `turnaway` and `turnalong`; `out/me/v16/patch.py` shows how the last change was
joined). For the power n: m = the whole number nearest to |n| (at least 1); k = m if m is odd, m + 1 if m is
even ("wound as many times as the power, and once more when that would be even, because an even count swaps the
two halves of the flat plane"); P is the one-plane power n already in the file. Decide `deMax` the way round 16
did: compare the lab's three distance estimates with point-by-point cuts and keep the finest one that draws
nothing that is not there. Every sentence of the entry's texts (tag, note, formula, about, round note, crush,
smooth, slice) must be something you measured or can read off the formula; write them in the plain style of
the neighbouring entries; say the weak spots as plainly as the strong ones; say nothing about the Mandelbrot
solid except that it has not been judged yet. Check whole powers 2 to 5 for the flat cut and for the count
round the axis.

Build with `python build.py --name r20-entry --base base16a --use src/js/10-approaches.js` (add other src files
only if you changed them, and say so) into `dist/r20-entry.html`. Do NOT run `--page`, do not publish. Test with
`tools/shot.py` (headless Chrome on the real GPU: ONE run at a time on this machine, `PYTHONIOENCODING=utf-8`):
the smoke list `tools/smoke-v14.json` must still pass on your build with no console errors, plus steps for the
new entry. Then make `out/r20/entry/sheet-for-user.png` from the lab itself: the seven flat-plane panel sets
(basilica, San Marco, airplane, cauliflower, rabbit, dendrite, Siegel disc) as Julia sets at 40 iterations or
more, for `windsq`, `turnalong` and `mercator` side by side from the same camera, plain labels; and
`out/r20/entry/close.png`: the basilica and the rabbit of `windsq` close up from two sides. Look at them and say
what you see. `out/me/panel/shots.py` and `sheet.py` show how the orchestrator drove the lab for such a sheet.

### profiles (prefix `w_`, Python only): the best form of the rule

The sinus profile is the smoothest g with slope 1 at the copy planes; it is not the only one. Find the form
that looks best on the panel, by pictures, and say why:

1. Exact bands: g(a) = a exactly within w degrees of the flat plane and slope exactly 1 within w degrees of
   each copy plane, joined by a smooth ramp; w = 5, 10, 15, 20. Does the Siegel disc get a body (W6)? Do the
   ribs go (J8)? What happens to the fins and to the rabbit's thin arcs as the ramp steepens?
2. The fins between the planes: how big are they beside the buds, at which depth do they show, with which
   profile are they least visible at the scale a person looks at (whole set, one bud, one bud's bud)?
3. k = 5 (`m_w5`), and the plain winding `m_w3lin` as the known bad end (every bud a thin plate, by W5).
4. No free size: if a band width or a ramp shape is needed, fix it by a stated principle and say so.
5. Gate each member by: rule checks, `out/r19/me/check.py cuts <rule>` (or your own), bench stage 1, then the
   rabbit, the dendrite and the Siegel disc with panel2's tools. Recommend ONE form.

### prover: are W1 to W6 right, and what do they leave out?

Prove or break each of W1 to W6 (W1 to W4 can be settled exactly; W5 and W6 need care). Say exactly what C1 of
round 17 forbids and why this rule is not forbidden. Is there any way to have TWO planes (k = 2, or a winding
with one fold) and keep the flat cut exact? Is there a member of this kind whose between-plane bodies do not
thin with depth, or a proof that there is none? What is the right k for a whole power n, by a principle and not
by taste (the user's test: the count must follow from the power)? One count to check: round bodies on average
need the sphere of directions covered n squared times; P covers it n times and T covers it k times. Stay with
Julia sets: nothing about the Mandelbrot solid beyond one sentence on its symmetry.

### check: try to fail `m_w3` on the panel

You did not design the rule and should not trust the orchestrator's first look. Use panel2 (`out/r19/panel2/`,
README first) and your own eyes: the numbers of the orchestrator's run when they are there; skin tiles at the
rule's own mid angles (`wide.py m_w3:<set>:30,90`); the worst tiles of every set; the four nudged sets (what
does a c lifted out of the flat plane do to three planes that all feed the flat plane?); several step counts;
the Siegel sheet; the 1160 pieces; anything its maker did not look at. For each of the eleven sets say pass or
fail, by which line, and what a person would SEE at the scale of the whole set and at one bud. Put `m_w3`
beside `along`, `twoplane` and `oneplane` in one sheet, `out/r20/check/sheet.png`, plain labels, readable by
the user. Say plainly whether the rule is better than `along` on the panel, and where it is worse.

Time for every section: aim for 75 minutes, stop at 95.
