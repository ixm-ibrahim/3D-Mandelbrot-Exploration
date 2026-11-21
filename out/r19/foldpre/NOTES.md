# Round 19, foldpre: fold the direction first, then square

Rules are in `myrules.py` (prefix `g_`), the direction screen is `dirs.py`, pictures are made by `stack.py`.
Every statement is marked (measured), (seen in the picture) or (reasoned).

## 0. What the one-plane rule is, in one line (reasoned, then measured in section 2)

Put the sphere of directions on a flat sheet in the angle-true way (north pole = straight up at the centre of
the sheet, the flat plane = the unit circle, straight down = infinitely far out). On that sheet the one-plane
rule is simply "square the number": w -> w^2. A latitude with sheet radius s goes to sheet radius s^2; the
sideways stretch is 2s(1 + s^2)/(1 + s^4): 2 on the flat plane, less off it, 0 at straight up and down.

A fold before squaring is: a mirror in a circle on the sphere of directions (the crease), used on one side of
the circle (the cap); outside the cap nothing changes. Then square.

## 1. Predictions, written BEFORE any rule was iterated (all reasoned)

P1. **The cap holds a mirror picture of everything outside it.** A point in the cap and its mirror point have
    the same answer, so they are inside or outside together. The mirror moves the direction and keeps the
    distance from the centre. So above the crease the solid is the mirror picture of what is below.

P2. **The copy can not be left out.** Whatever angle-keeping fold is used (circle or not), every direction
    outside the cap has at least one mirror direction inside the cap (counting argument: the folded map is the
    identity outside the cap and mirror-reversed inside, so it covers each outside direction once more inside).
    So each cap holds a copy of the WHOLE row of bodies, the two long arms of the basilica included. With one
    cap above and one below: at least 4 extra long arms, 4 extra copies of the two big buds. No fold of this
    kind has "buds only": it always has extra arms.

P3. **The copies are never round.** The mirror shrinks angles by a factor lam >= 1 (cap to outside it
    stretches by lam), and lam = 1 only ON the crease. The copy keeps its length along the ray from the centre
    and is lam times thinner across: a spindle pointing at the centre. Formula for a cap of angular radius a,
    for the copy of a direction at angle b from the cap's centre (s = tan(b/2), s0 = tan(a/2)):
        lam = (s^2 + s0^4) / (s0^2 (1 + s^2)),   near the crease lam = 1 + (angle between a body and its copy) x cot(a).
    Total stretch at a direction sent to -x: 2 lam, always more than 2 (needles, never lenses).
    Round copies need a cap that is nearly a half sphere (cot a = 0), and a half sphere that leaves the flat
    plane alone is the plane itself.

P4. **Round or separate, not both.** For caps round the poles with the crease at latitude L:
    copy of the flat plane at latitude L1, lam on it:
        L = 12:   L1 = 23.7,  lam = 1.09   (nearly round, but the big side bodies, about 20 degrees tall as seen
                                            from the centre, cross the crease: each is fused to its two copies)
        L = 22:   L1 = 42.2,  lam = 1.31   (side bodies just clear the crease: three bodies kissing in a fan)
        L = 24.5: L1 = 45.0,  lam = 1.41   (the one size with a principle: the copy lies half-way to the pole)
        L = 30:   L1 = 53.1,  lam = 1.67
        L = 45:   L1 = 70.5,  lam = 3.00   (thin spindles)
P5. **The middle body gets a groove along every crease** (its outline is mirrored there, so it has a kink
    unless the outline happens to meet the crease square on), and a second "equator" at latitude L1.

P6. **Leaning caps make it worse, not better.** A cap that leans over the bud direction +y so as to stay away
    from the long arms must be small (radius 35 degrees, centre at latitude 45): lam at the copy of the +y bud
    1.56, at the copies of the long arms 5.1: thin needles 11 degrees from the cap's centre. Two crossed caps
    (radius 48.3, centres at latitude 58.3 over +y and -y, crossing at right angles over +-x) put THREE copies
    of each arm into each side, lam 2.6 and more.

P7. **Kaleidoscope (the two creases as facing mirrors)**: copies of the band stacked all the way to the pole,
    each smaller than the last; the fold has no limit at the pole itself, so the rule tears at the upright
    axis (one line), which the jump test should find.

P8. **Crushed directions**: the mirror points of straight down (inside the upper cap) and of straight up; for
    caps round the poles these are the poles again. They are sent straight up or down. Harmless (target 3 met).

