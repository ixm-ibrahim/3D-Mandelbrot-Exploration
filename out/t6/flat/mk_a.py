import json, sys
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id), S = L.S;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
if (!document.getElementById('t6hide')) { const st = document.createElement('style'); st.id = 't6hide'; st.textContent = '#stage > *:not(canvas) { visibility: hidden !important; }'; document.head.appendChild(st); }
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const check = (id, on) => { const e = $(id); if (!e) fail('no control ' + id); if (e.checked !== on) e.click(); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const view = (x, y, h) => { S.v2.x = x; S.v2.y = y; S.v2.h = h; L.syncControls(); L.refresh(false); };
const st = () => JSON.stringify({ v2: [S.v2.x, S.v2.y, S.v2.h], n: S.n, iter: S.iter, mode: S.mode, flat: S.flat, cut: [S.cutOn, S.cut], edge: S.colour.edge, glow: S.colour.edgeGlow, inMode: S.colour.inMode, inPal: S.colour.inPal, inRev: S.colour.inRev, cutFace: S.colour.cutFace, pal: S.colour.pal, rev: S.colour.rev, trap: S.colour.trap, by: S.colour.by, cmode: S.colour.mode, shownCtl: ['col-edge', 'col-edgeGlow', 'col-inMode', 'col-inPal', 'col-inRev', 'col-cutFace'].filter(shown).join(' '), status: ($('status') || {}).textContent });
"""
A = []
D = 'out/t6/flat/a/'
def add(name, js, timeout=300):
    A.append({"js": PRE + js + "\nawait sleep(150); return '%s ' + st();" % name, "wait": "done", "timeout": timeout, "sleep": 0.3})
    A.append({"js": PRE + "await sleep(400); return null;", "wait": "done", "timeout": timeout, "shot": D + name + ".png", "clip": "#stage"})

add('00-flat', "$('flat').click();")
# --- outline width through the typed box
for v in ('0', '0.3', '1', '3', '8'):
    add('edge-%s' % v.replace('.', '_'), "type('col-edgeNum', '%s');" % v)
add('edge-40-refused', "type('col-edgeNum', '40');")   # Extreme is off: 40 is the typed limit
add('edge-1-glow5', "type('col-edgeNum', '1'); type('col-edgeGlowNum', '5');")
add('edge-1-glow20', "type('col-edgeGlowNum', '20');")
add('edge-1-glow60', "type('col-edgeGlowNum', '60');")
add('edge-0-glow20', "type('col-edgeNum', '0'); type('col-edgeGlowNum', '20');")
add('edge-3-glow20', "type('col-edgeNum', '3'); type('col-edgeGlowNum', '20');")
add('edge-reset', "type('col-edgeNum', '1'); type('col-edgeGlowNum', '0');")
# --- inside colourings
for mi, m in enumerate(('Orbit trap', 'Where the orbit ends up', 'How deep inside', 'How quickly the orbit settles'), 1):
    add('in%d-same' % mi, "pick('col-inMode', '%s'); pick('col-inPal', 'Same as outside'); " % m)
    for p in ('Fire', 'Classic blue and gold'):
        add('in%d-%s' % (mi, p.split()[0]), "pick('col-inPal', '%s'); check('col-inRev', false);" % p)
        add('in%d-%s-rev' % (mi, p.split()[0]), "check('col-inRev', true);")
add('in-plain-again', "pick('col-inMode', 'Plain');")
json.dump(A, open('out/t6/flat/a.json', 'w', encoding='utf-8'), indent=1)
print(len(A) // 2, 'pictures')
