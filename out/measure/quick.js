// keep the 3D picture cheap so the tests are not waiting on the GPU
const L = window.squaringLab; L.S.q.aa = 1; L.S.q.res = 0.4; L.S.q.shadow = false; L.S.q.ao = false; L.touch(); return 'quick render';
