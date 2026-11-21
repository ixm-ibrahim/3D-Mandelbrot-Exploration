"""Round 29, Track A, builder: write the three overlay files from the frozen copy base21a and the parts kept here.

  python -B out/r29/free/mk/make_overlay.py      -> out/r29/free/overlay/js/{32-balls.js,40-render.js,80-ui.js}

32-balls.js = parts/balls-head.js (everything above the program texts, with parts/balls-twin.js put in)
            + the lines of base21a/js/32-balls.js from "// The scene program of this group." to the end, AS THEY ARE
              (the long comment, GL_BALLS, the comment above GL_BALLS_RHO, GL_BALLS_RHO: not one character changes)
            + parts/balls-free.js (the new program GL_BALLS_FREE and its comment).
40-render.js, 80-ui.js = the frozen files with the pieces below exchanged; every piece must be found exactly once.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FREE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FREE)))
BASE = os.path.join(ROOT, 'base21a', 'js'); OUT = os.path.join(FREE, 'overlay', 'js')


def read(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def write(name, text):
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n').write(text)
    print('wrote overlay/js/%s (%d characters)' % (name, len(text)))


def swap(text, old, new, name):
    if text.count(old) != 1:
        sys.exit('%s: a piece to exchange was found %d times:\n%s' % (name, text.count(old), old[:200]))
    return text.replace(old, new)


# ------------------------------------------------------------------------------------------------ 32-balls.js
frozen = read(os.path.join(BASE, '32-balls.js'))
cut = frozen.index('// The scene program of this group.')
head = read(os.path.join(HERE, 'parts', 'balls-head.js')).rstrip('\n') + '\n'
twin = read(os.path.join(HERE, 'parts', 'balls-twin.js')).rstrip('\n') + '\n'
head = swap(head, '//__FREE_TWIN__\n', twin, 'balls-head.js')
free = read(os.path.join(HERE, 'parts', 'balls-free.js')).rstrip('\n') + '\n'
write('32-balls.js', head + '\n' + frozen[cut:].rstrip('\n') + '\n' + free)

# ------------------------------------------------------------------------------------------------ 40-render.js
r = read(os.path.join(BASE, '40-render.js'))
r = swap(r, """  if (klein === 'balls2') return { key: keyOf('balls2'), src: () => GL_HEAD + defs + GL_COLOUR + GL_BALLS_RHO + GL_TAIL };
""", """  if (klein === 'balls2') return { key: keyOf('balls2'), src: () => GL_HEAD + defs + GL_COLOUR + GL_BALLS_RHO + GL_TAIL };
  // (Round 29: 'balls3' is that group for every other pair of its two numbers, where the two spheres cut into each
  // other or the second lies between 1/2 and 1 of the first: GL_BALLS_FREE, again a text and a key of its own.)
  if (klein === 'balls3') return { key: keyOf('balls3'), src: () => GL_HEAD + defs + GL_COLOUR + GL_BALLS_FREE + GL_TAIL };
""", '40-render.js')
r = swap(r, """// there), or 'balls' / 'balls2' (the second group, when its module is part of the page: with two equal spheres, and
// with a smaller second sphere).
const sceneKlein = () => (S.mode !== 'k' ? false : typeof GL_BALLS === 'string' && S.k.group === 1 ? (ballsRho() < 1 ? 'balls2' : 'balls') : true);
const sceneBalls = (kl = sceneKlein()) => kl === 'balls' || kl === 'balls2';
""", """// there), or 'balls' / 'balls2' / 'balls3' (the second group, when its module is part of the page: with two equal
// spheres, with a smaller second sphere, and with every other pair of its two numbers; ballsKind in 32-balls.js).
const sceneKlein = () => (S.mode !== 'k' ? false : typeof GL_BALLS === 'string' && S.k.group === 1 ? ballsKind() : true);
const sceneBalls = (kl = sceneKlein()) => kl === 'balls' || kl === 'balls2' || kl === 'balls3';
""", '40-render.js')
r = swap(r, """  // (uBT: the two spheres may touch, never cut into each other, so t is held to (1 + rho) / 2 or more: with two
  //  equal spheres that is 1, as it always was. uBRho: only the program for a smaller second sphere has it.)
  if (balls) { gl.uniform1f(L('uBT'), ballsT()); gl.uniform1i(L('uBGrid'), k.bgrid | 0); if (kl === 'balls2') gl.uniform1f(L('uBRho'), ballsRho()); }
