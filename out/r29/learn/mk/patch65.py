# Applies the round-29 edits to 65-learn-steps.js: reads base21a's file, writes the overlay copy.
# (The overlay copy is always made afresh from the frozen file, so this can be run again at any time.)
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
SRC = os.path.join(ROOT, 'base21a', 'js', '65-learn-steps.js')
DST = os.path.join(ROOT, 'out', 'r29', 'learn', 'overlay', 'js', '65-learn-steps.js')
s = io.open(SRC, encoding='utf-8').read().replace('\r\n', '\n')
n = [0]


def rep(a, b, count=1):
    global s
    if s.count(a) != count:
        sys.exit('expected %d of %r, found %d' % (count, a[:70], s.count(a)))
    s = s.replace(a, b)
    n[0] += 1


# 1. the header: say what `all` is
rep("// Move = { key, name, say(a, b), at(v, t), hinge(v), sheet(v), hidden }\n",
    "// Move = { key, name, say(a, b), at(v, t), hinge(v), sheet(v), hidden, all }\n"
    "//   all (round 29): what the move does to EVERY dot at once, as the end of a sentence that begins with the move's\n"
    "//   name (\"every dot’s angle is doubled\"). \"A whole shape, Move by move\" (67-learn-shape.js) shows it; One point\n"
    "//   does not read it.\n")

# 2. the words for `all`
rep("const LEARN_NO_DIR = ",
    "// (Round 29.) Words for what a move does to every dot at once.\n"
    "const learnTimes = n => (learnIs(n, 2) ? 'doubled' : learnIs(n, 3) ? 'tripled' : `multiplied by ${aprNum(n)}`);\n"
    "const learnAllTurn = (n, what) => (learnIs(n, 1) ? 'the power is 1, so no dot turns' : `every dot’s ${what} is ${learnTimes(n)}`);\n"
    "// what: \"distance from the centre\"; a: where a far dot moves (\"out\"), b: where a near dot moves (\"in\")\n"
    "function learnAllStretch(n, what, a = 'out', b = 'in') {\n"
    "  if (learnIs(n, 1)) return 'the power is 1, so no dot moves';\n"
    "  const how = `every dot’s ${what} is ${learnPowWord(n)}`;\n"
    "  if (n > 1) return `${how}, so dots further out than 1 move ${a} and dots nearer than 1 move ${b}`;\n"
    "  if (n > 0) return `${how}, so every dot moves towards the distance 1`;\n"
    "  if (n < 0) return `${how}: with a negative power near dots go far ${a} and far dots come ${b}`;\n"
    "  return `${how}, so every dot goes to the distance 1`;\n"
    "}\n"
    "const LEARN_NO_DIR = ")

# 3. learnMove carries it
rep("    key, name, hidden: !!o.hidden,\n", "    key, name, hidden: !!o.hidden, all: o.all || '',\n")

# 4. Mirror
rep("    return ch.length ? `${which}, so before anything else ${ch.join(' and ')}, straight through 0.` : `${which}, but for this point that changes nothing.`;\n  });\n",
    "    return ch.length ? `${which}, so before anything else ${ch.join(' and ')}, straight through 0.` : `${which}, but for this point that changes nothing.`;\n"
    "  }, { all: (names.length > 1 ? `the modifiers ${names.join(', ')} are ticked` : `the modifier ${names[0]} is ticked`) + ', so '\n"
    "    + (names.length > 1 ? 'every dot first goes straight to its mirror place'\n"
    "      : on[0] ? 'every dot left of the centre goes straight across to its mirror place on the right'\n"
    "        : on[1] ? 'every dot below the centre goes straight up to its mirror place above'\n"
    "          : on[2] ? 'every dot under the flat plane goes straight up to its mirror place above it'\n"
    "            : fl[1] ? 'every dot goes straight to its mirror place: up becomes down' : 'every dot goes straight to its mirror place on the other side of the flat plane') });\n")

