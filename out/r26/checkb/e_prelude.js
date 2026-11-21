// helpers every step of out/r26/checkb/*.js starts with (see eyes.py)
const LAB = window.squaringLab, L = LAB.learn, S = LAB.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const frame = () => new Promise(r => requestAnimationFrame(() => r()));
const r1 = x => +(+x).toFixed(1), r3 = x => +(+x).toFixed(3);
const med = a => { const b = a.slice().sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : 0; };
const pct = (a, p) => { const b = a.slice().sort((x, y) => x - y); return b.length ? b[Math.min(b.length - 1, Math.floor(b.length * p))] : 0; };
// what stands on the page right now, read from the page itself (not from the test handle)
const said = () => ({ where: $('learnShapeWhere').textContent, say: $('learnShapeSay').textContent, play: $('learnShapePlay').textContent, slider: +$('learnShapePos').value });
// the reader's way in: the Learn tab, then "A whole shape" by its own radio (which plays by itself the first time)
const openLearn = async () => { if (!document.body.classList.contains('is-learn')) { $('mode-l').click(); await sleep(300); } };
const pickShape = async () => { $('learnFollowShape').click(); await frame(); };
// the reader's hand on a choice of the transport: kind 'm' | 'j' | 'both', space 2 | 3
const kindBar = v => { const r = document.querySelector('input[name=learnShapeKindBar][value=' + v + ']'); r.click(); };
const spaceBar = v => { const r = document.querySelector('input[name=learnShapeSpaceBar][value="' + v + '"]'); r.click(); };
// a scripted pointer on an element, at a place inside it
const ptr = (el, type, x, y, o) => { const r = el.getBoundingClientRect(); el.dispatchEvent(new PointerEvent(type, Object.assign({ bubbles: true, cancelable: true, pointerId: 7, pointerType: 'mouse', button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: r.left + x, clientY: r.top + y }, o || {}))); };
const wheel = (el, x, y, dy) => { const r = el.getBoundingClientRect(); el.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y, deltaY: dy, deltaMode: 0 })); };
// choose an approach of the lab by its id (the rule the 3D picture takes its steps with)
const approach = async id => { $('ap-' + id).click(); await sleep(250); const a = LAB.APPROACHES[S.approach]; if (a.id !== id) fail('could not choose ' + id); return a.name; };
const brief = s => ({ kind: s.kind, space: s.space, c: s.c, pos: r3(s.pos), playing: s.playing, sentence: s.sentence, note: s.note, quality: s.quality });
const box = e => { const b = (typeof e === 'string' ? $(e) : e).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; };
