// W2, M12: the Learn panel as it reads with "A whole shape" on, as pictures (run at --size 1400x2000 so that the
// whole panel is in the window): Both on the 2D page, then the Julia shape in 3D. On the page as joined
// (--page r26-fix-before --log before-panel) and on the mended page (--log after-panel).
//@ sleep=0.4 shot=out/r26/fix/NAME-2d-both.png clip=#learnPanel
await openShape(); kindBar('both'); await sleep(200); tick(3); await sleep(200);
return { note: $('learnShapeIntro').textContent, helps: [...document.querySelectorAll('.learn-kind-help p')].map(p => p.textContent), notice: $('learnShapeNotice').textContent };
//@ sleep=0.6 shot=out/r26/fix/NAME-3d-julia.png clip=#learnPanel
kindBar('j'); spaceBar(3); await sleep(1000);
return { rule: $('learnShapeRule').textContent, notice: $('learnShapeNotice').textContent, named: [...document.querySelectorAll('#learnShapeCs button')].map(b => b.textContent) };
//@ sleep=0.6 shot=out/r26/fix/NAME-3d-julia-stage.png clip=.bench-main
// and the stage with its transport in 3D, Julia shape: the hint, and the tooltip of "Start again"
tick(3); await rest(); return { hint: $('learnHint').textContent, again: $('learnShapeAgain').title };
