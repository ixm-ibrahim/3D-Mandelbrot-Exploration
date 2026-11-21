# Round 25, section "fromc": rules in which the flat picture does the choosing

Marks: **[M]** measured (a number I computed), **[S]** seen (in a picture I opened), **[R]** reasoned, **[T]** theorem
(short proof given or standard). Everything is in `out/r25/fromc/`. Internal names are used freely here; the plain
lines for the user are in section 0 and section 7 only.

## 0. Result in six plain lines

1. Nothing from this corner passes. No rule here gives the rabbit a blown-up body with round bulbs all over. [S]
2. A quaternion carried along the orbit and turned as the point turns is, for c on the x-axis, exactly the
   quaternion square (rings), and for the rabbit it leaves nothing at all off the flat picture. [M, S]
3. Letting c turn the rule so that its special direction points at the place where the bodies meet is the one thing
   that helped: it takes the lump away every time (rabbit under the copy-twice rule, c = -1 under the triangle rule). [M, S]
4. But what is left after the lump is gone is rough: spindles and flakes, or a scratched skin with small thorns. [S, M]
5. The look that "two planes" and "along" give c = -1 cannot exist for the rabbit at all, by any rule: three bodies
   meeting in a flat ring cannot each be turned a quarter-turn about their own line without the copies overlapping. [R, M]
6. Nearest thing (`twin_tri`): separate bodies for c = -1 AND the rabbit, not lopsided, small thorny knobs all over;
   it fails "no shards" (3.8 % of the rabbit is loose flakes, the skin is scratched) and "round bodies on the body". [M, S]

## 1. What was built (all in `rules.py`; `R.get(name)`)

Every rule is "square of v, then + c"; all read c through its flat part (cx, cy) only (cz is simply added).
a = a(c) = (1 - sqrt(1 - 4c)) / 2 is the flat fixed point where the big bodies meet ("the meeting point").

