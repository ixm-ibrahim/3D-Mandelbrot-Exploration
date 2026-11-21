//#
const L = window.squaringLab, G = L.GLSL();
window.sets = { old: G.OLD, 'before gates': G.V2, now: G };
return await window.gpuCompare('default, all on', window.sets);
//#
return await window.gpuCompare('default, no shadow/crevices', window.sets, { shadow: false, ao: false });
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
return await window.gpuCompare('classic n=8, all on', window.sets);
//#
const L = window.squaringLab; L.S.approach = 1; L.S.n = 2; L.S.iter = 14; L.S.param.lathe.spin = 3;
return await window.gpuCompare('lathe spin 3, all on', window.sets);
