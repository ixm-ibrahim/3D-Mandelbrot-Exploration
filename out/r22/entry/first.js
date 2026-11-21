// Round 22, entry: does the page come up with the two entries, do their programs build in both views, and what do
// the card and the texts say? (HEAD of run.py is in front of this.)
const out = {};
out.ids = L.APPROACHES.map(a => a.id);
out.carry = Object.keys(L.CARRY || {});
for (const id of ['alongonce', 'pulledplane']) {
  const o = out[id] = {};
  const r = $('ap-' + id); if (!r) fail('no entry ' + id);
  $('mode-j').click(); await sleep(150);
  r.click(); await sleep(250);
  if (apId() !== id) fail('choosing ' + id + ' did not take');
  const a = L.APPROACHES[S.approach];
  o.name = a.name; o.group = a.group; o.deMax = a.deMax; o.index = S.approach;
  S.n = 2; S.iter = 40; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; L.resetCam(); go(); await settle();
  o.julia = grid().slice(0, 2);
  $('mode-m').click(); await sleep(150); L.resetCam(); go(); await settle();
  o.mandel = grid().slice(0, 2);
  $('mode-j').click(); await sleep(150); go(); await settle();
  o.param = JSON.stringify(S.param[id]);
  o.formula = a.formula(S.param[id], 2);
  o.formula3 = a.formula(S.param[id], 3);
  o.crush = a.crush(S.param[id], 2); o.smooth = a.smooth(S.param[id], 2); o.smooth25 = a.smooth(S.param[id], 2.5);
  o.slice = [a.slice(true, S.param[id], 2), a.slice(false, S.param[id], 2)];
  o.round = a.roundNote(S.param[id], 2);
  o.card = $('card') ? $('card').innerText.slice(0, 1500) : '';
  o.first = L.MATH[id]([0.3, 0.4, 0.5], 2, S.param[id]);
  o.along = L.MATH.turnalong([0.3, 0.4, 0.5], 2, {});
  o.one = L.MATH.mercator([0.3, 0.4, 0.5], 2, {});
  const plan = L.learnPlan({ space: 3, id, params: S.param[id], n: 2, c: [-1, 0, 0], abs: [0, 0, 0], flip: [0, 0] });
  const run = plan.run([0.3, 0.4, 0.5]);
  o.learn = { moves: plan.moves.map(m => m.name), say: plan.moves.map((m, j) => m.say(run[j], run[j + 1])), check: plan.check([0.3, 0.4, 0.5]), note: plan.note };
}
// the Stretch wording for the other entries that use the generic moves, and one whose length is not the plain power
out.stretch = {};
for (const id of ['turnalong', 'windsq', 'rotorframe', 'sqpillow', 'kleinsq', 'softfold', 'pillow', 'axisbulb', 'quat4', 'rotor']) {
  const a = L.APPROACHES.find(x => x.id === id), q = Object.fromEntries((a.params || []).filter(s => s.key !== undefined).map(s => [s.key, s.def]));
  for (const n of [2, 3, 5, 2.5, -2]) {
    const plan = L.learnPlan({ space: 3, id, params: q, n, c: [0, 0, 0] });
    const pts = [[0.48, 0.64, 0.0].map(x => x * 1.0), [0.9, 0.8, 0.5]];
    out.stretch[id + ' n=' + n] = pts.map(p => { const run = plan.run(p); return plan.moves.map((m, j) => m.name + ': ' + m.say(run[j], run[j + 1])).filter(t => t.startsWith('Stretch')).join(' | ') || '(no Stretch move: ' + plan.moves.map(m => m.name).join(', ') + ')'; });
  }
}
$('resetAll').click(); await sleep(300);
return JSON.stringify(out);
