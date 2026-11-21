# One-off editor for src/js/20-formula.js: exact string replacements, each must match once.
import io, sys
p = 'src/js/20-formula.js'
s = io.open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d match(es), found %d for: %s' % (count, n, old[:70]))
    s = s.replace(old, new)


# ---- presets: which fields are the preset, which are only suggestions; plain names and notes
i = s.index('// Equation presets:')
j = s.index('// ---------- equation -> shader code.')
s = s[:i] + """// Equation presets.
// THE PRESET, always applied:   name, eq, z0   (the formula and its start value, nothing else)
//                               note            a few sentences on what the picture shows
// SUGGESTIONS ONLY, tuned for the Mandelbrot solid at n = 2 and the default approach. The page decides
// whether to use them; a preset is complete without them, and none of them belongs to the formula:
//   target, dist, yaw, pitch    a first camera (angles in radians)
//   cut                         a height at which the solid is worth cutting open
//   julia: { dist }             the same camera distance for Julia mode, where the solid has another size
// A preset never carries an iteration count, a power, a quality setting or a colour.
const PRESETS = [
  { name: 'zⁿ + c  (Mandelbrot)', eq: 'z^n + c', z0: '0' },
  { name: 'c·z·(1 − z)  (lambda)', eq: 'c*z*(1 - z)', z0: '0.5', target: [1, 0, 0], dist: 10 },
  { name: '|z|ⁿ + c  (burning ship)', eq: 'abs(z)^n + c', z0: '0' },
  { name: 'conj(z)ⁿ + c  (tricorn)', eq: 'conj(z)^n + c', z0: '0' },
  { name: 'z³ − z + c  (cubic)', eq: 'z^3 - z + c', z0: '0.57735' },
  { name: 'zⁿ + c/z  (with a division by z)', eq: 'z^n + c/z', z0: '1', dist: 6 },
  // Negative powers. The centre point is sent to infinity, so a path is thrown far out only by passing close to it.
  { name: 'z⁻ⁿ + c  (negative power)', eq: 'z^-n + c', z0: 'c', target: [0, 0, 0], dist: 6.5, julia: { dist: 4.8 },
    note: 'A negative power sends the centre point to infinity, so z starts at c instead of 0. The only paths thrown far out are the ones that pass close to the centre. In the plane the set is a star with n + 1 points.' },
  // z0 = 4c + 1/4 is where every critical orbit of z² + c/z² arrives after two steps, so no root of c is needed.
  { name: 'z² + c·z⁻²  (square against division)', eq: 'z^2 + c*z^-2', z0: '4*c + 0.25', target: [0, 0, 0], dist: 1.7, yaw: -1.0, pitch: 1.1, cut: 0, julia: { dist: 4.8 },
    note: 'The square pushes points outward and the division throws points near the centre far out, which leaves a small solid full of holes. It is worth cutting open at z = 0, where the cut face is the flat picture. The start value 4c + 1/4 is the one that makes this the true Mandelbrot-style set of the formula.' },
];

""" + s[j:]

# ---- every number becomes a float literal the shader accepts (1e15 and beyond used to come out as an integer)
rep("""  const flt = x => (Number.isInteger(x) && Math.abs(x) < 1e15 ? x + '.0' : String(x));""",
    """  const flt = x => (!Number.isInteger(x) ? String(x) : Math.abs(x) < 1e15 ? x + '.0' : x.toExponential());""")
rep("""    const m = /^(\\d+\\.?\\d*(?:[eE][+-]?\\d+)?|\\.\\d+)/.exec(s.slice(i));
    if (m) { i += m[0].length; const x = parseFloat(m[0]); return { c: flt(x), t: 's', lit: x }; }""",
    """    const m = /^(\\d+\\.?\\d*(?:[eE][+-]?\\d+)?|\\.\\d+)/.exec(s.slice(i));
    if (m) {
      i += m[0].length;
      const x = parseFloat(m[0]);
      if (!(Math.abs(x) <= 1e30)) throw new Error(`The number ${m[0]} is too large. Numbers up to 1e30 work.`);
      return { c: flt(x), t: 's', lit: x, k: () => x };
    }""")

# ---- the parser also reports which powers of a point the formula takes
rep("""function compileFormula(text, allowZ, n2) {
  const s = aprPlain(text);
  let i = 0;""",
"""// Parses a formula. Returns its shader code and `powers`: one entry for every power the formula takes of a
// point (a division by a point is the power −1), each a function of n giving the exponent as a number, or
// null where the exponent depends on z or c.
function aprParse(text, allowZ, n2) {
  const s = aprPlain(text), powers = [];
  // a number-valued node keeps k(n), its value for a given n, when that is known without z and c
  const both = (a, b, f) => (a.k && b.k ? n => f(a.k(n), b.k(n)) : undefined);
  let i = 0;""")
