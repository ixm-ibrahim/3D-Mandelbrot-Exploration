# Round 23, section outside2: what does mathematics say?

Folder: `out/r23/outside2/`. Marks: measured / seen / reasoned / theorem (cited in `references.md`).

## What was done

1. Web search and reading (2026-11-19). 21 sources in `references.md`, each marked by how much of it I read. Four
   papers were read as text (pdfminer on the downloaded PDFs): Cabrera-Makienko-Sienra, Fletcher-Nicks, Tengvall,
   Zimmermann-Bruckner; Fletcher-Macclure through ar5iv. The rest: abstracts or search excerpts, and said so.
2. `check1.py` (log `check1.log`): numbers behind the verdicts on section 2 (a) to (f).
3. `de.py` (logs `de-table.log`, `de-check.log`, `de-cuts.log`, `de-solids.log`; table `de_table.npz`): the
   Douady-Earle extension of z^2 built as a rule of the library and tested beside one plane.
4. `verdicts.md`: each of 2 (a) to (f) as theorem / wrong / open, the user's quaternion guess, and a straight answer.
5. `constructions.md`: three constructions not yet tried, as formulas. K1 built; K2, K3 not built.

## The five findings that matter

1. **The lab's one-plane rule is in the literature, exactly** (measured, 7e-15 over 200,000 points). It is the
   "product extension" of z^2 in Cabrera, Makienko, Sienra (2015), section 4.1, and it is v * v for a multiplication of
   space points that restricts to the complex product: lengths multiply, longitudes add, Mercator latitudes add
   (measured, 1e-14). They draw its Julia sets cut by the upright half-plane for five real c. A second canonical
   extension, Douady-Earle (Petersen 2011), was built here: same length |v|^2, direction within 1.21 degrees of one
   plane, latitude monotone, hinge-free (measured). Pictures look the same (seen: `de-cuts.png`, `de-solids-a.png`,
   `de-solids-top.png`: clean separate blown-up bodies for c = -1 and the rabbit, buds round the flat picture only).
2. **Section 2 (b) is wrong as written**: it leaves out the fold. A hinge-free, tear-free rule with no crushed cone
   CAN hold copies of the flat picture off the flat plane, for the rabbit too (measured counterexample "fold30":
   turn test 2e-14, flat check 0 of 20,000, the 45-degree cone holds the rabbit exactly, 0 of 40,000 differ, 93 % of it
   survives half a degree off the cone). The corrected statement (no tear, no fold, no crushed cone => nothing off the
   flat picture) is a two-line theorem. Under hinge-freeness every copy cone is wound twice (measured 2.00), stretch
   2 / cos L (2.83 at 45 degrees), so it never keeps shapes.
3. **Section 2 (c) is right, but its cone is not hinge-free**: a cone laid once round reverses the longitude, which
   allows only a threefold symmetry (theorem; measured: the cone rule passes the turn test at 120 degrees only). Two more
   theorems: the zone between the flat plane and the cone cannot be angle-true (identity theorem), and it must hold
   exactly 3 branch directions per side (Riemann-Hurwitz; measured for R_t: latitude +-32.96, sent to latitude +-15.83).
4. **Counting theorems that fence the whole search.** Two coverings and no fold: no point off the flat plane is ever
   sent into it, so no body off the flat picture (theorem). Buds off it need 4 (or 6) coverings or a fold. A second
   plane holding a true copy exists only for c on the x-axis (theorem), which is what "two planes" and "along" live on.
   An evenly spaced doubling pattern over a whole ball-like body is impossible without special points: 4 corners
   (the pillow) or a doughnut (theorem, Euler characteristic).
5. **Nothing published draws a 3D z^2 + c with buds all over.** The literature's 3D squares are: the one-plane rule
   (exact), its Douady-Earle twin, and Mayer's power map (the lab's square pillow, covers 4 times, bounded squeeze).
   "Power map + c" in R^3 has a theorem that its escape boundary is a bounded perfect set if 4 > K_I (Fletcher-Nicks),
   and no pictures. Quaternion squares spin the flat set (theorem); the Hopf-angle power map is 4D with Mandelbulb cuts.

## Numbers (all measured; scripts named)

`check1.py`:
- A: one plane against the published formula 7.1e-15; against "lengths multiply, longitudes and Mercator latitudes add" 1.1e-14.
- B: rabbit meeting point alpha = -0.2763 + 0.4797i. Height factor after one step, at heights 0.01 / 0.075 / 0.15:
  one plane 1.107 / 1.098 / 1.074; along 1.105 / 0.997 / 0.735; two planes 1.107 / 1.098 / 1.074. Along's square of
  (alpha, 0.075) is (-0.152, -0.262, 0.075): the y sign flips.
- C: turn test, largest |F(R_a v) - R_2a F(v)| for a = 37, 90, 120, 180 degrees: one plane 7e-15, 5e-15, 7e-15, 4e-15;
  fold30 2e-14, 1e-14, 2e-14, 1e-14; cone+ and R_t alone pass only at 120 (1.7e-14, 1.8e-14; elsewhere 24 to 42);
  lathe, two planes, along fail everywhere (14 to 41). fold30: flat check 0 / 0 / 0 / 0 of 20,000; cone copy of the
  rabbit 0 of 40,000 differ (6,361 inside); of those 5,937 stay at latitude 45 +- 0.5, 5,298 at +- 2, 4,375 at +- 5.
