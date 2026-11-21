//// wait=done shot=out/render/sh-1-default.png clip=#stage
// The new uniforms, checked against a snapshot of the live shader file (the baseline shader ignores them).
const L = window.squaringLab; L.R.warmOn = false; L.S.q.aa = 4; L.touch(); return 'default, new shader';
//// wait=done shot=out/render/sh-2-bound.png clip=#stage
const L = window.squaringLab; L.S.view.bound = 0.8; L.touch(); return 'drawing radius 0.8: the set is clipped to a ball';
//// wait=done shot=out/render/sh-3-de1.png clip=#stage
const L = window.squaringLab; L.S.view.bound = 8; L.S.q.de = 1; L.touch(); return 'one neighbouring orbit';
//// wait=done shot=out/render/sh-4-de0.png clip=#stage
const L = window.squaringLab; L.S.q.de = 0; L.touch(); return 'no neighbouring orbits (ultra fast estimate)';
//// wait=done shot=out/render/sh-5-mosaic.png clip=#stage
const L = window.squaringLab; L.S.q.de = 3; L.S.mosaic = true; L.S.mosaicCell = 0.3; L.touch(); return 'mosaic';
//// wait=done shot=out/render/sh-6-flat.png clip=#stage
const L = window.squaringLab; L.S.mosaic = false; L.S.flat = true; L.touch(); return 'flat view: ' + JSON.stringify(L.S.v2);
//// wait=done shot=out/render/sh-7-flat-mosaic.png clip=#stage
const L = window.squaringLab; L.S.mosaic = true; L.S.mosaicCell = 0.2; L.touch(); return 'flat mosaic';
//// wait=done shot=out/render/sh-8-flat-julia.png clip=#stage
const L = window.squaringLab; L.S.mosaic = false; document.getElementById('mode-j').click(); L.S.v2 = { x: 0, y: 0, h: 3.4 }; L.touch(); return 'flat Julia, c = ' + L.S.c;
//// wait=done shot=out/render/sh-9-flat-klein.png clip=#stage
const L = window.squaringLab; document.getElementById('mode-k').click(); L.S.v2 = { x: 0, y: 0, h: 6 }; L.touch(); return 'flat Kleinian';
