"""Third one-off edit of src/js/25-colour.js: cut the shader's preparation time. The first version carried ten
more numbers through the orbit loop than base4 and tripled the time the D3D compiler takes (measured: 1.7 to 2.9 s
on base4, 5.8 to 6.2 s with the colour file alone). Now two more are carried: the touch record shares the four
numbers of the three-tone mix, the stretch is one running sum of logarithms, and the cut face has no depth proxy."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '25-colour.js')
s = open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


def cut(a, b, new):
    """replace everything from the start of a up to (not including) b"""
    global s
    i = s.index(a); j = s.index(b, i)
    s = s[:i] + new + s[j:]


# ---- declarations
cut('// While an orbit runs: gNear = where it came nearest the trap', '// The plain distance from the orbit point v to the trap shape in use',
    '''// While an orbit runs: gNear = where it came nearest the trap (xyz, measured from the trap centre) and how near
// (w), gNearIt = at which step. gTrap = for the three-tone mix, its nearest approach to each coordinate plane and
// to the origin; for every other trap, the step that makes a trap solid (see trapAdd): where it was (xyz, or the
// step number in x when the colour goes by step) and its score (w). The two uses never meet, and every number
// carried through the orbit loop costs preparation time, so they share. gTouchLs = the logarithm of the stretch
// at that step, gLogS = the running sum of the logarithms of the stretch. c* are the captured copies.
// gColIn: pal() reads the inside palette.
vec4 gTrap, cTrap, gNear, cNear; float gNearIt, cNearIt, cIt, gLogS, cLogS, gTouchLs, cTouchLs; vec3 cLast; bool gColIn = false;
''')
cut('void trapStart(){', '// One orbit point. Two things in here are not obvious.',
    '''void trapStart(){ gTrap = vec4(1e9); gNear = vec4(0.0, 0.0, 0.0, 1e9); gNearIt = 0.0; gLogS = 0.0; gTouchLs = 0.0; }
''')
cut('// The running stretch. On a solid made from the trap, the step that matters', 'void colourCapture(){',
    '''// The running stretch. On a solid made from the trap, the step that matters is the one that touches the trap,
// and at a hovering point that is not always the step with the smallest distance: a late step magnifies the
// hover height hundreds of times. The renderer's solid is the least of (distance - thickness) / stretch, so the
// same score is kept here, with the stretch of a pure power (n |v|^(n-1) per step, and |v - mu|^2 per map of the
// Kleinian group) standing in for the true one, which only the renderer knows. It is kept as a sum of logarithms
// (uColLog.x + uColLog.y * log |v - uColMu|^2 per step). That step counts whatever gFade says: the flight is
// where most trap solids are touched.
void trapAdd(vec3 v, float it){
  if (uColNeed == 0) return;
  float ls = gLogS;
  if ((uColNeed & 2) != 0 && it > 0.5){
    vec3 u = v - uColMu;
    gLogS += uColLog.x + uColLog.y * log(max(dot(u, u), 1e-18));
    // an equation's step magnifies what comes after it; a Kleinian map has already magnified the point it made
    if (uColKlein > 0.5) ls = gLogS;
  }
  if ((uColNeed & 1) == 0) return;
  float w = clamp(gFade + 1.0 - it, 0.0, 1.0);
  if (uTrap == ${TRAP.tones}){
    if (w > 0.0){
      vec4 m = min(gTrap, vec4(abs(v), length(v)));
      if (w >= 1.0 || gTrap.w > 1e8) gTrap = m; else gTrap = mix(gTrap, m, w);
    }
    return;
  }
  float d = trapDist(v);
  if (w > 0.0 && d < gNear.w){
    if (w >= 1.0 || gNear.w > 1e8){ gNear = vec4(v - uTrapC, d); gNearIt = it; }
    else { gNear = mix(gNear, vec4(v - uTrapC, d), w); gNearIt = mix(gNearIt, it, w); }
  }
  if (uTrapSolid > 0.5 && it >= float(uTrapSkip)){
    ls = clamp(max(ls, uColFloor), -60.0, 60.0);
    float sc = (d - uTrapW) * exp(-ls);
    if (sc < gTrap.w){ gTrap = vec4(uTrapBy == 1 ? vec3(it, 0.0, 0.0) : v - uTrapC, sc); gTouchLs = ls; }
  }
}
''')
cut('void colourCapture(){', 'vec3 pal(float t){',
    '''void colourCapture(){ cTrap = gTrap; cNear = gNear; cNearIt = gNearIt; cIt = gIt; cLast = gLast; cLogS = gLogS; cTouchLs = gTouchLs; }
''')

# ---- the trap solid's colours
cut('  // The trap makes the solid, or part of it. Step, side and place are read from the step that touched the trap.',
    '// The colour for every mode that reads the palette (uColMode <= 5), from the captured values.',
    '''  // The trap makes the solid, or part of it. Step, side and place are read from the step that touched the trap.
  vec3 tq = cTrap.xyz; float ts = cTrap.w, tl = cTouchLs;
  if (uTrapSkip == 0 && uColJulia > 0.5){
    // A Julia orbit starts at the point itself, which trapAdd never sees: with no steps skipped the trap shape
    // is part of the solid, touched at step 0. The scores of the later steps lack the stretch of the first step.
    float d0 = trapDist(p), first = clamp(abs(uPow) * pow(max(length(p), 1e-9), uPow - 1.0), 1e-9, 1e9);
    if (d0 - uTrapW < ts / first){ tq = uTrapBy == 1 ? vec3(0.0) : p - uTrapC; ts = (d0 - uTrapW) * first; tl = -log(first); }
  }
  vec3 place = pal(uTrapBy == 1 ? 0.23 * tq.x : uTrapBy == 3 ? colSide(tq) : colWhere(tq));
  // Close to the set the solid is layer upon layer, each a share 1 / stretch of the thickness across. Once a
  // layer is thinner than a pixel or two its own colours can only sparkle. (A pixel is taken to be about 0.0015
  // of the distance from the camera across, which is right for the usual picture and only has to be roughly so.)
  float px = 0.0015 * max(depth, 0.0), fine = smoothstep(0.5, 1.5, px * exp(tl) / max(uTrapW, 1e-6));
  // Step, side and place give way there to what such a pixel would average out to: the mean of the palette.
  if (uTrapBy == 1 || uTrapBy == 3 || uTrapBy == 5) return mix(place, uPalMean, fine);
  // The choices by nearness. Nearness is the same all over the trap's part of the solid, so that part shows
  // the place it was touched instead, and nearness is left to the rest, where it does vary: the fine layers,
  // and the set's own surface when the trap was added to it (where the score, which is about the distance to
  // the trap's part, is more than a few pixels).
  t = uTrapBy == 2 ? band - 0.1 * back : uTrapBy == 4 ? 0.15 + 0.85 * exp(-2.4 * pow(uGlowK * s, uGlowP)) : band;
  return mix(place, pal(t), uTrapSolid < 1.5 ? fine : max(fine, smoothstep(3.0, 8.0, ts / max(px, 1e-9))));
}
''')

# ---- the inside and the cut face
rep('''  // how deep: the square root spreads out the rim, where the estimate is at its best
  else if (uInMode == 3) c = pal(1.3 * sqrt(max(deep, 0.0)));''', '''  // how deep: the square root spreads out the rim, where the estimate is at its best. The cut face has no
  // estimate (deep < 0) and shows how quickly the orbit settles there, which draws much the same rings.
  else if (uInMode == 3 && deep >= 0.0) c = pal(1.3 * sqrt(deep));''')
rep('  else c = pal(clamp(exp(cLogS / max(cSteps, 1.0)), 0.0, 1.0));', '  else c = pal(clamp(exp(cLogS / max(cIt, 1.0)), 0.0, 1.0));')
rep('''// values. deep: how far inside the point is, in scene units.''', '''// values. deep: how far inside the point is, in scene units, or negative when that is not known.''')
cut('vec3 cutFaceColour(vec3 p, vec3 hatch){', 'vec3 flatColour(vec3 p, float d, float px){',
    '''vec3 cutFaceColour(vec3 p, vec3 hatch){
  if (uCutFace < 0.5) return hatch;
  return colInside(p, -1.0);
}
''')
rep('  return e > 0.0 ? outer : colInside(p, -d);', '  return e > 0.0 ? outer : colInside(p, max(-d, 0.0));')

# ---- uniforms
rep('uniform float uEdge, uEdgeGlow, uCutFace, uColKlein, uColJulia;', 'uniform float uEdge, uEdgeGlow, uCutFace, uColKlein, uColJulia, uColFloor; uniform vec2 uColLog;')
rep('''// its fall-off; uColNeed = what trapAdd has to keep (1 the trap measures, 2 the running stretch); uColKlein,
// uColJulia, uColMu = which kind of orbit this is, for the running stretch;''', '''// its fall-off; uColNeed = what trapAdd has to keep (1 the trap measures, 2 the running stretch); uColKlein,
// uColJulia, uColMu, uColLog, uColFloor = which kind of orbit this is and what a step adds to the logarithm of
// the running stretch (see trapAdd), which is held above uColFloor;''')
rep('''  gl.uniform1f(L('uColKlein'), S.mode === 'k' ? 1 : 0); gl.uniform1f(L('uColJulia'), S.mode === 'j' ? 1 : 0);
  gl.uniform3f(L('uColMu'), k.mx, k.my, k.mz);''', '''  // The running stretch, as what one step adds to its logarithm: log |v - mu|^2 for a map of the Kleinian
  // group, log n + (n - 1) / 2 * log |v|^2 for an equation. In Mandelbrot mode the point moves with c itself as
  // well, so there the stretch never falls below 1.
  const kl = S.mode === 'k', n = Math.max(Math.abs(S.n), 1e-9);
  gl.uniform1f(L('uColKlein'), kl ? 1 : 0); gl.uniform1f(L('uColJulia'), S.mode === 'j' ? 1 : 0);
  gl.uniform3f(L('uColMu'), kl ? k.mx : 0, kl ? k.my : 0, kl ? k.mz : 0);
  gl.uniform2f(L('uColLog'), kl ? 0 : Math.log(n), kl ? 1 : 0.5 * (S.n - 1)); gl.uniform1f(L('uColFloor'), S.mode === 'm' ? 0 : -60);''')
rep("  { type: 'note', when: c => colInsideShown(c) && c.inMode === 1, text: 'The inside uses the trap shape and the \"Trap colours by\" choice above.' },",
    "  { type: 'note', when: c => colInsideShown(c) && c.inMode === 1, text: 'The inside uses the trap shape and the \"Trap colours by\" choice above.' },\n  { type: 'note', when: c => !S.flat && colInsideShown(c) && c.inMode === 3, text: 'The cut face has no measure of depth, so there this choice shows how quickly the orbit settles, which draws much the same rings.' },")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
