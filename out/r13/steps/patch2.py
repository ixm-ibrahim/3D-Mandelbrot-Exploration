def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (s.count(a), a[:70])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

sub('src/js/65-learn-steps.js', [
 # (b) exactly opposite directions: half a turn
 ("""  let w = sub(e, scl(d, c)), lw = len(w);
  if (lw < 1e-12) {
    if (c > 0) return d;
    w = cross(d, Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0]); lw = len(w);   // exactly opposite: no short way, one is picked
  }
  const om = Math.atan2(lw, c) * t;""",
  """  let w = sub(e, scl(d, c)), lw = len(w), ang = Math.atan2(lw, c);
  if (lw < 1e-12) {
    if (c > 0) return d;
    w = cross(d, Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0]); lw = len(w); ang = PI;   // exactly opposite: no short way, one is picked
  }
  const om = ang * t;"""),
 # (d) the origin: where the rule sends this very point (signed zeros and all)
 ("""// A point at the origin has no direction: `zero` is where the rule itself sends the origin (null: it stays).
function learnScale(v, R, t, zero) {
  const r = len(v);
  if (!(r > 0)) {
    const L = zero ? len(zero) : 0;
    if (!(L > 0)) return [0, 0, 0];
    return scl(zero, t >= 1 ? 1 : Math.exp((1 - t) * Math.log(1e-30) + t * Math.log(L)) / L);
  }""",
  """// A point at the origin has no direction: `rule(v)` is where the rule itself sends it (no rule: it stays).
function learnScale(v, R, t, rule) {
  const r = len(v);
  if (!(r > 0)) {
    const T = rule ? rule(v) : null, L = T ? len(T) : 0;
    if (!(L > 0)) return [0, 0, 0];
    return scl(T, t >= 1 ? 1 : Math.exp((1 - t) * Math.log(1e-30) + t * Math.log(L)) / L);
  }"""),
 ("// The stretch: the length r goes to r^n (the lab's own capped power). zero: where the rule sends the origin.\nfunction learnStretch(n, zero) {\n  const f = (v, t) => learnScale(v, learnPowLen(len(v), n), t, zero);",
  "// The stretch: the length r goes to r^n (the lab's own capped power). rule: the whole power, asked only at the origin.\nfunction learnStretch(n, rule) {\n  const f = (v, t) => learnScale(v, learnPowLen(len(v), n), t, rule);"),
 ("w = learnScale([v[0], v[1], 0], R, t, [R, 0, 0]);", "w = learnScale([v[0], v[1], 0], R, t, p => { const a = Math.atan2(p[1], p[0]) * m; return [R * Math.cos(a), R * Math.sin(a), 0]; });"),
 ("if (!(L * most > 1)) return learnScale(L > 0 ? v : [0, 0, 0], most, t, g);", "if (!(L * most > 1)) return learnScale([0, 0, 0], most, t, () => g);"),
 ("if (!(r > 0)) return together ? learnScale(v, L, t, T) : v;", "if (!(r > 0)) return together ? learnScale(v, L, t, () => T) : v;"),
 ("const f = (v, t) => learnScale(v, len(F(v)), t, F([0, 0, 0]));", "const f = (v, t) => learnScale(v, len(F(v)), t, F);"),
 ("moves.push(learnTurnZ(n, space, 'lean'), learnStretch(n, power([0, 0, 0])));", "moves.push(learnTurnZ(n, space, 'lean'), learnStretch(n, power));"),
 ("    power = F;\n    const zero = F([0, 0, 0]);\n", "    power = F;\n    const zero = F;\n"),
 # (a) the probe directions are made unit vectors
 ("const lens = [0.7, 1.3].map(r => LEARN_PROBE_DIRS.map(d => len(F(scl(d, r)))));", "const lens = [0.7, 1.3].map(r => LEARN_PROBE_DIRS.map(d => len(F(scl(norm(d), r)))));"),
 # (c) the lean of a point closer to a pole than the lab's Mercator scale reaches
 ("""    const m0 = Math.atanh(clamp(v[2] / r, -0.999999, 0.999999)), m = m0 + t * (clamp(n * m0, -20, 20) - m0), u = learnLevel(v), h = r / Math.cosh(m);
    return [h * u[0], h * u[1], r * Math.tanh(m)];
  };
  const say = (a, b) => {
    if (!(len(a) > 0)) return LEARN_NO_DIR;
    if (learnFlat(a))""",
  """    const Z = v[2] / r, m0 = Math.atanh(clamp(Z, -0.999999, 0.999999)), m1 = clamp(n * m0, -20, 20), u = learnLevel(v);
    if (t < 1 && Math.abs(Z) > 0.999999) {     // closer to a pole than the lab's Mercator scale reaches: go evenly in latitude
      const l0 = learnLat(v), l = l0 + t * (Math.atan(Math.sinh(m1)) - l0);
      return [r * Math.cos(l) * u[0], r * Math.cos(l) * u[1], r * Math.sin(l)];
    }
    const m = m0 + t * (m1 - m0), h = r / Math.cosh(m);
    return [h * u[0], h * u[1], r * Math.tanh(m)];
  };
  const say = (a, b) => {
    if (!(len(a) > 0)) return LEARN_NO_DIR;
    if (learnFlat(a))"""),
 ("so the point stays at the pole.';", "so the point stays at the pole, to within a hair.';"),
 (" Very close to a pole (less than a tenth of a degree) the lab stops the scale, and the point starts its lean with a tiny hop.';", "';"),
])
