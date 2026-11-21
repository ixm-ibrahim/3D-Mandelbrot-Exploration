// A drop-in replacement for kde() inside GL_KLEIN (src/js/30-shaders.js). Proposed by klein-presets, not applied:
// that file belongs to the shaders module. Tested on the baseline through
//   python build.py --name klein-presets-exact --base base --swap js/30-shaders.js=out/klein-presets/shaders-exact.js
// Same uniforms, same hooks (trapStart, trapAdd), same results gIt and gLast. Only the returned distance changes.
//
// Why. The estimate the lab uses, (distance from the mapped point to a wall) / DF, is not the distance to the
// pearl. For a pearl of radius rho at true distance t it equals t (1 + t / (2 rho)): right beside the pearl, far too
// large away from it. A ray that comes at a small pearl from open space therefore steps into it (the pearl is drawn
// hollow) or over it (the pearl is missing). At the default step share of 0.8 the baseline loses up to 9% of the
// pixels of a preset; see notes/klein-presets.md for the table.
//
// How. Carry one more point, W, through the same maps as z, starting at infinity (the point where the two walls
// touch). After n steps the maps so far are a Moebius map F with F(infinity) = W, and the pearl met at this step is
// the sphere that F carries onto a wall. Its radius is rho = |z - W|^2 / (2 D DF), where D is the distance from W
// to that wall. Solving E = t (1 + t / (2 rho)) for t gives the true distance
//     t = E * 2 / (1 + sqrt(1 + 2 E / rho)),     2 E / rho = 4 h D / |z - W|^2,     h = distance from z to the wall.
// Checked against a direct list of the pearls in notes/klein_model.py (kde_exact): never below the true distance,
// and equal to it for half of all sample points or more.
float kde(vec3 z){
  vec3 mu = uKMu, lz = z + vec3(1.0), llz = z - vec3(1.0), W = vec3(1e6);
  float a = mu.y, DF = 1.0, it = 0.0, fs = sign(-mu.x);
  float sx = mu.x / a, sz = mu.z / a;
  trapStart();
  float best = min(z.y, a - z.y);   // distance to the two walls, before any map is applied
  for (int i = 0; i < uIter; i++){
    float x0 = z.x;
    z.x -= sx * z.y; z.x = wrapf(z.x, 2.0, -1.0); z.x += sx * z.y; W.x += z.x - x0;
    if (uK3 > 0.5) { float z0 = z.z; z.z -= sz * z.y; z.z = wrapf(z.z, 2.0 * uKL, -uKL); z.z += sz * z.y; W.z += z.z - z0; }
    float xs = z.x - 0.5 * mu.x;
    if (z.y >= a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * sign(xs) * (1.0 - exp(-(7.2 - (1.95 - a) * 15.0) * abs(xs)))) { z = mu - z; W = mu - W; }
    float iR = 1.0 / max(dot(z, z), 1e-20);
    z = mu + vec3(z.x, -z.y, -z.z) * iR;   // q -> mu + 1/q
    W = mu + vec3(W.x, -W.y, -W.z) / max(dot(W, W), 1e-20);
    DF *= iR; it += 1.0;
    vec3 zw = z - W;
    float kk = 4.0 / max(dot(zw, zw), 1e-30), h0 = z.y, h1 = a - z.y;
    float c0 = h0 > 0.0 ? 2.0 * h0 / (1.0 + sqrt(1.0 + kk * h0 * max(W.y, 0.0))) : h0;
    float c1 = h1 > 0.0 ? 2.0 * h1 / (1.0 + sqrt(1.0 + kk * h1 * max(a - W.y, 0.0))) : h1;
    best = min(best, min(c0, c1) / DF);
    trapAdd(z, it);
    if (dot(z - llz, z - llz) < 1e-5) break;
    llz = lz; lz = z;
  }
  gIt = it; gLast = z;
  return min(best, 0.3);
}
