import io
def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) >= 1, a[:60]
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

sub('src/js/65-learn-steps.js', [
 # numbers: a coordinate is always two decimals; a length that is tiny but not 0 is written with a power of ten
 ("""function learnNum(x) {
  if (!isFinite(x)) return 'more than the lab can count';
  const a = Math.abs(x);
  if (a >= 1e6 || (a > 0 && a < 0.005)) {""",
  """function learnNum(x, coord) {
  if (!isFinite(x)) return 'more than the lab can count';
  const a = Math.abs(x);
  if (a >= 1e6 || (!coord && a > 1e-12 && a < 0.005)) {"""),
 ("(space === 2 ? [v[0], v[1]] : v).map(learnNum).join(', ')", "(space === 2 ? [v[0], v[1]] : v).map(x => learnNum(x, true)).join(', ')"),
 ("const learnPt = (v, space) => (space === 1 ? learnNum(v[0]) :", "const learnPt = (v, space) => (space === 1 ? learnNum(v[0], true) :"),
 ("""  return learnMove('shift', 'Add c', f, (a, b) => (len(c) > 0
    ? `Add c""", """  return learnMove('shift', 'Add c', f, (a, b) => (space === 1 && Math.abs(a[1]) > 1e-9 * (1 + len(a))
    ? `Add c: the point moves by ${learnNum(c[0], true)} along the line, but it is still off the line: ${learnNum(Math.abs(a[1]))} out in the direction the line does not have.`
    : len(c) > 0
    ? `Add c"""),
 ("    if (a[2] === 0) return 'The point lies in the flat plane: its latitude is 0°, and any number times 0° is 0°. It does not lean.';",
  "    if (learnFlat(a)) return 'The point lies in the flat plane: its latitude is 0°, and any number times 0° is 0°. It does not lean.';"),
 ("const learnLat = v =>", "const learnFlat = v => Math.abs(v[2]) <= 1e-12 * len(v);   // in the plane z = 0, for the wording\nconst learnLat = v =>"),
 ("a[2] === 0 ? 'The point lies in the flat plane: its latitude is 0°.'", "learnFlat(a) ? 'The point lies in the flat plane: its latitude is 0°.'"),
 ("!classic && a[2] === 0 ? ' Any number times 0° is 0°.'", "!classic && learnFlat(a) ? ' Any number times 0° is 0°.'"),
 ("classic && a[2] === 0 && Math.abs(b[2]) > 1e-9 * len(b)", "classic && learnFlat(a) && Math.abs(b[2]) > 1e-9 * len(b)"),
 ("${learnNum(learnMerc(a))} on the scale", "${learnNum(learnMerc(a), true)} on the scale"),
 ("${learnNum(learnMerc(b))}, which is latitude", "${learnNum(learnMerc(b), true)}, which is latitude"),
 ("`The height is ${learnNum(a[2])}. The power", "`The height is ${learnNum(a[2], true)}. The power"),
 ("y goes to its mirror value, from ${learnNum(a[1])} to ${learnNum(b[1])}.", "y goes to its mirror value, from ${learnNum(a[1], true)} to ${learnNum(b[1], true)}."),
 ("`${'xyz'[i]} goes from ${learnNum(a[i])} to ${learnNum(b[i])}`", "`${'xyz'[i]} goes from ${learnNum(a[i], true)} to ${learnNum(b[i], true)}`"),
])
sub('out/r13/steps/test.js', [
 ("const As = new Set(A.filter(isFinite).map(x => String(Math.abs(Math.round(x))))), Ns = new Set();", "const As = A.filter(isFinite).map(Math.abs), Ns = new Set();"),
 ("if (mm[4]) { if (!As.has(mm[1].replace('−', ''))) return", "if (mm[4]) { const tv = +mm[1].replace('−', ''); if (!As.some(x => Math.abs(x - tv) <= 0.5 + 1e-6)) return"),
])