| name | the rule | kind |
|---|---|---|
| `spin` | The orbit carries a quaternion Q with v = Q i Q* (x, y, z = the i, j, k parts). Square: Q -> Q^2. Adding c: Q is turned by the shortest turn from the old direction to the new one and stretched (Q' = sqrt\|v'\| N(Q^2 - v'^ Q^2 i)). First lift: shortest turn from the x-axis to the point (its square is -v i, no bad direction). | carries a quaternion |
| `prod` | z^2 + c = a + (z - a)(z + a). In space: a + (v - a) * (v + a), with * the sphere-inversion product (lengths multiply, turns round the upright axis add, Mercator heights add). | looks at c |
| `axis_every` | "along" about the line from 0 to a instead of the x-axis: Rot_z(2 arg a) along(Rot_z(-arg a) v). Round 22's `alonghinge`, rebuilt for reference. | looks at c |
| `axis_once` | that step at the first squaring only, the one-plane square afterwards | looks at c, counts |
| `axis_cycle` | that step once per round trip of c's cycle (when the orbit is in the body that holds 0; which steps those are is read off the flat orbit of the start point's shadow), one plane in between. Tests round 22's open suggestion "pages that come back after the cycle's length". | looks at c and at the orbit |
| `m4` / `face4` | direction map R(w) = (w^4 + t)/(w^2 (1 + t w^4)), t = -0.2, blended into doubling beside the flat plane (round 24's m = 4), length squared. `face4`: the pattern turned by c: Rot_z(2 arg a) G Rot_z(-arg a). | `face4` looks at c |
| `m4m` / `face4m` (also `face3`, `face3m`, `face6`, `face6m`) | the same with the length NOT squared: \|v\| to the power max(2, s), s = the sideways stretch of the direction map there (door (ii), tried because it was cheap) | side test |
| `tri` / `face_tri` | direction map "times 2 on two flat triangles" (`out/r24/me/tri.py`: even spacing, three corners on the flat circle, laid over 4 times), length squared. `face_tri`: turned by c so that one corner lies on the meeting point. | `face_tri` looks at c |
| `twin_tri` | `face_tri` after a fold: a direction on the far side from a is first turned half-way round the upright axis (z and -z have the same square). A corner then lies on the meeting point AND on its twin -a. | looks at c; has a seam |

For c off the flat plane: `spin` is defined for every c in space; the others read only c's shadow on the flat plane.

## 2. Numbers [M] (`check.py` -> `check-c.log` (final), `check-b.log` (axis rules; its pattern rows are from before the mend); `check2.py` -> `check2.txt`, `check2-twin.txt`; `check3.py` -> `check3.txt`)

Flat check (20,000 points, 60 steps; Mandelbrot / c = -1 / rabbit / Siegel): **0 / 0 / 0 / 0 differing verdicts for
every rule in the table.** Lift test (flat-inside points lifted by a millionth): all stay (2,920 of 2,920 and 2,716
of 2,716) for every rule EXCEPT `prod` (0 stay: a film) and `spin` on the rabbit (0 of 2,716 stay: a film).
(A first run of the pattern rules showed 2,960 differing for c = -1: a NaN when an orbit fell on 0 exactly. Mended.)

| rule | c = -1: inside / half-turn change / scrap | rabbit: inside / half-turn change / scrap | stretches at the meeting point (flat stretch 1.236 / 1.107) |
|---|---|---|---|
| oneplane | 0.0253 / 0.0 % / 0.2 % | 0.0158 / 0.0 % / 0.9 % | all three equal the flat stretch |
| along | 0.0228 / 2.5 % / 1.4 % | 0.0566 / 62 % / 0.4 % (one lump) | equal (in the limit of no height) |
| spin | = quaternion square: 0 of 200,000 verdicts differ (also c = -0.75: 0) | nothing inside (0 of 200,000; quaternion square 10,477) | - |
| prod | nothing off the plane | nothing off the plane | - |
| axis_every | 0.0228 / 2.5 % / - | 0.0203 / 31 % / - | equal |
| axis_once | 0.0245 / 3.2 % / 0.4 % | 0.0159 / 20 % / 1.2 % | equal |
| m4 (not turned) | 0.0199 / 0.0 % / - | **0.0826** / 0.0 % (a lump) | equal (in the limit of no height) |
| face4 | 0.0199 / 0.0 % / 4.7 % | **0.0175** / 0.0 % / 14.4 % | equal |
| tri (not turned) | 0.0548 / 48 % (one lump) | 0.0277 / 92 % | c = -1: 1.236, 1.236, **0.647**; rabbit: equal |
| face_tri | 0.0284 / 31 % / 1.8 % | 0.0277 / 92 % / 8.2 % | equal for all five c tried |
| twin_tri | 0.0229 / 0.0 % / 1.4 % | 0.0151 / 0.0 % / 3.8 % | equal for all five c tried |

"inside" = share of the box 3.6 x 2.8 x 2.8 that never leaves in 40 steps (150,000 points). "half-turn change" =
share of the inside whose verdict changes when the start is turned half-way round the upright axis (the flat picture
does not change under that turn): the lopsidedness as a number. "scrap" = share of the inside in pieces smaller than
0.2 % of the whole on a 110^3 grid (pieces = blocks joined by faces). Kept from 40 to 90 steps: 99.6 to 100 % for
c = -1 and the rabbit for every rule in the table (one plane's rabbit 99.2 %); Siegel disc under `twin_tri` 91.8 %,
under `face_tri` 93.2 % (a slow leak there).

Other numbers:
- `spin` turned round the x-axis: c = -1 changes 0.000 % (it is spun), Mandelbrot solid 0.27 %.
- The triangle pattern within 28 degrees of its corner, all round, equals the quaternion square about that corner's
  line to 1.5e-6 degrees (in the flat plane up to 60 degrees, in the upright plane up to 44) (`check3.txt` a).
- The seam of `twin_tri` (the upright plane through 0 square to the line 0 - a): the two sides are sent 0 / 0.8 / 3 /
  12 / 27 / 90 / 140 degrees apart at height angles 0 / 5 / 10 / 20 / 30 / 45 / 60. A real tear off the flat plane.
- Sideways stretch of the blended patterns (2 = keeps shapes when the length is squared): m = 4, t = -0.2 at
  longitude 0: 3.6 to 4.4 between height angles 10 and 40; at longitude 45: 0.2 to 0.8 between 10 and 30.
  m = 6: up to 7.5. m = 3: 0.6 to 3.5. (`check-b.log`)
- Junction count (`junction.py` -> `junction.txt`), see section 4 (a).

## 3. What the pictures show [S] (all opened)

`sheet.png` (eye (0.45, 0.5, 1)) and `sheet-top.png` (eye (0.2, 1, 0.35)): rough solids, c = -1 and the rabbit, 160
blocks deep (last row 170), 28 steps; rows one plane, along, `spin`, `axis_once`, `face4`, `face_tri`, `twin_tri`.
- `spin`: c = -1 is stacks of rings round the x-axis (the quaternion square); the rabbit tile is empty.
- `axis_once`: c = -1: the middle body carries a handful of round buds off the flat plane, the other bodies none.
  Rabbit: smooth separate bodies, the middle one with a few small pointed buds; otherwise one plane's rabbit.
- `face4`: c = -1 a star: the row of bodies plus four long spindles standing out from the middle body, thorns all
  over. Rabbit: no lump any more (the unturned `m4` is one, `cuts-B.png` row 1), but a cloud of spindles and flakes.
- `face_tri`: c = -1 a row of SEPARATE bodies (unturned `tri`: one fused ribbed lump, `solids-tri-a.png`,
  `solids-tri-top.png`); the middle and left bodies are balls with small knobs all over, the right-hand bodies are
  sliced into shells: lopsided. Rabbit: ragged, ribbed, shells from above.
- `twin_tri`: c = -1 a symmetric row of separate round bodies, scratched skin, small thorny knobs all over, the flat
  picture's own buds on top and bottom. Rabbit: separate round bodies with a ribbed middle body and loose flakes
  floating round them. No big round body off the flat picture on either.
`solids-axis-a.png`: `axis_every` (rabbit: three separate bodies with a terraced skin, as round 22 found),
`axis_once`, `axis_cycle` (rabbit: separate but crusted all over: worse than `axis_once`, no better than
`axis_every`). One eye only for `axis_every` and `axis_cycle`.
Cuts (60 steps): `cuts-A.png` (one plane, along, the three axis rules, `spin`, `prod`: the last two empty off the
plane for the rabbit, `prod` for c = -1 too); `cuts-B.png` (`m4`, `face4`, `m4m`, `face4m`, `face3`, `face3m`);
`cuts-C2.png` (`tri` against `face_tri`, four c); `cuts-D2.png` (`face_tri` against `twin_tri`, four c: for c = -1
and c = -0.75 the upright cut of `twin_tri` is a symmetric row of bodies with buds, close to the flat picture;
the rabbit's three cuts are clean; the Siegel disc is splinters under both).
Mandelbrot solid, cuts only (`mandel-M.png`, `mandel-N.png`): `axis_once` is one plane's cushion exactly; `face_tri`,
`twin_tri`, `face4` are one plane's cushion with a ragged edge plus a tall spike standing on c = 0 (the upright
axis, on which these rules act like a one-line rule t -> s - t^2; reasoned). No buds off the flat plane in any.

## 4. What I can say with reasons

**(a) The look of "two planes" / "along" cannot exist for the rabbit, as an object. [R; the count is M]**
In the two-planes solid of c = -1 every body carries its bulbs in 4 directions about its own line (the line from
its fastening point through its middle); under along, 8. That works where TWO bodies meet, because both lie on one
line and a turn about it moves neither. Where q bodies meet they stand in a flat ring, 360/q apart. If the set of
bodies at that point must be kept by a turn of 360/N about EACH body's own line, the turns generate a group, and
among the cases counted (q = 2 to 5, N = 2, 3, 4, 8) it closes only for N = 2 (any q), q = 2 (any N), and q = 4
with N = 4 (six directions, an octahedron); that agrees with the list of finite groups of turns (two four-fold
lines exist only a quarter turn apart). Count of directions forced (`junction.txt`):
q = 3, N = 4: 3, 9, 21, 45, 93, 189, 381, 765, ... (closest pair 0.8 degrees apart); q = 3, N = 8: 3, 9, 27, 81,
237, 693, 2025, ...; q = 2: stays 2; q = 3, N = 2: stays 3. Bodies of real width cannot stand 0.8 degrees apart.
So for the rabbit (q = 3) only N = 2 is possible: bulbs on both sides in the flat plane, i.e. one plane's look.
This is stronger than (W-b): it does not ask for a second flat plane, and it rules out every rule at once.
What is NOT ruled out: bulbs fastened elsewhere on each body, each junction a flat ring of three in a tilted
plane. That is what the rules without a line (cone rules, pillows) try, and what `face4`, `face_tri` are.

**(b) The hidden turn. [R]** In the flat plane, "square, then turn by an angle, then add c" is nothing new: z^2 is
round, so the turn can be moved into c. In space a square with a pattern on it (corners, extra copies) is not round,
so "square, then a 3D turn R, then add c" is a different rule for every R: the 3D family is v -> R S(v) + c with
R a rotation, i.e. a unit quaternion. Keeping the flat picture exact leaves the turns about the upright axis:
R = Rot_z(e), with the pattern itself turned by e (Rot_z(2e) G Rot_z(-e)). Every fixed rule so far silently took
e = 0. The flat picture offers a choice: e = arg a(c), "the special direction faces the meeting point". This is
where a quaternion enters honestly: as the turn that goes with c, not as the square.
Evidence that e matters [M, S]: `m4` -> `face4` on the rabbit: inside 0.0826 -> 0.0175 (lump gone); `tri` ->
`face_tri` on c = -1: upright stretch at the meeting point 0.647 -> 1.236, inside 0.0548 -> 0.0284, one lump ->
a row of bodies.

**(c) Section 4 of the briefing is wrong on one point. [M, S]** "Triangle pillow: c = -1 fused along the whole
x-axis by its nature". It is fused because the pattern was not turned: unturned, the meeting point of c = -1 sits on
a branch direction of the pattern (upright stretch 0.647 < 1: lifted points are held); turned by c it sits on a
corner, where the pattern is the quaternion square about the line 0 - a and the step is a plain enlargement
(1.236 three times). For the rabbit the unturned pattern happens to have a corner at 120 degrees and the meeting
point is at 119.9: that, not the rabbit, is why `tri` kept the rabbit's bodies apart. (W-e) should read: every such
rule makes a lump at the c whose meeting point faces its weak side UNLESS the rule is turned with c.

**(d) Why `spin` is the quaternion square, and why its rabbit is empty. [T for the first, R for the second]**
For c on the x-axis every plane through the x-axis is kept: the lift of a point in it is a turn about the
normal of that plane, squaring keeps the normal, adding c keeps the plane, the shortest turn is again
about that normal. So the carried quaternion never leaves the family the quaternion square uses (measured: 0 of
200,000 differ). A carried quaternion that knows only the x-axis must give rings; to do otherwise it must be told
about the flat plane by a rule for its start, and that rule is a choice. For the rabbit the orbit passes close to 0
once per round; the direction of a tiny point is noise, the shortest turn to the next point magnifies any lift off
the plane by about 1/|v| there, so every lifted orbit is thrown out (lift test 0 of 2,716).

**(e) Why `prod` is a film. [T]** With heights adding in Mercator fashion, a point at small height h above z is sent
to height h (|z - a| + |z + a|) >= 2 |a| h, and 2|a| is the flat stretch at the meeting point, above 1 for every c
outside the main body. Heights grow at every step, even over the middle of a body where the flat rule shrinks.

**(f) Letting the length follow the sideways stretch (door (ii), side test) makes it worse. [S]** `m4m`, `face4m`
(`cuts-B.png` rows 3, 4): the row of c = -1 fuses into one spiky lump in the upright cut, the rabbit swells
(inside at 30 steps 0.0185 -> 0.0409; c = -1 0.0193 -> 0.0341). Reasoned cause: the blended patterns have a sideways stretch of 3.5 to 4.4 already 10
degrees off the flat plane, so the length law changes violently right beside the flat picture. Cuts only; no solid.

**(g) Why the bulbs of the copy rules are spindles and why this corner cannot mend that. [R, with M for the
stretch]** A rule that is not lopsided (same after a half turn) lays every extra copy round an even number of times,
so beside the copy it spreads directions sideways by more than 2 (measured 3.5 to 7.5) while the length is only
squared: a body there is carried home sideways faster than outward and comes out long and thin (the spindles of
`face4`; round 24's "hairy stars"). The copy laid once round at the right height has stretch 2 but is three-fold
(lopsided) and needs a violent blend. Even spacing has stretch 2 everywhere but needs corners. Turning by c
chooses where these faults point; it does not remove one.

**(h) `twin_tri` is, near the line 0 - a, the quaternion square about that line [M, 28 degrees all round], and
elsewhere the even-spacing pattern.** For c on the x-axis the upright plane through the x-axis is squared like the
flat one within 44 degrees of the axis, which is why its upright cut looks like the flat picture [S]. It has no
tear on the diagonal planes (two planes has) but one on the plane square to the line 0 - a [M]. The scratched skin
and the rabbit's flakes may come from that seam or from the squeeze of the triangle layout (round 24 measured a
median squeeze of 5.7 for it); I did not separate the two.

## 5. Each rule against the user's tests

| rule | 1 exact flat picture | 2 count from the power | 3 no shards / smear / rings | 4 blown-up body with round bodies on it, every c | 5 principled |
|---|---|---|---|---|---|
| spin | yes | yes | NO: rings for c on the x-axis; rabbit has no body | no | yes |
| prod | yes, but a film (no body) | - | - | no | yes |
| axis_once | yes | NO (4 pages are written in) | yes (scrap 0.4 / 1.2 %) | c = -1: middle body only; rabbit: almost nothing | NO (special first step) |
| axis_every, axis_cycle | yes | NO | NO (terraced / crusted rabbit) | no | half |
| face4 | yes | NO (m = 4 and t are dials) | NO (spindles; 14 % scrap on the rabbit) | no | half |
| face_tri | yes | yes (4 coverings = power squared, even spacing) | NO (shells, lopsided 31 % / 92 %, scrap 8 %) | no | yes |
| twin_tri | yes | yes | NO (scratched skin, thorns, 3.8 % loose flakes on the rabbit, Siegel disc in splinters, a seam) | NO: bodies stay separate and round, but what grows on them off the flat picture is small thorns | mostly (the half-turn fold is natural for z -> -z but is a tear) |

## 6. Files

`rules.py` (all rules), `best.py` (`rule()` = `twin_tri`), `check.py`, `check2.py`, `check3.py`, `junction.py`,
`draw.py` (cuts, solids, Mandelbrot cuts). Logs: `check-b.log`, `check2.txt`, `check2-twin.txt`, `check3.txt`,
`junction.txt`, `solids-*.log`, `sheet-*.log`. Pictures: `sheet.png`, `sheet-top.png` (the two to look at),
`solids-tri-a.png`, `solids-tri-top.png` (unturned against turned triangle), `solids-twin-a.png`,
`solids-twin-top.png`, `solids-axis-a.png`, `cuts-A.png`, `cuts-B.png`, `cuts-C2.png`, `cuts-D2.png`
(`cuts-C.png`, `cuts-D.png` are the same as one wide strip), `mandel-M.png`, `mandel-N.png`.

## 7. Plain lines that may be told (user's words)

- A quaternion that rides along with the orbit and is turned as the point is turned gives, for c = -1, exactly the
  flat picture spun round the x-axis, and for the rabbit nothing at all above or below the flat picture.
- In 3D there is a dial the flat picture does not have: after squaring, the whole thing can be swung round the
  upright axis before c is added. In the flat plane that changes nothing; in 3D each setting is a different shape.
- Setting that dial from c, so that the rule's special direction points at the place where the bodies meet, takes
  the lump away. It does not make the skin smooth.
- At c = -1 two bodies meet at each meeting place, in a row. In the rabbit three meet, in a flat ring. Swing that
  ring a quarter turn about one body's own line and the other two land above and below; each of those has its own
  line to be swung about, and so on without end, until the copies overlap. So the rabbit cannot have the look that
  two planes and along give c = -1. No rule can change that.
- The nearest thing found here: the bodies stay separate and round for c = -1 and for the rabbit and nothing leans
  to one side, but what grows on them away from the flat picture is small thorns, and loose flakes float round the rabbit.

## 8. Not done, and weak spots

- Solids are 160 to 170 blocks deep at 28 steps, two eyes for seven rules, one eye for `axis_every` / `axis_cycle`.
  No finer blocks, no solids at more steps (only the 40 against 90 step counts), no c tilted out of the flat plane.
- c = -0.75 and the Siegel disc: cuts only. The 1/4 bud: numbers only (`check2.txt`).
- The length-follows-stretch test (f): cuts only, one way of flooring the power (never under 2, never over 8).
- Mandelbrot solids: cuts at 0, 45, 90 degrees only; the reason given for the spike is reasoning.
- `axis_cycle` reads the cycle and the start point's body off the flat orbit; for a c with no cycle, or for the
  Mandelbrot solid (c differs from point to point), it falls back to `axis_every`. It was not worth mending.
- (a) is an argument about turns that keep the set of bodies at a meeting point; it assumes the copies are as wide
  as the bodies they copy. It does not cover looks in which bulbs are fastened elsewhere on a body.
- (h): the cause of `twin_tri`'s rough skin (seam or layout squeeze) is not separated. A smoother triangle layout
  is the pillow section's business; the turn by c and the fold apply to whatever layout they find.
- "scrap" depends on the grid (bodies that touch at one point count as separate pieces; small real buds can fall
  under 0.2 %). One plane's own numbers (0.2 % / 0.9 %) are the floor to compare with.
