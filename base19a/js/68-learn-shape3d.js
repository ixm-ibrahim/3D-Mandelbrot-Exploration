// ---------- Learn, "A whole shape": the see-through 3D picture (round 26, builder "three").
// One top-level name, learnShape3d. Nothing here runs at load time and nothing touches the lab's own canvas: a view
// has a canvas and a WebGL2 context of its own. The contract is in docs/ROUND26.md, section 4.
//
// The game: a point of the big ball (everything no further than 2 from the centre) takes steps of z -> z^n + c with
// the rule of the approach chosen in the lab. A point that lands outside the ball is thrown out. out(p) is the step
// at which that happens; shape k is every point with out(p) > k, and its skin is where out crosses k.
//
// How a picture is made. Each pixel is one straight ray through the ball (the camera is flat, without perspective,
// like the Learn tab's own space view). The ray is walked in even steps and out() is worked out at each stop. Where
// two stops lie on different sides of a wanted skin, the crossing is narrowed by halving, and the slope there is
// read from four points around it. The skins a ray meets are laid over each other nearest first, each with its
// opacity, and the stretch of the ray that runs inside a shape adds a little of its colour (tinted glass).
// A skin lets most of the light through where it faces the eye and little at its rim; the near side of a body
// carries the highlight, and its far side shows brightest where the light falls on it from inside.
//
// Beyond the contract (all optional, none needed by a caller that keeps to the contract):
//   learnShape3d.proj(o, rect)   where a point of space lands in a pane: { s, cx, cy, R, U, D, to(v) -> [x, y, depth] }
//   a level's `ghost` (0..1)     pushes that skin's colour from the body colour towards colours.ink
//   a pane's `levels`            skins for that pane alone, in place of o.levels (in "Both" the first step takes
//                                nothing from the Mandelbrot shape and a bite from the Julia shape: the two differ)
//   view.columns(kind, c, opt)   for the page's words: the shape seen from straight above, without glass (see there)
//   o.flat                       the cut at z = 0 of the shape drawn most strongly, a shade lighter, inside the glass
//   a level's `solid` (0..1)     that skin's near side more solid and its far side fainter, for bodies with many
//                                fine folds (see SOLID); o.solid is the same for every level that has none of its own
//   o.look, o.lod, o.res         for trying things out and for timings (see LOOK and QUAL below)
//   view.slicePoint(row, col, opt), view.time(o, reps), view.stats(), learnShape3d.source(approach, n2)
//
// Building speed (see the header of 30-shaders.js): the compiler behind WebGL on Windows copies a function into
// every place that calls it. So main() is one loop around ONE call of lsOrb(), whose loop holds ONE call of the
// lab's f(): the walk, the halving and the four slope points are states of that one loop, not loops of their own.
// The rule is the lab's own text: the approach's GLSL as it stands, f() and start() cut out of GL_ORBIT (the
// modifiers and the carry hook with them), with the plain equation z^n + c compiled by compileFormula as the solid's
// is. One program serves both kinds: uJulia says which, pane by pane.
const learnShape3d = (() => {
  const BALL = 2;                 // the big ball
  // What the lab's shader head and orbit code are asked for. The fallbacks are today's text, used only if a later
  // edit of 30-shaders.js moves these lines out of reach of the search.
  const FALL_HELP = 'vec2 cmul(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }\n'
    + 'float at2(float y, float x){ return abs(x) + abs(y) > 0.0 ? atan(y, x) : 0.0; }\n';
  const FALL_STEP = '#ifdef APR_CARRY\nvec3 f(vec3 z, vec3 c){ z = mix(z, abs(z), uAbs) * uSgn; carStep(z, c); return __F__; }\n'
    + '#else\nvec3 f(vec3 z, vec3 c){ z = mix(z, abs(z), uAbs) * uSgn; return __F__; }\n#endif\nvec3 start(vec3 c){ return __Z0__; }\n';
  const FALL_VERT = '#version 300 es\nvoid main(){\n  vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2));\n  gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);\n}';
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
uniform vec3 uFlat, uFc;         // the cut at z = 0: (the step of the shape that is cut, the opacity or 0 for no cut, unused); its colour
uniform vec3 uLk, uLa;           // up to three skins, lowest step first: the step, the opacity (0: not drawn)
uniform vec3 uLs;                // how solid each of them is: 0 glass (uLook), 1 the solid look (uSolid)
uniform vec3 uSolid;             // the solid look: near side face on, near side at the rim, how much less the far side shows
uniform mat3 uLc;                // their colours, one per column
uniform vec3 uBg, uLight, uHalf, uSpec;
uniform vec3 uSl;                // for slice(): the height z, how far left of the centre the first point lies, the distance between two points
uniform int uN, uBis, uMaxK, uBudget, uSlice;   // uSlice: 0 the picture, 1 slice(), 2 columns()
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
  for (int k = 0; k <= km; k++){
    if (k > 0) r = length(z);
    gR = r;
    if (stop && !(r <= LS_BALL)){ res = k; break; }
    if (k == km) break;
    z = f(z, c);
  }
  return res;
}
float lsSel(vec3 v, int i){ return i == 0 ? v.x : i == 1 ? v.y : v.z; }
vec3 lsTet(int n){ return 0.57735 * (n == 0 ? vec3(1.0, -1.0, -1.0) : n == 1 ? vec3(-1.0, -1.0, 1.0) : n == 2 ? vec3(-1.0, 1.0, -1.0) : vec3(1.0)); }
void main(){
  bool slice = uSlice > 0, column = uSlice > 1;
  vec2 q = (gl_FragCoord.xy - uRect.xy - 0.5 * uRect.zw) * uPxw;
  float q2 = dot(q, q), edge = LS_BALL + uPxw;
  if (!slice && q2 >= edge * edge){ o = vec4(uBg, 1.0); return; }
  float h = sqrt(max(LS_BALL * LS_BALL - q2, 0.0));
  vec3 ro = q.x * uRt + q.y * uUp, rd = -uEye;
  if (slice) ro = vec3((gl_FragCoord.xy - 0.5) * uSl.z - uSl.y, uSl.x);
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
  // 3: the place where the ray goes through the flat plane z = 0 (only when the cut is asked for).
  int st = 0, i = 0, oA = 0, oB = 0, L = 0, n = 0, jo = 0, sres = 0;
  float tF = uFlat.y > 0.0 && abs(rd.z) > 1e-5 ? -ro.z / rd.z : 1e9;
  for (int it = 0; it < uBudget; it++){
    float t = 0.5 * (lo + hi);
    int km = uMaxK;
    vec3 p;
    if (st == 0){ t = i < ns ? -h + (float(i) + 0.5) * dt : h + E0; p = ro + t * rd; }
    else if (st == 1){ p = ro + t * rd; km = int(lk); }
    else if (st == 2){ p = ro + t * rd + uEps * lsTet(n); km = jo; }
    else { p = ro + tF * rd; p.z = 0.0; km = int(uFlat.x); }
    if (slice) p = ro;
    if (column) p.z = hc * (2.0 * (float(it) + 0.5) / float(uBudget) - 1.0);
    int res = lsOrb(p, km, slice || st != 2);
    if (column){ sres = max(sres, res); continue; }      // the highest number on the line: uBudget points of it, evenly spread
    if (slice){ sres = res; break; }
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
    } else if (st == 3){
      if (float(res) > uFlat.x){ col += T * uFlat.y * uFc; T *= 1.0 - uFlat.y; }
      tF = 1e9; st = 0;
      if (i > ns || T < 0.02) break;
    } else {
      // The skin is where the orbit stands exactly on the big ball at step jo. gR is how far out it stands there for
      // this slope point, so the way gR grows is the way out of the shape. gR itself runs from 0 to 1e18 within a
      // pixel once the steps are many; the logarithm of its logarithm grows by about one for each step a point was
      // thrown out earlier, which four points a pixel apart can be compared by. (A number that is no number at all
      // counts as far outside.)
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
      } else if (tF > tA && tF <= tB) st = 3;
      else {
        st = 0;
        if (i > ns || T < 0.02) break;
      }
    }
  }
  if (slice){ o = vec4(float(min(sres, 255)) / 255.0, 0.0, 0.0, 1.0); return; }
  col += T * uBg;
  float cov = clamp((LS_BALL - sqrt(q2)) / uPxw + 0.5, 0.0, 1.0);
  float di = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) - 0.5;
  o = vec4(mix(uBg, col, cov) + di / 255.0, 1.0);
}`;

  let okFlag = true, noteText = '';
  const LOST = 'The graphics of this page were interrupted. The 3D picture comes back by itself.';
  const NOGL = 'This device cannot draw the 3D picture.';
  const CLOSED = 'This 3D picture has been closed.';
  const failWords = a => `The 3D picture could not be prepared for “${a.name}” on this device.`;

  // ----- the rule in JavaScript (MATH and CARRY), for one point
  const fin = (x, d) => (isFinite(+x) ? +x : d);
  // what the approach's own cmap and zmap do (only two entries change anything: see GL_FOLD and GL_QUAT4)
  function cmapJs(id, c, q, jul) {
    if (id === 'fold') return foldk(c, Math.max(2, q.planes || 2));
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
    const K = maxK === undefined ? 16 : maxK;
    if (!(Math.hypot(p[0], p[1], p[2]) <= BALL)) return 0;
    let z = [0, 0, 0], cc;
    if (jul) {
      z = zmapJs(id, p, c, q); cc = cmapJs(id, c, q, true);
      if (!(Math.hypot(z[0], z[1], z[2]) <= BALL)) return 0;
    } else cc = cmapJs(id, p, q, false);
    const car = typeof CARRY !== 'undefined' && CARRY[id] ? CARRY[id] : null;
    let st = car ? car.start(q) : null;
    for (let k = 1; k <= K; k++) {
      const v = [ab[0] ? Math.abs(z[0]) : z[0], (ab[1] ? Math.abs(z[1]) : z[1]) * (fl[0] ? -1 : 1), (ab[2] ? Math.abs(z[2]) : z[2]) * (fl[1] ? -1 : 1)];
      let w;
      if (car) { st = car.step(st, v, cc, q); w = car.pw(st, v, n); } else w = MATH[id](v, n, q, cc);
      z = [w[0] + cc[0], w[1] + cc[1], w[2] + cc[2]];
      if (!(Math.hypot(z[0], z[1], z[2]) <= BALL)) return k;
    }
    return K + 1;
  }

  // ----- the camera, shared with whoever draws on top of the picture
  // yaw about the upright z-axis, pitch above the flat plane, as LEARN_V_VIEWS.s3 means them (learnVProj).
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
    return { s, cx, cy, R: B.R, U: B.U, D: B.D, to: v => [cx + d3(v, B.R) * s, cy - d3(v, B.U) * s, d3(v, B.D)] };
  }

  // ----- the program text for one approach
  function sourceFor(a, n2) {
    const pick = (text, re, fall) => { const m = typeof text === 'string' ? re.exec(text) : null; return m ? m[0] : fall; };
    const head = typeof GL_HEAD !== 'undefined' ? GL_HEAD : '', orbit = typeof GL_ORBIT !== 'undefined' ? GL_ORBIT : '';
    const cm = pick(head, /vec2 cmul\([^\n]*\n/, ''), at = pick(head, /float at2\([^\n]*\n/, '');
    const help = cm && at ? cm + at : FALL_HELP;
    const step = pick(orbit, /#ifdef APR_CARRY\nvec3 f\([^\n]*\n#else\nvec3 f\([^\n]*\n#endif\nvec3 start\([^\n]*\n/, FALL_STEP);
    const fc = compileFormula('z^n + c', true, n2), zc = compileFormula('0', false, n2);
    return HEAD + help + a.glsl + '\n' + step.split('__F__').join(fc).split('__Z0__').join(zc) + TAIL;
  }

  // How fine a picture is. n: stops across the whole ball. bis: halvings of a crossing. cross: skins a ray may meet
  // before it stops. res: buffer pixels per CSS pixel. cap: the most pixels a buffer may have.
  // 'still' draws four buffer pixels for each pixel of an ordinary screen, so edges come out smooth, steps down
  // only if a frame takes far too long, and comes back up when frames are quick again. 'move' starts at its second
  // entry and goes finer or coarser by what the graphics card reports (see learnt). Half size, the contract's
  // yardstick for 'move', is its third entry.
  const QUAL = {
    still: [{ n: 320, bis: 7, cross: 20, res: 2, cap: 3.6e6 }, { n: 256, bis: 6, cross: 16, res: 1.5, cap: 2.4e6 }, { n: 224, bis: 6, cross: 12, res: 1, cap: 1.6e6 }],
    move: [{ n: 160, bis: 5, cross: 12, res: 1, cap: 1.2e6 }, { n: 128, bis: 4, cross: 10, res: 0.75, cap: 0.8e6 }, { n: 96, bis: 4, cross: 10, res: 0.5, cap: 0.4e6 },
      { n: 80, bis: 3, cross: 8, res: 0.4, cap: 0.25e6 }, { n: 64, bis: 3, cross: 7, res: 0.33, cap: 0.16e6 }, { n: 48, bis: 2, cross: 6, res: 0.25, cap: 0.1e6 }],
  };
  // How see-through a skin is (o.look may change any of these, for trying things out):
  // front, back: the opacity of the near and of the far side of a body, [seen face on, at the rim]. rim: how quickly
  // a skin goes from the one to the other. fog: how strongly the inside of a body is tinted, per unit of length.
  // glow: how much more of a far side shows where the light falls on it from inside (the bright patch opposite the
  // highlight is what makes a plain ball read as glass and not as a painted one).
  const LOOK = { front: [0.13, 0.92], back: [0.12, 0.52], rim: 2.8, fog: 0.04, glow: 0.55 };
  // What `solid` = 1 makes of a skin (a level's `solid`, or o.solid for every level that has none): its near side
  // this opaque [face on, at the rim], and its far side and the glow there showing by this much less. For bodies
  // with many fine folds, which as glass are a tangle of sheets seen through one another: with the near side this
  // solid the form reads (tried at 0.13, 0.35, 0.6 and 0.85: out/r26/fix/NOTES.md).
  const SOLID = { front: [0.6, 0.95], hide: 0.6 };

  function make() {
    if (typeof document === 'undefined') return null;
    const canvas = document.createElement('canvas');
    canvas.className = 'learn-shape3d';
    let gl = null;
    try { gl = canvas.getContext('webgl2', { antialias: false, alpha: false, depth: false, stencil: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' }); } catch (err) { gl = null; }
    if (!gl) { okFlag = false; noteText = NOGL; return null; }
    const progs = new Map();      // by approach and kind of formula, least recently used first
    let tq = null, pend = null, fbo = null, last = null, gone = false, frames = 0;
    let ref = null;                      // the last frame the card has timed: its time, its work (buffer pixels times stops), its zoom and scene
    const lod = { move: 1, still: 0 };   // which entry of QUAL each quality stands at
    const gpuMs = { move: 0, still: 0 }, stats = { builds: {}, last: null };
    const setup = () => { tq = gl.getExtension('EXT_disjoint_timer_query_webgl2'); pend = null; fbo = null; progs.clear(); };
    setup();

    function program(a, n2) {
      const key = a.id + (n2 ? '|2' : '|n');
      let e = progs.get(key);
      if (e) { progs.delete(key); progs.set(key, e); return e; }
      const t0 = performance.now();
      e = { key, ok: false, p: null, ms: 0, log: '', loc: {} };
      try {
        const p = gl.createProgram(), vs = gl.createShader(gl.VERTEX_SHADER), fs = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(vs, typeof VERT !== 'undefined' ? VERT : FALL_VERT); gl.compileShader(vs);
        gl.shaderSource(fs, sourceFor(a, n2)); gl.compileShader(fs);
        gl.attachShader(p, vs); gl.attachShader(p, fs); gl.linkProgram(p);
        e.ok = !!gl.getProgramParameter(p, gl.LINK_STATUS);
        if (!e.ok) e.log = [gl.getShaderInfoLog(fs), gl.getShaderInfoLog(vs), gl.getProgramInfoLog(p)].filter(Boolean).join('\n') || 'link failed';
        gl.deleteShader(vs); gl.deleteShader(fs);
        if (e.ok) e.p = p; else gl.deleteProgram(p);
      } catch (err) { e.ok = false; e.log = String(err && err.message || err); }
      e.ms = performance.now() - t0;
      stats.builds[key] = e.ms;
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
      okFlag = e.ok; noteText = e.ok ? '' : failWords(a);
      return e;
    }
    // What a frame cost, as the graphics card (or, failing that, a wait for it) reports. 'move' has to feel live: a
    // frame that takes too long makes the next ones coarser, a quick one finer again. 'still' gets coarser only when
    // a frame takes far too long (a picture zoomed far in can), and finer again once a frame is quick: one step
    // finer costs two to three times as much, so a frame under 45 ms stays under the 160 that sent it down.
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
      if (gone) return { ok: false, ms: 0, note: CLOSED };
      if (gl.isContextLost()) return { ok: false, ms: 0, note: LOST };
      pollTimer();
      // o.lod (for tests and timings) holds the picture at one entry of QUAL; otherwise the view picks the entry itself
      const held = isFinite(+o.lod) && o.lod !== null && o.lod !== '';
      let at = held ? clamp(Math.round(+o.lod), 0, QUAL[quality].length - 1) : lod[quality];
      const panes = (o.panes || []).filter(p => p && p.rect && p.rect[2] > 0 && p.rect[3] > 0).slice(0, 2);
      // fit the buffer to the box the page gives the canvas
      const cw = canvas.clientWidth || Math.max(0, ...panes.map(p => p.rect[0] + p.rect[2])) || 300;
      const ch = canvas.clientHeight || Math.max(0, ...panes.map(p => p.rect[1] + p.rect[3])) || 150;
      // a sharp screen already has the pixels 'still' would add; 'move' takes half of what such a screen offers
      const dpr = clamp(window.devicePixelRatio || 1, 1, 3), V = viewOf(o);
      // the buffer and the stops that one entry of QUAL means for this box and this zoom
      const fit = q => {
        let sc = (quality === 'move' ? q.res * Math.min(dpr, 1.5) : Math.max(q.res, Math.min(dpr, 2))) * fin(o.res, 1);
        sc *= Math.min(1, Math.sqrt(q.cap / (cw * ch * sc * sc)));
        return { bw: Math.max(2, Math.round(cw * sc)), bh: Math.max(2, Math.round(ch * sc)), n: Math.round(q.n * clamp(Math.sqrt(V.zoom), 1, 2)) };
      };
      // A 'still' picture is dear: four buffer pixels for one and twice the stops, and zoomed in every ray runs
      // through the shape. The card's time goes with buffer pixels times stops (measured: out/r26/join/NOTES.md), so
      // what the last timed frame of the same scene cost says what this one would. One that would hold the page up
      // for more than about an eighth of a second is drawn a step or two coarser from the start. (Zoomed further in
      // than that frame was, more of the picture is shape: counted as the square of how much further.)
      const key = ap().id + '|' + panes.map(p => p.kind).join('');
      if (!held && quality === 'still' && ref && ref.key === key && Math.abs(Math.log(V.zoom / ref.zoom)) < 0.5) {
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
      if (!e.ok) return { ok: false, ms: performance.now() - t0, note: noteText };
      // the skins, lowest step first (of more than three, the three drawn most strongly): o.levels for every pane,
      // or a pane's own levels for that pane alone
      const skins = levels => {
        const lv = (levels || []).filter(l => l && isFinite(+l.k) && +l.alpha > 0.003)
          .map(l => ({ k: clamp(Math.round(+l.k), 0, 250), a: clamp(+l.alpha, 0, 1), t: clamp(fin(l.tint, 0), 0, 1), g: clamp(fin(l.ghost, 0), 0, 1), s: clamp(fin(l.solid, fin(o.solid, 0)), 0, 1) }))
          .sort((x, y) => y.a - x.a).slice(0, 3).sort((x, y) => x.k - y.k);
        const lk = [1e4, 1e4, 1e4], la = [0, 0, 0], ls = [0, 0, 0], lc = new Float32Array(9);
        lv.forEach((l, i) => {
          lk[i] = l.k; la[i] = l.a; ls[i] = l.s;
          // from the body colour towards the warning colour by the tint (and, as an extra, towards the ink by `ghost`)
          for (let j = 0; j < 3; j++) { const b = body[j] + (warn[j] - body[j]) * l.t; lc[3 * i + j] = b + (ink[j] - b) * l.g; }
        });
        return { lv, lk, la, ls, lc };
      };
      const shared = skins(o.levels), per = panes.map(p => (Array.isArray(p.levels) ? skins(p.levels) : shared));
      if (!panes.length || per.every(sk => !sk.lv.length)) return { ok: true, ms: performance.now() - t0, note: '' };
      const B = basis(V.yaw, V.pitch);
      // the light stays where it is for the viewer (from the upper left, in front), so a turned shape is lit the same way
      const mixv = (a, b, c) => { const v = [0, 1, 2].map(j => a * B.R[j] + b * B.U[j] + c * B.D[j]), l = Math.hypot(v[0], v[1], v[2]); return v.map(x => x / l); };
      const light = mixv(-0.46, 0.62, 0.64), half = mixv(-0.46, 0.62, 1.64);
      const lum = 0.3 * bg[0] + 0.59 * bg[1] + 0.11 * bg[2];
      const lookOf = (key, i) => { const v = o.look && o.look[key]; return fin(i === undefined ? v : v && v[i], i === undefined ? LOOK[key] : LOOK[key][i]); };
      gl.useProgram(e.p);
      ruleUniforms(e, o.c);
      gl.uniform3fv(U(e, 'uRt'), B.R); gl.uniform3fv(U(e, 'uUp'), B.U); gl.uniform3fv(U(e, 'uEye'), B.D);
      gl.uniform3fv(U(e, 'uBg'), bg); gl.uniform3fv(U(e, 'uLight'), light); gl.uniform3fv(U(e, 'uHalf'), half);
      gl.uniform3f(U(e, 'uSpec'), 1, 1, lum > 0.5 ? 1 : 0.94);
      gl.uniform4f(U(e, 'uLook'), lookOf('front', 0), lookOf('front', 1), lookOf('back', 0), lookOf('back', 1));
      gl.uniform1f(U(e, 'uRim'), lookOf('rim')); gl.uniform1f(U(e, 'uFog'), lookOf('fog')); gl.uniform1f(U(e, 'uGlow'), lookOf('glow'));
      // what a skin with `solid` 1 looks like (never more see-through than the glass it starts from)
      gl.uniform3f(U(e, 'uSolid'), Math.max(SOLID.front[0], lookOf('front', 0)), Math.max(SOLID.front[1], lookOf('front', 1)), SOLID.hide);
      // what one pane's skins hand to the program
      const wear = sk => {
        const lv = sk.lv, lc = sk.lc;
        gl.uniform3fv(U(e, 'uLk'), sk.lk); gl.uniform3fv(U(e, 'uLa'), sk.la); gl.uniform3fv(U(e, 'uLs'), sk.ls); gl.uniformMatrix3fv(U(e, 'uLc'), false, lc);
        gl.uniform1i(U(e, 'uMaxK'), lv[lv.length - 1].k);
        // the cut at z = 0 (o.flat): of the shape drawn most strongly, a shade lighter than its skin
        let cut = null;
        if (o.flat) lv.forEach((l, i) => { if (!cut || l.a >= cut.a) cut = { a: l.a, k: l.k, i }; });
        if (cut) {
          const sh = 0.5 + 0.5 * Math.abs(light[2]);
          gl.uniform3f(U(e, 'uFlat'), cut.k, 0.62 * cut.a, 0);
          gl.uniform3f(U(e, 'uFc'), ...[0, 1, 2].map(j => (lc[3 * cut.i + j] * 0.7 + ink[j] * 0.3) * sh));
        } else { gl.uniform3f(U(e, 'uFlat'), 0, 0, 0); gl.uniform3f(U(e, 'uFc'), 0, 0, 0); }
      };
      const n = F.n, job = { work: bw * bh * n, zoom: V.zoom, key };
      gl.uniform1i(U(e, 'uN'), n); gl.uniform1i(U(e, 'uBis'), Q.bis);
      gl.uniform1i(U(e, 'uBudget'), n + 3 + Q.cross * (Q.bis + 4)); gl.uniform1i(U(e, 'uSlice'), 0);
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
      if (timed) { gl.endQuery(tq.TIME_ELAPSED_EXT); pend = Object.assign({ q: timed, quality, lod: held ? -1 : at }, job); }
      stats.last = { quality, lod: at, n, bw, bh };
      frames++;
      // a browser that does not time its graphics card: now and then wait for one frame and take that time
      if (!tq && (frames % 24 === 1 || !gpuMs[quality])) {
        const px = new Uint8Array(4);
        gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        learnt(quality, held ? -1 : at, performance.now() - t0, job);
      }
      // the time of the graphics card for a frame of this quality once the browser has reported one, else the time this call took
      return { ok: true, ms: gpuMs[quality] || performance.now() - t0, note: '' };
    }

    // For tests: the step at which each point of the square |x|, |y| <= half at the height z is thrown out, worked
    // out by the same program the picture uses. size points to a side, the outer ones ON the edge of the square
    // (opt.centres: true puts them at the centres of size cells instead). Row 0 is the top, y = +half.
    // null when the program did not build.
    function slice(kind, c, opt) { return ask(kind, c, opt, 0); }
    // For the page's words (the picture itself is not read back): the shape seen from straight above, without glass.
    // Each point of the square |x|, |y| <= half stands for the upright line through it, and the answer is the
    // highest number slice() gives anywhere on the part of that line that lies inside the big ball: above k means
    // that something of shape k stands on this line. opt.stops points of each line are asked, evenly spread
    // (192 unless said). size, half, maxK, centres and the order of the rows as for slice(); null when the program
    // did not build. From the SAME GLSL as the picture and slice(): one more way to use the one loop.
    function columns(kind, c, opt) { return ask(kind, c, opt, clamp(Math.round(fin(opt && opt.stops, 192)), 1, 1024)); }
    function ask(kind, c, opt, stops) {
      opt = opt || {};
      const size = clamp(Math.round(fin(opt.size, 256)), 2, 2048), half = fin(opt.half, BALL), maxK = clamp(Math.round(fin(opt.maxK, 16)), 0, 254);
      if (gone || gl.isContextLost()) return null;
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
      const step = opt.centres ? 2 * half / size : 2 * half / (size - 1);
      gl.uniform3f(U(e, 'uSl'), stops ? 0 : fin(opt.z, 0), opt.centres ? half - step / 2 : half, step);
      gl.uniform1f(U(e, 'uJulia'), kind === 'j' ? 1 : 0);
      gl.uniform1i(U(e, 'uMaxK'), maxK); gl.uniform1i(U(e, 'uBudget'), stops || 1); gl.uniform1i(U(e, 'uSlice'), stops ? 2 : 1);
      gl.uniform1i(U(e, 'uN'), 1); gl.uniform1i(U(e, 'uBis'), 0); gl.uniform1f(U(e, 'uPxw'), 1); gl.uniform4f(U(e, 'uRect'), 0, 0, size, size);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      const px = new Uint8Array(size * size * 4), res = new Uint8Array(size * size);
      gl.readPixels(0, 0, size, size, gl.RGBA, gl.UNSIGNED_BYTE, px);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      for (let row = 0; row < size; row++) for (let x = 0; x < size; x++) res[row * size + x] = px[((size - 1 - row) * size + x) * 4];
      return res;
    }
    // The place slice() asks about for a row and a column: the same numbers the graphics card is given.
    function slicePoint(row, colm, opt) {
      const size = clamp(Math.round(fin(opt.size, 256)), 2, 2048), half = fin(opt.half, BALL);
      const step = opt.centres ? 2 * half / size : 2 * half / (size - 1), h0 = opt.centres ? half - step / 2 : half;
      return [colm * step - h0, (size - 1 - row) * step - h0, fin(opt.z, 0)];
    }
    // For tests and notes: draw o `reps` times, each time waiting for the graphics card, and give the times in ms.
    function time(o, reps) {
      const px = new Uint8Array(4), ts = [];
      draw(o); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
      for (let i = 0; i < (reps || 5); i++) {
        const t0 = performance.now();
        draw(o); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        ts.push(performance.now() - t0);
      }
      return ts;
    }
    const onLost = ev => { ev.preventDefault(); };
    const onBack = () => { setup(); if (last && !gone) draw(last); };
    canvas.addEventListener('webglcontextlost', onLost);
    canvas.addEventListener('webglcontextrestored', onBack);
    function dispose() {
      if (gone) return;
      gone = true; last = null;
      canvas.removeEventListener('webglcontextlost', onLost); canvas.removeEventListener('webglcontextrestored', onBack);
      if (!gl.isContextLost()) {
        for (const e of progs.values()) if (e.p) gl.deleteProgram(e.p);
        if (fbo) { gl.deleteTexture(fbo.tex); gl.deleteFramebuffer(fbo.fb); }
        if (pend) gl.deleteQuery(pend.q);
      }
      progs.clear(); fbo = null; pend = null;
      const lose = gl.getExtension('WEBGL_lose_context');
      if (lose) lose.loseContext();
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
    }
    return { canvas, draw, slice, columns, dispose, slicePoint, time, stats: () => ({ builds: Object.assign({}, stats.builds), last: stats.last, gpuMs: Object.assign({}, gpuMs), lod: Object.assign({}, lod) }), proj };
  }

  return { make, out, ok: () => okFlag, note: () => noteText, proj, source: sourceFor };
})();
