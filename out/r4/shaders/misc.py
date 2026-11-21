"""Assorted checks on the real pair: trap solids in colour, rough estimate on a trap solid, cut face, 2D mosaic."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab
page = sys.argv[1]; label = sys.argv[2]
d = '%s/%s' % (lab.HERE, label); os.makedirs(os.path.join(lab.ROOT, d), exist_ok=True)
S = lambda name, js: {'js': lab.PRE + js + " go(); return '%s';" % name, 'wait': 'done', 'timeout': 600, 'shot': '%s/%s.png' % (d, name), 'clip': '#view'}
sol = lambda extra: "Object.assign(L.S.colour, {mode: 0, solid: 1, thick: 0.05, skip: 1, tx: 0, ty: 0, tz: 0, %s});" % extra
steps = [
  S('mosaic2d', "$('mode-m').click(); $('m-mosaic').click(); $('flat').click();"),
  S('j-shell', "if (L.S.flat) $('flat').click(); if (L.S.mosaic) $('m-mosaic').click(); scene('basilicafar'); $('qBal').click(); " + sol("trap: 5, radius: 0.7")),
  S('j-cross', "scene('basilicafar'); $('qBal').click(); " + sol("trap: 1, radius: 0.7")),
  S('j-ring', "scene('basilicafar'); $('qBal').click(); " + sol("trap: 6, radius: 0.7")),
  S('j-line', "scene('basilicafar'); $('qBal').click(); " + sol("trap: 2, radius: 0.7")),
  S('j-point', "scene('basilicafar'); $('qBal').click(); " + sol("trap: 0, radius: 0.7")),
  S('m-shell', "scene('mandelfar'); $('qBal').click(); " + sol("trap: 5, radius: 0.7")),
  S('m-ring', "scene('mandelfar'); $('qBal').click(); " + sol("trap: 6, radius: 0.7")),
  S('m-cross', "scene('mandelfar'); $('qBal').click(); " + sol("trap: 1, radius: 0.7")),
  S('j-shell-union', "scene('basilicafar'); $('qBal').click(); " + sol("trap: 5, radius: 0.7") + " L.S.colour.solid = 2;"),
  S('j-ring-ultra', "scene('basilicafar'); $('qUltra').click(); " + sol("trap: 6, radius: 0.7")),
  S('j-shell-ultra', "scene('basilicafar'); $('qUltra').click(); " + sol("trap: 5, radius: 0.7")),
  S('j-ring-fine', "scene('basilicafar'); $('qFine').click(); L.S.q.aa = 8; " + sol("trap: 6, radius: 0.7")),
  S('j-shell-close-fine', "scene('basilica'); $('qFine').click(); L.S.q.aa = 8; " + sol("trap: 5, radius: 0.7")),
  S('q-bal-de1', "scene('basilicafar'); $('qBal').click(); L.S.q.de = 1; " + sol("trap: 5, radius: 0.7")),
  S('q-bal-de0', "scene('basilicafar'); $('qBal').click(); L.S.q.de = 0; " + sol("trap: 5, radius: 0.7")),
  S('q-ultra-de3', "scene('basilicafar'); $('qUltra').click(); L.S.q.de = 3; " + sol("trap: 5, radius: 0.7")),
  S('q-ultra-de3-d1', "scene('basilicafar'); $('qUltra').click(); L.S.q.de = 3; L.S.q.detail = 1; " + sol("trap: 5, radius: 0.7")),
  S('q-fast', "scene('basilicafar'); $('qFast').click(); " + sol("trap: 5, radius: 0.7")),
  S('q-fast-ring', "scene('basilicafar'); $('qFast').click(); " + sol("trap: 6, radius: 0.7")),
  S('cut-plain', "scene('basilicafar'); $('qBal').click(); L.S.colour.solid = 0; L.S.cutOn = true; L.S.cut = 0; L.S.colour.cutFace = false;"),
  S('cut-face', "scene('basilicafar'); $('qBal').click(); L.S.colour.solid = 0; L.S.cutOn = true; L.S.cut = 0; L.S.colour.cutFace = true; L.S.colour.inMode = 1;"),
  S('cut-solid', "scene('basilicafar'); $('qBal').click(); L.S.cutOn = true; L.S.cut = 0; L.S.colour.cutFace = false; " + sol("trap: 5, radius: 0.7")),
]
if len(sys.argv) > 3: steps = [s for s in steps if any(k in s['shot'] for k in sys.argv[3].split(','))]
code, log = lab.shot('dist/%s.html' % page, steps, label)
print('exit', code); print(chr(10).join(l for l in log.splitlines() if 'waited' in l or 'error' in l.lower() or 'PROBLEM' in l))
paths = [s['shot'] for s in steps]
print(lab.sheet(paths, [os.path.basename(p)[:-4] for p in paths], '%s/sheet-%s.png' % (lab.HERE, label), cols=4))
