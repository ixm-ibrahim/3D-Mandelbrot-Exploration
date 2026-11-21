"""Writes out/r13/view/checks.json: the view engineer's behaviour checks for the Learn tab (run with tools/shot.py --actions)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = ("const Q = window.squaringLab, L = Q.learn, S = Q.S, $ = id => document.getElementById(id);\n"
       "const sleep = ms => new Promise(r => setTimeout(r, ms));\n"
       "const ok = (c, m) => { if (!c) throw new Error('CHECK FAILED: ' + m); };\n"
       "const shown = id => getComputedStyle($(id)).display !== 'none' && !!$(id).getClientRects().length;\n"
       "const press = (el, type, x, y, o) => el.dispatchEvent(new PointerEvent(type, Object.assign({ clientX: x, clientY: y, pointerId: 7, pointerType: 'mouse', button: 0, buttons: type === 'pointerup' ? 0 : 1, bubbles: true, cancelable: true }, o || {})));\n")
steps = []
def js(code, **kw):
    d = {"js": PRE + code}; d.update(kw); steps.append(d)

steps.append({"wait": "done", "timeout": 300})
js("ok(!S.learn && !document.body.classList.contains('is-learn'), 'starts off'); ok($('learnPanel').hidden && $('learnBar').hidden && $('learnCanvas').hidden, 'own parts hidden');"
   "ok(document.querySelectorAll('fieldset.mode input[name=mode]').length === 4, 'four choices'); ok($('mode-m').checked, 'mandelbrot ticked');"
   "Q.cam.yaw += 0.4; Q.touch(); return $('status').textContent;", wait="done", timeout=300, shot="out/r13/view/chk-before.png", clip="#stage")
js("window.__st = $('status').textContent; $('mode-l').click(); await sleep(200);"
   "ok(S.learn === true && S.mode === 'm' && L.on, 'learn on, mode kept'); ok(document.body.classList.contains('is-learn'), 'class on');"
   "ok(!shown('view') && !shown('status') && !shown('mandelPanel') && !shown('secColour') && !shown('secQuality') && !shown('secExport') && !shown('secMesh') && !shown('secCut') && !shown('secView') && !shown('flatHost'), 'put away');"
   "ok(document.querySelector('.cam-zoom') && getComputedStyle(document.querySelector('.cam-zoom')).display === 'none' && getComputedStyle($('triad')).display === 'none', 'camera overlays put away');"
   "ok(shown('learnPanel') && shown('learnBar') && shown('learnCanvas') && shown('secApproach') && shown('secEq') && shown('secMod') && shown('pow'), 'on show');"
   "ok(!$('mandelPanel').hidden && !$('secCut').hidden, 'hidden state of others untouched');"
   "ok($('mode-l').checked, 'learn ticked'); const st = L.state(); ok(st.on && st.space === 2 && st.moves.length === 3 && st.sentence.length > 20, 'state');"
   "ok($('learnSay').textContent === st.sentence && $('learnSay').getAttribute('aria-live') === 'polite', 'sentence on the page');"
   "ok($('learnPanel') === $('sections').firstElementChild && $('learnBar').parentElement.classList.contains('bench-main') && $('learnBar').previousElementSibling.id !== undefined, 'placed');"
   "const cv = $('learnCanvas'); ok(cv.width === Math.round($('stage').clientWidth * Math.min(3, devicePixelRatio)) , 'canvas sized');"
   "return JSON.stringify({ moves: st.moves, fit: st.fit });")
js("Q.refresh(false); ok($('mode-l').checked && !$('mode-m').checked, 'refresh keeps Learn ticked');"
   "const a = L.state().sentence; $('ap-lathe').click(); ok($('mode-l').checked, 'still ticked after approach'); L.set({ space: 3 }); const b = L.state();"
   "ok(b.space === 3 && b.moves.join() !== '' && b.z.length === 3, '3d state'); ok(!shown('learn-hid'), 'no hidden box in 3D'); ok(shown('learn-zz') && shown('learn-cz'), 'z dials in 3D');"
   "const m1 = b.moves.join(); $('ap-bulb').click(); const c = L.state(); ok(c.moves.join() !== m1 || c.sentence !== b.sentence, 'approach changes the moves or words');"
   "S.n = 3; Q.refresh(false); await sleep(100); const d = L.state(); ok(d.sentence !== c.sentence, 'power changes the words: ' + d.sentence); S.n = 2; Q.refresh(false);"
   "S.param.bulb.lat = 30; Q.touch(); await sleep(150); const e = L.state(); ok(e.moves.join() !== c.moves.join() || e.sentence !== c.sentence || JSON.stringify(e.end) !== JSON.stringify(c.end), 'a dial of the approach reaches Learn through touch()'); S.param.bulb.lat = 0; Q.syncControls(); Q.touch();"
   "S.flip = [0, 1]; Q.touch(); await sleep(150); const f = L.state(); ok(f.moves.length === c.moves.length + 1, 'a modifier adds a move: ' + f.moves.join()); S.flip = [0, 0]; Q.syncControls(); Q.touch(); await sleep(100);"
   "return JSON.stringify({ lathe3: m1, bulb: c.moves, flip: f.moves });")
js("L.set({ space: 2, z: [0.9, 0.7, 0], c: [-0.4, 0.3, 0], hidden: false }); $('ap-mercator').click(); L.goto(0, 0);"
   "const s0 = L.state(); ok(s0.move === 0 && s0.t === 0 && !s0.playing, 'at the start'); $('learnPlay').click(); ok(L.state().playing && $('learnPlay').textContent === 'Pause', 'playing');"
   "await sleep(900); const s1 = L.state(); ok(s1.playing && (s1.move > 0 || s1.t > 0.1), 'moved on while playing: ' + s1.move + ' ' + s1.t); const p1 = s1.point;"
   "ok(Math.abs(Math.hypot(p1[0], p1[1]) - Math.hypot(0.9, 0.7)) < 1e-6, 'a turn keeps the length');"
   "$('learnPlay').click(); const s2 = L.state(); ok(!s2.playing, 'paused'); await sleep(300); ok(L.state().t === s2.t, 'stays paused');"
   "$('learnPos').value = 1.5; $('learnPos').dispatchEvent(new Event('input', { bubbles: true })); const s3 = L.state(); ok(s3.move === 1 && Math.abs(s3.t - 0.5) < 1e-9, 'slider goes to move 2, half way');"
   "ok($('learnWhere').textContent.includes('move 2 of 3') && $('learnTicks').children[1].classList.contains('is-on') && $('learnMoves').children[1].classList.contains('is-on'), 'marks follow');"
   "$('learnBack').click(); ok(L.state().move === 1 && L.state().t === 0, 'back to the start of the move'); $('learnBack').click(); ok(L.state().move === 0 && L.state().t === 0, 'back one move');"
   "$('learnMoves').children[2].click(); await sleep(60); ok(L.state().playing && L.state().move === 2, 'a move button plays that move');"
   "L.goto(2, 1); const s4 = L.state(); ok(s4.done && s4.sentence.includes('is done'), 'done text: ' + s4.sentence); ok(Math.abs(s4.point[0] - (0.9 * 0.9 - 0.7 * 0.7 - 0.4)) < 1e-9 && Math.abs(s4.point[1] - (2 * 0.9 * 0.7 + 0.3)) < 1e-9, 'the step ends at z squared plus c');"
   "ok(L.next() === true, 'next step'); const s5 = L.state(); ok(s5.step === 1 && s5.orbit.length === 2 && s5.move === 0 && s5.t === 0 && Math.abs(s5.z[0] - s4.point[0]) < 1e-12, 'goes on from the new point');"
   "$('learnAgain').click(); ok(L.state().step === 0 && L.state().orbit.length === 1, 'start again');"
   "return JSON.stringify({ done: s4.sentence });")
js("L.set({ space: 2, hidden: false, z: [0.9, 0.7, 0] }); L.goto(0, 0.5); await sleep(120); const cv = $('learnCanvas'), r = cv.getBoundingClientRect(), P = L.proj, q = P.to([0.9, 0.7, 0]);"
   "press(cv, 'pointerdown', r.left + q[0] + 3, r.top + q[1] - 2); press(cv, 'pointermove', r.left + q[0] + 3 + P.s * 0.5, r.top + q[1] - 2 - P.s * 0.25); press(cv, 'pointerup', r.left + q[0] + 3 + P.s * 0.5, r.top + q[1] - 2 - P.s * 0.25);"
   "const z = L.state().z0; ok(Math.abs(z[0] - 1.4) < 0.011 && Math.abs(z[1] - 0.95) < 0.011, 'dragging the ring moves z: ' + z); ok(L.state().move === 0 && Math.abs(L.state().t - 0.5) < 1e-9, 'the place in the move is kept');"
   "ok(Math.abs(+$('learn-zxNum').value - z[0]) < 1e-9, 'the dial follows');"
   "await sleep(80); const P2 = L.proj, qc = P2.to(L.state().c); press(cv, 'pointerdown', r.left + qc[0], r.top + qc[1]); press(cv, 'pointermove', r.left + qc[0] + P2.s * 0.2, r.top + qc[1]); press(cv, 'pointerup', r.left + qc[0] + P2.s * 0.2, r.top + qc[1]);"
   "ok(Math.abs(L.state().c[0] - (-0.2)) < 0.011, 'dragging the diamond moves c: ' + L.state().c);"
   "L.set({ hidden: true }); await sleep(80); const y0 = L.view.h2.yaw; press(cv, 'pointerdown', r.left + 200, r.top + 200); press(cv, 'pointermove', r.left + 260, r.top + 220); press(cv, 'pointerup', r.left + 260, r.top + 220);"
   "ok(Math.abs(L.view.h2.yaw - (y0 - 0.6)) < 1e-9 && JSON.stringify(L.state().z0) === JSON.stringify(z), 'in a tipped view a drag turns the view and moves no point'); ok(shown('learnViewReset'), 'reset view offered'); $('learnViewReset').click(); ok(L.view.h2.yaw === y0 && !shown('learnViewReset'), 'view reset');"
   "cv.dispatchEvent(new WheelEvent('wheel', { deltaY: -300, bubbles: true, cancelable: true })); ok(L.view.h2.zoom > 1.3, 'wheel zooms'); $('learnViewReset').click();"
   "L.set({ space: 1, z: [-1.5, 0, 0], c: [0.2, 0, 0] }); ok(L.state().hidden === true && $('learn-hid').checked, '1D opens with the hidden direction shown'); L.goto(0, 0.5); const h = L.state().point;"
   "ok(Math.abs(Math.hypot(h[1], h[2]) - 1.5) < 1e-6 && Math.abs(h[0]) < 1e-6, 'half way through its turn a negative number is off the line: ' + h); ok(!shown('learn-zy') && !shown('learn-cy') && shown('learn-zx'), 'one dial per point on a line');"
   "L.goto(2, 1); ok(Math.abs(L.state().point[0] - (2.25 + 0.2)) < 1e-9, '1D step ends at x squared plus c');"
   "L.set({ space: 2, z: [3, 3, 0] }); const a = L.state(); ok(a.away && $('learnNext').disabled === true, 'run away: next is off'); L.goto(2, 1); ok(L.state().sentence.includes('run away'), 'says it ran away'); ok(L.next() === false, 'no next step after running away');"
   "$('learnZero').click(); ok(L.state().z0.join() === '0,0,0', 'start at 0'); S.c = [-0.75, 0.1, 0.3]; $('learnJuliaC').click(); ok(L.state().c.join() === '-0.75,0.1,0', 'c of the Julia tab, as far as a page holds it: ' + L.state().c);"
   "L.set({ show: 'all' }); ok($('learn-show').selectedOptions[0].textContent.includes('All directions'), 'show select follows'); L.set({ show: 'circle' });"
   "return 'hands ok';")
js("$('mode-m').click(); await sleep(50); ok(!S.learn && !L.on && S.mode === 'm' && $('mode-m').checked && !document.body.classList.contains('is-learn'), 'left Learn'); ok(shown('view') && shown('mandelPanel') && !shown('learnPanel') && !shown('learnBar') && !shown('learnCanvas'), 'page back'); return 1;",
   wait="done", timeout=300, shot="out/r13/view/chk-after.png", clip="#stage")
js("ok($('status').textContent === window.__st, 'status line as before: ' + $('status').textContent + ' / ' + window.__st);"
   "$('mode-k').click(); await sleep(100); ok(S.mode === 'k' && !shown('secApproach'), 'kleinian hides Approach'); $('mode-l').click(); await sleep(100);"
   "ok(S.learn && S.mode === 'k' && shown('secApproach') && shown('secEq') && shown('secMod') && $('secApproach').hidden === true && !shown('kleinPanel'), 'Learn from Kleinian shows Approach by style only');"
   "$('mode-j').click(); await sleep(100); ok(!S.learn && S.mode === 'j' && shown('juliaPanel') && shown('secApproach'), 'on to Julia');"
   "$('eq').value = 'z^n + c*c'; $('eq').dispatchEvent(new Event('change', { bubbles: true })); $('mode-l').click(); await sleep(60); ok(shown('learnEqNote'), 'equation note'); "
   "L.set({ space: 3 }); L.goto(1, 0.5); $('resetAll').click(); await sleep(100);"
   "ok(!S.learn && !L.on && S.mode === 'm' && $('mode-m').checked && L.space === 2 && L.pos === 0 && L.show === 'circle' && !document.body.classList.contains('is-learn') && S.eq === 'z^n + c', 'Reset everything: Learn off and back to its start');"
   "$('mode-l').click(); await sleep(60); const st = L.state(); ok(st.space === 2 && st.z0.join() === '0.7,0.4,0' && !shown('learnEqNote'), 'opens as new'); $('mode-m').click(); return 'modes ok';", wait="done", timeout=300)
with open(os.path.join(HERE, "checks.json"), "w", encoding="utf-8") as f:
    json.dump(steps, f, ensure_ascii=False, indent=1)
print("wrote checks.json,", len(steps), "steps")
