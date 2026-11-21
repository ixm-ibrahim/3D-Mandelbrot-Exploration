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

// Trap shapes (S.colour.trap). The numbers are what the shader switches on.
const TRAP = { point: 0, cross: 1, line: 2, ray: 3, planes: 4, shell: 5, ring: 6, tones: 7 };
// Which controls apply: colouring by an orbit trap; by a trap that has a centre and a "colours by" choice
// (the three-tone mix has neither); by anything that reads the palette.
const colTrapOn = c => c.mode <= 1;
const colTrapShape = c => colTrapOn(c) && c.trap !== TRAP.tones;
const colPalOn = c => c.mode <= 5;
const colGlowOn = c => colTrapShape(c) && c.by === 4;
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
const COLOUR_CONTROLS = [
  { type: 'select', key: 'mode', label: 'Colour by', def: 0, options: [[0, 'Orbit trap'], [2, 'Escape count'], [3, 'Distance from the centre'], [4, 'Depth from the camera'], [5, 'Direction of the last step'], [6, 'Surface direction'], [7, 'Plain clay']] },
  { type: 'note', when: c => S.flat && c.mode === 4, text: 'A flat picture has no depth, so the 2D view shows the escape count here.' },
  { type: 'note', when: c => S.flat && c.mode >= 6, text: 'In the 2D view this choice leaves a plain outline of the set.' },
  { type: 'note', when: c => !S.flat && S.mode !== 'k' && c.mode === 5, text: 'On a solid the last step lands somewhere different for every point, so this choice looks speckled. It is at its best in the 2D view and on the Kleinian set.' },
  { type: 'select', key: 'trap', label: 'Trap shape', def: TRAP.shell, when: colTrapOn,
    options: [[TRAP.point, 'Point'], [TRAP.cross, 'Cross: the three axis lines'], [TRAP.line, 'Line: one axis'], [TRAP.ray, 'Ray: half of one axis'], [TRAP.planes, 'Planes: the three coordinate planes'], [TRAP.shell, 'Sphere shell'], [TRAP.ring, 'Ring in the xy-plane'], [TRAP.tones, 'Three tones, one for each plane']] },
  { type: 'note', when: colTrapOn, text: 'A trap is a shape left in the path of the orbit. Each point is coloured by how its own orbit passed that shape.' },
  { type: 'note', when: c => S.flat && colTrapOn(c) && (c.trap === TRAP.planes || c.trap === TRAP.ring),
    text: 'In the 2D view, while the slice and the trap centre are both at height 0, the planes show as the same two lines as the cross, and the ring as the same circle as the sphere shell. Raise either one to tell them apart.' },
  { type: 'select', key: 'by', label: 'Trap colours by', def: 4, when: colTrapShape,
    options: [[0, 'How near the orbit came, in bands'], [4, 'How near it came, as a glow'], [1, 'The step at which it came nearest'], [2, 'Nearness blended with the escape count'], [3, 'The side it came nearest on']] },
  { type: 'dial', key: 'glow', label: 'Glow width', min: 0.1, max: 8, step: 0.01, def: 1, lo: 0.01, hi: 100, when: colGlowOn,
    help: 'How far from the trap its glow reaches. Try another width if the picture comes out one colour.' },
  { type: 'select', key: 'axis', label: 'Trap line', def: 0, when: c => colTrapOn(c) && c.trap === TRAP.line,
    options: [[0, 'The x-axis'], [1, 'The y-axis'], [2, 'The z-axis']] },
  { type: 'select', key: 'ray', label: 'Trap ray points toward', def: 0, when: c => colTrapOn(c) && c.trap === TRAP.ray,
    options: [[0, '+x'], [1, '−x'], [2, '+y'], [3, '−y'], [4, '+z'], [5, '−z']] },
  { type: 'dial', key: 'radius', label: 'Trap radius', min: 0, max: 2, step: 0.01, def: 1, lo: 0, hi: 50, when: c => colTrapOn(c) && (c.trap === TRAP.shell || c.trap === TRAP.ring) },
  { type: 'dial', key: 'tx', label: 'Trap centre, x', min: -2, max: 2, step: 0.01, def: 0, lo: -50, hi: 50, when: colTrapShape },
  { type: 'dial', key: 'ty', label: 'Trap centre, y', min: -2, max: 2, step: 0.01, def: 0, lo: -50, hi: 50, when: colTrapShape },
  { type: 'dial', key: 'tz', label: 'Trap centre, z', min: -2, max: 2, step: 0.01, def: 0, lo: -50, hi: 50, when: colTrapShape },
  { type: 'select', key: 'pal', label: 'Palette', def: PALETTES.findIndex(p => p[0] === 'Rainbow'), when: colPalOn,
    options: [...PAL_MENU, ...PALETTES.keys()].filter((i, at, all) => all.indexOf(i) === at).map(i => [i, PALETTES[i][0]]) },
  { type: 'check', key: 'rev', label: 'Reverse the palette', def: true, when: colPalOn },
  { type: 'dial', key: 'bands', label: 'Colour bands, how many', min: 0.1, max: 6, step: 0.01, def: 1, lo: 0.01, hi: 50, when: colPalOn },
  { type: 'dial', key: 'shift', label: 'Colour bands, shift', min: 0, max: 2, step: 0.005, def: 0, lo: -50, hi: 50, animate: true, when: colPalOn },
];

