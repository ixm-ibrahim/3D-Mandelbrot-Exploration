"""Write the action files for the pin checks: out/r13/pin/run-<size>-<theme>.json, one per window size.
   python out/r13/pin/make.py   (from the project root)"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PRE = r"""
const L = window.squaringLab, $ = id => document.getElementById(id), P = L.pin;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const main = document.querySelector('.bench-main'), stage = $('stage');
const rect = el => { const r = el.getBoundingClientRect(); return { top: Math.round(r.top), bottom: Math.round(r.bottom), h: Math.round(r.height), w: Math.round(r.width) }; };
// what would change if the solid were drawn again: the time of the last touch(), the canvas size, the status line
const drawn = () => [L.R.lastTouch, $('view').width, $('view').height, $('status').textContent].join('|');
const geo = () => ({ win: [innerWidth, innerHeight], scrollY: Math.round(scrollY), pin: P.state(), main: rect(main), stage: rect(stage),
  share: +(rect(main).bottom / innerHeight).toFixed(3), pos: getComputedStyle(main).position, toprow: getComputedStyle($('toprow')).position,
  pinH: getComputedStyle(document.documentElement).getPropertyValue('--pin-h'), status: $('status').textContent,
  btn: $('pinToggle').textContent + ' ' + JSON.stringify(rect($('pinToggle'))), hint: $('pinHint') ? getComputedStyle($('pinHint')).display : null,
  overflowX: document.documentElement.scrollWidth - innerWidth });
