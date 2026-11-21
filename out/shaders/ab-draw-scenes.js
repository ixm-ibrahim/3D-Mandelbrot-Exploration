//#
window.bandRows = 120;
return window.abDraw('default (sphere inversions n=2), all on');
//#
return window.abDraw('default, no shadow no crevices', { shadow: false, ao: false });
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
return window.abDraw('classic n=8, all on');
//#
const L = window.squaringLab; L.S.approach = 1; L.S.n = 2; L.S.iter = 14; L.S.param.lathe.spin = 3;
return window.abDraw('lathe spin 3, all on');
//#
const L = window.squaringLab; L.S.approach = 0; L.S.mode = 'j'; L.cam.pitch = 1.5; L.cam.yaw = -Math.PI / 2; L.cam.dist = 4.4;
return window.abDraw('julia c=-1, all on');
//#
const L = window.squaringLab; L.S.mode = 'k'; L.resetCam();
return window.abDraw('kleinian, all on', { analytic: false });
