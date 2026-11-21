const GL_KLEIN = `
const bool ORBIT_SCENE = false;
float wrapf(float x, float a, float s){ x -= s; return (x - a * floor(x / a)) + s; }
// The exact distance from the point to a pearl, where the maps applied so far carry that pearl onto a wall.
// h: how far the mapped point stands from that wall. D: the same for W, the image of the point at infinity.
// kk = 4 / |z - W|^2. The plain estimate h / DF equals t (1 + t / 2 rho) for a pearl of radius rho at the true
// distance t, which is far too long for a small pearl seen from open space; this solves it for t.
float kpearl(float h, float D, float kk){ return h > 0.0 ? 2.0 * h / (1.0 + sqrt(1.0 + kk * h * max(D, 0.0))) : h; }
float kde(vec3 z){
  vec3 mu = uKMu, lz = z + vec3(1.0), llz = z - vec3(1.0), W = vec3(1e6);
  float a = mu.y, DF = 1.0, it = 0.0, fs = sign(-mu.x), far = 0.0;
  float sx = mu.x / a, sz = mu.z / a;
  bool solidTrap = uTrapSolid > 0.5, pearls = uTrapSolid < 0.5 || uTrapSolid > 1.5;
  trapStart();
  float best = min(z.y, a - z.y), bestT = 1e9;   // the two walls, before any map is applied
  if (solidTrap && uTrapSkip <= 0) bestT = trapDist(z) - uTrapW;
  for (int i = 0; i < uIter; i++){
    vec3 z0 = z;
    if (far < 0.5){
      // the usual choice of map: back into the leaning cell, then the half-turn about mu / 2 for the upper part
      z.x -= sx * z.y; z.x = wrapf(z.x, 2.0, -1.0); z.x += sx * z.y;
      if (uK3 > 0.5) { z.z -= sz * z.y; z.z = wrapf(z.z, 2.0 * uKL, -uKL); z.z += sz * z.y; }
      W += z - z0;
      float xs = z.x - 0.5 * mu.x;
      if (z.y >= a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * sign(xs) * (1.0 - exp(-(7.2 - (1.95 - a) * 15.0) * abs(xs)))) { z = mu - z; W = mu - W; }
    } else {
      // second wind (see below): toward whichever centre, 2m or mu + 2m, is nearest, the map that stretches most
      vec3 c0 = vec3(2.0 * floor(0.5 * z.x + 0.5), 0.0, 0.0), c1 = mu + vec3(2.0 * floor(0.5 * (z.x - mu.x) + 0.5), 0.0, 0.0);
      if (uK3 > 0.5){ float l2 = 2.0 * uKL; c0.z = l2 * floor(z.z / l2 + 0.5); c1.z += l2 * floor((z.z - mu.z) / l2 + 0.5); }
      if (dot(z - c1, z - c1) < dot(z - c0, z - c0)) { z = c1 - z; W = c1 - W; }
      else { z -= c0; W -= c0; }
    }
    float iR = 1.0 / max(dot(z, z), 1e-20);
    z = mu + vec3(z.x, -z.y, -z.z) * iR;   // q -> mu + 1/q
    W = mu + vec3(W.x, -W.y, -W.z) / max(dot(W, W), 1e-20);
    DF *= iR; it += 1.0;
    vec3 zw = z - W;
    float kk = 4.0 / max(dot(zw, zw), 1e-30);
    best = min(best, min(kpearl(z.y, W.y, kk), kpearl(a - z.y, a - W.y, kk)) / DF);
    if (solidTrap && i + 1 >= uTrapSkip) bestT = min(bestT, (trapDist(z) - uTrapW) / DF);
    trapAdd(z, it);
    if (dot(z - llz, z - llz) < 1e-5){
      // The search has started going round in a circle. The usual choice of map does that in every open gap, and
      // also beside some small pearls it has no route to: those were drawn cut or not at all. So it gets a second
      // wind with the other rule, and stops when that goes round as well.
      if (far > 0.5) break;
      break;
    } else { llz = lz; lz = z; }
  }
  gIt = it; gLast = z;
  best = min(best, 0.3);
  return !solidTrap ? best : pearls ? min(best, bestT) : bestT;
}
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0);
  float r2 = max(dot(p, p), 1e-12), r = sqrt(r2), R2 = uKInvR * uKInvR;
  vec3 q = uKInvC + (R2 / r2) * p;
  if (uTrapSolid < 0.5 && (q.y < 0.0 || q.y > uKMu.y)) { gEsc = 0.0; trapStart(); trapAdd(q, 0.0); gIt = 0.0; gLast = q; return 0.0; }
  float d = kde(q);
  if (d <= 0.0) gEsc = 0.0;
  return d > 0.0 ? r2 * d / (R2 + r * d) : d * r2 / R2;
}`;
