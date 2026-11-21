//pre  Fixer of round 12: the smoke test found the same 165 probes for the Julia set c = -1 of two entries. Same picture, or a coarse grid?
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { await sleep(150); for (let i = 0; i < 600 && !L.idle(); i++) await sleep(100); };
const gridN = (a, b) => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = ''; for (let i = 0; i < a; i++) for (let j = 0; j < b; j++) s += L.pick(w * (i + 0.5) / a, h * (j + 0.5) / b) ? '1' : '0'; return s; };
const diff = (p, q) => { let n = 0; for (let i = 0; i < p.length; i++) if (p[i] !== q[i]) n++; return n; };
const hits = s => s.split('1').length - 1;
//====
//shot pair-julia-mercator
$('mode-j').click(); L.applyJuliaPreset({ c: [-1, 0, 0] }); $('ap-mercator').click(); await settle();
window.pairA = { coarse: gridN(15, 11), fine: gridN(44, 30), finer: gridN(60, 44) };
return 'one plane, Julia c = -1: ' + hits(window.pairA.coarse) + ' of 165, ' + hits(window.pairA.fine) + ' of 1320, ' + hits(window.pairA.finer) + ' of 2640 probes hit';
//====
//shot pair-julia-tilt
$('ap-tilt').click(); await settle();
const B = { coarse: gridN(15, 11), fine: gridN(44, 30), finer: gridN(60, 44) }, A = window.pairA;
const out = ['twisted square (tilt ' + L.S.param.tilt.tilt + '), Julia c = -1: ' + hits(B.coarse) + ' of 165, ' + hits(B.fine) + ' of 1320, ' + hits(B.finer) + ' of 2640 probes hit',
  'probes that differ from one plane: ' + diff(A.coarse, B.coarse) + ' of 165, ' + diff(A.fine, B.fine) + ' of 1320, ' + diff(A.finer, B.finer) + ' of 2640'];
return out.join(' | ');
