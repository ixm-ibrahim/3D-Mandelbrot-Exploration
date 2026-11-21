"""One-off edit of src/js/10-approaches.js: every rule becomes a list entry of its own.

  mercator  Sphere inversions, one plane     (was: the Planes dial at 1)
  fold      Sphere inversions, two planes    (was: the Planes dial at 2 or more)
  lathe     Quaternion square (Lathe)        (renamed; the rule is unchanged)
  tilt      Quaternion square, twisted       (new)
and a `group` on every entry, with APPROACH_GROUPS giving the headings of the list.

Run once from the project root: python out/me/tilt/split_entries.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PATH = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
src = io.open(PATH, encoding='utf-8').read()

def between(text, a, b):
    i = text.index(a); j = text.index(b, i)
    assert text.count(a) == 1, a
    return i, j

HEAD = r"""// The headings of the Approach list, in the order they are shown. Every approach names one in `group`, and
// the list shows the approaches of a group in the order they stand in APPROACHES.
const APPROACH_GROUPS = [
  { id: 'inversions', title: 'Sphere inversions' },
  { id: 'quaternion', title: 'Quaternions' },
  { id: 'angles', title: 'Angle rules' },
  { id: 'other', title: 'Side by side' },
  { id: 'tried', title: 'Tried, and kept for the record' },
];
// The one-plane rule in words, shared by the two Sphere inversions entries.
function aprMercFormula(n) {
  const k = Math.round(n);
  if (aprWhole(n) && n >= 2) return `v${aprSup(k)} = |v|${aprSup(k)} · [1 + ${k}·inv(Σₖ Rₖ·inv(d − ωₖ))]   with d = v/|v| the direction of v, inv a sphere inversion, ωₖ the ${k} points spaced evenly round the unit circle, and Rₖ the turn about the z-axis that reaches the k-th of them.`;
  if (aprIs(n, 1)) return 'v¹ = v.';
  if (aprIs(n, 0)) return 'v⁰ = (1, 0, 0).';
  if (aprIs(n, -1)) return 'v⁻¹ = inv(v) = (x, −y, −z)/|v|²: one sphere inversion, then a flip.';
  if (aprWhole(n)) return `v${aprSup(k)} = inv(v${aprSup(-k)}): the sum of inversions for the power ${-k}, then one more inversion.`;
  return 'vⁿ = |v|ⁿ · (cos nφ / cosh nm, sin nφ / cosh nm, tanh nm)   with φ the longitude and m the latitude as a Mercator map stretches it. At whole n this is what the sum of inversions gives.';
}
const aprMercAfter = (turn, lift) => (turn || lift ? ' After it, ' + [turn ? `${aprDeg(turn)} is added to the longitude` : '', lift ? `${aprNum(lift)} is added to the latitude (measured the way a Mercator map stretches it)` : ''].filter(Boolean).join(' and ') + '.' : '');
const APR_LIFT = { type: 'dial', key: 'lift', label: 'Lift toward the pole', min: -2, max: 2, step: 0.01, def: 0, lo: -6, hi: 6, xmin: -6, xmax: 6, xlo: -20, xhi: 20, animate: 'bounce', help: 'The nearest thing this approach has to the Mandelbulb’s latitude phase: it pushes every direction toward one pole each time a power is taken. It is an offset where the phase is an angle, so play sweeps it to one end and back. Away from 0 the flat set leaves the plane z = 0.' };
const APR_LIFTED = 'With a lift the plane z = 0 lands on a cone, so no flat slice follows complex arithmetic. Set the lift to 0 to get the flat set back.';
const APR_CIRCLES = 'Circles on the sphere stay circles (see the step view). The squash is between the outward direction and the sphere.';

