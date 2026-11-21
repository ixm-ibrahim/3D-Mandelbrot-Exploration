# One-off editor for src/js/60-measure.js: exact string replacements, each must match once.
import io, sys
p = 'src/js/60-measure.js'
s = io.open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d match(es), found %d for: %s' % (count, n, old[:70]))
    s = s.replace(old, new)


# ---- the power that is described: the one the equation takes, which is not always the dial's n
rep("""const powerF = () => { const a = ap(), q = { ...apP() }, n = S.n; return v => MATH[a.id](v, n, q); };""",
"""const powerF = () => { const a = ap(), q = { ...apP() }, n = cardPower(); return v => MATH[a.id](v, n, q); };
// The power the scorecard and the two step figures describe. The equation may take another power of z than
// the dial shows: 'z^-n + c' takes -n, 'z^3 - z + c' takes 3 whatever n is. When it takes several, the first
// one written is described. A formula with no power in it (c*z*(1 - z)) leaves the dial's n.
const cardPow = { key: null, n: 2, several: false };
function cardPower() {
  const key = S.eq + '\\n' + S.n;
  if (cardPow.key !== key) {
    const all = formulaPowers(S.eq, S.n).filter(x => Math.abs(x) <= 64);
    cardPow.key = key; cardPow.n = all.length ? all[0] : S.n; cardPow.several = all.some(x => Math.abs(x - all[0]) > 1e-9);
  }
  return cardPow.n;
}""")

rep("""const cardRun = { cancel: null, last: -1e9, shown: null, result: null, cache: new Map(), slices: 0, longest: 0 };""",
    """// pow: the power the card last described (see cardPower).
const cardRun = { cancel: null, last: -1e9, shown: null, result: null, cache: new Map(), slices: 0, longest: 0, pow: null };""")

rep("""  $('card').innerHTML = '<div class="row head label"><div>Property</div><div>In the plane</div><div id="ruleHead">In space</div></div>' +""",
    """  $('card').innerHTML = '<p class="note" id="cardPowNote" hidden></p><div class="row head label"><div>Property</div><div>In the plane</div><div id="ruleHead">In space</div></div>' +""")

rep("""  const crush = n > 1 ? 'Only the origin is crushed. That one critical point is why the orbit of 0 decides everything.'""",
    """  const crush = n > 1 ? 'Only the origin is crushed. That is why following the single point 0 is enough to decide whether c is in the set.'""")

rep("""function updateCard() {
  const a = ap(), q = { ...apP() }, n = S.n, now = performance.now();
  cardStop();
  cardSet('ruleHead', a.name);""",
"""function updateCard() {
  const a = ap(), q = { ...apP() }, n = cardPower(), now = performance.now();
  cardStop();
  cardRun.pow = n;
  // say so when the power described is not the one on the dial
  const note = $('cardPowNote'), other = Math.abs(n - S.n) > 1e-9;
  if (note) {
    note.hidden = !other;
    cardSet('cardPowNote', other ? `The equation takes z to the power ${cardMinus(fmtN(n))}${cardPow.several ? ' first' : ''}, so that is the power described here and in the two figures above. The dial shows n = ${cardMinus(fmtN(S.n))}.` : '');
  }
  cardSet('ruleHead', a.name);""")

rep("""  const { ctx, w, h } = prep($('step2d')), n = S.n, whole = cardWhole(n),""",
    """  const { ctx, w, h } = prep($('step2d')), n = cardPower(), whole = cardWhole(n),""")
rep("""  const N = 34, rho = stepRadius(S.n, 0.11, 0.24, 0.2), h = 1e-4;""",
    """  const N = 34, n = cardPower(), rho = stepRadius(n, 0.11, 0.24, 0.2), h = 1e-4;""")
rep("""  cardSet('cap3d', stepCaption3d(ap(), S.n, stepCurves.some(cv => cv.flipped)));""",
    """  cardSet('cap3d', stepCaption3d(ap(), n, stepCurves.some(cv => cv.flipped)));""")
rep("""function drawStep3d() {
  const el = $('step3d'), b = basis(), axis = ap().axis(apP());""",
"""function drawStep3d() {
  // A new equation reaches this module only through this hook: the page redraws the picture without calling
  // refresh(). When the equation now takes another power, the figures and the card follow it.
  if (cardRun.pow !== null && cardRun.pow !== cardPower()) { buildStep3d(); drawStep2d(); updateCard(); }
  const el = $('step3d'), b = basis(), axis = ap().axis(apP());""")
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
