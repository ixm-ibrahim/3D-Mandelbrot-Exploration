"""One-off edit of src/js/25-colour.js (kept as a record of what changed after the first pictures):
bounded trap shapes for solids, the stretch at the touching step, fine layers fading to the palette's mean."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '25-colour.js')
s = open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# ---- trapDist: bounded shapes when the trap makes the solid
rep('''float trapDist(vec3 v){
  if (uTrap == ${TRAP.tones}){ vec3 a = abs(v) + uTrapOff; return min(a.x, min(a.y, a.z)); }
  vec3 q = v - uTrapC;
  if (uTrap == ${TRAP.point}) return length(q);
''', '''float trapDist(vec3 v){
  if (uTrap == ${TRAP.tones}){ vec3 a = abs(v) + uTrapOff; return min(a.x, min(a.y, a.z)); }
  vec3 q = v - uTrapC;
  if (uTrap == ${TRAP.point}) return length(q);
  if (uTrapSolid > 0.5 && uTrap <= ${TRAP.planes}){
    // As a solid, a trap that runs on for ever would fill the picture with sheets out to the drawing radius.
    // So there the lines stop uTrapR from the centre and the planes become discs of that radius.
    vec3 o = max(abs(q) - uTrapR, 0.0);
    if (uTrap == ${TRAP.cross}) return sqrt(min(o.x * o.x + q.y * q.y + q.z * q.z, min(q.x * q.x + o.y * o.y + q.z * q.z, q.x * q.x + q.y * q.y + o.z * o.z)));
    if (uTrap == ${TRAP.planes}){
      vec3 e = max(vec3(length(q.yz), length(q.zx), length(q.xy)) - uTrapR, 0.0);
      return sqrt(min(q.x * q.x + e.x * e.x, min(q.y * q.y + e.y * e.y, q.z * q.z + e.z * e.z)));
    }
    float along = dot(q, uTrapAx), over = uTrap == ${TRAP.ray} ? max(max(along - uTrapR, -along), 0.0) : max(abs(along) - uTrapR, 0.0);
    return sqrt(max(dot(q, q) - along * along, 0.0) + over * over);
  }
''')
rep('''// The three-tone mix has no shape of its own: it stands for the three coordinate planes through the origin.
float trapDist''', '''// The three-tone mix has no shape of its own: it stands for the three coordinate planes through the origin.
// While the trap makes the solid (uTrapSolid > 0.5) the endless shapes are cut down to the trap radius.
float trapDist''')

# ---- remember the stretch at the touching step
rep('vec4 gTrap, cTrap, gNear, cNear, gTouch, cTouch; float gNearIt, cNearIt, cIt, gTouchIt, cTouchIt, gTouchS;',
    'vec4 gTrap, cTrap, gNear, cNear, gTouch, cTouch; float gNearIt, cNearIt, cIt, gTouchIt, cTouchIt, gTouchS, gTouchStr, cTouchStr;')
rep('gTouch = gNear; gTouchIt = 0.0; gTouchS = 1e30; gStr = 1.0; gLogS = 0.0; gSteps = 0.0;',
    'gTouch = gNear; gTouchIt = 0.0; gTouchS = 1e30; gTouchStr = 1.0; gStr = 1.0; gLogS = 0.0; gSteps = 0.0;')
rep('if (sc < gTouchS){ gTouchS = sc; gTouch = vec4(v - uTrapC, d); gTouchIt = it; }',
    'if (sc < gTouchS){ gTouchS = sc; gTouch = vec4(v - uTrapC, d); gTouchIt = it; gTouchStr = s; }')
rep('cTouch = gTouch; cTouchIt = gTouchIt; cStr = gStr;', 'cTouch = gTouch; cTouchIt = gTouchIt; cTouchStr = gTouchStr; cStr = gStr;')
rep('''// (the three-tone mix). gTouch, gTouchIt = the same for the step that makes a trap solid (see trapAdd), and
// gTouchS its score.''', '''// (the three-tone mix). gTouch, gTouchIt = the same for the step that makes a trap solid (see trapAdd),
// gTouchS its score and gTouchStr the stretch at that step.''')

# ---- colTrapPick: takes the camera distance; fine layers fade to the palette's mean
rep('''// The colour an orbit trap gives, from the captured values. back: see colPick.
vec3 colTrapPick(float back){''', '''// The colour an orbit trap gives, from the captured values. back and depth: see colPick.
vec3 colTrapPick(float back, float depth){''')
rep('''  // The trap makes the solid, or part of it. Step, side and place are read from the step that touched the trap.
  if (uTrapBy == 1) return pal(0.23 * cTouchIt);
  if (uTrapBy == 3) return pal(colSide(cTouch.xyz));
  vec3 place = pal(colWhere(cTouch.xyz));
  if (uTrapBy == 5 || uTrapSolid < 1.5) return place;''', '''  // The trap makes the solid, or part of it. Step, side and place are read from the step that touched the trap.
  // Close to the set the solid is layer upon layer, each a share 1 / stretch of the thickness across. Once a
  // layer is thinner than a pixel or two its colours can only sparkle, so there they give way to what such a
  // pixel would average out to: the mean of the palette. (A pixel is taken to be about 0.0015 of the distance
  // from the camera across, which is right for the usual picture and only has to be roughly so.)
  vec3 place = pal(uTrapBy == 1 ? 0.23 * cTouchIt : uTrapBy == 3 ? colSide(cTouch.xyz) : colWhere(cTouch.xyz));
  place = mix(place, uPalMean, smoothstep(0.5, 1.5, 0.0015 * max(depth, 0.0) * cTouchStr / max(uTrapW, 1e-6)));
  if (uTrapBy == 1 || uTrapBy == 3 || uTrapBy == 5 || uTrapSolid < 1.5) return place;''')
rep('  if (uColMode <= 1) return colTrapPick(back);', '  if (uColMode <= 1) return colTrapPick(back, depth);')
rep('  if (uInMode == 1) c = colTrapPick(-cIt);', '  if (uInMode == 1) c = colTrapPick(-cIt, -1.0);')
rep('uniform vec3 uPal[${2 * PAL_MAX}], uTrapC, uTrapAx, uTrapOff, uColMu;', 'uniform vec3 uPal[${2 * PAL_MAX}], uTrapC, uTrapAx, uTrapOff, uColMu, uPalMean;')
rep('''// uColJulia, uColMu = which kind of orbit this is, for the running stretch;''', '''// uColJulia, uColMu = which kind of orbit this is, for the running stretch; uPalMean = the mean colour of the
// outside palette;''')

# ---- JS: palette mean, radius dial
rep("const palLoopCache = { key: '', n: 0, f: 1, data: new Float32Array(3 * PAL_MAX) };", "const palLoopCache = { key: '', n: 0, f: 1, data: new Float32Array(3 * PAL_MAX), mean: [0, 0, 0] };")
rep("const palLoopCacheIn = { key: '', n: 0, f: 1, data: new Float32Array(3 * PAL_MAX) };", "const palLoopCacheIn = { key: '', n: 0, f: 1, data: new Float32Array(3 * PAL_MAX), mean: [0, 0, 0] };")
rep("    C.data.fill(0); C.data.set(s.flatMap(h => lin(hexRgb(h))));", "    C.data.fill(0); C.data.set(s.flatMap(h => lin(hexRgb(h))));\n    C.mean = [0, 1, 2].map(j => s.reduce((sum, h, at) => sum + C.data[3 * at + j], 0) / s.length);")
rep("  gl.uniform1i(L('uPalInN'), Pin.n); gl.uniform1f(L('uPalInF'), Pin.f);", "  gl.uniform1i(L('uPalInN'), Pin.n); gl.uniform1f(L('uPalInF'), Pin.f); gl.uniform3fv(L('uPalMean'), P.mean);")
rep("{ type: 'dial', key: 'radius', label: 'Trap radius', min: 0, max: 2, step: 0.01, def: 1, lo: 0, hi: 50, xmax: 10, xhi: 500, when: c => colTrapOn(c) && (c.trap === TRAP.shell || c.trap === TRAP.ring) },",
    "{ type: 'dial', key: 'radius', label: 'Trap radius', min: 0, max: 2, step: 0.01, def: 1, lo: 0, hi: 50, xmax: 10, xhi: 500,\n    when: c => colTrapOn(c) && (c.trap === TRAP.shell || c.trap === TRAP.ring || (colSolidOn(c) && c.trap !== TRAP.point)) },\n  { type: 'note', when: c => colSolidOn(c) && c.trap >= TRAP.cross && c.trap <= TRAP.planes,\n    text: 'As a solid, a line stops at the trap radius from the trap centre, and each plane is a disc of that radius. Left endless they would fill the picture.' },")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
