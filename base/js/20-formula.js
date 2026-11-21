const PRESETS = [
  { name: 'zⁿ + c  (Mandelbrot)', eq: 'z^n + c', z0: '0' },
  { name: 'c·z·(1 − z)  (lambda)', eq: 'c*z*(1 - z)', z0: '0.5', target: [1, 0, 0], dist: 10 },
  { name: '|z|ⁿ + c  (burning ship)', eq: 'abs(z)^n + c', z0: '0' },
  { name: 'conj(z)ⁿ + c  (tricorn)', eq: 'conj(z)^n + c', z0: '0' },
  { name: 'z³ − z + c  (cubic)', eq: 'z^3 - z + c', z0: '0.57735' },
  { name: 'zⁿ + c/z  (with a pole)', eq: 'z^n + c/z', z0: '1', dist: 6 },
];

// ---------- equation -> shader code. A formula is typed with z, c, n, i, j; products and powers are
// handed to the approach's mul() and pw(), so one formula means something different under each approach.
function compileFormula(text, allowZ, n2) {
  const s = text;
  let i = 0;
  const peek = () => { while (i < s.length && /\s/.test(s[i])) i++; return s[i]; };
  const flt = x => (Number.isInteger(x) && Math.abs(x) < 1e15 ? x + '.0' : String(x));
  const V = e => (e.t === 'v' ? e.c : `vec3(${e.c}, 0.0, 0.0)`);
  const need = ch => { if (peek() !== ch) throw new Error(`A “${ch}” is missing.`); i++; };
  const times = (a, b) => (a.t === 's' && b.t === 's' ? { c: `(${a.c} * ${b.c})`, t: 's' } : a.t === 's' ? { c: `smul(${a.c}, ${b.c})`, t: 'v' } : b.t === 's' ? { c: `smul(${b.c}, ${a.c})`, t: 'v' } : { c: `mul(${a.c}, ${b.c})`, t: 'v' });
  const over = (a, b) => (b.t === 's' ? (a.t === 's' ? { c: `(${a.c} / ${b.c})`, t: 's' } : { c: `smul(1.0 / ${b.c}, ${a.c})`, t: 'v' }) : { c: `mul(${V(a)}, pw(${b.c}, -1.0))`, t: 'v' });
  const FUNCS = {
    abs: a => ({ c: `abs(${a.c})`, t: a.t }),
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
      a = a.t === 's' && b.t === 's' ? { c: `(${a.c} ${ch} ${b.c})`, t: 's' } : { c: `(${V(a)} ${ch} ${V(b)})`, t: 'v' };
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
    if (ch === '-') { i++; const a = unary(); return { c: `(-${a.c})`, t: a.t, lit: a.lit === undefined ? undefined : -a.lit }; }
    if (ch === '+') { i++; return unary(); }
    return power();
  }
  function power() {
    const a = atom();
    if (peek() !== '^') return a;
    i++;
    const b = unary();
    if (b.t !== 's') throw new Error('An exponent has to be a plain number, as in z^3 or z^n.');
    if (a.t === 's') return { c: `pow(${a.c}, ${b.c})`, t: 's' };
    if (b.lit === 2 || (b.isN && n2)) return { c: `sqr(${a.c})`, t: 'v' };
    return { c: `pw(${a.c}, ${b.c})`, t: 'v' };
  }
  function atom() {
    const ch = peek();
    if (ch === undefined) throw new Error('The formula stops too early.');
    if (ch === '(') { i++; const a = expr(); need(')'); return a; }
    const m = /^(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)/.exec(s.slice(i));
    if (m) { i += m[0].length; const x = parseFloat(m[0]); return { c: flt(x), t: 's', lit: x }; }
    const id = /^[A-Za-z_]\w*/.exec(s.slice(i));
    if (!id) throw new Error(`“${ch}” is not something a formula can use here.`);
    i += id[0].length;
    const name = id[0].toLowerCase();
    if (FUNCS[name]) { need('('); const a = expr(); need(')'); return FUNCS[name](a); }
    if (name === 'z') { if (!allowZ) throw new Error('The start value can use c and numbers, but not z.'); return { c: 'z', t: 'v' }; }
    if (name === 'c') return { c: 'c', t: 'v' };
    if (name === 'n') return { c: 'uPow', t: 's', isN: true };
    if (name === 'i') return { c: 'vec3(0.0, 1.0, 0.0)', t: 'v' };
    if (name === 'j') return { c: 'vec3(0.0, 0.0, 1.0)', t: 'v' };
    if (name === 'pi') return { c: flt(PI), t: 's', lit: PI };
    throw new Error(`“${id[0]}” is not a name the formula knows. Use z, c, n, i, j, and write products with *, as in c*z.`);
  }
  const out = expr();
  if (peek() !== undefined) throw new Error(`“${s[i]}” is unexpected here.`);
  return V(out);
}
