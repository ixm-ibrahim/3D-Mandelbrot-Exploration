# Sphere inversions and the flat set

The question was: circle inversions can build the Mandelbrot set, so why can sphere inversions not build a
solid whose slice at z = 0 is that set? They can. The approach the lab used to call "Mercator" is that solid.
It was reached by a different road, and this note shows the two roads meet.

## In the plane

Let ωₖ (k = 0 … n − 1) be the n-th roots of 1, the corners of a regular n-gon on the unit circle. Then

    zⁿ = 1 + n / Σₖ ωₖ / (z − ωₖ)

Why it is true: zⁿ − 1 = Πₖ (z − ωₖ). Taking the logarithmic derivative gives n·zⁿ⁻¹/(zⁿ − 1) = Σₖ 1/(z − ωₖ).
Since ωₖ/(z − ωₖ) = z/(z − ωₖ) − 1, the sum Σₖ ωₖ/(z − ωₖ) equals n·zⁿ/(zⁿ − 1) − n = n/(zⁿ − 1). Turn that
upside down and add 1.

Every `1/( )` in the formula is a circle inversion followed by a mirror (1/w is w reflected in the unit circle,
then in the real axis). So the power zⁿ is built from n + 1 inversions: n of them centred on the corners ωₖ,
whose results are turned and added, and one more applied to the sum.

## In space

Write a point of space as q = (x, y, z). Three substitutions carry the formula over:

| In the plane | In space |
|---|---|
| 1/w | inv(q) = (x, −y, −z)/\|q\|², a sphere inversion followed by a flip (the reciprocal of the quaternion x + yi + zj) |
| the corners ωₖ | the same n points, on the unit circle of the xy-plane |
| "times ωₖ" | Rₖ, a turn about the z-axis by the angle of ωₖ |

Apply the formula to the direction d = v/|v| and put the length back afterwards:

    vⁿ = |v|ⁿ · [ 1 + n · inv( Σₖ Rₖ · inv(d − ωₖ) ) ]

In the plane z = 0 nothing has changed, so that slice follows complex zⁿ exactly.

## Why this is the Mercator rule

Each inner inversion is centred on a point ωₖ of the unit sphere, and d lies on that sphere. An inversion
centred on a point of a sphere unrolls the sphere onto a flat plane (it is a stereographic projection). After
the turn Rₖ, all n copies lie in one plane, x = −1/2. Their sum lies in the plane x = −n/2. The outer
inversion rolls that plane back onto a sphere, and the "n ·" and "1 +" make it the unit sphere again. So a
direction goes in and a direction comes out: the result has length 1 before |v|ⁿ is put back.

Unrolling and rolling back both keep angles, and two inversions in a row keep handedness. Seen in a flat
chart of the sphere, each unrolled copy is therefore an analytic function, their sum is one too, and rolling
back keeps it so. An analytic map of the sphere is completely decided by what it does on one circle, and on
the equator this one is zⁿ. So it is ζ → ζⁿ in the stereographic coordinate ζ = e^(m + iφ), where φ is the
longitude and m the latitude as a Mercator chart measures it (m = atanh(z/|v|)). In plain words: the longitude is multiplied by n
and the Mercator latitude is multiplied by n. That is exactly what `MATH.mercator` and the shader compute, in
closed form, without a loop over k. It also works for any n, where the sum needs a whole number.

For a negative whole power one more inversion is needed: v⁻ⁿ = inv(vⁿ). At n = −1 the rule is a single sphere
inversion with a flip, which is why the scorecard reports perfect roundness there.

## Numeric evidence

`inversionPower(v, n)` in `src/js/10-approaches.js` is the sum written out literally. The parity page
(`python tools/shot.py --url tests/approaches.html --actions tests/approaches.json`, 76 checks, all passing)
compares it with `MATH.mercator` (one plane, no offsets) on 2,000 random directions and on 2,000 random points
at distances 0.3 to 2.3, in double precision:

| n | inversions used | largest difference, unit sphere | largest difference, all of space (relative) | \|result\| − 1 on the sphere |
|---|---|---|---|---|
| 2 | 3 | 1.1e-15 | 8.2e-16 | 8.9e-16 |
| 3 | 4 | 2.6e-15 | 1.9e-15 | 1.1e-15 |
| 4 | 5 | 1.9e-15 | 1.9e-15 | 1.1e-15 |
| 5 | 6 | 2.6e-15 | 2.2e-15 | 1.4e-15 |
| 8 | 9 | 4.1e-9 | 4.1e-9 | 2.0e-15 |
| −1 | 3 | 1.2e-15 | 7.1e-16 | 8.9e-16 |
| −2 | 4 | 1.0e-15 | 8.9e-16 | 8.9e-16 |
| −3 | 5 | 2.6e-15 | 2.3e-15 | 1.0e-15 |
| −8 | 10 | 4.1e-9 | 4.1e-9 | 2.1e-15 |

