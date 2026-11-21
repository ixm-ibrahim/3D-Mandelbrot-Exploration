"""Round 27, entry, step 2: first pictures of the new group. python out/r27/entry/mk/first.py [page] [tag]
-> out/r27/entry/shots/<tag>-*.png and logs/<tag>.log"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

page = sys.argv[1] if len(sys.argv) > 1 else run.PAGE
tag = sys.argv[2] if len(sys.argv) > 2 else 'first'
P = 'out/r27/entry/shots/%s-' % tag
H = run.HEAD
steps = [
    run.UP,
    dict(js=H + """
const t0 = performance.now();
$('apMenuBtn').click(); await sleep(150);
if (!$('ap-balls')) fail('no row for Balls on balls in the Approach list');
$('ap-balls').click(); await sleep(100);
if (S.mode !== 'k' || S.k.group !== 1) fail('the row did not switch to Balls on balls: ' + S.mode + ' ' + S.k.group);
await settle();
window.__t = performance.now() - t0;
return 'Balls on balls on show after ' + Math.round(window.__t) + ' ms; menu reads "' + $('apMenuName').textContent + '"; cam ' + JSON.stringify(L.cam) + '; status: ' + $('status').textContent + '; compiles ' + L.R.compiles;
""", wait='done', timeout=600, shot=P + '3d-a.png', clip='#stage'),
    dict(js=H + "L.cam.yaw = -1.571; L.cam.pitch = 0.12; L.touch(); await settle(); return 'front eye';", wait='done', timeout=600, shot=P + '3d-front.png', clip='#stage'),
    dict(js=H + "L.cam.yaw = -0.25; L.cam.pitch = 0.3; L.touch(); await settle(); return 'nearly end-on';", wait='done', timeout=600, shot=P + '3d-end.png', clip='#stage'),
    dict(js=H + "L.cam.yaw = -1.25; L.cam.pitch = 0.5; S.k.bgrid = 1; go(); await settle(); return 'honeycomb grid';", wait='done', timeout=600, shot=P + '3d-hex.png', clip='#stage'),
    dict(js=H + "S.k.bgrid = 2; go(); await settle(); return 'a line only';", wait='done', timeout=600, shot=P + '3d-line.png', clip='#stage'),
    dict(js=H + "S.k.bgrid = 0; $('flat').click(); await sleep(200); await settle(); return 'flat view, v2 ' + JSON.stringify(S.v2);", wait='done', timeout=600, shot=P + 'flat.png', clip='#stage'),
    dict(js=H + "return 'whole window';", shot=P + 'window.png'),
]
code, text, vals = run.shot(page, steps, tag)
run.write(tag + '.log', text + 'exit %d\n' % code)
print(text[-4000:]); print('exit', code)