P9. **Verdict predicted for every rule here**: target 1 met (exact flat plane, one-plane band, no tear), target
    3 met, target 5 partly (rabbit and dendrite stay one piece, joined through the centre), target 2 NOT met
    (stretch at the new bud directions is 2 lam > 2, and extra long arms come with them), target 4 only with
    the "half-way" principle. Bench: J1 pass; J2 pass for creases above 20 degrees; J4 and J8 fail (spindles,
    fused triples).

## 2. What was measured in seconds, no iteration (`dirs.py`, logs in `logs/dirs-*.log`)

Every rule here: length squared to 1e-13, flat plane exact to 1e-14, mirrors above/below and front/back exact,
angles kept on 100 % of directions (measured). Jump over a gap of 1e-3, 1e-4, 1e-5, 1e-6 = (largest stretch) x gap
for all but the kaleidoscopes: creases, no tear, no cliff (measured).

| rule | what it is | directions sent to -x (buds): latitude, stretch | sent to +x (long arms) | covers sphere | largest stretch |
|---|---|---|---|---|---|
| oneplane | yardstick | 2: flat plane, 2.00 | 2 | +2.00 | 2.0 |
| g_p12 | caps round the poles, crease 12 | 2 flat + 4 at 23.5, 2.18 | 2 + 4 at 23.5 (2.18) | -2.00 | 2.2 |
| g_p22 | crease 22 | 2 + 4 at 41.1, 2.65 | 2 + 4 | -1.99 | 2.8 |
| g_p245 | crease 24.47 (copy at 45) | 2 + 4 at 45.0, 2.83 | 2 + 4 | -1.99 | 3.0 |
| g_p30 | crease 30 | 2 + 4 at 53.1, 3.33 | 2 + 4 | -2.00 | 3.6 |
| g_p45 | crease 45 | 2 + 4 at 70.5, 6.00 | 2 + 4 | -2.00 | 6.8 |
| g_k12, g_k245 | the two creases as facing mirrors | copies at 23.5, 43.5, 58.5, 69 ... (2.18, 2.76, 3.83, 5.59 ...) | the same list | +18 (no meaning: tear) | 4856 |
| g_t35 | 4 small leaning caps | 2 + 4 at 18.0, 3.12 | 2 + 8 needles at 43.9, 10.2 | -5.99 | 17.6 |
| g_d48 | 2 crossed caps a side | 2 + 4 at 19.2 (2.70) + 4 at 71 to 76 (7.8, 8.5) | 2 + 8 at 51.9 (5.24) + 4 at 76 (8.5) | -1.99 | 9.6 |
| g_pl | 4 pleats (12, 90 / 27.9, 69.55) | 2 + 4 at 21.5 (3.16, mirror) + 4 at 32.8 (5.27, same hand) | **2 only** | **+2.01** | 5.6 |
| g_pt | 4 pleats through the pole (12 / 27.9) | 2 + 4 at 21.5 (3.16) + 4 at 33.3 (4.43) | **2 only** | **+2.00** | 4.4 |
| g_pt8 | the same, lower (8 / 19) | 2 + 4 at 14.9 (2.69) + 4 at 22.7 (3.26) | **2 only** | **+1.99** | 3.3 |
| g_mix | g_p245 and then the round-17 fold after | as g_p245 plus the two poles (stretch 0) | 2 + 4 | +2.02 | 17.9 |

(The search by random directions sometimes lists a symmetric partner twice or misses one; the counts above are
completed by the mirrors, which are exact.) Crushed directions: always the poles or their mirror points, sent
straight up or down (measured). Target 3 is met by every rule here.

Predictions against this: P3, P4, P6, P7, P8 held to the digit (23.5 / 2.18, 45.0 / 2.83, 53.1 / 3.33, 70.5 / 6.00,
needles at 43.9 with stretch 10.2, kaleidoscope jump / gap 493 to 2126 = a tear at the upright axis).
**P2 was wrong as written.** With one crease per cap: yes, a full copy of the row with its arms (6 directions
sent to +x). But a SECOND crease inside the cap (a pleat) turns the inner part back to the same hand, the counts
cancel, and the cap then shows only a disc of the world round the bud direction: g_pl, g_pt, g_pt8 send only +x
and -x to +x, and cover the sphere +2.00 times, the flat rule's own number (measured).