# 5. the turn about the z-axis
rep("  return learnMove('turn', 'Turn', f, say, { hinge: LEARN_Z, sheet: LEARN_PAGE, hidden: space === 1 });\n",
    "  return learnMove('turn', 'Turn', f, say, { hinge: LEARN_Z, sheet: LEARN_PAGE, hidden: space === 1,\n"
    "    all: learnAllTurn(n, space < 3 ? 'angle' : 'angle around the z-axis') + (what === 'flat' && !learnIs(n, 1) ? '; its height is not touched' : '') });\n")

# 6. the stretch
rep("  return learnMove('stretch', 'Stretch', f, (a, b) => learnSayStretch(n, 'Its length', len(a), len(b)));\n",
    "  return learnMove('stretch', 'Stretch', f, (a, b) => learnSayStretch(n, 'Its length', len(a), len(b)), { all: learnAllStretch(n, 'distance from the centre') });\n")

# 7. the lean of the sphere inversions
rep("  return learnMove('lean', 'Lean', f, say, { hinge: learnLevelHinge, sheet: learnMeridian });\n}\nfunction learnLift(lift) {",
    "  return learnMove('lean', 'Lean', f, say, { hinge: learnLevelHinge, sheet: learnMeridian,\n"
    "    all: learnIs(n, 1) ? 'the power is 1, so no dot leans'\n"
    "      : n > 1 ? 'every dot off the flat plane leans further towards the pole on its side, and never passes over it. Dots in the flat plane stay in it'\n"
    "        : n > 0 ? 'every dot off the flat plane leans back towards it. Dots in the flat plane stay in it'\n"
    "          : 'every dot off the flat plane leans over to the other side of it. Dots in the flat plane stay in it' });\n}\nfunction learnLift(lift) {")

# 8. the lift
rep("  return learnMove('phase', 'Lift', f, say, { hinge: learnLevelHinge, sheet: learnMeridian });\n",
    "  return learnMove('phase', 'Lift', f, say, { hinge: learnLevelHinge, sheet: learnMeridian,\n"
    "    all: `every dot is pushed towards the ${lift < 0 ? 'lower' : 'upper'} pole, each along its own way round: the dial “Lift toward the pole”` });\n")

# 9. a dial that adds an angle
rep("  return learnMove('phase', name, (v, t) => learnRz(v, t * rad), say, { hinge: LEARN_Z, sheet: LEARN_PAGE });\n",
    "  return learnMove('phase', name, (v, t) => learnRz(v, t * rad), say, { hinge: LEARN_Z, sheet: LEARN_PAGE,\n"
    "    all: `all the dots turn together about the z-axis by ${learnDeg(rad)}: ` + (/phase/i.test(label) ? 'one of this approach’s dials adds that turn' : `the dial “${label}”`) });\n")

# 10. the fold
rep("  return learnMove('fold', 'Fold', f, say, { hinge: LEARN_X, sheet: LEARN_YZ });\n",
    "  return learnMove('fold', 'Fold', f, say, { hinge: LEARN_X, sheet: LEARN_YZ,\n"
    "    all: 'every dot turns about the x-axis by its own amount. Dots on two sides of a crease go opposite ways' });\n")

# 11. the Lathe turn
rep("  return learnMove('turn', 'Turn', f, say, {\n    hinge: v => (len(v) > 0 ? learnRz(cross(ex, side(v).u), -tau) : null),\n",
    "  return learnMove('turn', 'Turn', f, say, {\n"
    "    all: learnIs(n, 1) ? 'the power is 1, so no dot turns' : `every dot’s angle away from ${axis} is ${learnTimes(n)}; it swings in the plane that holds that axis and the dot`,\n"
    "    hinge: v => (len(v) > 0 ? learnRz(cross(ex, side(v).u), -tau) : null),\n")

# 12. the spin
rep("  return learnMove('spin', 'Spin', f, say, { hinge: LEARN_X, sheet: LEARN_YZ });\n",
    "  return learnMove('spin', 'Spin', f, say, { hinge: LEARN_X, sheet: LEARN_YZ,\n"
    "    all: `every dot’s angle round the x-axis is multiplied by ${aprNum(spin)}: the dial “Spin multiplier”` });\n")

