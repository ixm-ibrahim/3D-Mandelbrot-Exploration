// Round 27, final, merge rehearsal: round 26's Learn ("A whole shape") in one page with the overlay.
// Does it start, in 3D and 2D, with Balls on balls behind it, and does the row Balls on balls still leave Learn?
const r = { hasShape: !!(L.learn && L.learn.shape), has3d: !!L.learnShape3d, hasBalls: typeof L.ballsInside === 'function' };
if (!r.hasShape) return JSON.stringify(r);
const st = () => { const s = L.learn.shape.state(); return { on: s.on, kind: s.kind, space: s.space, threeOk: s.threeOk, panes: (s.panes || []).length, steps: s.steps, note: (s.note || '').slice(0, 140), sentence: (s.sentence || '').slice(0, 140) }; };
const page = () => ({ learn: !!S.learn, mode: S.mode, group: S.k.group, approachSectionShown: vis($('secApproach')), ballsPartShown: vis($('ballsPart')), tableNoteShown: vis($('ballsCardNote')), tableShown: vis($('card')), body: document.body.className });
$('ap-balls').click(); await settle(); r.balls = page();
$('mode-l').click(); await sleep(900); r.learnFromBalls = page();
L.learn.shape.set({ on: true, kind: 'both', space: 3 }); await sleep(3500); r.wholeShape3D = st(); r.pageThen = page();
L.learn.shape.set({ space: 2 }); await sleep(1200); r.wholeShape2D = st();
L.learn.shape.set({ space: 3 }); await sleep(1500);
return JSON.stringify(r);