For pleats whose creases both pass through the pole there is a one-line formula (reasoned, then measured to
three digits): a copy that sits at latitude L above the bud direction arrives with stretch
1 + tan^2(45 + L/2): 2.2 at 5 degrees, 2.7 at 15, 3.2 at 21.5, 4.4 at 33. Round (within 10 %) only below 5 degrees,
where the copy would lie inside the bud it copies.

Two more facts found on the way:
- A fold BEFORE with caps round the poles at latitude L is the very same rule as a fold AFTER with caps round the
  poles at the copy latitude L1 (12 -> 23.49, 24.47 -> 45, 30 -> 53.13): largest difference on 400,000 points
  6e-14 (measured, `logs/same-as-post.log`). So g_p<L> are also members of foldpost's family (pole-centred,
  straight up sent straight down). Leaning caps and pleats are NOT fold-after rules (reasoned).
- Given the one-plane rule on one side of a crease circle, the angle-keeping rule on the other side is forced:
  mirror in that circle, then square (reasoned). So a fold-before rule IS its set of crease circles; nothing
  else is free.

## 3. Pictures and gates, rule by rule

Sheet for a quick look: `sheet-foldpre.png`. Cuts: `stack-basilica-*.png`, `stack-rabbit-*.png`,
`stack-dendrite-*.png`. Close cuts: `out/me/r16/closecut-g_*.png`. Bench sheets: `out/r16/bench/sheets/g_*.png`.

**P1, the mirror picture, holds exactly** (measured): on the cone that carries the copy of the flat plane the
solid agrees with the flat set on 100.00 % of 270,400 points, for g_p12 and g_p245, for the basilica, the
rabbit and the dendrite (the one-plane rule on that cone: 92.8 %, a plain smooth outline). Seen in
`stack-basilica-oneplane-g_p12-g_p245.png`: the last two tiles of each fold row are the same picture.

### Caps round the poles (g_p12, g_p22, g_p245, g_p30, g_p45): fail at the bench, J2 first
- Close cut by eye: g_p12 looks like the flat basilica's own edge: arcs with round buds, buds on buds, clean
  edges, no hair (seen; its hair number 49 is the known fault of that number). g_p245: the same but the buds
  are a little taller than wide and one tile has a small cluster of droplets. g_p30: buds clearly
  lemon-shaped, a few slivers. So the skin gets worse as the crease goes up, as the stretch says (2.18, 2.83,
  3.33).
- Bench (measured): all three that were run (g_p12, g_p22, g_p245) FAIL J2 with the same numbers as round
  17's m_cap15: no ball up to 0.32 parts the bodies, 0.400 of solid on the upright line through the neck, cut
  1.70 % full. J4 and J8 fail too (roundness 0.08 / 0.41 / 0.35); J3 fails for g_p22 and g_p245.
- What they look like (seen in the bench sheets): g_p12 is a ribbed barrel, the three big bodies and their
  copies fused into one stack of ribs (P4: "fused"); g_p245 is a ball crowded with buds and four extra long
  arms at 45 degrees (P2 for one crease). The upright cut through the x-axis is one slab with no necks at all.
- Not predicted: **the film on the necks** (section 4). P9 said J2 would pass for creases above 20 degrees. Wrong.

### Leaning caps and crossed caps (g_t35, g_d48): fail at the seconds screen
Needle arms: the copies of the long arms arrive with stretch 10.2 (g_t35) and 5.2 to 8.5 (g_d48) (measured).
Seen in `stack-basilica-g_pl-g_t35.png`: four thin needles at 44 degrees on the middle body. Not taken further.

### Kaleidoscope (g_k12, g_k245): fail at the seconds screen
Tear at the upright axis (jump 0.49 over a gap of 0.001, not shrinking in proportion; measured); film on the
necks 0.400 (measured).

### Mixture (g_mix = g_p245 before, round-17 cap fold after): fail at the seconds screen
Film on the necks 0.400 (measured); the poles are sent to -x with stretch 0 (measured), which is round 17's
fault again; four extra arms. A fold after can only add directions to those a fold before already sends to +x
and -x, and each fold multiplies the stretch by a factor over 1 (reasoned). Not taken further.

### Pleats (g_pl, g_pt, g_pt8): the best of the family. Pass the bench, fail the close cut by eye (mildly), fail the rabbit (plainly)
- Seconds: no extra arms, covers the sphere +2 times, no tear. Target 2 NOT met: the bud copies arrive with
  stretch 3.16 and 5.27 (g_pl), 3.16 and 4.43 (g_pt), 2.69 and 3.26 (g_pt8), not near 2 (measured).
