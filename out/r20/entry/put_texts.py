"""Round 20, entry: write the words of the entry "Wind, then square" into src/js/10-approaches.js, between the marks
R20-TEXTS-BEGIN and R20-TEXTS-END. Idempotent. Every sentence is a number from out/r20/entry/ (checks.txt, stretch.txt,
thick.txt, small.txt, measure-*.txt, brute-*.txt, flatcmp.txt) or is read off the formula; NOTES.md says which.
Run from the project root: python out/r20/entry/put_texts.py"""
import io, re, sys

TEXTS = r"""// R20-TEXTS-BEGIN
const WS_ROUGH = 'The lab always draws this rule with “Distance estimate” at “Rough”, whatever that setting says. The other two settings draw a spindle of fog round the solid: measured on seven views of the Julia sets for c = −1, the rabbit and the Siegel disc, between 21% and 99% of the places where a ray stopped had no point of the set within 8 pixels with “Exact”, between 75% and 99% with “One neighbour”, and at most 1% with “Rough”. Rough has a fault of its own: a ray can step over a sheet that is thinner than its step, so thin parts are left out of the 3D picture. For the rabbit 58 of 254 rays that meet the set stopped at nothing. With “Ray step, share of the distance estimate” lowered to 0.4 it was 15 of 254. The pictures described here were made with Iterations at 40: at 14 the bodies are still joined by short necks.';
const WS_TAG = 'Wind each point round the x-axis three times (at power 2), then square it by the one-plane rule, and turn nothing back. Three planes then carry the flat set for every c of the flat plane, and nothing tears. For c = −1 it gives separate bodies with buds in six directions, but their skin is ragged between the planes. Off the x-axis it falls short: the rabbit’s ears are thin plates and the Siegel disc is three sheets. Its Mandelbrot solid has not been judged yet.';
const WS_NOTE = WS_ROUGH + ' Measured: a point with z exactly 0 gets exactly the answer of Sphere inversions, one plane, and the cut at z = 0 is the flat set (six Julia sets at the powers 2 to 5, 160,000 points each, tested against plain complex arithmetic: none differs). WS_FLATCMP At power 2 the six half-planes through the x-axis at 0°, 60°, 120°, 180°, 240° and 300° are sent into the plane z = 0 in one step (to 15 digits), and from there on a point follows complex squaring. So three planes through the x-axis, 60° apart, each show the flat set, turned about the x-axis, whether c lies on the x-axis or not: for the rabbit the cut by the plane at 120° is the flat rabbit point for point, and the cut at 60° is the flat rabbit turned over (129,600 points each, none differs). No jump was found: for 200,000 pairs of close points the gap between the two answers shrinks in step with their distance, at four distances from 0.001 down to 0.000001, at the powers 2 to 5. The rule gives the same answer mirrored above and below and mirrored front and back, the same answer for a point turned by 120° about the x-axis (to 15 digits), and the length of a point is squared exactly. So every Julia set of this rule looks the same after a third of a turn about the x-axis. A whole power n is wound n times when n is odd and n + 1 times when n is even: the powers 2 and 3 have six half-planes that land in the plane z = 0, the powers 4 and 5 have ten (measured). A product of two different points is taken from Sphere inversions, one plane.';
const WS_ABOUT = 'In Sphere inversions, two planes and in the two Turning plane entries, each plane that carries the flat set is squared inside itself. Here only the plane z = 0 is squared. Before the squaring every point is carried round the x-axis: its angle round that axis is multiplied by three, unevenly, at the angle’s own pace beside six half-planes 60° apart and five times as fast half way between them. The six half-planes land in the plane z = 0, and a point of them is from then on a point of the flat plane, where c lives. So they show the flat picture without the rule having to keep them, and that works for every c of the flat plane. What the pictures show for c = −1: a row of separate bodies along the x-axis, each with six buds round it, one in each of the six half-planes, and smaller buds on those. Cut across at the point where two bodies touch, nothing but that point is left (40 steps, a cut 0.2 wide). The bud at 60° is a body and not a plate: cut along the x-axis it is an oval 0.13 long and 0.12 across. Cut across the x-axis through the middle of the middle body, at x = 0, the outline between two buds is smooth down to a picture 0.12 wide (80 steps), but that place is special. Where it falls short for c = −1: a little to the side, at x = 0.2, the same stretch of outline is ragged, with thin needles standing off it (80 steps, a picture 0.3 wide). At x = −0.3 a dozen short thin spikes and loose specks stand round the body, and the bud at 60° has a fringe of about 200 loose specks. The 3D picture shows this as a streaked, grainy skin, bristly like a sea urchin when seen along the x-axis, where Sphere inversions, one plane is smooth. The sets for c = −0.75 and c = 0.25 are ribbed from end to end: cut across the x-axis, c = 0.25 has twelve lobes like a pumpkin and c = −0.75 six sharp ridges, with a hairy rim at x = −0.3. Where it falls short away from the x-axis: the bodies are thin there. Turn the flat rabbit 4° about the x-axis and only 52% of its points are still in the set, and at 15° only 19% (the same with 40 and with 80 steps). For c = −1 it is 91% at 4° and 91% at 30°. So the rabbit’s middle body is a body with six points, but its ears are plates lying in the three planes, with shredded rims, and the 3D picture shows a feathery mass and no separate bodies. The Siegel disc is thinner still and thins with every step: a quarter of a degree off its planes 79% of its points are in the set after 40 steps and 64% after 80. It is three sheets crossing on the x-axis, not a body. For c = i, a tree in the plane, the cuts show three flat trees and the 3D picture a thin dust. Whole powers: cut across the x-axis the outline repeats six times round the axis at the powers 2 and 3 and ten times at the powers 4 and 5 (for c = −1 at power 4: ten buds), so the count follows the power two powers at a time. The Mandelbrot solid of this rule has not been judged yet.';
const wsRound = n => (wsCount(n) === 1 ? APR_CIRCLES
  : `Inside the ${wsCount(n)} planes that carry the flat set the rule is the complex power, which keeps shapes, and the ${2 * wsCount(n)} directions that are sent to the negative x-axis, one in each of the ${2 * wsCount(n)} half-planes, are stretched exactly as the flat plane stretches (measured at the powers 2 to 5). Beside those planes a small ball stays nearly a ball, and half way between them it is squeezed flat. Measured at power 2: 7% out of round within 5° of the planes, and about five to one within 5° of half way. The squeeze grows with the power: about 12 to one at power 3 and 19 to one at power 4.`);
const wsAngles = k => Array.from({ length: Math.min(k, 3) }, (_, j) => aprDeg((j + 0.5) * 180 / k)).join(', ');
const wsCrush = n => (wsCount(n) === 1 ? 'At this power the winding changes nothing, and the rule is Sphere inversions, one plane itself: it crushes the z-axis only.'
  : `Crushes ${2 * wsCount(n)} directions: those at right angles to the x-axis, half way between the half-planes that land in the plane z = 0 (at ${wsAngles(wsCount(n))} and so on round the x-axis). The winding sends them onto the z-axis, which the one-plane rule crushes: two of the three stretches fall to under 2% of what the plane gives (measured at the powers 2 to 5). Nothing is folded over: of 400,000 directions none came out as a mirror image (measured at the powers 2, 3 and 4).`);
const WS_SMOOTH_OTHER = ' A power that is not a whole number takes the winding of the nearest whole number, so the picture jumps between whole powers. It also tears space, the way zⁿ tears the plane along the negative x-axis: here along the half-planes half way between those that land in the plane z = 0, on the side x < 0 (measured at the power 2.5).';
const wsSmooth = n => (wsCount(n) === 1 ? 'At this power the rule is Sphere inversions, one plane itself.' + (aprWhole(n) ? '' : APR_HALF)
  : `One formula with no seam. No jump was found at the powers 2 to 5. The stretch is largest beside the x-axis, half way between the half-planes that land in the plane z = 0: ${2 * wsCount(n) - 1} times that of the plane (measured at the powers 2 to 5). It uses the sine of an angle, so it is not a polynomial.` + (aprWhole(n) ? '' : WS_SMOOTH_OTHER));
const wsSlice = (ok, n) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
  : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' + (aprWhole(n) && n >= 2 ? ` The ${2 * wsCount(n)} half-planes through the x-axis at every ${aprDeg(180 / wsCount(n))} are sent into the plane z = 0 at the first step, so ${wsCount(n)} planes in all show the flat set, each turned about the x-axis.` : ''));
const wsFormula = n => {
  const k = wsCount(n), m = Math.max(1, Math.floor(Math.abs(n) + 0.5)), own = aprWhole(n) && n >= 2, sup = own ? aprSup(n) : 'ⁿ';
  if (k === 1) return `At this power the turn round the x-axis is wound once, which changes nothing, and the rule is the power ${aprNum(n)} of Sphere inversions, one plane itself.`;
  return `v${sup} = P(W(v))   with P the power ${aprNum(n)} of Sphere inversions, one plane, and W the winding: W keeps x and the distance of v from the x-axis, and changes only φ, the angle of v round the x-axis (0 on the side y > 0 of the plane z = 0), to g(φ) = ${k}φ − ${k - 1}·sin ${2 * k}φ / ${2 * k}. Nothing is turned back afterwards. g runs at the pace of φ itself wherever φ is a multiple of ${aprDeg(180 / k)}, and ${2 * k - 1} times as fast half way between. `
    + (own ? `The ${k} in it is ${m % 2 ? 'the power itself' : 'the power plus one, because the power is even'}` : `The ${k} in it comes from ${m}, the whole number nearest to the size of the power: ${m % 2 ? 'that number itself' : 'one more, because that number is even'}`)
    + '. An even count would send the half y < 0 of the plane z = 0 onto the half y > 0, and the slice at z = 0 would no longer be the flat set. So the count follows the power and is not a free choice.'
    + (aprWhole(n) ? '' : ` P itself is taken at the power ${aprNum(n)}; only the winding follows the whole number.`);
};
// R20-TEXTS-END"""

