# Round 23, section outside1: what has the fractal community tried for a power-2 3D Mandelbrot?

Every statement is marked (measured) = a number I computed, (seen) = in a picture I opened, (reasoned).

## Straight answer

No. Nobody outside has a formula that passes the user's five tests, and none comes closer than `along` (reasoned from
the measurements below, for the 17 formulas I could pin down; the forum itself could not be read today, see "What failed").

What was found instead:

1. **The project's two favourites, and its one-plane rule, were all found outside before, in the same form for c on the x-axis.**
   - Msltoe's "Sym2" / "Sym3" (forum thread "choosing the squaring formula by location", 2009-2010) is the two-planes
     idea: square about the nearer of the two planes. For c = -1 its solid differs from `twoplane` on 3.8 % of the
     inside (measured); same clean bodies with four buds (seen, `sheet.png`).
   - Eiffie's version (reply 69, January 2015) folds the turn round the x-axis into eight wedges: the nearest of FOUR
     planes. 8 directions go to -x and 2 to +x, the same count as `along` (measured). For c = -1 its solid differs from
     `along` on 2.8 % of the inside (measured); same bodies with eight buds round each (seen).
   - The Mandelcup (pupukuusikko) with its two dials set to Shape 1, Scale 1/2 is `oneplane` exactly: 0 of 400,000
     verdicts differ for c = -1 and for the rabbit (measured). (That dial setting is my choice; the program's defaults were not read.)
2. **Off the x-axis the outside versions are worse than ours, not better.** Sym2, Sym3 and Eiffie fold the flat plane
   itself (y becomes |y|), so their cut at z = 0 is the flat picture only when c is on the x-axis: for the rabbit 2715
   (Sym2, Sym3: every flat-inside point lost) and 2415 (Eiffie) of 20,000 verdicts differ (measured). Sym2 / Sym3 have no
   rabbit at all (inside share 0.0000, empty panels seen); Eiffie's rabbit is one round lump (inside 0.078 of the box
   against 0.016 for one plane, measured; seen).
3. **Seven outside formulas are exact on the flat plane for every c** (flat check 0 of 20,000 differ in all four sets,
   measured): Mandelbulb power 2, quaternion cut (= the Lathe), Bristorbrot, scator "ix", hypercomplex cut, Hopfbrot
   cut (= the Mandelbulb, measured), Mandelcup(1, 1/2) (= one plane, measured). None has round buds off the flat plane
   together with a clean rabbit (seen, `all-solids-1.png`, `all-solids-2.png`): flakes and whiskers (Mandelbulb), rings
   (quaternion), fins and a ridged lump (Bristorbrot), long needles (scator), faceted bodies and slivers (hypercomplex).
4. **The community says so itself** (through the fetch and search tools, see formulas.md part D): Daniel White's page
   calls it the Holy Grail and says the angle-doubling shapes are not it; what he hoped for is the user's own picture
   (a body with spheres round it and further spheres round those). Tom Lowe is quoted in 2022 as saying nothing nearly as
   significant as the Mandelbrot set has been found in 3D.

Against the five tests (1 flat cut exact, 2 bodies from the power, 3 no shards, 4 no rings, 5 principled):

