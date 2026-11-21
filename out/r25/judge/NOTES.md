# Round 25, judge: working notes (internal names and numbers live here; the plain answers are in ANSWERS.md)

Marks: **measured** (a number from one of my scripts, log named), **seen** (in a picture I opened), **reasoned**,
**theorem** (short proof or cited), **read** (a published source, and how I read it).
I did not do the eight sections' work. Everything below marked measured or seen was made again with my own scripts in
`out/r25/judge/`; the sections' rules were only loaded (`jl.py`), never retyped. Where I only read a section's notes
and did not re-measure, it says so.

## 0. Verdict in six lines

1. Nobody found it. Fourteen new rules "square, add c" (and two for the power 3) pass my flat check; none passes tests 3 and 4 for both c = -1 and the rabbit. **measured, seen**
2. The only object that has the whole look (blown up, perfect balls on balls all over, nothing stretched, nothing lopsided) is klein's pearl tree. It is made of sphere inversions only, has no c and no power, and its flat cut is not the flat picture (38.6 % of the true area wrong; I got the same number). **measured, seen**
3. Nearest for c = -1: pillow's skew pillow. Nearest for the rabbit: fromc's twin_tri, which is one plane with a scratched skin. Nearest at another power: wall's even cube at c = i. Each fails, numbers in section 3.
4. New from me: wall's "one clean case" is lopsided (13.5 % of the solid has no partner under the third of a turn the flat picture keeps), and that is forced; the one even pattern that would keep that turn (power 3 on two flat triangles, built here as a probe) is a ridged lump. So even spacing is lopsided or lumped at every power tried. **measured, seen, reasoned**
5. New from me: the skew pillow has a handedness. The mirror-image rabbit gives a solid 4 times as big (one lump) instead of the mirror image. All the user's own rules give the exact mirror image. **measured**
6. The wall stands for z^2 + c. No proof closes it as a whole; section 4.

## 1. What I ran

| script | what | log |
|---|---|---|
| `flat.py` | my flat check: 30,000 points, 80 steps, own seed, own boxes, my own complex orbit; Mandelbrot set + 8 Julia sets; also one-step error and speed | `flat-1.log`, `flat-2.log` |
| `measure.py` | one grid of blocks per rule and c (side 0.015, 240 x 200 x 200, 50 steps): size, leak, lopsidedness, pieces and crumbs, skin growth, material outside the one-plane solid, how long the extra bodies are | `m-*.log` |
| `attack.py` | tear, pearl tree flat cut, zip plain orbit, turn test, mirror-image rabbit | `a-*.log` |
| `probe.py` | power 3 on two flat triangles (flat check); zip with its NaN removed | `p-*.log` |
| `draw.py`, `compose.py` | rough solids 440 x 330, 280 blocks deep, 40 steps (sections used 160 to 230 blocks, 26 to 40 steps), two eyes | `d-*.log` |

## 2. Flat check, mine (all **measured**, `flat-1.log`, `flat-2.log`)

