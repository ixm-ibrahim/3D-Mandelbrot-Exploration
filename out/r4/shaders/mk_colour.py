"""Make the private stand-in of the colour module: base4's 25-colour.js plus what CONTRACT4 promises
(the fading weights in trapAdd, uTrapSolid / uTrapW / uTrapSkip, cutFaceColour). Test use only."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src = io.open(os.path.join(ROOT, 'base4/js/25-colour.js'), encoding='utf-8').read().replace('\r\n', '\n')
def rep(a, b):
    global src
    if a not in src: sys.exit('missing: ' + a[:60])
    src = src.replace(a, b, 1)
rep("// ---------- colour:", "// TEST STAND-IN (out/r4/shaders): base4's colour module plus the names of CONTRACT4, until the real one arrives.\n// ---------- colour:")
rep("uniform float uPalS, uPalO, uPalF, uTrapR, uColIter, uGlowK, uGlowP;",
    "uniform float uPalS, uPalO, uPalF, uTrapR, uColIter, uGlowK, uGlowP, uTrapSolid, uTrapW, uCutFace;\nuniform int uTrapSkip;")
rep("""void trapAdd(vec3 v, float it){
  if (uColMode > 1) return;
  if (uTrap == ${TRAP.tones}){ gTrap = min(gTrap, vec4(abs(v), length(v))); return; }
  float d = trapDist(v);
  if (d < gNear.w){ gNear = vec4(v - uTrapC, d); gNearIt = it; }
}""", """void trapAdd(vec3 v, float it){
  if (uColMode > 1) return;
  float w = gFade + 1.0 - it;
  if (w <= 0.0) return;
  if (uTrap == ${TRAP.tones}){
    vec4 m = min(gTrap, vec4(abs(v), length(v)));
    if (w >= 1.0) gTrap = m; else gTrap += w * (m - gTrap);
    return;
  }
  float d = trapDist(v);
  if (d < gNear.w){
    vec4 nw = vec4(v - uTrapC, d);
    if (w >= 1.0){ gNear = nw; gNearIt = it; }
    else { gNear += w * (nw - gNear); gNearIt += w * (it - gNearIt); }
  }
}""")
rep("float colourUnlit(){", """vec3 cutFaceColour(vec3 p, vec3 hatch){
  if (uCutFace < 0.5) return hatch;
  return mix(hatch, pal(1.0 - 2.0 * sqrt(min(cNear.w, 1e4))), 0.8);
}
float colourUnlit(){""")
rep("function setColourUniforms(L) {", "function setColourUniforms(L, raw) {")
rep("  gl.uniform3f(L('uTrapC'), c.tx, c.ty, c.tz); gl.uniform3fv(L('uTrapAx'), ax);",
    "  gl.uniform3f(L('uTrapC'), c.tx, c.ty, c.tz); gl.uniform3fv(L('uTrapAx'), ax);\n"
    "  gl.uniform1f(L('uTrapSolid'), S.flat && !raw ? 0 : (c.solid || 0)); gl.uniform1f(L('uTrapW'), c.thick ?? 0.05); gl.uniform1i(L('uTrapSkip'), c.skip ?? 1);\n"
    "  gl.uniform1f(L('uCutFace'), c.cutFace ? 1 : 0);")
io.open(os.path.join(ROOT, 'out/r4/shaders/25-colour.js'), 'w', encoding='utf-8', newline='\n').write(src)
print('wrote out/r4/shaders/25-colour.js')
