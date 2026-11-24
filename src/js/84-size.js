// The picture's size by hand. A grip along the lower edge of the stage sets its height and one along its right
// edge its width; the upper and the left edge stay where they are. A double click on a grip gives that side back
// to the page. This file keeps the two numbers and decides what they may be; 84-size.css does the layout from the
// classes and the two variables set here, on wide windows only.
// Nothing here touches the camera. It reads the stage's shape whenever it draws (50-camera.js), so the picture is
// drawn afresh for the new shape and is never stretched.
const SIZE_KEY = 'squaringLab.size.v1';
const SIZE_MIN_W = CAM_ROW + 20;   // the narrowest picture (px): the zoom slider stays in it (50-camera.js)
const SIZE_MIN_H = 160;    // the lowest picture (px)
const SIZE_DIALS = 360;    // the width the controls column has when the page decides (.bench in 00-base.css), and its least
const SIZE_SIDE = 320;     // the custom approach: its steps stand beside the picture when this much (px) is free there,
const SIZE_GAP = 16;       // this far from it (84-size.css)
const SIZE_DOCK = 140;     // the height the steps keep while they stand under the picture (.cu-dock in 82-custom.css)
const SIZE_BAR = 240;      // the height kept for the bar while the steps stand beside the picture (84-size.css)
const SIZE_SLACK = 24;     // px left over at the tallest, so a line more under the picture does not move it
const SIZE = {
  w: 0, h: 0,              // what was set, in px; 0: the page decides
  how: '', wNow: 0, hNow: 0,   // what the page was last given: the width's layout ('col', 'in', 'side' or '') and the two sizes
  main: null, bench: null, mq: null, raf: 0,
};

