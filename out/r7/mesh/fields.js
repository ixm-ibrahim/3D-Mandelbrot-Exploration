// Built-in fields through the panel: closed and oriented, volume, and for the sphere how far the points are from
// where the asked offset puts them. Run by fields.py (wrapped into one step for tools/shot.py).
const L = window.squaringLab, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));
const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const shown = id => $(id).getBoundingClientRect().width > 0;
window.squaringLabSaveHook = () => {};
$('secMesh').open = true;
const out = [];
for (const [field, cells, off, all] of [['sphere', 96, 0], ['sphere', 96, 0.5], ['sphere', 128, 2], ['torus', 128, 0.5], ['gyroid', 96, 0.5, true], ['gyroid', 192, 0.5], ['pearl', 96, 0], ['pearl', 96, 0.5], ['noise', 40, 0.5, true], ['noise', 56, 0.5]]) {
  if (shown('meshDiscard')) $('meshDiscard').click();
  type('meshOffset', String(off));
  if ($('meshLargest').checked === !!all) $('meshLargest').click();
  window.squaringLabMeshTest = { field, cells };
  $('meshStart').click(); await sleep(60);
  let n = 0; while (L.meshBusy() && n++ < 8000) await sleep(25);
  const m = window.squaringLabMeshTest.mesh;
  if (!m) { out.push({ field, cells, off, msg: $('meshMsg').textContent }); continue; }
  const nv = m.pos.length / 3, E = new Map();
  for (let t = 0; t < m.idx.length; t += 3) for (let e = 0; e < 3; e++) { const k = m.idx[t + e] * nv + m.idx[t + (e + 1) % 3]; E.set(k, (E.get(k) || 0) + 1); }
  let twice = 0, lone = 0;
  for (const [k, c] of E) { if (c !== 1) twice++; const a = Math.floor(k / nv), b = k - a * nv; if (!E.has(b * nv + a)) lone++; }
  const rec = { field, cells, off, all: !!all, tris: m.idx.length / 3, points: nv, pieces: m.pieces, closed: twice === 0 && lone === 0, euler: nv - E.size / 2 + m.idx.length / 3,
    labVolume: +(m.volume / Math.pow(m.unit, 3)).toFixed(5), cell: +m.h.toFixed(5), warn: $('meshWarn').hidden ? '' : $('meshWarn').textContent.slice(0, 60) };
  if (field === 'sphere' || field === 'pearl') {
    const R = 1 + (field === 'sphere' ? off * m.h : off * m.h / 1.6);
    let s2 = 0, worst = 0;
    for (let p = 0; p < m.pos.length; p += 3) { const r = Math.hypot(m.org[0] + m.pos[p] * m.h, m.org[1] + m.pos[p + 1] * m.h, m.org[2] + m.pos[p + 2] * m.h), e = (r - R) / m.h; s2 += e * e; if (Math.abs(e) > worst) worst = Math.abs(e); }
    rec.fitCells = [+Math.sqrt(s2 / nv).toFixed(4), +worst.toFixed(4)];
    rec.volumeErrorPct = +(100 * (rec.labVolume / (4 / 3 * Math.PI * R * R * R) - 1)).toFixed(3);
  }
  if (field === 'torus') { const r = 0.35 + off * m.h; rec.volumeErrorPct = +(100 * (rec.labVolume / (2 * Math.PI * Math.PI * r * r) - 1)).toFixed(3); }
  out.push(rec);
}
delete window.squaringLabMeshTest;
if (shown('meshDiscard')) $('meshDiscard').click();
return JSON.stringify(out);
