// The final look: Follow = One point must be the page it was. The same steps on the frozen page (dist/r26-base.html,
// --log point-base) and on dist/r26-final.html (--log point-final): pictures of the stage and of the transport, and
// the state as the test handle gives it. compare_point.py then compares them pixel for pixel and word for word.
// (Nothing here touches "Follow": One point is how the page opens.)
//@ sleep=0.5 shot=out/r26/final/NAME-1-stage.png clip=#stage
// state 1: the Learn tab as it opens, the 2D page, the second move 0.4 of the way
$('mode-l').click(); await sleep(400);
L.goto(1, 0.4); await sleep(300);
const s = L.state();
return { state: 1, space: s.space, step: s.step, move: s.move, t: s.t, z: s.z, z0: s.z0, c: s.c, sentence: s.sentence, moves: s.moves, where: $('learnWhere').textContent, say: $('learnSay').textContent, note: s.note };
//@ sleep=0.2 shot=out/r26/final/NAME-1-bar.png clip=#learnBar
return null;
//@ sleep=0.7 shot=out/r26/final/NAME-2-stage.png clip=#stage
// state 2: 3D space, "Turning plane, along", after two whole steps, the third move 0.6 of the way
$('ap-turnalong').click(); await sleep(300);
$('learnSpace3').click(); await sleep(400);
$('learnNext').click(); await sleep(200); L.next(); await sleep(200);
L.goto(2, 0.6); await sleep(400);
const s = L.state();
return { state: 2, approach: AP().id, space: s.space, step: s.step, move: s.move, t: s.t, z: s.z, z0: s.z0, c: s.c, sentence: s.sentence, moves: s.moves, where: $('learnWhere').textContent, say: $('learnSay').textContent, note: s.note };
//@ sleep=0.2 shot=out/r26/final/NAME-2-bar.png clip=#learnBar
return null;
//@ sleep=0.5 shot=out/r26/final/NAME-3-stage.png clip=#stage
// state 3: the 1D line, power 3, the first move 0.5 of the way
$('learnSpace1').click(); await sleep(300);
S.n = 3; refresh(); await sleep(300);
L.goto(0, 0.5); await sleep(300);
const s = L.state();
return { state: 3, space: s.space, step: s.step, move: s.move, t: s.t, z: s.z, z0: s.z0, c: s.c, sentence: s.sentence, moves: s.moves, where: $('learnWhere').textContent, say: $('learnSay').textContent, note: s.note };
//@ sleep=0.2 shot=out/r26/final/NAME-3-bar.png clip=#learnBar
return null;
//@ sleep=0.4 shot=out/r26/final/NAME-4-window.png
// the whole window, for the eye (the panel differs by design: the choice "Follow" stands at its top)
return { panelTop: document.querySelector('#learnPanel .sec-body').firstElementChild.id || document.querySelector('#learnPanel .sec-body').firstElementChild.className };
