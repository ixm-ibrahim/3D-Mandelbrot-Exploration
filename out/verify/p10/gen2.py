import json
H = "const L = window.squaringLab, $ = id => document.getElementById(id); const type = (id, v) => { const e = $(id); e.value = String(v); e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; const sleep = ms => new Promise(r => setTimeout(r, ms)); const hid = id => { const d = $(id).closest('.dial'); return d.hidden || d.offsetParent === null; }; const P = () => JSON.stringify(L.S.param.mercator); const notes = () => [...document.querySelectorAll('#secApproach .note, #secApproach .dial-help, #secApproach p')].filter(e => e.offsetParent !== null).map(e => e.textContent.trim()).join(' ## '); "
D = "out/verify/p10/"
X = "L.cam.yaw = 0; L.cam.pitch = 0; L.cam.target = [0,0,0]; L.cam.dist = 5.2; L.touch(); "
TOP = "L.cam.yaw = -Math.PI/2; L.cam.pitch = 1.5; L.cam.target = [-0.4,0,0]; L.cam.dist = 5.6; L.touch(); "
DEF = "L.cam.yaw = -1.0; L.cam.pitch = 0.55; L.cam.dist = 5.2; L.cam.target = [-0.6,0,0]; L.touch(); "
A = []
def step(js, shot=None, clip="#view", wait="done"):
    a = {"js": H + js, "timeout": 400}
    if wait: a["wait"] = wait
    if shot:
        a["shot"] = D + shot
        a["clip"] = clip
    A.append(a)
