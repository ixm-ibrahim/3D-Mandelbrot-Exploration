// Before the steps of point.js: go to "A whole shape", use it, and come back to "One point" by the page's own
// controls. After that the one-point pictures must still be the frozen page's.
//@
$('mode-l').click(); await sleep(400);
$('learnFollowShape').click(); await sleep(600);
if (!L.shape.state().on) fail('A whole shape did not come on');
L.shape.set({ kind: 'both', pos: 3.5, c: [-1, 0, 0] }); await sleep(200);
$('stage').dispatchEvent(new WheelEvent('wheel', { deltaY: -300, bubbles: true, cancelable: true, clientX: 300, clientY: 400 })); await sleep(200);
$('learnFollowPoint').click(); await sleep(400);
if (L.follow !== 'point' || document.body.classList.contains('is-learn-shape')) fail('One point did not come back');
if (shown('learnShapeBar') || shown('learnShapeCanvas') || !shown('learnBar') || !shown('learnCanvas')) fail('the wrong transport or canvas is on show');
$('mode-m').click(); await sleep(400);
return 'went to A whole shape and back, then left Learn';
//@ wait=done timeout=110
return 'ready';
