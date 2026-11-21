"""One-off: the Learn note no longer names "Mandelbulb, classic" as the one entry that does not keep the flat
picture. It lists the entries that do not, found by the same probe the note already uses. Run from the project root."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '65-learn-steps.js')
s = io.open(p, encoding='utf-8').read()
a1 = "    const same = learnAgree(F, power, space === 1 ? LEARN_PROBE_LINE : LEARN_PROBE_FLAT), where = space === 1 ? 'on the x-axis' : 'in the plane z = 0';\n"
b1 = a1 + "    const odd = learnOdd(space), names = odd.map(a => `“${a.name}”`), list = names.length > 1 ? names.slice(0, -1).join(', ') + ' and ' + names[names.length - 1] : names[0];\n"
a2 = "every approach in the list does this ${where}. The one exception is “Mandelbulb, classic”, which does not keep the flat picture.`\n      + (id === 'classic' ? (same"
b2 = "every approach in the list does this ${where}.` + (odd.length === 1 ? ` The one exception is ${list}, which does not keep the flat picture.` : odd.length ? ` The exceptions are ${list}, which do not keep the flat picture.` : '')\n      + (odd.some(a => a.id === id) ? (same"
a3 = "\nfunction learnPlan(o = {}) {\n"
b3 = """
// The entries that do not follow the flat rule at the power 2 with their dials at the starting values: on the
// x-axis (space 1) or in the plane z = 0 (space 2). Found by the probe, not listed by hand, and found once.
const LEARN_ODD = {};
function learnOdd(space) {
  return LEARN_ODD[space] || (LEARN_ODD[space] = APPROACHES.filter(a => MATH[a.id]
    && !learnAgree(v => MATH[a.id](v, 2, specDefaults(a.params || [])), v => learnFlatRule(v, 2), space === 1 ? LEARN_PROBE_LINE : LEARN_PROBE_FLAT)));
}
function learnPlan(o = {}) {
"""
for a, b in ((a1, b1), (a2, b2), (a3, b3)):
    assert s.count(a) == 1, a
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('learn note updated')
