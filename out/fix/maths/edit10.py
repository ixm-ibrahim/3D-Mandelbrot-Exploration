# One-off editor for src/js/10-approaches.js: exact string replacements, each must match once.
import io, sys
p = 'src/js/10-approaches.js'
s = io.open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d match(es), found %d for: %s' % (count, n, old[:70]))
    s = s.replace(old, new)


# ---- split: negative powers (JS)
rep("""  // Exactly on the plane z = 0 the real factor stays 0 even for a negative power (where 0^n has no
  // value), so the flat slice survives; one step off the plane it is sent toward infinity.
  split(v, n) {
    const [x, y, z] = v,""",
"""  // A negative power is the positive power followed by one sphere inversion with a mirror (y -> -y), which
  // is what a reciprocal is in every other approach. Taken side by side, (1/(x + iy), 1/z) has no value on
  // the plane z = 0 or on the z-axis, so everything near them would be thrown to infinity. This form is
  // finite everywhere except the origin, and in the plane z = 0 it is still complex z^n exactly.
  split(v, n) {
    if (n < 0) {
      const u = MATH.split(v, -n), L = len(u), most = Math.exp(APR_LOGCAP);
      if (!(L * most > 1)) return [most, 0, 0];
      return [u[0] / L / L, -u[1] / L / L, u[2] / L / L];
    }
    const [x, y, z] = v,""")

# ---- split: negative powers (shader). One body, so the compiler copies it once.
rep("""vec3 pw(vec3 v, float n){
  float rho = length(v.xy), p = at2(v.y, v.x) * n, az = abs(v.z);
  float zs = az > 0.0 ? aprPow(az, n) * (v.z < 0.0 ? cos(PI * n) : 1.0) : 0.0;
  return vec3((rho < 1e-20 && n > 0.0 ? 0.0 : aprPow(rho, n)) * vec2(cos(p), sin(p)), zs);
}""",
"""// n < 0: the power -n, then one sphere inversion with a mirror (see MATH.split)
vec3 pw(vec3 v, float n){
  float m = abs(n), rho = length(v.xy), p = at2(v.y, v.x) * m, az = abs(v.z);
  float zs = az > 0.0 ? aprPow(az, m) * (v.z < 0.0 ? cos(PI * m) : 1.0) : 0.0;
  vec3 u = vec3((rho < 1e-20 && m > 0.0 ? 0.0 : aprPow(rho, m)) * vec2(cos(p), sin(p)), zs);
  if (n >= 0.0) return u;
  float L = length(u);
  if (!(L * APR_CAP > 1.0)) return vec3(APR_CAP, 0.0, 0.0);
  return (u / L) * vec3(1.0, -1.0, 1.0) / L;
}""")

# ---- wording helpers
rep("""  return `${subject} complex arithmetic with one change: every power is also turned by ${aprDeg(deg)} (it carries e^{iφ}·zⁿ).${back}`;""",
    """  return `${subject} complex arithmetic with one change: every power is also turned by ${aprDeg(deg)}.${back}`;""")
rep("""const APR_INVERSION = 'At n = −1 the rule is a single sphere inversion with a flip, and inversions keep every shape.';""",
"""const APR_INVERSION = 'At n = −1 the rule is a single sphere inversion with a flip, and inversions keep every shape.';
const APR_MIRROR = 'At n = −1 the rule is a single sphere inversion with a mirror, and inversions keep every shape.';
// n = 0 sends every point to the same place, whatever the approach
const aprNone = () => ['no', 'Everything is crushed onto one point.'];
const aprConstant = () => ['ok', 'A constant.'];
// what the turn and longitude-phase dials do to the slice at z = 0
const APR_SLICE_TURNS = ' Away from 0 the slice at z = 0 is no longer the plain 2D picture: for the Mandelbrot solid it is that picture turned, for a Julia set it is a different set.';""")