# A: default behaviour of the planes dial when the power changes
step("L.R.warmOn = false; document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); $('qFast').click(); L.S.q.aa = 2; L.syncControls(); const ctl = [...document.querySelectorAll('#secApproach input, #secApproach select, #secApproach button')].map(e => e.id || e.textContent.trim()).join(' | '); return 'start ' + P() + ' n=' + L.S.n + ' ; controls: ' + ctl;")
step("type('powNum', 8); " + X + "return 'after typing power 8: ' + P() + ' box=' + $('par-mercator-planesNum').value;", "a_n8_untouched_x.png")
step("type('powNum', 6); " + X + "return 'after typing power 6: ' + P();", "a_n6_untouched_x.png")
step("return notes();", "a_panel_n6.png", "#secApproach", None)
step("const sels = [...document.querySelectorAll('#sections select')].map(e => e.id + ': ' + [...e.options].map(o => o.text).join(' | ')); return sels.join(' ;; ').slice(0, 1500);", None, None, None)
# C: turn
step("type('powNum', 2); type('par-mercator-planesNum', 1); type('par-mercator-turnNum', 0); " + TOP + "return 'p1 turn0 hidden=' + hid('par-mercator-turn') + ' ' + P();", "c_p1_turn0_top.png")
step("type('par-mercator-turnNum', 40); " + TOP + "return 'p1 turn40 ' + P() + ' formula: ' + $('f-mercator').textContent + ' ## card: ' + $('card').textContent.replace(/\\s+/g, ' ').slice(0, 900);", "c_p1_turn40_top.png")
step("type('par-mercator-planesNum', 2); " + TOP + "return 'p2 with stored turn 40: hidden=' + hid('par-mercator-turn') + ' ' + P() + ' formula: ' + $('f-mercator').textContent + ' ## visible notes: ' + notes();", "c_p2_turn40hidden_top.png")
step("type('par-mercator-planesNum', 1); type('par-mercator-turnNum', 0); type('par-mercator-planesNum', 2); " + TOP + "return 'p2 turn0 ' + P();", "c_p2_turn0_top.png")
# play, then hide the dial
step("type('par-mercator-planesNum', 1); const b = $('par-mercator-turnPlay'); b.click(); await sleep(700); const t1 = L.S.param.mercator.turn; const lab1 = b.getAttribute('aria-pressed') + '/' + b.textContent + '/' + b.title; type('par-mercator-planesNum', 2); await sleep(400); const t2 = L.S.param.mercator.turn; await sleep(700); const t3 = L.S.param.mercator.turn; const lab2 = b.getAttribute('aria-pressed') + '/' + b.textContent; type('par-mercator-planesNum', 1); await sleep(500); const t4 = L.S.param.mercator.turn; await sleep(500); const t5 = L.S.param.mercator.turn; const lab3 = b.getAttribute('aria-pressed') + '/' + b.textContent; if (b.getAttribute('aria-pressed') === 'true') b.click(); type('par-mercator-turnNum', 0); return 'turn play: after 0.7s ' + t1 + ' [' + lab1 + ']; hidden (p=2) ' + t2 + ' -> ' + t3 + ' [' + lab2 + ']; shown again ' + t4 + ' -> ' + t5 + ' [' + lab3 + ']';")
step("const b = $('par-mercator-liftPlay'); b.click(); await sleep(600); const t1 = L.S.param.mercator.lift; $('ap-lathe').click(); await sleep(400); const t2 = L.S.param.mercator.lift; await sleep(600); const t3 = L.S.param.mercator.lift; $('ap-mercator').click(); await sleep(500); const t4 = L.S.param.mercator.lift; await sleep(500); const t5 = L.S.param.mercator.lift; const st = b.getAttribute('aria-pressed'); if (st === 'true') b.click(); type('par-mercator-liftNum', 0); return 'lift play: ' + t1 + '; other approach ' + t2 + ' -> ' + t3 + '; back ' + t4 + ' -> ' + t5 + ' pressed=' + st + ' ' + P();")
# lift pictures
step("type('par-mercator-planesNum', 2); type('par-mercator-liftNum', 0); " + DEF + "return 'p2 lift 0 ' + P();", "d_p2_lift0.png")
step("type('par-mercator-liftNum', 0.5); " + DEF + "return 'p2 lift 0.5 ' + P() + ' formula: ' + $('f-mercator').textContent + ' ## card: ' + $('card').textContent.replace(/\\s+/g, ' ').slice(0, 700);", "d_p2_lift05.png")
step("type('par-mercator-liftNum', -0.5); " + DEF + "return 'p2 lift -0.5 ' + P();", "d_p2_liftm05.png")
step("type('par-mercator-planesNum', 1); type('par-mercator-liftNum', 0.5); " + DEF + "return 'p1 lift 0.5 ' + P();", "d_p1_lift05.png")
step("type('par-mercator-liftNum', -0.5); " + DEF + "return 'p1 lift -0.5 ' + P();", "d_p1_liftm05.png")
# 2D slice with a turn (sign check) and with a lift
step("type('par-mercator-liftNum', 0); type('par-mercator-turnNum', 40); $('flat').click(); return '2D p1 turn 40 ' + P() + ' cut=' + L.S.cut + ' v2=' + JSON.stringify(L.S.v2);", "e_flat_p1_turn40.png")
step("type('par-mercator-turnNum', 0); type('par-mercator-liftNum', 0.5); return '2D p1 lift 0.5 ' + P();", "e_flat_p1_lift05.png")
step("type('par-mercator-liftNum', 0); $('flat').click(); document.querySelector('#approachReset .dial-reset').click(); return 'after approach reset ' + P() + ' flat=' + L.S.flat;")
# B: a Julia preset changes the planes dial
step("$('mode-j').click(); const b = [...document.querySelectorAll('#juliaList .plist-item')].find(x => x.textContent === 'Douady rabbit'); b.click(); const p1 = P(); $('mode-m').click(); await sleep(300); const p2 = P(); const box = $('par-mercator-planesNum').value; const jr = document.querySelector('#juliaReset .dial-reset'); $('mode-j').click(); jr.click(); const p3 = P(); $('mode-m').click(); L.resetCam(); L.touch(); return 'julia rabbit -> ' + p1 + '; back in Mandelbrot mode ' + p2 + ' box ' + box + '; after Julia reset ' + p3 + ' iter=' + L.S.iter;", "b_mandel_after_rabbit.png")
json.dump(A, open(D + 'tests.json', 'w'), indent=1)
