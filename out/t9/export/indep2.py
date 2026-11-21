"""Independence from later changes, with the controls that are new since the first check.
python out/t9/export/indep2.py <A|B|C>
A: opening Mandelbrot (trap-coloured). B: Mandelbrot with "Orbit steps the trap reads" at 9 and trap radius 0.7.
C: example "Sea urchins" (Julia, trap is the solid) with trap thickness 0.02.
For each: a reference job (typed size, Fine, PNG) on an untouched page, then the same job with everything changed while
it runs; the two files must be equal pixel for pixel."""
import json, sys, time
import numpy as np
from drv import Lab, log, open_rgb, blank

J = lambda o: json.dumps(o, ensure_ascii=False)
which = sys.argv[1]
W, H = (2000, 1200)
SETUP = {
    'A': "",
    'B': "type('col-reachNum', '9'); type('col-radiusNum', '0.7');",
    'C': "pick('trapExamples', 'Sea urchins'); await sleep(200); type('col-thickNum', '0.02');",
}[which]
STATE = "const c = L.S.colour; return { mode: L.S.mode, approach: L.APPROACHES[L.S.approach].id, flat: !!L.S.flat, trap: c.trap, solid: c.solid, thick: c.thick, skip: c.skip, radius: c.radius, reach: c.reach, pal: chosen('col-pal'), iter: L.S.iter, n: L.S.n, extreme: !!L.S.extreme, example: $('trapExamples') ? chosen('trapExamples') : null };"


def run(lab, tag, during=None):
    st = lab.start_job('Typed', 'Fine', 'PNG', W, H, watch=False)
    if not st['busy']:
        log(tag, 'DID NOT START', J(st)); return None
    if during: during()
    done = lab.job_wait(900)
    en = lab.end_job()
    log(tag, 'ended' if done else 'TIMED OUT', J({k: v for k, v in en.items() if k not in ('tl', 'gapsAt')}))
    path, r = lab.save('I-%s-%s' % (which, tag))
    im, fmt = open_rgb(path)
    log(tag, 'file', J({'size': im.size, 'blank': blank(im), 'name': r['name']}))
    return im


def same(a, b):
    A, B = np.asarray(a, dtype=np.int16), np.asarray(b, dtype=np.int16)
    if A.shape != B.shape: return {'shape': [A.shape, B.shape]}
    d = np.abs(A - B).max(axis=2)
    return {'worst': int(d.max()), 'differ_pct': round(float((d > 0).mean() * 100), 4), 'over8_pct': round(float((d > 8).mean() * 100), 4)}


def setup(lab):
    lab.idle()
    if SETUP:
        lab.js(SETUP + " await sleep(150);")
    lab.idle(); time.sleep(0.4); lab.idle()
    return lab.js(STATE)


# the reference: an untouched page
lab = Lab()
try:
    log(which, 'state at Start (reference page)', J(setup(lab)))
    lab.stage_shot('I-%s-stage.png' % which)
    ref = run(lab, 'ref')
    log(which, 'problems', lab.problems())
finally:
    lab.close()

# the same job on a fresh page, with everything changed while it runs
lab = Lab()
try:
    log(which, 'state at Start (page to be changed)', J(setup(lab)))
    pcs = []

    def change_all():
        pc = lambda what: pcs.append([what, lab.js("return [L.exportBusy(), $('exportStep').textContent.replace(/^.*pixels\\. /, '')];")])
        pc('start')
        lab.js("type('col-reachNum', '2');"); pc('Orbit steps the trap reads 2')
        lab.js("type('col-reachNum', '16'); type('col-radiusNum', '0.35'); type('col-glowNum', '4');"); pc('reads 16, radius 0.35, glow 4')
        lab.js("pick('trapExamples', 'Spiky coral');"); pc('example Spiky coral')
        lab.js("type('col-thickNum', '0.006'); type('col-skipNum', '3');"); pc('trap thickness 0.006, skip 3')
        lab.js("pick('trapExamples', 'Chain of bubbles');"); pc('example Chain of bubbles (Julia)')
        lab.js("$('twinLathe').click();"); pc('Twin of the Lathe')
        lab.js("$('fig4Show').click();"); pc('Show Figure 4')
        lab.js("pick('col-pal', 'Fire'); $('col-rev').click(); pick('col-mode', 'Escape count');"); pc('palette Fire, not reversed, colour by escape count')
        lab.js("$('qUltra').click();"); pc('Ultra fast')
        lab.js("pick('trapExamples', 'Pearls and balls');"); pc('example Pearls and balls (Kleinian)')
        lab.js("$('extreme').click(); await sleep(50); type('col-reachNum', '40');"); pc('Extreme ranges, reads 40')
        lab.js("$('flat').click(); await sleep(150); pick('col-inMode', 'How quickly'); await sleep(150); $('flat').click();"); pc('2D view with an inside colouring and back')
        lab.js("$('secMesh').open = true; $('meshStart').click(); await sleep(1500); if ($('meshCancel')) $('meshCancel').click();"); pc('a model job started and cancelled')
        lab.js("pick('exportSize', '1920'); pick('exportQuality', 'Extra fine'); pick('exportKind', 'WebP');"); pc('the panel own choices')
        lab.js("$('zoomIn').click(); $('zoomIn').click(); $('reset').click();"); pc('zoom buttons, Reset view')
        lab.js("$('resetAll').click();"); pc('Reset everything')
        lab.js("$('mode-k').click();"); pc('Kleinian mode')
        log(which, 'changes made while the job ran (what, [still running, percent]):', J(pcs))
    got = run(lab, 'changed', during=change_all)
    if ref is not None and got is not None:
        log(which, 'CHANGED AGAINST REFERENCE:', J(same(ref, got)))
    lab.idle()
    log(which, 'live state after', J(lab.js(STATE)))
    log(which, 'problems', lab.problems())
finally:
    lab.close()
