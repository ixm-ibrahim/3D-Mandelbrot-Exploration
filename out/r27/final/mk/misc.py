"""Round 27, final: two small comparisons with the frozen page.
(a) The section "One step, seen on directions" under the picture: is it on show in the Kleinian view, with the first
    group on the frozen page, and with each group on the final page?
(b) The eye inside the solid: what does the picture show? Frozen page, Mandelbrot as it opens, the camera moved into
    the solid; final page, Balls on balls, the camera moved into the middle ball. Share of the picture that is black.
  python out/r27/final/mk/misc.py   -> logs/misc.txt, shots/misc-*.png"""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

H = run.HEAD + """
const sec = () => { const hs = [...document.querySelectorAll('h2, h3')].filter(h => /One step, seen on directions/.test(h.textContent)); return hs.length ? vis(hs[0]) : 'no such heading'; };
const hide = () => { for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden'; };
const show = () => { for (const e of $('stage').children) e.style.visibility = ''; };
"""

if __name__ == '__main__':
    lines = []
    for tag, page in (('old', run.BASE), ('new', run.PAGE)):
        P = run.OUT + '/shots/misc-%s-' % tag
        steps = [run.UP,
                 dict(js=H + "const r = { page: '%s', mandelbrot_oneStepSectionShown: sec() }; $('mode-k').click(); await settle(); r.kleinianFirstGroup_oneStepSectionShown = sec(); r.tableShown = vis($('card'));"
                              " if ($('ap-balls')) { $('ap-balls').click(); await settle(); r.ballsOnBalls_oneStepSectionShown = sec(); } return JSON.stringify(r);" % tag),
                 dict(js=H + "$('resetAll').click(); await settle(); L.cam.target = [-0.2, 0, 0]; L.cam.dist = 0.05; L.touch(); await settle(); hide();"
                              " return JSON.stringify({ eyeInsideTheMandelbrotSolid: L.basis().pos.map(x => +x.toFixed(3)), pickAtTheMiddle: !!L.pick($('stage').clientWidth / 2, $('stage').clientHeight / 2), status: $('status').textContent });",
                      shot=P + 'eye-inside-mandelbrot.png', clip='#view'),
                 dict(js=H + "show(); $('mode-k').click(); await settle(); if ($('kleinGroup0')) { $('kleinGroup0').click(); await settle(); } const c = L.pick($('stage').clientWidth / 2, $('stage').clientHeight / 2);"
                              " if (!c) return JSON.stringify({ firstGroup: 'no stop at the middle of the picture' });"
                              " const b = L.basis(), f = b.f; L.cam.target = [c[0] + 0.03 * f[0], c[1] + 0.03 * f[1], c[2] + 0.03 * f[2]]; L.cam.dist = 0.01; L.touch(); await settle(); hide();"
                              " return JSON.stringify({ eyeInsideAPearlOfTheFirstGroup: L.basis().pos.map(x => +x.toFixed(3)), status: $('status').textContent });",
                      shot=P + 'eye-inside-first-group.png', clip='#view')]
        code, text, vals = run.shot(page, steps, 'misc-' + tag, '1400x950', 'dark')
        lines.append('%s: exit %d, %s' % (page, code, 'no console errors' if run.clean(text) else 'SEE THE LOG'))
        lines += ['  ' + v for v in vals[1:]]
        for n in ('eye-inside-mandelbrot', 'eye-inside-first-group'):
            f = os.path.join(run.ENTRY, 'shots', 'misc-%s-%s.png' % (tag, n))
            if os.path.exists(f):
                im = np.asarray(Image.open(f).convert('RGB')).astype(int)
                lines.append('  %s: %d of %d pixels darker than 12 of 255; %d different colours' % (n, int((im.max(axis=2) < 12).sum()), im.shape[0] * im.shape[1], len(np.unique(im.reshape(-1, 3), axis=0))))
        if code != 0:
            lines.append(text[-1500:])
    f = os.path.join(run.ENTRY, 'shots', 'holes2-t1-inside-a-ball.png')
    if os.path.exists(f):
        im = np.asarray(Image.open(f).convert('RGB')).astype(int)
        lines.append('final page, Balls on balls, the eye inside the middle ball (shots/holes2-t1-inside-a-ball.png): %d of %d pixels darker than 12 of 255; %d different colours' % (int((im.max(axis=2) < 12).sum()), im.shape[0] * im.shape[1], len(np.unique(im.reshape(-1, 3), axis=0))))
    out = '\n'.join(lines) + '\n'
    run.write('misc.txt', out); print(out)
