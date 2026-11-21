// ---------- the picture stays in view on a narrow window (a phone held upright). Styles: 85-pin.css.
// At 920 px and narrower the page is one column. When the window is also tall enough, .bench-main (the picture and
// whatever stands under it) is held at the top of the window while the controls scroll under it. This file only
// decides and measures: it sets classes on <html> and one CSS variable, and the style sheet does the rest.
//   pin-can     narrow and tall enough: the button "Unpin picture" / "Pin picture" shows
//   pin-on      pinned (pin-can, and the user has not unpinned)
//   pin-let-go  pinned, but not held for now: an on-screen keyboard is up, or the block is too tall for the window
//   --pin-h     the lower edge of the held block, in px from the top of the window (0 px while nothing is held)
// The picture's height never depends on the scroll position: see the note on svh in 85-pin.css.
const PIN_KEY = 'squaringLab.pin.v1';
const PIN_MIN_H = 520;     // the lowest window (px, with the browser's bars showing) in which the picture is pinned
const PIN_ROOM = 120;      // px that must stay visible under the block for a number box with focus, or the pin lets go
const PIN_MOST = 0.72;     // a block taller than this share of the window is not held (it would leave no room to scroll)
const PIN = {
  want: true,              // the user's choice; pinned is the starting state
  can: false, on: false, free: false, stuck: false,
  top: 0, h: 0, small: 0,  // where the block is held (px from the top), --pin-h, the window's height with the bars showing
  main: null, bench: null, btn: null, hint: null, probe: null, mq: null, raf: 0,
  state: () => ({ want: PIN.want, can: PIN.can, on: PIN.on, free: PIN.free, stuck: PIN.stuck, top: PIN.top, h: PIN.h, small: PIN.small }),
  set: v => { PIN.want = !!v; pinSave(); pinUpdate(); },
};

function pinSave() {
  try { localStorage.setItem(PIN_KEY, PIN.want ? '1' : '0'); } catch (err) { /* storage blocked: the choice lasts for this visit */ }
}
// A box the on-screen keyboard opens for: text and number boxes, not sliders, tick boxes, buttons or lists.
function pinEditing() {
  const el = document.activeElement;
  if (!el || el === document.body) return false;
  if (el.isContentEditable || el.tagName === 'TEXTAREA') return true;
  return el.tagName === 'INPUT' && !/^(range|checkbox|radio|button|submit|reset|file|color|image|hidden)$/.test(el.type);
}
// The window's height with the browser's bars showing. It stays the same while the page scrolls.
function pinSmall() {
  const h = PIN.probe ? PIN.probe.offsetHeight : 0;
  return h > 0 ? h : document.documentElement.clientHeight;
}
function pinUpdate() {
  const P = PIN, root = document.documentElement;
  if (!P.main) return;
  P.small = pinSmall();
  const editing = pinEditing();
  // With a box in use the window may have shrunk because the keyboard came up (on some phones the keyboard makes
  // the window itself lower). That must not switch the layout, which would change the picture's size: the pin
  // lets go instead (below) and the layout stays.
  const can = P.mq.matches && (P.small >= PIN_MIN_H || (editing && P.can));
  const on = can && P.want;
  if (can !== P.can) { P.can = can; root.classList.toggle('pin-can', can); }
  if (on !== P.on) { P.on = on; root.classList.toggle('pin-on', on); }
  const label = P.want ? 'Unpin picture' : 'Pin picture';
  if (P.btn.textContent !== label) {
    P.btn.textContent = label;
    P.btn.title = P.want ? 'Let the picture scroll away with the page' : 'Keep the picture in view while the controls scroll';
  }
  // the button stands beside the status line; without one it takes a line of its own
  const status = $('status');
  P.btn.classList.toggle('is-solo', can && !(status && status.offsetHeight > 0));
  let free = false, h = 0;
  if (on) {
    P.top = parseFloat(getComputedStyle(P.main).top) || 0;
    const bottom = P.top + P.main.offsetHeight;
    const vv = window.visualViewport, seen = vv ? vv.height : window.innerHeight;
    free = (editing && seen < bottom + PIN_ROOM) || bottom > P.small * PIN_MOST;
    if (!free) h = Math.ceil(bottom);
  }
  if (free !== P.free) { P.free = free; root.classList.toggle('pin-let-go', free); }
  if (h !== P.h) { P.h = h; root.style.setProperty('--pin-h', h + 'px'); }
  pinStuck();
}
// Whether the block is held at the top right now. It only switches the hairline under the block: paint, no layout.
function pinStuck() {
  const P = PIN, stuck = P.on && !P.free && P.bench.getBoundingClientRect().top < P.top - 0.5;
  if (stuck !== P.stuck) { P.stuck = stuck; P.main.classList.toggle('is-stuck', stuck); }
}
function pinSoon() {
  if (PIN.raf) return;
  PIN.raf = requestAnimationFrame(() => { PIN.raf = 0; pinUpdate(); });
}
function pinInit() {
  const P = PIN;
  P.main = document.querySelector('.bench-main'); P.bench = document.querySelector('.bench');
  const dials = document.querySelector('.dials');
  if (!P.main || !P.bench || !dials) return;
  try { if (localStorage.getItem(PIN_KEY) === '0') P.want = false; } catch (err) { /* storage blocked: start pinned */ }
  P.mq = matchMedia('(max-width: 920px)');

  P.probe = document.createElement('div');
  P.probe.className = 'pin-probe'; P.probe.setAttribute('aria-hidden', 'true');
  document.body.append(P.probe);

  P.btn = document.createElement('button');
  P.btn.type = 'button'; P.btn.className = 'btn pin-btn'; P.btn.id = 'pinToggle';
  P.btn.addEventListener('click', () => P.set(!P.want));
  P.main.append(P.btn);

  // On a phone the hint stands under the picture. While pinned it would cost the pinned block a line, so a copy
  // of it heads the controls instead (shown by the style sheet), and follows the words of the original.
  const below = $('hintBelow');
  if (below) {
    P.hint = document.createElement('p');
    P.hint.className = 'hint-below pin-hint'; P.hint.id = 'pinHint'; P.hint.setAttribute('aria-hidden', 'true');
    const copy = () => { if (P.hint.textContent !== below.textContent) P.hint.textContent = below.textContent; };
    copy();
    if (typeof MutationObserver === 'function') new MutationObserver(copy).observe(below, { childList: true, characterData: true, subtree: true });
    dials.prepend(P.hint);
  }

  const onMq = () => pinUpdate();
  if (P.mq.addEventListener) P.mq.addEventListener('change', onMq); else P.mq.addListener(onMq);
  window.addEventListener('resize', pinSoon);
  window.addEventListener('scroll', pinStuck, { passive: true });
  if (window.visualViewport) window.visualViewport.addEventListener('resize', pinSoon);
  // focus moving from one box to the next is a focusout and a focusin: decide once, after both
  document.addEventListener('focusin', pinSoon); document.addEventListener('focusout', pinSoon);
  if (typeof ResizeObserver === 'function') {
    const ro = new ResizeObserver(pinUpdate);
    ro.observe(P.main);    // the block is measured, whatever it holds
    ro.observe(P.probe);   // the window was turned or resized
  }
  if (window.squaringLab) window.squaringLab.pin = P;
  pinUpdate();
}
