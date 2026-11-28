// The lab's own approaches, written as steps of the custom approach (12-custom.js): the rest of the list that
// CU_STARTS begins. Each gives the numbers of the approach it is named after, with that approach's dials at their
// starting values; a dial becomes a slider step. `lab` is the approach's id, `q` the dials the rule stands for where
// they differ from the approach's own start, and `say` a sentence for the moment the rule is loaded. Three of the
// approaches fold c as they fold the point (their cmap in the shader): their rules have a fold or a mirror set to
// work on c, which stands among the steps taken once before the iterations, and so does a slider that step reads (once).
// Where the lab's picture lets the orbits beside a point borrow the point's own value, the rule says same( ).
// A rule that is longer than a few lines is the approach's arithmetic line for line (see MATH in 10-approaches.js).
// Two approaches draw their picture from several orbits at once (either, mirrorsblend). Steps follow one orbit, so
// their rules are the orbit the page itself follows for them, and `say` tells what the picture adds.
{
  const F = text => ['formula', { text }], num = (name, value, min, max) => ['slider', { name, value: String(value), min: String(min), max: String(max) }];
  const once = step => [step[0], step[1], 'pre'];
  const onePlane = [['len'], ['lon'], ['merc']];
  // the grid of Parts on a doubling grid: the flat point u under the middle of the box that holds the point
  const grid = finer => [F('m = max(2, round(abs(n)))'), F('el = abs(z.phi)'),
    F(`a = pi/2*m^(-floor(log(pi/2/el)/log(m)) - 1${finer})`),
    F('u = if(el < 0.00002, flat(z), vec(cos(a*floor(z.theta/a + 0.5)), sin(a*floor(z.theta/a + 0.5)), 0)*exp(a*floor(log(z.radius)/a + 0.5)))')];
  // the rotation and scaling that fits the flat power at u, and the Möbius move that fits its bend as well
  const fitTurn = [F('pw = cpow(u, n)'), F('b = cpow(u, n - 1)*n'), F('o = cmul(b, flat(z) - u)'), F('z = vec(pw.x + o.x, pw.y + o.y, len(b)*z.z)')];
  const fitBend = [F('s = 2/(n - 1)'), F('pw = cpow(u, n)'), F('g = cmul(pw, u)*(n*s*s)'), F('q = flat(z) - u*(1 + s)'), F('dd = max(dot(q, q) + z.z*z.z, 1e-30)'),
    F('o = cmul(g, vec(q.x, -q.y, 0))'), F('z = vec((1 - n*s)*pw.x - o.x/dd, (1 - n*s)*pw.y - o.y/dd, len(g)*z.z/dd)')];
  // one pull at the plane the orbit carries (Pulled plane): by a thing at (y, z) with the weight k
  const pull = (i, y, zz, k) => [F(`m${i} = min(${k}(${y}*${y} + ${zz}*${zz}), 1e18)`), F(`p${i} = atan2(w.y, w.x)`),
    F(`t${i} = atan2(2*${y}*${zz}, ${y}*${y} - ${zz}*${zz}) - p${i}`), F(`t${i} = t${i} - 2*pi*floor(t${i}/(2*pi) + 0.5)`),
    F(`w = w + vec(cos(p${i} + t${i} - ease*sin(t${i})), sin(p${i} + t${i} - ease*sin(t${i})), 0)*m${i}`)];
  // the caps of Kleinian squaring, for the direction d: the answer is h
  const caps = [F('m = max(2, round(abs(n)))'), F('gap = pi/(m + 1)'), F('ang = mod(atan2(d.y, d.x), 2*pi)'),
    F('mid = (2*min(floor(ang/(2*gap)), m) + 1)*gap'), F('a = vec(cos(mid), sin(mid), 0)'), F('cc = a/cos(gap)'), F('e = d - cc'), F('s = tan(gap)^2/dot(e, e)'),
    F('h = if(dot(d, a) > cos(gap), vec(cc.x + s*e.x, -(cc.y + s*e.y), s*e.z), vec(d.x, -d.y, d.z))')];
  // one step of Newton for the square pillow's beta
  const newton = F('b = if((b*(1 + b)^2 - xx*b - yy*(1 + b)^2 > 0)*((1 + b)*(1 + 3*b - 2*yy) - xx > 0), max(b - (b*(1 + b)^2 - xx*b - yy*(1 + b)^2)/((1 + b)*(1 + 3*b - 2*yy) - xx), 0), b)');
  const times = (k, step) => Array.from({ length: k }, () => step);
  // one step of Newton for Four to one, two planes alike: t is the tangent of half the changed angle from the x-axis
  const newtonT = F('t = if(4*s*t^3 + if(back, 6*co*t*t, 2*co) > 1e-20, t - (s*t^4 + 2*co*if(back, t^3, t) - s)/(4*s*t^3 + if(back, 6*co*t*t, 2*co)), t)');
  // The squaring step of the two caps entries, for the number a (a point of the flat plane): f4kPower, line for line.
  const newtonPsi = F('psi = min(psi - (psi + 3*atan2(rho*sin(psi), 1 - rho*cos(psi)) - ta)/(1 + 3*rho*(cos(psi) - rho)/(1 - 2*rho*cos(psi) + rho*rho)), ta)');
  const capsStep = [F('rho = len(a)'), F('r = z.radius'), F('rxy = len(flat(z))'), F('eu = if(rxy > 0, flat(z)/max(rxy, 1e-30), vec(1, 0, 0))'),
    F('et = cmul(cmul(cmul(eu, eu), eu), vec(a.x, -a.y, 0)/max(rho, 1e-30))'), F('tau = atan2(et.y, et.x)'), F('ta = abs(tau)'),
    F('psi = max(0, ta - 3*asin(rho))'), ...times(6, newtonPsi), F('slow = 1/(1 + 3*rho*(cos(psi) - rho)/(1 - 2*rho*cos(psi) + rho*rho))'),
    F('m = log((r + abs(z.z))/max(rxy, 1e-20*r))'), F('w = exp(-(m/0.6)^2)'), F('b = if(tau < 0, ta - psi, psi - ta)/3*w'),
    F('tw = cmul(eu, vec(cos(b), sin(b), 0))'), F('rh = exp(-m*(1 + (slow - 1)*w))'), F('up = z.z > 0'),
    F('ee = vec(rh*tw.x, if(up, -rh, rh)*tw.y, 0)'), F('e3 = cmul(cmul(ee, ee), ee)'), F('ga = vec(a.x, if(up, -a.y, a.y), 0)'), F('ge = cmul(vec(ga.x, -ga.y, 0), e3)'),
    F('fa = e3 - ga'), F('fb = cmul(ee, vec(1 - ge.x, -ge.y, 0))'), F('nu = if(up, fb, fa)'), F('de = if(up, fa, fb)'), F('k = r*r/(dot(nu, nu) + dot(de, de))'),
    F('z = if(z.z == 0, vec(z.x*z.x - z.y*z.y, 2*z.x*z.y, 0), if(rho > 0, vec(2*k*(nu.x*de.x + nu.y*de.y), 2*k*(nu.y*de.x - nu.x*de.y), k*(dot(nu, nu) - dot(de, de))), vec(z.x*z.x - z.y*z.y, 2*z.x*z.y, 2*r*z.z)*(r*r/(r*r + z.z*z.z))))'), ['addc']];
  const only2 = 'These steps are the entry at the power 2. At any other power the entry itself is Sphere inversions, one plane.';
  CU_STARTS.splice(CU_STARTS.findIndex(s => !s.lab), 0,
    { name: 'Blended planes', lab: 'softfold', steps: [num('planes', 2, 1, 8), num('blend', 0.25, 0, 0.49),
      F('d0 = unit(z)'), F('fl = if(max(d0.z < 0, (d0.z == 0)*(d0.y < 0))*(planes > 1.5), -1, 1)'), F('d = vec(d0.x, d0.y*fl, d0.z*fl)'),
      F('rho = len(vec(0, d.y, d.z))'), F('w = pi/round(planes)'), F('on = (planes > 1.5)*(d.z != 0)*(rho > 1e-15)'),
      F('uu = atan2(d.z, d.y)/w'), F('t = if(on, uu - min(floor(uu), round(planes) - 1), 0)'),
      F('qq = clamp((t - blend)/(1 - 2*blend), 0, 1)'), F('s = if(on, qq*qq*(3 - 2*qq), 0)'),
      F('cj = if(on, (d.y*cos(t*w) + d.z*sin(t*w))/rho, 1)'), F('sj = if(on, (d.z*cos(t*w) - d.y*sin(t*w))/rho, 0)'),
      F('pa = if(on, vec(d.x, rho*cos(t*w), rho*sin(t*w)), d)'), F('aa = sph(1, lon(pa)*n, asin(tanh(n*atanh(pa.z))))'),
      F('pb = vec(d.x, rho*cos(t*w - w), rho*sin(t*w - w))'), F('bb = rot(sph(1, lon(pb)*n, asin(tanh(n*atanh(pb.z)))), vec(1, 0, 0), w)'),
      F('co = clamp(dot(aa, bb), -1, 1)'), F('e = bb - aa*co'), F('om = atan2(len(e), co)*s'), F('dd = aa*cos(om) + e*(sin(om)/max(len(e), 1e-30))'),
      F('z = vec(dd.x, fl*(dd.y*cj - dd.z*sj), fl*(dd.y*sj + dd.z*cj))*z.radius^n'), ['addc']] },
    { name: 'Bulbs about the axis', lab: 'axisbulb', steps: [num('bulbs', 1, -4, 4), num('wob', 0.2, -1, 1), num('reach', 45, 1, 90), ['quatpow'],
      F('rho = len(vec(0, z.y, z.z))'), F('co = z.y/rho'), F('si = z.z/rho'), F('t = clamp(rho/(z.radius*sin(rad(reach))), 0, 1)'),
      F('ang = atan2(si, co)*round(bulbs) + wob*t*t*(3 - 2*t)*2*(2*co*si)*(co*co - si*si)'),
      F('z = if(rho > 0, vec(z.x, rho*cos(ang), rho*sin(ang)), z)'), ['addc']] },
    { name: 'Pillow (the smooth layout, power 2)', lab: 'pillow', q: { layout: 1 }, only2: true, say: 'These steps are the second layout of the Pillow entry, at the power 2. Its first layout, the creased one, is not written as steps.', steps: [
      F('d = unit(z)'), F('w = vec(d.x, d.y, 0)/(1 + abs(d.z))'), F('w3 = cpow(w, 3)'), F('nu = w3*2 - vec(1, 0, 0)'), F('de = cmul(w, vec(2, 0, 0) - w3)'),
      F('z = vec(2*dot(nu, de), 2*(nu.y*de.x - nu.x*de.y), if(d.z > 0, dot(de, de) - dot(nu, nu), dot(nu, nu) - dot(de, de))*(d.z != 0))*(z.radius^2/(dot(nu, nu) + dot(de, de)))'), ['addc']] },
    { name: 'Quaternions, 4D (the slice it starts with)', lab: 'quat4', say: 'With its dials at their start this entry is the quaternion power: its slice of four dimensions is the three you see. The dials that move the slice are not part of these steps.', steps: [['quatpow'], ['addc']] },
    { name: 'Rotor square (geometric algebra)', lab: 'rotor', steps: [['len'], ['lat', { axis: 'vec(0, 0, 1)', from: 'axis' }], ['addc']] },
    { name: 'Rotor square with a frame', lab: 'rotorframe', steps: [
      F('q = quat(cos(z.phi/2)*cos(z.theta/2), sin(z.phi/2)*sin(z.theta/2), -sin(z.phi/2)*cos(z.theta/2), cos(z.phi/2)*sin(z.theta/2))'),
      F('z = rot(vec(1, 0, 0), q^n)*z.radius^n'), ['addc']] },
    { name: 'Kleinian squaring, one plane', lab: 'kleinsq', steps: [F('d = unit(z)'), ...caps, F('z = h*z.radius^n'), ['addc']] },
    { name: 'Kleinian squaring, two planes', lab: 'kleinsq2', steps: [F('sw = abs(unit(z).z) > abs(unit(z).y)'), F('d = if(sw, vec(unit(z).x, unit(z).z, unit(z).y), unit(z))'), ...caps,
      F('z = if(sw, vec(h.x, h.z, h.y), h)*z.radius^n'), ['addc']] },
    { name: 'Square pillow (power 2)', lab: 'sqpillow', only2: true, say: 'These steps are the Square pillow at the power 2: four of their numbers are the layout worked out for that power.', steps: [
      F('den = z.radius + abs(z.z)'), F('px = z.x/den'), F('py = z.y/den'), F('xx = 4*px*px'), F('yy = py*py'), F('c1 = 1 - xx - 2*yy'), F('a1 = 2 - yy'), F('s1 = sqrt(c1*c1 + 4*a1*yy)'),
      F('b = min(1, min(px*px + yy, if(c1 >= 0, 2*yy/(c1 + s1), (s1 - c1)/(2*a1))))'), newton, newton, newton, newton, newton,
      F('beta = if(yy > 0, b, max(0, 2*abs(px) - 1))'), F('bb = sqrt(beta)'),
      F('cn = if(bb > 0, 2*px/(1 + beta), clamp(2*px, -1, 1))'), F('sn = if(bb > 0, py/bb, sqrt(max(1 - cn*cn, 0)))'), F('ln = sqrt(cn*cn + sn*sn)'),
      F('t = if(z.z > 0, 0.5 - asinh(bb*0.38714057818890835)/2.268416057338147, asinh(bb*3.7115963892637227)/6.066845545340116)'),
      F('wr = 2*t - floor(2*t)'), F('back = wr > 0.5'), F('t2 = if(back, 1 - wr, wr)'), F('north = t2 >= 1/3'),
      F('b2 = clamp(if(north, sinh(2.268416057338147*(0.5 - t2))/0.38714057818890835, sinh(6.066845545340116*t2)/3.7115963892637227), 0, 1)'),
      F('qx = (1 + b2*b2)/2*(cn*cn - sn*sn)/(ln*ln)'), F('qy = b2*if(back, 1, -1)*2*cn*sn/(ln*ln)'), F('q2 = qx*qx + qy*qy'),
      F('z = vec(2*qx, 2*qy, if(north, 1 - q2, q2 - 1))*(z.radius^n/(1 + q2))'), ['addc']] },
    { name: 'Turning plane, away', lab: 'turnaway', steps: [F('m = max(1, round(abs(n)))'), F('ang = atan2(z.z, z.y)'), F('psi = (1 - m)*(ang - sin(2*m*ang)/(2*m))'),
      F('z = rot(z, vec(1, 0, 0), -psi)'), ...onePlane, F('z = rot(z, vec(1, 0, 0), psi)'), ['addc']] },
    { name: 'Turning plane, along', lab: 'turnalong', steps: [F('m = max(1, round(abs(n)))'), F('ang = atan2(z.z, z.y)'), F('psi = ang - sin(2*m*ang)/(2*m)'),
      F('z = rot(z, vec(1, 0, 0), -psi)'), ...onePlane, F('z = rot(z, vec(1, 0, 0), psi)'), ['addc']] },
    { name: 'Wind, then square', lab: 'windsq', steps: [F('m = max(1, round(abs(n)))'), F('k = m + 1 - mod(m, 2)'), F('rho = len(vec(0, z.y, z.z))'), F('ang = atan2(z.z, z.y)'),
      F('g = k*ang - (k - 1)*sin(2*k*ang)/(2*k)'), F('z = vec(z.x, rho*cos(g), rho*sin(g))'), ...onePlane, ['addc']] },
    { name: 'Four to one, two planes alike (power 2)', lab: 'fourplanes', only2: true, say: only2, steps: [
      F('rho = len(vec(0, z.y, z.z))'), F('r = z.radius'), F('s = rho/r'), F('co = abs(z.x)/r'), F('back = z.x < 0'), F('h = s/max(2*co, 1e-30)'),
      F('t = min(1, if(back, h^(1/3), h))'), ...times(5, newtonT), F('l = sqrt(t*t + 1)'), F('sg = if(back, 1, t)/l'), F('cg = if(back, t, 1)/l'),
      F('cb = cg*cg - sg*sg'), F('sb = 2*sg*cg'), F('kk = 2*(1 - cb + cb*cb)/sqrt(sb*sb*(1 + cb)*(1 + cb) + 4*cb*cb)'),
      F('ey = z.y/max(rho, 1e-30)'), F('ez = z.z/max(rho, 1e-30)'), F('a = (1 - 1/kk)*(ey*ey - ez*ez)*ey*ez'),
      F('fy = ey*cos(a) + ez*sin(a)'), F('fz = ez*cos(a) - ey*sin(a)'), F('f2 = vec(fy*fy - fz*fz, 2*fy*fz, 0)'), F('k = 2*sg*cg*cg*cg'), F('s4 = sg*sg*sg*sg'),
      F('nu = vec(k*fy, k*fz, 0)'), F('de = vec(cg*cg*cg*cg - s4*(f2.x*f2.x - f2.y*f2.y), -2*s4*f2.x*f2.y, 0)'), F('m = r*r/(dot(nu, nu) + dot(de, de))'),
      F('z = if(z.z == 0, vec(z.x*z.x - z.y*z.y, 2*z.x*z.y, 0), if(z.y == 0, vec(z.x*z.x - z.z*z.z, 0, 2*z.x*z.z), vec(m*(dot(de, de) - dot(nu, nu)), 2*m*(nu.x*de.x + nu.y*de.y), 2*m*(nu.y*de.x - nu.x*de.y))))'), ['addc']] },
    { name: 'Four to one, caps flipped over (power 2)', lab: 'fourcaps', only2: true, say: only2, steps: [num('cap', 30, 0, 40),
      F('a = vec(tan(rad(clamp(cap, 0, 40))/2), 0, 0)'), ...capsStep] },
    { name: 'Four to one, caps placed by c (power 2)', lab: 'fourcapsc', only2: true, say: only2, steps: [num('cap', 30, 0, 51), num('crot', -90, -180, 180),
      F('k0 = tan(rad(clamp(cap, 0, 51))/2)'), F('a0 = cmul(vec(k0*cos(rad(crot)), k0*sin(rad(crot)), 0), flat(c))'),
      F('a = if(len(a0) > tan(rad(25.5)), a0*(tan(rad(25.5))/max(len(a0), 1e-30)), a0)'), ...capsStep] },
    { name: 'Along once, then one plane', lab: 'alongonce', steps: [F('m = max(1, round(abs(n)))'), F('ang = atan2(z.z, z.y)'), F('psi = if(count < 1.5, ang - sin(2*m*ang)/(2*m), 0)'),
      F('z = rot(z, vec(1, 0, 0), -psi)'), ...onePlane, F('z = rot(z, vec(1, 0, 0), psi)'), ['addc']] },
    { name: 'Pulled plane', lab: 'pulledplane', steps: [['keep', { name: 'w', start: 'vec(0.05, 0, 0)' }], num('ease', 0.7, 0, 1), num('cpull', 16, 0, 64),
      ...pull(1, 'c.y', 'c.z', 'cpull*'), ...pull(2, 'z.y', 'z.z', ''), F('psi = atan2(w.y, w.x)/2'),
      F('z = rot(z, vec(1, 0, 0), -psi)'), ...onePlane, F('z = rot(z, vec(1, 0, 0), psi)'), ['addc']] },
    { name: 'Sphere inversions, soft mirror', lab: 'softmirror', steps: [once(num('mir', 45, 45, 90)), once(num('soft', 20, 0, 45)), once(['softx', { on: 'c', angle: 'mir', soft: 'soft' }]), ['softx', { angle: 'mir', soft: 'soft' }], ...onePlane, ['addc']] },
    { name: 'Soft mirrors, doubling', lab: 'mirrorsdouble', steps: [once(num('soft', 2, 0, 45)), num('stop', 3, 1, 12), once(['softx', { on: 'c', angle: '45', soft: 'soft' }]),
      F('half = 2^(1 - clamp(count, 1, round(stop)))'), F('b = pi/4*half'), F('w = rad(soft)*half'), F('rho = len(vec(0, z.y, z.z))'),
      F('a = atan2(abs(z.z), abs(z.y))'), F('t = a - 2*b*floor(a/(2*b)) - b'), F('g = b - if(abs(t) >= w, abs(t), t*t/(2*w) + w/2)'),
      F('z = vec(z.x, if(z.y < 0, -1, 1)*rho*cos(g), if(z.z < 0, -1, 1)*rho*sin(g))'), ...onePlane, ['addc']] },
    { name: 'Sphere inversions, either side (one run of its choices)', lab: 'either', say: 'The lab’s picture of this entry asks every run of choices and keeps a point if any run keeps it. Steps follow one run: the slider run picks it, and run 0 never takes the mirror.', steps: [
      num('depth', 1, 0, 5), num('run', 0, 0, 31), F('on = (count - 1 < round(depth))*(mod(floor(round(run)/2^(count - 1)), 2) > 0.5)'),
      F('rho = len(vec(0, z.y, z.z))'), F('g = pi/4 - abs(atan2(abs(z.z), abs(z.y)) - pi/4)'),
      F('z = if(on*(z.z != 0)*(rho > 1e-20), vec(z.x, if(z.y < 0, -1, 1)*rho*cos(g), if(z.z < 0, -1, 1)*rho*sin(g)), z)'), ...onePlane, ['addc']] },
    { name: 'Blended mirrors, doubling (its mirrors, nothing blended)', lab: 'mirrorsblend', say: 'The lab’s picture of this entry runs two orbits beside each mirror and cross-fades them. Steps follow one orbit, so these are its mirrors kept sharp.', steps: [
      num('stop', 3, 1, 12), once(['softx', { on: 'c', angle: '45', soft: '0' }]),
      F('half = 2^(1 - clamp(count, 1, round(stop)))'), F('b = pi/4*half'), F('rho = len(vec(0, z.y, z.z))'),
      F('a = atan2(abs(z.z), abs(z.y))'), F('t = a - 2*b*floor(a/(2*b)) - b'), F('g = b - abs(t)'),
      F('z = vec(z.x, if(z.y < 0, -1, 1)*rho*cos(g), if(z.z < 0, -1, 1)*rho*sin(g))'), ...onePlane, ['addc']] },
    { name: 'Even pillow', lab: 'evenpillow', steps: [F('d = unit(z)'), F('rr = sqrt(2/(1 + sqrt(max(1 - 4*d.x*d.x*d.z*d.z, 0))))'), F('ca = clamp(rr*d.x, -1, 1)'), F('sl = clamp(rr*d.z, -1, 1)'),
      F('sa = if(d.y < 0, -1, 1)*sqrt(max(1 - ca*ca, 0))'), F('z = unit(vec(cos(atan2(sa, ca)*n), sin(atan2(sa, ca)*n)*cos(asin(sl)*n), sin(asin(sl)*n)))*z.radius^n'), ['addc']] },
    { name: 'Quaternion square, axis by step', lab: 'tiltstep', steps: [num('tilt0', 0, -90, 90), num('more', 90, -180, 180), F('tilt = tilt0 + (max(count, 1) - 1)*more'),
      ['rot', { angle: 'tilt' }], ['quatpow'], ['rot', { angle: '-n*tilt' }], ['addc']] },
    { name: 'All axes, nearest to upright', lab: 'nearaxis', steps: [F('u = unit(z)'), F('d = u - vec(1, 0, 0)'), F('m = unit(vec(0, 0, 1) - d*(d.z/dot(d, d)))'), F('s2 = 1 - m.x*m.x'),
      F('z = rot(u, m, atan2((m.z*u.y - m.y*u.z)/s2, (u.x - m.x*m.x)/s2)*(n - 1))*z.radius^n'), ['addc']] },
    { name: 'All axes, nearest to the last one', lab: 'lastaxis', steps: [['keep', { name: 'h', start: 'vec(0, 0, 1)' }], F('u = unit(z)'), F('d = u - vec(1, 0, 0)'),
      F('m = same(unit(h - d*(dot(h, d)/dot(d, d))))'), F('s2 = 1 - m.x*m.x'), F('h = m'),
      F('more = same(atan2((m.z*u.y - m.y*u.z)/s2, (u.x - m.x*m.x)/s2)*(n - 1))'), F('z = rot(u, m, more)*z.radius^n'), ['addc']] },
    { name: 'Parts on a doubling grid, turn and scale', lab: 'partsturn', steps: [...grid(''), ...fitTurn, ['addc']] },
    { name: 'Parts on a doubling grid, Möbius', lab: 'partsbend', steps: [num('finer', 0, 0, 6), ...grid(' - round(finer)'), ...fitBend, ['addc']] },
    { name: 'Parts on a square grid', lab: 'partssquare', steps: [F('hh = abs(z.z)'), F('sz = 2^floor(log(hh)/log(2))'),
      F('u = if(hh < 0.00001*(len(flat(z)) + 0.00001), flat(z), vec(sz*(floor(z.x/sz) + 0.5), sz*(floor(z.y/sz) + 0.5), 0))'), ...fitTurn, ['addc']] },
    { name: 'Two points side by side (power 2)', lab: 'twins', only2: true, say: only2, steps: [F('a = vec(0.5, 0, 0) - cpow(vec(0.25, 0, 0) - flat(c), 0.5)'),
      F('u = if(dot(a, a) > 0.000000000001, cmul(a, a)/dot(a, a), vec(1, 0, 0))'), F('s = cmul(flat(z), flat(z))'),
      F('z = vec(s.x - z.z*z.z*u.x, s.y - z.z*z.z*u.y, 2*len(flat(z))*z.z)'), ['addc']] },
    { name: 'Two points side by side, round (power 2)', lab: 'twinsround', only2: true, say: only2, steps: [F('a = vec(0.5, 0, 0) - cpow(vec(0.25, 0, 0) - flat(c), 0.5)'),
      F('u = if(dot(a, a) > 0.000000000001, cmul(a, a)/dot(a, a), vec(1, 0, 0))'), F('s = cmul(flat(z), flat(z))'),
      F('w = vec(s.x - z.z*z.z*u.x, s.y - z.z*z.z*u.y, 2*len(flat(z))*z.z)'), F('z = if(len(w) > 0, w*(dot(z, z)/len(w)), w)'), ['addc']] },
    { name: 'Two points side by side, up and across alike (power 2)', lab: 'twinsalike', only2: true, say: only2, steps: [F('a = vec(0.5, 0, 0) - cpow(vec(0.25, 0, 0) - flat(c), 0.5)'),
      F('u = if(dot(a, a) > 0.000000000001, cmul(a, a)/dot(a, a), vec(1, 0, 0))'), F('t = cmul(cmul(flat(z), flat(z)), vec(u.x, -u.y, 0))'), F('r2 = dot(flat(z), flat(z))'),
      F('xs = max((r2 + t.x)/2, 0)'), F('ys = max((r2 - t.x)/2, 0)'), F('h2 = z.z*z.z'), F('s2 = max(ys + h2, 1e-30)'),
      F('w = cmul(u, vec(t.x - h2, if(t.y < 0, -2, 2)*sqrt(ys*(xs + h2*h2/s2)), 0)) + vec(0, 0, 2*z.z*sqrt(xs + ys*ys/s2))'),
      F('z = if(len(w) > 0, w*(dot(z, z)/len(w)), w)'), ['addc']] },
    // g is the line, square to the side pinch point. Seen from it, behind( ) is how far a point lies behind the plane
    // across the line, in units of b, and land( ) is where squaring puts it when y lands with the sign sg. The
    // point's own sign is sharp, and the orbits beside it take the same one. k is the second point: its sign
    // changes gradually, as the cosine of how far round behind the top it stands (turned( ), with x counted in
    // units of sqrt(b·|h|)), over the share lam of the back of a body, and the colours follow it.
    { name: 'Two points side by side, whole buds on top (power 2)', lab: 'twinswhole', only2: true, say: only2, steps: [num('join', 2, 0, 4),
      ['keep', { name: 'k', start: 'vec(0, 0, 0)' }],
      ['func', { name: 'along', args: 'p, g', text: 'dot(flat(p), g)' }], ['func', { name: 'across', args: 'p, g', text: 'g.x*p.y - g.y*p.x' }],
      ['func', { name: 'off', args: 'p, g', text: 'max(across(p, g)*across(p, g) + p.z*p.z, 1e-30)' }],
      ['func', { name: 'behind', args: 'p, g', text: '-along(p, g)/max(p.z*p.z/sqrt(off(p, g)), 1e-20)' }],
      ['func', { name: 'land', args: 'p, g, sg', text: 'cmul(cmul(g, g), vec(along(p, g)*along(p, g) - across(p, g)*across(p, g) - p.z*p.z, 2*across(p, g)*sg*sqrt(along(p, g)*along(p, g) + p.z*p.z*p.z*p.z/off(p, g)), 0)) + vec(0, 0, 2*p.z*sqrt(along(p, g)*along(p, g) + across(p, g)*across(p, g)*across(p, g)*across(p, g)/off(p, g)))' }],
      F('k = if(count < 1.5, z, k)'), ['f_side', { out: 's', a0: 'c' }], F('g = unit(vec(s.y, -s.x, 0))'),
      F('sg = same(if(behind(z, g) > 0.414213562, -1, 1))'), F('w = land(z, g, sg)'), F('z = if(len(w) > 0, w*(dot(z, z)/len(w)), w)'), ['addc'],
      ['func', { name: 'turned', args: 'p, g', text: 'atan(-along(p, g)/max(sqrt(abs(p.z)*p.z*p.z/sqrt(off(p, g))), 1e-20))' }],
      F('g2 = cmul(g, g)'), F('lam = min(1, join*abs(g2.x*c.y - g2.y*c.x))'),
      F('wk = land(k, g, cos(pi*clamp((turned(k, g) - pi/8)/(3*pi/8*lam), 0, 1)))'), F('k = if(len(wk) > 0, wk*(dot(k, k)/len(wk)), wk) + c'),
      ['o_colours', { out: 'colours', a0: 'if(lam > 0.000001, k, z)' }]] },
    // The entry "twinslong": the rule above with its line taken from longway( ), and with the two shares put
    // through the step share( ) (lift( ) is the extra term of the across-part, times how much of it kept( ) says is
    // kept).
    { name: 'Two points side by side, line along the long way (power 2)', lab: 'twinslong', only2: true, say: only2, steps: [num('join', 2, 0, 4),
      ['keep', { name: 'k', start: 'vec(0, 0, 0)' }],
      ['func', { name: 'along', args: 'p, g', text: 'dot(flat(p), g)' }], ['func', { name: 'across', args: 'p, g', text: 'g.x*p.y - g.y*p.x' }],
      ['func', { name: 'off', args: 'p, g', text: 'max(across(p, g)*across(p, g) + p.z*p.z, 1e-30)' }],
      ['func', { name: 'share', args: 't', text: 't*t*t/(t*t*t + (1 - t)*(1 - t)*(1 - t))' }], ['func', { name: 'lift', args: 'p, g, kp', text: 'kp*kp*p.z*p.z*share(p.z*p.z/off(p, g))' }],
      ['func', { name: 'behind', args: 'p, g, kp', text: '-along(p, g)/max(sqrt(lift(p, g, kp)), 1e-20)' }],
      ['func', { name: 'land', args: 'p, g, sg, kp', text: 'cmul(cmul(g, g), vec(along(p, g)*along(p, g) - across(p, g)*across(p, g) - p.z*p.z, 2*across(p, g)*sg*sqrt(along(p, g)*along(p, g) + lift(p, g, kp)), 0)) + vec(0, 0, 2*p.z*sqrt(along(p, g)*along(p, g) + across(p, g)*across(p, g)*share(across(p, g)*across(p, g)/off(p, g))))' }],
      F('k = if(count < 1.5, z, k)'), ['f_longway', { out: 'g', a0: 'c' }], ['f_kept', { out: 'kp', a0: 'c' }],
      F('sg = same(if(behind(z, g, kp) > 0.414213562, -1, 1))'), F('w = land(z, g, sg, kp)'), F('z = if(len(w) > 0, w*(dot(z, z)/len(w)), w)'), ['addc'],
      ['func', { name: 'turned', args: 'p, g, kp', text: 'atan(-along(p, g)/max(sqrt(abs(p.z)*sqrt(lift(p, g, kp))), 1e-20))' }],
      F('g2 = cmul(g, g)'), F('lam = min(1, join*abs(g2.x*c.y - g2.y*c.x))'),
      F('wk = land(k, g, cos(pi*clamp((turned(k, g, kp) - pi/8)/(3*pi/8*lam), 0, 1)), kp)'), F('k = if(len(wk) > 0, wk*(dot(k, k)/len(wk)), wk) + c'),
      ['o_colours', { out: 'colours', a0: 'if(lam > 0.000001, k, z)' }]] },
    // The entry "twinsbud": the rule above with the fold kept for a point whose folded copy lies beyond the next
    // body's far pinch point, and made true to angles there. fromtop( ) is the angle from straight up, round the
    // line; beside( ) is 1 beside the plane across the line; twice( ) is the across-part's extra term that makes a
    // point at the angle t from straight up land at 2t; tall( ) is what a folded point's height is taken times, so
    // that its copy is as thick across the plane as wide in it; copy( ) is where the fold would put the point on the flat
    // plane. fz is 1 where the point is folded: the orbits beside it take the same answer. The sign is the one
    // of the rule above, whether the point is folded or not. fit( ) is what a point near the change of sign is
    // taken times before the step, from what seam( ) gives for the set at the point's angle from straight up;
    // the point the colours follow is not fitted.
    { name: 'Two points side by side, the bulb on top alone (power 2)', lab: 'twinsbud', only2: true, say: only2, steps: [num('join', 2, 0, 4),
      ['keep', { name: 'k', start: 'vec(0, 0, 0)' }],
      ['func', { name: 'along', args: 'p, g', text: 'dot(flat(p), g)' }], ['func', { name: 'across', args: 'p, g', text: 'g.x*p.y - g.y*p.x' }],
      ['func', { name: 'off', args: 'p, g', text: 'max(across(p, g)*across(p, g) + p.z*p.z, 1e-30)' }],
      ['func', { name: 'share', args: 't', text: 't*t*t/(t*t*t + (1 - t)*(1 - t)*(1 - t))' }],
      ['func', { name: 'fromtop', args: 'p, g', text: 'atan2(abs(across(p, g)), abs(p.z))' }],
      ['func', { name: 'beside', args: 'p, g', text: '1 - smoothstep(0.5, 2, along(p, g)*along(p, g)/off(p, g))' }],
      ['func', { name: 'twice', args: 'p, g', text: '1/max((p.z*p.z - across(p, g)*across(p, g))/off(p, g)*((p.z*p.z - across(p, g)*across(p, g))/off(p, g)), 0.000001)' }],
      ['func', { name: 'up', args: 'p, g', text: 'max(p.z*p.z/off(p, g), 0.000001)' }],
      ['func', { name: 'tall', args: 'p, g, kp', text: 'sqrt((1 + kp*kp*4*up(p, g)*(1 - up(p, g))*twice(p, g))/up(p, g))' }],
      ['func', { name: 'copyy', args: 'p, g, kp, sg', text: '2*across(p, g)*sg*sqrt(along(p, g)*along(p, g) + kp*kp*p.z*p.z*twice(p, g))' }],
      ['func', { name: 'copy', args: 'p, g, kp, q, sg', text: 'flat(q) + cmul(cmul(g, g), vec(along(p, g)*along(p, g) - across(p, g)*across(p, g) - p.z*p.z, copyy(p, g, kp, sg), 0))*(dot(p, p)/max(len(vec(along(p, g)*along(p, g) - across(p, g)*across(p, g) - p.z*p.z, copyy(p, g, kp, sg), 2*tall(p, g, kp)*abs(p.z*along(p, g)))), 1e-30))' }],
      ['func', { name: 'lift', args: 'p, g, kp, fz', text: 'kp*kp*p.z*p.z*(share(p.z*p.z/off(p, g)) + fz*(twice(p, g) - share(p.z*p.z/off(p, g))))' }],
      ['func', { name: 'raise', args: 'p, g, fz, nz, tz', text: 'across(p, g)*across(p, g)*if(fz > 0, share(across(p, g)*across(p, g)/off(p, g))*(1 - nz), share(across(p, g)*across(p, g)/off(p, g)) + tz*(share(across(p, g)*across(p, g)/max(along(p, g)*along(p, g) + across(p, g)*across(p, g), 1e-30)) - share(across(p, g)*across(p, g)/off(p, g))))' }],
      ['func', { name: 'behind', args: 'p, g, kp', text: '-along(p, g)/max(sqrt(lift(p, g, kp, 0)), 1e-20)' }],
      ['func', { name: 'fit', args: 'p, g, kp, q, sg', text: 'exp(0.25*if(sg < 0, 1 - smoothstep(0.414213562, 3, behind(p, g, kp)), -smoothstep(-1, 0.414213562, behind(p, g, kp)))*seam(q, atan2(across(p, g), abs(p.z))))' }],
      ['func', { name: 'land', args: 'p, g, sg, kp, fz, ra', text: 'cmul(cmul(g, g), vec(along(p, g)*along(p, g) - across(p, g)*across(p, g) - p.z*p.z, 2*across(p, g)*sg*sqrt(along(p, g)*along(p, g) + lift(p, g, kp, fz)), 0)) + vec(0, 0, 2*p.z*(1 + fz*(tall(p, g, kp) - 1))*sqrt(along(p, g)*along(p, g) + ra))' }],
      F('k = if(count < 1.5, z, k)'), ['f_longway', { out: 'g', a0: 'c' }], ['f_kept', { out: 'kp', a0: 'c' }], ['f_curves', { out: 'on', a0: 'c' }],
      F('sg = same(if(behind(z, g, kp) > 0.414213562, -1, 1))'), F('z = z*fit(z, g, kp, c, sg)'),
      F('nz = on*beside(z, g)'), F('tz = nz*(1 - smoothstep(0.610865238, 0.785398163, fromtop(z, g)))'),
      F('fo = same(if(nz > 0, if(fromtop(z, g) < 0.698131701, beyond(copy(z, g, kp, c, 1), c)*beyond(copy(z, g, kp, c, -1), c), 0), 0))'), F('fz = fo*nz'),
      F('w = land(z, g, sg, kp, fz, raise(z, g, fz, nz, tz))'), F('z = if(len(w) > 0, w*(dot(z, z)/len(w)), w)'), ['addc'],
      ['func', { name: 'turned', args: 'p, g, kp, fz', text: 'atan(-along(p, g)/max(sqrt(abs(p.z)*sqrt(lift(p, g, kp, fz))), 1e-20))' }],
      F('g2 = cmul(g, g)'), F('lam = min(1, join*abs(g2.x*c.y - g2.y*c.x))'),
      F('nk = on*beside(k, g)'), F('tk = nk*(1 - smoothstep(0.610865238, 0.785398163, fromtop(k, g)))'),
      F('fk = nk*if(nk > 0, if(fromtop(k, g) < 0.698131701, beyond(copy(k, g, kp, c, 1), c)*beyond(copy(k, g, kp, c, -1), c), 0), 0)'),
      F('wk = land(k, g, cos(pi*clamp((turned(k, g, kp, fk) - pi/8)/(3*pi/8*lam), 0, 1)), kp, fk, raise(k, g, fk, nk, tk))'), F('k = if(len(wk) > 0, wk*(dot(k, k)/len(wk)), wk) + c'),
      ['o_colours', { out: 'colours', a0: 'if(lam > 0.000001, k, z)' }]] },
    { name: 'Parts carried by the orbit', lab: 'partsorbit', steps: [['keep', { name: 'u', start: 'vec(0, 0, 0)' }], F('u = same(if(count < 1.5, flat(z), cpow(u, n) + flat(c)))'), ...fitBend, ['addc']] });
}
