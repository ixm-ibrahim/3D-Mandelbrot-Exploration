# Round 21, agent "span": planes that the orbit makes, not through the x-axis

Every statement is marked **measured** (a number I computed), **seen** (in a picture I looked at) or **reasoned**.

## Verdict in plain words

Nothing in this family passes. 21 rules were tried; all are exact on the flat page; none has a basilica with round
buds off the flat page that are not rings together with a rabbit that has separate bodies.

Taking the user's words literally ("follow whatever new plane is made during the orbit") runs into one plain fact:
**for the Mandelbrot solid no new plane is ever made.** The orbit of 0 goes c, then (square of c) + c, and so on. If
each point is squared inside a plane it spans with c or with an earlier point, the square stays in that plane and c
lies in it too, so the next point is in the same plane again. The orbit never leaves the first plane it gets, and
which plane that is, is not made by the orbit at all: it is whatever the rule says for the very first squaring,
where the plane is not defined (c with c, or c with nothing before it).
- first plane = the point's own sheet through the x-axis: the solid is exactly the flat set spun (Claim S holds).
- first plane = the plane through the point nearest the flat page: not spun, but still the flat set swept along
  curves, with a paper-thin half-disc flange. No round buds.

The planes can only be made to move by something that is not the orbit's own: a carried plane that starts as the
flat page and lags behind, or a first guess made with the one-plane rule on the flat page. Those give, off the
flat page, smooth blobs without buds, or lumps with fins.

For Julia sets: squaring a point inside ANY plane through it is the lathe's mechanism with a movable axis, and it
makes rings, ribs and flanges in every variant. For c on the x-axis "the plane of the point and c" is exactly the
lathe.

## 1. The squaring (full definition)

A plane through 0 is kept as a unit normal n (n and -n are the same plane; every formula gives the same for both).

- **Real axis of a plane**: a = the direction in the plane nearest to +x = (e_x - n_x n) / sqrt(1 - n_x^2).
- **Square inside the plane** (the point v lies in it): double the angle of v from a, square the length:
  **Sq(v) = 2 (a.v) v - |v|^2 a** (the mirror image of a in the line of v, times |v|^2).
  Coded as: al = a.v; b = v - al a; be = |b|; result = (al^2 - be^2) a + 2 al be (b / be). For a = (1,0,0), z = 0 this
  is complex squaring to the last bit.
- Identity (**measured**, 100,000 random points and planes, largest difference 1.2e-12 of |v|^2):
  Sq(v) = (L(v) + |v|^2 n_x n) / sqrt(1 - n_x^2), L = the lathe (x^2-y^2-z^2, 2xy, 2xz). So: the square inside a
  plane is the lathe's square pressed flat into the plane and stretched back to full length.
- **One-plane rule about a plane n** (the point need not lie in it): frame a, b = n x a, n; coordinates
  (v.a, v.b, v.n); apply P(x,y,z) = f (x^2-y^2, 2xy, 2 r z), f = r^2/(r^2+z^2); put back. For a point in the plane it
  equals Sq (**measured**, 3.7e-14).

Planes used when the made plane is not defined:
- **page**: the plane through the point nearest to the flat page, n = (-xz, -yz, x^2+y^2) / (rho r), rho = sqrt(x^2+y^2)
  (it holds the point and the level direction (-y, x, 0)); on the z-axis: the x-z plane.
- **lathe**: the point's own sheet through the x-axis, n = (0, -z, y) / sqrt(y^2+z^2).
- **keep**: the carried plane, turned the least that makes it hold the point: n - (n.v) v/|v|^2, made one long.
"Parallel" means: sine of the angle between point and partner below 1e-9, or one of them 0.
"Move the share lam toward the made plane m": n <- unit((1-lam) n + lam s m), s = sign(n.m) (so that m's nearer
normal is used). Carried state of every rule: n (starts (0,0,1), the flat page), the point before (starts 0), a
carried real axis (starts +x, read by prev_axis only). Code: `out/r21/span/myrules.py`, `RULES`, `get(name)`.

## 2. The rules