The 4e-9 at |n| = 8 is the closed form's own guard: it caps the multiplied Mercator latitude at ±20, where a
direction is already within 4e-9 of the pole. Directions within 2.6° of a pole were left out of the comparison
because the closed form also stops the latitude 0.08° short of the poles, to keep the 32-bit shader finite.

The same run checks that the plane z = 0 follows complex zⁿ to 3e-15 or better for every approach except the
classic Mandelbulb, at n = −3, −2, −1, 2, 3, 8, and that the shader code agrees with the JavaScript to 2.4e-4
(32-bit arithmetic) for every approach.

`notes/invcheck.py` (the orchestrator's first check) reaches the same conclusion with a separate program, and
shows that flipping only y in the reciprocal, a plain mirror instead of a half-turn, gives the same map.

## What the earlier page got wrong

It said an approach that contains the exact flat set cannot be built from inversions. The true statement is
narrower. A chain of inversions, one after another, is a shape-keeping map, and Liouville's theorem says the
power map is not one of those. A sum of inversions is allowed to be anything, and this sum is the power map
on directions. The price is paid where the sum is taken and where the length is put back: circles on the
sphere of directions stay circles, but the stretch along the sphere no longer matches the stretch outward.

## Planes, turn and lift

- **Planes.** The sum above is the one-plane rule: Kučera's "inflated" sets. His "truly 3D" figure folds
  space first, so that the nearest of p planes through the x-axis lands on the xy-plane. The number of planes
  is a free choice. It sets the number of fins around the x-axis (2p), whatever the power is, so the fins
  match the power when p = n/2. That is the pattern the user noticed (n = 8 with 4 planes, n = 6 with 3,
  n = 4 with 2), and it is why n = 2 with 1 plane is only the inflated set: 2 fins, top and bottom.
- **Turn and lift** are the phase offsets of this approach: ζ → e^(lift)·e^(i·turn)·ζⁿ. The turn is added to
  the longitude, the lift to the Mercator latitude, after both are multiplied by n. A turn keeps the plane
  z = 0 in itself, where it carries e^(iφ)·zⁿ; for zⁿ + c that slice is the usual flat set turned by
  −φ/(n − 1) (checked on 4,000 sample points for n = 2, 3, 8: none disagree). A lift moves the plane z = 0
  onto a cone, so the flat set is no longer a flat slice.
- **The turn works with one plane only.** The folds identify points that are mirror images in y, which is
  harmless only while the rule itself has that mirror symmetry. A turn breaks it, and the solid tears into
  striped sheets along the folds (`out/approaches/08-merc-turn15.png`, `02-merc-turn60.png`; 180° is the one
  angle that survives, `09-merc-turn180.png`). So with two or more planes the turn dial is hidden and has no
  effect. The lift keeps the mirror symmetry and works with any number of planes.

## The "fixed spheres" variant: tried, and left out

The construction above lets the n spheres follow the point: they sit on the sphere through v. The other
natural reading keeps them on the unit sphere and applies the sum to the point itself:

    vⁿ = 1 + n · inv( Σₖ Rₖ · inv(v − ωₖ) )

`python notes/fixed_spheres.py` characterises it. Findings:

- It agrees with the following version on the unit sphere (4e-14 at n = 2) and in the plane z = 0 (6e-16), so
  its flat slice is exact too. Everywhere else the two differ, by up to half the size of the result at n = 2.
- It leaves every point of the z-axis exactly where it is (difference 4e-16 for t from −5 to 40).
- Far from the origin it grows like |v| / sin(latitude), linearly, where a power should grow like |v|ⁿ.
  At |v| = 100, n = 2: 10,000 in the plane, but 1,140 at latitude 5°, 200 at 30°, 100 beside the pole.
- So off the plane an orbit of vⁿ + c only drifts outward (on the z-axis by exactly c per step), and whether it "escapes"
  depends on how many steps are allowed. For z² + c the solid reaches up the z-axis to 64/steps: 4.9 with
  14 steps, 1.1 with 60, 0.27 with 240, 0.06 with 1,000. On a grid over the slice y = 0, the share of points
  that never escape is 99% with 14 steps, 44% with 60 and 8% with 240, while the following version holds
  steady at 2 to 3%. The slice z = 0.3 is entirely solid at 60 steps and entirely empty at 240.

It is a smooth lens whose thickness is set by the iteration count, with no detail off the plane
(`out/approaches/fixed-n2-xz-60.png`, `fixed-n2-xz-240.png`). That is not a usable object, so there is no
`fixed` option. The spheres have to follow the point for the escape to be a real one.

## Sentences the page can reuse

1. "In the plane, zⁿ can be written exactly as a sum of circle inversions. Put spheres where the circles were
   and the same sum gives a power for points in space, and its slice at z = 0 is the flat set."
2. "One inversion after another can never do this: a chain of inversions keeps every shape, and no power
   does that in space. Adding inversions together is what makes it possible, and adding is also where the
   perfect shape-keeping is lost."
3. "Worked out, the sum multiplies the longitude and the Mercator latitude of a direction by n. With n = −1 it
   is a single sphere inversion."
