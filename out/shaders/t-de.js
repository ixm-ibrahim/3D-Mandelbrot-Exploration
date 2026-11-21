//# wait=done timeout=120 shot=out/shaders/g-de3.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 4; L.S.q.de = 3; L.touch(); return 'de 3 (exact)';
//# wait=done timeout=120 shot=out/shaders/g-de3-soft.png clip=#stage
const L = window.squaringLab; L.S.q.normals = 'soft'; L.touch(); return 'de 3, sampled slope';
//# wait=done timeout=120 shot=out/shaders/g-de1.png clip=#stage
const L = window.squaringLab; L.S.q.normals = 'sharp'; L.S.q.de = 1; L.touch(); return 'de 1 (one neighbour)';
//# wait=done timeout=120 shot=out/shaders/g-de0.png clip=#stage
const L = window.squaringLab; L.S.q.de = 0; L.touch(); return 'de 0 (rough)';
