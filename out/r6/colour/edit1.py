"""Round 6, colour: the edits to src/js/30-shaders.js, applied once from the base6 text (kept as a record)."""
import io, sys
p = 'src/js/30-shaders.js'
s = io.open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit('expected %d of: %s (found %d)' % (n, a[:70], s.count(a)))
    s = s.replace(a, b)

# ---- GL_HEAD
rep("""// gFade is set BEFORE a query: an orbit point with step number "it" counts towards the colour trap with the
// weight clamp(gFade + 1 - it, 0, 1), so 1e9 lets every point count in full. Only the query the surface colour
// of the 3D view is read from uses anything else (see TAIL).
// gPix is also set before a query: the size of a pixel where the point asked about lies, or 0 when the
// answer must not depend on the picture (the 2D view, volume sampling).
float gEsc, gIt, gId, gFade, gPix; vec3 gLast, gGrad; bool gOnTrap;""",
"""// gFade is set BEFORE a query: an orbit point with step number "it" counts towards the colour trap with the
// weight clamp(gFade + 1 - it, 0, 1), so 1e9 lets every point count in full. Only the query the surface colour
// of the 3D view or of a 3D model is read from uses anything else: there it is the number of orbit steps the trap
// reads (colourReach() in the colour module), which depends on a dial and on the size of a pixel and on nothing
// else. The Kleinian program has no fading (its trapAdd is built without the weights).
// gPix is also set before a query: the size of a pixel where the point asked about lies, or 0 when the
// answer must not depend on the picture (the 2D view, volume sampling).
// gLand is set before a query too and only the Kleinian search reads it. Above 0 it is a length in the scene:
// the search stops feeding the colour trap at the first step that lands within that length of a pearl or a wall,
// and feeds that last point as if it lay exactly on the wall (the query a hit's trap colour is read from).
float gEsc, gIt, gId, gFade, gPix, gLand; vec3 gLast, gGrad; bool gOnTrap;""")
rep("""const float TRAP_THIN = 2.0;
""", """const float TRAP_THIN = 2.0;
const float MOSAIC_FIT = 0.225;   // cell widths per unit of a mosaic Julia set: a set of radius 2 spans 90% of its cell
""")
rep("""const glNeeds = needs => `#define TRAP_SOLIDS ${needs.solid ? 1 : 0}\\n#define COL_INSIDE ${needs.inside ? 1 : 0}\\n`;""",
"""// The third switch is not a colour setting but the kind of program: COL_KLEIN 1 for the Kleinian search, whose
// trap never fades (gFade is always 1e9 there), so its trapAdd is written without the fading weights.
const glNeeds = (needs, klein) => `#define TRAP_SOLIDS ${needs.solid ? 1 : 0}\\n#define COL_INSIDE ${needs.inside ? 1 : 0}\\n#define COL_KLEIN ${klein ? 1 : 0}\\n`;""")
# ---- GL_ORBIT
rep("""const float MOSAIC_FIT = 0.225;   // cell widths per unit of a mosaic Julia set: a set of radius 2 spans 90% of its cell
const float MOSAIC_BALL""", """const float MOSAIC_BALL""")
# ---- GL_KLEIN
rep("""// Returns the distance to the nearest pearl it met (negative inside one), or to the trap solid, or to both.
float kde(vec3 z){""", """// Returns the distance to the nearest pearl it met (negative inside one), or to the trap solid, or to both.
// land: 0, or (for the query a hit's trap colour is read from) the landing length in the units of the cell. A ray
// stops a fraction of a pixel off a pearl, and left alone the search carries that hovering point on past the wall
// the pearl is an image of, to places that depend on how high it hovered: the trap colours then changed with every
// quality setting. So once a step lands within the landing length of a pearl the search is over: that point is
// fed to the trap as a point of the wall itself, and no later one is.
float kde(vec3 z, float land){""")
rep("""    best = min(best, min(kpearl(z.y, W.y, kk), kpearl(a - z.y, a - W.y, kk)) / DF);""",
"""    float cand = min(kpearl(z.y, W.y, kk), kpearl(a - z.y, a - W.y, kk)) / DF;
    best = min(best, cand);""")
rep("""    trapAdd(z, it);
    if (dot(z - llz, z - llz) < 1e-5) break;""", """    if (land > 0.0 && cand < land){ trapAdd(vec3(z.x, z.y < 0.5 * a ? 0.0 : a, z.z), it); break; }
    trapAdd(z, it);
    if (dot(z - llz, z - llz) < 1e-5) break;""")
