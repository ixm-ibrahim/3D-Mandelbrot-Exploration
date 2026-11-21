//# wait=done timeout=300
const L = window.squaringLab; L.S.q.aa = 4; L.touch(); return 'default';
//# wait=done timeout=300
const L = window.squaringLab; L.S.n = 3; L.cam.target = [0, 0, 0]; L.cam.dist = 6; L.refresh(false); return 'n = 3 (first use of the pw program)';
//# wait=done timeout=300
const L = window.squaringLab; L.S.n = -2; L.refresh(false); return 'n = -2 (same program, inside-out)';
//# wait=done timeout=300
const L = window.squaringLab; L.cam.dist = 6.01; L.touch(); return 'n = -2 again, camera nudged';
//# wait=done timeout=300
const L = window.squaringLab; L.S.n = 3; L.refresh(false); return 'n = 3 again';
//#
return document.getElementById('status').textContent;
