"""Round 28, dial checker (ui): three last things.

  python -B out/r28/final/ui/mk/last.py     -> out/r28/final/ui/logs/last.txt

1. The start picture, then a visit past 100 (size 150, 300), "Reset this section" and "Frame it": is the picture the
   same to the pixel as before the visit? (the canvas alone, controls over it hidden by script for the screenshot)
2. One drag that goes too far and comes back, without letting go: the second-sphere slider at size 150 dragged from
   33 up to about 85 and back down to about 40; the size slider at 80 dragged up to about 130 and back to about 80.
3. The same start picture on the frozen page, taken the same way, against the new page's.
Real mouse and keys (hand.py).
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hand import Hand, ROOT, UI
import numpy as np
from PIL import Image

LOG = os.path.join(UI, 'logs', 'last.txt'); SHOTS = 'out/r28/final/ui/shots'
lines = []


def say(t):
    lines.append(t); print(t)
    open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def view(h, name):
    h.done()
    h.js("for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden'; await sleep(200); return 1;")
    p = '%s/last-%s.png' % (SHOTS, name); h.shot(p, '#view')
    h.js("for (const e of $('stage').children) e.style.visibility = ''; return 1;")
    return np.asarray(Image.open(os.path.join(ROOT, p)).convert('RGB')).astype(int)


def diff(a, b):
    return 'sizes differ' if a.shape != b.shape else '%d of %d pixels differ' % (int((np.abs(a - b).max(axis=2) > 0).sum()), a.shape[0] * a.shape[1])


def main():
    say('started %s' % time.strftime('%H:%M:%S'))
    with Hand('dist/r28-final.html', '1400x950', 'dark', warm=False) as h:
        h.js("S.q.aa = 4; L.touch(); return 1;")                                  # (by script: four passes a picture, so that two pictures of one state are the same to the pixel)
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        A = view(h, 'new-start')
        A2 = view(h, 'new-start-again')
        say('1. the start picture taken twice: %s' % diff(A, A2))
        h.type('#ballsSizeNum', '150'); h.done(); h.click('#ballsFrame'); h.done()
        h.type('#ballsSizeNum', '300'); h.done(); h.click('#ballsFrame'); h.done()
        h.click('#ballsReset button'); h.done(); h.click('#ballsFrame'); h.done()
        s = h.js("return [$('ballsSizeNum').value, $('ballsRhoNum').value, S.k.bt, S.k.brho, String(L.R.sig).split('\\n')[0], S.view.bound, L.cam.dist];")
        B = view(h, 'new-after-visit')
        say('   after size 150, Frame it, size 300, Frame it, Reset this section, Frame it (size %s, second sphere %s, t %r, rho %r, program %s, Drawing radius %s, camera distance %.4f): against the start picture %s' % (s[0], s[1], s[2], s[3], s[4], s[5], s[6], diff(A, B)))
        say('2. one drag too far and back')
        rd = lambda hh: hh.js("return [$('ballsSizeNum').value, $('ballsRhoNum').value, +$('ballsRho').value, +$('ballsSize').value];")
        h.type('#ballsSizeNum', '150'); h.done()
        x0, y, bx = h.thumb('#ballsRho'); x_hi = h.thumb('#ballsRho', 85)[0]; x_lo = h.thumb('#ballsRho', 40)[0]
        h.mouse('mouseMoved', x0, y); h.mouse('mousePressed', x0, y, 1); time.sleep(0.06); seen = []
        for k in range(1, 9):
            h.mouse('mouseMoved', x0 + (x_hi - x0) * k / 8, y, 1); time.sleep(0.07); seen.append(rd(h))
        for k in range(1, 9):
            h.mouse('mouseMoved', x_hi + (x_lo - x_hi) * k / 8, y, 1); time.sleep(0.07); seen.append(rd(h))
        h.mouse('mouseReleased', x_lo, y, 0); time.sleep(0.2); h.done(); e = rd(h)
        say('   size 150, second sphere 33.33; its slider dragged up to about 85 and back to about 40 in one go. size / second sphere (thumb) after each move: %s' % ' '.join('%s/%s(%g)' % (a, b, c) for a, b, c, _ in seen))
        say('   let go: size %s, second sphere %s. The size was 150 before the drag.' % (e[0], e[1]))
        h.click('#ballsReset button'); h.done(); h.type('#ballsSizeNum', '80'); h.done()
        x0, y, bx = h.thumb('#ballsSize'); x_hi = h.thumb('#ballsSize', 130)[0]
        h.mouse('mouseMoved', x0, y); h.mouse('mousePressed', x0, y, 1); time.sleep(0.06); seen = []
        for k in range(1, 7):
            h.mouse('mouseMoved', x0 + (x_hi - x0) * k / 6, y, 1); time.sleep(0.07); seen.append(rd(h))
        for k in range(1, 7):
            h.mouse('mouseMoved', x_hi + (x0 - x_hi) * k / 6, y, 1); time.sleep(0.07); seen.append(rd(h))
        h.mouse('mouseReleased', x0, y, 0); time.sleep(0.2); h.done(); e = rd(h)
        say('   size 80, second sphere 100; the size slider dragged up to about 130 and back to where it was in one go: %s' % ' '.join('%s/%s' % (a, b) for a, b, _, _ in seen))
        say('   let go: size %s, second sphere %s; sentence "%s"' % (e[0], e[1], h.js("return vis($('ballsWarn')) ? $('ballsWarn').textContent : '';")))
        probs = h.problems(); say('   console: %s' % ('no console errors or warnings' if not probs else ' || '.join(p[:300] for p in probs[:6])))
    with Hand('dist/r28-base-final.html', '1400x950', 'dark', warm=False) as h:
        h.js("S.q.aa = 4; L.touch(); return 1;")
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        C = view(h, 'frozen-start')
        say('3. the start picture of the frozen page against the new page\'s: %s; against the new page\'s after the visit past 100: %s' % (diff(A, C), diff(B, C)))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        say('THE SCRIPT STOPPED: ' + repr(e)); say(traceback.format_exc()); sys.exit(1)
