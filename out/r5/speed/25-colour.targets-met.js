// ---------- colour: palettes, orbit traps, and how a surface point or a 2D pixel is coloured.
// This module owns everything about colour: its controls (COLOUR_CONTROLS -> S.colour), its shader code
// (GL_COLOUR) and its uniforms (setColourUniforms). The renderer only calls the hooks named below.

// A palette is [name, stop, stop, ...] with two to eight stops, spread evenly. A palette whose last stop
// repeats its first runs round in a circle; any other runs to its end and back again, so neither has a seam.
// S.colour.pal is an index into this list: add new palettes at the end so the numbers keep their meaning.
const PALETTES = [
  ['Brass and verdigris', '#c98f33', '#2a8078', '#21386b', '#dbd1b8', '#c98f33'],
  ['Ember', '#2a1430', '#8c1c2c', '#e2622a', '#f6c453', '#fff1cf'],
  ['Glacier', '#0b2545', '#13607a', '#58b3c4', '#d9f0ef', '#8fb8d8'],
  ['Moss and rust', '#26381f', '#5a7a3c', '#b0bf68', '#ece3b2', '#9a5a2a'],
  ['Stone', '#4a4f57', '#858c96', '#bcc1c8', '#e9ebee', '#a39c90'],
  ['Fire', '#200408', '#8a0f0f', '#e8380c', '#ff9a1f', '#ffe45c', '#fffbe6'],
  ['Electric', '#120a3d', '#5a1fd1', '#1f6bff', '#19d3ff', '#e9fdff'],
  ['Sunset', '#1f0f47', '#7a1672', '#d92e62', '#ff7a3d', '#ffc857', '#fff1b8'],
  ['Rainbow', '#ff3d3d', '#ff9a1f', '#ffe234', '#4ddc5a', '#1fd4d0', '#2f8cff', '#7b5cff', '#f04bd0', '#ff3d3d'],
  ['Ocean', '#04143c', '#0b3f86', '#0e86b8', '#2fd0c4', '#b9f7e6'],
  ['Neon', '#1a0b3b', '#ff2fd2', '#34106e', '#1de9ff', '#0f2166', '#b4ff3c', '#1a0b3b'],
  ['Classic blue and gold', '#000764', '#206bcb', '#edffff', '#ffaa00', '#2b1204', '#000764'],
  ['Viridis', '#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'],
  ['Aurora', '#0a2f3f', '#12a37a', '#7df0a2', '#56b7f5', '#7a4fe0', '#e466c8'],
  ['Candy', '#ff5c8a', '#ffb347', '#fff275', '#5fe3b0', '#4aa8ff', '#b07cff', '#ff5c8a'],
  ['Peacock', '#1b1464', '#0b6fa4', '#12b3a0', '#9bd13b', '#f0c33c'],
  ['Ice and fire', '#0a2a7a', '#3aa0f0', '#f3f1e7', '#ff9a2e', '#b3201a'],
  ['Porcelain', '#f3efe6', '#c7d5e8', '#5a7fbd', '#23407f', '#e8dfcf'],
  ['Orchid', '#2a0f3d', '#7a2a8f', '#d05aa8', '#f7b6c8', '#fff4e6'],
];
// The order of the palette menu: vivid ones first, restrained ones last, and warm and cool taking turns at the
// top, so that stepping down the list changes the picture every time (Sunset, Fire and Ember in a row looked
// like one palette). A palette missing from this list is still offered, after the others.
const PAL_MENU = [7, 6, 5, 9, 13, 1, 2, 12, 15, 8, 14, 10, 11, 16, 18, 0, 3, 17, 4];
const PAL_MAX = 16;   // stops the shader has room for: eight out and back
const palMenuOptions = () => [...PAL_MENU, ...PALETTES.keys()].filter((i, at, all) => all.indexOf(i) === at).map(i => [i, PALETTES[i][0]]);

// Trap shapes (S.colour.trap). The numbers are what the shader switches on.
const TRAP = { point: 0, cross: 1, line: 2, ray: 3, planes: 4, shell: 5, ring: 6, tones: 7 };
// Which controls apply. The trap is in use when the surface is coloured by it, when it shapes the solid (3D
// only), or when the inside of the flat picture or of the cut face is coloured by it.
const colSolidAsked = c => !S.flat && c.solid > 0;
const colSolidOn = c => colSolidAsked(c) && c.trap !== TRAP.tones;
const colInsideShown = c => !!S.flat || (!!c.cutFace && !!S.cutOn);
const colInsideOn = c => colInsideShown(c) && c.inMode > 0;
const colTrapColours = c => c.mode <= 1 || (colInsideShown(c) && c.inMode === 1);
const colTrapOn = c => colTrapColours(c) || colSolidAsked(c);
// A trap that has a centre (the three-tone mix has none), and one that has a "colours by" choice as well.
const colTrapShape = c => colTrapOn(c) && c.trap !== TRAP.tones;
const colTrapBy = c => colTrapColours(c) && c.trap !== TRAP.tones;
// Anything that reads the palette.
const colPalOn = c => c.mode <= 5 || colInsideOn(c);
const colGlowOn = c => colTrapBy(c) && c.by === 4;
// The "colours by" choices that go by nearness. On a solid made from the trap every point is equally near the
// trap, so these have nothing to show there (see colPick in the shader for what is shown instead).
const colNearBy = c => c.by === 0 || c.by === 2 || c.by === 4;
// True when every orbit of the picture stays in the plane z = 0: the 2D view of the slice at height 0 (for the
// Kleinian set only while neither the group nor the turning-out sphere leans out of that plane).
const colOrbitsFlat = () => S.flat && S.cut === 0 && (S.mode !== 'k' || (S.k.cz === 0 && S.k.mz === 0));
// How much wider than the others the glow of a thin trap is drawn (see setColourUniforms).
const COL_GLOW_THIN = 1.5;

