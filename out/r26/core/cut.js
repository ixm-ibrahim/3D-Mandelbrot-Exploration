// The sentence "cutting the 3D shape through the middle (at z = 0) gives exactly the 2D shape of the same step" is
// shown only when the page has checked it for the approach on show. Here: which approaches get the sentence, and a
// finer count of my own for each (learnShape3d.out at z = 0 against LEARN.shape.out2, 61 x 61 points, both kinds).
// Run on the page with builder "three"'s module.
//@
const s = await shapeOn({ kind: 'both', space: 3, pos: 4, c: [-0.1226, 0.7449, 0] });
const T = LAB.learnShape3d, rows = [];
const count = c => { let bad = 0, n = 0; for (const kind of ['m', 'j']) for (let i = 0; i < 61; i++) for (let j = 0; j < 61; j++) { const p = [-2 + (i + 0.29) * 4 / 61, -2 + (j + 0.53) * 4 / 61, 0]; if (Math.hypot(p[0], p[1]) > 2) continue; n++; if (T.out(p, kind, c, 16) !== L.shape.out2(p, kind, c, 16)) bad++; } return [bad, n]; };
for (const a of LAB.APPROACHES) {
  $('ap-' + a.id).click(); await sleep(250);
  if (LAB.APPROACHES[S.approach].id !== a.id) fail('could not choose ' + a.id);
  S.n = 2; go(); await sleep(100);
  L.shape.set({ c: [-0.1226, 0.7449, 0] });
  const said = $('learnShapeNotice').textContent.includes('cutting the 3D shape'), cnt = count([-0.1226, 0.7449, 0]);
  L.shape.set({ c: [-0.1226, 0.7449, 0.2] });
  const saidOff = $('learnShapeNotice').textContent.includes('cutting the 3D shape');
  const st = L.shape.state();
  rows.push({ id: a.id, name: a.name, sentenceShown: said, differ: cnt[0] + ' of ' + cnt[1], sentenceWithCOffThePlane: saidOff, note: st.note, sentence0: st.sentence.slice(0, 60) });
  if (said && cnt[0] > 2) fail(a.id + ': the sentence is shown but ' + cnt[0] + ' points differ');
  if (saidOff) fail(a.id + ': the sentence must go when c leaves the flat plane (Both is on show)');
}
$('ap-mercator').click(); await sleep(250);
// a dial that breaks the flat picture (the lift of "Sphere inversions, one plane"): the sentence must go
L.shape.set({ c: [-0.1226, 0.7449, 0] });
const before = $('learnShapeNotice').textContent.includes('cutting the 3D shape');
const keys = Object.keys(S.param.mercator);
S.param.mercator.lift = 0.3; go(); await sleep(150);
const lifted = $('learnShapeNotice').textContent.includes('cutting the 3D shape'), cntL = count([-0.1226, 0.7449, 0]);
S.param.mercator.lift = 0; go(); await sleep(150);
// the Mandelbrot shape alone needs no c in the plane
L.shape.set({ kind: 'm', c: [0.1, 0.1, 0.9] });
const mAlone = $('learnShapeNotice').textContent;
return { rows: rows.map(r => r.id + ': ' + (r.sentenceShown ? 'SHOWN' : 'not shown') + ', ' + r.differ + ' differ' + (r.note ? ', NOTE ' + r.note : '')), mercatorDials: keys, withLift0: before, withLift0_3: lifted, differWithLift: cntL.join(' of '), mandelbrotAlone: mAlone };
