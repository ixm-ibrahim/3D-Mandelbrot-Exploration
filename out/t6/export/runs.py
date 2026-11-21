"""Runs B to F of the export tester.  python out/t6/export/runs.py <indep|states|refuse|gaps|lost>"""
import json, os, sys, time
import numpy as np
from PIL import Image
from drv import Lab, HERE, HOOK, log, open_rgb, blank, compare, seams, tl_report

J = lambda o: json.dumps(o, ensure_ascii=False)


def job(lab, tag, size, quality, kind, w=None, h=None, stage=None, during=None, timeout=900):
    st = lab.start_job(size, quality, kind, w, h)
    if not st['busy']:
        log(tag, 'DID NOT START', J(st)); return None, None
    if during: during()
    done = lab.job_wait(timeout)
    en = lab.end_job()
    log(tag, 'ended' if done else 'TIMED OUT', J({k: v for k, v in en.items() if k != 'tl'}))
    if not done or not en['saveShown']:
        return None, None
    path, r = lab.save(tag)
    log(tag, 'saved', J(r))
    im, fmt = open_rgb(path)
    out = {'fmt': fmt, 'size': im.size, 'blank': blank(im)}
    if stage: out['stage'] = compare(im, stage, tag + '-pair.png')
    out['borders'] = seams(im)
    log(tag, 'file', J(out))
    return path, im


def same(a, b):
    A, B = np.asarray(a, dtype=np.int16), np.asarray(b, dtype=np.int16)
    if A.shape != B.shape: return {'shape': [A.shape, B.shape]}
    d = np.abs(A - B).max(axis=2)
    return {'worst': int(d.max()), 'differ_pct': round(float((d > 0).mean() * 100), 4), 'over8_pct': round(float((d > 8).mean() * 100), 4)}


def drag(lab, secs=5.0):
    """A real mouse drag over the picture, back and forth, for about `secs` seconds."""
    b = lab.js("const r = $('view').getBoundingClientRect(); return [r.left, r.top, r.width, r.height];")
    cx, cy = b[0] + b[2] / 2, b[1] + b[3] / 2
    p = lab.page
    p.call('Input.dispatchMouseEvent', type='mouseMoved', x=cx, y=cy)
    p.call('Input.dispatchMouseEvent', type='mousePressed', x=cx, y=cy, button='left', buttons=1, clickCount=1)
    t0, i = time.time(), 0
    while time.time() - t0 < secs:
        i += 1
        x = cx + 120 * np.sin(i / 14.0); y = cy + 40 * np.sin(i / 23.0)
        p.call('Input.dispatchMouseEvent', type='mouseMoved', x=float(x), y=float(y), button='left', buttons=1)
        time.sleep(0.012)
    p.call('Input.dispatchMouseEvent', type='mouseReleased', x=float(x), y=float(y), button='left', clickCount=1)
    return i


GAPS_ON = """window.__g2 = []; window.__r2 = true; { let last = performance.now(); const tick = () => { const now = performance.now(); window.__g2.push(now - last); last = now; if (window.__r2) requestAnimationFrame(tick); }; requestAnimationFrame(tick); }"""
GAPS_OFF = """window.__r2 = false; const g = window.__g2.slice(2).sort((a, b) => a - b), n = g.length;
return { frames: n, mean: +(g.reduce((a, b) => a + b, 0) / n).toFixed(1), p95: +g[Math.floor(n * 0.95)].toFixed(1), p99: +g[Math.floor(n * 0.99)].toFixed(1), worst: +g[n - 1].toFixed(1), over50: g.filter(x => x > 50).length, over100: g.filter(x => x > 100).length };"""


