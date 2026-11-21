//# wait=done timeout=240 shot=out/shaders/m-mosaic.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 6; L.S.mosaic = true; L.S.mosaicCell = 0.3; L.touch(); return 'mosaic 0.3';
//# wait=done timeout=240 shot=out/shaders/m-mosaic-close.png clip=#stage
const L = window.squaringLab; L.cam.dist = 2.2; L.cam.target = [-0.3, 0, 0]; L.touch(); return 'mosaic close';
//# wait=done timeout=240 shot=out/shaders/m-mosaic-cut.png clip=#stage
const L = window.squaringLab; L.cam.dist = 4.2; L.cam.pitch = 1.1; L.S.cutOn = true; L.S.cut = 0; L.touch(); return 'mosaic cut at z=0';
//# wait=done timeout=240 shot=out/shaders/m-mosaic-big.png clip=#stage
const L = window.squaringLab; L.S.cutOn = false; L.cam.pitch = 0.55; L.S.mosaicCell = 0.6; L.cam.dist = 5.2; L.cam.target = [-0.6, 0, 0]; L.touch(); return 'mosaic 0.6';
//# wait=done timeout=240 shot=out/shaders/m-flat-mosaic.png clip=#stage
const L = window.squaringLab; L.S.mosaicCell = 0.25; L.S.flat = true; L.S.v2 = { x: -0.5, y: 0, h: 3.2 }; L.touch(); return 'flat mosaic 0.25';
//# wait=done timeout=240 shot=out/shaders/m-flat-julia.png clip=#stage
const L = window.squaringLab; L.S.mosaic = false; L.S.mode = 'j'; L.S.c = [-0.8, 0.156, 0]; L.S.v2 = { x: 0, y: 0, h: 3 }; L.refresh(false); return 'flat julia';
//# wait=done timeout=240 shot=out/shaders/m-flat-klein.png clip=#stage
const L = window.squaringLab; L.S.mode = 'k'; L.S.v2 = { x: 0, y: 0, h: 6 }; L.refresh(false); return 'flat klein';
//# wait=done timeout=240 shot=out/shaders/m-flat-classic.png clip=#stage
const L = window.squaringLab; L.S.mode = 'm'; L.S.approach = 3; L.S.n = 8; L.S.v2 = { x: 0, y: 0, h: 3 }; L.refresh(false); return 'flat classic n=8 at z=0';
