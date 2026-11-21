//# wait=done timeout=300 shot=out/shaders/h-neg2-rough.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 4; L.S.q.de = 0; L.S.n = -2; L.cam.target = [0, 0, 0]; L.cam.dist = 6; L.refresh(false); return 'n = -2 rough';
