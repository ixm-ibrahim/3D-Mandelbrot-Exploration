"""The orchestrator's own check of "Reset this section" on dist/preview.html (my look.py pressed the box round the
button, not the button).   python -B out/r28/me/reset.py -> out/r28/me/reset.txt"""
import os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand
INFO = ("return JSON.stringify({ size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, t: +S.k.bt.toFixed(6), rho: +S.k.brho.toFixed(6),"
        " sentence: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', program: String(L.R.sig || '').split('\\n')[0] });")
out = []
def say(t):
    out.append(t); print(t, flush=True); open(os.path.join(HERE, 'reset.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
with Hand('dist/preview.html', '1400x950', 'light') as h:
    h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
    h.type('#ballsSizeNum', '300'); h.done(); say('typed 300: ' + h.js(INFO))
    h.type('#ballsSizeNum', '80'); h.done(); say('typed 80: ' + h.js(INFO))
    h.type('#ballsDepthNum', '2'); h.done(); say('depth 2: ' + h.js(INFO))
    h.click('#ballsReset button'); h.done(); say('after Reset this section: ' + h.js(INFO))
    h.window_shot('out/r28/me/v21-6-after-reset.png')
    h.type('#ballsRhoNum', '70'); h.done(); say('second sphere typed 70: ' + h.js(INFO))
    h.type('#ballsRhoNum', '80'); h.done(); say('second sphere typed 80: ' + h.js(INFO))
    h.type('#ballsSizeNum', '5000'); h.done(); say('size typed 5000: ' + h.js(INFO))
    h.type('#ballsDepthNum', '5000'); h.done(); say('depth typed 5000: ' + h.js(INFO))
    h.click('#ballsReset button'); h.done(); say('after Reset this section: ' + h.js(INFO))
    p = h.problems(); say('console: ' + ('no console errors or warnings' if not p else ' || '.join(x[:300] for x in p[:8])))
