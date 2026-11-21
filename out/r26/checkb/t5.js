// The phone, the reader's way: find Learn, find "A whole shape", watch it play, then use every control of the
// transport. Whole-window pictures, so that what is in reach without scrolling is what the picture shows.
//@ shot=out/r26/checkb/NAME-a-opened.png
return { w: innerWidth, h: innerHeight, scrollY: Math.round(scrollY), docH: document.documentElement.scrollHeight };
//@ sleep=0.4 shot=out/r26/checkb/NAME-b-learn-tab-found.png
$('mode-l').scrollIntoView({ block: 'center' }); await sleep(200);
return { scrollY: Math.round(scrollY), tab: box('mode-l') };
//@ sleep=0.5 shot=out/r26/checkb/NAME-c-learn-on.png
$('mode-l').click(); await sleep(300);
return { scrollY: Math.round(scrollY), follow: box('learnFollow'), stage: box('stage') };
//@ sleep=0.3 shot=out/r26/checkb/NAME-d-follow-found.png
$('learnFollowShape').scrollIntoView({ block: 'center' }); await sleep(200);
return { scrollY: Math.round(scrollY), follow: box('learnFollow'), stage: box('stage'), bar: box('learnBar') };
//@
window.__t0 = performance.now();
$('learnFollowShape').click(); await frame();
return { scrollY: Math.round(scrollY), stage: box('stage'), bar: box('learnShapeBar'), ...said() };
//@ repeat=14 sleep=0.33 shot=out/r26/checkb/NAME-play-##.png
return { i: __I__, t: Math.round(performance.now() - window.__t0), scrollY: Math.round(scrollY), stage: box('stage'), bar: box('learnShapeBar'), say: box('learnShapeSay'), pos: box('learnShapePos'), play: box('learnShapePlay'), ...said() };
//@ sleep=0.4 shot=out/r26/checkb/NAME-e-top.png
// back to the top of the page, as a reader who wants the picture and its buttons
L.shape.pause(); scrollTo(0, 0); await sleep(300);
const vis = id => { const b = $(id).getBoundingClientRect(); return b.top >= 0 && b.bottom <= innerHeight && b.width > 0; };
return { scrollY: Math.round(scrollY), stage: box('stage'), bar: box('learnShapeBar'), inWindow: { stage: vis('stage'), say: vis('learnShapeSay'), slider: vis('learnShapePos'), play: vis('learnShapePlay'), back: vis('learnShapeBack'), fwd: vis('learnShapeFwd'), again: vis('learnShapeAgain'), kinds: vis('learnShapeKindBar'), spaces: vis('learnShapeSpaceBar'), speed: vis('learnShapeSpeed') },
  sizes: { play: box('learnShapePlay'), back: box('learnShapeBack'), fwd: box('learnShapeFwd'), again: box('learnShapeAgain'), kinds: box('learnShapeKindBar'), spaces: box('learnShapeSpaceBar'), tick: box($('learnShapeTicks').children[3]), speed: box('learnShapeSpeed') } };
