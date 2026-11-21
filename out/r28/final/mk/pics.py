"""Round 28, Track A, the final checker: the pictures for the user. Real screenshots of dist/r28-final.html,
1400x950, light theme, the whole window, nothing drawn on them. The page is opened fresh; the Approach list is opened
and the row Balls on balls is clicked; the size is TYPED into its dial and Frame it is pressed (real mouse and keys,
the dial checker's hand.py). For the views along the chain only the camera is then turned (by script).

  python -B out/r28/final/mk/pics.py      -> out/r28/final/cand/cand-*.png (candidates), logs/pics.txt
The three that are kept are copied to out/r28/final/user-*.png after looking at them (see NOTES.md).
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'ui', 'mk'))
from hand import Hand, ROOT

PAGE = 'dist/r28-final.html'
OUT = 'out/r28/final/cand'
lines = []
INFO = ("return JSON.stringify({ size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, t: S.k.bt, rho: S.k.brho, grid: S.k.bgrid, flat: !!S.flat,"
        " cam: [+L.cam.yaw.toFixed(4), +L.cam.pitch.toFixed(3), +L.cam.dist.toFixed(3)], status: $('status').textContent, sentence: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', program: String(L.R.sig || '').split('\\n')[0],"
        " theme: getComputedStyle(document.body).backgroundColor });")


def say(t):
    lines.append(t); print(t, flush=True)
    open(os.path.join(FINAL, 'logs', 'pics.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def snap(h, name):
    h.mouse('mouseMoved', 430, 880); time.sleep(0.3); h.done(); time.sleep(0.4)
    h.window_shot('%s/cand-%s.png' % (OUT, name))
    say('%s: %s' % (name, h.js(INFO)))


def cam(h, yaw, pitch, dist=None, target=None):
    h.js("L.cam.yaw = %s; L.cam.pitch = %s; %s %s L.touch(); if (L.viewChanged) L.viewChanged(); return 1;" % (
        yaw, pitch, '' if dist is None else 'L.cam.dist = %s;' % dist, '' if target is None else 'L.cam.target = %s;' % json.dumps(target)))
    h.done()


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    with Hand(PAGE, '1400x950', 'light') as h:
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        snap(h, '0-as-the-row-gives-it')
        h.type('#ballsSizeNum', '150'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, '1-150-start')
        for nm, yaw, pitch, dist in (('3a-150-along', 0.32, 0.24, None), ('3b-150-along-nearer', 0.32, 0.24, 4.6), ('3c-150-along-end-on', 0.12, 0.2, 4.8), ('3d-150-along-wider', 0.5, 0.28, None)):
            h.click('#ballsFrame'); h.done(); cam(h, yaw, pitch, dist); snap(h, nm)
        h.click('#ballsFrame'); h.done()
        h.type('#ballsSizeNum', '300'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, '2-300-start')
        for nm, yaw, pitch, dist in (('3e-300-along', 0.35, 0.25, None), ('3f-300-along-nearer', 0.35, 0.25, 7.0)):
            h.click('#ballsFrame'); h.done(); cam(h, yaw, pitch, dist); snap(h, nm)
        probs = h.problems()
        say('console: %s' % ('no console errors or warnings' if not probs else ' || '.join(p[:300] for p in probs[:8])))
