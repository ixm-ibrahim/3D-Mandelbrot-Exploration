// Fixer of round 12: numbers behind the sentences that were rewritten (run on the fixed page).
const L = window.squaringLab, M = L.MATH, PI = Math.PI, out = {};
let seed = 424242;
const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const sci = x => +x.toExponential(2);
// "away from a tilt of 0 the plane y = 0 is not [exact]": the plane y = 0 against the complex square, tilt by tilt
out.plane_y0_misses_the_complex_square_by = {};
for (const t of [0, 15, 40, 90, 137, 180, -60]) { let w = 0; for (let i = 0; i < 2000; i++) { const a = rnd() * 3 - 1.5, b = rnd() * 3 - 1.5, o = M.tilt([a, 0, b], 2, { tilt: t }); w = Math.max(w, Math.hypot(o[0] - (a * a - b * b), o[1], o[2] - 2 * a * b)); } out.plane_y0_misses_the_complex_square_by['tilt ' + t] = w < 1e-9 ? sci(w) : +w.toFixed(2); }
// "a wedge as wide as the tilt, beside the negative x-axis": where the slice z = 0 differs from the complex power 2.5
out.wedge_at_power_2p5 = {};
for (const t of [40, -60, 100, 0]) { let lo = 1e9, hi = -1e9, n = 0; for (let i = 0; i < 20000; i++) { const ang = rnd() * 360, r = 0.2 + rnd() * 1.5, a = r * Math.cos(ang * PI / 180), b = r * Math.sin(ang * PI / 180), o = M.tilt([a, b, 0], 2.5, { tilt: t }); const ph = Math.atan2(b, a) * 2.5, R = Math.pow(r, 2.5); if (Math.hypot(o[0] - R * Math.cos(ph), o[1] - R * Math.sin(ph), o[2]) > 1e-9 * (1 + R)) { n++; lo = Math.min(lo, ang); hi = Math.max(hi, ang); } } out.wedge_at_power_2p5['tilt ' + t] = n ? n + ' of 20000 directions differ, between ' + lo.toFixed(1) + ' and ' + hi.toFixed(1) + ' degrees' : 'none of 20000 differ'; }
// Bulbs about the axis, multiplier 3 as well (the slice sentence names 5, 3 and -3)
{ const bounded = (q, c) => { let v = [0, 0, 0]; for (let i = 0; i < 1000; i++) { v = M.axisbulb(v, 2, q); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; if (!(v[0] * v[0] + v[1] * v[1] + v[2] * v[2] < 1e6)) return false; } return true; };
  const flat = (cx, cy) => { let x = 0, y = 0; for (let i = 0; i < 1000; i++) { const X = x * x - y * y + cx, Y = 2 * x * y + cy; x = X; y = Y; if (!(x * x + y * y < 1e6)) return false; } return true; };
  const cs = []; for (let i = 0; i < 60; i++) for (let j = 0; j < 30; j++) { const cx = -2 + 2.5 * (i + 0.5) / 60, cy = 1.2 * (j + 0.5) / 30; if (flat(cx, cy)) cs.push([cx, cy]); }
  out.axisbulb_share_of_the_flat_set_where_the_solid_has_no_thickness = {};
  for (const k of [5, 3, -3, 1]) { const left = cs.filter(c => bounded({ k, wob: 0.2, reach: 45, pinch: 0 }, [c[0], c[1], 1e-8])).length; out.axisbulb_share_of_the_flat_set_where_the_solid_has_no_thickness['multiplier ' + k] = (100 * (1 - left / cs.length)).toFixed(0) + ' % (' + (cs.length - left) + ' of ' + cs.length + ' points escape when lifted by 1e-8)'; } }
// the texts as the page now holds them
const A = id => L.APPROACHES.find(a => a.id === id);
out.texts = { tilt_tag: A('tilt').tag, tilt_help: A('tilt').params[0].help, tilt_note: A('tilt').params[1].text, softfold_mix_help: A('softfold').params[4].help, softfold_curve: A('softfold').params[3].options.map(o => o[1]),
  classic_slice: A('classic').slice(false, { theta: 0, phi: 0 }, 2), axisbulb_slice_5: A('axisbulb').slice(true, { k: 5, wob: 0.2, reach: 45, pinch: 0 }, 2), tilt_smooth: A('tilt').smooth({ tilt: 40 }, 2), tilt_crush: A('tilt').crush({ tilt: 40 }, 2), pillow_smooth_row: A('pillow').smooth({ layout: 1 }, 2) };
return JSON.stringify(out, null, 1);
