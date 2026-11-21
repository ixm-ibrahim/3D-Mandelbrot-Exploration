"""Private stand-ins of base4's 30-shaders.js for testing the colour module before the real shader arrives.

  30-shaders-id.js   base4 plus `float gFade;`, always 1e9: every picture must equal base4's.
  30-shaders.js      the same plus a rough version of what CONTRACT4 asks of the shader: the two colour queries
                     (gFade = count - TAIL), trap solids (uTrapSolid, uTrapW, uTrapSkip) and cutFaceColour.
Run from the workspace root: python out/r4/colour/mk_standin.py
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src = open(os.path.join(ROOT, 'base4', 'js', '30-shaders.js'), encoding='utf-8').read()


def rep(s, old, new, count=1):
    assert s.count(old) == count, (old, s.count(old))
    return s.replace(old, new)


# ----- identity stand-in
ident = rep(src, 'float gEsc, gIt, gId; vec3 gLast, gGrad;', 'float gEsc, gIt, gId, gFade; vec3 gLast, gGrad;')
ident = rep(ident, '  gInsideOut = false; gPowerLaw = true; gId = 0.0;', '  gInsideOut = false; gPowerLaw = true; gId = 0.0; gFade = 1e9;')
open(os.path.join(ROOT, 'out', 'r4', 'colour', '30-shaders-id.js'), 'w', encoding='utf-8', newline='\n').write(ident)

# ----- working stand-in
s = ident
# the two colour queries
s = rep(s, 'const float LEVEL = 0.8;', 'const float LEVEL = 0.8;\nconst float TAIL = __TAIL__;')
s = rep(s, '  int phase = ORBIT_SCENE ? PH_PROBE : flat2 ? PH_COLOUR : PH_MARCH, n = 0, nt = uNT, crawl = 0;',
        '  int phase = ORBIT_SCENE ? PH_PROBE : flat2 ? PH_COLOUR : PH_MARCH, n = 0, nt = uNT, crawl = 0;\n  bool counted = false; float fade = 1e9;')
s = rep(s, '  int budget = gate2 + turns * 5 + 2;', '  int budget = gate2 + turns * 7 + 2;')
s = rep(s, '    d = de(q, qn, dir);\n', '    gFade = phase == PH_COLOUR && counted ? fade : 1e9;\n    d = de(q, qn, dir);\n')
s = rep(s, '    if (phase == PH_COLOUR){ phase = flat2 ? END_FLAT : END_LIT; break; }',
        '    if (phase == PH_COLOUR){\n'
        '      if (!flat2 && !counted){ counted = true; fade = max((gEsc > 0.5 ? gIt : float(uIter)) - TAIL, 1.0); continue; }\n'
        '      phase = flat2 ? END_FLAT : END_LIT; break;\n    }')
# trap solids, equations
s = rep(s, '  bool esc = false, still = false;\n  trapStart();',
        '  bool esc = false, still = false;\n  float tb = 1e30;\n  trapStart();\n'
        '  if (uTrapSolid > 0.5 && uTrapSkip == 0 && jul) tb = trapDist(v) - uTrapW;')
s = rep(s, '    trapAdd(v, it);\n  }\n  gLast = v; gIt = it;',
        '    trapAdd(v, it);\n'
        '    if (uTrapSolid > 0.5 && it >= float(uTrapSkip)){\n'
        '      float lmx = nt == 3 ? max(ls1, max(ls2, ls3)) : ls1;\n'
        '      float st = nt == 3 ? sqrt(dot(dv1, dv1) * exp(2.0 * (ls1 - lmx)) + dot(dv2, dv2) * exp(2.0 * (ls2 - lmx)) + dot(dv3, dv3) * exp(2.0 * (ls3 - lmx))) : nt == 1 ? length(dv1) : dv1.x;\n'
        '      if (lmx < 60.0) tb = min(tb, (trapDist(v) - uTrapW) / max(st * exp(lmx), 1e-20));\n'
        '    }\n'
        '  }\n  gLast = v; gIt = it;')
s = rep(s, '  float cap = 0.75 * length(p) + 0.5;\n',
        '  if (uTrapSolid > 0.5 && gAsk != ASK_PROBE && gAsk != ASK_CELL){\n'
        '    float own = outside ? max(d, 0.0) : min(d, 0.0);\n'
        '    d = uTrapSolid > 1.5 ? min(own, tb) : tb;\n'
        '    outside = d > 0.0; gEsc = outside ? 1.0 : 0.0; gGrad = vec3(0.0);\n'
        '  }\n'
        '  float cap = 0.75 * length(p) + 0.5;\n')
s = rep(s, '        if (uAnalytic < 0.5 || nt != 3 || gInsideOut){ phase = PH_SLOPE; continue; }',
        '        if (uAnalytic < 0.5 || nt != 3 || gInsideOut || uTrapSolid > 0.5){ phase = PH_SLOPE; continue; }')
# trap solids, Kleinian
s = rep(s, '  float best = min(z.y, a - z.y);   // distance to the two walls, before any map is applied',
        '  float best = min(z.y, a - z.y);   // distance to the two walls, before any map is applied\n  float tb = 1e30;')
s = rep(s, '    trapAdd(z, it);\n    if (dot(z - llz, z - llz) < 1e-5) break;',
        '    trapAdd(z, it);\n'
        '    if (uTrapSolid > 0.5 && it >= float(uTrapSkip)) tb = min(tb, (trapDist(z) - uTrapW) / max(DF, 1.0));\n'
        '    if (dot(z - llz, z - llz) < 1e-5) break;')
s = rep(s, '  gIt = it; gLast = z;\n  return min(best, 0.3);',
        '  gIt = it; gLast = z;\n  if (uTrapSolid > 0.5) best = uTrapSolid > 1.5 ? min(best, tb) : tb;\n  return min(best, 0.3);')
# cut face
s = rep(s, '    col = mix(uCutCol, uCutInk, 0.55 * smoothstep(0.36, 0.42, s));',
        '    col = mix(uCutCol, uCutInk, 0.55 * smoothstep(0.36, 0.42, s));\n    colourCapture();\n    col = cutFaceColour(p, col);')
import sys
tail = sys.argv[1] if len(sys.argv) > 1 else '4.0'
open(os.path.join(ROOT, 'out', 'r4', 'colour', '30-shaders.js'), 'w', encoding='utf-8', newline='\n').write(s.replace('__TAIL__', tail))
print('wrote the two stand-ins, TAIL =', tail)
