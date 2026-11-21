"""The eyes, second look at a find: faint lozenge-shaped patches on the bare skin of a large neighbour (seen at 300
and at 390 / 400 with the second sphere at 25). Which part of the picture makes them? The same view four times:
as the page draws it, with shadows off, with the crevice shading off, with both off. For each: the picture, and how
much darker the patch is than the skin round it (the box of the patch against a frame 12 px wide round the box).
  python out/r28/eyes/mk/skin.py   -> shots/skin-*.png, logs/skin.txt"""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run
import views, rays

BOX = (355, 598, 445, 678)      # the patch in the 862 x 701 picture of the view p300-r25-neighbour
KINDS = [('as-drawn', ''), ('no-shadow', 'S.q.shadow = false;'), ('no-crevice', 'S.q.shadow = true; S.q.ao = false;'), ('neither', 'S.q.shadow = false; S.q.ao = false;')]
if __name__ == '__main__':
    v = views.V['p300-r25-neighbour']
    js0 = rays.SETUP % (json.dumps('p300-r25-neighbour'), v['grid'], json.dumps(str(v['p'])), json.dumps(str(v['rho'])), v['depth'], json.dumps(views.cam_numbers(v)), 'false', rays.STEP)
    steps = [run.UP, {'js': js0, 'wait': 'done', 'timeout': 900}]
    for name, js in KINDS:
        steps.append({'js': run.HEAD + js + " go(); await settle(); for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden'; return '%s: shadow ' + S.q.shadow + ', crevice shading ' + S.q.ao + ', ' + $('status').textContent;" % name,
                      'wait': 'done', 'timeout': 600, 'shot': '%s/shots/skin-%s.png' % (run.OUT, name), 'clip': '#view'})
    code, text, vals = run.shot(run.PAGE, steps, 'skin', '1400x950', 'dark')
    lines = ['exit %d, %s' % (code, 'no console errors' if run.clean(text) else 'SEE THE LOG')] + [x for x in vals if 'shadow' in x and 'crevice' in x]
    x0, y0, x1, y1 = BOX
    for name, _ in KINDS:
        a = np.asarray(Image.open(os.path.join(run.EYES, 'shots', 'skin-%s.png' % name)).convert('RGB')).astype(float)
        lum = a.sum(axis=2) / 3
        inner = lum[y0:y1, x0:x1]
        frame = np.concatenate([lum[y0 - 12:y0, x0 - 12:x1 + 12].ravel(), lum[y1:y1 + 12, x0 - 12:x1 + 12].ravel(), lum[y0:y1, x0 - 12:x0].ravel(), lum[y0:y1, x1:x1 + 12].ravel()])
        # the strength of the patch's edges: the largest step between neighbouring pixels inside the box (a smooth skin has steps of 1 or 2)
        st = max(np.abs(np.diff(a[y0:y1, x0:x1], axis=1)).max(), np.abs(np.diff(a[y0:y1, x0:x1], axis=0)).max())
        n4 = int((np.abs(np.diff(a[y0:y1, x0:x1], axis=1)).max(axis=2) >= 4).sum())
        lines.append('%-11s box %s: darkest tenth of the box %.1f, middle of the box %.1f, middle of the frame round it %.1f (of 255); largest step between neighbouring pixels in the box %d; steps of 4 or more: %d'
                     % (name, BOX, np.percentile(inner, 10), np.median(inner), np.median(frame), st, n4))
    run.write('skin.txt', '\n'.join(lines) + '\n'); print('\n'.join(lines))
