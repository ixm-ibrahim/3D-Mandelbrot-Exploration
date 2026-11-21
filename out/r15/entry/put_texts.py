"""Round 15, entry: the words of the Square pillow, written from out/r15/entry/ (checks.txt, delicate.txt, skin*.txt,
neck.txt, mirror.txt, stretch_where.txt, flatcmp.txt, card.txt and the pictures). Replaces what stands between the
marks R15-TEXTS-BEGIN and R15-TEXTS-END in src/js/10-approaches.js, and the entry's own lines. Can be run again."""
import io, re
P = 'src/js/10-approaches.js'
s = io.open(P, encoding='utf-8').read()

TEXTS = r'''// R15-TEXTS-BEGIN
const spGrid = n => clamp(Math.floor(Math.abs(n) + 0.5), 2, SP_MAXN);   // the whole power the grid is laid out for
const spOwn = n => aprWhole(n) && Math.abs(n) >= 2 && Math.abs(n) <= SP_MAXN;   // a power the grid is made for
const SP_TAG = 'Lay the directions on a square pillowcase grid and double both of its coordinates. The slice at z = 0 is the flat set and no tear was found, but at power 2 the solid is streaked and its bodies do not come apart. Power 3 looks better: buds on buds.';
const SP_NOTE = 'Measured at power 2. The plane z = 0 follows complex arithmetic exactly: the 2D view draws the same picture as for Sphere inversions, one plane, pixel for pixel (five pictures compared). No jump was found between close directions (400,000 pairs). The rule is lopsided above and below the plane z = 0, because the belt of the grid that carries that plane does not lie half way between the two seams, it is twice as far from the lower seam as from the upper one: a direction and its mirror image are sent to places 0.7 apart on average, on a sphere of radius 1. At power 3 the belt lies half way and the rule is mirror-symmetric (to 15 digits). Beside the plane z = 0 a small circle of directions stays nearly a circle. Away from it the stretch is uneven: for half of all directions at least 1.6 times as much one way as the other, and for about one in six more than 3 times. The skin of the 3D picture was compared with a plain test of the set along 567 rays per picture: for three Julia sets every place where a ray stopped lay within 0.05 of the set (about 11 pixels of the opening picture), and about 5 in 6 within 0.0125. For the Mandelbrot solid 3 of 223 lay further away than 0.05. The same test gives 0.025 at most for Sphere inversions, one plane, and more than 0.1 at 12 of 145 places for Pillow. This is not the entry Pillow under “Tried”: that one wraps a sheet of triangles and has corners in the plane z = 0, this one a square sheet with no corner and no fold in that plane. A product of two different points is taken from Sphere inversions, one plane.';
const SP_ABOUT = 'The Mandelbulb doubles two angles on a globe grid, and a globe grid is squeezed toward its poles. This entry tries another grid: a square pillowcase, a flat sheet folded double and sewn shut, which is squeezed nowhere except at its four corners. On that sheet the rule doubles both coordinates, a plain enlargement by 2. One belt of the pillow comes back to itself with its position doubled. That belt is laid on the equator, so the plane z = 0 follows complex squaring exactly, and no seam is needed. What the pictures show at power 2: the Mandelbrot solid is one lopsided rock with fins. The Julia set for c = −1 is a row of bodies with spikes, but the bodies do not come apart: cut through the point where two flat bodies touch, the solid is 24% as large as cut through its middle, and it reaches as far above and below the plane there as 0.54 (in the middle: 0.60). Sphere inversions, one plane gives 4% there. The rabbit is a group of lumps, c = i a branching coral, and c = 0.3 one smooth block. Close up, at three depths, the skin is made of streaked sheets, blades and thin slits, like combed or stirred paint. Cuts worked point by point, without the shortcuts of the 3D picture, show the same thing: the detail goes on at smaller sizes, but as thin sheets and slivers, not as smaller bodies. Where it falls short: a pillowcase is flat and a sphere is round, so laying one on the other stretches it somewhere, and the layout used here is even only beside the plane z = 0. The streaks probably come from that, which was not tested. At the powers 3, 4 and 5 the opening pictures show a blocky body with knobbly buds on its corners and rims. At power 3 one Julia set, c = (0.3, 0.5, 0), was also looked at close up in one place, at three depths: there the skin is buds with smaller buds on them, with no streaks, and cuts worked point by point show a bumpy outline with no slits. Other sets and other places at these powers were not looked at.';
const SP_ROUND = 'On the pillow grid the rule is a plain enlargement, but the grid is laid on the sphere unevenly. Beside the plane z = 0 a small circle of directions stays nearly a circle (measured at power 2: about 5% out of round within 5° of the plane). Further away it comes out as an oval.';
const SP_CRUSH2 = 'Nothing but the origin is crushed onto one point. Beside the upper pole the stretch falls to almost nothing (measured: down to 0.001 where the plane gives 2), and beside the corner points of the grid in the lower half it is largest (measured: up to 10).';
const SP_CRUSHN = 'Nothing but the origin is crushed onto one point. Where the stretch is smallest and largest was measured at power 2 only: smallest beside the upper pole, largest beside the corner points of the grid in the lower half.';
const SP_SMOOTH = 'Not one formula: the grid is laid on the upper and the lower half of the sphere by two formulas that meet on the equator, and a cubic equation is solved at every step. No jump was found: the gap between the answers for two close directions shrinks in step with their distance (measured at the powers 2 to 5).';
const SP_SMOOTH_OTHER = ' The grid exists for the whole powers 2 to 5 only. Every other power uses the grid of the nearest of them, so the picture jumps between whole powers.';
const SP_SLICE = 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set. No corner and no fold of the grid lies in that plane.';
const spSliceOther = n => `The grid exists for the whole powers 2 to 5 only. At the power ${aprNum(n)} the directions follow the power ${spGrid(n)} and only the length follows ${aprNum(n)}. So the plane z = 0 lands on itself, but it does not follow complex arithmetic.`;
const spFormula = n => {
  const m = spGrid(n), own = spOwn(n) && n > 0, k = own ? aprSup(m) : 'ⁿ';
  return `v${k} = |v|${k} · dir(D(pil(d)))   with d = v/|v| the direction of v. pil lays d on a square pillowcase grid: s runs once round the pillow from 0 to 1, and t from the lower seam (0) to the upper seam (½). D multiplies both by ${m} with a mirror, (s, t) → (−${m}s, ${m}t), and where the result passes a seam the sheet is folded back over it. dir is pil backwards. The belt t = 1/${m + 1} comes back to itself with s multiplied by ${m}, and that belt is the equator, with s the longitude.`
    + (own ? '' : ` The grid is that of the whole power ${m}; only the length follows the power ${aprNum(n)}.` + (n < 0 ? ' A negative power ends with a mirror, y → −y and z → −z.' : ''));
};
// R15-TEXTS-END
'''
a, b = s.index('// R15-TEXTS-BEGIN'), s.index('// R15-TEXTS-END') + len('// R15-TEXTS-END\n')
s = s[:a] + TEXTS + s[b:]

a = s.index("    id: 'sqpillow', name: 'Square pillow'")
b = s.index('  },\n];', a)
ENTRY = '''    id: 'sqpillow', name: 'Square pillow', group: 'pillow', glsl: GL_SQPILLOW, axis: () => [0, 0, 1],
    tag: SP_TAG,
    params: [{ type: 'note', text: SP_NOTE }],
    formula: (p, n) => spFormula(n),
    about: SP_ABOUT,
    roundNote: () => SP_ROUND,
    crush: (p, n = S.n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto the sphere of radius 1.'] : ['part', (aprIs(Math.abs(n), 2) ? SP_CRUSH2 : SP_CRUSHN) + aprPole(n)]),
    smooth: (p, n = S.n) => ['no', SP_SMOOTH + (spOwn(n) ? '' : SP_SMOOTH_OTHER)],
    slice: (ok, p, n = S.n) => (spOwn(n) && ok ? SP_SLICE : spSliceOther(n)),
'''
s = s[:a] + ENTRY + s[b:]
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
bad = [m.group(0) for m in re.finditer('[—–]', TEXTS)]
print('written; long dashes in the texts:', len(bad))