In-plane rules (point squared inside the made plane):
| name | partner of the point | where undefined |
|---|---|---|
| c_lathe | c | own sheet |
| c_page | c | plane nearest the flat page |
| c_Pfirst | c | the very first squaring of an orbit is the one-plane rule on the flat page; later: page |
| prev_lathe | the point before | own sheet |
| prev_page | the point before | plane nearest the flat page |
| prev_keep | the point before | the plane it had, tilted to hold the point |
| prev_Pfirst | the point before | first squaring = one-plane rule on the flat page |
| prev_axis | the point before | page; and the real axis is the direction in the new plane nearest to the real axis of the step BEFORE (starts +x) |
| prev_lag50in | the point before | carried plane moves half way to the made plane, is then tilted to hold the point; squared inside |
| guessP | P(v), the point's image under the one-plane rule on the flat page (no memory) | page |
| guessPc | P(v) + c | page |
| guessN | image of v under the one-plane rule about the CARRIED plane | keep |
| guessNc | that image + c | keep |

One-plane rule about a carried plane that does not hold the point:
| name | what the carried plane does before each squaring |
|---|---|
| c_lag10, c_lag25, c_lag50 | moves 0.1 / 0.25 / 0.5 of the way to the plane of the point and c (undefined: stays) |
| prev_lag10P, prev_lag25P, prev_lag50P | moves 0.1 / 0.25 / 0.5 of the way to the plane of the point and the point before |
| prev_delay | the point is squared about the plane of the two points BEFORE it (plane updated after the squaring) |
| roll | the carried plane is turned by the least turn that takes the direction of the point before into the direction of this point: n <- n - s (s.n)/(1+p.q) + 2 (p.n) q, p, q the two unit directions, s = p+q; stays where p is missing or opposite |

For c on the x-axis c_lag is the scout's lag idea (the made plane is the point's own sheet), blended on the normal
instead of on the doubled angle.

## 3. Numbers (`checks.txt`, `benchnum.txt`)

flat_check: **all 21 rules: 0 of 40,000 verdicts differ** (Mandelbrot, basilica, rabbit, Siegel), strays 0. **measured**

| rule | turned: M differs | turned: basilica differs | basilica volume 30/80 steps | rabbit volume 30/80 | M volume 30/80 | orbit of 0 off its first plane (max) |
|---|---|---|---|---|---|---|
| c_lathe | 0.00% | 0.00% | 3.24/3.24 | 4.84/4.08 | 7.95/7.32 | 2.9e-12 |
| c_page | 3.46% | 0.00% | 3.24/3.24 | 4.84/4.08 | 9.43/8.69 | 1.7e-12 |
| c_Pfirst | 1.77% | 0.52% | 3.07/3.07 | 3.90/2.81 | 6.03/5.72 | 7.2e-13 |
| c_lag10 | 1.49% | 0.33% | 2.93/2.92 | 2.54/2.37 | 1.98/1.75 | 3.0 |
| c_lag25 | 1.75% | 0.23% | 2.74/2.74 | 2.69/2.30 | 2.54/2.45 | 2.9 |
| c_lag50 | 2.16% | 0.25% | 2.74/2.74 | 3.30/2.82 | 3.91/3.75 | 3.0 |
| prev_lathe | 0.34% | 0.00% | 3.24/3.24 | 2.73/2.31 | 7.78/6.23 | 7.1e-02 |
| prev_page | 3.72% | 1.43% | 3.98/3.97 | 3.27/2.75 | 9.32/7.78 | 7.3e-02 |
| prev_keep | 3.73% | 1.43% | 3.98/3.97 | 3.27/2.75 | 9.32/7.76 | 7.3e-02 |
| prev_Pfirst | 2.18% | 1.06% | 3.53/3.53 | 3.08/2.45 | 5.90/4.69 | 6.8e-02 |
| prev_axis | 3.48% | 1.82% | 2.94/2.88 | 3.84/2.49 | 9.43/8.64 | 6.3e-02 |
| prev_lag50in | 3.73% | 1.39% | 3.95/3.95 | 3.82/3.31 | 9.35/7.93 | 4.3e-02 |
| prev_lag10P | 2.03% | 0.80% | 3.55/3.48 | 2.20/0.37 | 2.89/2.77 | 3.0 |
| prev_lag25P | 1.98% | 1.47% | 4.32/4.28 | 1.25/0.01 | 3.84/3.54 | 2.9 |
| prev_lag50P | 1.59% | 1.80% | 4.20/4.20 | 0.23/0.00 | 4.18/3.72 | 3.0 |
| prev_delay | 1.01% | 0.78% | 2.60/2.60 | 0.00/0.00 | 3.27/2.55 | 3.0 |
| guessP | 4.58% | 1.99% | 4.27/4.27 | 5.92/5.79 | 10.02/8.92 | 3.0 |
| guessPc | 3.26% | 2.39% | 4.58/4.58 | 0.56/0.01 | 7.65/6.65 | 2.9 |
| guessN | 4.43% | 1.81% | 5.24/5.24 | 3.38/1.80 | 10.32/8.71 | 9.8e-06 |
| guessNc | 5.29% | 1.14% | 3.92/3.92 | 1.60/1.20 | 10.43/8.91 | 8.2e-02 |
| roll | 5.15% | 4.98% | 3.81/3.22 | 5.25/4.96 | 8.17/7.81 | 2.9 |
| bench along | 1.52% | 0.25% | 2.71/2.71 | 6.75/6.66 | 7.81/7.20 | |
| bench oneplane | 1.23% | 0.34% | 2.99/2.99 | 1.95/1.89 | 1.58/1.44 | |
| bench lathe | 0.00% | 0.00% | 3.24/3.24 | 6.23/6.10 | 7.95/7.32 | |

