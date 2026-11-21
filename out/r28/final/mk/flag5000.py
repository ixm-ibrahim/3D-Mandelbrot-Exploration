"""The final checker: one line of the dial checker's f1.py came out WRONG in my run ("size: typed 5000: the box is
marked '', wanted 'clamped'"). The mark is a flash of 1.4 s (70-dial.js, not in the overlay); f1.py reads it after the
picture has finished, and at size 2000 before Frame it the picture took longer than that on the loaded machine.
Here the mark is read at once after the key, and again after the picture is done, with the time between. Real keys.
  python -B out/r28/final/mk/flag5000.py   -> out/r28/final/logs/flag5000.txt"""
import os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'ui', 'mk'))
from hand import Hand
out = []
FLAG = "const b = $('%sNum').closest('.dial-num'); return [b.dataset.flag || '', $('%sNum').value];"
with Hand('dist/r28-final.html', '1400x950', 'dark') as h:
    h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
    for dial, text in (('ballsSize', '5000'), ('ballsSize', '0'), ('ballsRho', '5000'), ('ballsDepth', '5000'), ('ballsSize', '2000')):
        for k in range(3):
            h.click('#ballsReset button'); h.done()
            h.type('#%sNum' % dial, text); t0 = time.time()
            a = h.js(FLAG % (dial, dial)); h.done(); dt = time.time() - t0; b = h.js(FLAG % (dial, dial))
            out.append('%s typed "%s", try %d: at once the box reads %s and is marked "%s"; after the picture was done, %.1f s later, it is marked "%s"' % (dial, text, k + 1, a[1], a[0], dt, b[0]))
            print(out[-1], flush=True)
    p = h.problems(); out.append('console: %s' % ('no console errors or warnings' if not p else ' || '.join(x[:200] for x in p)))
open(os.path.join(FINAL, 'logs', 'flag5000.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