- Close cut by eye (`closecut-g_pl.png`, `-g_pt.png`, `-g_pt8.png`): no hair, no dust, no film; the skin
  itself is smooth, with a sharp ridge where a crease runs. But what stands on it are thin slanted leaves, 3 to
  5 times longer than wide in the cut, and small combs of 4 to 6 teeth (g_pl); fewer and fatter for g_pt and
  g_pt8 (ovals about twice as long as wide). Not round buds. By the brief's wording (fins and combs fail) I
  call this a fail for g_pl and borderline for g_pt and g_pt8 (seen in the picture).
- Bench (measured): **g_pl and g_pt pass all eight lines.** g_pl: J2 ball 0.02, line 0.000, cut 0.02 %; J4 14
  buds on the middle body, 8 off the flat plane, 4 of them round; on a bud 10 smaller ones (6 round, 2 off its
  own plane); J8 roundness 0.59, 0.52, 0.57, ribs 0.34, 0.18, 0.31. g_pt: J8 0.58, 0.53, 0.55, ribs 0.14,
  0.09, 0.27. g_pt8 fails J4 only (its copies sit 15 and 23 degrees up and count as "in the flat plane").
  The roundness numbers 0.52 to 0.59 lie in the band the bench's own README calls undecided (rules known bad
  are under 0.34, known good over 0.71): they are lemons, as the stretch says.
- What the basilica looks like (seen, `out/r16/bench/sheets/g_pl.png`, `sheet-foldpre.png`): the one-plane
  basilica, clean, bodies meeting at points, the upright cut through the x-axis untouched, and on each side of
  the middle body a fan of five buds up the sky (latitudes 0, +-21.5, +-33): the flat one round, the others
  lemon- and leaf-shaped, each thinner than the last. The side bodies carry the same fans, smaller.
- Rabbit (the filter; measured by the round-18 panel and seen in `stack-rabbit-*.png`): **out.** g_pl: volume
  1.401 = 3.2 times the yardstick's 0.444 (over 2 = a lump); at the point where three bodies should meet, a
  ball is 83 % full and no ball parts them; 0.4 of solid on the upright line there. The cut across the middle
  shows a swollen middle body with a feathered edge, between curved feathered bands. g_pt8 and g_t35 the same
  by eye. g_p245: the middle body stays round but is ringed by broken lumps and frills.
- Dendrite (g_pl, measured by the panel): **out.** It falls into pieces (biggest piece at 6, 8, 10, 12 steps 98.05, 97.95, 98.05, 97.72 % where the flat tree
  gives 100 %) and it is sheet-like, not a thread (a box twice the size holds 3.6 times the solid; 2 = thread,
  4 = sheet; allowed 3.0). Rabbit lines of the same run: no ball up to 0.32 parts the bodies, the solid reaches
  0.418 straight up from the meeting point (one plane: 0.023), close-up worst 2.30. Log: `logs/panel-g_pl.log`.
  Seen in `stack-dendrite-*.png` (a tree has no inside to paint, so the picture shows where points linger):
  the tree is copied onto the cone (g_p245: 100.00 % agreement) and the cut across the middle shows bright
  arcs round the centre instead of one line.

Why the rabbit fails (reasoned): the creases are fixed in space. For the basilica they were placed over the
only thin spot, the small buds at +-y. The rabbit has a big body in that very direction (its c lies at 99
degrees of longitude, 0.75 out; the body round it is about 19 degrees tall as seen from the centre), so the
crease cuts it, it is fused to its own mirror copy, and the middle body, which takes its shape from that body,
swells. No fixed crease can be clear of the big bodies for every c. This is target 5, and no fold of this
kind can meet it.

## 4. The film on the necks (new; measured with `neckline.py`, seconds)

On the upright line through the basilica's touching point, (-0.618, y, z) with |z| < 0.2: length still inside.

