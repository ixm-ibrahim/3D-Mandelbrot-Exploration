"""Round 27, final: the pictures for the user. Real screenshots of dist/r27-final.html, 1400x950, dark, the whole
window, nothing drawn on them. The page is opened fresh, the Approach list is opened and the row Balls on balls is
clicked (the user's way in); then only the camera is turned (and for the flat view the box "2D view" is ticked).
  python out/r27/final/mk/pics.py      -> out/r27/final/cand-*.png (candidates), logs/pics.txt
The three that are kept are copied to out/r27/final/user-*.png by hand after looking at them (see NOTES.md).
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

H = run.HEAD
INFO = " return JSON.stringify({ view: '%s', mode: S.mode, group: S.k.group, t: S.k.bt, grid: S.k.bgrid, depth: S.k.bit, flat: S.flat, cam: [+L.cam.yaw.toFixed(4), +L.cam.pitch.toFixed(3), +L.cam.dist.toFixed(3)], scrollY: Math.round(scrollY), status: $('status').textContent, stage: (() => { const b = $('stage').getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom)]; })() });"
CAM = "L.cam.yaw = %s; L.cam.pitch = %s; %s L.touch(); await settle();"

if __name__ == '__main__':
    P = run.OUT + '/cand-'
    steps = [run.UP,
             dict(js=H + "$('apMenuBtn').click(); await sleep(400); $('ap-balls').click(); await settle(); await sleep(300);" + INFO % 'as it opens after the click on the row', wait='done', timeout=300, shot=P + '0-as-it-opens.png'),
             dict(js=H + CAM % ('-1.5708', '0.22', '') + INFO % 'front', wait='done', timeout=300, shot=P + '1-front.png'),
             dict(js=H + CAM % ('0.0', '0.15', '') + INFO % 'end-on', wait='done', timeout=300, shot=P + '2a-end-on.png'),
             dict(js=H + CAM % ('0.0', '0.15', 'L.cam.dist = 2.6;') + INFO % 'end-on, nearer', wait='done', timeout=300, shot=P + '2b-end-on-nearer.png'),
             dict(js=H + "$('ballsFrame').click(); await settle(); " + CAM % ('-1.5708', '1.45', '') + INFO % 'above', wait='done', timeout=300, shot=P + '2c-above.png'),
             dict(js=H + "$('ballsFrame').click(); await settle(); $('flat').click(); await settle();" + INFO % 'flat view', wait='done', timeout=300, shot=P + '3-flat.png')]
    code, text, vals = run.shot(run.PAGE, steps, 'pics', '1400x950', 'dark')
    run.write('pics.log', text + 'exit %d\n' % code)
    lines = ['page %s, exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE logs/pics.log')] + vals[1:]
    out = '\n'.join(lines) + '\n'
    run.write('pics.txt', out); print(out)
    if code != 0:
        print(text[-2000:])