// Shader hooks. The renderer includes GL_COLOUR after GL_HEAD, so it may use what GL_HEAD declares:
//   PI, at2(), cmul(), uBg, uCutCol, uCutInk (linear colours), and the orbit results gIt (smooth step count),
//   gLast (last orbit point) and gEsc (1 when the point is outside the solid).
// The renderer calls, in this order:
//   trapStart()            once before each orbit
//   trapAdd(v, it)         after every orbit step, with the new point and the step number
//   colourCapture()        once, right after the ray has hit: copy whatever the colour needs out of the live globals,
//                          because later distance queries (slope, shadows, crevices) overwrite them
//   surfaceColour(p, nor, t)   the unlit colour of the hit: p position, nor unit normal, t distance from the camera
//   colourUnlit()          1.0 if that colour should be shown as it is, without lighting
//   flatColour(p, d, px)   2D view: the final colour of a slice pixel. Called right after the orbit, so the live
//                          globals are valid. d is the distance estimate (<= 0 inside), px the size of a pixel.
// pal(t) reads the palette: t = 0 is its first stop, t = 1 its last, and it repeats with period 2 (a circular
// palette goes once round per unit, so it also closes up at 2). trapDist(v) is the plain distance from an orbit
// point to the trap shape in use; it reads only v and uniforms, so other shader code may call it whenever it
// likes. Everything else in here is private (col*, trap*).
// Uniforms: uColMode, uTrap, uTrapBy = S.colour.mode, .trap, .by; uPal[uPalN] = the palette as a closed loop,
// gone round uPalF times per unit of t; uPalS, uPalO = bands and shift; uTrapC, uTrapR = trap centre and radius;
// uTrapAx = unit vector along the trap line or ray; uTrapOff = added to the distance to each trap plane
// (a large number switches that plane off); uColIter = the step limit of the orbit; uGlowK, uGlowP = the glow's
// narrowness and the power of its fall-off.
const GL_COLOUR = `
uniform int uColMode, uTrap, uTrapBy, uPalN;
uniform float uPalS, uPalO, uPalF, uTrapR, uColIter, uGlowK, uGlowP;
uniform vec3 uPal[${PAL_MAX}], uTrapC, uTrapAx, uTrapOff;
// STAND-IN (kleinian engineer): the trap-solid uniforms of CONTRACT4, until the real colour module has them
uniform float uTrapSolid, uTrapW; uniform int uTrapSkip;
// While an orbit runs: gNear = where it came nearest the trap (xyz, measured from the trap centre) and how near
// (w), gNearIt = at which step, and gTrap = its nearest approach to each coordinate plane and to the origin
// (the three-tone mix). c* are the captured copies.
vec4 gTrap, cTrap, gNear, cNear; float gNearIt, cNearIt, cIt; vec3 cLast;
// The plain distance from the orbit point v to the trap shape in use, wherever the trap has been moved to.
// Nothing is read but v and the trap's uniforms and nothing is written, so it may be called from anywhere.
// The three-tone mix has no shape of its own: it stands for the three coordinate planes through the origin.
float trapDist(vec3 v){
  if (uTrap == ${TRAP.tones}){ vec3 a = abs(v) + uTrapOff; return min(a.x, min(a.y, a.z)); }
  vec3 q = v - uTrapC;
  if (uTrap == ${TRAP.point}) return length(q);
  if (uTrap == ${TRAP.cross}){ vec3 s = q * q; return sqrt(min(s.x + s.y, min(s.y + s.z, s.z + s.x))); }
  if (uTrap == ${TRAP.line} || uTrap == ${TRAP.ray}){
    float a = dot(q, uTrapAx);
    return uTrap == ${TRAP.ray} && a < 0.0 ? length(q) : sqrt(max(dot(q, q) - a * a, 0.0));
  }
  if (uTrap == ${TRAP.planes}){ vec3 s = abs(q) + uTrapOff; return min(s.x, min(s.y, s.z)); }
  if (uTrap == ${TRAP.shell}) return abs(length(q) - uTrapR);
  return length(vec2(length(q.xy) - uTrapR, q.z));
}
void trapStart(){ gTrap = vec4(1e9); gNear = vec4(0.0, 0.0, 0.0, 1e9); gNearIt = 0.0; }
void trapAdd(vec3 v, float it){
  if (uColMode > 1) return;
  if (uTrap == ${TRAP.tones}){ gTrap = min(gTrap, vec4(abs(v), length(v))); return; }
  float d = trapDist(v);
  if (d < gNear.w){ gNear = vec4(v - uTrapC, d); gNearIt = it; }
}
void colourCapture(){ cTrap = gTrap; cNear = gNear; cNearIt = gNearIt; cIt = gIt; cLast = gLast; }
vec3 pal(float t){
  float n = float(uPalN), x = fract((t * uPalS + uPalO) * uPalF) * n;
  if (!(x >= 0.0 && x < n)) x = 0.0;   // also catches a value that is not a number
  int i = int(x), j = i + 1 == uPalN ? 0 : i + 1;
  float u = x - float(i);
  return mix(uPal[i], uPal[j], u * u * (3.0 - 2.0 * u));
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
// The colour for every mode that reads the palette (uColMode <= 5), from the captured values.
// depth is the distance from the camera, or negative in the flat picture, which has none.
vec3 colPick(vec3 p, float depth){
  // Escape count. On a surface nearly every point escapes in the last few steps or not at all, so there it is
  // counted back from the step limit: "never" always lands on the same bright part of the palette, whatever
  // the limit is set to. The flat picture counts forward from zero, so its colours stay put when the limit changes.
  float back = depth > 0.0 ? uColIter - cIt : -cIt;
  float t = (depth > 0.0 ? 0.8 : 0.0) - 0.25 * back;   // also stands in for depth in the flat picture
  if (uColMode <= 1){
    if (uTrap == ${TRAP.tones}){
      vec3 tone[4];
      for (int i = 0; i < 4; i++) tone[i] = pal(0.25 * float(i));
      vec3 a = mix(tone[0], tone[1], clamp(1.6 * cTrap.y, 0.0, 1.0));
      a = mix(a, tone[2], clamp(2.5 * cTrap.z * cTrap.z, 0.0, 1.0));
      // the fourth tone marks orbits that keep clear of the origin; it comes in gently and never takes over,
      // or everything outside the unit ball would be that one tone
      return mix(a, tone[3], 0.5 * smoothstep(0.0, 2.0, cTrap.w));
    }
    // A touch lands on the palette's last stop, so palettes that run dark to light are bright along the trap.
    // The square root spreads out the close calls, where the detail is. "Bands" keeps going through the
    // palette for as long as the distance grows; "glow" dies away instead, stopping just short of the first
    // stop, which in most palettes is too dark to show the shape of a solid. How narrow the glow is and how it
    // falls off depend on the trap (uGlowK, uGlowP: see setColourUniforms).
    float s = sqrt(min(cNear.w, 1e4)), band = 1.0 - 2.0 * s;
    t = uTrapBy == 1 ? 0.23 * cNearIt : uTrapBy == 2 ? band - 0.1 * back : uTrapBy == 3 ? colSide(cNear.xyz) : uTrapBy == 4 ? 0.15 + 0.85 * exp(-2.4 * pow(uGlowK * s, uGlowP)) : band;
  }
  else if (uColMode == 3) t = 0.45 * length(p);
  // by ratio, so the colours still change after zooming far in; at the usual viewing distance near is light
  else if (uColMode == 4 && depth > 0.0) t = 1.1 - 1.2 * log2(depth);
  else if (uColMode == 5) t = colDir(cLast);
  return pal(t);
}
vec3 surfaceColour(vec3 p, vec3 nor, float t){
  if (uColMode == 6){ vec3 a = 0.5 + 0.5 * nor; return a * a; }
  if (uColMode >= 7) return vec3(0.80, 0.78, 0.74);
  return colPick(p, max(t, 1e-6));
}
float colourUnlit(){ return uColMode == 6 ? 1.0 : 0.0; }
vec3 flatColour(vec3 p, float d, float px){
  colourCapture();
  // surface direction and plain clay have nothing to show off the solid: they leave a plain silhouette
  vec3 c = uColMode >= 6 ? uBg : colPick(p, -1.0);
  // Far from the set there is nothing left to show, and colour bands that go on repeating would shrink to a
  // moire once the view is zoomed far out: out there the colours fade into the stage. The 2D view's own range
  // (40 units from top to bottom at its farthest) ends before the fade begins.
  c = mix(c, uBg, smoothstep(40.0, 120.0, length(p.xy)));
  // The solid is drawn like the cut face of the 3D view, with a one-pixel outline in the hatching ink so that
  // it stays distinct from a palette that happens to end in the same colour.
  float e = gEsc * d / px;
  return mix(uCutCol, mix(uCutInk, c, clamp(e - 1.0, 0.0, 1.0)), clamp(e, 0.0, 1.0));
}`;