| rule | test 1 flat cut (differ of 20,000: M / c=-1 / rabbit / Siegel) | lift c=-1 / rabbit | to -x / to +x | door | c = -1 (seen) | rabbit (seen) |
|---|---|---|---|---|---|---|
| ours `oneplane` | 0 / 0 / 0 / 0 | 1.000 / 1.000 | 2 / 2 | none | clean, buds in the flat plane only | clean separate bodies, nothing off the plane |
| ours `twoplane` | 0 / 0 / 0 / 0 | 1.000 / 1.000 | 4 / 2 | tear | clean, four buds | shards |
| ours `along` | 0 / 0 / 0 / 0 | 1.000 / 1.000 | 8 / 2 | fold 39 % | eight buds on each body | one swollen ribbed lump |
| `mb2` Mandelbulb p2 | 0 / 0 / 0 / 0 | 1.000 / 1.000 | 2 / 2 | fold 71 %, torn poles | bodies with flakes and whiskers | bodies with debris |
| `quat3d` quaternion | 0 / 0 / 0 / 0 | 1.000 / 1.000 | circle / 2 | spun | rings | ringed lump |
| `bristor` | 0 / 0 / 0 / 0 | 1.000 / 1.000 | 6 / 2 | fold 50 % | bodies with rough fins | ridged lump |
| `sym2` | 2337 / 0 / 2715 / 3415 | 1.000 / 0.000 | 4 / 2 | tear + fold | as two planes | nothing |
| `sym3` | 2337 / 0 / 2715 / 3415 | 1.000 / 0.000 | 4 / 2 | fold 50 %, no tear | as two planes | nothing |
| `sym4` | 5220 / 4097 / 2715 / 9205 | 0.975 / 0.000 | 0 / 6 | fold | cross of lumps, debris | nothing |
| `eiffie` | 2264 / 0 / 2415 / 3770 | 1.000 / 0.594 | 8 / 2 | fold 50 %, no tear | as along | one round lump |
| `benesi` | 4806 / 0 / 8169 / 3770 | 1.000 / 1.000 | circle / 2 | spun + fold | rings (= Lathe, 0 differ) | ridged lump |
| `scator_ix` | 0 / 0 / 0 / 0 | 0.998 / 0.946 | 0 / circle | tear on x = 0 | spiky star, needles | spiky star, needles |
| `hyper` | 0 / 0 / 0 / 0 | 1.000 / 0.991 | not screened (4D) | two flat rules crossed | four buds, bumpy faceted skin | bodies frayed into slivers |
| `quickdudley` | 1882 / 506 / 2715 / 2508 | 0.840 / 0.000 | 2 / 2 | fold | blocks with shards | dust |
| `lkmitch` | 1955 / 901 / 2715 / 1964 | 0.693 / 0.000 | 0 / 4 | fold | blocky cross | nothing |
| `makin3d2` | 2337 / 418 / 4042 / 3770 | 0.881 / 0.644 | 2 / 2 | fold | lumpy with shards | one spindle |
| `xeno_t` | 3558 / 0 / 2715 / 6557 | 1.000 / 0.000 | circle / 2 | spun + fold | rings (= Lathe, 0 differ) | nothing |
| `cup0` Mandelcup(0, 1) | 1238 / 3049 / 2715 / 3768 | 0.123 / 0.000 | 4 / 4 | fold | ringed cup | dust |
| `cup1` Mandelcup(1, 1/2) | 0 / 0 / 0 / 0 | 1.000 / 1.000 | 2 / 2 | none (flipped) | = one plane | = one plane |
| `mandelnest` | 2528 / 2960 / 2715 / 3770 | 0.000 / 0.000 | 5 / 0 | fold | nothing | nothing |
| `hopfcut` | 0 / 0 / 0 / 0 | 1.000 / 1.000 | 2 / 2 | fold, torn poles | = Mandelbulb | = Mandelbulb |

All numbers in this table are measured (`check.log`, `checks.json`, `compare.log`); the two "seen" columns are from
`all-solids-1.png`, `all-solids-2.png`, `sheet.png`. "circle" = a whole circle of directions (23 or 22 groups found).

The three that come closest to the user's words (`sheet.png`): `sym2` (the two-planes look), `eiffie` (the along look),
`hyper` (the only other outside formula with an exact flat cut for every c, buds in more than two directions and no
rings; its rabbit keeps three bodies in place, but frayed). None is closer than `along` on c = -1 (Eiffie equals it
there) and none is closer than "along once" on the rabbit (reasoned from the pictures; "along once" was not redrawn here).

## What this gives the next sections (reasoned unless marked)

- The community reached the same two looks through the same idea, "square about the nearest of 2 or 4 planes through
  the x-axis", and never got past the same wall: bodies off the x-axis. That is independent support for section 2 (a)
  of the briefing (the hinge is the problem), not a way round it.
