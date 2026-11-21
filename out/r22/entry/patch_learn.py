"""Round 22, entry: src/js/65-learn-steps.js (the Stretch wording; c handed to the rule; a line for the two entries
whose later squarings differ) and one line in src/js/90-boot.js (CARRY for the tests). Run once."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
def patch(rel, pairs):
    P = os.path.join(ROOT, *rel.split('/'))
    s = io.open(P, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (rel, s.count(old), old)
        s = s.replace(old, new)
    io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
    print('patched', rel)

patch('src/js/65-learn-steps.js', [
("""// the stretch that follows learnOwn: the length goes to the rule's length (the rule's length must not depend on the direction)
function learnStretchTo(F) {
  const f = (v, t) => learnScale(v, len(F(v)), t, F);
  const say = (a, b) => {
    if (!(len(a) > 0)) return len(b) > 0 ? `The point is at the origin, and the rule sends the origin outward: to a length of ${learnNum(len(b))}.` : 'The point is at the origin, and it stays there.';
    return `Then the length goes from ${learnNum(len(a))} to the rule’s length, ${learnNum(len(b))}.`;
  };
  return learnMove('stretch', 'Stretch', f, say);
}
""",
"""// The Stretch of a rule whose length is the plain power of the length, |F(v)| = |v|^n, for a reader who takes "stretch"
// for doubling (round 22): the words of learnSayStretch, and for a whole power above 1 the contrast said outright.
function learnSayPower(n, r, R) {
  if (!(n > 1) || !aprWhole(n) || !(r > 0) || R >= 1e18 || learnIs(r, 1)) return learnSayStretch(n, 'Its length', r, R);
  const how = learnIs(n, 2) ? 'multiplied by itself, not doubled' : learnIs(n, 3) ? 'multiplied by itself twice, not tripled' : `multiplied by itself ${aprNum(n - 1)} times, not multiplied by ${aprNum(n)}`;
  const ex = r < 1 ? 2 : 0.5, show = x => String(+x.toPrecision(3));
  return `Its length is ${how}: ${learnNum(r)} becomes ${learnNum(R)}, and ${show(ex)} would become ${show(ex ** n)}. A length under 1 gets shorter, a length over 1 gets longer.`;
}
// the stretch that follows learnOwn: the length goes to the rule's length (the rule's length must not depend on the direction).
// n: the power. Where the rule's length is the plain power of the point's length (to rounding), the move says so in plain
// words (learnSayPower); for any other rule it keeps the sentence it had.
function learnStretchTo(F, n) {
  const f = (v, t) => learnScale(v, len(F(v)), t, F);
  const say = (a, b) => {
    const r = len(a), R = len(b);
    if (!(r > 0)) return R > 0 ? `The point is at the origin, and the rule sends the origin outward: to a length of ${learnNum(R)}.` : 'The point is at the origin, and it stays there.';
    if (n !== undefined && Math.abs(R - learnPowLen(r, n)) <= 1e-9 * Math.max(1, R)) return learnSayPower(n, r, R);
    return `Then the length goes from ${learnNum(r)} to the rule’s length, ${learnNum(R)}.`;
  };
  return learnMove('stretch', 'Stretch', f, say);
}
"""),
("    && !learnAgree(v => MATH[a.id](v, 2, specDefaults(a.params || [])), v => learnFlatRule(v, 2), space === 1 ? LEARN_PROBE_LINE : LEARN_PROBE_FLAT)));",
 "    && !learnAgree(v => MATH[a.id](v, 2, specDefaults(a.params || []), [0, 0, 0]), v => learnFlatRule(v, 2), space === 1 ? LEARN_PROBE_LINE : LEARN_PROBE_FLAT)));"),
("  const F = v => MATH[id](v, n, q);\n  const moves = mirror ? [mirror] : [];",
 "  // (the fourth argument is for the entries whose orbit carries something, see CARRY in 10-approaches.js: their one\n  // squaring is the first of an orbit with this c; every other entry does not look at it)\n  const F = v => MATH[id](v, n, q, c);\n  const moves = mirror ? [mirror] : [];"),
("      if (even) moves.push(learnOwn(F, false), learnStretchTo(F));",
 "      if (even) moves.push(learnOwn(F, false), learnStretchTo(F, n));"),
("with these dials the rule’s length depends on the direction, so the two cannot be shown apart.');",
 "with these dials the rule’s length depends on the direction, so the two cannot be shown apart.')\n        + (typeof CARRY !== 'undefined' && CARRY[id] ? ' In this entry an orbit carries something from step to step, and these moves show its first squaring only: after “Next step” the moves on show are still those of a first squaring, not the ones the entry’s later squarings make.' : '');"),
])
patch('src/js/90-boot.js', [
("if (typeof APPROACH_GROUPS !== 'undefined') window.squaringLab.APPROACH_GROUPS = APPROACH_GROUPS;\n",
 "if (typeof APPROACH_GROUPS !== 'undefined') window.squaringLab.APPROACH_GROUPS = APPROACH_GROUPS;\nif (typeof CARRY !== 'undefined') window.squaringLab.CARRY = CARRY;\n"),
])
