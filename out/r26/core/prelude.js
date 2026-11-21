// helpers every step of out/r26/core/*.js starts with (see run.py)
const LAB = window.squaringLab, L = LAB.learn, S = LAB.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const shown = id => { const e = typeof id === 'string' ? $(id) : id; return !!e && e.getBoundingClientRect().width > 0; };
const go = () => { LAB.syncControls(); LAB.refresh(false); LAB.touch(); };
const shapeOn = async o => { if (!document.body.classList.contains('is-learn')) { $('mode-l').click(); await sleep(250); } return L.shape.set(Object.assign({ on: true }, o || {})); };
// a scripted pointer on an element, at a place inside it
const ptr = (el, type, x, y, o) => { const r = el.getBoundingClientRect(); el.dispatchEvent(new PointerEvent(type, Object.assign({ bubbles: true, cancelable: true, pointerId: 7, pointerType: 'mouse', button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: r.left + x, clientY: r.top + y }, o || {}))); };
const frame = () => new Promise(r => requestAnimationFrame(() => r()));
// the brief: what a state looks like, short
const brief = s => ({ on: s.on, kind: s.kind, space: s.space, c: s.c, pos: +s.pos.toFixed(3), playing: s.playing, sentence: s.sentence, note: s.note, panes: s.panes.length, threeOk: s.threeOk, quality: s.quality, ms: Object.fromEntries(Object.entries(s.ms).map(([k, v]) => [k, +(+v).toFixed(2)])) });