rep("""  // inside a wall sphere (unless the trap alone is the solid): no search is needed, and the depth is known
  if (wall < 0.0 && (uTrapSolid < 0.5 || uTrapSolid > 1.5)) { trapStart(); trapAdd(q, 0.0); gIt = 0.0; gLast = q; }
  else d = kde(q);""", """  // The landing length (see kde) in the units of the cell; none while the trap alone is the solid, because then
  // the pearls and the walls are not in the picture.
  bool walls = uTrapSolid < 0.5 || uTrapSolid > 1.5;
  float land = walls ? gLand * R2 / r2 : 0.0;
  // inside a wall sphere (unless the trap alone is the solid): no search is needed, and the depth is known.
  // A hit on a wall sphere has landed before the first step: its trap colour is read from the wall point alone.
  if (walls && wall < land) {
    if (land > 0.0) q.y = q.y < 0.5 * uKMu.y ? 0.0 : uKMu.y;
    trapStart(); trapAdd(q, 0.0); gIt = land > 0.0 ? 8.0 : 0.0; gLast = q;
  }
  else d = kde(q, land);""")
# ---- GL_TAIL
rep("""const int PH_PROBE = 0, PH_MARCH = 1, PH_SLOPE = 2, PH_SHADOW = 3, PH_CUT = 4, PH_AO = 5, PH_COUNT = 6, PH_COLOUR = 7;
const int END_MISS = 8, END_CUT = 9, END_LIT = 10, END_FLAT = 11;""",
"""const int PH_PROBE = 0, PH_MARCH = 1, PH_SLOPE = 2, PH_SHADOW = 3, PH_CUT = 4, PH_AO = 5, PH_COLOUR = 6;
const int END_MISS = 7, END_CUT = 8, END_LIT = 9, END_FLAT = 10;""")
a = s.index("// A ray stops a fraction of a pixel short of the solid, so the colour is read from a point that hovers just")
b = s.index("// the four corners of a tetrahedron")
s = s[:a] + """// The colour an orbit trap gives a hit must be a property of the surface, not of the ray that found it. A ray
// stops a fraction of a pixel short of the solid, at a height that every quality setting sets differently, and the
// orbit of that hovering point keeps to the surface for a while and then flies off: where the flight passes the
// trap depends on the height, which changes smoothly from pixel to pixel. Read from there, with every step
// counting, the trap painted rings over the solid, one for every extra step, like a stack of slices, and the
// colours moved with the quality settings, the step limit and the distance from the camera. Two things cure it.
// 1. The colour is read from the surface itself: the hit is moved down its own normal by the height it hovers at
//    ("lift": what the distance estimate read where the march ended, or for the fastest estimate, which reads too
//    short, the mean of the four slope samples scaled by the gauge).
// 2. The trap reads a fixed number of orbit steps (gFade = colourReach(pixel), in the colour module): the number
//    on the "Orbit steps the trap reads" dial, or fewer where a pixel cannot show that many. "The nearest the
//    first K orbit points come to the trap" is a continuous function of the starting point, inside and outside
//    the solid alike, so what is left of the height does not show. The pixel meant is one of the page (uPx
//    picture pixels), so the moving preview, every quality setting and a saved picture of any size agree.
// Colours that do not come from a trap are read from the hit point as before, so that they do not change.
""" + s[b:]
rep("""  float t = spanOut.x, tOut = 0.0, dOut = 0.0, tIn = -1.0, gauge = 1.0, ts = 0.0, res = 1.0, ao = 0.0, d = 0.0, fade = 1e9;""",
    """  float t = spanOut.x, tOut = 0.0, dOut = 0.0, tIn = -1.0, gauge = 1.0, ts = 0.0, res = 1.0, ao = 0.0, d = 0.0, lift = 0.0;""")
rep("""    // The step the colour of a hit begins with. The tail is not faded where the step count is not a smooth
    // measure of how long the orbit kept to the surface: the Kleinian search, and inside-out solids.
    int qn = nt, hue = ORBIT_SCENE && !gInsideOut ? PH_COUNT : PH_COLOUR;
    gAsk = ASK_PLAIN; gFade = 1e9; gPix = flat2 ? 0.0 : pix * t;""",
"""    int qn = nt;
    gAsk = ASK_PLAIN; gFade = 1e9; gLand = 0.0; gPix = flat2 ? 0.0 : pix * t;
    // the size of a page pixel at this point, in the units the orbit runs in (a mosaic set is drawn small)
    float pagePix = (flat2 ? uFlatH / uRes.y : pix * t * uPx) / (mosaic ? uMosaic * MOSAIC_FIT : 1.0);""")
