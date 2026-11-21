//# wait=done timeout=120 shot=out/shaders/f-de3.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 4; L.S.q.de = 3; L.touch(); return 'de 3 (exact)';
//# wait=done timeout=120 shot=out/shaders/f-de1.png clip=#stage
const L = window.squaringLab; L.S.q.de = 1; L.touch(); return 'de 1 (one neighbour)';
//# wait=done timeout=120 shot=out/shaders/f-de0.png clip=#stage
const L = window.squaringLab; L.S.q.de = 0; L.touch(); return 'de 0 (rough)';
//# wait=done timeout=120 shot=out/shaders/f-mosaic.png clip=#stage
const L = window.squaringLab; L.S.q.de = 3; L.S.mosaic = true; L.S.mosaicCell = 0.3; L.touch(); return 'mosaic 0.3';
//# wait=done timeout=120 shot=out/shaders/f-flat.png clip=#stage
const L = window.squaringLab; L.S.mosaic = false; L.S.flat = true; L.touch(); return 'flat';
//# wait=done timeout=120 shot=out/shaders/f-flat-mosaic.png clip=#stage
const L = window.squaringLab; L.S.mosaic = true; L.touch(); return 'flat mosaic';