# 13. the turn back
rep("  return learnMove('back', 'Turn back', (v, t) => learnRz(v, t * ang), say, { hinge: LEARN_Z, sheet: LEARN_PAGE });\n",
    "  return learnMove('back', 'Turn back', (v, t) => learnRz(v, t * ang), say, { hinge: LEARN_Z, sheet: LEARN_PAGE,\n"
    "    all: Math.abs(ang) < 1e-12 ? 'there is nothing to turn back, so no dot moves' : `all the dots turn back together about the z-axis by ${learnDeg(Math.abs(ang))}` });\n")

# 14. the Mandelbulb lean
rep("  return learnMove('lean', 'Lean', f, say, { hinge: learnLevelHinge, sheet: learnMeridian });\n}\n// Split:",
    "  return learnMove('lean', 'Lean', f, say, { hinge: learnLevelHinge, sheet: learnMeridian,\n"
    "    all: (learnIs(n, 1) ? `the power is 1, so every dot keeps its angle ${classic ? 'from the z-axis' : 'above the flat plane'}` : `every dot’s angle ${classic ? 'from the z-axis' : 'above the flat plane'} is ${learnTimes(n)}`)\n"
    "      + (phase ? `, and one of this approach’s dials adds ${learnDeg(phase)}` : '') + (classic ? '. A dot may swing past the axis' : '. A dot may swing over a pole') });\n}\n// Split:")

# 15. Split: the flat stretch, the height, inside out
rep("  return learnMove('stretch', 'Stretch', f, (a, b) => learnSayStretch(m, 'The length of the flat part', Math.hypot(a[0], a[1]), Math.hypot(b[0], b[1]), true) + ' The height is not touched.');\n",
    "  return learnMove('stretch', 'Stretch', f, (a, b) => learnSayStretch(m, 'The length of the flat part', Math.hypot(a[0], a[1]), Math.hypot(b[0], b[1]), true) + ' The height is not touched.',\n"
    "    { all: learnAllStretch(m, 'distance from the z-axis', 'away from it', 'towards it') + '. Heights are not touched' });\n")
rep("  return learnMove('own', 'Height', f, say);\n",
    "  return learnMove('own', 'Height', f, say, { all: learnIs(m, 1) ? 'the power is 1, so no dot moves' : `every dot’s height is ${learnPowWord(m)} on its own, like a number on a line. A dot under the flat plane passes through it` });\n")
rep("  return learnMove('own', 'Inside out', f, say);\n",
    "  return learnMove('own', 'Inside out', f, say, { all: 'space is turned inside out: every dot’s distance from the centre becomes 1 divided by it, and its y goes to the mirror value' });\n")

# 16. any other rule: the turn, and the stretch to the rule's length
rep("  return learnMove('own', 'Turn', f, say, { hinge: v => { const s = way(v); return s ? cross(s[0], s[1]) : null; }, sheet: way });\n",
    "  return learnMove('own', 'Turn', f, say, { hinge: v => { const s = way(v); return s ? cross(s[0], s[1]) : null; }, sheet: way,\n"
    "    all: 'every dot swings round the centre, the short way, to the direction this approach sends it to' + (together ? ', and its distance from the centre changes on the way' : '') + '. Each by its own amount: Follow One point shows it for a single dot' });\n")
rep("function learnStretchTo(F, n) {\n", "function learnStretchTo(F, n, plain) {\n")
rep("  return learnMove('stretch', 'Stretch', f, say);\n}\n\n// ----- the plans",
    "  // plain (round 29): the rule's length is the plain power of the dot's own, whatever its direction (probed by learnPlan)\n"
    "  return learnMove('stretch', 'Stretch', f, say, { all: plain ? learnAllStretch(n, 'distance from the centre') : 'every dot’s distance from the centre goes to the one this approach gives it. Each by its own amount: Follow One point shows it for a single dot' });\n}\n\n// ----- the plans")
rep("      if (even) moves.push(learnOwn(F, false), learnStretchTo(F, n));\n",
    "      const plain = even && [0.7, 1.3].every((r, i) => Math.abs(lens[i][0] - learnPowLen(r, n)) <= 1e-9 * Math.max(1, lens[i][0]));\n"
    "      if (even) moves.push(learnOwn(F, false), learnStretchTo(F, n, plain));\n")

io.open(DST, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', n[0], 'places ->', DST)
