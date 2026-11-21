# Round 29: 68-learn-shape3d.js gets one more function, orbit(), beside out(). Nothing else changes.
import sys
sys.dont_write_bytecode = True
from patchlib import Patch, frag

p = Patch('js/68-learn-shape3d.js')
p.rep("//   view.slicePoint(row, col, opt), view.time(o, reps), view.stats(), learnShape3d.source(approach, n2)\n",
      "//   view.slicePoint(row, col, opt), view.time(o, reps), view.stats(), learnShape3d.source(approach, n2)\n"
      "//   learnShape3d.orbit(p, kind, c, maxK)   (round 29) out() with the places kept: where the point is after each step\n")
p.before("\n  // ----- the camera, shared with whoever draws on top of the picture\n", "\n" + frag('68-orbit.js').rstrip('\n') + "\n")
p.rep("  return { make, out, ok: () => okFlag, note: () => noteText, proj, source: sourceFor };\n",
      "  return { make, out, orbit, ok: () => okFlag, note: () => noteText, proj, source: sourceFor };\n")
p.write()
