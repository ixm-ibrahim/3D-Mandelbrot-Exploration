//# wait=done timeout=240 shot=out/shaders/r-classic8-de0.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 4; L.S.q.de = 0; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2; L.refresh(false); return 'classic n=8 rough';
//# wait=done timeout=240 shot=out/shaders/r-bulb2-de0.png clip=#stage
const L = window.squaringLab; L.S.approach = 2; L.S.n = 2; L.S.iter = 14; L.cam.target = [-0.6, 0, 0]; L.cam.dist = 5.2; L.refresh(false); return 'bulb n=2 rough';
//# wait=done timeout=240 shot=out/shaders/r-lathe-de0.png clip=#stage
const L = window.squaringLab; L.S.approach = 1; L.S.param.lathe.spin = 1; L.refresh(false); return 'lathe rough';
