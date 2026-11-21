// Every sentence the feature can put on the page: read from the page (not from the code) at every whole step and
// between every two, for every choice, and in the odd cases (other powers, a modifier, another equation, a c
// outside the big circle or off the flat plane, an approach that does not keep the flat picture).
//@
await openLearn(); await pickShape(); L.shape.pause(); L.shape.goto(0);
window.__all = {};
window.__grab = async tag => {
  const out = window.__all[tag] = {};
  const add = (k, v) => { if (v) (out[k] = out[k] || new Set()).add(v); };
  for (let p = 0; p <= 16; p += 0.5) {
    L.shape.set({ pos: p }); await frame();
    const s = said();
    add('say', s.say.replace(/\d+/g, 'N')); add('where', s.where.replace(/\d+/g, 'N'));
    add('valuetext', ($('learnShapePos').getAttribute('aria-valuetext') || '').replace(/\d+/g, 'N'));
    if (p === 0 || p === 0.5 || p === 1 || p === 16) add('say-exact', 'pos ' + p + ': ' + s.say);
  }
  add('hint', $('learnHint').hidden ? '(hidden)' : $('learnHint').textContent);
  add('rule', $('learnShapeRule').offsetParent ? $('learnShapeRule').textContent : '');
  add('notice', $('learnShapeNotice').textContent);
  add('note', $('learnShapeNote').hidden ? '' : $('learnShapeNote').textContent);
  add('eqNote', L.el && L.el.eqNote && !L.el.eqNote.hidden ? L.el.eqNote.textContent : '');
  add('helpJ', $('learnShapeHelpJ').textContent);
  add('again', $('learnShapeAgain').title);
  add('named', [...document.querySelectorAll('#learnShapeCs button')].map(b => [...b.children].filter(c => !c.hidden).map(c => c.textContent).join('') || b.textContent).join(' | '));
  add('dials', [...document.querySelectorAll('#learnShapeDials > *')].filter(e => e.getBoundingClientRect().height > 0).map(e => (e.querySelector('.label') || e).textContent.trim()).join(' | '));
  for (const k in out) out[k] = [...out[k]];
  return out;
};
return 'ready';
//@
const res = {};
for (const space of [2, 3]) for (const kind of ['m', 'j', 'both']) { L.shape.set({ kind, space, c: [-0.4, 0.3, 0] }); await sleep(150); res[kind + space] = await window.__grab('plain ' + kind + space); }
return res;
//@
// odd cases
const go = () => { LAB.syncControls(); LAB.refresh(false); LAB.touch(); };
const res = {};
S.n = 3; go(); for (const space of [2, 3]) { L.shape.set({ kind: 'both', space }); await sleep(150); res['power3 both' + space] = await window.__grab('p3 ' + space); }
S.n = 2.5; go(); L.shape.set({ kind: 'm', space: 2 }); await sleep(150); res['power2.5 m2'] = await window.__grab('p2.5');
S.n = -2; go(); for (const space of [2, 3]) for (const kind of ['m', 'j', 'both']) { L.shape.set({ kind, space }); await sleep(150); res['power-2 ' + kind + space] = await window.__grab('p-2 ' + kind + space); }
S.n = 2; go();
return res;
//@
const go = () => { LAB.syncControls(); LAB.refresh(false); LAB.touch(); };
const res = {};
S.abs[0] = true; go(); L.shape.set({ kind: 'both', space: 2 }); await sleep(150); res['abs-x both2'] = await window.__grab('absx');
S.abs[0] = false; go();
L.shape.set({ kind: 'j', space: 2, c: [2.2, 0.9, 0] }); await sleep(150); res['c outside the big circle j2'] = await window.__grab('cout j2');
L.shape.set({ kind: 'both', space: 2, c: [2.2, 0.9, 0] }); await sleep(150); res['c outside the big circle both2'] = await window.__grab('cout both2');
L.shape.set({ kind: 'both', space: 2, c: [0.6, 0.6, 0] }); await sleep(150); res['c outside the Mandelbrot shape both2'] = await window.__grab('cfar both2');
L.shape.set({ kind: 'j', space: 3, c: [-0.4, 0.3, 0.5] }); await sleep(250); res['c off the flat plane j3'] = await window.__grab('cz j3');
L.shape.set({ kind: 'j', space: 3, c: [3, 3, 3] }); await sleep(250); res['c far outside j3'] = await window.__grab('cfar j3');
L.shape.set({ c: [-0.4, 0.3, 0] });
return res;
//@
const res = {};
for (const id of ['classic', 'kleinsq', 'pillow', 'alongonce']) { await approach(id); L.shape.set({ kind: 'm', space: 3, pos: 0 }); await sleep(400); const g = await window.__grab('ap ' + id); res[id] = { rule: g.rule, notice: g.notice, end: g['say-exact'].filter(x => x.startsWith('pos 16')), note: g.note }; }
await approach('mercator');
return res;
//@
// another equation in the equation field: the note that the plain equation is used
const eq = document.querySelector('#eq, #equation, input[name=eq]');
return { eqField: eq ? eq.id : null, eqNoteText: L.el.eqNote ? L.el.eqNote.textContent : null };