function sizeSave() {
  try { localStorage.setItem(SIZE_KEY, JSON.stringify({ w: SIZE.w, h: SIZE.h })); } catch (err) { /* storage blocked: the size lasts for this visit */ }
}
// The width the picture's column has when the page decides it, and whether the custom approach's layout is on show.
function sizeRoom() {
  const body = document.body.classList;
  return {
    col: SIZE.bench.clientWidth - (parseFloat(getComputedStyle(SIZE.bench).columnGap) || 0) - SIZE_DIALS,
    custom: body.contains('is-custom') && !body.contains('is-learn'),
  };
}
// The tallest picture that leaves the rest of its block on one screen: whatever stands under it, as it is now.
// What scrolls by itself counts for the height it keeps: the custom approach's steps under the picture, and its
// bar while the steps stand beside the picture.
function sizeMostH() {
  const gap = parseFloat(getComputedStyle(SIZE.main).rowGap) || 0, side = SIZE.how === 'side';
  let rest = 0;
  for (const el of SIZE.main.children) {
    if (el === stage || !el.offsetHeight || getComputedStyle(el).position === 'absolute') continue;
    if (el.id === 'cuDock') { if (!side) rest += SIZE_DOCK + gap; continue; }
    rest += (side && el.id === 'cuBar' ? Math.min(SIZE_BAR, el.scrollHeight) : el.offsetHeight) + gap;
  }
  return Math.max(SIZE_MIN_H, innerHeight - 24 - SIZE_SLACK - rest);
}
function sizeApply() {
  const root = document.documentElement, on = SIZE.mq.matches;
  let w = 0, how = '';
  if (on && SIZE.w) {
    const room = sizeRoom(), want = Math.max(SIZE_MIN_W, Math.round(SIZE.w));
    if (want < room.col) { w = want; how = !room.custom ? 'col' : room.col - w - SIZE_GAP >= SIZE_SIDE ? 'side' : 'in'; }
  }
  if (how !== SIZE.how || w !== SIZE.wNow) {
    SIZE.how = how; SIZE.wNow = w;
    for (const k of ['col', 'in', 'side']) root.classList.toggle('size-' + k, how === k);
    if (w) root.style.setProperty('--size-w', w + 'px'); else root.style.removeProperty('--size-w');
  }
  // the height is measured against the block as the width has just left it
  const h = on && SIZE.h ? clamp(Math.round(SIZE.h), SIZE_MIN_H, sizeMostH()) : 0;
  if (h !== SIZE.hNow) {
    SIZE.hNow = h;
    root.classList.toggle('size-h', h > 0);
    if (h) root.style.setProperty('--size-h', h + 'px'); else root.style.removeProperty('--size-h');
  }
}
function sizeSoon() {
  if (SIZE.raf) return;
  SIZE.raf = requestAnimationFrame(() => { SIZE.raf = 0; sizeApply(); });
}
// One grip. side 's': the lower edge, which sets the height; 'e': the right edge, which sets the width.
function sizeGrip(side) {
  const el = document.createElement('div'), tall = side === 's', word = tall ? 'height' : 'width';
  el.className = 'size-grip size-' + side;
  el.tabIndex = 0;
  el.setAttribute('role', 'separator'); el.setAttribute('aria-orientation', tall ? 'horizontal' : 'vertical');
  el.setAttribute('aria-label', `The picture's ${word}`);
  el.setAttribute('aria-valuemin', String(tall ? SIZE_MIN_H : SIZE_MIN_W));
  el.title = `Drag to set the picture's ${word}. Double-click to let the page set it again.`;
  el.addEventListener('focus', () => el.setAttribute('aria-valuenow', String(tall ? stage.offsetHeight : stage.offsetWidth)));
  // The edge goes to v px from the stage's opposite edge. The lower edge stays inside the window, where it can be
  // taken hold of again; a width that fills the column is the page's own again.
  const to = v => {
    if (tall) SIZE.h = clamp(v, SIZE_MIN_H, Math.min(sizeMostH(), innerHeight - 8 - stage.getBoundingClientRect().top));
    else SIZE.w = v >= sizeRoom().col ? 0 : Math.max(SIZE_MIN_W, v);
    sizeSoon();
  };
  el.addEventListener('pointerdown', e => {
    if (e.button) return;
    e.preventDefault();
    const r = stage.getBoundingClientRect(), off = tall ? r.bottom - e.clientY : r.right - e.clientX;   // the edge keeps its place under the pointer
    const move = ev => { const q = stage.getBoundingClientRect(); to(tall ? ev.clientY + off - q.top : ev.clientX + off - q.left); };
    const end = () => {
      el.classList.remove('is-drag');
      el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', end); el.removeEventListener('pointercancel', end);
      sizeSave();
    };
    el.setPointerCapture(e.pointerId); el.classList.add('is-drag');
    el.addEventListener('pointermove', move); el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
  });
  el.addEventListener('dblclick', () => { if (tall) SIZE.h = 0; else SIZE.w = 0; sizeApply(); sizeSave(); });
  el.addEventListener('keydown', e => {
    const d = (tall ? { ArrowUp: -1, ArrowDown: 1 } : { ArrowLeft: -1, ArrowRight: 1 })[e.key];
    if (!d || e.ctrlKey || e.metaKey || e.altKey) return;
    e.preventDefault();
    to((tall ? stage.offsetHeight : stage.offsetWidth) + d * (e.shiftKey ? 64 : 16));
    sizeSave();
  });
  return el;
}
function sizeInit() {
  SIZE.main = document.querySelector('.bench-main'); SIZE.bench = document.querySelector('.bench');
  SIZE.mq = matchMedia('(min-width: 921px)');
  try {
    const o = JSON.parse(localStorage.getItem(SIZE_KEY) || 'null');
    if (o) { SIZE.w = Math.max(0, +o.w || 0); SIZE.h = Math.max(0, +o.h || 0); }
  } catch (err) { /* storage blocked or unreadable: the page decides the size */ }
  stage.append(sizeGrip('s'), sizeGrip('e'));
  // The limits are taken again when the window changes or another approach or tab comes on show, and not when
  // a line under the picture grows or shrinks: the picture keeps one size through a play.
  SIZE.mq.addEventListener('change', sizeApply);
  window.addEventListener('resize', sizeSoon);
  new MutationObserver(sizeSoon).observe(document.body, { attributes: true, attributeFilter: ['class'] });
  sizeApply();
}