rep("""  const times = (a, b) => (a.t === 's' && b.t === 's' ? { c: `(${a.c} * ${b.c})`, t: 's' } :""",
    """  const times = (a, b) => (a.t === 's' && b.t === 's' ? { c: `(${a.c} * ${b.c})`, t: 's', k: both(a, b, (x, y) => x * y) } :""")
rep("""  const over = (a, b) => (b.t === 's' ? (a.t === 's' ? { c: quot(a.c, b), t: 's' } : { c: `smul(${quot('1.0', b)}, ${a.c})`, t: 'v' }) : { c: `mul(${V(a)}, pw(${b.c}, -1.0))`, t: 'v' });""",
    """  const over = (a, b) => {
    if (b.t === 's') return a.t === 's' ? { c: quot(a.c, b), t: 's', k: both(a, b, (x, y) => x / y) } : { c: `smul(${quot('1.0', b)}, ${a.c})`, t: 'v' };
    powers.push(() => -1);
    return { c: `mul(${V(a)}, pw(${b.c}, -1.0))`, t: 'v' };
  };""")
rep("""    abs: a => ({ c: `abs(${a.c})`, t: a.t }),""",
    """    abs: a => ({ c: `abs(${a.c})`, t: a.t, k: a.t === 's' && a.k ? n => Math.abs(a.k(n)) : undefined }),""")
rep("""      a = a.t === 's' && b.t === 's' ? { c: `(${a.c} ${ch} ${b.c})`, t: 's' } : { c: `(${V(a)} ${ch} ${V(b)})`, t: 'v' };""",
    """      a = a.t === 's' && b.t === 's' ? { c: `(${a.c} ${ch} ${b.c})`, t: 's', k: both(a, b, ch === '+' ? (x, y) => x + y : (x, y) => x - y) } : { c: `(${V(a)} ${ch} ${V(b)})`, t: 'v' };""")
rep("""    if (ch === '-') { i++; const a = unary(); return { c: `(-${a.c})`, t: a.t, lit: a.lit === undefined ? undefined : -a.lit }; }""",
    """    if (ch === '-') { i++; const a = unary(); return { c: `(-${a.c})`, t: a.t, lit: a.lit === undefined ? undefined : -a.lit, k: a.t === 's' && a.k ? n => -a.k(n) : undefined }; }""")
rep("""    if (a.t === 's') return { c: `aprSPow(${a.c}, ${b.c})`, t: 's' };   // real power of a real number, finite at 0 and for a negative base
    if (b.lit === 2 || (b.isN && n2)) return { c: `sqr(${a.c})`, t: 'v' };""",
    """    if (a.t === 's') return { c: `aprSPow(${a.c}, ${b.c})`, t: 's', k: both(a, b, Math.pow) };   // real power of a real number, finite at 0 and for a negative base
    powers.push(b.k || null);
    if (b.lit === 2 || (b.isN && n2)) return { c: `sqr(${a.c})`, t: 'v' };""")
rep("""    if (name === 'n') return { c: 'uPow', t: 's', isN: true };""",
    """    if (name === 'n') return { c: 'uPow', t: 's', isN: true, k: n => n };""")
rep("""    if (name === 'pi') return { c: flt(PI), t: 's', lit: PI };""",
    """    if (name === 'pi') return { c: flt(PI), t: 's', lit: PI, k: () => PI };""")
rep("""  const out = expr();
  if (peek() !== undefined) throw new Error(`“${s[i]}” is unexpected here.`);
  return V(out);
}""",
"""  const out = expr();
  if (peek() !== undefined) throw new Error(`“${s[i]}” is unexpected here.`);
  return { code: V(out), powers };
}
function compileFormula(text, allowZ, n2) { return aprParse(text, allowZ, n2).code; }
// The powers a formula takes of a point, as numbers for a given n, in the order they are worked out
// ('z^-n + c' at n = 2 gives [-2]; 'z^2 + c/z' gives [2, -1]). Powers that depend on z or c are left out,
// and a formula that does not parse gives an empty list.
function formulaPowers(text, n) {
  try { return aprParse(text, true, false).powers.map(f => (f ? f(n) : NaN)).filter(Number.isFinite); }
  catch (e) { return []; }
}""")
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
