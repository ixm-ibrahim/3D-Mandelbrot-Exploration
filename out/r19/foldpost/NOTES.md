# Round 19, foldpost: fold the one-plane ANSWER with sphere inversions

No rule here gets through the gates. Six rules built, four tested with iteration, all fail; two closed-form
results say why the kind fails as a whole. Every statement is marked measured / seen in the picture / reasoned.

Files: `folds.py` (construction and the seconds-long predictor), `scan1.py` + `scan1.txt` (one fold, closed form),
`scan2.py` + `scan2.txt` (two folds), `screens.py` + `screens.json` + `logs/screens.log` (rule checks and
direction tables of all six rules), `myrules.py` (the rules, prefix `f_`), `logs/` (closecut and stage-1 logs),
pictures `closecut-f_*.png`, `bench-f_*.png` (copies of the bench's own output).

## The construction, in plain words

The one-plane rule turns each direction into an answer direction (longitude doubled, height above the flat plane
"Mercator-doubled"). A fold takes a round cap of ANSWER directions and mirrors it in its own rim, like folding a
flap of paper over its crease: no tear, angles kept, handedness reversed. Stretch of a fold at a point that sits
at angle t_in from the cap centre and lands at t_out: sin(t_out) / sin(t_in) (closed form; checked against the
rule code to 2 decimals, measured).

## Result 1 (one fold): closed. The surplus has nowhere good to go.

Reasoned, then measured on three rules:

- A cap mirrored in its rim lands on EVERYTHING outside the cap. So one fold makes an extra copy of every flat
  direction, not just of the bud direction -x: the long-arm direction +x always gets extra copies too (measured:
  the sphere is covered -2 times, 39 to 64 % of directions land mirror-reversed; every flat direction tested has
  2 extra sources above the plane and 2 below).
- Asking that the extra copy of -x arrives with stretch exactly 2 fixes the cap radius for each cap centre
  (`scan1.txt`, table A). The cap then has to sit 2 to 30 degrees off straight-up, leaning toward +x, and:
  - either its rim comes within 2.4 to 13 degrees of the flat plane above +x and cuts the big bodies of the row
    (f_one60: crease 2.5 degrees above +x), 
  - or the extra copies of +x arrive with stretch 5.0 to 11 (f_one80: 5.04 at latitude 43; f_one85: 5.48 at
    latitude 53): thin spindles where the flat picture has its biggest bodies.
- Is there a cap for which BOTH copies arrive with stretch 2? Scan of the whole family (`scan1.txt`, table B):
  only when the cap is nearly a half sphere with its rim 0.4 to 8 degrees from the flat plane. That is the
  degenerate end (a plain mirror image stacked directly on the flat picture). No real solution.
- The crushed pole (straight up) is sent to within 14 to 29 degrees of -x, exactly the bud line (f_one80: 13.7
  above -x; f_one85: 13.8 below -x; f_one60: 28.9 above). Moving it away costs the stretch-2 condition.
- Extra fault found, not predicted: the upright plane y = 0 is a mirror plane, so the rule keeps it; when the
  fold reaches the meridian above +x, a point straight above a neck can no longer leave upward (the fold sends
  steep answers back down). Result: a membrane of zero thickness standing on every neck in the plane y = 0.
  Measured on m_cap15 (round 17) and on f_pl10 below: the upright line above the touching point is inside the
  set for 1.15 to 1.7 units, where oneplane has 0. (Zero thickness is reasoned: the sideways stretch there is
  above 1 at every step.)

Test: f_one80 closecut (`closecut-f_one80.png`, seen): edges are clean, no fins or dust films, but the skin
carries pointed lens bodies (aspect about 2) and loose droplets; same character as m_cap15. FAIL at closecut.
f_one85: same kind of numbers (worst 10.5), picture not studied. f_one60 not iterated (crease 2.5 degrees from
the flat plane: fails the design target itself).

## Result 2 (two folds = a pleat): the surplus can be confined to the bud direction, but it cannot be round

A pleat: answers inside cap 1 are mirrored out; those that land outside a slightly larger cap 2 are mirrored
back in its rim. Three layers lie only over the ring between the two rims; elsewhere nothing is added. Put -x in
the ring and keep +x out of it.

Measured (screens.log): covers the sphere +2.00 times (as the flat rule), 5 to 12 % of directions mirrored,
+x has NO extra copy, -x has 4 extra copies above the plane (2 mirrored, 2 not) and 4 below, largest stretch
2.4 to 3.7 (round-17 scouts: 380 to 3400). The jump tests pass (largest distance / gap constant at 2.4 to 8.3
for gaps 1e-3 to 1e-6), both mirrors exact, flat plane exact to 4e-15.

Closed form for the pleat whose two rims pass through straight-up (so straight-up stays straight-up, the
harmless place): a copy of -x that lands from answer elevation e arrives with stretch
sqrt(W) (1 + W), W = tan(45 degrees + e/2), whatever the rims are. That is 2 only at e = 0:
2.39 at source latitude 5, 2.90 at 10, 3.60 at 15.5, 4.60 at 21, 9.1 at 35 (measured on the rule: 2.37, 2.80,
3.53; `scan2.txt`). So in this family an extra bud is rounder the closer it hugs the flat plane, and exactly
round only when it coincides with the flat bud.

Wider caps lower the stretch (cap 1 from 10 degrees above -x over the top to 40 degrees above +x: 2.24 and 2.50
at latitudes 9.8 and 18), but then the fold reaches the +x meridian and covers 77 % of all directions.

Tests:

| rule | prediction written before the run | closecut (eye) | stage 1 |
|---|---|---|---|
| f_cres10, rims through straight-up, 10 degrees above and below -x | clean skin; no membrane (the upright plane is untouched); extra buds at latitude 9 and 15, egg-shaped (stretch 2.8, 3.5) | clean: five of six tiles are a smooth line with one small kink (the crease), the sixth shows one separate smooth oval about 1.6 times longer than wide; no fins, no dust (`closecut-f_cres10.png`) | see below |
| f_pl10, wide pleat | nearest to round (2.24, 2.50); risk: terraces where the ring crosses the big bodies | rows of lemon-shaped buds meeting at pinch points, plus small teeth and a notch at the creases (`closecut-f_pl10.png`) | FAIL J2, J3, J4, J8: a terraced block. Membrane on the neck (upright line inside 1.15), 1 ring, 0 buds off the flat plane, roundness 0.70, 0.10, 0.27 (`bench-f_pl10.png`: plates and ridges, stepped outline in the cuts x = 0 and y = 0) |

f_cres10 stage 1 (measured; `bench-f_cres10.png`, `logs/stage1-f_cres10.log`): J1 pass, J2 pass (a ball of
radius 0.02 parts the bodies, upright line inside 0.000: the same numbers as oneplane, so no membrane, as
predicted), J3 pass (0 rings), J5, J6, J7 pass. **J4 FAIL**: 6 buds on the middle body, 0 off the flat plane (the
four new ones, size 0.044 against 0.103 for the flat buds, sit 9 and 15 degrees from the flat plane and the
bench counts them as in it). **J8 FAIL**: what comes off is round to 0.25, 0.47, 0.25 (oneplane: 0.76, 0.72,
0.73; under 0.45 = streaks). Seen in the picture: the one-plane basilica unchanged (a clean row of balls meeting
at points), with a small fan of about five short stubby fingers on each side of every body, all within about 20
degrees of the flat plane. Clean, in one piece, but not round bodies in a new direction. FAIL at stage 1.

## What limits the kind (reasoned from the two results)

1. One-plane stretch is below 2 everywhere off the flat plane, so an extra bud needs the fold to magnify by
   2 / (one-plane stretch) at that one spot. A fold magnifies by sin(t_out)/sin(t_in): mild magnification with a
   copy well away from the crease needs a cap that is nearly a half sphere (radius 64 to 84 degrees), and a half
   sphere cannot stay clear of the flat plane and of the big bodies' own directions.
2. Caps small enough to stay clear (radius at most 45 degrees if the upright plane above +x is to be left alone)
   magnify too much: stretch 2.4 to 3.5 for copies at latitude 5 to 15. The buds are eggs, less than half the
   size of the flat buds, and they crowd the flat plane.
3. Folding the answer never makes a bud at the top (straight up): the pole is crushed (stretch 0) before any
   fold acts, and a fold multiplies by a finite number.

## Not done

- No panel run (rabbit, dendrite): no rule got through stage 1, so the gates stop before it.
- f_one85, f_one60, f_pl5: screens only (f_one85 also closecut numbers); not iterated further.
- Cuts at 45 degrees and at the rules' own mid angles were not made (closecut's 22.5 and 11.25 only).
- Caps centred off the upright plane (pairs mirrored in y) were reasoned about, not scanned: the stretch formula
  is the same, so result 1 should carry over, but that is not measured.
- Three or more folds, and pleats that are not built from round caps, were not tried.
