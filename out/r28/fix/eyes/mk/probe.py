"""The eyes, first look: what is on the page (ids, numbers of the view), and one picture at 150 reached by typing.
  python out/r28/fix/eyes/mk/probe.py   -> logs/probe.txt, shots/probe-*.png"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run

JS1 = run.HEAD + """
$('ap-balls').click(); await settle();
const ids = [...document.querySelectorAll('[id]')].map(e => e.id).filter(i => /balls|klein|mode-|tab|learn|theme|view2|flat|frame/i.test(i));
const b = L.basis();
return JSON.stringify({ ids, fov: S.view.fov, bound: S.view.bound, cam: [L.cam.yaw, L.cam.pitch, L.cam.dist, L.cam.target], stage: [$('stage').clientWidth, $('stage').clientHeight], canvas: [$('view').width, $('view').height],
  k: S.k, q: S.q, v2: S.v2, view: S.view, flat: S.flat, status: $('status').textContent, basisKeys: Object.keys(b), Rkeys: Object.keys(L.R), sig: String(L.R.sig).slice(0, 80), warn: warn(), dpr: devicePixelRatio });
"""
JS2 = run.HEAD + """
await type('ballsSize', '150'); await settle();
return JSON.stringify({ k: S.k, cam: [L.cam.yaw, L.cam.pitch, L.cam.dist, L.cam.target], bound: S.view.bound, status: $('status').textContent, warn: warn(), sizeBox: $('ballsSizeNum').value, rhoBox: $('ballsRhoNum').value, sig: String(L.R.sig).slice(0, 80) });
"""
JS3 = run.HEAD + """
$('ballsFrame').click(); await settle();
return JSON.stringify({ k: S.k, cam: [L.cam.yaw, L.cam.pitch, L.cam.dist, L.cam.target], bound: S.view.bound, status: $('status').textContent, warn: warn(), reach: L.ballsReach() });
"""
JS4 = run.HEAD + """
S.flat = true; go(); await settle();
return JSON.stringify({ v2: S.v2, status: $('status').textContent, warn: warn() });
"""
if __name__ == '__main__':
    steps = [run.UP, {'js': JS1, 'shot': run.OUT + '/shots/probe-default.png'},
             {'js': JS2, 'shot': run.OUT + '/shots/probe-150-typed.png'},
             {'js': JS3, 'shot': run.OUT + '/shots/probe-150-framed.png'},
             {'js': JS4, 'shot': run.OUT + '/shots/probe-150-2d.png'}]
    code, text, vals = run.shot(run.PAGE, steps, 'probe', '1400x950', 'dark')
    run.write('probe.txt', text + 'exit %d\n' % code); run.write('probe-vals.txt', '\n'.join(vals) + '\n')
    print(text[-9000:]); print('exit', code)
