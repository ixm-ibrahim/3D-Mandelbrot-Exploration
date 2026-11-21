// ---------- colour: palettes, orbit traps, and how a surface point or a 2D pixel is coloured.
// This module owns everything about colour: its controls (COLOUR_CONTROLS -> S.colour), its shader code
// (GL_COLOUR) and its uniforms (setColourUniforms). The renderer only calls the hooks named below.
const PALETTES = [
  ['Brass and verdigris', '#c98f33', '#2a8078', '#21386b', '#dbd1b8', '#c98f33'],
  ['Ember', '#2a1430', '#8c1c2c', '#e2622a', '#f6c453', '#fff1cf'],
  ['Glacier', '#0b2545', '#13607a', '#58b3c4', '#d9f0ef', '#8fb8d8'],
  ['Moss and rust', '#26381f', '#5a7a3c', '#b0bf68', '#ece3b2', '#9a5a2a'],
  ['Stone', '#4a4f57', '#858c96', '#bcc1c8', '#e9ebee', '#a39c90'],
];
// Control specs: rendered by buildControls() into the Colour section; values live in S.colour[key].
const COLOUR_CONTROLS = [
  { type: 'select', key: 'mode', label: 'Colour by', def: 0, options: [[0, 'Orbit trap, three tones'], [1, 'Orbit trap, nearest approach to the origin'], [2, 'Escape count'], [3, 'Distance from the centre'], [4, 'Depth from the camera'], [5, 'Direction of the last step'], [6, 'Surface direction'], [7, 'Plain clay']] },
  { type: 'select', key: 'pal', label: 'Palette', def: 0, options: PALETTES.map((p, i) => [i, p[0]]) },
  { type: 'dial', key: 'bands', label: 'Colour bands, how many', min: 0.1, max: 6, step: 0.01, def: 1, lo: 0.01, hi: 50 },
  { type: 'dial', key: 'shift', label: 'Colour bands, shift', min: 0, max: 2, step: 0.005, def: 0, lo: -50, hi: 50 },
];
// Shader hooks. The renderer includes GL_COLOUR after GL_HEAD, so it may use what GL_HEAD declares:
//   PI, at2(), cmul(), uBg, uCutCol, uCutInk (linear colours), and the orbit results gIt (smooth step count),
//   gLast (last orbit point) and gEsc (1 if the orbit escaped).
// The renderer calls, in this order:
//   trapStart()            once before each orbit
//   trapAdd(v, it)         after every orbit step, with the new point and the step number
//   colourCapture()        once, right after the ray has hit: copy whatever the colour needs out of the live globals,
//                          because later distance queries (slope, shadows, crevices) overwrite them
//   surfaceColour(p, nor, t)   the unlit colour of the hit: p position, nor unit normal, t distance from the camera
//   colourUnlit()          1.0 if that colour should be shown as it is, without lighting
//   flatColour(p, d, px)   2D view: the final colour of a slice pixel. Called right after the orbit, so the live
//                          globals are valid. d is the distance estimate (<= 0 inside), px the size of a pixel.
const GL_COLOUR = `
uniform int uColMode; uniform float uPalS, uPalO; uniform vec3 uPal[5];
vec4 gTrap, cTrap; float cIt; vec3 cLast;
void trapStart(){ gTrap = vec4(1e9); }
void trapAdd(vec3 v, float it){ gTrap = min(gTrap, vec4(abs(v), length(v))); }
void colourCapture(){ cTrap = gTrap; cIt = gIt; cLast = gLast; }
vec3 pal(float t){
  t = t * uPalS + uPalO;
  t = abs(fract(t * 0.5) * 2.0 - 1.0) * 4.0;
  int i = int(min(floor(t), 3.0));
  float u = t - float(i);
  return mix(uPal[i], uPal[i + 1], u * u * (3.0 - 2.0 * u));
}
vec3 surfaceColour(vec3 p, vec3 nor, float t){
  if (uColMode == 0){
    vec3 a = mix(pal(0.0), pal(0.25), clamp(1.6 * cTrap.y, 0.0, 1.0));
    a = mix(a, pal(0.5), clamp(2.5 * cTrap.z * cTrap.z, 0.0, 1.0));
    return mix(a, pal(0.75), 0.85 * clamp(pow(cTrap.w, 4.0), 0.0, 1.0));
  }
  if (uColMode == 1) return pal(cTrap.w * 0.6);
  if (uColMode == 2) return pal(cIt * 0.09);
  if (uColMode == 3) return pal(length(p) * 0.45);
  if (uColMode == 4) return pal(t * 0.18);
  if (uColMode == 5) return pal(at2(cLast.y, cLast.x) / (2.0 * PI) + 0.5 + 0.25 * cLast.z / max(length(cLast), 1e-20));
  if (uColMode == 6) { vec3 a = 0.5 + 0.5 * nor; return a * a; }
  return vec3(0.80, 0.78, 0.74);
}
float colourUnlit(){ return uColMode == 6 ? 1.0 : 0.0; }
vec3 flatColour(vec3 p, float d, float px){
  vec3 outside = mix(uBg, pal(gIt * 0.09), 0.85);
  return mix(uCutCol, outside, clamp(d / px, 0.0, 1.0) * gEsc);
}`;
// Set this module's uniforms. L(name) returns the uniform location in the program in use.
function setColourUniforms(L) {
  const c = S.colour;
  gl.uniform1i(L('uColMode'), c.mode); gl.uniform1f(L('uPalS'), c.bands); gl.uniform1f(L('uPalO'), c.shift);
  gl.uniform3fv(L('uPal[0]'), new Float32Array(PALETTES[c.pal].slice(1).flatMap(h => lin(hexRgb(h)))));
}