// Control specs: rendered by buildControls() into the Colour section; values live in S.colour[key].
// Mode 1 is not offered: it was "nearest approach to the origin", which is now the point trap, and the shader
// still reads 1 as "orbit trap". The page opens with what its user picked after trying the rest: a sphere shell
// as the trap, shown as a glow, in the rainbow reversed. The shell's radius of 1 is tuned to that choice: the
// orbits of the usual sets cross that sphere again and again, so its glow draws rings over the whole surface,
// where a smaller shell left the rounder Julia sets one colour.
// A `when` rule may read the page state S as well as the colour values; colViewSync keeps those rules in step.
// xmin, xmax, xlo, xhi are the ranges while "Extreme ranges" is on.
const COLOUR_CONTROLS = [
  { type: 'select', key: 'mode', label: 'Colour by', def: 0, options: [[0, 'Orbit trap'], [2, 'Escape count'], [3, 'Distance from the centre'], [4, 'Depth from the camera'], [5, 'Direction of the last step'], [6, 'Surface direction'], [7, 'Plain clay']] },
  { type: 'note', when: c => S.flat && c.mode === 4, text: 'A flat picture has no depth, so the 2D view shows the escape count here.' },
  { type: 'note', when: c => S.flat && c.mode >= 6, text: 'In the 2D view this choice leaves a plain outline of the set.' },
  { type: 'note', when: c => !S.flat && S.mode !== 'k' && c.mode === 5, text: 'On a solid the last step lands somewhere different for every point, so this choice looks speckled. It is at its best in the 2D view and on the Kleinian set.' },
  { type: 'select', key: 'trap', label: 'Trap shape', def: TRAP.shell, when: colTrapOn,
    options: [[TRAP.point, 'Point'], [TRAP.cross, 'Cross: the three axis lines'], [TRAP.line, 'Line: one axis'], [TRAP.ray, 'Ray: half of one axis'], [TRAP.planes, 'Planes: the three coordinate planes'], [TRAP.shell, 'Sphere shell'], [TRAP.ring, 'Ring in the xy-plane'], [TRAP.tones, 'Three tones, one for each plane']] },
  { type: 'note', when: c => c.mode <= 1, text: 'A trap is a shape left in the path of the orbit. Each point is coloured by how its own orbit passed that shape.' },
  { type: 'note', when: c => S.flat && colTrapColours(c) && (c.trap === TRAP.planes || c.trap === TRAP.ring),
    text: 'In the 2D view, while the slice and the trap centre are both at height 0, the planes show as the same two lines as the cross, and the ring as the same circle as the sphere shell. Raise either one to tell them apart.' },
  { type: 'select', key: 'solid', label: 'In the 3D view the trap', def: 0, when: c => !S.flat && (colTrapShape(c) || c.solid > 0),
    options: [[0, 'Colours the surface'], [1, 'Is the solid'], [2, 'Is added to the solid']] },
  { type: 'note', when: colSolidOn, text: 'The solid now holds every point whose orbit comes within the trap thickness of the trap shape, so each trap shape gives a different object. Each further step of the orbit adds a finer layer of pieces: lower the iterations to keep only the large ones. The 2D view is not changed by this.' },
  { type: 'note', when: c => colSolidAsked(c) && !colSolidOn(c), text: 'Three tones has no shape of its own, so no solid can be made from it. Pick another trap shape.' },
  { type: 'dial', key: 'thick', label: 'Trap thickness', min: 0.005, max: 0.5, step: 0.005, def: 0.05, lo: 0.0005, hi: 5, xmax: 2.5, xhi: 50, when: colSolidOn,
    help: 'How close an orbit has to come to the trap shape for the point it started from to be solid.' },
  { type: 'dial', key: 'skip', label: 'Orbit steps skipped at the start', min: 0, max: 12, step: 1, def: 1, lo: 0, hi: 100, xmax: 60, xhi: 1000, int: true, when: colSolidOn,
    help: 'The trap is ignored for this many steps of each orbit. Higher numbers peel the large outer pieces away and leave the finer ones.' },
  { type: 'select', key: 'by', label: 'Trap colours by', def: 4, when: colTrapBy,
    options: [[0, 'How near the orbit came, in bands'], [4, 'How near it came, as a glow'], [1, 'The step at which it came nearest'], [2, 'Nearness blended with the escape count'], [3, 'The side it came nearest on'], [5, 'Where on the trap it came nearest']] },
  { type: 'note', when: c => colSolidOn(c) && colTrapBy(c) && colNearBy(c),
    text: 'Every point of a solid made from the trap is equally near the trap, so nearness would paint it one flat colour. Those parts are coloured by where on the trap the orbit touched instead. The choices by step and by side work there too.' },
  { type: 'dial', key: 'glow', label: 'Glow width', min: 0.1, max: 8, step: 0.01, def: 1, lo: 0.01, hi: 100, xmax: 40, xhi: 1000, when: colGlowOn,
    help: 'How far from the trap its glow reaches. Try another width if the picture comes out one colour.' },
  { type: 'select', key: 'axis', label: 'Trap line', def: 0, when: c => colTrapOn(c) && c.trap === TRAP.line,
    options: [[0, 'The x-axis'], [1, 'The y-axis'], [2, 'The z-axis']] },
  { type: 'select', key: 'ray', label: 'Trap ray points toward', def: 0, when: c => colTrapOn(c) && c.trap === TRAP.ray,
    options: [[0, '+x'], [1, '−x'], [2, '+y'], [3, '−y'], [4, '+z'], [5, '−z']] },
  { type: 'dial', key: 'radius', label: 'Trap radius', min: 0, max: 2, step: 0.01, def: 1, lo: 0, hi: 50, xmax: 10, xhi: 500,
    when: c => colTrapOn(c) && (c.trap === TRAP.shell || c.trap === TRAP.ring || (colSolidOn(c) && c.trap !== TRAP.point)) },
  { type: 'note', when: c => colSolidOn(c) && c.trap >= TRAP.cross && c.trap <= TRAP.planes,
    text: 'As a solid, a line stops at the trap radius from the trap centre, and each plane is a disc of that radius. Left endless they would fill the picture.' },
  { type: 'dial', key: 'tx', label: 'Trap centre, x', min: -2, max: 2, step: 0.01, def: 0, lo: -50, hi: 50, xmin: -10, xmax: 10, xlo: -500, xhi: 500, when: colTrapShape },
  { type: 'dial', key: 'ty', label: 'Trap centre, y', min: -2, max: 2, step: 0.01, def: 0, lo: -50, hi: 50, xmin: -10, xmax: 10, xlo: -500, xhi: 500, when: colTrapShape },
  { type: 'dial', key: 'tz', label: 'Trap centre, z', min: -2, max: 2, step: 0.01, def: 0, lo: -50, hi: 50, xmin: -10, xmax: 10, xlo: -500, xhi: 500, when: colTrapShape },
  { type: 'select', key: 'pal', label: 'Palette', def: PALETTES.findIndex(p => p[0] === 'Rainbow'), when: colPalOn, options: palMenuOptions() },
  { type: 'check', key: 'rev', label: 'Reverse the palette', def: true, when: colPalOn },
  { type: 'dial', key: 'bands', label: 'Colour bands, how many', min: 0.1, max: 6, step: 0.01, def: 1, lo: 0.01, hi: 50, xmax: 30, xhi: 500, when: colPalOn },
  { type: 'dial', key: 'shift', label: 'Colour bands, shift', min: 0, max: 2, step: 0.005, def: 0, lo: -50, hi: 50, animate: true, when: colPalOn },
  // The flat picture. At these defaults it is drawn exactly as it always was: one pixel of outline, no glow,
  // a plain inside.
  { type: 'dial', key: 'edge', label: 'Outline width, pixels', min: 0, max: 8, step: 0.1, def: 1, lo: 0, hi: 40, xmax: 40, xhi: 400, when: () => !!S.flat,
    help: 'The outline is drawn from the distance estimate, so threads thinner than a pixel still show. 0 leaves it out.' },
  { type: 'dial', key: 'edgeGlow', label: 'Glow beside the outline, pixels', min: 0, max: 60, step: 0.5, def: 0, lo: 0, hi: 400, xmax: 400, xhi: 4000, when: () => !!S.flat,
    help: 'How far the outline fades out into the colours around the set. 0 is no glow.' },
  { type: 'check', key: 'cutFace', label: 'Colour the cut face like the inside of the 2D view', def: false, when: () => !S.flat && !!S.cutOn },
  { type: 'select', key: 'inMode', label: 'Inside the set, colour by', def: 0, when: colInsideShown,
    options: [[0, 'Plain'], [1, 'Orbit trap'], [2, 'Where the orbit ends up'], [3, 'How deep inside'], [4, 'How quickly the orbit settles']] },
  { type: 'note', when: c => colInsideShown(c) && c.inMode === 1, text: 'The inside uses the trap shape and the "Trap colours by" choice above.' },
  { type: 'select', key: 'inPal', label: 'Palette for the inside', def: -1, when: colInsideOn, options: [[-1, 'Same as outside'], ...palMenuOptions()] },
  { type: 'check', key: 'inRev', label: 'Reverse the inside palette', def: false, when: c => colInsideOn(c) && c.inPal >= 0 },
];

