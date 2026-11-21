"""Round 22, entry: the four hooks APR_CARRY in src/js/30-shaders.js (GL_ORBIT). Idempotent: refuses to run twice."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = os.path.join(ROOT, 'src', 'js', '30-shaders.js')
s = io.open(P, encoding='utf-8').read()
if 'APR_CARRY' in s:
    sys.exit('already patched')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old)
    s = s.replace(old, new)
rep("// An approach's GLSL defines mul, pw, sqr and cmap, and may define APR_ZMAP with zmap (see orbitDE).\n",
    "// An approach's GLSL defines mul, pw, sqr and cmap, and may define APR_ZMAP with zmap (see orbitDE).\n"
    "// An approach whose orbit carries something besides its point defines APR_CARRY with carStart, carStep, carFit and\n"
    "// gCarI (see GL_CARRY in 10-approaches.js). Every use of them below stands between #ifdef APR_CARRY and #endif, so the\n"
    "// program of an approach that carries nothing is, once the preprocessor has run, the program it was before.\n")
rep("vec3 f(vec3 z, vec3 c){ z = mix(z, abs(z), uAbs) * uSgn; return __F__; }\n",
    "#ifdef APR_CARRY\n"
    "vec3 f(vec3 z, vec3 c){ z = mix(z, abs(z), uAbs) * uSgn; carStep(z, c); return __F__; }\n"
    "#else\n"
    "vec3 f(vec3 z, vec3 c){ z = mix(z, abs(z), uAbs) * uSgn; return __F__; }\n"
    "#endif\n")
rep("  vec3 c = vec3(0.0), v = vec3(0.0);\n  for (int i = 0; i <= nt; i++){   // i = 0 is the point itself, the others its neighbours\n",
    "  vec3 c = vec3(0.0), v = vec3(0.0);\n"
    "  // What an orbit carries besides its point (APR_CARRY) is made fresh here, for the point and for every neighbour:\n"
    "  // this is the only place an orbit begins, whatever the query is for (the picture, its light, a colour, the cut,\n"
    "  // the 2D view, a mosaic cell or its Julia set, a pick, a sample of a 3D model).\n"
    "#ifdef APR_CARRY\n"
    "  carStart();\n"
    "#endif\n"
    "  for (int i = 0; i <= nt; i++){   // i = 0 is the point itself, the others its neighbours\n")
rep("      vec3 wi = f(v + dz, c + dk);\n",
    "#ifdef APR_CARRY\n"
    "      gCarI = i;   // the step that follows belongs to this orbit, and reads and changes what this orbit carries\n"
    "      bool seam = false;\n"
    "#endif\n"
    "      vec3 wi = f(v + dz, c + dk);\n")
rep("          dw = dz * max(pn * length(w - c) / max(r, 1e-6), 1e-3); m = length(dw);\n",
    "          dw = dz * max(pn * length(w - c) / max(r, 1e-6), 1e-3); m = length(dw);\n"
    "#ifdef APR_CARRY\n"
    "          seam = true;\n"
    "#endif\n")
rep("        if (m > 0.0){ float s = clamp(2e-3 * (lw + 1e-3) / m, 1e-8, 1e8); dw *= s; dk *= s; lg = log(s); }\n        else dw = vec3(0.0);\n",
    "#ifdef APR_CARRY\n"
    "        if (m > 0.0){ float s = clamp(2e-3 * (lw + 1e-3) / m, 1e-8, 1e8); dw *= s; dk *= s; lg = log(s); carFit(i, seam ? 0.0 : s); }\n"
    "        else { dw = vec3(0.0); carFit(i, 0.0); }\n"
    "#else\n"
    "        if (m > 0.0){ float s = clamp(2e-3 * (lw + 1e-3) / m, 1e-8, 1e8); dw *= s; dk *= s; lg = log(s); }\n"
    "        else dw = vec3(0.0);\n"
    "#endif\n")
rep("      v = vec3(1e9, 0.0, 0.0); r = 0.0; steps -= 1.0;\n",
    "      v = vec3(1e9, 0.0, 0.0); r = 0.0; steps -= 1.0;\n"
    "#ifdef APR_CARRY\n"
    "      carStart();   // the orbit begins again from the point at infinity, and so does what it carries\n"
    "#endif\n")
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', P)
