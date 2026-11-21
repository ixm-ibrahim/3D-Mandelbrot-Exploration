//# {"wait":"done","timeout":300}
const L = window.squaringLab; L.R.warmOn = false; return 'loaded';
//# {}
const L = window.squaringLab, $ = id => document.getElementById(id);
const vis = e => { if (!e) return null; const r = e.getBoundingClientRect(); return !!(r.width && r.height) && getComputedStyle(e).visibility !== 'hidden'; };
const dump = () => { const o = {}; document.querySelectorAll('input[id],select[id],button[id]').forEach(e => { o[e.id] = (vis(e) ? 'V' : 'h') + (e.disabled ? 'D' : ''); }); return o; };
document.querySelectorAll('details.sec').forEach(d => { d.open = true; });
window.__d3 = dump();
const f = $('flat'), fr = f.getBoundingClientRect();
const show = [...document.querySelectorAll('#sections summary, .label')].find(e => /^show/i.test(e.textContent.trim()));
const sr = show ? show.getBoundingClientRect() : null;
return { flatTop: fr.top, flatLeft: fr.left, showText: show && show.textContent.trim(), showTop: sr && sr.top, flatLabel: f.closest('label') ? f.closest('label').textContent.trim() : (document.querySelector('label[for=flat]')||{}).textContent,
  approaches: L.APPROACHES.map(a => a.id), presets: L.PRESETS.map(p => p.eq), S: JSON.stringify(L.S).slice(0, 1500), cam: JSON.stringify(L.cam), hint: document.querySelector('.hint') && document.querySelector('.hint').textContent, status: $('status').textContent };
//# {"wait":"done","timeout":300,"shot":"a1-default-3d.png","clip":"#stage"}
return 1;
//# {"wait":"done","timeout":300,"shot":"a2-default-2d.png","clip":"#stage"}
const L = window.squaringLab, $ = id => document.getElementById(id);
window.__cam0 = JSON.stringify(L.cam);
$('flat').click();
await new Promise(r => setTimeout(r, 400));
return { flat: L.S.flat, v2: L.S.v2, cut: L.S.cut, cutOn: L.S.cutOn, stageCam: $('stage').dataset.cam };
//# {"shot":"a3-page-2d.png"}
const L = window.squaringLab, $ = id => document.getElementById(id);
const vis = e => { if (!e) return null; const r = e.getBoundingClientRect(); return !!(r.width && r.height) && getComputedStyle(e).visibility !== 'hidden'; };
const o = {}; document.querySelectorAll('input[id],select[id],button[id]').forEach(e => { const s = (vis(e) ? 'V' : 'h') + (e.disabled ? 'D' : ''); if (window.__d3[e.id] !== s) o[e.id] = window.__d3[e.id] + '->' + s; });
const lab = id => { const e = $(id); if (!e) return null; const d = e.closest('.dial, label, .check, div'); return (d ? d.textContent.trim().slice(0, 80) : '') + ' [' + (vis(e) ? 'V' : 'h') + (e.disabled ? 'D' : '') + ']'; };
const all = {}; document.querySelectorAll('input[id],select[id],button[id]').forEach(e => { if (vis(e)) all[e.id] = (e.closest('.dial, label') || e).textContent.trim().slice(0, 50); });
window.scrollTo(0, 0);
return { changed: o, hint: document.querySelector('.hint').textContent, status: $('status').textContent, aria: $('view').getAttribute('aria-label'), visibleNow: all, stageText: $('stage').innerText.slice(0, 400) };