// Shader hooks. The renderer includes GL_COLOUR after GL_HEAD, so it may use what GL_HEAD declares:
//   PI, at2(), cmul(), uPow, uBg, uCutCol, uCutInk (linear colours), and the orbit results gIt (smooth step count),
//   gLast (last orbit point), gEsc (1 when the point is outside the solid) and gFade (see trapAdd).
// The renderer calls, in this order:
//   trapStart()            once before each orbit
//   trapAdd(v, it)         after every orbit step, with the new point and the step number
//   colourCapture()        once, right after the ray has hit: copy whatever the colour needs out of the live globals,
//                          because later distance queries (slope, shadows, crevices) overwrite them
//   pixelColour(kind, p, nor, t, d, px, hatch)   the colour of the pixel, whatever kind of pixel it is (see the
//                          function). main() calls it in one place only: the compiler behind WebGL on Windows copies
//                          a function into every place that calls it, and this one carries all the colour code.
//   colourUnlit()          1.0 if the colour of a surface point should be shown as it is, without lighting
// pal(t, inside) reads the palette (the inside one when asked): t = 0 is its first stop, t = 1 its last, and it
// repeats with period 2 (a circular palette goes once round per unit, so it also closes up at 2). trapDist(v) is
// the plain distance from an orbit point to the trap shape in use; it reads only v and uniforms, so other shader
// code may call it whenever it likes. Everything else in here is private (col*, trap*).
//
// A program is built for what the colour settings need (colProgramNeeds below, glNeeds in 30-shaders.js): the
// source is written with TRAP_SOLIDS and COL_INSIDE defined as 1 or 0, and a program built with 0 carries none of
// that code, which is what keeps the usual program quick to prepare and quick to draw. Such a program reads
// uTrapSolid, or uInMode and uCutFace, as constants in place of uniforms.
// Uniforms the renderer's shader code may read: uTrapSolid (0 the trap only colours, 1 it is the solid, 2 it is
// added to the solid), uTrapW (thickness of that solid), uTrapSkip (orbit points with a lower index do not count).
// Private uniforms: uColMode, uTrap, uTrapBy = S.colour.mode, .trap, .by; uPal = two palettes, each a closed loop
// in PAL_MAX slots: the outside one (uPalN stops, gone round uPalF times per unit of t), then the inside one
// (uPalInN, uPalInF); uPalS, uPalO = bands and shift; uTrapC, uTrapR = trap centre and radius; uTrapAx = unit
// vector along the trap line or ray; uTrapOff = added to the distance to each trap plane (a large number switches
// that plane off); uColIter = the step limit of the orbit; uGlowK, uGlowP = the glow's narrowness and the power of
// its fall-off; uColNeed = what trapAdd has to keep (1 the trap measures, 2 the running stretch); uColKlein,
// uColJulia, uColMu = which kind of orbit this is, for the running stretch; uPalMean = the mean colour of the
// outside palette; uInMode = how the inside is coloured
// (0 plain); uEdge, uEdgeGlow = outline width and glow reach of the flat picture, in pixels; uCutFace = 1 when the
// cut face is coloured like the inside.
const GL_COLOUR = `
#ifndef TRAP_SOLIDS
#define TRAP_SOLIDS 1
#endif
#ifndef COL_INSIDE
#define COL_INSIDE 1
#endif
uniform int uColMode, uTrap, uTrapBy, uPalN, uPalInN, uTrapSkip, uColNeed;
uniform float uPalS, uPalO, uPalF, uPalInF, uTrapR, uColIter, uGlowK, uGlowP, uTrapW;
uniform float uEdge, uEdgeGlow, uColKlein, uColJulia;
uniform vec3 uPal[${2 * PAL_MAX}], uTrapC, uTrapAx, uTrapOff, uColMu, uPalMean;
#if TRAP_SOLIDS
uniform float uTrapSolid;
#else
const float uTrapSolid = 0.0;
#endif
#if COL_INSIDE
uniform int uInMode; uniform float uCutFace;
#else
const int uInMode = 0; const float uCutFace = 0.0;
#endif
// While an orbit runs: gNear = where it came nearest the trap (xyz, measured from the trap centre) and how near
// (w), gNearIt = at which step, and gTrap = its nearest approach to each coordinate plane and to the origin
// (the three-tone mix). gTouch, gTouchIt = the same for the step that makes a trap solid (see trapAdd),
// gTouchS its score and gTouchStr the stretch at that step. gStr = the running stretch, gLogS = the sum of the
// logarithms of its factors over gSteps steps. c* are the captured copies.
vec4 gTrap, cTrap, gNear, cNear; float gNearIt, cNearIt, cIt; vec3 cLast;
#if TRAP_SOLIDS
vec4 gTouch, cTouch; float gTouchIt, cTouchIt, gTouchS, cTouchS, gTouchStr, cTouchStr;
#endif
#if TRAP_SOLIDS || COL_INSIDE
float gStr, cStr, gLogS, cLogS, gSteps, cSteps;
#endif
// The plain distance from the orbit point v to the trap shape in use, wherever the trap has been moved to.
// Nothing is read but v and the trap's uniforms and nothing is written, so it may be called from anywhere.
// The three-tone mix has no shape of its own: it stands for the three coordinate planes through the origin.
// While the trap makes the solid (uTrapSolid > 0.5) the endless shapes are cut down to the trap radius.
float trapDist(vec3 v){
  if (uTrap == ${TRAP.tones}){ vec3 a = abs(v) + uTrapOff; return min(a.x, min(a.y, a.z)); }
  vec3 q = v - uTrapC;
  if (uTrap == ${TRAP.point}) return length(q);
#if TRAP_SOLIDS
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
#endif
  if (uTrap == ${TRAP.cross}){ vec3 s = q * q; return sqrt(min(s.x + s.y, min(s.y + s.z, s.z + s.x))); }
  if (uTrap == ${TRAP.line} || uTrap == ${TRAP.ray}){
    float a = dot(q, uTrapAx);
    return uTrap == ${TRAP.ray} && a < 0.0 ? length(q) : sqrt(max(dot(q, q) - a * a, 0.0));
  }
  if (uTrap == ${TRAP.planes}){ vec3 s = abs(q) + uTrapOff; return min(s.x, min(s.y, s.z)); }
  if (uTrap == ${TRAP.shell}) return abs(length(q) - uTrapR);
  return length(vec2(length(q.xy) - uTrapR, q.z));
}
void trapStart(){
  gTrap = vec4(1e9); gNear = vec4(0.0, 0.0, 0.0, 1e9); gNearIt = 0.0;
#if TRAP_SOLIDS
  gTouch = gNear; gTouchIt = 0.0; gTouchS = 1e30; gTouchStr = 1.0;
#endif
#if TRAP_SOLIDS || COL_INSIDE
  gStr = 1.0; gLogS = 0.0; gSteps = 0.0;
#endif
}
// One orbit point. Two things in here are not obvious.
// The fading tail. A ray stops a fraction of a pixel short of the solid, so the colour is read from a point that
// hovers just outside it. Its orbit follows the surface for a while and then flies off, and the last steps of
// that flight pass the trap at places that depend on how high the point hovers, which drew fine rings all over
// the surface. So a point with step number it counts with the weight clamp(gFade + 1 - it, 0, 1): the renderer
// sets gFade a few steps short of the flight (1e9: everything counts). Every measure moves the share "weight"
// of the way to what the point would have made it, so nothing jumps while gFade slides.
// The running stretch. On a solid made from the trap, the step that matters is the one that touches the trap,
// and at a hovering point that is not always the step with the smallest distance: a late step magnifies the
// hover height hundreds of times. The renderer's solid is the least of (distance - thickness) / stretch, so the
// same score is kept here, with the stretch of a pure power (n |v|^(n-1) per step, and |v - mu|^2 per map of the
// Kleinian group) standing in for the true one, which only the renderer knows. That step counts whatever gFade
// says: the flight is where most trap solids are touched.
// This runs at every step of every orbit, so a program that needs neither trap solids nor an inside colouring
// is built without the stretch and the touch record: left in, they slowed the drawing even while switched off.
void trapAdd(vec3 v, float it){
  if (uColNeed == 0) return;
#if TRAP_SOLIDS || COL_INSIDE
  float s = gStr;
  if ((uColNeed & 2) != 0 && it > 0.5){
    float g = uColKlein > 0.5 ? dot(v - uColMu, v - uColMu) : abs(uPow) * pow(max(length(v), 1e-9), uPow - 1.0);
    g = clamp(g, 1e-9, 1e9);
    gLogS += log(g); gSteps += 1.0;
    // an equation's step magnifies what comes after it; a Kleinian map has already magnified the point it made
    gStr = clamp(gStr * g + (uColKlein > 0.5 ? 0.0 : 1.0 - uColJulia), 1e-30, 1e30);
    if (uColKlein > 0.5) s = gStr;
  }
  if ((uColNeed & 1) == 0) return;
#endif
  float w = clamp(gFade + 1.0 - it, 0.0, 1.0);
  if (uTrap == ${TRAP.tones}){
    if (w > 0.0){
      vec4 m = min(gTrap, vec4(abs(v), length(v)));
      if (w >= 1.0 || gTrap.w > 1e8) gTrap = m; else gTrap = mix(gTrap, m, w);
    }
    return;
  }
  float d = trapDist(v);
  if (w > 0.0 && d < gNear.w){
    if (w >= 1.0 || gNear.w > 1e8){ gNear = vec4(v - uTrapC, d); gNearIt = it; }
    else { gNear = mix(gNear, vec4(v - uTrapC, d), w); gNearIt = mix(gNearIt, it, w); }
  }
#if TRAP_SOLIDS
  if (uTrapSolid > 0.5 && it >= float(uTrapSkip)){
    float sc = (d - uTrapW) / s;
    if (sc < gTouchS){ gTouchS = sc; gTouch = vec4(v - uTrapC, d); gTouchIt = it; gTouchStr = s; }
  }
#endif
}
void colourCapture(){
  cTrap = gTrap; cNear = gNear; cNearIt = gNearIt; cIt = gIt; cLast = gLast;
#if TRAP_SOLIDS
  cTouch = gTouch; cTouchIt = gTouchIt; cTouchStr = gTouchStr; cTouchS = gTouchS;
#endif
#if TRAP_SOLIDS || COL_INSIDE
  cStr = gStr; cLogS = gLogS; cSteps = gSteps;
#endif
}
vec3 pal(float t, bool inside){
#if COL_INSIDE
  int N = inside ? uPalInN : uPalN, o = inside ? ${PAL_MAX} : 0;
  float n = float(N), x = fract((t * uPalS + uPalO) * (inside ? uPalInF : uPalF)) * n;
#else
  int N = uPalN, o = 0;
  float n = float(N), x = fract((t * uPalS + uPalO) * uPalF) * n;
#endif
  if (!(x >= 0.0 && x < n)) x = 0.0;   // also catches a value that is not a number
  int i = int(x), j = i + 1 == N ? 0 : i + 1;
  float u = x - float(i);
  return mix(uPal[o + i], uPal[o + j], u * u * (3.0 - 2.0 * u));
}
// a direction as a place in the palette: once round the z-axis is one full period, so there is no seam
float colDir(vec3 v){ return at2(v.y, v.x) / PI + 0.5 * v.z / max(length(v), 1e-20); }
// The side of the trap an orbit passed on, from its offset q at the nearest pass. Beside a line or a ray that is
// the angle round the axis: how far along the axis the pass was says nothing about the side, and it is most of q.
float colSide(vec3 q){
  float a = dot(q, uTrapAx);
  if (uTrap == ${TRAP.line} || (uTrap == ${TRAP.ray} && a > 0.0)){
    vec3 w = q - a * uTrapAx, m = abs(uTrapAx);
    vec2 s = m.x > 0.5 ? w.yz : m.y > 0.5 ? w.zx : w.xy;
    return at2(s.y, s.x) / PI;
  }
  return colDir(q);
}
// The place on the trap an orbit came nearest to, from its offset q there: how far along a line, how far round
// the ring, which way out from the centre of a shell or a point. The lines of the cross and the three planes
// each start a third of the palette apart, so that they can be told from one another.
float colWhere(vec3 q){
  if (uTrap == ${TRAP.line} || uTrap == ${TRAP.ray}) return 0.5 * dot(q, uTrapAx);
  if (uTrap == ${TRAP.ring}) return at2(q.y, q.x) / PI;
  vec3 a = abs(q);
  if (uTrap == ${TRAP.cross}){
    float third = a.x >= a.y && a.x >= a.z ? 0.0 : a.y >= a.z ? 1.0 : 2.0;
    return 0.6667 * third + 0.35 * (third < 0.5 ? q.x : third < 1.5 ? q.y : q.z);
  }
  if (uTrap == ${TRAP.planes}){
    float third = a.x <= a.y && a.x <= a.z ? 0.0 : a.y <= a.z ? 1.0 : 2.0;
    return 0.6667 * third + 0.4 * length(third < 0.5 ? q.yz : third < 1.5 ? q.zx : q.xy);
  }
  return colDir(q);
}
// The colour for every way of colouring that reads the palette, from the captured values. p: the point being
// coloured. depth: its distance from the camera, or negative where there is none (the flat picture, and anything
// inside the solid). inside: the point lies in the solid and is coloured by uInMode (1 to 4) with the inside
// palette; otherwise it is coloured by uColMode (5 or less). deep: how far inside it is, in scene units.
// The branches only work out places in the palette. The palette itself is read at the end, once for each colour
// that can be in the mix: every call of pal() is another copy of it for the compiler, and this function, which
// used to be reached by four paths with seven calls each, was most of the time a new program took to prepare.
vec3 colPick(vec3 p, float depth, bool inside, float deep){
  // Escape count. On a surface nearly every point escapes in the last few steps or not at all, so there it is
  // counted back from the step limit: "never" always lands on the same bright part of the palette, whatever
  // the limit is set to. The flat picture counts forward from zero, so its colours stay put when the limit changes.
  float back = depth > 0.0 ? uColIter - cIt : -cIt;
  float q0 = (depth > 0.0 ? 0.8 : 0.0) - 0.25 * back, q1 = 0.0;   // q0 also stands in for depth in the flat picture
  bool byTrap = uColMode <= 1, tones = false;
#if TRAP_SOLIDS
  float mixW = 0.0; bool mixed = false, mean = false;
#endif
#if COL_INSIDE
  if (inside){
    byTrap = uInMode == 1;
    // where the orbit ends up: the direction of its last point round the palette, shifted by how far out it is
    if (uInMode == 2) q0 = colDir(cLast) + 0.5 * length(cLast);
    // how deep: the square root spreads out the rim, where the estimate is at its best
    else if (uInMode == 3) q0 = 1.3 * sqrt(max(deep, 0.0));
    // how quickly it settles: the average stretch of a step, which runs from 0 where the orbit is drawn in at
    // once to 1 at the edge of the set, where it is only just held
    else if (uInMode != 1) q0 = clamp(exp(cLogS / max(cSteps, 1.0)), 0.0, 1.0);
  } else
#endif
  if (uColMode == 3) q0 = 0.45 * length(p);
  // by ratio, so the colours still change after zooming far in; at the usual viewing distance near is light
  else if (uColMode == 4 && depth > 0.0) q0 = 1.1 - 1.2 * log2(depth);
  else if (uColMode == 5) q0 = colDir(cLast);
  if (byTrap){
    if (uTrap == ${TRAP.tones}) tones = true;
    else {
      // A touch lands on the palette's last stop, so palettes that run dark to light are bright along the trap.
      // The square root spreads out the close calls, where the detail is. "Bands" keeps going through the
      // palette for as long as the distance grows; "glow" dies away instead, stopping just short of the first
      // stop, which in most palettes is too dark to show the shape of a solid. How narrow the glow is and how it
      // falls off depend on the trap (uGlowK, uGlowP: see setColourUniforms).
      float s = sqrt(min(cNear.w, 1e4)), band = 1.0 - 2.0 * s;
      float tNear = uTrapBy == 2 ? band - 0.1 * back : uTrapBy == 4 ? 0.15 + 0.85 * exp(-2.4 * pow(uGlowK * s, uGlowP)) : band;
      vec4 at = cNear; float atIt = cNearIt;
#if TRAP_SOLIDS
      // The trap makes the solid, or part of it. Step, side and place are read from the step that touched the trap.
      bool solid = uTrapSolid > 0.5; float atStr = cTouchStr;
      if (solid){
        at = cTouch; atIt = cTouchIt;
        if (uTrapSkip == 0 && uColJulia > 0.5){
          // A Julia orbit starts at the point itself, which trapAdd never sees: with no steps skipped the trap shape
          // is part of the solid, touched at step 0. The scores of the later steps lack the stretch of the first step.
          float d0 = trapDist(p), first = clamp(abs(uPow) * pow(max(length(p), 1e-9), uPow - 1.0), 1e-9, 1e9);
          if (d0 - uTrapW < cTouchS / first){ at = vec4(p - uTrapC, d0); atIt = 0.0; atStr = 1.0 / first; }
        }
      }
#endif
      float tSide = colSide(at.xyz), tWhere = colWhere(at.xyz);
      q0 = uTrapBy == 1 ? 0.23 * atIt : uTrapBy == 3 ? tSide : uTrapBy == 5 ? tWhere : tNear;
#if TRAP_SOLIDS
      if (solid){
        // Close to the set the solid is layer upon layer, each a share 1 / stretch of the thickness across. Once a
        // layer is thinner than a pixel or two its own colours can only sparkle. (A pixel is taken to be about 0.0015
        // of the distance from the camera across, which is right for the usual picture and only has to be roughly so.)
        float fine = smoothstep(0.5, 1.5, 0.0015 * max(depth, 0.0) * atStr / max(uTrapW, 1e-6));
        mixed = true;
        // Step, side and place give way there to what such a pixel would average out to: the mean of the palette.
        if (uTrapBy == 1 || uTrapBy == 3 || uTrapBy == 5){ mean = true; mixW = fine; }
        else {
          // The choices by nearness. Nearness is the same all over the trap's part of the solid, so that part shows
          // the place it was touched instead, and nearness is left to the rest, where it does vary: the fine layers,
          // and the set's own surface when the trap was added to it. On the trap's part the step that touched lies
          // within the thickness (a little more where the picture is fine).
          q0 = tWhere; q1 = tNear; mixW = max(fine, smoothstep(1.5, 2.5, at.w / max(uTrapW, 1e-6)));
        }
      }
#endif
    }
  }
  vec3 c0 = pal(tones ? 0.0 : q0, inside), c1 = pal(tones ? 0.25 : q1, inside);
  if (tones){
    vec3 a = mix(c0, c1, clamp(1.6 * cTrap.y, 0.0, 1.0));
    a = mix(a, pal(0.5, inside), clamp(2.5 * cTrap.z * cTrap.z, 0.0, 1.0));
    // the fourth tone marks orbits that keep clear of the origin; it comes in gently and never takes over,
    // or everything outside the unit ball would be that one tone
    return mix(a, pal(0.75, inside), 0.5 * smoothstep(0.0, 2.0, cTrap.w));
  }
#if TRAP_SOLIDS
  if (mixed) return mix(c0, mean ? uPalMean : c1, mixW);
#endif
  return c0;
}
float colourUnlit(){ return uColMode == 6 ? 1.0 : 0.0; }
// What kind of pixel pixelColour() is asked about.
const int COL_HIT = 0, COL_FLAT = 1, COL_CUT = 2;
// The colour of one pixel, from the captured values (call colourCapture() first).
//   COL_HIT   a point of the surface, or a volume sample: p position, nor unit normal, t distance from the camera.
//             Returns the unlit colour.
//   COL_FLAT  a pixel of the 2D view: p the slice point, d the distance estimate there (<= 0 inside), px the size
//             of a pixel. Returns the finished colour, outline and all.
//   COL_CUT   a point of the cut face: p the point, hatch the section hatching. Returns hatch unless the user has
//             asked for the cut face to be coloured like the inside of the 2D view.
// Arguments a kind does not use may hold anything.
vec3 pixelColour(int kind, vec3 p, vec3 nor, float t, float d, float px, vec3 hatch){
  bool flat2 = kind == COL_FLAT, inside = false;
  float depth = flat2 ? -1.0 : max(t, 1e-6), deep = -d, e = gEsc * d / px;
#if COL_INSIDE
  if (kind == COL_CUT){
    if (uCutFace < 0.5) return hatch;
    if (uInMode == 0) return uCutCol;
    // The cut face gets no distance estimate from the renderer, so its depth is the one a pure power would give
    // (the renderer's roughest estimate), held to the same limit as the real one. 64 is the escape radius.
    float r = length(cLast);
    deep = min(0.5 * r * log(64.0 / clamp(r, 1e-9, 64.0)) / cStr, 0.75 * length(p) + 0.5);
    inside = true;
  }
  // An inside colouring is read from the orbit, and just outside the set the orbit is a different one, so there
  // is no blending across the edge of the flat picture: the refining passes soften it.
  else if (flat2 && uInMode != 0 && !(e > 0.0)) inside = true;
  if (inside) depth = -1.0;
#else
  if (kind == COL_CUT) return hatch;
#endif
  bool plain = uColMode >= 6 && !inside;   // surface direction and plain clay do not read the palette
  if (plain && !flat2){
    if (uColMode >= 7) return vec3(0.80, 0.78, 0.74);
    vec3 a = 0.5 + 0.5 * nor;
    return a * a;
  }
  // off the solid those two have nothing to show: the flat picture is left a plain silhouette
  vec3 c = plain ? uBg : colPick(p, depth, inside, deep);
  if (!flat2 || inside) return c;
  // Far from the set there is nothing left to show, and colour bands that go on repeating would shrink to a
  // moire once the view is zoomed far out: out there the colours fade into the stage. The 2D view's own range
  // (40 units from top to bottom at its farthest) ends before the fade begins.
  c = mix(c, uBg, smoothstep(40.0, 120.0, length(p.xy)));
  // The solid is drawn like the cut face of the 3D view, with an outline in the hatching ink so that it stays
  // distinct from a palette that happens to end in the same colour. The outline lies on the outside, uEdge
  // pixels wide by the distance estimate, which is what keeps threads thinner than a pixel in the picture; under
  // one pixel it thins out by fading. Beyond it the ink can die away into the colours as a glow.
  if (uEdgeGlow > 0.0) c = mix(c, uCutInk, 0.8 * exp(-max(e - uEdge, 0.0) / uEdgeGlow));
  vec3 ink = uCutInk;
  if (uEdge < 1.0) ink = mix(c, uCutInk, uEdge);
  vec3 outer = mix(ink, c, clamp(e - max(uEdge, 1.0), 0.0, 1.0));
  return uInMode == 0 ? mix(uCutCol, outer, clamp(e, 0.0, 1.0)) : outer;
}`;

