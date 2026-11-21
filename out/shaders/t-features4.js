//# wait=done timeout=240 shot=out/shaders/q-rough-mosaic.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 4; L.S.q.de = 0; L.S.mosaic = true; L.cam.dist = 3; L.touch(); return 'rough mosaic';
//# wait=done timeout=240 shot=out/shaders/q-one-mosaic.png clip=#stage
const L = window.squaringLab; L.S.q.de = 1; L.touch(); return 'one-neighbour mosaic';
//# wait=done timeout=240 shot=out/shaders/q-rough-julia.png clip=#stage
const L = window.squaringLab; L.S.q.de = 0; L.S.mosaic = false; L.S.mode = 'j'; L.S.c = [-1, 0, 0]; L.resetCam(); L.refresh(false); return 'rough julia';
//# wait=done timeout=240 shot=out/shaders/q-ultra.png clip=#stage
const L = window.squaringLab; L.S.mode = 'm'; L.resetCam(); Object.assign(L.S.q, { res: 0.5, aa: 1, steps: 90, detail: 2, shadow: false, ao: false, de: 0, normals: 'soft' }); L.refresh(false); return 'ultra fast preset values';
//# wait=done timeout=240 shot=out/shaders/q-ultra-classic.png clip=#stage
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2; L.refresh(false); return 'ultra fast classic n=8';
//# wait=done timeout=240 shot=out/shaders/q-ultra-lambda.png clip=#stage
const L = window.squaringLab; L.S.approach = 0; L.S.n = 2; L.S.iter = 14; L.S.eq = 'c*z*(1 - z)'; L.S.z0 = '0.5'; L.cam.target = [1, 0, 0]; L.cam.dist = 10; L.refresh(false); return 'ultra fast lambda (falls back to one neighbour)';
