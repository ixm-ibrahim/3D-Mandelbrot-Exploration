// helpers every step of out/r26/fix/*.js starts with (see frun.py)
const LAB = window.squaringLab, L = LAB.learn, S = LAB.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const frame = () => new Promise(r => requestAnimationFrame(() => r()));
const r1 = x => +(+x).toFixed(1), r3 = x => +(+x).toFixed(3);
const med = a => { const b = a.slice().sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : 0; };
const go = () => { LAB.syncControls(); LAB.refresh(false); LAB.touch(); };
const AP = () => LAB.APPROACHES[S.approach];
// what stands on the page right now, read from the page itself (not from the test handle)
const said = () => ({ where: $('learnShapeWhere').textContent, say: $('learnShapeSay').textContent, play: $('learnShapePlay').textContent, slider: +$('learnShapePos').value });
// the reader's way in: the Learn tab, then "A whole shape" by its own radio (which plays by itself the first time)
const openLearn = async () => { if (!document.body.classList.contains('is-learn')) { $('mode-l').click(); await sleep(300); } };
const pickShape = async () => { $('learnFollowShape').click(); await frame(); };
// in, and standing still at the start (the play that starts by itself is stopped)
const openShape = async () => { await openLearn(); if (L.follow !== 'shape') { await pickShape(); } L.shape.pause(); $('learnShapeAgain').click(); await sleep(150); };
const kindBar = v => { document.querySelector('input[name=learnShapeKindBar][value=' + v + ']').click(); };
const spaceBar = v => { document.querySelector('input[name=learnShapeSpaceBar][value="' + v + '"]').click(); };
const slider = async v => { const e = $('learnShapePos'); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); await frame(); };
const tick = k => $('learnShapeTicks').children[k].click();
const setRange = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
const ptr = (el, type, x, y, o) => { const r = el.getBoundingClientRect(); el.dispatchEvent(new PointerEvent(type, Object.assign({ bubbles: true, cancelable: true, pointerId: 7, pointerType: 'mouse', button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: r.left + x, clientY: r.top + y }, o || {}))); };
const wheel = (el, x, y, dy) => { const r = el.getBoundingClientRect(); el.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y, deltaY: dy, deltaMode: 0 })); };
const approach = async id => { if (AP().id !== id) { $('ap-' + id).click(); await sleep(250); } if (AP().id !== id) fail('could not choose ' + id); return AP().name; };
const dialsBack = id => { const a = LAB.APPROACHES.find(x => x.id === id); for (const s of a.params || []) if (s.key !== undefined) S.param[id][s.key] = s.def; go(); };
const box = e => { const b = (typeof e === 'string' ? $(e) : e).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; };
// how much of the 3D picture is not the stage colour (0 .. 1)
const cover = () => { const c = document.querySelector('canvas.learn-shape-gl'); if (!c || c.hidden) return null; const t = document.createElement('canvas'); t.width = 216; t.height = 128; const g = t.getContext('2d'); g.drawImage(c, 0, 0, 216, 128); const d = g.getImageData(0, 0, 216, 128).data, b = [d[0], d[1], d[2]]; let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - b[0]) + Math.abs(d[i + 1] - b[1]) + Math.abs(d[i + 2] - b[2]) > 12) n++; return +(n / (216 * 128)).toFixed(4); };
// the finished picture: ask for the state (which draws a waiting fine picture) and give the card a moment
const rest = async (ms) => { await sleep(ms === undefined ? 450 : ms); const s = L.shape.state(); await sleep(250); return s; };
const lv = s => (s.three && s.three.levels ? s.three.levels.map(l => l.k + ':a' + (+l.alpha).toFixed(2) + (l.tint ? ':t' + (+l.tint).toFixed(2) : '')).join(' ') : null);