Volumes are the share of a box that is inside, in percent; a drop from 30 to 80 steps is a slow leak (dust, thin
layers). "Turned" = `M.spun_check`: 0 means the same from every side of the x-axis.

## 4. What each choice costs where the plane is not defined (`tears.txt`, **measured**)

1. **Plane square to the x-axis** (no direction in it is nearest to +x). No convention helps: just beside such a
   plane the real axes point every way. For c = i (c square to the x-axis) and partner c, this is the whole plane
   x = 0, and the square jumps by 2.000 |v|^2 across it (thrown to the opposite point). A tear.
2. **Point parallel to its partner.** On a small circle round the line of c (rabbit, partner c) the squares differ
   by up to 1.70 |v|^2, the same at radius 1e-3 and 1e-6: a whirl along the whole line of c. The convention only
   decides the value ON the line. Harmless only on the x-axis, where every plane gives the same square.
3. **First plane by convention.** "Nearest the flat page" has a whirl of 2.000 |v|^2 on the z-axis. "Own sheet"
   has no jump (6.7e-6 at radius 1e-6) but brings the lathe's rings.
4. **Moving only part of the way.** A plane has two ways to turn toward another; where the made plane stands
   square to the carried one they are equally short, and the rule jumps: median 1.23 / 0.61 / 0.21 |v|^2 for
   lam = 0.5 / 0.25 / 0.1 (c = -1, across the x-z plane).
5. **Two consecutive points when the orbit comes to rest.** See claim 6 below: the plane vanishes exactly where an
   orbit settles on one point.

## 5. Claims

1. **For c on the x-axis, "the plane of the point and c" is the lathe.** Reasoned: the plane of the point and a
   point of the x-axis is the point's own sheet. Measured (`identity.txt`): c_lathe, c_page, prev_lathe against the
   bench lathe, 0 of 60,000 verdicts differ for c = -1, -0.75, -1.7549. Seen (`julia-c.png` rows 1-2): the ringed
   basilica, San Marco, airplane. prev_page is NOT the lathe (619 of 60,000 differ for c = -1): its first plane does
   not hold the x-axis, and its rings come out sheared (`julia-prev.png` row 2), not gone.