# ---------- B: a job started, then everything changed
def indep():
    lab = Lab()
    try:
        lab.idle(); lab.stage_shot('B-stage.png')
        _, ref = job(lab, 'B-ref', 'Typed', 'Fine', 'PNG', 1600, 900, stage='B-stage.png')

        def change_all():
            pcs = []
            pc = lambda: lab.js("return [L.exportBusy(), $('exportStep').textContent];")
            lab.js("$('mode-j').click(); await sleep(30); pick('juliaPreset', 'Douady rabbit');"); pcs.append(pc())
            lab.js("$('ap-bulb').click();"); pcs.append(pc())
            lab.js("pick('col-pal', 'Fire'); pick('col-trap', 'Cross'); type('powNum', '3'); type('iterNum', '9');"); pcs.append(pc())
            drag(lab, 1.5)
            b = lab.js("const r = $('view').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2];")
            for _ in range(4): lab.page.call('Input.dispatchMouseEvent', type='mouseWheel', x=b[0], y=b[1], deltaX=0, deltaY=-240)
            pcs.append(pc())
            lab.js("$('qUltra').click(); $('cutOn').click(); await sleep(50); $('flat').click(); await sleep(200); $('flat').click();"); pcs.append(pc())
            lab.js("pick('exportSize', '1920'); pick('exportQuality', 'As on screen'); pick('exportKind', 'JPG'); $('extreme').click();"); pcs.append(pc())
            log('B changes made while', J(pcs))
        _, got = job(lab, 'B-changed', 'Typed', 'Fine', 'PNG', 1600, 900, stage='B-stage.png', during=change_all)
        if ref is not None and got is not None:
            log('B changed against reference:', J(same(ref, got)))
        lab.idle(); lab.stage_shot('B-live-after.png')
        log('B live state after', lab.js("return { mode: L.S.mode, approach: L.APPROACHES[L.S.approach].id, n: L.S.n, iter: L.S.iter, pal: chosen('col-pal'), trap: chosen('col-trap'), cutOn: L.S.cutOn, flat: L.S.flat, q: L.S.q.aa, extreme: L.S.extreme, size: chosen('exportSize'), kind: chosen('exportKind') };"))
        # second round: Reset everything, a resized window and the other theme during the job
        lab.js("$('exportDiscard').click(); $('resetAll').click();"); lab.idle()
        lab.js("pick('exportSize', 'Typed'); pick('exportQuality', 'Fine'); pick('exportKind', 'PNG');")
        lab.js("$('mode-k').click();"); lab.idle(); lab.stage_shot('B2-stage.png')
        _, ref2 = job(lab, 'B2-ref', 'Typed', 'Fine', 'PNG', 1600, 900, stage='B2-stage.png')

        def change2():
            lab.js("$('resetAll').click();")
            lab.page.call('Emulation.setDeviceMetricsOverride', width=1000, height=700, deviceScaleFactor=1, mobile=False)
            lab.page.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-color-scheme', 'value': 'light'}])
            log('B2 changes made while', J(lab.js("return [L.exportBusy(), $('exportStep').textContent, L.S.mode, innerWidth];")))
        _, got2 = job(lab, 'B2-changed', 'Typed', 'Fine', 'PNG', 1600, 900, during=change2)
        if ref2 is not None and got2 is not None:
            log('B2 changed (reset everything, window resized, light theme) against reference:', J(same(ref2, got2)))
        log('problems', lab.problems())
    finally:
        lab.close()