""", """  // (uBT: t as the state holds it, ballsTOf. The program for two equal spheres is only chosen with t at 1 or more,
  //  as it always was; the one for a smaller second sphere is handed the touching value for a t that is a rounding
  //  hair under it. uBRho: the two programs for a second sphere of any size have it.)
  if (balls) { gl.uniform1f(L('uBT'), ballsTOf(kl)); gl.uniform1i(L('uBGrid'), k.bgrid | 0); if (kl !== 'balls') gl.uniform1f(L('uBRho'), ballsRho()); }
""", '40-render.js')
r = swap(r, """  // Balls on balls on show: its other program first (the one for a smaller second sphere, or the one for two equal
  // spheres), so that dragging the size of the neighbours past 100 does not stop to prepare it.
  const kl = sceneKlein();
  if (sceneBalls(kl)) want(a, '', '', false, kl === 'balls' ? 'balls2' : 'balls');
""", """  // Balls on balls on show: its other two programs first (the one for pairs of numbers whose spheres cut into each
  // other before the others: that is where the size of the neighbours goes when it is dragged past 100), so that
  // moving a dial does not stop to prepare one.
  const kl = sceneKlein();
  if (sceneBalls(kl)) for (const other of ['balls3', 'balls2', 'balls']) if (other !== kl) want(a, '', '', false, other);
""", '40-render.js')
write('40-render.js', r)

# ------------------------------------------------------------------------------------------------ 80-ui.js
u = read(os.path.join(BASE, '80-ui.js'))
a = u.index("  // (two of the dials give way to each other, so after either has moved the other is shown again: ballsSetShare and")
b = u.index("  addSelect('ballsDials', 'ballsGrid', 'Whole numbers', BALLS_GRIDS")
new = """  // (Round 29: each of the two dials below sets its own number and nothing else: ballsSetShare and ballsSetRho in
  //  32-balls.js. Version 21 made the second sphere smaller by itself where the size went past 100; the user asked
  //  for that rule to go, so the picture is whatever the plain recipe gives for the two numbers.)
  const bSet = () => { uiKleinMark(); touch(); };
  // The slider runs to 400 and typed values to 2000 (round 28; it stopped at 100).
  addDial('ballsDials', 'ballsSize', 'Size of the neighbours, % of the middle ball', 2, 400, 0.1, () => +ballsShare(ballsT(K.bt)).toFixed(2), v => { ballsSetShare(v); bSet(); },
    { lo: 1, hi: 2000, def: +ballsShare(BALLS_T).toFixed(2), group: 'balls', help: 'How wide the two big neighbours are, measured against the middle ball: smaller neighbours give a shorter chain. Past 100, with the second sphere at 100, the balls run into one another.' });
  // The second sphere: any value from 2 to 100 % of the first (the slider in whole numbers, typed values with two
  // decimals).
  addDial('ballsDials', 'ballsRho', 'Second sphere, % of the first', 2, 100, 1, ballsRhoShown, v => { ballsSetRho(v); bSet(); },
    { lo: 2, hi: 100, def: 100, group: 'balls', help: 'The sphere inversions use two spheres, and this is the size of the second against the first: with a smaller one the neighbours can be larger than the middle ball before the balls run into one another, and their buds are smaller and stand further apart.' });
"""
u = u[:a] + new + u[b:]
write('80-ui.js', u)