rep("""    else if (flat2) qn = 3;
    else if (phase == PH_COUNT) qn = min(nt, 1);
    else if (phase == PH_COLOUR && !gInsideOut){
      // the colour needs the orbit, not the distance (but with a trap solid, also which of the two was hit)
      qn = uTrapSolid > 0.5 ? min(nt, 1) : 0; gFade = fade;
    }""",
"""    else if (flat2){
      // a volume sample for a 3D model is coloured by the rule of the 3D view, with the sample spacing as the pixel
      qn = 3; if (ORBIT_SCENE && uRaw > 0.5) gFade = colourReach(pagePix);
    } else if (phase == PH_COLOUR){
      // the colour needs the orbit, not the distance (but with a trap solid, also which of the two was hit)
      if (!gInsideOut) qn = uTrapSolid > 0.5 ? min(nt, 1) : 0;
      if (colourFromTrap()){
        q = p - nor * lift;
        if (ORBIT_SCENE) gFade = colourReach(pagePix);
        else gLand = max(pix * t * uPx, 0.5 * e);
      }
    }""")
rep("""    if (phase == PH_COUNT){
      // gIt is the smooth step count of the hit (the step limit when its orbit never leaves). A hit on a trap
      // solid is not faded: that surface is made by one early step, and its colour is read from that step.
      fade = min(gIt, -log(pix * t * max(uPx, uDetail)) / log(max(abs(uPow), 1.5)) + LEVEL_STEPS);
      fade = gOnTrap ? 1e9 : max(fade - TAIL, 1.0);
      phase = PH_COLOUR; continue;
    }
""", "")
rep("""      nor += tetra(n) * d; n++;
      if (n < 4) continue;
      if (rough) gauge = clamp(4.0 * uNormEps * e / max(length(nor), 1e-30), 1.0, 64.0);""",
"""      nor += tetra(n) * d; n++;
      if (rough) lift += 0.25 * d;
      if (n < 4) continue;
      if (rough){ gauge = clamp(4.0 * uNormEps * e / max(length(nor), 1e-30), 1.0, 64.0); lift *= gauge; }""")
# the march: leave in d what the estimate read, less the level, at the place the ray ends
rep("""            t = tOut + (t - tOut) * clamp(dOut / (dOut - d), 0.0, 1.0); conv = true;""",
    """            t = tOut + (t - tOut) * clamp(dOut / (dOut - d), 0.0, 1.0); conv = true; d = 0.0;""")
rep("""              if (tIn - tOut < 0.5 * e){ conv = true; if (!rough) t = tOut; }""",
    """              if (tIn - tOut < 0.5 * e){ conv = true; if (!rough){ t = tOut; d = dOut; } }""")
rep("""        n = 0;
        // the set's own slope says nothing about a trap solid, so with one in the picture the slope is sampled""",
"""        n = 0;
        // How high above the solid the ray has stopped: on the level, give or take what is left in d. (A ray that
        // ran out of steps has moved on since its last reading, and the fastest estimate is gauged by the slope
        // samples that follow.)
        lift = rough ? 0.0 : LEVEL * e + (conv ? clamp(d, -e, e) : 0.0);
        // the set's own slope says nothing about a trap solid, so with one in the picture the slope is sampled""")
rep("""        n = 0; phase = uAO > 0.5 ? PH_AO : hue;""", """        n = 0; phase = uAO > 0.5 ? PH_AO : PH_COLOUR;""")
rep("""        if (n == 4) phase = hue;""", """        if (n == 4) phase = PH_COLOUR;""")
rep("""      phase = uShadow > 0.5 && dot(nor, L) > 0.001 ? PH_SHADOW : uAO > 0.5 ? PH_AO : hue;""",
    """      phase = uShadow > 0.5 && dot(nor, L) > 0.001 ? PH_SHADOW : uAO > 0.5 ? PH_AO : PH_COLOUR;""")
rep("""  int budget = gate2 + turns * 6 + 2;""", """  int budget = gate2 + turns * 5 + 2;""")
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
