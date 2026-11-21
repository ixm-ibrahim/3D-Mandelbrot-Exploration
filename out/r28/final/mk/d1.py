"""Round 28, Track A, the final checker: defect D1 (Frame it in low, wide pictures) once more.

  python -B out/r28/final/mk/d1.py      -> out/r28/final/ui/logs/sizes2.txt, pictures out/r28/final/ui/shots/sizes2-*.png

REUSED: the dial checker's sizes2.py (real click on the row, real keys into the size dial, real click on Frame it;
the edge pixels of the saved picture are read). MINE: the windows and sizes. The three windows the checker found cut
(844x390, 915x412, 900x420), two lower ones it did not try (740x360, 1000x380), the two windows the brief names
(1400x950 and 390x800) and a tall one; sizes 150, 300, 400, 1000 and 2000 in each.
"""
import os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'ui', 'mk'))
import sizes2 as Z

if __name__ == '__main__':
    Z.say('started %s (the final checker\'s windows)' % time.strftime('%H:%M:%S'))
    for size in ('844x390', '915x412', '900x420', '740x360', '1000x380', '1400x950', '390x800', '820x1180'):
        try:
            Z.run('dist/r28-final.html', 'new', size, ('150', '300', '400', '1000', '2000'))
        except Exception as e:
            Z.say('window %s STOPPED: %r' % (size, e)); Z.wrong.append('window %s stopped' % size)
    Z.say('=== %d picture(s) cut off%s' % (len(Z.wrong), ': ' + ' | '.join(Z.wrong) if Z.wrong else ''))
