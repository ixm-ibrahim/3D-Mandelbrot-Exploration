//#
const c = window.abCount;
return [c('default, all on'), c('default, no shadow/crevices', { shadow: false, ao: false }), c('default, sampled slope', { analytic: false })];
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
const c = window.abCount;
return [c('classic n=8, all on'), c('classic n=8, no shadow/crevices', { shadow: false, ao: false })];
//#
const L = window.squaringLab; L.S.approach = 1; L.S.n = 2; L.S.iter = 14; L.S.param.lathe.spin = 3;
return window.abCount('lathe spin 3, all on');
//#
const L = window.squaringLab; L.S.approach = 0; L.S.mode = 'j'; L.cam.pitch = 1.5; L.cam.yaw = -Math.PI / 2; L.cam.dist = 4.4;
return window.abCount('julia c=-1, all on');