2. **Julia set of "the point and c", c off the x-axis: a fan of flat Julia sets round the line of c.** Reasoned:
   the orbit never leaves the plane of its start point and c; in it, it is the flat orbit under z^2 + gamma, where
   gamma has the length of c and the angle between c and the plane's real axis. Measured (`theory.txt` part 2): 0 of
   40,000 verdicts differ for the rabbit, the Siegel disc and a c off the page; gamma's angle runs from 99.3 to
   180 degrees for the rabbit. Seen (`fan-rabbit.png`): planes turned 0, 30, 50 degrees from the page hold rabbits,
   60 and 75 hold dust (gamma has left the flat Mandelbrot set), 90 holds a basilica-like set (gamma = -0.755); cuts
   across the line of c are bow-ties and blades. So: rings and wedges round the line of c, with dust between.
3. **The orbit of 0 never leaves its first plane** whenever each squaring is done inside a plane spanned by the
   point and c, an earlier point, or an image that lies in the same plane. Reasoned (above). Measured: largest
   distance from the first plane 2.9e-12 (c_lathe), 1.7e-12 (c_page), 7.2e-13 (c_Pfirst).
4. **Then the Mandelbrot solid is the flat set swept: { c : |c| e^(i theta(c)) in the flat set }**, theta(c) = the
   angle between c and the real axis of its first plane. Measured (`theory.txt` part 1): 0 of 40,000 verdicts
   differ, for c_lathe (theta = angle from +x) and for c_page (tan theta = |y| r / (x rho)). A bud of the flat set
   sits at one length and one angle, so in the solid it becomes a band along a level line of theta: a ring or a
   rib, not a ball (reasoned; seen in `sweep-c_page.png`, `mandel-c.png`).
5. **Claim S holds in this family, and the conventions decide everything** (briefing's question):
   - own sheet: the spun solid exactly (turned: 0.00%; every cut along a sheet is the flat set; `mandel-c.png` row 1).
   - nearest the flat page: not spun (3.46%), but swept. Seen (`mandel-c.png` row 2, `sweep-c_page.png`): cuts at
     22.5 and 45 degrees are the flat set mildly squeezed; the cut along the x-z plane is a half-disc of radius 2 on
     the left and of radius 0.25 on the right (the whole real line of the flat set laid onto that plane): a
     paper-thin flange; pinches on the z-axis; the cut across at x = -1 is a tall spindle instead of a disc.
   - first squaring = one-plane rule on the flat page: not spun (1.77%); the orbit is still flat but does not start
     where the flat rule would start it; cuts off the page are deformed blobs, the buds worn down to bumps at 22.5
     degrees and to spikes at 45 and 90 (`mandel-c.png` row 3).
   Every rule here that is not spun uses the flat page somewhere (convention, start of the carried plane, or the
   guess). prev_lathe uses none and is spun in exact arithmetic; its 0.34% is the damage of claim 6.
6. **"The point and the point before" loses its plane where the orbit comes to rest.** Reasoned: two points that
   coincide span no plane; just before, the plane hangs on the tiny difference of two nearly equal points and any
   rounding error is blown up by 1/sine of the angle between them, step after step. Measured (`rest.txt`): of the c
   in the heart-shaped main body of the swept set (orbit comes to rest) the rule throws out 16.6% (prev_lathe),
   13.6% (prev_page), 13.7% (prev_keep); of all other c 0.1%; c_page 0. The loss grows with the steps (prev_keep:
   1.5% of the inside lost at 30 steps, 12.6% at 120, 14.5% at 240). `theory.txt` part 3: of the orbits of 0
   that are still within distance 3 after 40 steps, 44% are more than 0.001 off their plane, with no push at all
   (c_page: 0%); a push of 1e-9 changes nothing, so it is the rest points that do it, not a general drift. Seen (`mandel-prev.png`, `mandel-lag.png`
   rows 1-2): speckled bites on the right of the main body in the cuts at 22.5 and 90 degrees. "Keep the plane you
   had" does not cure it. Carrying the real axis as well (prev_axis) cuts the loss to 0.7%, but its Julia sets
   have fins and dust (`julia-prev.png` row 4).
7. **Squaring inside a plane through the point always carries the lathe's ring mechanism.** Reasoned: all points
   that stand square to their own real axis (a whole surface) are sent onto the negative real ray (a line); what
   sits on that ray is pulled back to surfaces: rings, ribs, flanges. With a fixed axis they are round rings (the
   lathe); with an axis that moves with the point they are sheared and bent, not removed. Seen: every in-plane
   rule shows them (`julia-c.png` rows 1-3, `julia-prev.png`, `julia-lag.png` rows 1-2, `julia-guess.png`).
8. **The one-plane rule about a lagging made plane runs from the one-plane rule to the in-plane rule and has no
   good middle.** Seen (`julia-extra.png`, `julia-c.png` row 4, `cuts-c_lag10.png` against `cuts-oneplane.png`):
   at 0.1 the basilica is the one-plane rule's to the eye (cuts at 11.25, 22.5, 33.75, 90 degrees: smooth bodies,
   buds only on the flat page); the rabbit has separate bodies, a little fatter, with a few more lumps and thin
   streaks at the necks. At 0.25 the rabbit's bodies have merged into one ridged lump; at 0.5 a layered lump.
   With the point before as partner the rabbit turns to dust (volume 2.20% -> 0.37%, 1.25% -> 0.01%,
   0.23% -> 0.00% for 0.1, 0.25, 0.5). Mandelbrot solids (`mandel-extra.png`, `mandel-lag.png`): off the flat page
   thin blades or smooth teardrops, no buds.