const APPROACHES = [
  {
    id: 'mercator', name: 'Sphere inversions, one plane', group: 'inversions', glsl: GL_MERCATOR, axis: () => [0, 0, 1],
    tag: 'Add up sphere inversions, the way circle inversions add up to zⁿ in the plane.',
    params: [
      { type: 'note', text: 'For whole powers this rule is smooth and has no seam, so nothing tears the solid. The fine detail lies around the plane z = 0 only: these are the “inflated” sets in Václav Kučera’s paper (Bridges 2019, Figure 3). The look of Figure 4, with beads around two circles, belongs to the next entry, Sphere inversions, two planes.' },
      { type: 'dial', key: 'turn', label: 'Turn, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'This approach’s version of the Mandelbulb’s longitude phase, added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis, and Julia sets change shape.' + APR_SLICE_TURNS },
      // Lift is an offset where a phase is an angle: its two ends give different solids, so its sweep runs there and back.
      APR_LIFT,
    ],
    formula: (p, n) => aprMercFormula(n) + aprMercAfter(aprMercTurn(p), p.lift),
    about: 'In the plane, zⁿ can be built from n + 1 circle inversions: one about each of n points spaced evenly round the unit circle, the results added, then one more inversion of the sum. Swap the circles for spheres and the same recipe works in space, once a plane is chosen for the n points to lie in. Worked out, it multiplies two angles by n: the longitude, and the latitude as a Mercator map stretches it. Cut the solid at z = 0 and the slice is exactly the ordinary 2D Mandelbrot or Julia set of the same power (the 2D view shows it).',
    // a lift stretches the sphere of directions, so at n = −1 the rule is a plain inversion only while the lift is 0
    roundNote: (p, n) => (aprIs(n, -1) && !p.lift ? APR_INVERSION : APR_CIRCLES),
    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      const a = Math.abs(n);
      if (aprIs(a, 1)) return ['ok', n < 0 ? 'Crushes nothing: at n = −1 the rule is one sphere inversion. The origin is sent to infinity.' : 'Crushes nothing: at n = 1 every point stays where it is.'];
      if (a < 1) return ['part', 'Crushes nothing at this power, but the stretch has no limit beside the z-axis.' + aprPole(n)];
      return ['part', 'Crushes the z-axis only: a line where the plane has a point.' + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'Smooth for whole powers only.' + aprTear(n, APR_HALF)];
      return ['part', n < 0 ? 'Smooth everywhere except the origin, which is a pole.' : 'Smooth everywhere except the origin. It needs |v|, so it is not a polynomial.'];
    },
    slice: (ok, p, n = S.n) => {
      if (p.lift) return APR_LIFTED;
      const turn = aprMercTurn(p);
      if (turn) return aprTurned('The plane z = 0 follows', turn, n);
      return !ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.';
    },
  },
  {
    // The earlier version of Sphere inversions, an approach of its own so that the two can be told apart. The fold
    // sends the half y > 0 and the half y < 0 of space to opposite sides, so the rule jumps across the plane
    // y = 0 (see foldk).
    id: 'fold', name: 'Sphere inversions, two planes', group: 'inversions', glsl: GL_FOLD, axis: () => [1, 0, 0],
    tag: 'The earlier version. Fold space like a fan first, so that two planes carry the flat set.',
    params: [
      { type: 'dial', key: 'planes', label: 'Planes', min: 2, max: 8, step: 1, def: 2, int: true, xmax: 16, xhi: 64 },
      { type: 'note', text: 'An attempt to copy Figure 4 in Václav Kučera’s paper (Bridges 2019), with beads around two circles. It looks right for a Julia set whose c lies on the x-axis, such as the Basilica. Everywhere else, the Mandelbrot solid included, the rule jumps on the seam of its fold, which tears the solid. The count is a free choice: p planes give 2p fins around the x-axis, whatever the power is. There is no Turn dial here: with a fold a turn tears the solid into sheets.' },
      APR_LIFT,
    ],
    formula: (p, n) => aprMercFormula(n) + ` Before that, the nearest of ${p.planes} planes through the x-axis is folded onto the xy-plane.` + aprMercAfter(0, p.lift),
    about: 'The one-plane rule with a fold in front of it. Space is folded around the x-axis like a fan, until the nearest of the chosen planes lies on the xy-plane, and then the one-plane rule is applied. With two planes, the planes z = 0 and y = 0 both carry the flat set. This follows the second construction in Kučera’s paper, whose third map is the second one turned by 90° about the x-axis. The paper reports that construction for c on the x-axis only, and that is where this rule is whole too.',
    roundNote: (p, n) => (aprIs(n, -1) && !p.lift ? 'At n = −1 each piece is a sphere inversion with a flip, which keeps every shape. The folds between the pieces still leave creases.' : APR_CIRCLES),
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone()
      : ['part', (n > 1 ? 'Nothing but the origin is crushed.' : 'Nothing is crushed.') + ' Space is creased where the folds meet instead.' + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant()
      : ['no', 'Pieces of the one-plane rule joined by mirror folds. The folds leave creases, and across the plane y = 0 a jump, whose effect cancels only when c is on the x-axis.' + aprTear(n, APR_HALF)]),
    slice: (ok, p) => (p.lift ? APR_LIFTED : !ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : `${p.planes} planes through the x-axis follow complex arithmetic exactly, z = 0 among them.`),
  },
"""

TILT = r"""  {
    // F = A^(-n) L^n A, with A the turn by the tilt about the z-axis and L the quaternion power. In 4D it is
    // q times a twisted copy of q: for q = z + w j the copy is z + e^(2i tilt) w j, and
    // q . copy = z^2 - e^(-2i tilt) |w|^2 + (...) w j. A tilt of 180 is the Lathe with z mirrored (its twin).
    id: 'tilt', name: 'Quaternion square, twisted', group: 'quaternion', glsl: GL_TILT,
    axis: p => [Math.cos(aprRad(p.tilt)), -Math.sin(aprRad(p.tilt)), 0],
    tag: 'Square a quaternion with its second factor twisted. The rings of the Lathe break up.',
    params: [
      { type: 'dial', key: 'tilt', label: 'Tilt of the axis, degrees', min: -180, max: 180, step: 1, def: 40, lo: -360, hi: 360, animate: true, help: 'At 0 this is the plain quaternion square, the Lathe, and the solid is made of rings. Away from 0 the rings break up into one body with tunnels. At 180 it is the Lathe’s mirror twin. At 90 and −90 the Mandelbrot solid has no end: it runs off along a band and the drawing radius cuts it. A minus sign gives the mirror image. The plane z = 0 is exact at every tilt.' },
      { type: 'note', text: 'A rule for all of space with no plane chosen and no seam: for whole powers it is a polynomial. Up close its skin is smooth, as with every quaternion rule. The fine detail of the flat set shows where the solid meets the plane z = 0.' },
    ],
    formula: (p, n) => (aprIs(n, 2) ? `v² = ((x + iy)² − z²·e^(−2it), 2z·(x cos t − y sin t))   with t = ${aprDeg(p.tilt)}, and the first two coordinates written as one complex number. At t = 0 it is the quaternion square (x² − y² − z², 2xy, 2xz).`
      : `vⁿ = turn(−n·t) · qⁿ(turn(t) · v)   with t = ${aprDeg(p.tilt)}, qⁿ the quaternion power and turn a turn about the z-axis.`),
    about: 'A quaternion square is q times q. Here the second factor is twisted first: quaternions have four directions, two of them outside the flat plane, and those two are turned against each other by twice the tilt. What that leaves in 3D is the Lathe rule with its angle measured from an axis tilted inside the plane z = 0, and the result turned back. In the plane z = 0 the two turns cancel, so the slice is the flat set at every tilt. A Julia set whose c lies in that plane is a true slice of the 4D set. A Mandelbrot solid needs a c with a height, and adding it as a 3D point is this page’s own choice.',
    roundNote: () => 'The squash is in the spin direction around the tilted axis.',
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the tilted axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane through the origin square to the tilted axis.` : '') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'A polynomial for whole positive powers only. A power that is not a whole number also tears space along a line, the way zⁿ tears the plane along the negative x-axis.'];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial.'];
    },
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, at every tilt.'),
  },
"""

# 1. the list head and the two Sphere inversions entries
i, j = between(src, "const APPROACHES = [\n", "  {\n    id: 'lathe'")
src = src[:i] + HEAD + src[j:]

# 2. the Lathe: a new name, a group, and the plane-free note
old = "id: 'lathe', name: 'Lathe', glsl: GL_LATHE, axis: () => [1, 0, 0],\n    tag: 'Multiply the angle from the x-axis. Leave the spin around it alone, or multiply that too.',"
assert src.count(old) == 1
src = src.replace(old, "id: 'lathe', name: 'Quaternion square (Lathe)', group: 'quaternion', glsl: GL_LATHE, axis: () => [1, 0, 0],\n    tag: 'Square a quaternion: multiply the angle from the x-axis, and leave the spin around it alone. Sphere inversions with no plane chosen give this same rule.',")
old = "about: 'With spin 1 this is the power of a quaternion (a number with three imaginary parts) with one part held at zero, and the set is the flat one turned on a lathe."
assert src.count(old) == 1
src = src.replace(old, "about: 'With spin 1 this is the power of a quaternion (a number with three imaginary parts) with one part held at zero, and the set is the flat one turned on a lathe. It is also what the sum of sphere inversions gives when no plane is chosen: for the square, the two centres are the points 1 and −1 on the x-axis, and they need no plane. So this is the one rule of its kind that treats every direction around the x-axis alike.")

# 3. the twisted square, after the Lathe
anchor = "  {\n    id: 'bulb', name: 'Mandelbulb', glsl: GL_BULB,"
assert src.count(anchor) == 1
src = src.replace(anchor, TILT + "  {\n    id: 'bulb', name: 'Mandelbulb', group: 'angles', glsl: GL_BULB,")
for old, new in (("id: 'classic', name: 'Mandelbulb, classic', glsl:", "id: 'classic', name: 'Mandelbulb, classic', group: 'angles', glsl:"),
                 ("id: 'split', name: 'Split', glsl:", "id: 'split', name: 'Split', group: 'other', glsl:")):
    assert src.count(old) == 1, old
    src = src.replace(old, new)

# 4. small things
old = "const aprMercTurn = p => ((p.planes || 1) < 2 ? aprWrap(p.turn || 0) : 0);   // the turn in effect: one plane only"
assert src.count(old) == 1
src = src.replace(old, "const aprMercTurn = p => aprWrap(p.turn || 0);   // the turn in effect, between −180° and 180°")

io.open(PATH, 'w', encoding='utf-8', newline='\n').write(src)
print('wrote', PATH, len(src))