- Sym3 against Sym2 is a small lesson: the tear of two planes can be replaced by a mirror fold with the same count
  (4 to -x, 2 to +x) and the same c = -1 solid (identical inside shares, measured; jumps 2e-4 instead of 2.0, measured).
  The price in Sym3 and in Eiffie's formula is that the flat plane itself is folded (y -> |y|), which is why they lose
  the rabbit. Reason: a mirror fold into one wedge must send the two wedges on either side of the upright plane to the
  same wedge, and that forces y and -y together. So the fold door, as the community uses it, pays with test 1 for c
  off the x-axis; `along` (a fold of 39 % that leaves the flat plane alone) is already the better version of it.
- Bristorbrot is the one outside formula that is exact on both planes for every c with no tear (a polynomial;
  measured: z = 0 and y = 0 exact to 0, jumps 3e-4) and sends 6 directions to -x. It does not contradict round 17's
  "no tear-free rule exact on two mirror planes with the 4-and-2 count": its planes are not mirror planes (the formula
  changes under z -> -z), its count is 6 and 2, and it folds 50 %. Its pictures are not good (fins, ridged lump), but it
  is a different kind of example from anything in the lab and cheap to look at again.
- Scator "ix" is exact on both planes for every c and its rabbit has a solid inside (lift 0.946, measured), but off the
  planes everything is needles: it divides by x, so the whole plane x = 0 is thrown to infinity. Not a lead.
- The hypercomplex cut is "two flat pictures pushed straight through space and crossed": the user's "blown up 2D
  version which is not what I want", twice. Not a lead, but it is the cleanest outside rabbit that is not one plane's.

## What was done

- Read 28 formula files of Mandelbulber 2 (its headers cite the forum threads), MathWorld's Hopfbrot page, the arXiv
  abstract of Knill 2023, White's Mandelbulb page, Wikipedia. Pinned down 17 formulas (formulas.md part A), gave 9 more
  one line each (part B), listed 4 that could not be read (part C).
- Typed each as a rule: `outrules.py` (`O.get(name)`, `O.plain(name)`, `O.NAMES`). `python out/r23/outside1/outrules.py`
  prints finiteness, length ratio and the z = 0 comparison for each.
- `check.py`: `M.flat_check` (20,000 points per set, 60 steps), lift test (flat-inside points lifted by 1e-6, 60 steps),
  inside share of a box (200,000 points, 40 steps), round 17's `screen` (covers, folded share, jumps) and a copy of
  `count_dirs` (1.5 million directions). Output `check.log`, `checks.json`. The LAST line for a name in `check.log` is the
  valid one (scator, the cups and hopfcut were re-run after fixes; `checks.json` holds the final values).
- `compare.py`: verdicts of pairs of rules on 400,000 points, and inside share at 30 against 80 steps. Output `compare.log`.
  30 against 80 steps: c = -1 keeps 99.9 to 100 % for along, twoplane, sym2, eiffie, hyper, bristor, mb2, scator; the
  rabbit keeps 98.3 % (along), 95.9 % (twoplane), 93.8 % (eiffie), 92.8 % (hyper), 98.0 % (bristor) (measured).
- `draw.py`: rough solids (28 steps) of c = -1 and the rabbit from two eye positions (front (0.45, 0.5, 1.0), along
  the x-axis (1.0, 0.42, 0.22)) for the three reference rules and all 18 outside rules; cuts for five rules.
- Turning to the best plane: `xeno_t` is Xenodreambuie turned (its real line is its z-axis). For the three polynomial
  triples `O.best_plane` searched all planes through 0 and found none with complex squaring (misfit 0.39, 0.71, 0.40;
  measured), so they are drawn as given. Mandelcup(0, 1) and Mandelnest have no such plane either (reasoned from the
  code: the cup sends its whole plane z = 0 to a pole; the nest is even in every coordinate).

## What failed or is weak

