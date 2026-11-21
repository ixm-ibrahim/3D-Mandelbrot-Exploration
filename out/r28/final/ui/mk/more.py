"""Round 28, dial checker (ui): a few more things a user does, beyond the list of section 1.4 f.

  python -B out/r28/final/ui/mk/more.py [wide|phone]      -> out/r28/final/ui/logs/more-<layout>.txt

wide:  A. a saved picture started at 150, and the section reset while it is being drawn (the page promises: "what
          you change afterwards does not affect it"); the file is compared with the picture of 150 on the screen.
       B. the Learn tab and back, at 150.  C. the switch Extreme ranges, at 150.  D. Reset view at 400.
       E. the Kleinian panel folded and opened.  F. the second sphere's slider played with at a size past 100.
phone: G. the size slider and the second sphere's slider moved with a FINGER (touch events, not the mouse).
Real input (hand.py) unless a line says "(by script)".
"""
import base64, json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hand import Hand, ROOT, UI
import numpy as np
from PIL import Image

LAYOUT = sys.argv[1] if len(sys.argv) > 1 else 'wide'
SIZE = {'wide': '1400x950', 'phone': '390x800'}[LAYOUT]
PAGE = 'dist/r28-final.html'
LOG = os.path.join(UI, 'logs', 'more-%s.txt' % LAYOUT)
SHOTS = 'out/r28/final/ui/shots'
lines, wrong = [], []
STATE = """return { mode: S.mode, group: S.k.group, learn: document.body.classList.contains('is-learn'), size: $('ballsSizeNum').value, rho: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, sizeS: +$('ballsSize').value, rhoS: +$('ballsRho').value,
  bt: S.k.bt, brho: S.k.brho, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', status: $('status').textContent, prog: String(L.R.sig || '').split('\\n')[0], failed: String(L.R.failed || ''), extreme: !!S.extreme,
  dist: L.cam.dist, bound: S.view.bound, reach: L.ballsReach() };"""


def say(t):
    lines.append(t); print(t)
    open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def st(h):
    h.done(); return h.js(STATE)


def b(s):
    return 'mode %s%s, group %s, size %s, second sphere %s, depth %s, program %s%s' % (s['mode'], ' (Learn)' if s['learn'] else '', s['group'], s['size'], s['rho'], s['depth'], s['prog'], ' | sentence: ' + s['warn'] if s['warn'] else ' | no sentence')


def want(what, ok):
    say('   -> %s' % ('OK' if ok else 'WRONG: ' + what))
    if not ok:
        wrong.append(what)


def rim(h):
    return h.js("const w = $('stage').clientWidth, hh = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 29; i++) for (let j = 0; j < 21; j++) { const hit = !!L.pick(w * (i + 0.5) / 29, hh * (j + 0.5) / 21); if (hit) { n++; if (i === 0 || j === 0 || i === 28 || j === 20) ring++; } } return [n, ring];")


