//#
const L = window.squaringLab, G = L.GLSL(), S = window.subAll;
const noGates = { ...G, GL_TAIL: S(G.GL_TAIL, 'if (!flat2 && i < (phase >= PH_AO ? gate2 : phase >= PH_SLOPE ? gate1 : 0)) continue;', '') };
window.sets = { old: G.OLD, now: G, 'no gates': noGates };
return await window.gpuCompare('default, all on', window.sets, {}, 30);
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
return await window.gpuCompare('classic n=8, all on', window.sets, {}, 30);
//#
return await window.gpuCompare('classic n=8, sampled slope, all on', window.sets, { analytic: false }, 30);