// The palette as the shader wants it: one closed loop of linear colours, and how many loops fit in a unit of t.
const palLoopCache = { key: '', n: 0, f: 1, data: new Float32Array(3 * PAL_MAX) };
function palLoop(i, rev) {
  const C = palLoopCache, key = i + (rev ? 'r' : 'f');
  if (C.key !== key) {
    let s = (PALETTES[i] || PALETTES[0]).slice(1, 10);
    const round = s.length > 2 && s[0] === s[s.length - 1];
    if (round) { s.pop(); if (rev) s = [s[0], ...s.slice(1).reverse()]; }
    else { s = s.slice(0, 8); if (rev) s.reverse(); s = s.concat(s.slice(1, -1).reverse()); }
    C.key = key; C.n = s.length; C.f = round ? 1 : 0.5;
    C.data.fill(0); C.data.set(s.flatMap(h => lin(hexRgb(h))));
  }
  return C;
}
// A CSS gradient of palette i, for a preview strip.
function paletteCss(i, rev) {
  let s = (PALETTES[i] || PALETTES[0]).slice(1);
  if (rev) s = s[0] === s[s.length - 1] ? [s[0], ...s.slice(1, -1).reverse(), s[0]] : s.slice().reverse();
  return `linear-gradient(90deg, ${s.join(', ')})`;
}
// Set this module's uniforms. L(name) returns the uniform location in the program in use.
function setColourUniforms(L) {
  const c = S.colour, k = S.k, P = palLoop(c.pal, c.rev), ax = [0, 0, 0], flatOrbits = colOrbitsFlat();
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
  gl.uniform3fv(L('uPal[0]'), P.data); gl.uniform1i(L('uPalN'), P.n); gl.uniform1f(L('uPalF'), P.f);
  gl.uniform1i(L('uTrap'), c.trap); gl.uniform1i(L('uTrapBy'), c.by); gl.uniform1f(L('uTrapR'), c.radius);
  gl.uniform3f(L('uTrapC'), c.tx, c.ty, c.tz); gl.uniform3fv(L('uTrapAx'), ax);
  // STAND-IN: S.colour.solid / thick / skip are set by tests; the 2D view never shows a trap solid
  gl.uniform1f(L('uTrapSolid'), S.flat ? 0 : (c.solid || 0)); gl.uniform1f(L('uTrapW'), c.thick === undefined ? 0.05 : c.thick); gl.uniform1i(L('uTrapSkip'), c.skip === undefined ? 1 : c.skip);
}