- D: one plane: ray stretch / 2|v| = 1.000000; the other two stretches (divided by |v|) 1.996..2.000 at latitude 0..2,
  1.326..1.447 at 28..32, 0.529..0.616 at 58..62, 0.009..0.086 at 85..90. R_t branch directions: |w| = 1.8402 and
  0.5434, latitude +-32.96, longitudes 0 and +-120, sent to latitude +-15.83 at longitudes 0 and -+120.
- E: one plane, largest / smallest stretch at latitude 0, 30, 60, 80, 89, 89.9: 1.0, 1.4, 3.5, 11.3, 115, 1146.

`de.py`:
- table: latitude of the square at latitude 7.5, 15, 30, 45, 60, 75: Douady-Earle 14.93, 29.36, 54.22, 71.66, 82.43,
  88.19; one plane 14.87, 29.02, 53.13, 70.53, 81.79, 88.01. Largest difference 1.213 degrees. Length 1.0000.
  Increasing all the way: yes. Residual of the balance equation under 1e-13 (200,000 directions).
- check: flat check 0 / 0 / 0 / 0 of 20,000, strays 0; all finite; turn test 7.1e-15; lift test 3441 of 3443 (basilica),
  3195 of 3195 (rabbit), the same as one plane. Inside share of the box, Douady-Earle against one plane: basilica
  0.0290 / 0.0297, rabbit 0.0179 / 0.0188, c = -0.75 0.0587 / 0.0640; tallest point 0.501 / 0.505, 0.379 / 0.384,
  0.617 / 0.644. Stretches at latitude 30: 2.000, 1.417, 1.350 (not angle-true on the sphere of directions, unlike
  one plane); ratio 3.8 at 60, 12.5 at 80, 126 at 89; determinant positive at every latitude tried.

## Pictures (all opened and looked at)

- `de-cuts.png`: flat cut and upright cut through the x-axis, 60 steps, for c = -1, the rabbit, c = -0.75; top row one
  plane, bottom row Douady-Earle. Seen: flat cuts identical; upright cuts of c = -1 the same row of smooth lens bodies
  touching at points, no buds; rabbit upright cut one oval in both; c = -0.75 upright cut joined in both, the waists
  deeper in the Douady-Earle row. (The upright cut is a mirror plane of both rules; no off-mirror cut was made.)
- `de-solids-a.png`, `de-solids-top.png`: rough solids, 30 steps, 300 x 225 x 170 blocks, eyes (0.45, 0.5, 1) and
  (0.2, 1, 0.35). Seen: for c = -1 and the rabbit both rules give the same separate rounded bodies meeting at points,
  small buds round the rim where the flat picture has them, nothing above or below. I cannot tell the two rules apart
  by eye at this size. (30 steps only; no 80-step comparison was made.)

## What failed or was not done

- Three PDFs could not be read by the fetch tool directly; they were read after local text extraction. The AMS page of
  Kangaslampi-Peltonen-Wu refused the fetch (403): cited from the search excerpt only. Mayer 1997, Petersen 2011,
  Martin 2004, Martin-Mayer 2003, Milnor, Pilgrim-Tan Lei: abstract or excerpt only, marked in `references.md`.
- No paper citing Kučera's Bridges paper with a continuation of its 3D construction was found (one search; not exhaustive).
- K2 (arc blow-up) and K3 (doughnut doubling) are formulas only. K3 fails the user's first test by reasoning, not by a run.
- Two reasoned statements in `verdicts.md` have no computation behind them: the "at least 6 coverings" count for two
  exact mirror planes without folds, and the claim that every straight line of the pillow through the fixed direction
  is kept by the pillow map. Treat them as reasoned.
- The squeeze K_I of the lab's pillow was not measured, so whether Fletcher-Nicks' theorem (needs 4 > K_I) applies to
  "pillow + c" is open.
- The Douady-Earle rule was not tested at 80 steps, on the Siegel disc or the dendrite, or on off-mirror cuts. It is
  so close to one plane that I did not spend the time.

## For `design` and the orchestrator

- Do not present the one-plane rule as home-made: it is the published square of a published multiplication of space points.
- Section 2 (b) needs the word "fold" added before it is told to anyone. The folds of round 17 / 22 are the hinge-free
  road with copies off the flat plane; they are wound twice and cannot keep shapes there.
- The cone rule should be described as "three special upright half-planes", not "hinge-free".
- If one more thing is built: K2 in `constructions.md` (one plane with an arc blown up), because it adds coverings
  without a blend near the flat plane and with only two new branch directions per side whose images are chosen.
- The honest answer to "can two planes and along be ironed into one rule for every c": by the same means, no (theorem:
  no second true plane off the x-axis). By other means it is open, and the fold-free roads are fenced as in `verdicts.md`.
