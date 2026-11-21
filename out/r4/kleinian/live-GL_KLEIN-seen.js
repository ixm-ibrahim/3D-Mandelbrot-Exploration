const GL_KLEIN = `
const bool ORBIT_SCENE = false;
float wrapf(float x, float a, float s){ x -= s; return (x - a * floor(x / a)) + s; }
float kde(vec3 z){
  vec3 mu = uKMu, lz = z + vec3(1.0), llz = z - vec3(1.0);
  float a = mu.y, DF = 1.0, it = 0.0, fs = sign(-mu.x);
  float sx = mu.x / a, sz = mu.z / a;
  trapStart();
  float best = min(z.y, a - z.y);   // distance to the two walls, before any map is applied
  for (int i = 0; i < uIter; i++){
    z.x -= sx * z.y; z.x = wrapf(z.x, 2.0, -1.0); z.x += sx * z.y;
    if (uK3 > 0.5) { z.z -= sz * z.y; z.z = wrapf(z.z, 2.0 * uKL, -uKL); z.z += sz * z.y; }
    float xs = z.x - 0.5 * mu.x;
    if (z.y >= a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * sign(xs) * (1.0 - exp(-(7.2 - (1.95 - a) * 15.0) * abs(xs)))) z = mu - z;
    float iR = 1.0 / max(dot(z, z), 1e-20);
    z = mu + vec3(z.x, -z.y, -z.z) * iR;   // q -> mu + 1/q
    DF *= iR; it += 1.0;
    best = min(best, min(z.y, a - z.y) / max(DF, 1.0));
    trapAdd(z, it);
    if (dot(z - llz, z - llz) < 1e-5) break;
    llz = lz; lz = z;
  }
  gIt = it; gLast = z;
  return min(best, 0.3);
}
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0);
  float r2 = max(dot(p, p), 1e-12), r = sqrt(r2), R2 = uKInvR * uKInvR;
  vec3 q = uKInvC + (R2 / r2) * p;
  if (q.y < 0.0 || q.y > uKMu.y) { gEsc = 0.0; trapStart(); trapAdd(q, 0.0); gIt = 0.0; gLast = q; return 0.0; }
  float d = kde(q);
  return r2 * d / (R2 + r * d);
}`;