def main():
    say('page %s, window %s, started %s' % (PAGE, SIZE, time.strftime('%H:%M:%S')))
    with Hand(PAGE, SIZE, 'dark') as h:
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); st(h)
        typed = lambda d, v: (h.type('#balls%sNum' % d, v), st(h))[1]
        reset = lambda: (h.click('#ballsReset button'), st(h))[1]
        if LAYOUT == 'wide':
            say('--- A. a saved picture started at 150, the section reset while it is drawn')
            typed('Size', '150'); h.click('#ballsFrame'); s = st(h)
            h.js("window.__saved = null; window.squaringLabSaveHook = (name, blob) => { window.__saved = { name, blob }; }; $('secExport').open = true; return 1;")
            h.click('#exportStart'); time.sleep(0.25)
            busy0 = h.js("return L.exportBusy();")
            h.click('#ballsReset button'); time.sleep(0.3)
            mid = h.js(STATE); busy1 = h.js("return L.exportBusy();")
            say('Start the picture pressed at 150 (job running: %s); then Reset this section (job still running: %s): the page now shows %s' % (busy0, busy1, b(mid)))
            h.page.wait("!window.squaringLab.exportBusy()", 900); time.sleep(0.5)
            if h.js("return vis($('exportSave'));"):
                h.click('#exportSave'); time.sleep(1.0)
            b64 = h.js("""const sv = window.__saved; delete window.squaringLabSaveHook; if (!sv) return null; const buf = new Uint8Array(await sv.blob.arrayBuffer()); let s = ''; for (let i = 0; i < buf.length; i += 30000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 30000)); return btoa(s);""")
            if not b64:
                say('NO FILE reached the save hook'); want('the picture export gave no file', False)
            else:
                p_new = os.path.join(ROOT, SHOTS, 'more-export-150-reset-while-drawn.png')
                open(p_new, 'wb').write(base64.b64decode(b64))
                p_ref = os.path.join(ROOT, SHOTS, 'f1-wide-dark-export-150-file.png')
                A = np.asarray(Image.open(p_new).convert('RGB')).astype(int)
                fg = int((np.abs(A - A[0, 0]).max(axis=2) > 24).sum())
                msg = 'file %d x %d, %.1f %% of it not background' % (A.shape[1], A.shape[0], 100.0 * fg / (A.shape[0] * A.shape[1]))
                if os.path.exists(p_ref):
                    B = np.asarray(Image.open(p_ref).convert('RGB')).astype(int)
                    if A.shape == B.shape:
                        d = np.abs(A - B).max(axis=2)
                        msg += '; against the file saved at 150 with nothing changed (first run, same window, same view): %d of %d pixels differ, %d by more than 8 of 255' % (int((d > 0).sum()), d.size, int((d > 8).sum()))
                        ok = int((d > 8).sum()) < 0.002 * d.size
                    else:
                        msg += '; the other file has another size %s' % (B.shape,); ok = False
                else:
                    ok = 15 < 100.0 * fg / (A.shape[0] * A.shape[1]) < 30
                say(msg); want('the saved picture is not the picture of 150', ok)
            if h.js("return vis($('exportDiscard'));"):
                h.click('#exportDiscard')
            s = st(h); say('afterwards the page shows: ' + b(s)); want('the page is not back at the start values', s['size'] == '55.56' and s['rho'] == '100' and s['prog'] == 'k-balls')

            say('--- B. the Learn tab and back, at 150')
            typed('Size', '150'); h.click('#ballsFrame'); s0 = st(h)
            h.click('#mode-l'); h.done(); time.sleep(0.5); s1 = h.js(STATE)
            say('Learn pressed: ' + b(s1))
            h.shot('%s/more-learn-from-balls-150.png' % SHOTS)
            h.click('#mode-k'); s2 = st(h)
            say('Kleinian pressed: ' + b(s2)); want('after Learn the dials or the sentence are not as they were left', s2['size'] == '150' and s2['rho'] == '33.33' and 'It is now 33.33 % of the first' in s2['warn'] and s2['prog'] == 'k-balls2' and not s2['learn'])
            r = rim(h); say('   the picture: %d of 609 probes hit, %d on the rim' % tuple(r))

            say('--- C. the switch Extreme ranges, at 150')
            h.click('#extreme'); s = st(h)
            ends = h.js("return ['ballsSize', 'ballsRho', 'ballsDepth'].map(id => [$(id).min, $(id).max, $(id + 'Num').getAttribute('aria-valuemin'), $(id + 'Num').getAttribute('aria-valuemax')].join('/'));")
            say('Extreme ranges on (%s): %s; ends of the three dials (slider min/max, typed min/max): %s' % (s['extreme'], b(s), ends))
            want('Extreme ranges changed a dial of this group', s['size'] == '150' and s['rho'] == '33.33' and ends == ['2/400/1/2000', '2/100/2/100', '1/100/1/1000'])
            h.click('#extreme'); s = st(h)
            say('Extreme ranges off: ' + b(s)); want('switching Extreme ranges off moved a dial', s['size'] == '150' and s['rho'] == '33.33')

            say('--- D. Reset view at 400')
            reset(); typed('Size', '400'); h.click('#ballsFrame'); s = st(h); r0 = rim(h)
            for _ in range(6):
                h.click('#zoomIn')
            s1 = st(h); r1 = rim(h)
            h.click('#reset'); s2 = st(h); r2 = rim(h)
            say('size 400, Frame it: camera distance %.2f, %d probes hit, %d on the rim; six presses of + : distance %.2f, %d on the rim; Reset view: distance %.2f, %d probes hit, %d on the rim' % (s['dist'], r0[0], r0[1], s1['dist'], r1[1], s2['dist'], r2[0], r2[1]))
            want('Reset view at 400 does not bring the whole chain back', r2[1] == 0 and abs(s2['dist'] - s['dist']) < 0.01)
            reset(); typed('Size', '2000'); h.click('#ballsFrame'); s = st(h); r0 = rim(h)
            h.click('#reset'); s2 = st(h); r2 = rim(h)
            say('size 2000, Frame it: distance %.2f, %d on the rim; Reset view: distance %.2f, %d on the rim' % (s['dist'], r0[1], s2['dist'], r2[1]))
            want('Reset view at 2000 does not bring the whole chain back', r2[1] == 0)

            say('--- E. the panel folded and opened, the page\'s Collapse all')
            reset(); typed('Size', '150')
            h.click('#kleinPanel > summary'); time.sleep(0.3); a = h.js("return [$('kleinPanel').open, vis($('ballsDials'))];")
            h.click('#kleinPanel > summary'); time.sleep(0.3); s = st(h)
            say('panel folded (open %s, dials seen %s) and opened again: %s' % (a[0], a[1], b(s))); want('folding the panel changed something', s['size'] == '150' and s['rho'] == '33.33')

            say('--- F. the second sphere\'s slider at a size past 100')
            reset(); typed('Size', '150'); h.click('#ballsFrame'); st(h)
            seen = h.drag('#ballsRho', 60, moves=8, hold=True, read=lambda hh: hh.js("return [$('ballsRhoNum').value, +$('ballsRho').value, $('ballsSizeNum').value];"))
            say('size 150 (second sphere 33.33); its slider dragged up towards 60, button held; second sphere box / thumb / size box after each move: %s' % ' '.join('%s/%g/%s' % tuple(x) for x in seen))
            h.release(); s = st(h)
            say('let go: ' + b(s) + '; thumb at %s' % s['rhoS'])
            want('at 150 a second sphere dragged to 60 should end at 50 and leave the size alone (150 x 0.5 = 75)', s['rho'] == '50' and s['size'] == '150')
            seen = h.drag('#ballsRho', 90, moves=8, hold=True, read=lambda hh: hh.js("return [$('ballsRhoNum').value, +$('ballsRho').value, $('ballsSizeNum').value];"))
            say('dragged on towards 90, held: %s' % ' '.join('%s/%g/%s' % tuple(x) for x in seen))
            h.release(); s = st(h)
            say('let go: ' + b(s) + '; thumb at %s' % s['rhoS'])
            want('a second sphere dragged to 90 at size 150 should end at 100 with the size at 50', s['rho'] == '100' and s['size'] == '50')
            h.shot('%s/more-after-rho-drag-to-100.png' % SHOTS, '#stage')
            reset()
        else:
            say('--- G. the sliders moved with a finger (touch events)')
            h.page.call('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=1)

            def finger(sel, to, steps=8):
                x0, y, bx = h.thumb(sel)
                x1 = bx[0] + bx[2] + 40 if to == 'right' else bx[0] - 40 if to == 'left' else h.thumb(sel, to)[0]
                ok, what = h.on_top(sel, x0, y)
                if not ok:
                    bx = h.box(sel, 'end'); x0, y, _ = h.thumb(sel); x0 = min(max(x0, bx[0] + 8), bx[0] + bx[2] - 8); y = bx[1] + bx[3] / 2
                    x1 = bx[0] + bx[2] + 40 if to == 'right' else bx[0] - 40 if to == 'left' else x1
                h.page.call('Input.dispatchTouchEvent', type='touchStart', touchPoints=[{'x': x0, 'y': y}]); time.sleep(0.06)
                for k in range(1, steps + 1):
                    h.page.call('Input.dispatchTouchEvent', type='touchMove', touchPoints=[{'x': x0 + (x1 - x0) * k / steps, 'y': y}]); time.sleep(0.06)
                h.page.call('Input.dispatchTouchEvent', type='touchEnd', touchPoints=[]); time.sleep(0.2)
            reset()
            finger('#ballsSize', 200); s = st(h)
            say('size slider, finger from 55.56 towards 200: ' + b(s))
            want('the finger did not move the size past 100 with the second sphere following', float(s['size']) > 150 and abs(float(s['rho']) - 5000 / float(s['size'])) < 0.02)
            h.shot('%s/more-phone-finger-size-200.png' % SHOTS)
            finger('#ballsSize', 'right'); s = st(h)
            say('finger past the right end: ' + b(s)); want('finger to the right end: size 400, second sphere 12.5', s['size'] == '400' and s['rho'] == '12.5')
            finger('#ballsSize', 'left'); s = st(h)
            say('finger past the left end: ' + b(s)); want('finger to the left end: size 2', s['size'] == '2')
            reset()
            finger('#ballsRho', 64); s = st(h)
            say('second-sphere slider, finger from 100 towards 64: ' + b(s) + '; thumb at %s' % s['rhoS']); want('finger let go near 64: 50', s['rho'] == '50' and s['rhoS'] == 50)
            finger('#ballsRho', 'left'); s = st(h)
            say('finger past the left end: ' + b(s)); want('finger to the left end: 2', s['rho'] == '2')
            finger('#ballsRho', 'right'); s = st(h)
            say('finger past the right end: ' + b(s)); want('finger to the right end: 100', s['rho'] == '100')
            finger('#ballsDepth', 'left'); s = st(h)
            say('depth slider, finger past the left end: ' + b(s)); want('depth 1 with its sentence', s['depth'] == '1' and 'so few rounds' in s['warn'])
            finger('#ballsDepth', 'right'); s = st(h)
            say('depth slider, finger past the right end: ' + b(s)); want('depth 100', s['depth'] == '100')
            reset()
        probs = h.problems()
        say('--- console: %s' % ('no console errors or warnings' if not probs else '%d PROBLEM(S): ' % len(probs) + ' || '.join(p[:400] for p in probs[:12])))
        if probs:
            wrong.append('console problems')
        if getattr(h, 'not_clicked', None):
            say('clicks that could not be made (covered): %s' % h.not_clicked)
    say('=== %d thing(s) marked WRONG%s' % (len(wrong), ': ' + ' | '.join(wrong) if wrong else ''))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        say('THE SCRIPT STOPPED: ' + repr(e)); say(traceback.format_exc()); sys.exit(1)
