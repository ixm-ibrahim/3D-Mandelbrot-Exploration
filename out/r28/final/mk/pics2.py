"""Round 28, Track A, the final checker: the three pictures for the user, after looking at the candidates of pics.py.
Real screenshots of dist/r28-final.html, 1400x950, light theme, the whole window, nothing drawn on them.
The page is opened fresh; the Approach list is opened and the row Balls on balls is clicked; the size is TYPED into
its dial and Frame it is pressed (real mouse and keys, the dial checker's hand.py). Done by script, and only this:
the panel is scrolled back to the top of its Kleinian section, so that the dials and the sentence show beside the
picture; and for the third picture the camera is turned to look along the chain (yaw 0.5, pitch 0.28, a little nearer).

  python -B out/r28/final/mk/pics2.py      -> out/r28/final/user-1-150.png, user-2-300.png, user-3-along.png, logs/pics2.txt
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'ui', 'mk'))
from hand import Hand, ROOT

PAGE = 'dist/r28-final.html'
OUT = 'out/r28/final'
lines = []
INFO = ("return JSON.stringify({ size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, t: S.k.bt, rho: S.k.brho, grid: S.k.bgrid, flat: !!S.flat,"
        " cam: [+L.cam.yaw.toFixed(4), +L.cam.pitch.toFixed(3), +L.cam.dist.toFixed(3)], status: $('status').textContent, sentence: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', program: String(L.R.sig || '').split('\\n')[0],"
        " theme: getComputedStyle(document.body).backgroundColor, scrollY: Math.round(scrollY), sizeBoxInWindow: (() => { const b = $('ballsSizeNum').getBoundingClientRect(); return b.top > 0 && b.bottom < innerHeight; })(),"
        " sentenceInWindow: (() => { const w = $('ballsWarn'); if (!vis(w)) return null; const b = w.getBoundingClientRect(); return b.top > 0 && b.bottom < innerHeight; })() });")
PANEL = ("const el = $('kleinPanel'); let sc = el.parentElement; while (sc && !(sc.scrollHeight > sc.clientHeight + 4 && /(auto|scroll)/.test(getComputedStyle(sc).overflowY))) sc = sc.parentElement;"
         " if (sc) sc.scrollTop += el.getBoundingClientRect().top - sc.getBoundingClientRect().top - 6; window.scrollTo(0, 0); if (document.activeElement) document.activeElement.blur(); await sleep(200); return sc ? sc.className || sc.tagName : 'no scrolling panel';")


def say(t):
    lines.append(t); print(t, flush=True)
    open(os.path.join(FINAL, 'logs', 'pics2.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def snap(h, name):
    sc = h.js(PANEL)
    h.mouse('mouseMoved', 430, 880); time.sleep(0.3); h.done(); time.sleep(0.5)
    h.window_shot('%s/%s.png' % (OUT, name))
    say('%s (panel scrolled: %s): %s' % (name, sc, h.js(INFO)))


if __name__ == '__main__':
    with Hand(PAGE, '1400x950', 'light') as h:
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        h.type('#ballsSizeNum', '150'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'user-1-150')
        h.type('#ballsSizeNum', '300'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'user-2-300')
        h.type('#ballsSizeNum', '150'); h.done(); h.click('#ballsFrame'); h.done()
        h.js("L.cam.yaw = 0.5; L.cam.pitch = 0.28; L.cam.dist = 6.3; L.touch(); if (L.viewChanged) L.viewChanged(); return 1;"); h.done()
        snap(h, 'user-3-along')
        probs = h.problems()
        say('console: %s' % ('no console errors or warnings' if not probs else ' || '.join(p[:300] for p in probs[:8])))
