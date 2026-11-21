//# wait=done timeout=300 shot=out/shaders/live-1-default.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 4; L.touch(); return 'live default: approach ' + L.S.approach + ', de ' + L.S.q.de + ', colour ' + JSON.stringify(L.S.colour);
//# wait=done timeout=300 shot=out/shaders/live-2-rough.png clip=#stage
const L = window.squaringLab; L.S.q.de = 0; L.touch(); return 'rough';
//# wait=done timeout=300 shot=out/shaders/live-3-mosaic.png clip=#stage
const L = window.squaringLab; L.S.q.de = 3; L.S.mosaic = true; L.touch(); return 'mosaic';
//# wait=done timeout=300 shot=out/shaders/live-4-flat-mosaic.png clip=#stage
const L = window.squaringLab; L.S.flat = true; L.touch(); return 'flat mosaic';
//# wait=done timeout=300 shot=out/shaders/live-5-flat.png clip=#stage
const L = window.squaringLab; L.S.mosaic = false; L.touch(); return 'flat';
//# wait=done timeout=300 shot=out/shaders/live-6-neg.png clip=#stage
const L = window.squaringLab; L.S.flat = false; L.S.n = -2; L.cam.target = [0, 0, 0]; L.cam.dist = 6; L.refresh(false); return 'n = -2';
//# wait=done timeout=300 shot=out/shaders/live-7-neg-flat.png clip=#stage
const L = window.squaringLab; L.S.flat = true; L.S.v2 = { x: 0, y: 0, h: 5 }; L.touch(); return 'n = -2 flat';
//# wait=done timeout=300 shot=out/shaders/live-8-klein.png clip=#stage
const L = window.squaringLab; L.S.flat = false; L.S.n = 2; L.S.mode = 'k'; L.refresh(false); return 'klein';
