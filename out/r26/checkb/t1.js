// The ten-second test: open Learn, choose "A whole shape" by hand, and let it play by itself. A picture of the
// whole window about every half second, with the time since the click and what the page says at that moment.
//@ shot=out/r26/checkb/NAME-a-opened.png
return { title: document.title, learnTab: $('mode-l') ? $('mode-l').textContent.trim() : null };
//@ sleep=0.5 shot=out/r26/checkb/NAME-b-learn.png
await openLearn();
return { follow: [...document.querySelectorAll('#learnFollow .seg span')].map(s => s.textContent), panelHead: document.querySelector('#learnFollow').closest('details').querySelector('summary').textContent };
//@
window.__t0 = performance.now();
await pickShape();
return { clicked: true, ...said() };
//@ repeat=52 sleep=0.33 shot=out/r26/checkb/NAME-play-##.png
return { i: __I__, t: Math.round(performance.now() - window.__t0), ...said() };
//@ shot=out/r26/checkb/NAME-z-end.png
return { t: Math.round(performance.now() - window.__t0), ...said(), state: brief(L.shape.state()) };
