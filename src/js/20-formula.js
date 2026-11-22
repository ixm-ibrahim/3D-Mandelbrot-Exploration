// Equations: the equation presets, and the parser that turns a typed formula into shader code.
// A preset is its name, eq and z0 (the formula and its start value), with an optional note on what the picture
// shows. It may add view hints, tuned for the Mandelbrot solid at n = 2 with the default approach:
//   target, dist, yaw, pitch    a first camera (angles in radians)
//   cut                         a height at which the solid is worth cutting open
const PRESETS = [
  { name: 'zⁿ + c  (Mandelbrot)', eq: 'z^n + c', z0: '0' },
  { name: 'c·z·(1 − z)  (lambda)', eq: 'c*z*(1 - z)', z0: '0.5', target: [1, 0, 0], dist: 10 },
  { name: '|z|ⁿ + c  (burning ship)', eq: 'abs(z)^n + c', z0: '0' },
  { name: 'conj(z)ⁿ + c  (tricorn)', eq: 'conj(z)^n + c', z0: '0' },
  { name: 'z³ − z + c  (cubic)', eq: 'z^3 - z + c', z0: '0.57735' },
  { name: 'zⁿ + c/z  (with a division by z)', eq: 'z^n + c/z', z0: '1', dist: 6 },
  { name: 'z⁻ⁿ + c  (negative power)', eq: 'z^-n + c', z0: 'c', target: [0, 0, 0], dist: 6.5,
    note: 'A negative power sends the centre point to infinity, so z starts at c instead of 0. The only paths thrown far out are the ones that pass close to the centre. In the plane the set is a star with n + 1 points.' },
  // z0 = 4c + 1/4 is where every critical orbit of z² + c/z² arrives after two steps, so no root of c is needed.
  { name: 'z² + c·z⁻²  (square against division)', eq: 'z^2 + c*z^-2', z0: '4*c + 0.25', target: [0, 0, 0], dist: 1.7, yaw: -1.0, pitch: 1.1, cut: 0,
    note: 'The square pushes points outward and the division throws points near the centre far out, which leaves a small solid full of holes. It is worth cutting open at z = 0, where the cut face is the flat picture. The start value 4c + 1/4 is the one that makes this the true Mandelbrot-style set of the formula.' },
];

// From an equation to shader code. A formula is typed with z, c, n, i, j. Products and powers are handed to
// the approach's mul() and pw(), so one formula means something different under each approach.