// What the scene program has to be able to do for the colour settings in use: the renderer builds one program
// for each answer (sceneWant in 40-render.js) and keeps it under a key that holds the answer, so changing one of
// these settings prepares a new program, shown as "Preparing the formula". Only drop-downs and tick boxes are
// read here, never a dial: moving a dial must not make the page wait. (That is also why the cut face does not
// ask whether the cut is switched on: the height dial switches it on.)
//   solid   the trap is, or is added to, the solid. Asked for in the 2D view too, where it is not drawn: a 3D
//           model made from a 2D picture samples the solid with the same program.
//   inside  the inside of the set is coloured, in the 2D view or on the cut face.
function colProgramNeeds() {
  const c = S.colour;
  return { solid: c.solid > 0 && c.trap !== TRAP.tones, inside: (c.inMode | 0) > 0 && (!!S.flat || !!c.cutFace) };
}

// The palette as the shader wants it: one closed loop of linear colours, and how many loops fit in a unit of t.
// Each cache holds the last palette it was asked for: one for the outside, one for the inside.
const palLoopCache = { key: '', n: 0, f: 1, data: new Float32Array(3 * PAL_MAX), mean: [0, 0, 0] };
const palLoopCacheIn = { key: '', n: 0, f: 1, data: new Float32Array(3 * PAL_MAX), mean: [0, 0, 0] };
const palBoth = new Float32Array(6 * PAL_MAX);
function palLoop(i, rev, C = palLoopCache) {
  const key = i + (rev ? 'r' : 'f');
  if (C.key !== key) {
    let s = (PALETTES[i] || PALETTES[0]).slice(1, 10);
    const round = s.length > 2 && s[0] === s[s.length - 1];
    if (round) { s.pop(); if (rev) s = [s[0], ...s.slice(1).reverse()]; }
    else { s = s.slice(0, 8); if (rev) s.reverse(); s = s.concat(s.slice(1, -1).reverse()); }
    C.key = key; C.n = s.length; C.f = round ? 1 : 0.5;
    C.data.fill(0); C.data.set(s.flatMap(h => lin(hexRgb(h))));
    C.mean = [0, 1, 2].map(j => s.reduce((sum, h, at) => sum + C.data[3 * at + j], 0) / s.length);
  }
  return C;
}
// A CSS gradient of palette i, for a preview strip.
function paletteCss(i, rev) {
  let s = (PALETTES[i] || PALETTES[0]).slice(1);
  if (rev) s = s[0] === s[s.length - 1] ? [s[0], ...s.slice(1, -1).reverse(), s[0]] : s.slice().reverse();
  return `linear-gradient(90deg, ${s.join(', ')})`;
}
// Several `when` rules above read the page state (the 2D view, the cut, the mode), which other modules change
// without telling the colour controls. Called once a frame after anything changed: when one of those three is
// different, every control is asked to show itself again, which re-checks the rules.
const colSeen = { sig: '' };
function colViewSync() {
  const sig = `${!!S.flat}|${!!S.cutOn}|${S.mode}`;
  if (sig === colSeen.sig) return;
  colSeen.sig = sig;
  syncControls();
}
// Set this module's uniforms. L(name) returns the uniform location in the program in use. raw: the call is for
// volume sampling (the 3D model): the flat branch of the shader is in use, but what is asked for is the solid
// and its surface colour as the 3D view has them.
function setColourUniforms(L, raw) {
  if (!hooks.view.includes(colViewSync)) hooks.view.push(colViewSync);
  const c = S.colour, k = S.k, ax = [0, 0, 0], flat = !!S.flat && !raw, flatOrbits = flat && colOrbitsFlat();
  const P = palLoop(c.pal, c.rev), Pin = c.inPal >= 0 ? palLoop(c.inPal, c.inRev, palLoopCacheIn) : P;
  if (c.trap === TRAP.ray) ax[c.ray >> 1] = c.ray & 1 ? -1 : 1; else ax[c.axis] = 1;
  // In the 2D view of the slice z = 0 every orbit stays in that plane, so as one of the three trap planes it
  // would read "touching" everywhere. It is left out there (pushed far away); the other two still cross the picture.
  gl.uniform3f(L('uTrapOff'), 0, 0, flatOrbits && c.tz === 0 ? 1e9 : 0);
  // The glow. Orbits keep crossing a trap that divides the space they move in (a plane or a shell in 3D, any
  // line or circle in a flat slice), so its glow can be narrow, which shows the close passes in fine detail.
  // A trap that is thin in that space (a point anywhere, a line or a ring in 3D) is hardly ever met: the nearest
  // passes all lie in a small range some way off, where a narrow glow has long since faded, and the whole solid
  // came out one colour. Such a trap gets a wider glow with a steadier fall-off (the power 0.75 of the distance
  // in place of its square root).
  const thin = c.trap === TRAP.point || (!flatOrbits && c.trap !== TRAP.planes && c.trap !== TRAP.shell);
  gl.uniform1f(L('uGlowK'), 1 / Math.sqrt((c.glow > 0 ? c.glow : 1) * (thin ? COL_GLOW_THIN : 1)));
  gl.uniform1f(L('uGlowP'), thin ? 1.5 : 1);
  gl.uniform1i(L('uColMode'), c.mode); gl.uniform1f(L('uColIter'), S.mode === 'k' ? k.iter : S.iter);
  gl.uniform1f(L('uPalS'), c.bands); gl.uniform1f(L('uPalO'), c.shift);
  palBoth.set(P.data); palBoth.set(Pin.data, 3 * PAL_MAX);
  gl.uniform3fv(L('uPal[0]'), palBoth); gl.uniform1i(L('uPalN'), P.n); gl.uniform1f(L('uPalF'), P.f);
  gl.uniform1i(L('uPalInN'), Pin.n); gl.uniform1f(L('uPalInF'), Pin.f); gl.uniform3fv(L('uPalMean'), P.mean);
  gl.uniform1i(L('uTrap'), c.trap); gl.uniform1i(L('uTrapBy'), c.by); gl.uniform1f(L('uTrapR'), c.radius);
  gl.uniform3f(L('uTrapC'), c.tx, c.ty, c.tz); gl.uniform3fv(L('uTrapAx'), ax);
  // The trap as a solid: never in the 2D view on screen, whose picture is not to change, and only for a trap
  // that has a shape. Values missing from an older saved state read as the defaults.
  const solid = !flat && c.trap !== TRAP.tones && c.solid > 0 ? +c.solid : 0;
  gl.uniform1f(L('uTrapSolid'), solid); gl.uniform1f(L('uTrapW'), c.thick > 0 ? c.thick : 0.05);
  gl.uniform1i(L('uTrapSkip'), c.skip >= 0 ? c.skip : 1);
  // The inside: always part of the flat picture, and of the cut face when that is asked for.
  const cutFace = !S.flat && !raw && !!c.cutFace, inMode = flat || (cutFace && S.cutOn) ? c.inMode | 0 : 0;
  gl.uniform1i(L('uInMode'), inMode); gl.uniform1f(L('uCutFace'), cutFace ? 1 : 0);
  gl.uniform1f(L('uEdge'), flat && c.edge >= 0 ? c.edge : 1); gl.uniform1f(L('uEdgeGlow'), flat && c.edgeGlow > 0 ? c.edgeGlow : 0);
  // What trapAdd has to keep while an orbit runs: the trap measures when anything is coloured by the trap, and
  // the running stretch for a trap solid's colours and for the inside colourings that are worked out from it.
  const byTrap = c.mode <= 1 || inMode === 1;
  gl.uniform1i(L('uColNeed'), (byTrap ? 1 : 0) | ((byTrap && solid) || inMode >= 3 ? 2 : 0));
  gl.uniform1f(L('uColKlein'), S.mode === 'k' ? 1 : 0); gl.uniform1f(L('uColJulia'), S.mode === 'j' ? 1 : 0);
  gl.uniform3f(L('uColMu'), k.mx, k.my, k.mz);
}