# ---- sphere inversions: note, hints, formula, about
rep("""      { type: 'note', text: 'Planes are a free choice, separate from the power: p planes give 2p fins around the x-axis whatever n is, so the fins match the power when p = n/2. Kučera’s 3D figure is 2 planes at n = 2. The flat set’s own (n − 1)-fold symmetry is a turn about the z-axis, a different thing.' },""",
"""      { type: 'note', text: 'The number of planes is a free choice: nothing in this rule fixes it, and it has nothing to do with the power. With p planes the solid has 2p fins around the x-axis, whatever n is. So the fins match the power only when p is half of n: 4 planes for n = 8, 3 for n = 6, 2 for n = 4. Fins always come in pairs, so an odd power has no exact match: the nearest choices give n − 1 or n + 1 fins. No value is the correct one. Kučera’s 3D figure uses 2 planes at n = 2, which is the starting value here.' },""")
rep("""help: 'Added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis; Julia sets change shape.' },
      { type: 'note', when: p => p.planes >= 2,""",
"""help: 'This approach’s version of the Mandelbulb’s longitude phase: added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis, and Julia sets change shape.' + APR_SLICE_TURNS },
      { type: 'note', when: p => p.planes >= 2,""")
rep("""help: 'Added to the Mercator latitude each time a power is taken. Away from 0 the flat set leaves the plane z = 0.' },""",
    """help: 'This approach’s version of the Mandelbulb’s latitude phase: it pushes every direction toward one pole each time a power is taken. Press play to make the solid pulse. Away from 0 the flat set leaves the plane z = 0.' },""")
rep("""s = `v${aprSup(k)} = |v|${aprSup(k)} · [1 + ${k}·inv(Σₖ Rₖ·inv(d − ωₖ))]   with d = v/|v| and k = 0 … ${k - 1}.`;""",
    """s = `v${aprSup(k)} = |v|${aprSup(k)} · [1 + ${k}·inv(Σₖ Rₖ·inv(d − ωₖ))]   where d = v/|v| is the direction of v, inv is a sphere inversion, ωₖ are ${k} points spaced evenly round the unit circle, and Rₖ is the turn about the z-axis that reaches the k-th one.`;""")
rep("""else if (aprIs(n, -1)) s = 'v⁻¹ = inv(v) = (x, −y, −z)/|v|².';""",
    """else if (aprIs(n, -1)) s = 'v⁻¹ = inv(v) = (x, −y, −z)/|v|²: one sphere inversion, then a flip.';""")
rep("""with φ the longitude and m the Mercator latitude. At whole n this is what the sum of inversions gives.';""",
    """with φ the longitude and m the latitude as a Mercator map stretches it. At whole n this is what the sum of inversions gives.';""")
rep("""p.lift ? `${aprNum(p.lift)} is added to the Mercator latitude` : '']""",
    """p.lift ? `${aprNum(p.lift)} is added to the latitude (measured the way a Mercator map stretches it)` : '']""")
rep("""    about: 'In the plane, zⁿ is exactly a sum of circle inversions: zⁿ = 1 + n / Σₖ ωₖ/(z − ωₖ), with ωₖ the n-th roots of 1. Swap the circles for spheres and the same sum works on directions in space, where inv(q) = (x, −y, −z)/|q|² is a sphere inversion with a flip and Rₖ turns about the z-axis by the angle of ωₖ. Worked out, it multiplies the longitude and the Mercator latitude by n. It reproduces the Julia sets in Václav Kučera’s paper (Bridges 2019): one plane gives his inflated sets, two planes his truly 3D figure (Julia set at c = (−1, 0, 0), seen straight down).',""",
"""    about: 'In the plane, zⁿ can be built from n + 1 circle inversions: one about each of n points spaced evenly round the unit circle, the results added together, then one more inversion of the sum. Swap the circles for spheres and the same recipe works on points in space. Cut the solid at z = 0 and the slice is exactly the ordinary 2D Mandelbrot or Julia set of the same power: the 2D view shows it. Slices at other heights are different shapes. Worked out, the recipe multiplies two angles by n: the longitude, and the latitude as a Mercator map stretches it (more and more toward the poles). It reproduces the Julia sets in Václav Kučera’s paper (Bridges 2019): one plane gives his inflated sets, two planes his fully 3D figure (the Julia set at c = (−1, 0, 0), seen straight down).',""")
rep("""    crush: (p, n = S.n) => {
      if (p.planes >= 2) return""",
"""    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      if (p.planes >= 2) return""")
rep("""    smooth: (p, n = S.n) => {
      if (p.planes >= 2) return ['no', 'Pieces""",
"""    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (p.planes >= 2) return ['no', 'Pieces""")

# ---- lathe
rep("""about: 'With spin 1 this is the quaternion power with one component held at zero, and the set""",
    """about: 'With spin 1 this is the power of a quaternion (a number with three imaginary parts) with one part held at zero, and the set""")