# ---------- C: cancel, again, discard, second job, and the kinds of picture
def states():
    lab = Lab()
    try:
        lab.idle()
        # real mouse: open the section, press Start, press Cancel
        lab.js("$('secExport').scrollIntoView({ block: 'center' }); await sleep(200);")
        def click(sel):
            b = lab.js("const e = document.querySelector(%s); e.scrollIntoView({ block: 'center' }); await sleep(120); const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, r.width];" % json.dumps(sel))
            for kind in ('mousePressed', 'mouseReleased'):
                lab.page.call('Input.dispatchMouseEvent', type=kind, x=b[0], y=b[1], button='left', clickCount=1)
            return b
        click('#secExport > summary'); time.sleep(0.3)
        log('C section open after a real click on its heading:', lab.js("return $('secExport').open;"))
        lab.js("pick('exportSize', '3840'); pick('exportQuality', 'Extra fine');")
        click('#exportStart'); time.sleep(0.15); click('#exportStart') if lab.js("return shown('exportStart');") else None
        time.sleep(1.5)
        log('C running', J(lab.js("return { busy: L.exportBusy(), step: $('exportStep').textContent, bar: $('exportBar').getAttribute('aria-valuenow'), startShown: shown('exportStart'), cancelShown: shown('exportCancel'), focus: document.activeElement.id };")))
        lab.shot('C-running.png', '#secExport')
        click('#exportCancel')
        t0 = time.time(); lab.job_wait(60)
        log('C after Cancel (%.1f s)' % (time.time() - t0), J(lab.js("await sleep(150); return { busy: L.exportBusy(), msg: $('exportMsg').textContent, startShown: shown('exportStart'), saveShown: shown('exportSave'), focus: document.activeElement.id, files: window.files.length };")))
        lab.shot('C-cancelled.png', '#secExport')
        # start again after the cancel; then a second job without Discard is not possible: is Start hidden?
        lab.stage_shot('C-m-stage.png')
        job(lab, 'C-m-same', 'As on screen', 'As on screen', 'PNG', stage='C-m-stage.png')
        log('C finished state', J(lab.js("return { startShown: shown('exportStart'), saveShown: shown('exportSave'), discardShown: shown('exportDiscard'), sizeShown: shown('exportSize'), msg: $('exportMsg').textContent };")))
        lab.shot('C-done.png', '#secExport')
        # save twice, then discard
        log('C second save', J(lab.js("const n = window.files.length; $('exportSave').click(); await sleep(300); return { got: window.files.length - n, msg: $('exportMsg').textContent };")))
        log('C discard', J(lab.js("$('exportDiscard').click(); await sleep(100); return { startShown: shown('exportStart'), saveShown: shown('exportSave'), msg: $('exportMsg').textContent, focus: document.activeElement.id };")))
        # double press on Start: one job only
        log('C double press', J(lab.js("pick('exportSize', 'As on screen'); pick('exportQuality', 'As on screen'); $('exportStart').click(); $('exportStart').click(); await sleep(100); return { busy: L.exportBusy() };")))
        lab.job_wait(120); lab.js("if (shown('exportDiscard')) $('exportDiscard').click();")
        kinds = [
            ('C-m2x', "", 'Twice', 'Fine'),
            ('C-flat', "$('flat').click();", 'As on screen', 'As on screen'),
            ('C-flat4k', "", '3840', 'Fine'),
            ('C-flatglow', "type('col-edgeNum', '3'); if ($('col-edgeGlowNum')) type('col-edgeGlowNum', '0.6'); pick('col-inMode', 'How quickly');", 'Twice', 'As on screen'),
            ('C-mosaic2d', "L.resetAll(); await sleep(50); $('m-mosaic').click(); await sleep(50); $('flat').click();", 'As on screen', 'As on screen'),
            ('C-mosaic3d', "$('flat').click();", 'As on screen', 'As on screen'),
            ('C-mosaic3d-2x', "", 'Twice', 'As on screen'),
            ('C-cut', "L.resetAll(); await sleep(50); $('cutOn').click();", 'As on screen', 'As on screen'),
            ('C-cut4k', "", '3840', 'As on screen'),
            ('C-cutface', "$('col-cutFace').click(); pick('col-inMode', 'How quickly');", 'Twice', 'As on screen'),
            ('C-klein', "L.resetAll(); await sleep(50); $('mode-k').click();", 'As on screen', 'As on screen'),
            ('C-klein2x', "", 'Twice', 'Fine'),
            ('C-solid', "L.resetAll(); await sleep(50); $('mode-j').click(); await sleep(50); pick('col-solid', 'Is the solid');", 'As on screen', 'As on screen'),
            ('C-solid2x', "", 'Twice', 'Fine'),
            ('C-solidk', "$('mode-k').click();", 'Twice', 'As on screen'),
        ]
        for tag, js, size, quality in kinds:
            try:
                if js:
                    lab.js(js + " await sleep(100);")
                lab.idle(); time.sleep(0.3); lab.idle()
                lab.stage_shot(tag + '-stage.png')
                job(lab, tag, size, quality, 'PNG', stage=tag + '-stage.png')
            except Exception as e:
                log(tag, 'FAILED', repr(e)[:400])
        log('problems', lab.problems())
    finally:
        lab.close()


