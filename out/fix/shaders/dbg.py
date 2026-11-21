"""Make a debugging copy of a shader file: tints each lit pixel by how its march ended.
red = ran out of steps, green = converged between an outside and an inside point, blue = estimate fell under the threshold.
usage: python out/fix/shaders/dbg.py <in.js> <out.js>"""
import sys
s = open(sys.argv[1], encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a, s.count(a))
    s = s.replace(a, b)
rep("        if (!conv && t <= tMax && n < uSteps) continue;",
    "        if (!conv && t <= tMax && n < uSteps) continue;\n        dbgK = !conv ? 1 : tIn >= 0.0 ? 2 : d < 0.0 ? 4 : 3; dbgN = n;")
rep("  int phase = ORBIT_SCENE ? PH_PROBE", "  int dbgK = 0, dbgN = 0;\n  int phase = ORBIT_SCENE ? PH_PROBE")
rep("    if (colourUnlit() > 0.5) col = alb;",
    "    if (colourUnlit() > 0.5) col = alb;\n    col = mix(col, dbgK == 1 ? vec3(1.0, 0.0, 0.0) : dbgK == 2 ? vec3(0.0, 1.0, 0.0) : dbgK == 4 ? vec3(1.0) : vec3(0.0, 0.0, 1.0), 0.6);")
open(sys.argv[2], 'w', encoding='utf-8').write(s)
