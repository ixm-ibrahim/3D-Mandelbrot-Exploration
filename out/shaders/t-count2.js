//#
const L = window.squaringLab; L.S.eq = 'z^n + c/z'; L.S.z0 = '1'; L.cam.target = [0, 0, 0]; L.cam.dist = 6;
return window.abCount('pole, all on');
//#
const L = window.squaringLab; L.S.eq = 'c*z*(1 - z)'; L.S.z0 = '0.5'; L.cam.target = [1, 0, 0]; L.cam.dist = 10;
return window.abCount('lambda, all on');
//#
const L = window.squaringLab; L.S.eq = 'z^n + c'; L.S.z0 = '0'; L.cam.target = [-0.6, 0, 0]; L.cam.dist = 5.2;
const c = window.newCount;
return [c('default nt=3', {}), c('default nt=1', { nt: 1, analytic: false }), c('default nt=0', { nt: 0, analytic: false }),
  c('default nt=3 plain', { shadow: false, ao: false }), c('default nt=1 plain', { nt: 1, analytic: false, shadow: false, ao: false }), c('default nt=0 plain', { nt: 0, analytic: false, shadow: false, ao: false })];
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
const c = window.newCount;
return [c('classic nt=3 plain', { shadow: false, ao: false }), c('classic nt=1 plain', { nt: 1, analytic: false, shadow: false, ao: false }), c('classic nt=0 plain', { nt: 0, analytic: false, shadow: false, ao: false })];