# ---------- D: sizes that cannot be held, and a refused save
def refuse():
    lab = Lab()
    try:
        lab.idle()
        r = lab.js("""
$('secExport').open = true; pick('exportSize', 'Typed'); await sleep(50);
const out = {};
out.boxes = { wMax: $('exportWNum').max, wMin: $('exportWNum').min, shown: shown('exportWNum') };
type('exportWNum', '20000'); type('exportHNum', '20000'); await sleep(50);
out.typed20000 = [$('exportWNum').value, $('exportHNum').value, $('exportSizeNote').textContent];
type('exportWNum', 'abc'); type('exportHNum', '-5'); await sleep(50);
out.nonsense = [$('exportWNum').value, $('exportHNum').value, $('exportSizeNote').textContent];
type('exportWNum', '3'); type('exportHNum', '0'); await sleep(50);
out.tiny = [$('exportWNum').value, $('exportHNum').value, $('exportSizeNote').textContent];
type('exportWNum', '1000.6'); type('exportHNum', '500.4'); await sleep(50);
out.fraction = [$('exportWNum').value, $('exportHNum').value, $('exportSizeNote').textContent];
$('extreme').click(); await sleep(80);
type('exportWNum', '20000'); type('exportHNum', '20000'); await sleep(50);
out.extreme20000 = [$('exportWNum').value, $('exportHNum').value, $('exportSizeNote').textContent];
$('exportStart').click(); await sleep(400);
out.refused = { busy: L.exportBusy(), msg: $('exportMsg').textContent, startShown: shown('exportStart') };
return out;""")
        log('D typed sizes', J(r))
        lab.shot('D-refused.png', '#secExport')
        # just under the limit of 100 million pixels: does it start, and does Cancel work?
        r = lab.js("""type('exportWNum', '16384'); type('exportHNum', '6100'); pick('exportQuality', 'As on screen'); await sleep(50);
const note = $('exportSizeNote').textContent; const t = performance.now(); $('exportStart').click(); await sleep(3000);
return { note, busy: L.exportBusy(), step: $('exportStep').textContent, msg: $('exportMsg').textContent, ms: Math.round(performance.now() - t) };""")
        log('D 16384 x 6100', J(r))
        r = lab.js("""if (L.exportBusy()) $('exportCancel').click(); await sleep(1500); const e1 = { busy: L.exportBusy(), msg: $('exportMsg').textContent };
$('extreme').click(); await sleep(80);
return { afterCancel: e1, extremeOff: [$('exportWNum').value, $('exportHNum').value, $('exportSizeNote').textContent] };""")
        log('D after cancel, extreme off', J(r))
        lab.idle()
        # a small picture to save
        lab.js("pick('exportSize', 'Typed'); type('exportWNum', '400'); type('exportHNum', '300'); pick('exportQuality', 'As on screen'); pick('exportKind', 'PNG'); await sleep(50); $('exportStart').click();")
        lab.job_wait(120)
        # 1. the hook throws
        r = lab.js("""window.__rej = []; addEventListener('unhandledrejection', e => window.__rej.push(String(e.reason && e.reason.message || e.reason)));
window.squaringLabSaveHook = () => { throw new Error('hook says no'); };
$('exportSave').click(); await sleep(500);
const a = { msg: $('exportMsg').textContent, saveShown: shown('exportSave'), rejections: window.__rej.slice() };
window.files = []; window.squaringLabSaveHook = (name, blob) => { window.files.push({ name, blob }); };
$('exportSave').click(); await sleep(500);
const b = { msg: $('exportMsg').textContent, got: window.files.length };
return { hookThrows: a, thenGoodHook: b };""")
        log('D hook throws', J(r))
        lab.shot('D-hook-throws.png', '#secExport')
        # 2. a fresh picture, the host declines
        r = lab.js("""$('exportDiscard').click(); await sleep(100); $('exportStart').click(); await sleep(200); return L.exportBusy();""")
        lab.job_wait(120)
        r = lab.js("""delete window.squaringLabSaveHook;
window.__calls = []; window.__mode = 'declined';
window.claude = { use: async what => { window.__calls.push('use:' + what); return { save: async o => { window.__calls.push('save:' + o.filename + ':' + (o.data && o.data.size)); if (window.__mode === 'ok') return {}; const e = new Error('no'); e.code = window.__mode; throw e; } }; } };
const out = {};
for (const mode of ['declined', 'rate_limited', 'too_large', 'rejected_extension', 'something_new', 'ok']) {
  window.__mode = mode; $('exportSave').click(); await sleep(400);
  out[mode] = { msg: $('exportMsg').textContent, saveShown: shown('exportSave'), discardShown: shown('exportDiscard') };
}
out.calls = window.__calls;
return out;""")
        log('D host answers', J(r))
        lab.shot('D-declined.png', '#secExport')
        r = lab.js("""window.__mode = 'declined'; $('exportSave').click(); await sleep(300); return $('exportMsg').textContent;""")
        log('D declined message alone:', r)
        lab.shot('D-declined-msg.png', '#secExport')
        log('problems', lab.problems())
    finally:
        lab.close()
    # the host cannot save at all (use rejects), on a fresh page
    lab = Lab(hook=False)
    try:
        lab.idle()
        lab.js("window.claude = { use: async () => { throw new Error('no downloads'); } }; $('secExport').open = true; pick('exportSize', 'Typed'); type('exportWNum', '320'); type('exportHNum', '200'); pick('exportQuality', 'As on screen'); await sleep(50); $('exportStart').click();")
        lab.job_wait(120)
        log('D host without downloads', J(lab.js("$('exportSave').click(); await sleep(400); return { msg: $('exportMsg').textContent, saveShown: shown('exportSave') };")))
        log('problems', lab.problems())
    finally:
        lab.close()


