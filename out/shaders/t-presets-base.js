//# wait=done timeout=240 shot=out/shaders/p-base-pole.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 4; L.S.eq = 'z^n + c/z'; L.S.z0 = '1'; L.cam.target = [0, 0, 0]; L.cam.dist = 6; L.refresh(false); return 'z^n + c/z';
//# wait=done timeout=240 shot=out/shaders/p-base-lambda.png clip=#stage
const L = window.squaringLab; L.S.eq = 'c*z*(1 - z)'; L.S.z0 = '0.5'; L.cam.target = [1, 0, 0]; L.cam.dist = 10; L.refresh(false); return 'lambda';
//# wait=done timeout=240 shot=out/shaders/p-base-cubic.png clip=#stage
const L = window.squaringLab; L.S.eq = 'z^3 - z + c'; L.S.z0 = '0.57735'; L.cam.target = [0, 0, 0]; L.cam.dist = 4.8; L.refresh(false); return 'cubic';
//# wait=done timeout=240 shot=out/shaders/p-base-ship.png clip=#stage
const L = window.squaringLab; L.S.eq = 'abs(z)^n + c'; L.S.z0 = '0'; L.cam.target = [-0.6, 0, 0]; L.cam.dist = 5.2; L.refresh(false); return 'burning ship';
//# wait=done timeout=240 shot=out/shaders/p-base-bulb3.png clip=#stage
const L = window.squaringLab; L.S.eq = 'z^n + c'; L.S.approach = 2; L.S.n = 3; L.cam.target = [0, 0, 0]; L.cam.dist = 4.8; L.refresh(false); return 'bulb n=3';
//# wait=done timeout=240 shot=out/shaders/p-base-split.png clip=#stage
const L = window.squaringLab; L.S.approach = 4; L.S.n = 2; L.cam.target = [-0.6, 0, 0]; L.cam.dist = 5.2; L.refresh(false); return 'split';
