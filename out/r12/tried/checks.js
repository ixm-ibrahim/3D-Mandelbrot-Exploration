// Round 12, tried rules: MATH against the flat complex power on the plane z = 0, and a dry run of every text.
// Runs inside the page (tools/shot.py). Returns one JSON string.
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES;
let seed = 12345;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const pts = [];
for (let i = 0; i < 2000; i++) { const r = Math.exp((rnd() * 2 - 1) * 2.5), a = (rnd() * 2 - 1) * Math.PI; pts.push([r * Math.cos(a), r * Math.sin(a)]); }
[[1, 0], [-1, 0], [0, 1], [0, -1], [0.5, 0], [-0.5, 0], [0, 2], [0, -2], [-2, 1e-9], [-2, -1e-9], [1e-5, 1e-5], [-1e-5, 1e-5], [3, 4], [-3, -4]].forEach(p => pts.push(p));
const cpow = (x, y, n) => { const r = Math.hypot(x, y), a = Math.atan2(y, x) * n, R = Math.pow(r, n); return [R * Math.cos(a), R * Math.sin(a)]; };
const defaults = a => Object.fromEntries((a.params || []).filter(s => s.key !== undefined).map(s => [s.key, s.def]));
// worst relative error of F against z^n on the plane through the x-axis turned by `ang` from z = 0, and the
// worst distance of the result from that plane
function plane(id, q, n, ang) {
  const c = Math.cos(ang), s = Math.sin(ang);
  let worst = 0, off = 0, exactZero = true, bad = 0;
  for (const [x, y] of pts) {
    const v = ang === 0 ? [x, y, 0] : [x, y * c, y * s], w = cpow(x, y, n), o = M[id](v, n, q), size = Math.hypot(w[0], w[1]);
    const want = ang === 0 ? [w[0], w[1], 0] : [w[0], w[1] * c, w[1] * s];
    const e = Math.hypot(o[0] - want[0], o[1] - want[1], o[2] - want[2]) / size;
    if (!(e <= worst)) worst = e;
    if (!(e < 1e-9)) bad++;
    const out = Math.abs(ang === 0 ? o[2] : -o[1] * s + o[2] * c) / size;
    if (out > off) off = out;
    if (ang === 0 && o[2] !== 0) exactZero = false;
  }
  return { worst, off, exactZero, bad };
}
const POWERS = [2, 3, -1], rows = [];
const run = (id, q, label, ang = 0, powers = POWERS) => {
  const r = { id, label, plane: ang === 0 ? 'z=0' : Math.round(ang * 180 / Math.PI) + 'deg', q: JSON.stringify(q) };
  for (const n of powers) { const p = plane(id, q, n, ang); r['n' + n] = p.worst; r['bad' + n] = p.bad; if (ang === 0) r['z0_' + n] = p.exactZero; }
  rows.push(r);
};
AP.forEach(a => run(a.id, defaults(a), 'default'));
const d = id => defaults(AP.find(a => a.id === id));
// Blended planes: other settings, and the other planes
[3, 4].forEach(p => run('softfold', { ...d('softfold'), planes: p }, 'planes ' + p));
run('softfold', { ...d('softfold'), mix: 1 }, 'straight blend');
run('softfold', { ...d('softfold'), mix: 2 }, 'pinch');
run('softfold', { ...d('softfold'), curve: 1 }, 'smoother step');
run('softfold', { ...d('softfold'), blend: 0 }, 'band 0');
run('softfold', { ...d('softfold'), blend: 0.45 }, 'band 0.45');
[2, 3, 4].forEach(p => { for (let j = 1; j < p; j++) run('softfold', { ...d('softfold'), planes: p }, `planes ${p}, plane ${j}`, j * Math.PI / p); });
run('softfold', { ...d('softfold'), mix: 2 }, 'pinch, plane 1', Math.PI / 2);
run('softfold', d('softfold'), 'default, power 2.5 and -2', 0, [2.5, -2]);
// Bulbs about the axis
[5, -3, 9, -7, 3, -1, 2, 4].forEach(k => run('axisbulb', { ...d('axisbulb'), k }, 'multiplier ' + k));
run('axisbulb', { ...d('axisbulb'), pinch: 1.5 }, 'pinch 1.5');
run('axisbulb', { ...d('axisbulb'), wob: 1, reach: 0 }, 'wobble 1, reach 0');
run('axisbulb', d('axisbulb'), 'default, plane y=0', Math.PI / 2);
[5, -3, 3].forEach(k => run('axisbulb', { ...d('axisbulb'), k }, `multiplier ${k}, plane y=0`, Math.PI / 2));
run('axisbulb', d('axisbulb'), 'default, power 2.5 and -2', 0, [2.5, -2]);
// Pillow
run('pillow', { layout: 1 }, 'smooth layout');
run('pillow', { layout: 0 }, 'creased, plane y=0', Math.PI / 2);
run('pillow', { layout: 0 }, 'creased, powers 4, 5, 8, -2, -3', 0, [4, 5, 8, -2, -3]);
run('pillow', { layout: 1 }, 'smooth, powers 4, 8', 0, [4, 8]);