- **fractalforums.com could not be read**: every request returned "SMF was unable to connect to the database", later
  HTTP 429; web.archive.org is blocked for the fetch tool. So no forum post is quoted directly, and three threads named
  in formulas.md part C (Nylander's Hopf-map formula of 2009, "rotation away from azimuthal axis", the "summary of 3D
  Mandelbrot set formulas") are NOT tested. The answer above holds for what Mandelbulber's formula list carries (which
  is where forum formulas that people kept using ended up), not for every post ever made.
- The small model behind the fetch tool refused to print three files in full (Makin 3D-2, Aexion, Msltoe Donut); for
  Makin and Aexion the squaring lines were fetched again separately and are quoted; the Donut is described only.
- Two formulas needed a guard to be testable at all, and I say so in formulas.md: scator "ix" with the source's own
  commented-out `+ 1e-30` (without it the flat picture of c = -1 is lost: 2960 of 2960, measured), and the Mandelcup
  at the one direction its projection sends to infinity (without it Mandelcup(1, 1/2) loses 37 % of the c = -1 body to
  0 / 0 on the pole ray: inside 0.0161 against 0.0257, measured before the fix).
- Mandelcup's default Shape and Scale were not read from the program; `cup0` is a guess at "neutral" values.
- The hypercomplex rule's escape test looks at x, y, z only (the library's test), not at the carried fourth coordinate.
- Benesi's formula depends on the sign of c.x; `O.plain('benesi')` and the screen use the branch for c.x < 0 (both test shapes).
- No Mandelbrot solids were drawn, no Siegel disc or dendrite solids; solids are rough blocks at 28 steps.
- "Closer than along once on the rabbit" is judged from pictures of this section against the briefing's description
  of "along once"; that rule was not drawn here.

## Pictures (all in out/r23/outside1/)

- `sheet.png`: rows one plane, two planes, along (ours), then Msltoe Sym2, Eiffie / Msltoe, hypercomplex cut. Columns
  c = -1 front, c = -1 along the x-axis, rabbit front, rabbit along the x-axis. Seen: Sym2's c = -1 looks like two
  planes and its rabbit panels are empty; Eiffie's c = -1 looks like along and its rabbit is one round lump with spiral
  marks; the hypercomplex c = -1 has four buds and a bumpy skin, its rabbit is three bodies frayed into slivers.
- `all-solids-1.png`: one plane, two planes, along, Mandelbulb p2, quaternion, Bristorbrot, Sym2, Sym3, Sym4, Eiffie.
- `all-solids-2.png`: Benesi, scator ix, hypercomplex, Quick Dudley, Lkmitch, Makin 3D-2, Xenodreambuie, Mandelcup
  (0, 1), Mandelcup (1, 1/2), Mandelnest, Hopfbrot cut.
- `cuts-eiffie.png`: c = -1: flat basilica at 0, 45, 90 degrees, smooth at 22.5, rounded octagon across. Rabbit: a
  mirror-symmetric double rabbit at 0, 45, 90 (not the rabbit), shards at 22.5.
- `cuts-sym2.png`: c = -1: flat basilica at 0 and 90, smooth at 22.5 and 45. Rabbit: empty in every cut.
- `cuts-scator_ix.png`: c = -1: basilica at 0 and 90, feathers at 22.5, two bodies with hyperbola-shaped shards at 45.
  Rabbit: the rabbit at 0, needles elsewhere, nothing across x = 0.
- `cuts-bristor.png`: c = -1: basilica at 0 and 90, smooth with tiny bumps between. Rabbit: the rabbit at 0, a
  recognisable rabbit at 22.5, a squared one at 45, a four-pointed star at 90, a disc with two arcs across.
- `cuts-along.png`: the same cuts for `along`, for comparison.
- `tiles/`, `tiles-big/`: the single panels the sheets are pasted from.

## Files

`formulas.md` (every formula with its source), `outrules.py`, `check.py`, `compare.py`, `draw.py`, `check.log`,
`checks.json`, `compare.log`, `tiles1.log`, `tiles2.log`, `sheet.log`.
