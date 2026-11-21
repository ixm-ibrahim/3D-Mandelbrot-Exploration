// Every sentence the transport can show, read back from the page: for each kind, in 2D and 3D, at step 0, between
// 0 and 1, at 1, between two later steps, at a middle step and at the last one; and the special cases (a power that
// is not a whole number, a negative power where nothing is left, modifiers, a c outside the big circle).
// The words the round forbids on the page are looked for in everything "A whole shape" puts on the page.
//@
await shapeOn({ kind: 'm', space: 2, pos: 0, c: [-0.1226, 0.7449, 0] });
const out = {}, at = [0, 0.5, 1, 4.5, 7, 16];
const read = async (label) => { for (const kind of ['m', 'j', 'both']) for (const space of [2, 3]) { L.shape.set({ kind, space }); const row = []; for (const p of at) { const s = L.shape.set({ pos: p }); await sleep(30); row.push(p + ': ' + L.shape.state().sentence + '  [' + $('learnShapeWhere').textContent + ']'); } out[label + ' / ' + kind + ' / ' + space + 'D'] = row; } };
await read('power 2');
S.n = 2.5; go(); await sleep(100); L.shape.set({ kind: 'm', space: 2 }); out['power 2.5 / m / 2D / 16'] = L.shape.set({ pos: 16 }).sentence;
S.n = -2; go(); await sleep(100); out['power -2 / m / 2D'] = [0.5, 1, 16].map(p => { L.shape.set({ pos: p }); return p + ': ' + L.shape.state().sentence; });
L.shape.set({ kind: 'both' }); out['power -2 / both / 2D / 1'] = L.shape.set({ pos: 1 }).sentence;
S.n = 3; go(); await sleep(100); L.shape.set({ kind: 'both', space: 2 }); out['power 3 / both / 2D / 16'] = L.shape.set({ pos: 16 }).sentence;
S.n = 2; S.abs = [1, 0, 0]; go(); await sleep(100); out['power 2 with |x| / m / 2D / 16'] = L.shape.set({ kind: 'm', pos: 16 }).sentence;
S.abs = [0, 0, 0]; go(); await sleep(100);
out['c outside the big circle / j / 2D / 16'] = L.shape.set({ kind: 'j', c: [2.2, 1, 0], pos: 16 }).sentence;
out['c outside the big circle / both / 2D / 16'] = L.shape.set({ kind: 'both', pos: 16 }).sentence;
L.shape.set({ c: [-0.1226, 0.7449, 0] });
// zoomed in on a place where nothing is left: the sentence must not say that nothing is left anywhere
L.shape.set({ kind: 'm', space: 2, pos: 8 });
const st = $('stage'), r = st.getBoundingClientRect();
for (let i = 0; i < 5; i++) st.dispatchEvent(new WheelEvent('wheel', { deltaY: -400, bubbles: true, cancelable: true, clientX: r.left + 80, clientY: r.top + 80 }));
await sleep(400);
out['zoomed in on an empty corner / m / 2D / 8'] = L.shape.state().sentence + '  (zoom ' + L.shape.state().view2.m.zoom.toFixed(1) + ')';
$('learnShapeViewReset').click(); await sleep(200);
// the forbidden words, looked for in everything of this part that is on the page (panel, transport, stage)
const text = [...document.querySelectorAll('#learnPanel, #learnShapeBar, #learnShapeNote, #learnHint')].map(e => e.innerText).join(' ') + ' ' + Object.values(out).flat().join(' ')
  + ' ' + [...document.querySelectorAll('#learnShapeBar [title], #learnShapeBar [aria-label], #learnShapeCanvas')].map(e => (e.title || '') + ' ' + (e.getAttribute('aria-label') || '')).join(' ');
const banned = ['iterate', 'iteration', 'escape', 'bailout', 'radius of escape', 'preimage', 'level set', 'orbit count', 'potential', 'membership', 'sample', 'voxel', 'shader', 'mesh', 'render'];
const found = banned.filter(w => new RegExp('\\b' + w, 'i').test(text));
const longest = Math.max(...Object.values(out).flat().map(s => String(s).replace(/^\S+: /, '').replace(/  \[.*$/, '').length));
return { sentences: out, forbiddenWordsFound: found, longestSentence: longest, oddities: Object.values(out).flat().filter(s => /undefined|NaN|null/.test(s)) };
