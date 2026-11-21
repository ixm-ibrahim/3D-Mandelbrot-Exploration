"""Round 27, entry: fourth set of edits. Trap solids are switched off for Balls on balls (decision 7): the trap
colours its balls and makes no solid there. See NOTES.md for why."""
import io, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patch_ui import patch, O
patch(O + 'js/25-colour.js', [
 ("const colSolidOn = c => colSolidAsked(c) && c.trap !== TRAP.tones;",
  "// (Balls on balls, the second Kleinian group, has no trap solid: there the trap only colours. colBalls is below.)\nconst colSolidOn = c => colSolidAsked(c) && c.trap !== TRAP.tones && !colBalls();"),
 ("const colTrapOn = c => colTrapColours(c) || colSolidAsked(c);", "const colTrapOn = c => colTrapColours(c) || (colSolidAsked(c) && !colBalls());"),
 ("  { type: 'note', when: c => colSolidOn(c) && typeof ballsTrapCuts === 'function' && ballsTrapCuts(c),\n    text: 'With this trap some pieces come out cut open, with flat faces. For Balls on balls the pieces are whole only while the trap centre has y = 0 and z = 0, and with the honeycomb grid only for a point or a sphere shell.' },\n",
  "  { type: 'note', when: c => colSolidAsked(c) && colBalls(), text: 'Balls on balls has no trap solid: in this view the trap only colours the balls.' },\n"),
 ("  return { solid: c.solid > 0 && c.trap !== TRAP.tones, inside:", "  return { solid: c.solid > 0 && c.trap !== TRAP.tones && !colBalls(), inside:"),
 ("  const solid = !flat && c.trap !== TRAP.tones && c.solid > 0 ? +c.solid : 0;", "  const solid = !flat && c.trap !== TRAP.tones && c.solid > 0 && !colBalls() ? +c.solid : 0;"),
])
patch(O + 'js/50-camera.js', [
 ("  if (!c || !(c.solid > 0) || typeof TRAP === 'undefined' || c.trap === TRAP.tones) return 0;",
  "  if (!c || !(c.solid > 0) || typeof TRAP === 'undefined' || c.trap === TRAP.tones || camBalls()) return 0;   // (Balls on balls has no trap solid)"),
])
patch(O + 'js/46-mesh.js', [
 ("`${['square grid', 'honeycomb grid', 'a line only'][k.bgrid] || 'square grid'}, depth of search ${k.bit}${trap}`;", "`${['square grid', 'honeycomb grid', 'a line only'][k.bgrid] || 'square grid'}, depth of search ${k.bit}`;   // (no trap solid for this group)"),
])
patch(O + 'js/32-balls.js', [
 ("// A trap solid of this group comes out in whole pieces only while the trap is the same on both sides of every slide.\nconst ballsTrapCuts = c => ballsShown() && (c.ty !== 0 || c.tz !== 0 || (S.k.bgrid === 1 && c.trap !== TRAP.point && c.trap !== TRAP.shell));\n", ""),
 ("  // The trap solid takes the place of the balls (1) or joins them (2: whichever surface is nearer).\n#if TRAP_SOLIDS\n  gOnTrap = trapSolid",
  "  // The trap solid takes the place of the balls (1) or joins them (2: whichever surface is nearer).\n  // THE PAGE DOES NOT USE THIS: for this group the colour module never asks for a trap solid (colBalls in\n  // 25-colour.js), so this program is always built with TRAP_SOLIDS 0. Tried and put away in round 27: the trap is\n  // met inside one cell of the grid, so any trap wider than the cell comes out cut open along the cell's flat\n  // faces, and a trap near the point (0, 0, 1), which is the far distance of the picture, grows past the camera.\n  // The cap keeps a ray from leaping when no round was tested (a far point is OUTSIDE at once).\n#if TRAP_SOLIDS\n  if (trapSolid && uTrapSolid < 1.5) bestT = min(bestT, gPix > 0.0 ? max(abs(d), 2.0 * uDetail * gPix) : 0.3);\n  gOnTrap = trapSolid"),
])
