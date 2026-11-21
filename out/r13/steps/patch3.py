def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (s.count(a), a[:70])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

sub('src/js/65-learn-steps.js', [
 ("    if (!(rho > 0)) return `The point is on the z-axis, where it has no ${what}. This turn leaves it where it is.`;",
  "    if (!(rho > 0)) return what === 'flat' ? 'The point is on the z-axis: its flat part (x, y) is 0, so there is nothing to turn.' : `The point is on the z-axis, where it has no ${what}. This turn leaves it where it is.`;"),
 ("function learnSayStretch(n, what, r, R) {\n  if (!(r > 0)) return R > 0 ? `The point is at the origin, and this power sends the origin outward: to a length of ${learnNum(R)}.` : `The point is at the origin: its length is 0, and 0 ${learnPowWord(n)} is still 0. It stays.`;",
  "function learnSayStretch(n, what, r, R, flat) {\n  if (!(r > 0)) return R > 0 ? `${flat ? 'The flat part of the point is 0' : 'The point is at the origin'}, and this power sends it outward: to a length of ${learnNum(R)}.`\n    : `${flat ? 'The flat part of the point is 0' : 'The point is at the origin: its length is 0'}, and 0 ${learnPowWord(n)} is still 0. It stays.`;"),
 ("learnSayStretch(m, 'The length of the flat part', Math.hypot(a[0], a[1]), Math.hypot(b[0], b[1])) + ' The height is not touched.'",
  "learnSayStretch(m, 'The length of the flat part', Math.hypot(a[0], a[1]), Math.hypot(b[0], b[1]), true) + ' The height is not touched.'"),
 ("${learnMul(n)}${learnDeg(to)}: it ends ${learnDeg(end)} from ${pos}.`;",
  "${learnMul(n)}${learnDeg(to)}: it ${end < 0.01 ? 'lands on ' + pos : `ends ${learnDeg(end)} from ${pos}`}.`;"),
 ("    return `The rule sends this direction ${learnDeg(ang)} round the sphere, and the point goes there the short way.` + lens;",
  "    if (ang > PI - 1e-9) return 'The rule sends this direction to the exact opposite one, half way round the sphere. No way round is shorter than another, so one is picked.' + lens;\n    return `The rule sends this direction ${learnDeg(ang)} round the sphere, and the point goes there the short way.` + lens;"),
])
