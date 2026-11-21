"""Private test: add the tilted quaternion square as an approach of its own.

Reads base11/js/10-approaches.js, writes out/me/tilt/10-approaches.js.
Run from the project root: python out/me/tilt/make.py

The rule (alpha = the tilt, A = the turn by alpha about the z-axis, L = the quaternion power, "Lathe"):
    v^n = A^(-n) . L^n . A (v)
In the plane z = 0 a turn is multiplication by e^(i alpha), so (e^(i a) z)^n e^(-i n a) = z^n: exact for
every alpha. It is the 3D shadow of the quaternion product q . sigma(q) with sigma a twist of the hidden
plane by 2 alpha: for q = z + w j,  q . sigma(q) = z^2 - e^(-2 i alpha) |w|^2 + (...) w j.
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src = io.open(os.path.join(ROOT, 'base11', 'js', '10-approaches.js'), encoding='utf-8').read()

GLSL = r"""// uA.x: the tilt in degrees. The quaternion power, measured from an axis turned by the tilt inside the plane z = 0.
const GL_TILT = GL_APR + `
vec3 aprRz(vec3 v, float a){ float c = cos(a), s = sin(a); return vec3(c * v.x - s * v.y, s * v.x + c * v.y, v.z); }
vec3 aprLmul(vec3 a, vec3 b){ return vec3(a.x * b.x - dot(a.yz, b.yz), a.x * b.yz + b.x * a.yz); }
vec3 mul(vec3 a, vec3 b){ float t = radians(uA.x); return aprCap(aprRz(aprLmul(aprRz(a, t), aprRz(b, t)), -2.0 * t)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float t = radians(uA.x);
  vec3 u = aprRz(v, t);
  float rho = length(u.yz), a = at2(rho, u.x) * n;
  vec2 d = rho > 0.0 ? u.yz / rho : vec2(1.0, 0.0);
  return aprRz(aprPow(r, n) * vec3(cos(a), sin(a) * d), -n * t);
}
vec3 sqr(vec3 v){
  float t = radians(uA.x);
  vec3 u = aprRz(v, t);
  return aprCap(aprRz(vec3(u.x * u.x - dot(u.yz, u.yz), 2.0 * u.x * u.yz), -2.0 * t));
}
vec3 cmap(vec3 c){ return c; }`;
"""

MATHJS = r"""  tilt(v, n, q = {}) {
    const t = aprRad(q.tilt), rz = (p, a) => [Math.cos(a) * p[0] - Math.sin(a) * p[1], Math.sin(a) * p[0] + Math.cos(a) * p[1], p[2]];
    return rz(MATH.lathe(rz(v, t), n, {}), -n * t);
  },
"""

ENTRY = r"""  {
    id: 'tilt', name: 'Quaternion square, tilted', glsl: GL_TILT, axis: () => [1, 0, 0],
    tag: 'The quaternion rule, with its angle measured from an axis tilted inside the flat plane.',
    params: [{ type: 'dial', key: 'tilt', label: 'Tilt, degrees', min: -90, max: 90, step: 1, def: 30, lo: -180, hi: 180, animate: 'bounce', help: 'At 0 this is the Lathe. Away from 0 the axis the rule spins around no longer lines up with the x-axis, which breaks the rings. The plane z = 0 stays exact at every tilt.' }],
    formula: (p, n) => (aprIs(n, 2) ? `v² = turn(−${aprDeg(2 * p.tilt)}) · q²(turn(${aprDeg(p.tilt)}) · v)   with q² = (x² − y² − z², 2xy, 2xz) and turn a turn about the z-axis`
      : `vⁿ = turn(−n · ${aprDeg(p.tilt)}) · qⁿ(turn(${aprDeg(p.tilt)}) · v)   with qⁿ the quaternion power and turn a turn about the z-axis`),
    about: 'A quaternion square is q times q. Here the second factor is twisted first: the two hidden directions of 4D space are turned against each other by twice the tilt. Seen in 3D, that is the Lathe rule with its angle measured from an axis tilted inside the plane z = 0, and the result turned back. In the plane z = 0 the two turns cancel, so the slice is the flat set at every tilt.',
    roundNote: () => 'The squash is in the spin direction.',
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : Math.abs(n) < 1 + 1e-9 ? ['ok', 'Crushes nothing at this power.' + aprPole(n)]
      : ['no', 'Crushes every direction whose angle from the tilted axis, times n, is a multiple of 180°.' + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : !aprWhole(n) ? ['no', 'A polynomial for whole positive powers only.']
      : n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial.']),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, at every tilt.'),
  },
"""

def put_before(text, anchor, block):
    assert text.count(anchor) == 1, (anchor, text.count(anchor))
    return text.replace(anchor, block + anchor)

out = put_before(src, "// uA.x, uA.y: phases in degrees, added to the latitude and the longitude", GLSL)
out = put_before(out, "  bulb(v, n, q = {}) {", MATHJS)
out = put_before(out, "  {\n    id: 'bulb', name: 'Mandelbulb'", ENTRY)
dst = os.path.join(ROOT, 'out', 'me', 'tilt', '10-approaches.js')
io.open(dst, 'w', encoding='utf-8', newline='\n').write(out)
print('wrote', dst, len(out))
