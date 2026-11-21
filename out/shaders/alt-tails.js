// test-only: alternative main() structures, to see which the D3D compiler digests fastest
const ALT_TAILS = {
march: `
void main(){
  vec2 uv = (2.0 * (gl_FragCoord.xy + uOff) - uRes) / uRes.y;
  vec3 ro = uCamPos, rd = normalize(uCam * vec3(uv * uFov, 1.0)), p = ro;
  gB = mat3(1.0); gStepLimit = 1e9; gRayDir = rd; gEmptyCell = false; gProbing = false; gInsideOut = false; gPowerLaw = true;
  float t = 0.0, e = 1e-6, pix = 2.0 * uFov / uRes.y;
  for (int i = 0; i < uSteps; i++){
    p = ro + rd * t; e = max(uDetail * pix * t, 1e-7);
    float d = de(p, uNT);
    if (d < e) break;
    t += d * uStepK;
    if (t > 20.0) break;
  }
  o = vec4(t, gEsc, gIt, gGrad.x + gLast.x);
}`,
nocont: `
const int PH_PROBE = 0, PH_BEGIN = 1, PH_FLAT = 2, PH_MARCH = 3, PH_SLOPE = 4, PH_SHADOW = 5, PH_AO = 6;
vec3 tetra(int i){ return vec3(i == 0 || i == 3 ? 1.0 : -1.0, i == 2 || i == 3 ? 1.0 : -1.0, i == 1 || i == 3 ? 1.0 : -1.0); }
float withCut(float d, vec3 q, float e){
  float pl = q.z - uCut;
  if (gEsc < 0.5 && pl > -e) d = min(d, 0.0);
  gId = pl > d ? 1.0 : 0.0;
  return max(d, pl);
}
void main(){
  vec2 uv = (2.0 * (gl_FragCoord.xy + uOff) - uRes) / uRes.y;
  bool flat2 = uFlat > 0.5, picking = uPick > 0.5;
  vec3 ro = uCamPos, rd = normalize(uCam * vec3(uv * uFov, 1.0)), col = uBg, L = uLight, nor = vec3(0.0);
  vec3 p = flat2 ? vec3(uFlatC + 0.5 * uFlatH * uv, uSliceZ) : ro;
  if (flat2 && picking){ o = vec4(p, 1.0); return; }
  float bound = uBound > 0.0 ? uBound : 8.0, pix = 2.0 * uFov / uRes.y, farLimit = 0.45 * uBail;
  float t = 0.0, tMax = -1.0, e = 1e-6, hh = 0.0, ts = 0.0, res = 1.0, sh = 1.0, occ = 1.0, ao = 0.0, aw = 1.0, dif = 0.0;
  int phase = ORBIT_SCENE ? PH_PROBE : PH_BEGIN, n = 0, nt = uNT, budget = uSteps + uShSteps + 12;
  bool hit = false, lit = false, done = false;
  gB = mat3(1.0); gId = 0.0; gStepLimit = 1e9; gRayDir = rd;
  gEmptyCell = false; gProbing = false; gInsideOut = false; gPowerLaw = true;
  for (int i = 0; i < budget; i++){
    if (phase == PH_BEGIN){
      if (flat2) phase = PH_FLAT;
      else {
        if (nt == 0 && !gPowerLaw) nt = 1;
        if (nt == 1) gB[0] = rd;
        float R = gInsideOut ? min(bound, farLimit) : bound;
        float b = dot(ro, rd), h = b * b - dot(ro, ro) + R * R;
        if (h <= 0.0) done = true;
        else {
          h = sqrt(h);
          t = max(-b - h, 0.0); tMax = -b + h;
          if (tMax < t) done = true;
          phase = PH_MARCH;
        }
      }
    }
    if (!done){
      vec3 q = p; int qn = nt;
      if (phase == PH_PROBE){ q = farLimit * normalize(vec3(0.62, 0.37, 0.69)); qn = 0; gProbing = true; }
      else if (phase == PH_FLAT) qn = 3;
      else if (phase == PH_MARCH){ p = ro + rd * t; e = max(uDetail * pix * t, 1e-7); q = p; }
      else if (phase == PH_SLOPE) q = p + tetra(n) * hh;
      else if (phase == PH_SHADOW){ q = p + nor * 2.0 * e + L * ts; qn = min(nt, 1); }
      else { q = p + nor * (0.006 * t * float((n + 1) * (n + 1))); qn = min(nt, 1); }
      float d = de(q, qn);
      if (phase == PH_PROBE){ gProbing = false; gInsideOut = gEsc < 0.5; phase = PH_BEGIN; }
      else if (phase == PH_FLAT){
        if (gInsideOut && length(p) > farLimit){ gEsc = 1.0; d = max(d, length(p) - farLimit); }
        col = flatColour(p, d, uFlatH / uRes.y);
        done = true;
      } else {
        if (phase != PH_SLOPE) d = withCut(d, q, e);
        bool settle = false, toAO = false;
        if (phase == PH_MARCH){
          n++;
          bool conv = d < e;
          if (!conv) t += min(d * uStepK, gStepLimit);
          if (conv || t > tMax || n >= uSteps){
            hit = t <= tMax && (conv || !gEmptyCell);
            if (!hit || picking) done = true;
            else {
              p = ro + rd * t;
              colourCapture();
              if (gId > 0.5){
                float s = abs(fract((gl_FragCoord.x + gl_FragCoord.y) / (8.0 * uPx)) - 0.5);
                col = mix(uCutCol, uCutInk, 0.55 * smoothstep(0.36, 0.42, s));
                done = true;
              } else if (uAnalytic < 0.5 || nt != 3){ phase = PH_SLOPE; n = 0; hh = uNormEps * e; }
              else { nor = gGrad; settle = true; }
            }
          }
        } else if (phase == PH_SLOPE){
          nor += tetra(n) * d; n++;
          settle = n == 4;
        } else if (phase == PH_SHADOW){
          res = min(res, 10.0 * d / ts); n++;
          if (res >= 0.005 && ts <= 5.0 && n < uShSteps) ts += min(clamp(d, 2.0 * e, 0.35), gStepLimit);
          else { sh = clamp(res, 0.0, 1.0); sh = sh * sh * (3.0 - 2.0 * sh); toAO = true; }
        } else {
          float reach = 0.006 * t * float((n + 1) * (n + 1));
          ao += aw * clamp(1.0 - 1.6 * d / reach, 0.0, 1.0); aw *= 0.7; n++;
          if (n == 4){ occ = clamp(1.0 - 0.45 * ao, 0.0, 1.0); done = true; }
        }
        if (settle){
          nor = dot(nor, nor) > 0.0 ? normalize(nor) : -rd;
          if (dot(nor, rd) > 0.0) nor = normalize(nor - 1.05 * dot(nor, rd) * rd);
          dif = clamp(dot(nor, L), 0.0, 1.0); lit = true;
          if (uShadow > 0.5 && dif > 0.001){ phase = PH_SHADOW; n = 0; ts = 4.0 * e; res = 1.0; gB[0] = L; gRayDir = L; }
          else toAO = true;
        }
        if (toAO){
          if (uAO < 0.5) done = true;
          else { phase = PH_AO; n = 0; gB[0] = nor; }
        }
      }
    }
    if (done) break;
  }
  if (picking){ o = hit ? vec4(ro + rd * t, 1.0) : vec4(0.0); return; }
  if (lit){
    vec3 alb = surfaceColour(p, nor, t);
    float sky = 0.5 + 0.5 * nor.z;
    float bac = clamp(0.3 + 0.7 * dot(nor, normalize(vec3(-L.x, -L.y, 0.3))), 0.0, 1.0);
    float fre = pow(clamp(1.0 + dot(nor, rd), 0.0, 1.0), 3.0);
    float spe = pow(clamp(dot(nor, normalize(L - rd)), 0.0, 1.0), 40.0) * dif * sh;
    vec3 lig = 1.45 * dif * sh * vec3(1.00, 0.94, 0.84) + occ * (0.42 * sky * vec3(0.50, 0.62, 0.80) + 0.20 * bac * vec3(0.80, 0.70, 0.58));
    col = alb * lig + 0.16 * spe + 0.06 * fre * occ * alb;
    if (colourUnlit() > 0.5) col = alb;
  }
  o = vec4(col, 1.0);
}`,
};
