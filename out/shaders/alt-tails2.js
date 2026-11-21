// test-only: more main() structures. "three": march loop (with the probe as its first turn), slope loop, light loop.
const ALT_PRE = `
vec3 tetra(int i){ return vec3(i == 0 || i == 3 ? 1.0 : -1.0, i == 2 || i == 3 ? 1.0 : -1.0, i == 1 || i == 3 ? 1.0 : -1.0); }
float withCut(float d, vec3 q, float e){
  float pl = q.z - uCut;
  if (gEsc < 0.5 && pl > -e) d = min(d, 0.0);
  gId = pl > d ? 1.0 : 0.0;
  return max(d, pl);
}
vec2 span(vec3 ro, vec3 rd, float R){
  float b = dot(ro, rd), h = b * b - dot(ro, ro) + R * R;
  if (h <= 0.0) return vec2(1.0, -1.0);
  h = sqrt(h);
  return vec2(max(-b - h, 0.0), -b + h);
}
void main(){
  vec2 uv = (2.0 * (gl_FragCoord.xy + uOff) - uRes) / uRes.y;
  bool flat2 = uFlat > 0.5, picking = uPick > 0.5;
  vec3 ro = uCamPos, rd = normalize(uCam * vec3(uv * uFov, 1.0)), col = uBg, L = uLight, nor = vec3(0.0);
  vec3 p = flat2 ? vec3(uFlatC + 0.5 * uFlatH * uv, uSliceZ) : ro;
  if (flat2 && picking){ o = vec4(p, 1.0); return; }
  float bound = uBound > 0.0 ? uBound : 8.0, pix = 2.0 * uFov / uRes.y, farLimit = 0.45 * uBail;
  float t = 0.0, e = 1e-6, ts = 0.0, res = 1.0, sh = 1.0, occ = 1.0, ao = 0.0, aw = 1.0, dif = 0.0;
  int n = 0, nt = uNT;
  bool hit = false, lit = false, probing = ORBIT_SCENE;
  gB = mat3(1.0); gId = 0.0; gStepLimit = 1e9; gRayDir = rd;
  gEmptyCell = false; gProbing = false; gInsideOut = false; gPowerLaw = true;
  vec2 sp = span(ro, rd, bound);
  if (nt == 1) gB[0] = rd;
  int turns = uSteps + (ORBIT_SCENE ? 1 : 0);
  for (int i = 0; i < turns; i++){
    vec3 q = p; int qn = nt;
    if (probing){ q = farLimit * normalize(vec3(0.62, 0.37, 0.69)); qn = 0; gProbing = true; }
    else if (flat2) qn = 3;
    else { p = ro + rd * sp.x; e = max(uDetail * pix * sp.x, 1e-7); q = p; }
    float d = de(q, qn);
    if (probing){
      probing = false; gProbing = false; gInsideOut = gEsc < 0.5;
      if (gInsideOut) sp = span(ro, rd, min(bound, farLimit));
      if (nt == 0 && !gPowerLaw){ nt = 1; gB[0] = rd; }
      if (sp.y < sp.x && !flat2) break;
      continue;
    }
    if (flat2){
      if (gInsideOut && length(p) > farLimit){ gEsc = 1.0; d = max(d, length(p) - farLimit); }
      col = flatColour(p, d, uFlatH / uRes.y);
      break;
    }
    d = withCut(d, q, e);
    n++;
    bool conv = d < e;
    if (!conv) sp.x += min(d * uStepK, gStepLimit);
    if (conv || sp.x > sp.y || n >= uSteps){ hit = sp.x <= sp.y && (conv || !gEmptyCell); break; }
  }
  t = sp.x;
  if (picking){ o = hit ? vec4(ro + rd * t, 1.0) : vec4(0.0); return; }
  if (hit){
    p = ro + rd * t;
    colourCapture();
    if (gId > 0.5){
      float s = abs(fract((gl_FragCoord.x + gl_FragCoord.y) / (8.0 * uPx)) - 0.5);
      col = mix(uCutCol, uCutInk, 0.55 * smoothstep(0.36, 0.42, s));
    } else {
      lit = true;
`;
const ALT_POST = `
    }
  }
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
}`;
const ALT_LIGHT = `
      nor = dot(nor, nor) > 0.0 ? normalize(nor) : -rd;
      if (dot(nor, rd) > 0.0) nor = normalize(nor - 1.05 * dot(nor, rd) * rd);
      dif = clamp(dot(nor, L), 0.0, 1.0);
      int nSh = uShadow > 0.5 && dif > 0.001 ? uShSteps : 0, nAo = uAO > 0.5 ? 4 : 0;
      bool shadowing = nSh > 0;
      gB[0] = shadowing ? L : nor; gRayDir = L; ts = 4.0 * e; n = 0;
      for (int i = 0; i < nSh + nAo; i++){
        float reach = 0.006 * t * float((n + 1) * (n + 1));
        vec3 q = shadowing ? p + nor * 2.0 * e + L * ts : p + nor * reach;
        float d = withCut(de(q, min(nt, 1)), q, e);
        n++;
        if (shadowing){
          res = min(res, 10.0 * d / ts);
          if (res < 0.005 || ts > 5.0 || n >= nSh){
            shadowing = false; n = 0; gB[0] = nor;
            if (nAo == 0) break;
          } else ts += min(clamp(d, 2.0 * e, 0.35), gStepLimit);
        } else {
          ao += aw * clamp(1.0 - 1.6 * d / reach, 0.0, 1.0); aw *= 0.7;
          if (n == 4) break;
        }
      }
      sh = clamp(res, 0.0, 1.0); sh = sh * sh * (3.0 - 2.0 * sh);
      occ = clamp(1.0 - 0.45 * ao, 0.0, 1.0);
`;
ALT_TAILS.three = ALT_PRE + `
      nor = gGrad;
      int ns = uAnalytic < 0.5 || nt != 3 ? 4 : 0;
      float hh = uNormEps * e;
      if (ns > 0) nor = vec3(0.0);
      for (int i = 0; i < ns; i++){ vec3 k = tetra(i); nor += k * de(p + k * hh, nt); }
` + ALT_LIGHT + ALT_POST;
// "two": the slope samples share the light loop's call
ALT_TAILS.two = ALT_PRE + `
      nor = gGrad;
      int ns = uAnalytic < 0.5 || nt != 3 ? 4 : 0, nSh = 0, nAo = uAO > 0.5 ? 4 : 0, stage = ns > 0 ? 0 : 1;
      float hh = uNormEps * e;
      if (ns > 0) nor = vec3(0.0);
      n = 0;
      for (int i = 0; i < ns + uShSteps + nAo; i++){
        if (stage == 1){
          nor = dot(nor, nor) > 0.0 ? normalize(nor) : -rd;
          if (dot(nor, rd) > 0.0) nor = normalize(nor - 1.05 * dot(nor, rd) * rd);
          dif = clamp(dot(nor, L), 0.0, 1.0);
          nSh = uShadow > 0.5 && dif > 0.001 ? uShSteps : 0;
          stage = nSh > 0 ? 2 : 3; n = 0; ts = 4.0 * e;
          gB[0] = nSh > 0 ? L : nor; gRayDir = L;
          if (nSh + nAo == 0) break;
        }
        float reach = 0.006 * t * float((n + 1) * (n + 1));
        vec3 k = tetra(n);
        vec3 q = stage == 0 ? p + k * hh : stage == 2 ? p + nor * 2.0 * e + L * ts : p + nor * reach;
        float d = de(q, stage == 0 ? nt : min(nt, 1));
        n++;
        if (stage == 0){ nor += k * d; if (n == 4) stage = 1; }
        else {
          d = withCut(d, q, e);
          if (stage == 2){
            res = min(res, 10.0 * d / ts);
            if (res < 0.005 || ts > 5.0 || n >= nSh){
              stage = 3; n = 0; gB[0] = nor;
              if (nAo == 0) break;
            } else ts += min(clamp(d, 2.0 * e, 0.35), gStepLimit);
          } else {
            ao += aw * clamp(1.0 - 1.6 * d / reach, 0.0, 1.0); aw *= 0.7;
            if (n == 4) break;
          }
        }
      }
      if (stage == 1){
        nor = dot(nor, nor) > 0.0 ? normalize(nor) : -rd;
        if (dot(nor, rd) > 0.0) nor = normalize(nor - 1.05 * dot(nor, rd) * rd);
        dif = clamp(dot(nor, L), 0.0, 1.0);
      }
      sh = clamp(res, 0.0, 1.0); sh = sh * sh * (3.0 - 2.0 * sh);
      occ = clamp(1.0 - 0.45 * ao, 0.0, 1.0);
` + ALT_POST;
const ALT_SETTLE = `
      nor = dot(nor, nor) > 0.0 ? normalize(nor) : -rd;
      if (dot(nor, rd) > 0.0) nor = normalize(nor - 1.05 * dot(nor, rd) * rd);
      dif = clamp(dot(nor, L), 0.0, 1.0);
`;
const ALT_SLOPE = `
      nor = gGrad;
      int ns = uAnalytic < 0.5 || nt != 3 ? 4 : 0;
      float hh = uNormEps * e;
      if (ns > 0) nor = vec3(0.0);
      for (int i = 0; i < ns; i++){ vec3 k = tetra(i); nor += k * de(p + k * hh, nt); }
`;
ALT_TAILS.m1 = ALT_PRE + 'nor = gGrad;' + ALT_SETTLE + ALT_POST;
ALT_TAILS.m2 = ALT_PRE + ALT_SLOPE + ALT_SETTLE + ALT_POST;
ALT_TAILS.m3 = ALT_PRE + 'nor = gGrad;' + ALT_LIGHT + ALT_POST;
