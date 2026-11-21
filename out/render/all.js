//// wait=done shot=out/render/all-1-default.png clip=#stage timeout=120
const L = window.squaringLab; L.S.q.aa = 4; L.touch(); return 'everything live: default';
//// wait=done shot=out/render/all-2-flat.png clip=#stage
const L = window.squaringLab; L.S.flat = true; L.touch(); return 'flat';
//// wait=done shot=out/render/all-3-mosaic.png clip=#stage
const L = window.squaringLab; L.S.flat = false; L.S.mosaic = true; L.touch(); return 'mosaic';
//// wait=done shot=out/render/all-4-ultra.png clip=#stage
const L = window.squaringLab; L.S.mosaic = false; Object.assign(L.S.q, { res: 0.5, aa: 1, steps: 90, detail: 2, shadow: false, ao: false, de: 0, normals: 'smooth' }); L.touch(); return 'ultra fast settings';
//// wait=done shot=out/render/all-5-klein.png clip=#stage
const L = window.squaringLab; Object.assign(L.S.q, { res: 1, aa: 4, steps: 260, detail: 1, shadow: true, ao: true, de: 3, normals: 'sharp' }); document.getElementById('mode-k').click(); return 'Kleinian';
//// 
const L = window.squaringLab; return 'compiles ' + L.R.compiles + ', status ' + document.getElementById('status').textContent + ', dt ' + L.R.dt.toFixed(1);
