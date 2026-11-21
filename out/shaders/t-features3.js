//# wait=done timeout=240
const L = window.squaringLab; L.S.q.aa = 3; L.touch();
const st = document.getElementById('stage'), w = st.clientWidth, h = st.clientHeight;
const fmt = p => p ? p.map(x => x.toFixed(3)).join(', ') : 'null';
window.fmtP = fmt;
return 'pick 3D at centre: ' + fmt(L.pick(w / 2, h / 2)) + ' | at corner: ' + fmt(L.pick(5, 5)) + ' | camera distance ' + L.cam.dist;
//#
const L = window.squaringLab; L.S.flat = true; L.S.v2 = { x: -0.5, y: 0, h: 3.2 };
const st = document.getElementById('stage'), w = st.clientWidth, h = st.clientHeight;
const a = L.pick(w / 2, h / 2), b = L.pick(0, 0), c = L.pick(w, h);
L.S.cut = 0.25; const d = L.pick(w / 2, h / 2); L.S.cut = 0; L.S.flat = false;
return 'pick 2D centre: ' + window.fmtP(a) + ' (want -0.5, 0, 0) | top left: ' + window.fmtP(b) + ' (want y = +1.6) | bottom right: ' + window.fmtP(c) + ' | slice at 0.25: ' + window.fmtP(d);
//# wait=done timeout=240 shot=out/shaders/b-bound1.png clip=#stage
const L = window.squaringLab; L.S.view.bound = 1; L.touch(); return 'drawing radius 1';
//# wait=done timeout=240 shot=out/shaders/b-bound200.png clip=#stage
const L = window.squaringLab; L.S.view.bound = 200; L.S.view.zmax = 1000; L.cam.dist = 40; L.touch(); return 'drawing radius 200, camera at 40';
//# wait=done timeout=240 shot=out/shaders/b-klein-wide.png clip=#stage
const L = window.squaringLab; L.S.mode = 'k'; L.resetCam(); L.S.k.invR = 3; L.cam.dist = 30; L.refresh(false); return 'kleinian, big inversion sphere, radius 200';
//# wait=done timeout=240 shot=out/shaders/b-klein-wide8.png clip=#stage
const L = window.squaringLab; L.S.view.bound = 8; L.touch(); return 'same with drawing radius 8';
