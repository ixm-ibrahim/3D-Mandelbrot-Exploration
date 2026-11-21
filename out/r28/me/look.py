"""Round 28, the orchestrator's own look at the merged page dist/preview.html before Version 21 is published.
Real mouse and keys (the dial checker's Hand). Light theme first, as the user sees it.

  python -B out/r28/me/look.py      -> out/r28/me/v21-*.png, out/r28/me/look.txt
"""
import os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand

PAGE = 'dist/preview.html'
OUT = 'out/r28/me'
lines = []
INFO = ("return JSON.stringify({ size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, t: +S.k.bt.toFixed(6), rho: +S.k.brho.toFixed(6), flat: !!S.flat,"
        " status: $('status').textContent, sentence: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', program: String(L.R.sig || '').split('\\n')[0] });")


def say(t):
    lines.append(t); print(t, flush=True)
    open(os.path.join(HERE, 'look.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def snap(h, name):
    h.done(); time.sleep(0.6); h.done()
    h.window_shot('%s/%s.png' % (OUT, name))
    say('%s: %s' % (name, h.js(INFO)))


if __name__ == '__main__':
    with Hand(PAGE, '1400x950', 'light') as h:
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        snap(h, 'v21-1-as-the-row-gives-it')
        h.type('#ballsSizeNum', '150'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'v21-2-size-150')
        h.drag('#ballsSize', 300); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'v21-3-dragged-to-300')
        h.type('#ballsSizeNum', '1000'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'v21-4-typed-1000')
        h.type('#ballsSizeNum', '80'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'v21-5-back-to-80')
        h.click('#ballsReset'); h.done()
        snap(h, 'v21-6-after-reset')
        h.type('#ballsDepthNum', '2'); h.done()
        snap(h, 'v21-7-depth-2')
        h.click('#ballsReset'); h.done()
        h.type('#ballsRhoNum', '25'); h.done(); h.type('#ballsSizeNum', '400'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'v21-8-second-25-size-400-touching')
        probs = h.problems()
        say('wide light, console: %s' % ('no console errors or warnings' if not probs else ' || '.join(p[:300] for p in probs[:8])))
    with Hand(PAGE, '390x800', 'light') as h:
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        h.type('#ballsSizeNum', '150'); h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'v21-9-phone-size-150')
        probs = h.problems()
        say('phone light, console: %s' % ('no console errors or warnings' if not probs else ' || '.join(p[:300] for p in probs[:8])))
    with Hand(PAGE, '1400x950', 'dark') as h:
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        h.type('#ballsSizeNum', '150'); h.done()
        h.js("$('flat').click(); return 1;") if h.js("return !!$('flat');") else None
        h.done(); h.click('#ballsFrame'); h.done()
        snap(h, 'v21-10-dark-size-150-flat')
        probs = h.problems()
        say('wide dark, console: %s' % ('no console errors or warnings' if not probs else ' || '.join(p[:300] for p in probs[:8])))
