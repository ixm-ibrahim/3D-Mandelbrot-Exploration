//#
const L = window.squaringLab, c = window.newCount; L.S.n = -2; L.cam.target = [0, 0, 0]; L.cam.dist = 6;
return [c('n = -2, exact, all on', { analytic: false }), c('n = -2, exact, plain', { analytic: false, shadow: false, ao: false }), c('n = -2, rough, plain', { nt: 0, analytic: false, shadow: false, ao: false })];
//#
const L = window.squaringLab, c = window.newCount; L.S.n = 2; L.S.mosaic = true; L.cam.target = [-0.6, 0, 0]; L.cam.dist = 5.2;
return [c('mosaic 0.3, exact, all on', {}), c('mosaic 0.3, exact, plain', { shadow: false, ao: false }), c('mosaic 0.3, rough, plain', { nt: 0, analytic: false, shadow: false, ao: false })];