| rule | on the upright plane, y = 0 | y = 0.001 | y = 0.003 | y = 0.01 |
|---|---|---|---|---|
| oneplane, twoplane, along | 0.000 | 0.000 | 0.000 | 0.000 |
| m_cap15 (round 17, fold after) | 0.400 | 0.000 | 0.000 | 0.000 |
| g_p245, g_k245, g_mix | 0.400 | 0.000 | 0.000 | 0.000 |
| g_p12 | 0.400 | 0.026 | 0.024 | 0.015 |
| g_p45 | 0.306 | 0.153 | 0.120 | 0.066 |
| m_cap80 | 0.351 | 0.184 | 0.103 | 0.000 |
| g_t35, g_pl, g_pt, g_pt8 | 0.000 | 0.000 | 0.000 | 0.000 |
| g_d48 | 0.002 | 0.000 | 0.000 | 0.003 |

The same at 60 and at 300 steps. So the "thin sheet standing on every neck" of m_cap15 and of every pole fold
is a film of no thickness lying exactly in the upright plane y = 0: all of the line is inside on the plane,
none of it one thousandth to the side. The bench sees it as a sheet one voxel thick because its grid holds
that plane; that is why J2 gives the identical 0.400 and 1.70 % for four different rules.

Why (reasoned; it fits all 16 rules in the table): for c on the x-axis the upright plane through the x-axis is
kept by the rule. A neck pushes nearby points away from itself, 1.24 times further each step; in the upright
plane that means straight up. The one-plane rule lets them go on up and out. Any crease that crosses the
upright plane hands them back down as their mirror points, and the only ways left are sideways into one of the
two bodies. So they never leave. Creases that stay clear of the upright plane (the leaning caps and pleats)
leave it as the one-plane rule has it: no film.

Round 19's brief gives another reason for m_cap15's sheet (the direction sent to -x is the crushed pole). The
numbers above say the sheet is this film. Foldpost should run `neckline.py` on its rules (it takes any bench
rule name) before reading J2. A film of no thickness may or may not show in the lab (the lab paints every
pixel within a pixel of the set), so I do not call it harmless.

## 5. Verdict on the design targets

1. Exact flat plane, one-plane band, no tear: met by all but the kaleidoscopes (measured).
2. Bud directions arriving with stretch near 2: **not met by any rule, and it cannot be** (reasoned): a copy
   made by mirrors in circles is thinned by the product of the mirrors' factors, each over 1 when the cap is
   smaller than a half sphere and the thing copied lies outside it. Shown here for one cap, two crossed caps
   and a pleat (not for every crease pattern one could draw); measured 2.18 at best, and that rule is a fused
   barrel. A mirror that keeps sizes is a mirror in a plane through the centre, and that cannot leave the flat
   plane alone (round 17).
3. Crushed directions go straight up or down: met (measured).
4. Same above and below, nothing free: the mirrors are exact. A pole cap has one size, and one principle for
   it was found (copy at 45 degrees: crease 24.47). A pleat has four sizes and no principle was found that
   fixes them. Not met for the pleats.
5. Must not need the x-axis: **not met** (rabbit, section 3).

No rule of this section gets through every gate. No claim.

## 6. How to run

    python out/r19/foldpre/dirs.py <rule> ...       # seconds: checks, bud and arm directions with their stretch
    python out/r19/foldpre/neckline.py <rule> ...   # seconds: the film on the necks
    python out/r19/foldpre/stack.py basilica|rabbit|dendrite <rule> ...   # one minute: cuts point by point
    python out/r19/foldpre/sheet.py                 # the summary sheet

## 7. Added at the end: the pleat skin at 33.75 and 45 degrees (`close45.py`, `close45-g_pl.png`, `close45-g_pt.png`)

g_pl (seen in the picture): at widths 0.04 and 0.008 the skin is smooth and clean in all four tiles (hair
number 0.00 to 0.01, measured). At width 0.2 it shows sharp corners where the creases run and, in each of the
two wide tiles, one small comb of 6 to 10 thin slanted teeth (hair number 0.90 and 0.17). g_pt: hair numbers
0.04, 0.00, 0.00, 0.02, 0.00, 0.01 (measured; picture not looked at closely). So the verdict of section 3
stands: no hair, no dust, no film, but small combs and thin leaves in places. A mild fail by eye for g_pl.

## 8. Files outside this folder that the brief's own commands wrote

`out/me/r16/closecut-g_*.png` (closecut), `out/r16/bench/results|sheets|tiles|cache/g_*` (bench stage 1 for
g_p12, g_p22, g_p245, g_pl, g_pt, g_pt8), `out/r18/panel/results|tiles|sheets/g_pl*` (panel, rabbit and
dendrite only). No .py file of the bench or the panel was touched.
