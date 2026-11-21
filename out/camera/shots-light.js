const L = window.squaringLab, S = L.S, cam = L.cam, c = document.getElementById('view');
const $ = id => document.getElementById(id);
//# wait=done shot=out/camera/21-light-a.png clip=#stage
S.q.aa = 3; document.getElementById('ap-mercator').click(); L.resetCam(); L.touch();
const st = document.getElementById('stage').getBoundingClientRect(), box = id => { const b = $(id).getBoundingClientRect(); return [Math.round(b.left - st.left), Math.round(b.top - st.top), Math.round(b.width), Math.round(b.height)]; };
return { stage: [Math.round(st.width), Math.round(st.height)], mode: box('camMode'), zoom: box('camZoom'), rail: box('camRail'), near: box('camNear'), far: box('camFar'), btns: (() => { const b = document.querySelector('.stage-btns').getBoundingClientRect(); return [Math.round(b.left - st.left), Math.round(b.top - st.top), Math.round(b.width), Math.round(b.height)]; })(), scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth };
//# wait=done shot=out/camera/21-light-b.png clip=#stage
$('camFly').click(); return 'fly';
