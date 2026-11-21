import json, re
src = open('out/t6/flat/mk_a.py', encoding='utf-8').read()
PRE = re.search(r'PRE = r"""(.*?)"""', src, re.S).group(1)
def mk(D):
    A = []
    def add(name, js, timeout=400, now=False):
        if now:
            A.append({"js": PRE + js + "\nreturn '%s ' + st();" % name, "sleep": 0.25, "shot": D + name + ".png", "clip": "#stage"})
        else:
            A.append({"js": PRE + js + "\nawait sleep(150); return '%s ' + st();" % name, "wait": "done", "timeout": timeout, "sleep": 0.3})
            A.append({"js": PRE + "await sleep(400); return null;", "wait": "done", "timeout": timeout, "shot": D + name + ".png", "clip": "#stage"})
    return A, add
IN = {1: 'Orbit trap', 2: 'Where the orbit ends up', 3: 'How deep inside', 4: 'How quickly the orbit settles'}
# ---- B: thread and small copies, 300 iterations
A, add = mk('out/t6/flat/b/')
add('T-edge1', "$('flat').click(); type('iterNum', '300'); view(-1.86, 0, 0.06);")
add('T-edge0', "type('col-edgeNum', '0');")
add('T-edge3', "type('col-edgeNum', '3');")
add('C-plain', "type('col-edgeNum', '1'); view(-1.765, 0, 0.06);")
for k in (1, 2, 3, 4): add('C-in%d' % k, "pick('col-inMode', '%s');" % IN[k])
add('D-in4', "view(-1.9408, 0, 0.004);")
add('D-in3', "pick('col-inMode', '%s');" % IN[3])
add('D-plain', "pick('col-inMode', 'Plain');")
add('D-edge3', "type('col-edgeNum', '3');")
json.dump(A, open('out/t6/flat/b.json', 'w', encoding='utf-8'), indent=1)
# ---- C: zoom ladder, hold still while zooming and refining
A, add = mk('out/t6/flat/c/')
add('Z-3_2', "$('flat').click(); type('iterNum', '300'); view(-0.7453, 0.1127, 3.2);")
for h in ('0.3', '0.03', '0.003', '0.0005'): add('Z-%s' % h.replace('.', '_'), "view(-0.7453, 0.1127, %s);" % h)
add('H0', "type('iterNum', '14'); view(-0.6, 0, 3.328);")
for k in (1, 2, 3, 4):
    add('H%d-now' % k, "pick('col-inMode', '%s'); view(-0.6, 0, 3.328); await sleep(1200);" % IN[k], now=True)
    add('H%d-a' % k, "")
    add('H%d-b' % k, "view(-0.6, 0, 2.6);")
json.dump(A, open('out/t6/flat/c.json', 'w', encoding='utf-8'), indent=1)
# ---- D: cut face in 3D, and the inside colourings in the other modes
A, add = mk('out/t6/flat/d/')
add('cut-hatch', "check('cutOn', true); L.cam.pitch = 1.1; L.cam.yaw = -1.2; L.touch();")
add('cut-face-plain', "check('col-cutFace', true);")
for k in (1, 2, 3, 4): add('cut-face-in%d' % k, "pick('col-inMode', '%s');" % IN[k])
add('J-in4', "check('cutOn', false); $('flat').click(); $('mode-j').click(); S.c[0] = -0.123; S.c[1] = 0.745; S.c[2] = 0; L.syncControls(); L.refresh(false);")
for k in (3, 2, 1): add('J-in%d' % k, "pick('col-inMode', '%s');" % IN[k])
add('K-in1', "$('mode-k').click();")
for k in (2, 3, 4): add('K-in%d' % k, "pick('col-inMode', '%s');" % IN[k])
add('N-in4', "$('mode-m').click(); type('powNum', '-2');")
add('N-in2', "pick('col-inMode', '%s');" % IN[2])
add('M-in2', "type('powNum', '2'); check('m-mosaic', true);")
json.dump(A, open('out/t6/flat/d.json', 'w', encoding='utf-8'), indent=1)
