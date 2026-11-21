"""Round 22, entry: the point at infinity (a pole passed at the start) counts for nothing either. Run once."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(P, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old)
    s = s.replace(old, new)
rep("//                      Called ONCE per step, before any power of that step is taken. A step that starts at the exact\n//                      origin changes nothing (so the orbit of 0, the Mandelbrot orbit, counts from its point c).\n",
    "//                      Called ONCE per step, before any power of that step is taken. A step that starts at the exact\n//                      origin changes nothing (so the orbit of 0, the Mandelbrot orbit, counts from its point c), and\n//                      neither does one that starts at the point at infinity, which the orbit code puts at 1e9 on the\n//                      x-axis when a negative power throws the start of an orbit onto its pole.\n")
rep("const carOrigin = v => !(v[0] * v[0] + v[1] * v[1] + v[2] * v[2] >= 1e-30);\n",
    "const carOrigin = v => { const r2 = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]; return !(r2 >= 1e-30) || r2 >= 1e17; };\n")
rep("float gAoCount;\nvoid carStart(){ gAoCount = 0.0; gCarI = 0; }\nvoid carStep(vec3 z, vec3 c){ if (gCarI == 0 && dot(z, z) >= 1e-30) gAoCount += 1.0; }\n",
    "float gAoCount;\nbool carOrigin(vec3 z){ float r2 = dot(z, z); return !(r2 >= 1e-30) || r2 >= 1e17; }\nvoid carStart(){ gAoCount = 0.0; gCarI = 0; }\nvoid carStep(vec3 z, vec3 c){ if (gCarI == 0 && !carOrigin(z)) gAoCount += 1.0; }\n")
rep("void carStep(vec3 z, vec3 c){\n  if (!(dot(z, z) >= 1e-30)) return;\n",
    "bool carOrigin(vec3 z){ float r2 = dot(z, z); return !(r2 >= 1e-30) || r2 >= 1e17; }\nvoid carStep(vec3 z, vec3 c){\n  if (carOrigin(z)) return;\n")
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
