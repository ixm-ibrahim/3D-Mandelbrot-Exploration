# Second check, tester "flat": the first check's runs a, b, c and d (out/t6/flat/mk_a.py, mk_bcd.py), the same
# steps and names, written to out/t9/flat/<run>/ so that they can be compared with out/t6/flat/<run>/ (v6).
import json
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id), S = L.S;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
if (!document.getElementById('t6hide')) { const st = document.createElement('style'); st.id = 't6hide'; st.textContent = '#stage > *:not(canvas) { visibility: hidden !important; }'; document.head.appendChild(st); }
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const check = (id, on) => { const e = $(id); if (!e) fail('no control ' + id); if (e.checked !== on) e.click(); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const view = (x, y, h) => { S.v2.x = x; S.v2.y = y; S.v2.h = h; L.syncControls(); L.refresh(false); };
const notes = () => [...document.querySelectorAll('#colDials .note, #colDials p')].filter(e => e.getBoundingClientRect().width > 0).map(e => e.textContent.trim().slice(0, 70));
const st = () => JSON.stringify({ v2: [S.v2.x, S.v2.y, S.v2.h], n: S.n, iter: S.iter, mode: S.mode, flat: S.flat, cut: [S.cutOn, S.cut], edge: S.colour.edge, glow: S.colour.edgeGlow, inMode: S.colour.inMode, inPal: S.colour.inPal, inRev: S.colour.inRev, cutFace: S.colour.cutFace, pal: S.colour.pal, rev: S.colour.rev, trap: S.colour.trap, by: S.colour.by, cmode: S.colour.mode, reach: S.colour.reach, shownCtl: ['col-edge', 'col-edgeGlow', 'col-inMode', 'col-inPal', 'col-inRev', 'col-cutFace', 'col-reach'].filter(shown).join(' '), notes: notes(), status: ($('status') || {}).textContent });
"""
def mk(D):
    A = []
    def add(name, js, timeout=600, now=False):
        if now:
            A.append({"js": PRE + js + "\nreturn '%s ' + st();" % name, "sleep": 0.25, "shot": D + name + ".png", "clip": "#stage"})
        else:
            A.append({"js": PRE + js + "\nawait sleep(150); return '%s ' + st();" % name, "wait": "done", "timeout": timeout, "sleep": 0.3})
            A.append({"js": PRE + "await sleep(400); return null;", "wait": "done", "timeout": timeout, "shot": D + name + ".png", "clip": "#stage"})
    return A, add
IN = {1: 'Orbit trap', 2: 'Where the orbit ends up', 3: 'How deep inside', 4: 'How quickly the orbit settles'}
# ---- A: outline width, glow, inside colourings with palettes
A, add = mk('out/t9/flat/a/')
add('00-flat', "$('flat').click();")
for v in ('0', '0.3', '1', '3', '8'):
    add('edge-%s' % v.replace('.', '_'), "type('col-edgeNum', '%s');" % v)
add('edge-40-refused', "type('col-edgeNum', '40');")
add('edge-1-glow5', "type('col-edgeNum', '1'); type('col-edgeGlowNum', '5');")
add('edge-1-glow20', "type('col-edgeGlowNum', '20');")
add('edge-1-glow60', "type('col-edgeGlowNum', '60');")
add('edge-0-glow20', "type('col-edgeNum', '0'); type('col-edgeGlowNum', '20');")
add('edge-3-glow20', "type('col-edgeNum', '3'); type('col-edgeGlowNum', '20');")
add('edge-reset', "type('col-edgeNum', '1'); type('col-edgeGlowNum', '0');")
for mi, m in enumerate(('Orbit trap', 'Where the orbit ends up', 'How deep inside', 'How quickly the orbit settles'), 1):
    add('in%d-same' % mi, "pick('col-inMode', '%s'); pick('col-inPal', 'Same as outside'); " % m)
    for p in ('Fire', 'Classic blue and gold'):
        add('in%d-%s' % (mi, p.split()[0]), "pick('col-inPal', '%s'); check('col-inRev', false);" % p)
        add('in%d-%s-rev' % (mi, p.split()[0]), "check('col-inRev', true);")
add('in-plain-again', "pick('col-inMode', 'Plain');")
json.dump(A, open('out/t9/flat/a.json', 'w', encoding='utf-8'), indent=1)
# ---- B: thread and small copies, 300 iterations
A, add = mk('out/t9/flat/b/')
add('T-edge1', "$('flat').click(); type('iterNum', '300'); view(-1.86, 0, 0.06);")
add('T-edge0', "type('col-edgeNum', '0');")
add('T-edge3', "type('col-edgeNum', '3');")
add('C-plain', "type('col-edgeNum', '1'); view(-1.765, 0, 0.06);")
for k in (1, 2, 3, 4): add('C-in%d' % k, "pick('col-inMode', '%s');" % IN[k])
add('D-in4', "view(-1.9408, 0, 0.004);")
add('D-in3', "pick('col-inMode', '%s');" % IN[3])
add('D-plain', "pick('col-inMode', 'Plain');")
add('D-edge3', "type('col-edgeNum', '3');")
json.dump(A, open('out/t9/flat/b.json', 'w', encoding='utf-8'), indent=1)
# ---- C: zoom ladder, hold still while zooming and refining
A, add = mk('out/t9/flat/c/')
add('Z-3_2', "$('flat').click(); type('iterNum', '300'); view(-0.7453, 0.1127, 3.2);")
for h in ('0.3', '0.03', '0.003', '0.0005'): add('Z-%s' % h.replace('.', '_'), "view(-0.7453, 0.1127, %s);" % h)
add('H0', "type('iterNum', '14'); view(-0.6, 0, 3.328);")
for k in (1, 2, 3, 4):
    add('H%d-now' % k, "pick('col-inMode', '%s'); view(-0.6, 0, 3.328); await sleep(1200);" % IN[k], now=True)
    add('H%d-a' % k, "")
    add('H%d-b' % k, "view(-0.6, 0, 2.6);")
json.dump(A, open('out/t9/flat/c.json', 'w', encoding='utf-8'), indent=1)
# ---- D: cut face in 3D, and the inside colourings in the other modes
A, add = mk('out/t9/flat/d/')
add('cut-hatch', "check('cutOn', true); L.cam.pitch = 1.1; L.cam.yaw = -1.2; L.touch();")
add('cut-face-plain', "check('col-cutFace', true);")
for k in (1, 2, 3, 4): add('cut-face-in%d' % k, "pick('col-inMode', '%s');" % IN[k])
add('J-in4', "check('cutOn', false); $('flat').click(); $('mode-j').click(); S.c[0] = -0.123; S.c[1] = 0.745; S.c[2] = 0; L.syncControls(); L.refresh(false);")
for k in (3, 2, 1): add('J-in%d' % k, "pick('col-inMode', '%s');" % IN[k])
add('K-in1', "$('mode-k').click();")
for k in (2, 3, 4): add('K-in%d' % k, "pick('col-inMode', '%s');" % IN[k])
add('N' + '-in4', "$('mode-m').click(); type('powNum', '-2');")
add('N' + '-in2', "pick('col-inMode', '%s');" % IN[2])
add('M-in2', "type('powNum', '2'); check('m-mosaic', true);")
json.dump(A, open('out/t9/flat/d.json', 'w', encoding='utf-8'), indent=1)
print('ok')
