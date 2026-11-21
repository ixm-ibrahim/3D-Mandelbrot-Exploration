//#
const L = window.squaringLab, G = L.GLSL();
window.sets = { old: G.OLD, now: G };
return await window.gpuCompare('default, all on', window.sets, {}, 30);
//#
return await window.gpuCompare('default, no shadow/crevices', window.sets, { shadow: false, ao: false }, 30);
//#
const G2 = window.squaringLab.GLSL(), o = { shadow: false, ao: false }, t = {}; for (const [k, P, nt] of [['exact', G2, 3], ['one neighbour', G2, 1], ['rough', G2, 0]]) { let b = 1e9; for (let r = 0; r < 20; r++) b = Math.min(b, await window.gpuTime(P, { ...o, nt, analytic: nt === 3 })); t[k] = b.toFixed(1) + ' ms'; } return 'default, no shadow/crevices, by distance mode: ' + JSON.stringify(t);
