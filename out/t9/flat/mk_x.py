# Second check, tester "flat": more flat pictures for v5 against v8 than the first check's thirteen, because its
# zoom picture (m-zoom, 14 iterations at height 0.02) is one flat colour and so tests nothing.
# Only state that both builds have is set. python out/t9/flat/mk_x.py
import json
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id), S = L.S;
const sleep = ms => new Promise(r => setTimeout(r, ms));
if (!document.getElementById('t6hide')) { const st = document.createElement('style'); st.id = 't6hide'; st.textContent = '#stage > *:not(canvas) { visibility: hidden !important; }'; document.head.appendChild(st); }
const go = () => { L.syncControls(); L.refresh(false); };
const view = (x, y, h) => { S.v2.x = x; S.v2.y = y; S.v2.h = h; go(); };
"""
def steps(tag):
    d = 'out/t9/flat/x%s/' % tag
    A = []
    def add(name, js, timeout=600):
        A.append({"js": PRE + js, "wait": "done", "timeout": timeout, "sleep": 0.5})
        A.append({"js": PRE + "await sleep(600); return JSON.stringify({name: '%s', v2: [S.v2.x, S.v2.y, S.v2.h], iter: S.iter, n: S.n, mode: S.mode, flat: S.flat, trap: S.colour.trap, by: S.colour.by, pal: S.colour.pal, rev: S.colour.rev, cmode: S.colour.mode, res: S.q && S.q.res});" % name,
                  "wait": "done", "timeout": timeout, "shot": d + name + ".png", "clip": "#stage"})
    add('m-i300', "$('flat').click(); S.iter = 300; go(); return S.iter;")
    add('m-i300-valley-03', "view(-0.7453, 0.1127, 0.3);")
    add('m-i300-valley-003', "view(-0.7453, 0.1127, 0.03);")
    add('m-i300-copy', "view(-1.765, 0, 0.06);")
    add('m-i300-thread', "view(-1.86, 0, 0.06);")
    add('m-i60-fast', "S.iter = 60; view(-0.6, 0, 3.328); $('qFast').click();")
    add('m-i60-ultra', "$('qUltra').click();")
    add('m-i60-fine', "$('qFine').click();")
    add('m-i60-bal', "$('qBal').click();")
    add('m-cross-bands', "S.colour.trap = 1; S.colour.by = 0; go();")
    add('m-point-step', "S.colour.trap = 0; S.colour.by = 1; go();")
    add('m-ring-fire', "S.colour.trap = 6; S.colour.by = 4; S.colour.pal = 5; S.colour.rev = false; go();")
    add('m-escape', "S.colour.mode = 2; go();")
    add('j-rabbit-zoom', "S.colour.mode = 0; S.colour.trap = 5; S.colour.pal = 8; S.colour.rev = true; S.iter = 100; go(); $('mode-j').click(); S.c[0] = -0.123; S.c[1] = 0.745; S.c[2] = 0; view(0.2, 0.3, 0.6);")
    add('k-zoom', "$('mode-k').click(); view(1.0, 0.0, 1.0);")
    return A
for tag in ('5', '8'):
    json.dump(steps(tag), open('out/t9/flat/x%s.json' % tag, 'w', encoding='utf-8'), indent=1)
print('ok')
