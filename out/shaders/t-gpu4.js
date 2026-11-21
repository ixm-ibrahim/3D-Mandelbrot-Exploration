//#
const L = window.squaringLab, G = L.GLSL();
window.sets = { old: G.OLD, 'arrays': G.V2, now: G };
return await window.gpuCompare('default, all on', window.sets, {}, 30);
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
return await window.gpuCompare('classic n=8, all on', window.sets, {}, 30);
//#
return await window.gpuCompare('classic n=8, no shadow/crevices', window.sets, { shadow: false, ao: false }, 30);