//@ sleep=0.4 shot=out/r26/checkb/NAME-f-stage-in-view.png
// the picture and everything under it, scrolled so that the stage is at the top of the window
$('stage').scrollIntoView({ block: 'start' }); await sleep(300);
const vis = id => { const b = $(id).getBoundingClientRect(); return b.top >= 0 && b.bottom <= innerHeight && b.width > 0; };
return { scrollY: Math.round(scrollY), stage: box('stage'), bar: box('learnShapeBar'), inWindow: { stage: vis('stage'), say: vis('learnShapeSay'), slider: vis('learnShapePos'), play: vis('learnShapePlay'), kinds: vis('learnShapeKindBar'), spaces: vis('learnShapeSpaceBar') } };
//@ sleep=0.5 shot=out/r26/checkb/NAME-g-both-00.png
kindBar('both'); $('learnShapeAgain').click(); await frame(); return { ...said(), sayBox: box('learnShapeSay'), sayScroll: [$('learnShapeSay').scrollHeight, $('learnShapeSay').clientHeight], pos: box('learnShapePos') };
//@ sleep=0.4 shot=out/r26/checkb/NAME-g-both-00.5.png
L.shape.goto(0.5); await frame(); return { ...said(), sayBox: box('learnShapeSay'), sayScroll: [$('learnShapeSay').scrollHeight, $('learnShapeSay').clientHeight], pos: box('learnShapePos') };
//@ sleep=0.5 shot=out/r26/checkb/NAME-g-both-03.png
$('learnShapeTicks').children[3].click(); await frame(); return { ...said(), sayBox: box('learnShapeSay'), sayScroll: [$('learnShapeSay').scrollHeight, $('learnShapeSay').clientHeight], pos: box('learnShapePos') };
//@ sleep=0.45 shot=out/r26/checkb/NAME-g-both-03.4.png
L.shape.goto(3.4); await frame(); return { ...said(), sayBox: box('learnShapeSay'), sayScroll: [$('learnShapeSay').scrollHeight, $('learnShapeSay').clientHeight], pos: box('learnShapePos') };
//@ sleep=0.5 shot=out/r26/checkb/NAME-g-both-16.png
$('learnShapeTicks').children[16].click(); await frame(); return { ...said(), sayBox: box('learnShapeSay'), sayScroll: [$('learnShapeSay').scrollHeight, $('learnShapeSay').clientHeight], pos: box('learnShapePos') };
//@ sleep=0.5 shot=out/r26/checkb/NAME-h-julia-05.png
kindBar('j'); $('learnShapeTicks').children[5].click(); await frame(); return said();
//@ sleep=1.2 shot=out/r26/checkb/NAME-i-3d-m-00.png
kindBar('m'); $('learnShapeAgain').click(); spaceBar(3); await frame(); return { ...said(), hint: $('learnHint').textContent };
//@ sleep=1.0 shot=out/r26/checkb/NAME-i-3d-m-03.png
$('learnShapeTicks').children[3].click(); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-i-3d-m-03.4.png
L.shape.goto(3.4); await frame(); return said();
//@ sleep=1.0 shot=out/r26/checkb/NAME-i-3d-m-08.png
$('learnShapeTicks').children[8].click(); await frame(); return said();
//@ sleep=1.0 shot=out/r26/checkb/NAME-j-3d-both-05.png
kindBar('both'); $('learnShapeTicks').children[5].click(); await frame(); return { ...said(), panes: L.shape.state().panes, side: L.shape.state().side };
//@ sleep=1.0 shot=out/r26/checkb/NAME-k-3d-both-turned-zoomed.png
// one finger turns, two fingers pinch (scripted touches)
const cv = $('learnShapeCanvas'), t = (type, id, x, y) => ptr(cv, type, x, y, { pointerId: id, pointerType: 'touch' });
t('pointerdown', 21, 180, 60); for (let i = 1; i <= 10; i++) { t('pointermove', 21, 180 + 8 * i, 60 + 3 * i); await frame(); } t('pointerup', 21, 260, 90);
await sleep(200);
t('pointerdown', 31, 150, 60); t('pointerdown', 32, 210, 60);
for (let i = 1; i <= 10; i++) { t('pointermove', 31, 150 - 3 * i, 60); t('pointermove', 32, 210 + 3 * i, 60); await frame(); }
t('pointerup', 31, 120, 60); t('pointerup', 32, 240, 60); await sleep(300);
return { view3: L.shape.state().view3, reset: box('learnShapeViewReset'), unpin: [...document.querySelectorAll('button')].filter(b => /pin/i.test(b.textContent) && b.getBoundingClientRect().width > 0).map(b => [b.textContent.trim(), box(b)]) };
//@ sleep=0.4 shot=out/r26/checkb/NAME-l-panel-1.png
// the panel under the transport, as the reader scrolls down
$('learnFollow').scrollIntoView({ block: 'start' }); await sleep(250); return { scrollY: Math.round(scrollY), stage: box('stage') };
//@ sleep=0.4 shot=out/r26/checkb/NAME-l-panel-2.png
scrollBy(0, 420); await sleep(250); return { scrollY: Math.round(scrollY), stage: box('stage') };
//@ sleep=0.4 shot=out/r26/checkb/NAME-l-panel-3.png
scrollBy(0, 420); await sleep(250); return { scrollY: Math.round(scrollY), stage: box('stage') };
//@ sleep=0.4 shot=out/r26/checkb/NAME-l-panel-4.png
scrollBy(0, 420); await sleep(250); return { scrollY: Math.round(scrollY), stage: box('stage'), pageWidth: document.documentElement.scrollWidth };
