// Round 22, entrycheck second pass: Pulled plane, the thread of c = (-1, 0, 0.3) in the lab itself, beside the same c
// lying in the flat page and a c of the standing page that has an inside.
const pick = async (id, c) => { $('mode-j').click(); await sleep(150); $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 40; S.c = c.slice(); S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; Object.assign(S.param.pulledplane, { hold: 0.05, ease: 0.7, cpull: 16 }); L.resetCam(); go(); await settle(); };
const hits = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight, PX = 90, PY = 68, ay = [], az = []; for (let j = 0; j < PY; j++) for (let i = 0; i < PX; i++) { const p = L.pick(w * (i + 0.5) / PX, h * (j + 0.5) / PY); if (p) { ay.push(Math.abs(p[1])); az.push(Math.abs(p[2])); } } ay.sort((a, b) => a - b); az.sort((a, b) => a - b); const med = a => (a.length ? a[a.length >> 1] : NaN); return ay.length + ' of ' + PX * PY + ' probes stop; their distance from the plane y = 0: median ' + med(ay).toFixed(3) + ', largest ' + (ay[ay.length - 1] || NaN).toFixed(3) + '; from the plane z = 0: median ' + med(az).toFixed(3) + ', largest ' + (az[az.length - 1] || NaN).toFixed(3); };
//@@STEP shot: out/r22/entrycheck2/break/pp-thread-standing.png
await pick('pulledplane', [-1, 0, 0.3]);
return 'Pulled plane, c = (-1, 0, 0.3): ' + hits();
//@@STEP shot: out/r22/entrycheck2/break/pp-thread-lying.png
await pick('pulledplane', [-1, 0.3, 0]);
return 'Pulled plane, c = (-1, 0.3, 0), the same c lying in the flat page: ' + hits();
//@@STEP shot: out/r22/entrycheck2/break/pp-standing-body.png
await pick('pulledplane', [-1, 0, 0.2]);
return 'Pulled plane, c = (-1, 0, 0.2): ' + hits();
//@@STEP shot: out/r22/entrycheck2/break/pp-lying-body.png
await pick('pulledplane', [-1, 0.2, 0]);
return 'Pulled plane, c = (-1, 0.2, 0): ' + hits();
//@@STEP shot: out/r22/entrycheck2/break/ao-standing.png
await pick('alongonce', [-1, 0, 0.2]);
return 'Along once, c = (-1, 0, 0.2): ' + hits();
//@@STEP
S.c = [-1, 0, 0]; S.iter = 30; go(); await settle(); return 'done';
