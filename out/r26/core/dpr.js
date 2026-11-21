// Screens with more than one device pixel to a CSS pixel (the test tool's window has exactly one), and a stage that
// changes size. The page is told another ratio by hand; the picture must come out the same, only finer.
//@
const s = await shapeOn({ kind: 'both', space: 2, pos: 6.4, c: [-0.1226, 0.7449, 0] });
const cv = $('learnShapeCanvas'), g = cv.getContext('2d');
const share = () => { const d = g.getImageData(0, 0, cv.width, cv.height).data; let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 200 && d[i] > 180 && d[i + 1] > 140 && d[i + 2] < 130) n++; return n / (cv.width * cv.height); };
const rows = [];
for (const r of [1, 1.25, 1.5, 2, 3]) {
  Object.defineProperty(window, 'devicePixelRatio', { get: () => r, configurable: true });
  window.dispatchEvent(new Event('resize'));
  L.shape.set({ pos: 6.4 }); await sleep(250);
  const st = L.shape.state();
  rows.push({ ratio: r, canvas: [cv.width, cv.height], css: [cv.clientWidth, cv.clientHeight], bodyShare: +share().toFixed(5), ms: st.ms.mapLast, samples: st.ms.mapSamples, quality: st.quality });
}
return rows;
//@ sleep=0.3 shot=out/r26/core/dpr-3-both.png clip=#stage
//@
Object.defineProperty(window, 'devicePixelRatio', { get: () => 1, configurable: true });
// the stage changes size (as when the window is resized): the pictures follow
const before = L.shape.state().panes;
$('stage').style.height = '330px'; $('stage').style.width = '520px'; await sleep(500);
const mid = L.shape.state();
$('stage').style.height = '520px'; $('stage').style.width = '300px'; await sleep(500);
const tall = L.shape.state();
return { before, smaller: mid.panes, quality: mid.quality, tallAndNarrow: tall.panes, side: tall.side, sentence: tall.sentence };
//@ sleep=0.3 shot=out/r26/core/dpr-tall-stage.png clip=.bench-main
//@
$('stage').style.height = ''; $('stage').style.width = ''; await sleep(400);
return L.shape.state().panes;
