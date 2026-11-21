import json, sys
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id), S = L.S;
const sleep = ms => new Promise(r => setTimeout(r, ms));
if (!document.getElementById('t6hide')) { const st = document.createElement('style'); st.id = 't6hide'; st.textContent = '#stage > *:not(canvas) { visibility: hidden !important; }'; document.head.appendChild(st); }
"""
def steps(tag):
    d = 'out/t6/flat/eq%s/' % tag
    A = []
    def add(name, js, timeout=300):
        A.append({"js": PRE + js, "wait": "done", "timeout": timeout, "sleep": 0.5})
        A.append({"js": PRE + "await sleep(600); const c = $('view'); return JSON.stringify({name: '%s', w: c.width, h: c.height, cw: c.clientWidth, ch: c.clientHeight, v2: S.v2, cut: S.cut, n: S.n, mode: S.mode, flat: S.flat, col: S.colour});" % name,
                  "wait": "done", "timeout": timeout, "shot": d + name + ".png", "clip": "#stage"})
    add('3d-open', "return 'open';")
    add('m', "$('flat').click(); return 'flat ' + S.flat;")
    add('j-default', "$('mode-j').click(); return JSON.stringify(S.c);")
    add('j-rabbit', "S.c[0] = -0.123; S.c[1] = 0.745; S.c[2] = 0; L.syncControls(); L.refresh(false); return JSON.stringify(S.c);")
    add('j-dendrite', "S.c[0] = 0; S.c[1] = 1; S.c[2] = 0; L.syncControls(); L.refresh(false); return JSON.stringify(S.c);")
    add('j-slice03', "S.c[0] = -0.8; S.c[1] = 0.156; S.c[2] = 0; S.cut = 0.3; L.syncControls(); L.refresh(false); return JSON.stringify(S.c);")
    add('m-slice025', "$('mode-m').click(); S.cut = 0.25; L.syncControls(); L.refresh(false); return S.cut;")
    add('m-slice-06', "S.cut = -0.6; L.syncControls(); L.refresh(false); return S.cut;")
    add('k', "S.cut = 0; L.syncControls(); $('mode-k').click(); return S.mode;")
    add('k-slice02', "S.cut = 0.2; L.syncControls(); L.refresh(false); return S.cut;")
    add('m-neg2', "S.cut = 0; $('mode-m').click(); S.n = -2; L.syncControls(); L.refresh(false); return S.n;")
    add('m-pow3', "S.n = 3; L.syncControls(); L.refresh(false); return S.n;")
    add('m-zoom', "S.n = 2; S.v2.x = -0.745; S.v2.y = 0.113; S.v2.h = 0.02; L.syncControls(); L.refresh(false); return JSON.stringify(S.v2);")
    add('m-mosaic', "S.v2.x = -0.5; S.v2.y = 0; S.v2.h = 3.2; L.syncControls(); $('m-mosaic').click(); return 'mosaic ' + S.mosaic;")
    return A
for tag in ('5', '6'):
    json.dump(steps(tag), open('out/t6/flat/eq%s.json' % tag, 'w', encoding='utf-8'), indent=1)
print('ok')