0 differing verdicts of 30,000 in every one of nine sets (Mandelbrot, c = -1, rabbit, c = -0.75, Siegel, mirror rabbit,
-0.12 + 0.6i, 0.28 + 0.53i, c = i) for: oneplane, twoplane, along, skew, skew-mirror, tetra, square pillow (pillow's),
twin_tri, face_tri, axis_once, wall's square pattern, fourd's cone cut, holo, zip (b = 1, 2), ring3, kfix.
Even cube against z^3 + c: 0 of 30,000 in six sets. My probe tri3 against z^3 + c: 0 of 30,000 in five sets.
One squaring keeps a flat point on the plane to 1e-14 or better in all of them. So every section's "passes the flat
check" claim holds. The pearl tree has no c; its flat cut is checked in section 3d.

## 3. The candidates, re-measured

How to read the numbers (**measured** on the user's favourites first, `m-base.log`, `m-bench.log`):

| | c | skin growth (2.0 = smooth) | crumbs (share of solid) | outside the one-plane solid | extra bodies: long / thick | no partner: above-below / half turn |
|---|---|---|---|---|---|---|
| one plane | -1 | 2.06 | 0.0004 | 0 | - | 0 / 0 |
| two planes | -1 | 2.09 | 0.0013 | 0.007 | 1.46 | 0 / 0 |
| along | -1 | 2.15 | 0.0056 | 0.027 | 1.42 | 0 / 0.012 |
| one plane | rabbit | 2.10 | 0.0020 | 0 | - | 0 / 0 |
| along once | rabbit | 2.12 | 0.0031 | 0.355 | 2.33 | 0 / 0.318 |
| along | rabbit | 2.40 | 0.0029 | 0.728 (3.66 x one plane: the lump) | - | 0 / 0.317 |

"Long / thick" is the longest over the shortest axis of each piece of the solid that lies outside the one-plane solid
(one block shaved off to cut necks, pieces of 150 blocks or more, median). A round bud cut off at the one-plane skin
scores about 1.4 (two planes, along). A true ball scores 1.0 (pearl tree, against its own one-plane version).
Note for the lab: "along once" and "along" at the rabbit are 32 % lopsided under the half turn that the flat rabbit keeps (**measured**, `a-turn.log`); two planes at the rabbit 21 %.

### 3a. skew pillow (pillow) : nearest to the user's picture for c = -1

`m-skew.log`, `a-mirror.log`, `a-lift.log`, pictures `1-c-minus-1.png`, `2-rabbit.png`, `w-tilt.png`.

| c | size against one plane | skin growth | crumbs | outside one plane | one-plane solid missing | long / thick | above-below no partner | y-mirror no partner |
|---|---|---|---|---|---|---|---|---|
| -1 | 1.09 | 2.20 | 986 pieces, 0.0096 | 0.153 | 0.073 | 2.37 (two biggest 1.88) | 0.178 (volume above / below 0.836) | 0.174 (flat picture: 0) |
| rabbit | 1.08 | 2.42 | 3,490 pieces, 0.0495 | 0.314 | 0.257 | 1.80 | 0.371 (0.664) | - |
| mirror rabbit | 4.35 | 2.34 | 0.0013 | 0.771 | 0.002 | one lump (biggest piece 0.999) | 0.384 | - |
| -0.75 | 1.27 | 2.25 | 0.0007 | 0.266 | 0.064 | 1.65 | 0.285 | 0.251 |
| Siegel | 1.51 | 2.39 | 0.0012 | 0.431 | 0.141 | 5.07 | 0.376 | - |

- **seen**: c = -1 at 280 blocks is what pillow said: three bodies apart, egg-shaped bodies with buds of their own on them, on one side, thorns on the skin. It holds up at finer blocks (no crust). The rabbit is rough small lumps with crumbs from both eyes.
- **measured**: pillow's own numbers reproduce (above / below 0.84 and 0.66; 17 % not its own mirror image; eggs "about 2 to 1": 1.9 to 2.4; mirror rabbit 4 times the size).
- **measured, new**: mirror test. For c and conj(c) the flat pictures are mirror images. One plane, two planes, along, along once, twin_tri, cone cut: the solid of conj(c), mirrored back, is the solid of c (0.0 % differs). Skew pillow: 346 % of the solid differs. A left or right was chosen in the rule. This is a failure of "nothing chosen" that pillow reported only as "a lump for the mirror image".
- **measured**: c lifted out of the flat plane by 0.25 to 6 degrees: the solid stays and grows slowly (0.0246 to 0.0286 at c = -1). It does not fail this attack. (One plane and along once lose the whole solid between 2 and 3 degrees at c = -1 and between 1 and 2 at the rabbit; two planes and along keep c = -1 to 6 degrees. `a-lift.log`.)
- Gives up: test 3 (thorns, crumbs), "not stretched" (eggs), lopsided above / below by force (wall's and pillow's theorem), a chosen handedness, and test 4 for every c but c = -1.

### 3b. twin_tri (fromc) : nearest for the rabbit

`m-twin.log`, `a-tear.log`, `a-lift.log`.

| c | size against one plane | skin growth | crumbs | outside one plane | long / thick of extra bodies |
|---|---|---|---|---|---|
| -1 | 0.91 | 2.22 | 0.0071 | 0.028 | 4.58 (four pieces of 282 blocks: thorns) |
| rabbit | 0.96 | 2.30 | 0.0173 | 0.056 | no extra body of 150 blocks |
| -0.75 | 0.86 | 2.24 | 0.0013 | 0.023 | 5.15 |
| Siegel | 0.56 | 2.73 | 0.0392 (5,066 crumbs) | 0.247 | splinters |

- Even: 0 % no partner above / below, half turn, and mirror test (**measured**).
- It is one plane with a scratched skin: 3 to 6 % of the solid lies outside the one-plane solid, and that is thorns. **measured, seen**
- Its fold is a tear off the flat plane: the two sides are sent 3.0 / 11.8 / 27.2 / 90.3 / 139.5 degrees apart at height angles 10 / 20 / 30 / 45 / 60 (fromc's numbers, reproduced exactly). **measured**
- c lifted 3 degrees: rabbit 0.0132 to 0.0066 and still leaking at 150 steps (0.0080 / 0.0070 / 0.0066); nothing left at 6 degrees. **measured**
- The Siegel disc loses 58 % of the one-plane solid and is splinters. Its "meeting point" is the centre of the disc there, not a meeting point at all (**reasoned**: the rule reads the fixed point (1 - sqrt(1 - 4c))/2, which is where bodies meet only for c in the bulbs fastened to the main body).
- fromc's correction of the briefing holds (**measured**, `m-tri2.log`): round 24's triangle rule unturned, c = -1: one piece holds 0.994 of the solid, 2.14 x one plane. Turned by c (face_tri): pieces 0.673 and 0.204, 1.13 x. So "fused by its nature" was wrong; it was fused because the pattern was not turned. face_tri is lopsided instead (half turn 16 % at c = -1, 46 % at the rabbit).
- Gives up: test 4 (nothing blown up off the flat picture), test 3 (flakes, scratches, a tear).

### 3c. even cube at c = i (wall) : "the one clean case", at the power 3

`m-cube.log`, `a-turn.log`, `m-tri3.log`, `p-tri3.log`, pictures `3-bulbs-all-over.png`, `w-cube.png`, `w-tilt.png`.

- **measured**: flat check exact; nothing leaks (0.0314 at 30, 60, 150 steps); survives c lifted 3 degrees (0.0298); mirror x -> -x exact (0.000). All as wall said.
- **measured, new**: the flat picture of z^3 + c is unchanged by a third of a turn. The one-plane cube solid keeps it (0.0 %). The even cube does not: 13.5 % of the solid has no partner (c = i), 21.8 % at the three-bodied c. wall checked only the left-right mirror.
- **reasoned**: forced. The pattern's four special spots stand above two opposite directions, so the pattern repeats twice round, never three times. For the square the same pattern repeats twice round (good) but cannot sit the same above and below (wall's theorem). So on four spots no power has both.
- **measured**: extra bodies: the two biggest 1.35 long / thick (as round as along's buds), the other six 2.6 to 3.5; median 3.27. Skin growth 2.23, crumbs 0.0076. wall's "eggs about 2 to 1 by eye" is too kind for six of eight.
- **seen** at 280 blocks, 40 steps: a blown-up body, smaller bodies in many directions, pointed and thorny; the three arms do not match.
- Three-bodied c: one lump, 2.72 x the one-plane cube solid, biggest piece 0.999. As wall said.
- **Probe (mine)**: the one even pattern that does repeat three times round is round 24's two flat triangles; nobody had run it at the power 3 (`tri3` = `tri.tri_rule(3)`). Flat check 0 of 30,000 (five sets); third of a turn 0.000, above / below 0.000. **Seen**: one ridged lump at c = i and at the three-bodied c, from both eyes (`w-cube.png`). **Measured**: skin growth 2.51 and 2.70, biggest piece 0.975, extra bodies 6.9 long / thick. It is also 36 % lopsided under the left-right mirror that the flat picture of c = i keeps (its three spots sit on the flat circle at fixed places). So the lead does not open into a family.

### 3d. pearl tree (klein) : the look, without the flat picture

`m-other.log`, `a-pearl.log`, picture `3-bulbs-all-over.png`.

- **measured**: flat cut against the true flat picture of c = -1: 38.6 % of the true area wrong (27.1 % extra, 11.5 % missing); the same for Gaussian, Eisenstein and the one-plane tree. Control on the same grid: skew pillow 0.000 %.
- **measured**: balls: long / thick 1.01 to 1.03. No partner missing under any mirror or half turn: 0.000. 8, 14 and 40 rounds give the same solid.
- **seen**: balls on balls on balls all over, from both eyes.
- Not re-derived by me: "three balls cannot share a point, so no rabbit" (**theorem**, two balls that touch have one common tangent plane and a third must lie on one of its sides); the discreteness proof (klein's, **read** in their notes only).

### 3e. the others (lighter touch)

- cone cut (fourd): c = -1: no extra body of 150 blocks; 17.6 % of the one-plane solid missing; skin growth 2.38. Rabbit: biggest piece 0.495, crumbs 0.021, skin 2.51. Fails 3 and 4 as fourd said. **measured**
- tetra pillow: c = -1 above-below no partner 39 %, crumbs 0.028; rabbit one piece (0.991), 1.68 x. **measured**
- zip (inverse): `best.rule(1.0)` as delivered gives an EMPTY solid for c = -1 under a plain orbit (0.0261 at 20 steps, 0.0000 at 40). Cause: the rule returns NaN for a point exactly on the upright axis, and the orbit of c = -1 lands there by rounding (traced, `a-zip.log` and section 5). With such points nudged off the axis the solid is 0.0660 of the box, 2.96 x one plane: inverse's "3.0 times" lump is confirmed, the delivered rule is not. Rabbit unaffected (0.0221, 1.6 x one plane). **measured**
- holo, ring3, kfix, wall's square pattern, vahlen's and fourd's carried quaternions: flat check only (0 everywhere); their solids I looked at in the sections' own sheets (**seen**: lenses; shells and crumbs; rock; lump; rings and empty rabbit panels). Not re-drawn.

## 4. The wall

- (W-a): two sections (wall, torus) independently found that the statement needs "length squared times a map of directions"; both built the same counter-kind (three times round the unit circle, then one plane: shells). I did not re-measure it; I confirmed ring3's flat check (0) and its size (0.30 of the box at 30 steps). With "c = 0 gives the plain ball" added wall proves the four cases come back. **reasoned by them, read by me**
- (W-b): **theorem**; wall's stronger form (also for rules that look at c) reads correct to me.
- (W-d): **theorem**; plus wall's parity fact and my turn fact (3c). Together (**reasoned**): an even pattern on a ball has the picture's own turns and its above-below mirror at no power: four spots lose above-below at the square and the turn at every higher power; three spots lose the half turn at the square (face_tri: 16 % and 46 %, measured) and keep both at the power 3 only by putting the spots on the flat circle (lump, measured).
- (W-e): the measurement stands; the wording does not. "Fused by its nature" was wrong for the triangle rule (3b). And a lump comes also where the push is even (skew pillow, mirror rabbit: pillow measured push 2.00 everywhere; I measured the lump).
- (W-f): not re-measured.
- Martin 2004 (vahlen's item). **Read at second hand**: Meyer and Muench, arXiv 2510.18015, introduction: Martin found criteria for the non-existence of uniformly quasi-regular extensions; a rational map with a super-attracting fixed point (or cycle) has no uniformly quasi-regular map of the upper half-space inducing it on the boundary. I could not open Martin's paper itself (the journal page refused the request). What it covers: rules that keep each side of the flat plane to itself. What it does not cover: rules that send points off the plane INTO the plane (every rule with extra copies does). So it proves "one-plane kinds must squeeze without bound", not the whole wall.
- fromc's junction argument (bulbs four ways round each body's own line cannot close up where three bodies meet): sound as group counting, under its premise that the surroundings of a meeting point look the same after a quarter turn about each body's line. It does not forbid bulbs placed otherwise. **reasoned**
- "Adds up to": still no counterexample and still no proof. Eight independent starts, some forty rules and objects by their own count, none through.

## 5. Things that did not hold, or held only in part

1. inverse: `best.rule(1.0)` is empty at c = -1 as delivered (NaN on the upright axis). Trace: step 9 leaves height -2e-13 beside (-1, 0, 0), step 11 lands at (0, 0, -2e-13), step 12 returns NaN. Claim confirmed only after my nudge.
2. wall: "one clean case", "mirror-exact": true for the one mirror tested, but 13.5 % lopsided under the third of a turn; and the eggs are 2.6 to 3.5 long for six of eight.
3. briefing section 4: "triangle pillow: c = -1 fused along the whole x-axis by its nature": wrong (3b).
4. briefing (W-e) wording, and (W-a) wording: see section 4.
5. fromc's and pillow's "nearest things" are described fairly by their authors; I found nothing better in them than they said, and two things worse (handedness of the skew pillow; twin_tri's Siegel disc and its decay when c is lifted).

## 6. What I did not do

- No Mandelbrot solids for the candidates (only c lifted by up to 6 degrees).
- (W-f), the carried-quaternion laws (vahlen, fromc, fourd) and klein's group proofs were read, not re-measured.
- skin growth is from one grid and its two coarser sub-grids; it ranks rules, it is not a dimension.
- The tear test by random pairs finds only tears that fill space; twin_tri's seam was tested directly, the pillows' seams were not (pillow's `seamjump.log` not repeated).
- A house-rule slip of mine: two throw-away debug scripts were written with a shell heredoc into the scratchpad (not into the project); every file in `out/r25/judge/` was written with the editor.

## 7. Files

`jl.py` loader; `flat.py`; `measure.py` (grids in `cache/g-*.npz`); `attack.py`; `probe.py`; `draw.py` (depth maps in `cache/d-*.npz`); `compose.py`.
Pictures for the user: `1-c-minus-1.png`, `2-rabbit.png`, `3-bulbs-all-over.png`. Working sheets: `w-tilt.png`, `w-cube.png`.
Logs: `flat-*.log`, `m-*.log`, `a-*.log`, `p-*.log`, `d-*.log`.