def main(flatcmp=None):
    p = 'src/js/10-approaches.js'
    s = io.open(p, encoding='utf-8', newline='').read()
    m = re.search(r'// R20-TEXTS-BEGIN.*?// R20-TEXTS-END', s, re.S)
    if not m:
        sys.exit('marks not found')
    t = TEXTS
    if flatcmp is None:
        try:
            flatcmp = io.open('out/r20/entry/flatcmp-sentence.txt', encoding='utf-8').read().strip()
        except IOError:
            sys.exit('no flatcmp sentence yet (run flatcmp.py first)')
    t = t.replace('WS_FLATCMP', flatcmp)
    s2 = s[:m.start()] + t + s[m.end():]
    # the entry: the smooth line no longer adds APR_HALF itself (the tear of this rule lies elsewhere, see WS_SMOOTH_OTHER)
    old = "smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', wsSmooth(n) + aprTear(n, APR_HALF)]),"
    new = "smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', wsSmooth(n)]),"
    if old in s2:
        s2 = s2.replace(old, new)
    elif new not in s2:
        sys.exit('entry smooth line not found')
    old, new = "roundNote: () => WS_ROUND,", "roundNote: (p, n = S.n) => wsRound(n),"
    if old in s2:
        s2 = s2.replace(old, new)
    elif new not in s2:
        sys.exit('entry roundNote line not found')
    io.open(p, 'w', encoding='utf-8', newline='').write(s2)
    print('texts written' if s2 != s else 'texts already in place')

if __name__ == '__main__':
    main()