// a fingerprint of the picture: where 49 rays through it meet the solid (only when the page is idle)
const print = () => { const w = stage.clientWidth, h = stage.clientHeight; let s = ''; for (let i = 1; i < 8; i++) for (let j = 1; j < 8; j++) { const p = L.pick(w * i / 8, h * j / 8); s += p ? p.map(x => x.toFixed(2)).join(',') + ';' : '-;'; } return s; };
const seen = e => e.checkVisibility() && e.getBoundingClientRect().width > 0;
const stored = () => { try { return localStorage.getItem('squaringLab.pin.v1'); } catch (e) { return 'blocked'; } };
"""


def js(body):
    return PRE + body


def run(size, theme, tag):
    d = "out/r13/pin/%s-%s" % (tag, theme)
    w, h = (int(x) for x in size.split("x"))
    acts = [
        {"wait": "done", "timeout": 240},
        {"js": js("window.__d0 = drawn(); window.__p0 = print(); return { at: 'top', ...geo() };"), "shot": d + "-1-top.png"},
        # scroll to the Approach section, in steps as a finger would
        {"js": js("""
            const sec = [...document.querySelectorAll('#sections > details.sec')].find(s => /approach/i.test(s.querySelector('summary').textContent));
            const y = Math.round(sec.getBoundingClientRect().top + scrollY - (P.state().h || 0) - 12);
            for (let i = 1; i <= 12; i++) { window.scrollTo(0, y * i / 12); await sleep(40); }
            await sleep(300);
            return { at: 'approach', sec: sec.id, secTop: rect(sec).top, same: drawn() === window.__d0, samePicture: print() === window.__p0, ...geo() };"""),
         "shot": d + "-2-approach.png"},
        # the end of the controls
        {"js": js("""
            const dials = document.querySelector('.dials');
            const y = Math.round(dials.getBoundingClientRect().bottom + scrollY - innerHeight);
            for (let i = 1; i <= 12; i++) { window.scrollTo(0, scrollY + (y - scrollY) * i / 12); await sleep(40); }
            await sleep(300);
            return { at: 'end of controls', dialsBottom: rect(dials).bottom, same: drawn() === window.__d0, samePicture: print() === window.__p0, ...geo() };"""),
         "shot": d + "-3-end.png"},
        # a dial moved while scrolled down: the power, 2 -> 3
        {"js": js("""
            const pow = $('pow'); pow.scrollIntoView({ block: 'center' }); await sleep(200);
            window.__before = print(); window.__y = Math.round(scrollY);
            const box = pow.closest('.dial') || pow.parentElement;
            const num = box.querySelector('input[type=text], input[type=number]') || pow;
            const set = (el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
            set(pow, '3');
            return { at: 'dial', pow: pow.type, n: L.S.n, powRect: rect(box) };"""),
         "wait": "done", "timeout": 240},
        {"js": js("return { at: 'dial moved', n: L.S.n, pictureChanged: print() !== window.__before, scrolled: Math.round(scrollY) - window.__y, stageInView: rect(stage).top >= 0 && rect(stage).bottom <= innerHeight, ...geo() };"),
         "shot": d + "-4-dial.png"},
        # focus on a control far down
        {"js": js("""
            window.scrollTo(0, 0); await sleep(150);
            const all = [...document.querySelectorAll('.dials input, .dials select, .dials button, .dials summary')].filter(seen);
            const far = all[all.length - 1], mid = all[Math.floor(all.length * 0.6)];
            const out = [];
            for (const el of [far, mid]) { el.focus(); await sleep(250); const r = rect(el); out.push({ id: el.id || el.tagName, top: r.top, bottom: r.bottom, clear: r.top >= (P.state().h || 0) && r.bottom <= innerHeight }); }
            // and one that lies under the pinned block when it takes focus
            const under = all.find(e => { const r = e.getBoundingClientRect(); return r.top > 0 && r.bottom < (P.state().h || 0); });
            if (under) { under.focus(); await sleep(250); const r = rect(under); out.push({ under: under.id || under.tagName, top: r.top, bottom: r.bottom, clear: r.top >= (P.state().h || 0) && r.bottom <= innerHeight }); }
            return { at: 'focus', pinH: P.state().h, out };"""),
         "shot": d + "-5-focus.png"},
        # unpin, scroll, pin again
        {"js": js("""
            $('pinToggle').scrollIntoView({ block: 'nearest' }); document.activeElement.blur(); await sleep(100);
            window.scrollTo(0, 0); await sleep(100);
            $('pinToggle').click(); await sleep(300);
            const a = { ...geo() };
            window.scrollTo(0, 900); await sleep(300);
            return { at: 'unpinned', atTop: a, stored: stored(), ...geo() };"""),
         "wait": "done", "timeout": 240, "shot": d + "-6-unpinned.png"},
        {"js": js("""
            window.scrollTo(0, 0); await sleep(150); $('pinToggle').click(); await sleep(300);
            window.scrollTo(0, 900); await sleep(300);
            return { at: 'pinned again', stored: stored(), ...geo() };"""),
         "wait": "done", "timeout": 240, "shot": d + "-7-pinned-again.png"},
    ]

    acts += [
        # a button of the closing text that ends with uiShowStage(), pressed while the picture is pinned over the controls
        {"js": js("""
            window.scrollTo(0, 1200); await sleep(200); const y0 = Math.round(scrollY);
            L.twinOff(); await sleep(1500);
            return { at: 'show stage, pinned', moved: Math.round(scrollY) - y0, stageInView: rect(stage).top >= 0 && rect(stage).bottom <= innerHeight, stage: rect(stage) };"""),
         "wait": "done", "timeout": 240},
        # and from the closing text itself, where the pinned block has scrolled away with the bench
        {"js": js("""
            const why = document.querySelector('.why'); why.scrollIntoView({ block: 'end' }); await sleep(300);
            const before = { scrollY: Math.round(scrollY), stage: rect(stage) };
            L.showFigure4(); await sleep(2500);
            return { at: 'show stage, from the closing text', before, after: { scrollY: Math.round(scrollY), stage: rect(stage) }, stageInView: rect(stage).top >= 0 && rect(stage).bottom <= innerHeight, pin: P.state() };"""),
         "wait": "done", "timeout": 240, "shot": d + "-8-figure4.png"},
        # the on-screen keyboard, stood in for by a visible window of 300 px while a number box has focus
        {"js": js("""
            L.resetAll(); window.scrollTo(0, 0); await sleep(300);
            const box = [...document.querySelectorAll('.dials input[type=text], .dials input[type=number]')].filter(seen)[0];
            if (!box) return { at: 'keyboard', skipped: 'no number box in view' };
            box.scrollIntoView({ block: 'center' }); await sleep(200);
            const d0 = [$('view').width, $('view').height, rect(stage).h].join('|'), real = window.visualViewport;
            let hgt = 300; const fake = { get height() { return hgt; }, addEventListener() {}, removeEventListener() {} };
            Object.defineProperty(window, 'visualViewport', { configurable: true, get: () => fake });
            box.focus(); box.dispatchEvent(new FocusEvent('focusin', { bubbles: true })); await sleep(300);
            const up = { active: document.activeElement === box, pin: P.state(), pos: getComputedStyle(main).position, cls: document.documentElement.className, sizeSame: [$('view').width, $('view').height, rect(stage).h].join('|') === d0, box: rect(box) };
            hgt = innerHeight; window.dispatchEvent(new Event('resize')); await sleep(300);
            const down = { pin: P.state(), pos: getComputedStyle(main).position, sizeSame: [$('view').width, $('view').height, rect(stage).h].join('|') === d0 };
            box.blur(); document.dispatchEvent(new FocusEvent('focusout', { bubbles: true })); await sleep(200); const after = P.state().free; Object.defineProperty(window, 'visualViewport', { configurable: true, get: () => real });
            return { at: 'keyboard', box: box.id || box.className, up, down, freeAfterBlur: after };"""),
         "wait": "done", "timeout": 240},
    ]
    with open(os.path.join(HERE, "run-%s-%s.json" % (tag, theme)), "w", encoding="utf-8") as f:
        json.dump(acts, f, indent=1)


for size, tag in (("375x667", "375x667"), ("390x844", "390x844"), ("768x1024", "768x1024"), ("667x375", "667x375")):
    for theme in ("light", "dark"):
        run(size, theme, tag)
print("ok")
