//#
const L = window.squaringLab, G = L.GLSL(), S = window.subAll;
window.sets = {
  old: G.OLD,
  now: G,
  'light queries use three neighbours': { ...G, GL_TAIL: S(G.GL_TAIL, 'qn = min(nt, 1);', 'qn = nt;') },
};
return await window.gpuCompare('default, all on', window.sets);
//#
return await window.gpuCompare('default, shadow only', window.sets, { ao: false });
//#
return await window.gpuCompare('default, crevices only', window.sets, { shadow: false });
