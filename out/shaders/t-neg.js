//# wait=done timeout=180 shot=out/shaders/h-neg2-3d.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 4; L.S.n = -2; L.cam.target = [0, 0, 0]; L.cam.dist = 6; L.refresh(false); return 'n = -2, sphere inversions, 3D';
//# wait=done timeout=180 shot=out/shaders/h-neg2-flat.png clip=#stage
const L = window.squaringLab; L.S.flat = true; L.S.v2 = { x: 0, y: 0, h: 5 }; L.touch(); return 'n = -2, 2D';
//# wait=done timeout=180 shot=out/shaders/h-neg2-cut.png clip=#stage
const L = window.squaringLab; L.S.flat = false; L.S.cutOn = true; L.S.cut = 0; L.cam.pitch = 0.9; L.touch(); return 'n = -2, 3D cut at z = 0';
//# wait=done timeout=180 shot=out/shaders/h-neg3-classic.png clip=#stage
const L = window.squaringLab; L.S.cutOn = false; L.S.approach = 3; L.S.n = -3; L.cam.pitch = 0.55; L.refresh(false); return 'n = -3, classic bulb';
//# wait=done timeout=180 shot=out/shaders/h-neg2-julia.png clip=#stage
const L = window.squaringLab; L.S.approach = 0; L.S.n = -2; L.S.mode = 'j'; L.S.c = [-1, 0, 0]; L.refresh(false); return 'n = -2 julia c = -1';
//# wait=done timeout=180 shot=out/shaders/h-neg2-julia2.png clip=#stage
const L = window.squaringLab; L.S.c = [0.6, 0.4, 0.2]; L.touch(); return 'n = -2 julia c = (0.6, 0.4, 0.2)';
//# wait=done timeout=180 shot=out/shaders/h-pole.png clip=#stage
const L = window.squaringLab; L.S.mode = 'm'; L.S.n = 2; L.S.eq = 'z^n + c/z'; L.S.z0 = '1'; L.cam.dist = 6; L.refresh(false); return 'z^n + c/z';
