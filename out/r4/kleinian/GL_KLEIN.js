const GL_KLEIN = `
const bool ORBIT_SCENE = false;
float wrapf(float x, float a, float s){ x -= s; return (x - a * floor(x / a)) + s; }
// The true distance to a pearl, in the units of the wall it has been carried onto. A pearl is the sphere that
// the maps applied so far carry onto a wall. h: how far the mapped point stands from that wall. D: the same for
// W, the image of the point at infinity. kk = 4 / |z - W|^2. Dividing h by the scale factor alone gives
// t (1 + t / 2 rho) for a pearl of radius rho at the true distance t: right beside the pearl, far too long for a
// small pearl seen from open space, where rays then stepped into it (a hollow shell) or over it. This is that
// equation solved for t; the caller still divides by the scale factor.
float kpearl(float h, float D, float kk){ return h > 0.0 ? 2.0 * h / (1.0 + sqrt(1.0 + kk * h * max(D, 0.0))) : h; }
// The search: carry the point back into one cell with the generators, tracking the scale factor DF and W.
// Returns the distance to the nearest pearl it met (negative inside one), or to the trap solid, or to both.
float kde(vec3 z){
  vec3 mu = uKMu, lz = z + vec3(1.0), llz = z - vec3(1.0), W = vec3(1e6);
  float a = mu.y, DF = 1.0, it = 0.0, fs = sign(-mu.x);
  float sx = mu.x / a, sz = mu.z / a;
  bool trapSolid = uTrapSolid > 0.5;
  trapStart();
  float best = min(z.y, a - z.y), bestT = 1e9;   // the two walls, before any map is applied
  if (trapSolid && uTrapSkip <= 0) bestT = trapDist(z) - uTrapW;
  for (int i = 0; i < uIter; i++){
    vec3 z0 = z;
    z.x -= sx * z.y; z.x = wrapf(z.x, 2.0, -1.0); z.x += sx * z.y;
    if (uK3 > 0.5) { z.z -= sz * z.y; z.z = wrapf(z.z, 2.0 * uKL, -uKL); z.z += sz * z.y; }
    W += z - z0;
    float xs = z.x - 0.5 * mu.x;
    if (z.y >= a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * sign(xs) * (1.0 - exp(-(7.2 - (1.95 - a) * 15.0) * abs(xs)))) { z = mu - z; W = mu - W; }
    float iR = 1.0 / max(dot(z, z), 1e-20);
    z = mu + vec3(z.x, -z.y, -z.z) * iR;   // q -> mu + 1/q
    W = mu + vec3(W.x, -W.y, -W.z) / max(dot(W, W), 1e-20);
    DF *= iR; it += 1.0;
    vec3 zw = z - W;
    float kk = 4.0 / max(dot(zw, zw), 1e-30);
    best = min(best, min(kpearl(z.y, W.y, kk), kpearl(a - z.y, a - W.y, kk)) / DF);
    // The trap as a solid: every point whose orbit, from step uTrapSkip on, comes within uTrapW of the trap shape.
    // To first order the point is that far from it, divided by how much the maps so far have stretched.
    if (trapSolid && i + 1 >= uTrapSkip) bestT = min(bestT, (trapDist(z) - uTrapW) / DF);
    trapAdd(z, it);
    if (dot(z - llz, z - llz) < 1e-5) break;
    llz = lz; lz = z;
  }
  // In the 3D view the count is reported 8 steps high. "Escape count" colours come out the same (8 steps are one
  // full turn of the palette), and a fading tail (gFade) set from this count leaves every step of the search in.
  gIt = uFlat > 0.5 ? it : it + 8.0; gLast = z;
  best = min(best, 0.3);
  return !trapSolid ? best : uTrapSolid > 1.5 ? min(best, bestT) : bestT;
}
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0);
  float r2 = max(dot(p, p), 1e-12), r = sqrt(r2), R2 = uKInvR * uKInvR;
  vec3 q = uKInvC + (R2 / r2) * p;   // turned out through the sphere
  float wall = min(q.y, uKMu.y - q.y), d = wall;
  // inside a wall sphere (unless the trap alone is the solid): no search is needed, and the depth is known
  if (wall < 0.0 && (uTrapSolid < 0.5 || uTrapSolid > 1.5)) { trapStart(); trapAdd(q, 0.0); gIt = 0.0; gLast = q; }
  else d = kde(q);
  if (d <= 0.0) gEsc = 0.0;
  // back through the sphere: a length d beside q is at least this long beside p
  return d > 0.0 ? r2 * d / (R2 + r * d) : d * r2 / R2;
}`;
