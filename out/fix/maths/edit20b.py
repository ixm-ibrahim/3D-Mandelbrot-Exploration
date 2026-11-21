import io, sys
p = 'src/js/20-formula.js'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ("""// Parses a formula. Returns its shader code and `powers`: one entry for every power the formula takes of a
// point (a division by a point is the power −1), each a function of n giving the exponent as a number, or
// null where the exponent depends on z or c.""",
  """// Parses a formula. Returns its shader code and `powers`: one entry for every power the formula takes of
// something that holds z (dividing by it is the power −1), each a function of n giving the exponent as a
// number, or null where the exponent itself depends on z or c."""),
 ("""  const both = (a, b, f) => (a.k && b.k ? n => f(a.k(n), b.k(n)) : undefined);""",
  """  const both = (a, b, f) => (a.k && b.k ? n => f(a.k(n), b.k(n)) : undefined);
  const hasZ = e => /\bz\b/.test(e.c);   // in the shader code z is written as the bare name z, and nothing else is"""),
 ("""    powers.push(() => -1);""", """    if (hasZ(b)) powers.push(() => -1);"""),
 ("""    powers.push(b.k || null);""", """    if (hasZ(a)) powers.push(b.k || null);"""),
 ("""// The powers a formula takes of a point, as numbers for a given n, in the order they are worked out""",
  """// The powers a formula takes of z, as numbers for a given n, in the order they are worked out"""),
]
for old, new in pairs:
    if s.count(old) != 1:
        sys.exit('expected one match for: ' + old[:60])
    s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
