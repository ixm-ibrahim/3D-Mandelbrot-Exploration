// Round 27, final, merge rehearsal, second step (the page is under Learn with "A whole shape" on, 3D):
// the row Balls on balls chosen from there, Learn again, Show: Kleinian, Reset everything.
const page = () => ({ learn: !!S.learn, mode: S.mode, group: S.k.group, approachSectionShown: vis($('secApproach')), ballsPartShown: vis($('ballsPart')), tableNoteShown: vis($('ballsCardNote')), tableShown: vis($('card')), body: document.body.className,
  shapeOn: L.learn.shape.state().on, status: $('status').textContent });
const r = { before: page() };
$('ap-balls').click(); await settle(); r.afterTheRow = page();
$('mode-l').click(); await sleep(900); r.learnAgain = page();
$('mode-k').click(); await settle(); r.kleinianAgain = page();
$('kleinGroup0').click(); await settle(); r.firstGroup = page();
$('mode-l').click(); await sleep(900); r.learnFromFirstGroup = page();
$('mode-m').click(); await settle(); r.mandelbrot = page();
$('resetAll').click(); await settle(); r.afterResetEverything = page();
return JSON.stringify(r);
