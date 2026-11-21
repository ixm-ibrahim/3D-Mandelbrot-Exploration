"""Is the 3D rule the lab's own text? For all 21 approaches and both kinds of formula (the squaring short cut at the
power 2, the general power otherwise) the program text the 3D module builds (learnShape3d.source) must hold
  - the approach's GLSL as it stands (a.glsl, the text the solid is drawn with),
  - the lab's step f() and start() as they stand in GL_ORBIT (src/js/30-shaders.js), with the plain equation
    z^n + c and the start 0 compiled by the lab's own compileFormula.
The lines of GL_ORBIT are read here from the source file, not from the module.
"""
import json, os, re
from clab import Lab, Log, ROOT

log = Log("t13_source")
with open(os.path.join(ROOT, "src", "js", "30-shaders.js"), encoding="utf-8") as f:
    sh = f.read()
m = re.search(r"#ifdef APR_CARRY\n(vec3 f\([^\n]*)\n#else\n(vec3 f\([^\n]*)\n#endif\n(vec3 start\([^\n]*)\n", sh)
f_carry, f_plain, start = m.group(1), m.group(2), m.group(3)
log("the lab's own lines (30-shaders.js):"); log("   " + f_carry); log("   " + f_plain); log("   " + start)
with Lab("r26-checka") as lab:
    r = lab.js("""
      const [fCarry, fPlain, start] = %s, rows = [];
      for (const a of LAB.APPROACHES) for (const n2 of [true, false]) {
        const src = LAB.learnShape3d.source(a, n2), fc = LAB.compileFormula('z^n + c', true, n2), zc = LAB.compileFormula('0', false, n2);
        const put = t => t.split('__F__').join(fc).split('__Z0__').join(zc);
        rows.push([a.id, n2, src.includes(a.glsl), src.includes(put(fCarry)), src.includes(put(fPlain)), src.includes(put(start)), fc, zc, src.length, (src.match(/\\bf\\(z, c\\)/g) || []).length]);
      }
      return rows;""" % json.dumps([f_carry, f_plain, start]))
    bad = [x for x in r if not (x[2] and x[3] and x[4] and x[5])]
    log("%d program texts (21 approaches x 2): the approach's GLSL, f() with and without the carry hook, and start() found in all but %d" % (len(r), len(bad)))
    log("   the plain equation compiles to: %s (power 2) and %s (any other power); the start to %s" % (r[0][6], r[1][6], r[0][7]))
    for x in bad: log("   MISSING in %s (n2 %s): glsl %s, f carry %s, f plain %s, start %s" % tuple(x[:6]))
    log.problems(lab)
log("DEFECTS: %d" % len(bad))