# ---------- E: frames while a job runs
def gaps():
    lab = Lab()
    try:
        lab.idle()
        out = {}
        def measure(tag):
            lab.js(GAPS_ON); n = drag(lab, 6.0); g = lab.js(GAPS_OFF)
            t0 = time.time(); lab.idle(120); g['settle_s'] = round(time.time() - t0, 1); g['moves'] = n
            log('E', tag, J(g)); return g
        measure('no job, drag 1'); measure('no job, drag 2')
        lab.js("$('secExport').open = true; pick('exportSize', '7680'); pick('exportQuality', 'Extra fine'); pick('exportKind', 'PNG'); await sleep(50); $('exportStart').click(); await sleep(1500);")
        log('E job', J(lab.js("return [L.exportBusy(), $('exportStep').textContent];")))
        measure('8K Extra fine job, drag 1'); measure('8K Extra fine job, drag 2')
        lab.js(GAPS_ON); time.sleep(6); log('E job, live picture idle', J(lab.js(GAPS_OFF)))
        # the page's own controls while the job runs: does a click answer?
        r = lab.js("""const t = performance.now(); $('mode-j').click(); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); const ms = Math.round(performance.now() - t);
return { clickToNextFrames: ms, step: $('exportStep').textContent, mode: L.S.mode };""")
        log('E mode change during the job', J(r))
        t0 = time.time(); ok = lab.idle(240); log('E live Julia picture finished during the job after %.1f s' % (time.time() - t0), ok, J(lab.js("return [L.exportBusy(), $('exportStep').textContent];")))
        lab.shot('E-page-during-job.png')
        lab.js("$('mode-m').click();"); lab.idle(240)
        measure('8K Extra fine job, drag 3')
        log('E job before cancel', J(lab.js("const s = $('exportStep').textContent; $('exportCancel').click(); await sleep(1500); return [s, L.exportBusy(), $('exportMsg').textContent];")))
        measure('after the job, drag')
        log('problems', lab.problems())
    finally:
        lab.close()


# ---------- F: the graphics context is lost during a job; a model job at the same time
def lost():
    lab = Lab()
    try:
        lab.idle()
        lab.js("$('secExport').open = true; pick('exportSize', '3840'); pick('exportQuality', 'Fine'); await sleep(50); $('exportStart').click(); await sleep(1500);")
        r = lab.js("""const ext = L.R && $('view').getContext('webgl2').getExtension('WEBGL_lose_context'); const before = $('exportStep').textContent; ext.loseContext(); await sleep(1500);
const a = { before, busy: L.exportBusy(), msg: $('exportMsg').textContent, startShown: shown('exportStart') }; ext.restoreContext(); await sleep(2500);
return a;""")
        log('F context lost during a job', J(r))
        lab.idle(120)
        lab.stage_shot('F-stage.png')
        job(lab, 'F-after', 'As on screen', 'As on screen', 'PNG', stage='F-stage.png')
        # picture job and model job together
        r = lab.js("""$('exportDiscard').click(); $('secMesh').open = true; pick('exportSize', '1920'); pick('exportQuality', 'Fine'); await sleep(50);
$('exportStart').click(); $('meshStart').click(); await sleep(500); return { picture: L.exportBusy(), model: L.meshBusy() };""")
        log('F both jobs started', J(r))
        t0 = time.time()
        while time.time() - t0 < 300 and lab.js("return L.exportBusy() || L.meshBusy();"): time.sleep(0.5)
        log('F both ended after %.1f s' % (time.time() - t0), J(lab.js("return { picture: L.exportBusy(), model: L.meshBusy(), msg: $('exportMsg').textContent, save: shown('exportSave'), meshSave: shown('meshSave') };")))
        log('problems', lab.problems())
    finally:
        lab.close()


if __name__ == '__main__':
    {'indep': indep, 'states': states, 'refuse': refuse, 'gaps': gaps, 'lost': lost}[sys.argv[1]]()
