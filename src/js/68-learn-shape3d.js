// Learn, "A whole shape": the 3D picture. One top-level name, learnShape3d. Nothing here runs at load time, and a
// view has a canvas and a WebGL2 context of its own.

// A point of the big ball (everything no further than 2 from the centre) takes steps of z -> z^n + c with the rule
// of the approach chosen in the lab, and is thrown out when it lands outside the ball. out(p) is the step at which
// that happens; shape k is every point with out(p) > k, and its skin is where out crosses k.
//
// Each pixel is one straight ray through the ball (no perspective), walked in even steps with out() worked out at
// each stop. Where two stops lie on different sides of a wanted skin, the crossing is narrowed by halving and the
// slope there is read from four points around it. The skins a ray meets are laid over each other nearest first,
// each with its opacity, and the stretch of the ray inside a shape adds a little of its colour.
//
// The compiler behind WebGL on Windows copies a function into every place that calls it (see 30-shaders.js), so
// main() is one loop around one call of lsOrb(), whose loop holds one call of the lab's f(): the walk, the halving
// and the four slope points are states of that one loop.
const learnShape3d = (() => {
  const BALL = 2;                 // radius of the big ball
  const HEAD = `#version 300 es
precision highp float;
precision highp int;
uniform vec4 uA;                 // the approach's dials, as the solid gets them
uniform float uPow, uJulia;      // the power; 1: Julia shape, 0: Mandelbrot shape
uniform vec3 uC, uAbs, uSgn;     // the Julia c; the modifiers
uniform vec4 uRect;              // the pane in buffer pixels: lower left corner, width, height
uniform vec3 uRt, uUp, uEye;     // the camera: screen right, screen up, the direction to the eye
uniform float uPxw, uEps, uFog;  // scene units per buffer pixel; how far apart the slope points sit; how strongly the inside is tinted
uniform vec4 uLook;              // how see-through a skin is: near side seen face on, near side at the rim, far side face on, far side at the rim
uniform float uRim, uGlow;       // how quickly a skin goes from its face-on look to its rim look; how much the lit part of a far side shows
uniform vec3 uLk, uLa;           // up to three skins, lowest step first: the step, the opacity (0: not drawn)
uniform vec3 uLs;                // how solid each of them is: 0 glass (uLook), 1 the solid look (uSolid)
uniform vec3 uSolid;             // the solid look: near side face on, near side at the rim, how much less the far side shows
uniform mat3 uLc;                // their colours, one per column
uniform vec3 uBg, uLight, uHalf, uSpec;
uniform vec2 uColGrid;           // for columns(): how far left of the centre the first point lies, the distance between two points
uniform int uN, uBis, uMaxK, uBudget, uColumns;   // uColumns: 0 the picture, 1 columns()
out vec4 o;
const float PI = 3.14159265358979;
const float LS_BALL = 2.0;
float gR;                        // set by lsOrb: how far from the centre the last point it looked at was
`;
  const TAIL = `
// The step at which the point p is thrown out: 0 when it starts outside the big ball, km + 1 when it is still in
// after km steps. With stop false the orbit is run to step km whatever happens on the way (the answer is then
// km + 1 and means nothing): that is how the slope of a skin is read, from gR at step km.
int lsOrb(vec3 p, int km, bool stop){
  bool jul = uJulia > 0.5;
  vec3 z = p;
#ifdef APR_ZMAP
  if (jul) z = zmap(p, uC);
#endif
  vec3 c = cmap(jul ? uC : p);
  float r = max(length(p), length(z));
  if (!jul){ z = start(c); r = length(p); }
#ifdef APR_CARRY
  carStart();
#endif
  int res = km + 1;
  // A Mandelbrot dot starts on its own point: the step that carries it there from the start value comes before the
  // count (k = -1) and nothing is asked of it. Step 1 is then the first that can throw a dot out, as for a Julia dot.
  for (int k = jul ? 0 : -1; k <= km; k++){
    if (k > 0) r = length(z);
    if (k >= 0){
      gR = r;
      if (stop && !(r <= LS_BALL)){ res = k; break; }
      if (k == km) break;
    }
    z = f(z, c);
  }
  return res;
}
float lsSel(vec3 v, int i){ return i == 0 ? v.x : i == 1 ? v.y : v.z; }
vec3 lsTet(int n){ return 0.57735 * (n == 0 ? vec3(1.0, -1.0, -1.0) : n == 1 ? vec3(-1.0, -1.0, 1.0) : n == 2 ? vec3(-1.0, 1.0, -1.0) : vec3(1.0)); }
void main(){
  bool column = uColumns > 0;
  vec2 q = (gl_FragCoord.xy - uRect.xy - 0.5 * uRect.zw) * uPxw;
  float q2 = dot(q, q), edge = LS_BALL + uPxw;
  if (!column && q2 >= edge * edge){ o = vec4(uBg, 1.0); return; }
  float h = sqrt(max(LS_BALL * LS_BALL - q2, 0.0));
  vec3 ro = q.x * uRt + q.y * uUp, rd = -uEye;
  if (column) ro = vec3((gl_FragCoord.xy - 0.5) * uColGrid.y - uColGrid.x, 0.0);
  // columns(): half the stretch of the upright line through this point that lies inside the ball
  float hc = column ? sqrt(max(LS_BALL * LS_BALL - dot(ro.xy, ro.xy), 0.0)) : 0.0;
  // the stops of the walk: evenly spaced on the stretch of the ray inside the ball, never further apart than 4 / uN
  int ns = max(int(ceil(0.5 * h * float(uN))), 1);
  float dt = 2.0 * h / float(ns);
  const float E0 = 4e-3;           // the walk begins and ends this far outside the ball, where out is 0
  vec3 col = vec3(0.0), g = vec3(0.0);
  float T = 1.0, tA = 0.0, tB = -h - E0, lo = 0.0, hi = 0.0, lk = 0.0;
  // st 0: the next stop of the walk. 1: halving towards the crossing of skin L between the stops A and B.
  // 2: the four slope points around that crossing.
  int st = 0, i = 0, oA = 0, oB = 0, L = 0, n = 0, jo = 0, sres = 0;
  for (int it = 0; it < uBudget; it++){
    float t = 0.5 * (lo + hi);
    int km = uMaxK;
    vec3 p;
    if (st == 0){ t = i < ns ? -h + (float(i) + 0.5) * dt : h + E0; p = ro + t * rd; }
    else if (st == 1){ p = ro + t * rd; km = int(lk); }
    else { p = ro + t * rd + uEps * lsTet(n); km = jo; }
    if (column){ p = ro; p.z = hc * (2.0 * (float(it) + 0.5) / float(uBudget) - 1.0); }
    int res = lsOrb(p, km, column || st != 2);
    if (column){ sres = max(sres, res); continue; }      // the highest number on the line: uBudget points of it, evenly spread
    bool seek = false;
    if (st == 0){
      tA = tB; oA = oB; tB = t; oB = res; i++;
      // tinted glass: the stretch just walked, for every shape this stop lies in
      vec3 w = step(uLk + 0.5, vec3(float(res))) * uLa * (uFog * dt);
      float ws = w.x + w.y + w.z;
      if (ws > 0.0){ float af = 1.0 - exp(-ws); col += T * af * (uLc * w) / ws; T *= 1.0 - af; }
      L = oA < oB ? -1 : 3; seek = true;
    } else if (st == 1){
      bool inA = float(oA) > lk, in1 = float(res) > lk;
      if (in1 == inA) lo = t; else hi = t;
      if (!in1) jo = res;
      n++;
      if (n >= uBis){ st = 2; n = 0; g = vec3(0.0); }
    } else {
      // The skin is where the orbit stands exactly on the big ball at step jo. gR is how far out it stands there for
      // this slope point, so the way gR grows is the way out of the shape. gR runs from 0 to 1e18 within a pixel once
      // the steps are many, so the slope is read from the logarithm of its logarithm, which grows by about one for
      // each step a point is thrown out earlier. A NaN counts as far outside.
      float V = clamp(log2(log(clamp(gR < 1e30 ? gR : 1e30, 1.0001, 1e30)) / log(LS_BALL)), -1.0, 6.5);
      g += lsTet(n) * V;
      n++;
      if (n >= 4){
        float g2 = dot(g, g);
        vec3 nr = g2 > 0.0 ? g * inversesqrt(g2) : uEye;
        float ne = dot(nr, uEye), nv = abs(ne);
        vec3 nf = ne < 0.0 ? -nr : nr;       // the side of the skin that faces the eye
        bool front = float(oA) <= lk;        // the ray is going in: the near side of a body
        float fr = pow(1.0 - nv, uRim);
        float a = lsSel(uLa, L), so = lsSel(uLs, L), dif = max(dot(nf, uLight), 0.0), sp = pow(max(dot(nf, uHalf), 0.0), 60.0);
        vec3 base = L == 0 ? uLc[0] : L == 1 ? uLc[1] : uLc[2], c;
        float al;
        if (front){ c = base * (0.34 + 0.8 * dif) + (0.9 * sp) * uSpec; al = a * mix(mix(uLook.x, uSolid.x, so), mix(uLook.y, uSolid.y, so), fr) + a * 0.5 * sp; }
        else { c = base * (0.3 + 0.9 * dif) + (0.25 * sp) * uSpec; al = a * (1.0 - uSolid.z * so) * (mix(uLook.z, uLook.w, fr) + uGlow * dif * dif); }
        al = min(al, 1.0);
        col += T * al * c; T *= 1.0 - al;
        seek = true;
      }
    }
    if (seek){
      // the next skin crossed between the stops A and B, in the order the ray meets them
      float fa = float(oA), fb = float(oB);
      bool c0 = uLa.x > 0.0 && (fa > uLk.x) != (fb > uLk.x), c1 = uLa.y > 0.0 && (fa > uLk.y) != (fb > uLk.y), c2 = uLa.z > 0.0 && (fa > uLk.z) != (fb > uLk.z);
      int nx = oA < oB ? (L < 0 && c0 ? 0 : L < 1 && c1 ? 1 : L < 2 && c2 ? 2 : -1) : (L > 2 && c2 ? 2 : L > 1 && c1 ? 1 : L > 0 && c0 ? 0 : -1);
      if (nx >= 0){
        L = nx; lk = lsSel(uLk, L); lo = tA; hi = tB; n = 0;
        jo = fa > lk ? oB : oA;
        st = uBis > 0 ? 1 : 2;
        if (st == 2) g = vec3(0.0);
      } else {
        st = 0;
        if (i > ns || T < 0.02) break;
      }
    }
  }
  if (column){ o = vec4(float(min(sres, 255)) / 255.0, 0.0, 0.0, 1.0); return; }
  col += T * uBg;
  float cov = clamp((LS_BALL - sqrt(q2)) / uPxw + 0.5, 0.0, 1.0);
  float di = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) - 0.5;
  o = vec4(mix(uBg, col, cov) + di / 255.0, 1.0);
}`;

  let noteText = '';
  const LOST = 'The graphics of this page were interrupted. The 3D picture comes back by itself.';
  const NOGL = 'This device cannot draw the 3D picture.';
  const failWords = a => `The 3D picture could not be prepared for “${a.name}” on this device.`;

  // The rule in JavaScript (MATH and CARRY), for one point
  const fin = (x, d) => (isFinite(+x) ? +x : d);
  // what the approach's own cmap and zmap do in the shader (see the approaches' GLSL in 10-approaches.js)
  function cmapJs(id, c, q, jul) {
    if (id === 'fold') return foldk(c, Math.max(2, q.planes || 2));
    if (id === 'softmirror') return smFold(c, q);
    if (id === 'mirrorsdouble') return smFoldK(c, 1, smDial(q, 'soft', 2, 0, 45));
    if (id === 'mirrorsblend') return smFoldK(c, 1, 0);
    if (id === 'quat4') {
      const k = jul ? [c[0], c[1], c[2], fin(q.cw, 0)] : q4Embed(c, q);
      if (k[3] === 0) return [k[0], k[1], k[2]];
      const l = Math.hypot(k[1], k[2]), d = l > 1e-12 ? [k[1] / l, k[2] / l] : [1, 0], m = Math.hypot(k[1], k[2], k[3]);
      return [k[0], m * d[0], m * d[1]];
    }
    return c;
  }
  function zmapJs(id, P, c, q) {
    if (id !== 'quat4') return P;
    const E = q4Embed(P, q), k = [c[0], c[1], c[2], fin(q.cw, 0)];
    if (k[3] === 0 && fin(q.w, 0) === 0 && fin(q.tilt, 0) === 0) return [E[0], E[1], E[2]];
    const m = Math.hypot(k[1], k[2], k[3]), u = m > 1e-12 ? [k[1] / m, k[2] / m, k[3] / m] : [1, 0, 0];
    const l = Math.hypot(k[1], k[2]), d = l > 1e-12 ? [k[1] / l, k[2] / l] : [1, 0];
    const b = E[1] * u[0] + E[2] * u[1] + E[3] * u[2], mu = Math.hypot(E[1] - b * u[0], E[2] - b * u[1], E[3] - b * u[2]);
    return [E[0], b * d[0] - mu * d[1], b * d[1] + mu * d[0]];
  }
  // The step at which p is thrown out: 0 when it starts outside the big ball, maxK + 1 when it is still in after
  // maxK steps. The approach, its dials, the power and the modifiers are the lab's (ap(), S.param, S.n, S.abs, S.flip).
  function out(p, kind, c, maxK) {
    const a = ap(), id = a.id, q = S.param[id] || {}, n = S.n, jul = kind === 'j', ab = S.abs, fl = S.flip;
    if (!(Math.hypot(p[0], p[1], p[2]) <= BALL)) return 0;
    let z = [0, 0, 0], cc;
    if (jul) {
      z = zmapJs(id, p, c, q); cc = cmapJs(id, c, q, true);
      if (!(Math.hypot(z[0], z[1], z[2]) <= BALL)) return 0;
    } else cc = cmapJs(id, p, q, false);
    const car = CARRY[id] || null;
    let st = car ? car.start(q) : null;
    for (let k = jul ? 1 : 0; k <= maxK; k++) {      // k = 0: a Mandelbrot dot's step to its own point, of which nothing is asked
      const v = [ab[0] ? Math.abs(z[0]) : z[0], (ab[1] ? Math.abs(z[1]) : z[1]) * (fl[0] ? -1 : 1), (ab[2] ? Math.abs(z[2]) : z[2]) * (fl[1] ? -1 : 1)];
      let w;
      if (car) { st = car.step(st, v, cc, q); w = car.pw(st, v, n); } else w = MATH[id](v, n, q, cc);
      z = [w[0] + cc[0], w[1] + cc[1], w[2] + cc[2]];
      if (k && !(Math.hypot(z[0], z[1], z[2]) <= BALL)) return k;
    }
    return maxK + 1;
  }

  // The same orbit with its places kept, in the arithmetic of out(). It returns { out, pts, c, carry }:
  //   out     what out() answers
  //   pts[j]  where the dot is after j steps, for j = 0 .. min(out, maxK): when the dot is thrown out, the last
  //           place is the one that lies outside the big ball. Empty when the picture's point itself lies outside.
  //   c       the number that is added at every step (what the approach's own cmap makes of the picture's c)
  //   carry   for an entry whose orbit carries something (CARRY): carry[j] is what it carries when step j + 1
  //           begins; null for every other entry
  function orbit(p, kind, c, maxK) {
    const a = ap(), id = a.id, q = S.param[id] || {}, n = S.n, jul = kind === 'j', ab = S.abs, fl = S.flip;
    const res = { out: 0, pts: [], c: [0, 0, 0], carry: null };
    if (!(Math.hypot(p[0], p[1], p[2]) <= BALL)) return res;
    let z = [0, 0, 0], cc;
    if (jul) { z = zmapJs(id, p, c, q); cc = cmapJs(id, c, q, true); } else cc = cmapJs(id, p, q, false);
    res.c = [cc[0], cc[1], cc[2]];
    const car = CARRY[id] || null;
    let st = car ? car.start(q) : null;
    // a Mandelbrot dot's pts[0] is its own point, where the uncounted first step lands it
    if (jul) res.pts.push([z[0], z[1], z[2]]);
    if (car) res.carry = jul ? [st] : [];
    if (jul && !(Math.hypot(z[0], z[1], z[2]) <= BALL)) return res;
    for (let k = jul ? 1 : 0; k <= maxK; k++) {      // k = 0: a Mandelbrot dot's step to its own point, of which nothing is asked
      const v = [ab[0] ? Math.abs(z[0]) : z[0], (ab[1] ? Math.abs(z[1]) : z[1]) * (fl[0] ? -1 : 1), (ab[2] ? Math.abs(z[2]) : z[2]) * (fl[1] ? -1 : 1)];
      let w;
      if (car) { st = car.step(st, v, cc, q); w = car.pw(st, v, n); } else w = MATH[id](v, n, q, cc);
      z = [w[0] + cc[0], w[1] + cc[1], w[2] + cc[2]];
      res.pts.push(z);
      if (car) res.carry.push(st);
      if (k && !(Math.hypot(z[0], z[1], z[2]) <= BALL)) { res.out = k; return res; }
    }
    res.out = maxK + 1;
    return res;
  }

  // The camera, shared with whoever draws on top of the picture: yaw about the upright z-axis, pitch above the flat
  // plane, as LEARN_V_VIEWS.s3 means them (learnVProj).
  function basis(yaw, pitch) {
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    return { R: [cy, sy, 0], U: [-sy * sp, cy * sp, cp], D: [sy * cp, -cy * cp, sp] };
  }
  const viewOf = o => ({ yaw: fin(o && o.yaw, -0.62), pitch: fin(o && o.pitch, 0.4), zoom: Math.max(fin(o && o.zoom, 1), 0.05) });
  // Where a point of space lands in a pane: rect in CSS pixels inside the canvas. s: pixels per unit.
  // to(v) -> [x, y, depth], depth growing towards the eye.
  function proj(o, rect) {
    const V = viewOf(o), B = basis(V.yaw, V.pitch), s = 0.2 * Math.min(rect[2], rect[3]) * V.zoom;
    const cx = rect[0] + rect[2] / 2, cy = rect[1] + rect[3] / 2, d3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    return { s, R: B.R, U: B.U, D: B.D, to: v => [cx + d3(v, B.R) * s, cy - d3(v, B.U) * s, d3(v, B.D)] };
  }

  // The program text for one approach. The rule is the lab's own text: the approach's GLSL, cmul and at2 cut out of
  // GL_HEAD, f() and start() cut out of GL_ORBIT (the modifiers and the carry hook with them), and the plain equation
  // z^n + c compiled by compileFormula. Those lines of 30-shaders.js have to keep the shape the searches here expect.
  // One program serves both kinds: uJulia says which, pane by pane.
  function sourceFor(a, n2) {
    const pick = (text, re) => re.exec(text)[0];
    const help = pick(GL_HEAD, /vec2 cmul\([^\n]*\n/) + pick(GL_HEAD, /float at2\([^\n]*\n/);
    const step = pick(GL_ORBIT, /#ifdef APR_CARRY\nvec3 f\([^\n]*\n#else\nvec3 f\([^\n]*\n#endif\nvec3 start\([^\n]*\n/);
    const fc = compileFormula('z^n + c', true, n2), zc = compileFormula('0', false, n2);
    return HEAD + help + a.glsl + '\n' + step.split('__F__').join(fc).split('__Z0__').join(zc) + TAIL;
  }

  // How fine a picture is. n: stops across the whole ball. bis: halvings of a crossing. cross: skins a ray may meet
  // before it stops. res: buffer pixels per CSS pixel. cap: the most pixels a buffer may have.
  // 'still' starts at its first entry (four buffer pixels for each pixel of an ordinary screen, so edges come out
  // smooth), 'move' at its second. Both go finer or coarser by what the graphics card reports (see learnt).
  const QUAL = {
    still: [{ n: 320, bis: 7, cross: 20, res: 2, cap: 3.6e6 }, { n: 256, bis: 6, cross: 16, res: 1.5, cap: 2.4e6 }, { n: 224, bis: 6, cross: 12, res: 1, cap: 1.6e6 }],
    move: [{ n: 160, bis: 5, cross: 12, res: 1, cap: 1.2e6 }, { n: 128, bis: 4, cross: 10, res: 0.75, cap: 0.8e6 }, { n: 96, bis: 4, cross: 10, res: 0.5, cap: 0.4e6 },
      { n: 80, bis: 3, cross: 8, res: 0.4, cap: 0.25e6 }, { n: 64, bis: 3, cross: 7, res: 0.33, cap: 0.16e6 }, { n: 48, bis: 2, cross: 6, res: 0.25, cap: 0.1e6 }],
  };
  // How see-through a skin is. front, back: the opacity of the near and of the far side of a body, [seen face on, at
  // the rim]. rim: how quickly a skin goes from the one to the other. fog: how strongly the inside of a body is
  // tinted, per unit of length. glow: how much more of a far side shows where the light falls on it from inside;
  // that bright patch makes a plain ball read as glass.
  const LOOK = { front: [0.13, 0.92], back: [0.12, 0.52], rim: 2.8, fog: 0.04, glow: 0.55 };
  // What a level's `solid` = 1 makes of its skin: its near side this opaque [face on, at the rim], and its far side
  // and the glow there showing by `hide` less. For bodies with many fine folds, which as glass are a tangle of sheets
  // seen through one another.
  const SOLID = { front: [0.6, 0.95], hide: 0.6 };

  function make() {
    const canvas = document.createElement('canvas');
    canvas.className = 'learn-shape3d';
    let gl = null;
    try { gl = canvas.getContext('webgl2', { antialias: false, alpha: false, depth: false, stencil: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' }); } catch (err) { gl = null; }
    if (!gl) { noteText = NOGL; return null; }
    const progs = new Map();      // by approach and kind of formula, least recently used first
    let tq = null, pend = null, fbo = null, last = null, frames = 0;
    let ref = null;                      // the last frame the card has timed: its time, its work (buffer pixels times stops), its zoom and scene
    const lod = { move: 1, still: 0 };   // which entry of QUAL each quality stands at
    const gpuMs = { move: 0, still: 0 };
    const setup = () => { tq = gl.getExtension('EXT_disjoint_timer_query_webgl2'); pend = null; fbo = null; progs.clear(); };
    setup();

    function program(a, n2) {
      const key = a.id + (n2 ? '|2' : '|n');
      let e = progs.get(key);
      if (e) { progs.delete(key); progs.set(key, e); return e; }
      e = { ok: false, p: null, log: '', loc: {} };
      try {
        const p = gl.createProgram(), vs = gl.createShader(gl.VERTEX_SHADER), fs = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(vs, VERT); gl.compileShader(vs);
        gl.shaderSource(fs, sourceFor(a, n2)); gl.compileShader(fs);
        gl.attachShader(p, vs); gl.attachShader(p, fs); gl.linkProgram(p);
        e.ok = !!gl.getProgramParameter(p, gl.LINK_STATUS);
        if (!e.ok) e.log = [gl.getShaderInfoLog(fs), gl.getShaderInfoLog(vs), gl.getProgramInfoLog(p)].filter(Boolean).join('\n') || 'link failed';
        gl.deleteShader(vs); gl.deleteShader(fs);
        if (e.ok) e.p = p; else gl.deleteProgram(p);
      } catch (err) { e.ok = false; e.log = String(err && err.message || err); }
      if (!e.ok && !gl.isContextLost()) console.error('learnShape3d: the program for ' + key + ' did not build: ' + e.log);
      if (!gl.isContextLost()) progs.set(key, e);
      for (const [k, old] of progs) { if (progs.size <= 8) break; if (old.p) gl.deleteProgram(old.p); progs.delete(k); }
      return e;
    }
    const U = (e, name) => (name in e.loc ? e.loc[name] : (e.loc[name] = gl.getUniformLocation(e.p, name)));
    // the uniforms the rule reads: the lab's state, as 40-render.js hands it to the solid
    function ruleUniforms(e, c) {
      gl.uniform4fv(U(e, 'uA'), apVec()); gl.uniform1f(U(e, 'uPow'), S.n);
      gl.uniform3fv(U(e, 'uAbs'), S.abs); gl.uniform3f(U(e, 'uSgn'), 1, S.flip[0] ? -1 : 1, S.flip[1] ? -1 : 1);
      gl.uniform3f(U(e, 'uC'), fin(c && c[0], 0), fin(c && c[1], 0), fin(c && c[2], 0));
    }
    function current() {
      const a = ap(), e = program(a, Math.abs(S.n - 2) < 1e-9);
      noteText = e.ok ? '' : failWords(a);
      return e;
    }
    // What a frame cost, as the graphics card (or, failing that, a wait for it) reports. A 'move' frame that takes
    // too long makes the next ones coarser, a quick one finer again. 'still' gets coarser only when a frame takes far
    // too long, and finer once a frame is quick: one step finer costs two to three times as much, so a frame under
    // 45 ms stays under the 160 that sent it down.
    function learnt(quality, at, ms, job) {
      gpuMs[quality] = ms;
      if (job && job.work > 0) ref = { ms, work: job.work, zoom: job.zoom, key: job.key };
      if (at !== lod[quality]) return;
      if (quality === 'move') { if (ms > 40 && lod.move < QUAL.move.length - 1) lod.move++; else if (ms < 9 && lod.move > 0) lod.move--; }
      else if (ms > 160 && lod.still < QUAL.still.length - 1) lod.still++;
      else if (ms < 45 && lod.still > 0) lod.still--;
    }
    function pollTimer() {
      if (!pend || !tq) return;
      if (!gl.getQueryParameter(pend.q, gl.QUERY_RESULT_AVAILABLE)) return;
      const bad = gl.getParameter(tq.GPU_DISJOINT_EXT), ns = gl.getQueryParameter(pend.q, gl.QUERY_RESULT);
      gl.deleteQuery(pend.q);
      if (!bad) learnt(pend.quality, pend.lod, ns / 1e6, pend);
      pend = null;
    }

    function draw(o) {
      o = o || {};
      last = o;
      const t0 = performance.now(), quality = o.quality === 'move' ? 'move' : 'still';
      if (gl.isContextLost()) return { ok: false, note: LOST };
      pollTimer();
      let at = lod[quality];
      const panes = (o.panes || []).filter(p => p && p.rect && p.rect[2] > 0 && p.rect[3] > 0).slice(0, 2);
      // fit the buffer to the box the page gives the canvas
      const cw = canvas.clientWidth || Math.max(0, ...panes.map(p => p.rect[0] + p.rect[2])) || 300;
      const ch = canvas.clientHeight || Math.max(0, ...panes.map(p => p.rect[1] + p.rect[3])) || 150;
      // a sharp screen already has the pixels 'still' would add; 'move' takes half of what such a screen offers
      const dpr = clamp(window.devicePixelRatio || 1, 1, 3), V = viewOf(o);
      // the buffer and the stops that one entry of QUAL means for this box and this zoom
      const fit = q => {
        let sc = quality === 'move' ? q.res * Math.min(dpr, 1.5) : Math.max(q.res, Math.min(dpr, 2));
        sc *= Math.min(1, Math.sqrt(q.cap / (cw * ch * sc * sc)));
        return { bw: Math.max(2, Math.round(cw * sc)), bh: Math.max(2, Math.round(ch * sc)), n: Math.round(q.n * clamp(Math.sqrt(V.zoom), 1, 2)) };
      };
      // The card's time goes with buffer pixels times stops, so what the last timed frame of the same scene cost says
      // what a 'still' one would. One that would hold the page up for more than about an eighth of a second is drawn
      // coarser from the start. Zoomed further in than that frame, more of the picture is shape: counted as the
      // square of how much further.
      const key = ap().id + '|' + panes.map(p => p.kind).join('');
      if (quality === 'still' && ref && ref.key === key && Math.abs(Math.log(V.zoom / ref.zoom)) < 0.5) {
        const grown = Math.max(1, V.zoom / ref.zoom);
        for (; at < QUAL.still.length - 1; at++) { const f = fit(QUAL.still[at]); if (0.9 * ref.ms * grown * grown * f.bw * f.bh * f.n / ref.work <= 130) break; }
      }
      const Q = QUAL[quality][at], F = fit(Q), bw = F.bw, bh = F.bh;
      if (canvas.width !== bw || canvas.height !== bh) { canvas.width = bw; canvas.height = bh; }
      const col = o.colours || {}, bg = col.bg || [0.08, 0.08, 0.09], body = col.body || [0.79, 0.64, 0.36], warn = col.warn || [0.9, 0.45, 0.2], ink = col.ink || [0.9, 0.9, 0.9];
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND); gl.disable(gl.DEPTH_TEST);
      gl.viewport(0, 0, bw, bh);
      gl.clearColor(bg[0], bg[1], bg[2], 1); gl.clear(gl.COLOR_BUFFER_BIT);
      const e = current();
      if (!e.ok) return { ok: false, note: noteText };
      // the skins of a pane, lowest step first (of more than three, the three drawn most strongly)
      const skins = levels => {
        const lv = (levels || []).filter(l => l && isFinite(+l.k) && +l.alpha > 0.003)
          .map(l => ({ k: clamp(Math.round(+l.k), 0, 250), a: clamp(+l.alpha, 0, 1), t: clamp(fin(l.tint, 0), 0, 1), g: clamp(fin(l.ghost, 0), 0, 1), s: clamp(fin(l.solid, 0), 0, 1) }))
          .sort((x, y) => y.a - x.a).slice(0, 3).sort((x, y) => x.k - y.k);
        const lk = [1e4, 1e4, 1e4], la = [0, 0, 0], ls = [0, 0, 0], lc = new Float32Array(9);
        lv.forEach((l, i) => {
          lk[i] = l.k; la[i] = l.a; ls[i] = l.s;
          // from the body colour towards the warning colour by the tint, then towards the ink by `ghost`
          for (let j = 0; j < 3; j++) { const b = body[j] + (warn[j] - body[j]) * l.t; lc[3 * i + j] = b + (ink[j] - b) * l.g; }
        });
        return { lv, lk, la, ls, lc };
      };
      const per = panes.map(p => skins(p.levels));
      if (!panes.length || per.every(sk => !sk.lv.length)) return { ok: true, note: '' };
      const B = basis(V.yaw, V.pitch);
      // the light stays where it is for the viewer (from the upper left, in front), so a turned shape is lit the same way
      const mixv = (a, b, c) => { const v = [0, 1, 2].map(j => a * B.R[j] + b * B.U[j] + c * B.D[j]), l = Math.hypot(v[0], v[1], v[2]); return v.map(x => x / l); };
      const light = mixv(-0.46, 0.62, 0.64), half = mixv(-0.46, 0.62, 1.64);
      const lum = 0.3 * bg[0] + 0.59 * bg[1] + 0.11 * bg[2];
      gl.useProgram(e.p);
      ruleUniforms(e, o.c);
      gl.uniform3fv(U(e, 'uRt'), B.R); gl.uniform3fv(U(e, 'uUp'), B.U); gl.uniform3fv(U(e, 'uEye'), B.D);
      gl.uniform3fv(U(e, 'uBg'), bg); gl.uniform3fv(U(e, 'uLight'), light); gl.uniform3fv(U(e, 'uHalf'), half);
      gl.uniform3f(U(e, 'uSpec'), 1, 1, lum > 0.5 ? 1 : 0.94);
      gl.uniform4f(U(e, 'uLook'), LOOK.front[0], LOOK.front[1], LOOK.back[0], LOOK.back[1]);
      gl.uniform1f(U(e, 'uRim'), LOOK.rim); gl.uniform1f(U(e, 'uFog'), LOOK.fog); gl.uniform1f(U(e, 'uGlow'), LOOK.glow);
      gl.uniform3f(U(e, 'uSolid'), SOLID.front[0], SOLID.front[1], SOLID.hide);
      // what one pane's skins hand to the program
      const wear = sk => {
        gl.uniform3fv(U(e, 'uLk'), sk.lk); gl.uniform3fv(U(e, 'uLa'), sk.la); gl.uniform3fv(U(e, 'uLs'), sk.ls); gl.uniformMatrix3fv(U(e, 'uLc'), false, sk.lc);
        gl.uniform1i(U(e, 'uMaxK'), sk.lv[sk.lv.length - 1].k);
      };
      const n = F.n, job = { work: bw * bh * n, zoom: V.zoom, key };
      gl.uniform1i(U(e, 'uN'), n); gl.uniform1i(U(e, 'uBis'), Q.bis);
      gl.uniform1i(U(e, 'uBudget'), n + 3 + Q.cross * (Q.bis + 4)); gl.uniform1i(U(e, 'uColumns'), 0);
      const timed = tq && !pend ? gl.createQuery() : null;
      if (timed) gl.beginQuery(tq.TIME_ELAPSED_EXT, timed);
      gl.enable(gl.SCISSOR_TEST);
      const sx = bw / cw, sy = bh / ch;
      for (let pi = 0; pi < panes.length; pi++) {
        const pane = panes[pi];
        if (!per[pi].lv.length) continue;      // no skin for this pane: it keeps the stage colour
        wear(per[pi]);
        const r = pane.rect, x0 = Math.round(r[0] * sx), x1 = Math.round((r[0] + r[2]) * sx), y1 = bh - Math.round(r[1] * sy), y0 = bh - Math.round((r[1] + r[3]) * sy);
        const w = x1 - x0, h = y1 - y0;
        if (w < 1 || h < 1) continue;
        const pxw = 1 / (0.2 * Math.min(w, h) * V.zoom);   // scene units per buffer pixel
        gl.viewport(x0, y0, w, h); gl.scissor(x0, y0, w, h);
        gl.uniform4f(U(e, 'uRect'), x0, y0, w, h);
        // the slope is read over three quarters of a CSS pixel, whatever the buffer: finer than that only glitters
        gl.uniform1f(U(e, 'uPxw'), pxw); gl.uniform1f(U(e, 'uEps'), Math.max(0.75 * pxw * Math.max(sx, sy), 5e-4));
        gl.uniform1f(U(e, 'uJulia'), pane.kind === 'j' ? 1 : 0);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }
      gl.disable(gl.SCISSOR_TEST);
      if (timed) { gl.endQuery(tq.TIME_ELAPSED_EXT); pend = Object.assign({ q: timed, quality, lod: at }, job); }
      frames++;
      // a browser that does not time its graphics card: now and then wait for one frame and take that time
      if (!tq && (frames % 24 === 1 || !gpuMs[quality])) {
        const px = new Uint8Array(4);
        gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        learnt(quality, at, performance.now() - t0, job);
      }
      return { ok: true, note: '' };
    }

    // For the page's words: the shape seen from straight above, worked out by the program the picture uses. Each
    // point of the square |x|, |y| <= half stands for the upright line through it, and the answer is the latest step
    // at which a point on the part of that line inside the big ball is thrown out: above k means that something of
    // shape k stands on this line. size points to a side, the outer ones on the edge of the square; row 0 is the
    // top, y = +half. opt.stops points of each line are asked, evenly spread. null when the program did not build.
    function columns(kind, c, opt) {
      const stops = clamp(Math.round(fin(opt.stops, 192)), 1, 1024);
      const size = clamp(Math.round(fin(opt.size, 256)), 2, 2048), half = fin(opt.half, BALL), maxK = clamp(Math.round(fin(opt.maxK, 16)), 0, 254);
      if (gl.isContextLost()) return null;
      const e = current();
      if (!e.ok) return null;
      if (!fbo || fbo.size !== size) {
        if (fbo) { gl.deleteTexture(fbo.tex); gl.deleteFramebuffer(fbo.fb); }
        const tex = gl.createTexture(), fb = gl.createFramebuffer();
        gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, size, size, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
        fbo = { tex, fb, size };
      }
      gl.bindFramebuffer(gl.FRAMEBUFFER, fbo.fb);
      gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
      gl.viewport(0, 0, size, size);
      gl.useProgram(e.p);
      ruleUniforms(e, c);
      gl.uniform2f(U(e, 'uColGrid'), half, 2 * half / (size - 1));
      gl.uniform1f(U(e, 'uJulia'), kind === 'j' ? 1 : 0);
      gl.uniform1i(U(e, 'uMaxK'), maxK); gl.uniform1i(U(e, 'uBudget'), stops); gl.uniform1i(U(e, 'uColumns'), 1);
      gl.uniform1i(U(e, 'uN'), 1); gl.uniform1i(U(e, 'uBis'), 0); gl.uniform1f(U(e, 'uPxw'), 1); gl.uniform4f(U(e, 'uRect'), 0, 0, size, size);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      const px = new Uint8Array(size * size * 4), res = new Uint8Array(size * size);
      gl.readPixels(0, 0, size, size, gl.RGBA, gl.UNSIGNED_BYTE, px);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      for (let row = 0; row < size; row++) for (let x = 0; x < size; x++) res[row * size + x] = px[((size - 1 - row) * size + x) * 4];
      return res;
    }
    canvas.addEventListener('webglcontextlost', ev => { ev.preventDefault(); });
    canvas.addEventListener('webglcontextrestored', () => { setup(); if (last) draw(last); });
    return { canvas, draw, columns };
  }

  return { make, out, orbit, note: () => noteText, proj };
})();