9. **guessP has two exact planes in its Mandelbrot solid**: the flat page and the x-z plane (seen: the cut turned
   90 degrees in `mandel-guess.png` row 1 is the flat set; reasoned: the one-plane rule sends the x-z plane into
   itself, so point and guess span it). Between them: arcs and fins (cut at 45 degrees), a squarish cut across
   with four spikes. Its Julia sets are lumps with flanges and dusty edges (`julia-guess.png` row 1).
10. **roll** (plane turned along with the point): shells and one big lump, no bodies (`julia-extra.png` row 4);
    Mandelbrot solid a big lump with a frayed spike (`mandel-extra.png` row 4).

## 6. Pictures (all looked at)

- `julia-c.png` (320x240 blocks, 28 steps), `julia-prev.png`, `julia-lag.png`, `julia-guess.png`, `julia-extra.png`,
  `julia-bench.png` (250x188 blocks): six Julia sets per rule.
- `mandel-c.png`, `mandel-prev.png`, `mandel-lag.png`, `mandel-guess.png`, `mandel-extra.png`, `mandel-bench.png`:
  cuts at 0, 22.5, 45, 90 degrees, one cut across, rough solid.
- `fan-rabbit.png`: claim 2. `sweep-c_page.png`: claims 4 and 5, against the lathe, three eye positions.
- `cuts-c_lag10.png`, `cuts-oneplane.png`: basilica and rabbit, cuts at 0, 11.25, 22.5, 33.75, 90 degrees and
  across, solids at 60 steps from three eye positions.
- Numbers: `checks.txt`, `benchnum.txt`, `theory.txt`, `identity.txt`, `tears.txt`, `rest.txt`.
- Scripts: `myrules.py`, `checks.py`, `sheets.py`, `theory.py`, `identity.py`, `rest.py`, `detail.py`, `benchnum.py`, `timing.py`.

## 7. Ranking inside the family (none passes)

1. **c_lag10**: the nearest to a clean result, because it is nearly the one-plane rule. Rabbit with separate
   bodies; basilica buds only round the flat page; Mandelbrot solid a thin blade. No gain over the one-plane rule
   that I could see, and a small leak (rabbit 2.54% -> 2.37%; one-plane 1.95% -> 1.89%).
2. **c_lag25**: basilica as above; rabbit already one ridged lump (2.69% -> 2.30%).
3. **c_page**: the literal reading, fully understood (claims 1 to 5): lathe for c on the x-axis, fan with dust for
   the rabbit, swept Mandelbrot solid with a flange.
None beats `along` on the basilica (no buds off the flat page), and only c_lag10 has what `along` lacks (separate
rabbit bodies), which the one-plane rule already has.

## 8. Not done

- No close-up of skin detail beyond the 60-step solids of c_lag10; no rule earned one.
- Lags below 0.1 and between 0.1 and 0.25 were not scanned; the two ends bracket them.
- The loss in claim 6 was measured in ordinary double precision only; "spun in exact arithmetic" for prev_lathe is
  reasoned, not computed with longer numbers.
