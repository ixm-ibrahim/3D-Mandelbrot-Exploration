// A reader who has asked for reduced motion, on a fresh page: the first switch to "A whole shape" does not play
// by itself. (The media query is answered by hand: the test tool can only set the colour theme.)
//@
const mm = window.matchMedia.bind(window);
window.matchMedia = q => (String(q).includes('prefers-reduced-motion') ? { matches: true, media: q, addEventListener() {}, removeEventListener() {} } : mm(q));
$('mode-l').click(); await sleep(400);
$('learnFollowShape').click(); await sleep(700);
const a = L.shape.state();
if (!a.on) fail('A whole shape should be on');
if (a.playing || a.pos !== 0) fail('with reduced motion nothing should play by itself: ' + JSON.stringify([a.playing, a.pos]));
// Play is still there for the asking
$('learnShapePlay').click(); await sleep(500);
const b = L.shape.state();
L.shape.pause();
if (!(b.pos > 0)) fail('Play should still play when it is pressed');
return { afterTheSwitch: { playing: a.playing, pos: a.pos }, afterPlayWasPressed: +b.pos.toFixed(2) };