rep("""    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (a < 1 + 1e-9) return ['ok', (n < 0 ?""",
"""    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ?""")
rep("""      const tear = aprTear(n, APR_LINE);
      if (p.spin !== 1)""",
"""      const tear = aprTear(n, APR_LINE);
      if (aprIs(n, 0)) return aprConstant();
      if (p.spin !== 1)""")

# ---- Mandelbulb
rep("""help: 'Added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis; Julia sets change shape.' },
    ],
    formula: (p, n) => (aprIs(n, 2) && !p.lat && !p.lon""",
"""help: 'Added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis, and Julia sets change shape.' + APR_SLICE_TURNS },
    ],
    formula: (p, n) => (aprIs(n, 2) && !p.lat && !p.lon""")
rep("""    crush: (p, n = S.n) => {
      if (!aprPasses((p.lat || 0) - 90 * n,""",
"""    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      if (!aprPasses((p.lat || 0) - 90 * n,""")
rep("""    smooth: (p, n = S.n) => {
      const torn = Math.abs(Math.cos(n * PI / 2 + aprRad(p.lat))) > 1e-6, even""",
"""    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      const torn = Math.abs(Math.cos(n * PI / 2 + aprRad(p.lat))) > 1e-6, even""")

# ---- classic
rep("""    crush: (p, n = S.n) => (aprPasses(p.theta || 0, (p.theta || 0) + 180 * n, 0)
      ? ['no',""",
"""    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : aprPasses(p.theta || 0, (p.theta || 0) + 180 * n, 0)
      ? ['no',""")
rep("""    smooth: (p, n = S.n) => {
      const torn = Math.abs(Math.sin(aprRad(p.theta))) > 1e-6 ||""",
"""    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      const torn = Math.abs(Math.sin(aprRad(p.theta))) > 1e-6 ||""")

# ---- split texts
i = s.index("    formula: (p, n) => (aprIs(n, 2) ? 'v² = (x² − y², 2xy, z²)'")
j = s.index("  },\n];", i)
s = s[:i] + """    formula: (p, n) => {
      if (aprIs(n, 2)) return 'v² = (x² − y², 2xy, z²)';
      if (aprIs(n, -1)) return 'v⁻¹ = (x, −y, z)/|v|²: one sphere inversion with a mirror';
      if (n >= 0) return 'vⁿ = ((x + iy)ⁿ, zⁿ): the complex power and the real power, side by side';
      const whole = aprWhole(n), m = whole ? aprSup(-n) : 'ᵐ';
      return `v${whole ? aprSup(n) : 'ⁿ'} = (X, −Y, Z)/(X² + Y² + Z²)   with X + iY = (x + iy)${m} and Z = z${m}` + (whole ? '' : `, m = ${aprNum(-n)}`) + ': the two powers side by side, then one sphere inversion with a mirror';
    },
    about: 'Space treated as a complex number x + iy and an ordinary number z side by side, each multiplied on its own. Two points that are not 0 can multiply to 0 this way, and the set is the flat one extruded into a prism. A negative power is the positive power followed by one sphere inversion, as in the other approaches. Dividing by z on its own is not possible on the plane z = 0, where z is 0.',
    roundNote: (p, n) => (aprIs(n, -1) ? APR_MIRROR : 'Each factor keeps shapes on its own. Together they do not.'),
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (aprIs(a, 1)) return ['ok', n < 0 ? 'Crushes nothing: at n = −1 the rule is one sphere inversion with a mirror. The origin is sent to infinity.' : 'Crushes nothing: at n = 1 every point stays where it is.'];
      if (a < 1) return ['part', 'Crushes nothing at this power, but the stretch has no limit at the plane z = 0 and the z-axis.' + aprPole(n)];
      return ['no', 'Crushes the plane z = 0 and the z-axis.' + aprPole(n)];
    },
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant()
      : !aprWhole(n) ? ['no', 'A polynomial for whole positive powers only. Otherwise the complex factor is torn along the half-plane y = 0, x < 0, and below the plane the real factor keeps only the real part of zⁿ.']
      : n < 0 ? ['part', 'One polynomial divided by another: smooth everywhere except the origin, which is sent to infinity.'] : ['ok', 'A polynomial.']),
    slice: (ok, p, n = S.n) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : n < 0 ? 'The plane z = 0 follows complex arithmetic exactly. Because a negative power ends with an inversion, the slices at other heights are not copies of it.'
      : 'The plane z = 0 follows complex arithmetic exactly. So does every level slice of the prism.'),
""" + s[j:]
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
