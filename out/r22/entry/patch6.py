"""Round 22, entry: the card and the two step figures of an entry whose one squaring depends on c (Pulled plane) follow
the c of the Julia dials: src/js/60-measure.js (c handed to the rule, c in the key of the remembered measurements) and
src/js/80-ui.js (a c dial that moves redoes them). Run once."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
def patch(rel, pairs):
    P = os.path.join(ROOT, *rel.split('/'))
    s = io.open(P, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (rel, s.count(old), old)
        s = s.replace(old, new)
    io.open(P, 'w', encoding='utf-8', newline='\n').write(s); print('patched', rel)
patch('src/js/60-measure.js', [
("const powerF = () => { const a = ap(), q = { ...apP() }, n = cardPower(); return v => MATH[a.id](v, n, q); };\n",
 "// (The fourth argument is the Julia constant, for the entries whose orbit carries something, see CARRY in\n"
 "// 10-approaches.js: their one squaring is the first of an orbit with that c. No other entry looks at it.)\n"
 "const cardCarries = a => typeof CARRY !== 'undefined' && !!CARRY[a.id];\n"
 "const powerF = () => { const a = ap(), q = { ...apP() }, n = cardPower(), c = S.c.slice(); return v => MATH[a.id](v, n, q, c); };\n"),
("  const key = a.id + ' ' + n + ' ' + JSON.stringify(q), known = cardRun.cache.get(key), stream = now - cardRun.last < CARD_QUIET;\n",
 "  const c0 = S.c.slice(), key = a.id + ' ' + n + ' ' + JSON.stringify(q) + (cardCarries(a) ? ' ' + JSON.stringify(c0) : ''), known = cardRun.cache.get(key), stream = now - cardRun.last < CARD_QUIET;\n"),
("  const st = measureBegin(v => MATH[a.id](v, n, q), n);\n",
 "  const st = measureBegin(v => MATH[a.id](v, n, q, c0), n);\n"),
])
patch('src/js/80-ui.js', [
("() => S.c[i], v => { S.c[i] = v; uiJuliaMark(); touch(); },",
 "() => S.c[i], v => { S.c[i] = v; uiJuliaMark(); if (typeof CARRY !== 'undefined' && CARRY[ap().id]) uiApproachParam(); else touch(); },"),
])
