// The same program for every pair of numbers the two programs above were not written for (round 29): the two spheres
// cut into each other (top < 1 + rho), or the second sphere lies between 1/2 and 1 of the first, so that its copies at
// neighbouring whole numbers cut into each other. A text of its own, under its own key in the cache ('balls3':
// sceneWant in 40-render.js), so that the two programs above stay exactly what they were. The recipe and "best" are
// the same lines. What is new is "free", the length that is certainly free of balls at the place m where the recipe
// ends OUTSIDE. Each piece was put to the recipe alone on a fine grid, and to the true distance taken from that grid,
// before it was built in (out/r29/free/mk/kit29.py, proto.py; the numbers are in out/r29/free/NOTES.md).
//
// A. The two spheres apart or touching, the second between 1/2 and 1 of the first. The hulls of GL_BALLS_RHO hold as
//   they stand: nothing that grows on the bottom wall reaches higher than HB, nothing on the top wall hangs lower
//   than HT, and a bud that does not hang at a whole number is the image, by the second sphere's inversion, of
//   something that hangs OUTSIDE that sphere, so it is no deeper than rho^2 HT whatever rho is. The top wall inside
//   the cell is covered by the second sphere, so "the rest" is the part of its slab inside that sphere (rT = rho).
//   The spindle holds too: inside the middle cell only the first and the second sphere act, whatever the copies do.
//   In place of the side spindle there is the side ring of C below.
//
// B. The two spheres cut into each other. Then the hulls are gone, and what is used instead is this.
//   The verdict of the recipe is the same on both sides of a sphere surface: a point just inside the first sphere is
//   carried to its mirror image just outside and goes on from there, and the same for the second sphere outside the
//   first. It is also its own mirror image in every wall of the cell. So seen from m (in the middle cell, between
//   the walls, outside both spheres) every ball other than the two walls lies inside the first sphere or inside the
//   second, in the middle cell (a ball beyond a wall of the cell has a twin on this side that is nearer).
//   Looking through a sphere. What lies inside the first sphere is the mirror image of what lies outside it. So the
//   first sphere's inversion is applied to m although m is outside ("a round that does not count"), with DF and W
//   carried along as in a real round. There the point is inside the first sphere and everything that counts is
//   outside it: the two walls (kpearl gives the true distance; the top wall is the first bud behind the mirror, a
//   ball of the picture that the recipe's own chain never meets), the second sphere and its copies, each in its
//   own cell, and (square grid) the copies of the first sphere on the diagonals. The smaller of the distances to
//   those, or the distance to the first sphere's own surface from inside where that is the longer, is a room, and
//   it is carried back with e L / ((L + e) DF). The same through the second sphere. The smaller of the two rooms
//   is free of balls, and it is zero only on the circles where two spheres cross.
//   Balls that every move carries onto themselves. A ball that crosses both spheres squarely is carried onto itself
//   by both inversions; if it lies in the middle cell, or its centre lies on a wall of the cell (or on an upright
//   edge) and it reaches no other wall, the slides carry it onto itself as well. A point in such a ball never leaves
//   it, so if the ball lies between the two walls nothing in it is ever INSIDE: the whole ball is free. These balls
//   have their centres at the height zm of the circle where the two spheres cross, and
//   radius^2 = (distance of the centre from the middle line)^2 - q0^2, q0 the radius of that circle. Used here:
//   the ring round the circle (all such balls that reach 1/2 from the middle line; the spindle's formula with
//   d2 = -q0^2), the ball centred on the wall of the cell that m leans towards (as far along the wall as the cell
//   lets it), and the ball centred on the nearest upright edge of the cell. In the flat picture the round holes
//   ARE these balls, so there the room is the true distance to the rim of the hole.
// C. The side ring. Where rho > 1/2 the second sphere and its copy at the next whole number cross in a circle that
//   stands in the wall of the cell, and beside it the room of B is zero although nothing is near. Both inversions
//   carry every ring round that circle onto itself and the top wall onto itself; the half ring under the wall holds
//   no ball as long as it stays clear of the first sphere and of its copy (w <= wA below) and inside the two cells
//   (|across| <= clip). The side spindle's formula with c2 = 1/4 - rho^2 < 0.
// D. The depth of the search. A point that is still undecided when the rounds run out counts as INSIDE, and the
//   rooms of B and C say nothing about that: they are rooms of the object at endless depth. Where the two spheres
//   cut into each other the holes of the picture are made of many mirror images of one small piece, one round of
//   the search apart, and with the dial at 16 the far side of a hole is still undecided: the hole comes out smaller
//   than it is. So those rooms are made smaller by the rounds the search had left when it ended: none at all with
//   fewer left than the fan round the crossing circle has pieces (pi / the angle between the spheres), and from
//   there on the share 1 - exp(-rhoT (left - fan)), rhoT the size of one piece as the hole measures it. With no
//   round left only the two sphere surfaces themselves are trusted. This part is fitted to the reference, not
//   proved (out/r29/free/NOTES.md says what was measured). Where the spheres are apart (A) nothing is taken off,
//   as in the two programs above.
// E. The Drawing radius. With these pairs of numbers the far distance is often INSIDE, and the 3D picture is then
//   one lump as large as the Drawing radius (ballsTrouble says so). Nothing beyond the Drawing radius is drawn, but
//   the distance knew nothing of it: the skin of the lump lay inside the solid, no light reached it and it came out
//   black. So for every query of the 3D picture (gPix > 0: the ray, its slope, its shadow) the solid ends at the
//   Drawing radius: the larger of the distance above and (distance from the middle - Drawing radius). The lump then
//   has a round skin that is lit like any other. The 2D view and a 3D model (gPix = 0) are not touched, and neither
//   is the twin in JavaScript, which does not know the picture.
const GL_BALLS_FREE = `
const bool ORBIT_SCENE = false;
uniform float uBT, uBRho; uniform int uBGrid;
const float BALLS_K2 = ${BALLS_K2.toFixed(4)};
float kpearl(float h, float D, float kk){ return h > 0.0 ? 2.0 * h / (1.0 + sqrt(1.0 + kk * h * max(D, 0.0))) : h; }
// the whole number of the grid nearest to q (what the slide takes away)
vec2 bnear(vec2 q){
  if (uBGrid == 2) return vec2(floor(q.x + 0.5), 0.0);
  if (uBGrid == 0) return floor(q + 0.5);
  float b0 = floor(q.y / 0.8660254038 + 0.5), bd = 1e30;
  vec2 best = vec2(0.0);
  for (int j = -1; j <= 1; j++){
    float b = b0 + float(j), a = floor(q.x + 0.5 * b + 0.5);
    vec2 s = vec2(a - 0.5 * b, 0.8660254038 * b), w = q - s;
    float d = dot(w, w);
    if (d < bd){ bd = d; best = s; }
  }
  return best;
}
// the k-th whole number round the middle one: 0 the middle itself, then the ones next to it, then (square grid) the
// four on the diagonals
vec2 bround(int k){
  if (k == 0) return vec2(0.0);
  if (uBGrid == 2) return vec2(k == 1 ? 1.0 : -1.0, 0.0);
  if (uBGrid == 0) return k == 1 ? vec2(1.0, 0.0) : k == 2 ? vec2(-1.0, 0.0) : k == 3 ? vec2(0.0, 1.0) : k == 4 ? vec2(0.0, -1.0)
    : vec2(k < 7 ? 1.0 : -1.0, k == 5 || k == 7 ? 1.0 : -1.0);
  float a = float(k - 1) * 1.0471975512;
  return vec2(cos(a), sin(a));
}
// a length that is no longer than the distance to the cell of a whole number (d: the point less that number)
float bcell(vec2 d){
  if (uBGrid == 2) return max(abs(d.x) - 0.5, 0.0);
  if (uBGrid == 0) return length(max(abs(d) - 0.5, 0.0));
  return max(max(abs(d.x), max(abs(0.5 * d.x + 0.8660254038 * d.y), abs(0.5 * d.x - 0.8660254038 * d.y))) - 0.5, 0.0);
}
// a room e at the place z, carried back to the picture
float bback(float e, vec3 z, vec3 W, float DF){ float L = length(z - W), x = max(e, 0.0); return x * L / ((L + x) * DF); }
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0); gOnTrap = false;
  float top = 2.0 * uBT, rr = uBRho * uBRho;
  bool apart = top - 1.0 - uBRho >= -1e-6;
  // A: the two fixed points on the middle line, the two hull balls and the spindle (see above GL_BALLS_RHO)
  float sD = max(top - 1.0 - uBRho, 0.0) * (top - 1.0 + uBRho) / top, sQ = sqrt(sD * (sD + 4.0));
  float HB = 1.0 / (1.0 + 0.5 * (sD + sQ)), HT = rr / (top - HB), hzm = 1.0 + 0.5 * sD, d2 = 0.25 * sD * (sD + 4.0);
  float restB = uBGrid == 0 ? 0.5 * HB : uBGrid == 1 ? HB / 3.0 : 0.25 * HB, restT = rr * HT;
  float rT = min(uBRho, 2.0 * rr / (1.0 + sqrt(max(1.0 - 4.0 * rr, 0.0))) + restT);
  float sw = min(0.5, top - hzm + uBRho), sa = (sw * sw - d2) / (2.0 * sw), sR = (sw * sw + d2) / (2.0 * sw);
  // C: the side spindle (rho <= 1/2) or the side ring (rho > 1/2)
  float tc2 = 0.25 - rr, tK = top * top - 1.0 + rr, tdisc = tK * tK + 4.0 * (top * top - 1.0) * tc2;
  float tlim = uBGrid == 2 ? 1e9 : uBGrid == 0 ? 0.5 : 0.2886751346, tclip = 1e9;
  float tw = (tK + sqrt(max(tdisc, 0.0))) / (2.0 * (top + 1.0));
  bool sideOn = tdisc >= 0.0;
  // (asked of rho itself, not of its square: at exactly 1/2 the card's rounding must not choose)
  bool upto = uBRho <= 0.5;
  if (upto) tw = min(tw, min(tlim, (uBGrid == 1 ? 0.8660254038 : 1.0) - uBRho));
  else { sideOn = sideOn && tw * tw > -tc2 * 1.0000001; tclip = tlim * -tc2 / (tw * tw); }
  sideOn = sideOn && tw > 0.0;
  float ta = (tw * tw - tc2) / (2.0 * tw), tR = (tw * tw + tc2) / (2.0 * tw);
  // B: the circle where the two spheres cross (height zm, radius q0), the ring round it, the balls on the walls and
  // on the upright edges of the cell
  float zm = (top * top + 1.0 - rr) / (2.0 * top), dd = zm * zm - 1.0, q0 = sqrt(max(-dd, 0.0)), hmin = min(zm, top - zm);
  float rw = min(0.5, top - zm + uBRho), ra = (rw * rw - dd) / (2.0 * rw), rR = (rw * rw + dd) / (2.0 * rw);
  bool ringOn = rw * rw + dd > 0.0;
  // (a ball centred on a wall of the cell stays under the top wall only while its centre is no further along the
  //  wall than sqrt(rho^2 - 1/4): so there is none for a second sphere of half the first's size or less)
  float slab = rr - 0.25;
  float ylim = slab > 1e-5 ? min(uBGrid == 0 ? -dd : uBGrid == 1 ? 2.0 * (q0 - 0.4330127019) : 1e9, sqrt(slab)) : -1.0;
  float er2 = (uBGrid == 0 ? 0.5 : 1.0 / 3.0) + dd;
  float edge = uBGrid != 2 && er2 > 0.0 && sqrt(max(er2, 0.0)) <= min(hmin, uBGrid == 0 ? 1.0 : 0.5) ? sqrt(max(er2, 0.0)) : -1.0;
  // D: the depth of the search
  float gv = q0 < 0.5 ? 0.5 : uBGrid == 0 ? 0.7071067812 : uBGrid == 1 ? 0.5773502692 : q0 + 0.25;
  float kap = sqrt(max(gv - q0, 1e-9) / (gv + q0)), rhoT = log((1.0 + kap) / (1.0 - kap));
  // (a hair under, so that rounding does not decide where the fan has a whole number of pieces)
  float fan = 3.1415926536 / max(3.1415926536 - acos(clamp((1.0 + rr - top * top) / (2.0 * uBRho), -1.0, 1.0)), 1e-6) - 1e-3;
  float fanS = !upto ? 3.1415926536 / max(3.1415926536 - acos(clamp((2.0 * rr - 1.0) / (2.0 * rr), -1.0, 1.0)), 1e-6) - 1e-3 : 0.0;
  // the frame: one sphere inversion about (k^2 / 2, 0, 0), which is the point (0, 0, 1) of the object's own space
  vec3 u = vec3(p.y, p.z, p.x - 0.5 * BALLS_K2);
  float DF = BALLS_K2 / max(dot(u, u), 1e-20), it = 0.0, best = 1e9, free = 0.0;
  vec3 z = vec3(0.0, 0.0, 1.0) + DF * u, W = vec3(0.0, 0.0, 1.0);
  // The landing length (see gLand in GL_HEAD); none while the trap alone is the solid, because then the balls are
  // not in the picture. The distances here are lengths of the picture already, so it is used as it comes.
  bool walls = uTrapSolid < 0.5 || uTrapSolid > 1.5, inside = false, decided = false;
  float land = walls ? gLand : 0.0;
  trapStart();
#if TRAP_SOLIDS
  bool trapSolid = uTrapSolid > 0.5;
  float bestT = 1e9;
#endif
  for (int i = 0; i < uIter; i++){
    vec2 n = bnear(z.xy);
    z.xy -= n; W.xy -= n;
    // the point as the trap sees it: x along the chain (0 half-way between the walls), z out of the flat plane
    vec3 zw = z - W, tv = vec3(z.z - uBT, z.x, z.y);
    float L2 = max(dot(zw, zw), 1e-30), kk = 4.0 / L2, hb = z.z, ht = top - z.z;
    float cand = min(kpearl(hb, W.z, kk), kpearl(ht, top - W.z, kk)) / DF;
    best = min(best, cand); it = float(i);
    // The trap as a solid: every point whose chain, from round uTrapSkip on, comes within uTrapW of the trap shape.
    // The length is carried back to the picture the way "free" is.
#if TRAP_SOLIDS
    if (trapSolid && i >= uTrapSkip){
      float dq = trapDist(tv), et = dq - uTrapW, L = sqrt(L2);
      float sc = (et > 0.0 ? et * L / (L + et) : et) / DF;
      if (sc < bestT){ bestT = sc; gTouch = vec4(tv - uTrapC, dq); gTouchIt = it; gTouchS = sc; gTouchStr = DF; }
    }
#endif
    // a hit's trap colour: the search is over at the first round that lands within the landing length of a ball,
    // and that point is fed to the trap as a point of the wall itself
    bool landed = land > 0.0 && cand < land;
    if (landed){ tv.x = hb < ht ? -uBT : uBT; free = 1e9; }
    trapAdd(tv, it); gLast = tv;
    if (landed || hb < 0.0 || ht < 0.0){ inside = hb < 0.0 || ht < 0.0; decided = true; break; }
    vec3 zt = vec3(z.xy, z.z - top);
    float rb = dot(z, z), rt = dot(zt, zt);
    if (rb < 1.0){
      float s = 1.0 / max(rb, 1e-20);
      z *= s; W /= max(dot(W, W), 1e-20); DF *= s;
    } else if (rt < rr){
      float s = rr / max(rt, 1e-20);
      vec3 Wt = vec3(W.xy, W.z - top);
      z = vec3(0.0, 0.0, top) + zt * s; W = vec3(0.0, 0.0, top) + Wt * (rr / max(dot(Wt, Wt), 1e-20)); DF *= s;
    } else {
      // OUTSIDE, for good. How much room is certain here (see above this program).
      float q = length(z.xy);
      // the whole number next to the middle one that the point leans towards, along it and across it
      float al = abs(z.x), ac = z.y;
      if (uBGrid == 0 && abs(z.y) > al){ al = abs(z.y); ac = z.x; }
      if (uBGrid == 1){
        float h1 = abs(0.5 * z.x + 0.8660254038 * z.y), h2 = abs(0.5 * z.x - 0.8660254038 * z.y);
        if (h1 > al){ al = h1; ac = 0.5 * z.y - 0.8660254038 * z.x; }
        if (h2 > al){ al = h2; ac = 0.5 * z.y + 0.8660254038 * z.x; }
      }
      // C: the side spindle or the side ring
      float side = -1.0;
      if (sideOn){
        float tl = al - 0.5, tq = length(vec2(ac, ht));
        side = min((tc2 - tl * tl + tq * (2.0 * ta - tq)) / (tR + length(vec2(tl, tq - ta))), tclip - abs(ac));
      }
      if (apart){
        // A: the hulls
        float cb = length(vec3(z.xy, hb - 0.5 * HB)) - 0.5 * HB, ct = length(vec3(z.xy, ht - 0.5 * HT)) - 0.5 * HT;
        float lo = uBGrid == 2 ? length(vec2(z.y, hb)) : hb, hi = uBGrid == 2 ? length(vec2(z.y, ht)) : ht;
        float e = max(min(min(cb, ct), min(lo - restB, max(hi - restT, sqrt(rt) - rT))), 0.0), dz = z.z - hzm;
        if (d2 < 3.0) e = max(e, (d2 + q * (2.0 * sa - q) - dz * dz) / (sR + length(vec2(q - sa, dz))));
        free = bback(max(e, side), z, W, DF);
      } else {
        // B: looking through the first sphere (zA) and through the second (zB)
        float left = float(uIter - 1 - i), sA = 1.0 / max(rb, 1e-20), sB = rr / max(rt, 1e-20);
        vec3 C = vec3(0.0, 0.0, top), zA = z * sA, WA = W / max(dot(W, W), 1e-20), Wt = W - C;
        vec3 zB = C + zt * sB, WB = C + Wt * (rr / max(dot(Wt, Wt), 1e-20)), dA = zA - WA, dB = zB - WB;
        float DFA = DF * sA, DFB = DF * sB;
        float bud = min(kpearl(top - zA.z, top - WA.z, 4.0 / max(dot(dA, dA), 1e-30)) / DFA, kpearl(zB.z, WB.z, 4.0 / max(dot(dB, dB), 1e-30)) / DFB);
        float eA = 0.5, eB = 0.5;
        int nc = uBGrid == 2 ? 3 : uBGrid == 0 ? 9 : 7;
        for (int k = 0; k < 9; k++){
          if (k >= nc) break;
          vec2 c = bround(k), a2 = zA.xy - c, b2 = zB.xy - c;
          float fa = bcell(a2), fb = bcell(b2);
          eA = min(eA, max(length(vec3(a2, zA.z - top)) - uBRho, fa));
          if (uBGrid == 0 && k >= 5) eA = min(eA, max(length(vec3(a2, zA.z)) - 1.0, fa));
          eB = min(eB, max(length(vec3(b2, zB.z)) - 1.0, fb));
          if (k >= 1) eB = min(eB, max(length(vec3(b2, zB.z - top)) - uBRho, fb));
        }
        eA = max(eA, 1.0 - length(zA)); eB = max(eB, uBRho - length(zB - C));
        free = left < 1.0 ? min(bback(sqrt(rb) - 1.0, z, W, DF), bback(sqrt(rt) - uBRho, z, W, DF)) : min(bback(eA, zA, WA, DFA), bback(eB, zB, WB, DFB));
        // the ring round the crossing circle, the ball on the wall, the ball on the upright edge
        float dz = z.z - zm;
        float ring = ringOn ? (dd + q * (2.0 * ra - q) - dz * dz) / (rR + length(vec2(q - ra, dz))) : -1.0, whole = ring;
        if (ylim >= 0.0){
          float yc = clamp(ac, -ylim, ylim), r2 = 0.25 + yc * yc + dd;
          if (r2 > 0.0) whole = max(whole, sqrt(r2) - length(vec3(al - 0.5, ac - yc, dz)));
        }
        if (edge > 0.0){
          vec2 ev = vec2(z.x < 0.0 ? -0.5 : 0.5, z.y < 0.0 ? -0.5 : 0.5);
          if (uBGrid == 1){ float a0 = (floor(atan(z.y, z.x) / 1.0471975512) + 0.5) * 1.0471975512; ev = vec2(cos(a0), sin(a0)) * 0.5773502692; }
          whole = max(whole, edge - length(vec3(z.xy - ev, dz)));
        }
        // D: the depth of the search
        float wholeP = left >= fan ? bback(whole, z, W, DF) * (1.0 - exp(-rhoT * (left - fan)))
          : left >= 0.5 * fan + 1.0 && ringOn ? bback(min(ring, length(vec2(q - q0, dz))), z, W, DF) : -1.0;
        float sideP = bback(side, z, W, DF) * (!upto ? 1.0 - exp(-rhoT * max(left - fanS, 0.0)) : max(left - 1.0, 0.0) / (left + 8.0));
        free = max(free, max(wholeP, sideP));
        if (left >= 1.0) best = min(best, bud);
      }
      decided = true; break;
    }
  }
  // In the 3D view the count is reported 8 rounds high, as the other Kleinian program does (see kde).
  gIt = uFlat > 0.5 ? it : it + 8.0;
  // undecided when the rounds ran out: that counts as inside, a hair deep
  // (the hold: two thresholds while a ray takes half of the estimate or less, so that it goes on a threshold a step;
  //  with a longer ray step less, down to one and a quarter)
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
  // E (see above this program): in the 3D picture the solid ends at the Drawing radius
  if (gPix > 0.0) d = max(d, length(p) - (uBound > 0.0 ? uBound : 8.0));
  // (the trap solid: as in GL_BALLS, the page never asks this group for one)
#if TRAP_SOLIDS
  if (trapSolid && uTrapSolid < 1.5) bestT = min(bestT, gPix > 0.0 ? max(abs(d), 2.0 * uDetail * gPix) : 0.3);
  gOnTrap = trapSolid && (uTrapSolid < 1.5 || bestT < d);
  if (gOnTrap) d = bestT;
#endif
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