// every text of every entry, at several powers and settings: nothing may throw, nothing may be empty
const texts = [], NS = [2, 3, -1, 2.5, 0, 1, 8, -2, 0.5];
const settings = {
  softfold: [d('softfold'), { ...d('softfold'), planes: 3 }, { ...d('softfold'), mix: 2 }, { ...d('softfold'), mix: 1, curve: 1 }],
  axisbulb: [d('axisbulb'), { ...d('axisbulb'), k: 5 }, { ...d('axisbulb'), k: 2 }, { ...d('axisbulb'), k: 0, wob: 0 }, { ...d('axisbulb'), k: 1, wob: 0, pinch: 0 }, { ...d('axisbulb'), pinch: 1 }, { ...d('axisbulb'), k: 3 }],
  pillow: [{ layout: 0 }, { layout: 1 }],
};
let dashes = 0;
AP.forEach(a => {
  const list = settings[a.id] || [defaults(a)];
  for (const q of list) for (const n of NS) {
    try {
      const out = [a.formula(q, n), a.crush(q, n), a.smooth(q, n), a.slice(true, q, n), a.slice(false, q, n), typeof a.roundNote === 'function' ? a.roundNote(q, n) : a.roundNote, a.axis(q)];
      const flat = JSON.stringify(out);
      if (out.some(x => x === undefined || x === null || x === '') || /undefined|NaN|\[object/.test(flat)) texts.push(`${a.id} n=${n} q=${JSON.stringify(q)}: odd text ${flat.slice(0, 300)}`);
      if (/—|–/.test(flat)) dashes++;
      if (!['ok', 'part', 'no'].includes(out[1][0]) || !['ok', 'part', 'no'].includes(out[2][0])) texts.push(`${a.id} n=${n}: bad pill`);
    } catch (err) { texts.push(`${a.id} n=${n} q=${JSON.stringify(q)}: THROWS ${err.message}`); }
  }
  const fixed = JSON.stringify([a.name, a.tag, a.about, (a.params || []).map(s => [s.label, s.text, s.help, s.options])]);
  if (/—|–/.test(fixed)) dashes++;
  if (!a.group || !a.id || !a.name || !a.glsl || !a.tag || !a.about) texts.push(a.id + ': a field is missing');
});
const list = AP.map(a => `${a.id} [${a.group}] ${a.name}; dials ${(a.params || []).filter(s => s.key !== undefined).map(s => s.key).join(', ') || 'none'}; first under the name: ${(a.params || [])[0] ? (a.params || [])[0].type : 'nothing'}`);
return JSON.stringify({ points: pts.length, rows, textProblems: texts, dashes, list }, null, 1);
