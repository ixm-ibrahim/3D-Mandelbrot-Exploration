// helpers every step of out/r26/final/*.js starts with (see run_final.py). The final look's own; nothing shared.
const LAB = window.squaringLab, L = LAB.learn, S = LAB.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const frame = () => new Promise(r => requestAnimationFrame(() => r()));
const fail = m => { throw new Error(m); };
const r2 = x => +(+x).toFixed(2), r3 = x => +(+x).toFixed(3);
const refresh = () => { LAB.syncControls(); LAB.refresh(false); LAB.touch(); };
const AP = () => LAB.APPROACHES[S.approach];
// what stands on the page, read from the page itself
const page = () => ({ where: $('learnShapeWhere').textContent, say: $('learnShapeSay').textContent, play: $('learnShapePlay').textContent, slider: +$('learnShapePos').value });
// the reader's way in: the Learn tab, then "A whole shape" by its own radio (the first time it plays by itself)
const openLearn = async () => { if (!document.body.classList.contains('is-learn')) { $('mode-l').click(); await sleep(300); } };
const openShape = async () => { await openLearn(); if (L.follow !== 'shape') { $('learnFollowShape').click(); await frame(); } L.shape.pause(); $('learnShapeAgain').click(); await sleep(150); };
const kindBar = v => document.querySelector('input[name=learnShapeKindBar][value=' + v + ']').click();
const spaceBar = v => document.querySelector('input[name=learnShapeSpaceBar][value="' + v + '"]').click();
const tick = k => $('learnShapeTicks').children[k].click();
const slider = async v => { const e = $('learnShapePos'); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); await frame(); };
const approach = async id => { if (AP().id !== id) { const b = $('ap-' + id); if (!b) fail('no approach button ' + id); b.click(); await sleep(250); } if (AP().id !== id) fail('could not choose ' + id); return AP().name; };
const box = e => { const b = (typeof e === 'string' ? $(e) : e).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; };
// the finished picture: ask for the state (which draws a waiting fine picture) and give the graphics card a moment
const rest = async ms => { await sleep(ms === undefined ? 450 : ms); const s = L.shape.state(); await sleep(300); return s; };
const lv = l => (l ? l.map(x => x.k + ':a' + (+x.alpha).toFixed(2) + (x.tint ? ':t' + (+x.tint).toFixed(2) : '') + (x.solid ? ':s' + (+x.solid).toFixed(2) : '')).join(' ') : null);
// the 3D picture's own pixels, shrunk: the share that is not stage colour, and the share that is clearly red (warning colour)
const look3 = () => {
  const c = document.querySelector('canvas.learn-shape-gl'); if (!c || c.hidden) return null;
  const W = 240, H = Math.max(2, Math.round(240 * c.height / c.width)), t = document.createElement('canvas'); t.width = W; t.height = H;
  const g = t.getContext('2d', { willReadFrequently: true }); g.drawImage(c, 0, 0, W, H);
  const d = g.getImageData(0, 0, W, H).data, b = [d[0], d[1], d[2]]; let n = 0, red = 0;
  for (let i = 0; i < d.length; i += 4) { if (Math.abs(d[i] - b[0]) + Math.abs(d[i + 1] - b[1]) + Math.abs(d[i + 2] - b[2]) > 12) { n++; if (d[i] - d[i + 1] > 55 && d[i] - d[i + 2] > 40 && d[i + 1] < 0.62 * d[i]) red++; } }
  return { cover: +(n / (W * H)).toFixed(4), red: n ? +(red / n).toFixed(3) : 0 };
};