// Formulas are pasted the way the page prints them (z² − c·z⁻¹): this puts those glyphs back into typed form.
const APR_SUPER = '⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺ⁿ', APR_TYPED = '0123456789-+n';
function aprPlain(text) {
  return text.replace(/[−–—]/g, '-').replace(/[·×∙⋅]/g, '*').replace(/÷/g, '/').replace(/π/g, 'pi')
    .replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺ⁿ]+/g, m => '^(' + [...m].map(ch => APR_TYPED[APR_SUPER.indexOf(ch)]).join('') + ')');
}
// Parses a formula. Returns its shader code and `powers`: one entry for every power the formula takes of
// something that holds z (dividing by it is the power −1), each a function of n giving the exponent as a
// number, or null where the exponent itself depends on z or c.
function aprParse(text, allowZ, n2) {
  const s = aprPlain(text), powers = [];
  // a number-valued node keeps k(n), its value for a given n, when that is known without z and c
  const both = (a, b, f) => (a.k && b.k ? n => f(a.k(n), b.k(n)) : undefined);
  const hasZ = e => /\bz\b/.test(e.c);   // in the shader code z is written as the bare name z, and nothing else is
  let i = 0;
  const peek = () => { while (i < s.length && /\s/.test(s[i])) i++; return s[i]; };
  const flt = x => (!Number.isInteger(x) ? String(x) : Math.abs(x) < 1e15 ? x + '.0' : x.toExponential());
  const V = e => (e.t === 'v' ? e.c : `vec3(${e.c}, 0.0, 0.0)`);
  const need = ch => { if (peek() !== ch) throw new Error(`A “${ch}” is missing.`); i++; };
  const times = (a, b) => (a.t === 's' && b.t === 's' ? { c: `(${a.c} * ${b.c})`, t: 's', k: both(a, b, (x, y) => x * y) } : a.t === 's' ? { c: `smul(${a.c}, ${b.c})`, t: 'v' } : b.t === 's' ? { c: `smul(${b.c}, ${a.c})`, t: 'v' } : { c: `mul(${a.c}, ${b.c})`, t: 'v' });
  // a over b. A typed number divides directly; a quantity that can reach zero (n, len(z)) goes through
  // aprDiv, which keeps the quotient finite. Dividing by a point is multiplying by its power −1.
  const quot = (a, b) => {
    if (b.lit === 0) throw new Error('The formula divides by zero.');
    return b.lit === undefined ? `aprDiv(${a}, ${b.c})` : `(${a} / ${b.c})`;
  };
  const over = (a, b) => {
    if (b.t === 's') return a.t === 's' ? { c: quot(a.c, b), t: 's', k: both(a, b, (x, y) => x / y) } : { c: `smul(${quot('1.0', b)}, ${a.c})`, t: 'v' };
    if (hasZ(b)) powers.push(() => -1);
    return { c: `mul(${V(a)}, pw(${b.c}, -1.0))`, t: 'v' };
  };
  const FUNCS = {
    abs: a => ({ c: `abs(${a.c})`, t: a.t, k: a.t === 's' && a.k ? n => Math.abs(a.k(n)) : undefined }),
    conj: a => ({ c: `(${V(a)} * vec3(1.0, -1.0, -1.0))`, t: 'v' }),
    len: a => ({ c: `length(${V(a)})`, t: 's' }),
  };
  function expr() {
    let a = term();
    for (;;) {
      const ch = peek();
      if (ch !== '+' && ch !== '-') return a;
      i++;
      const b = term();
      a = a.t === 's' && b.t === 's' ? { c: `(${a.c} ${ch} ${b.c})`, t: 's', k: both(a, b, ch === '+' ? (x, y) => x + y : (x, y) => x - y) } : { c: `(${V(a)} ${ch} ${V(b)})`, t: 'v' };
    }
  }
  function term() {
    let a = unary();
    for (;;) {
      const ch = peek();
      if (ch === '*' || ch === '/') { i++; const b = unary(); a = ch === '*' ? times(a, b) : over(a, b); }
      else if (ch !== undefined && /[A-Za-z_(0-9.]/.test(ch)) a = times(a, power()); // 2z, 3(z + 1)
      else return a;
    }
  }
  function unary() {
    const ch = peek();
    if (ch === '-') { i++; const a = unary(); return { c: `(-${a.c})`, t: a.t, lit: a.lit === undefined ? undefined : -a.lit, k: a.t === 's' && a.k ? n => -a.k(n) : undefined }; }
    if (ch === '+') { i++; return unary(); }
    return power();
  }
  function power() {
    const a = atom();
    if (peek() !== '^') return a;
    i++;
    const b = unary();
    if (b.t !== 's') throw new Error('An exponent has to be a plain number, as in z^3, z^-2 or z^n.');
    if (a.t === 's') return { c: `aprSPow(${a.c}, ${b.c})`, t: 's', k: both(a, b, Math.pow) };   // real power of a real number, finite at 0 and for a negative base
    if (hasZ(a)) powers.push(b.k || null);
    if (b.lit === 2 || (b.isN && n2)) return { c: `sqr(${a.c})`, t: 'v' };
    return { c: `pw(${a.c}, ${b.c})`, t: 'v' };
  }
  function atom() {
    const ch = peek();
    if (ch === undefined) throw new Error('The formula stops too early.');
    if (ch === '(') { i++; const a = expr(); need(')'); return a; }
    const m = /^(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)/.exec(s.slice(i));
    if (m) {
      i += m[0].length;
      const x = parseFloat(m[0]);
      if (!(Math.abs(x) <= 1e30)) throw new Error(`The number ${m[0]} is too large. Numbers up to 1e30 work.`);
      return { c: flt(x), t: 's', lit: x, k: () => x };
    }
    const id = /^[A-Za-z_]\w*/.exec(s.slice(i));
    if (!id) throw new Error(`“${ch}” is not something a formula can use here.`);
    i += id[0].length;
    const name = id[0].toLowerCase();
    if (FUNCS[name]) { need('('); const a = expr(); need(')'); return FUNCS[name](a); }
    if (name === 'z') { if (!allowZ) throw new Error('The start value can use c and numbers, but not z.'); return { c: 'z', t: 'v' }; }
    if (name === 'c') return { c: 'c', t: 'v' };
    if (name === 'n') return { c: 'uPow', t: 's', isN: true, k: n => n };
    if (name === 'i') return { c: 'vec3(0.0, 1.0, 0.0)', t: 'v' };
    if (name === 'j') return { c: 'vec3(0.0, 0.0, 1.0)', t: 'v' };
    if (name === 'pi') return { c: flt(PI), t: 's', lit: PI, k: () => PI };
    throw new Error(`“${id[0]}” is not a name the formula knows. Use z, c, n, i, j, and write products with *, as in c*z.`);
  }
  const out = expr();
  if (peek() !== undefined) throw new Error(`“${s[i]}” is unexpected here.`);
  return { code: V(out), powers };
}
function compileFormula(text, allowZ, n2) { return aprParse(text, allowZ, n2).code; }
// The powers a formula takes of z, as numbers for a given n, in the order they are worked out
// ('z^-n + c' at n = 2 gives [-2]; 'z^2 + c/z' gives [2, -1]). Powers that depend on z or c are left out,
// and a formula that does not parse gives an empty list.
function formulaPowers(text, n) {
  try { return aprParse(text, true, false).powers.map(f => (f ? f(n) : NaN)).filter(Number.isFinite); }
  catch (e) { return []; }
}
