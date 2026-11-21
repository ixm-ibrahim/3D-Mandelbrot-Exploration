"""Round 27, entry: what trap solids of Balls on balls look like (pictures and probe counts).
python out/r27/entry/mk/traps.py -> shots/trap-*.png, logs/traps.log"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
H = run.HEAD
P = 'out/r27/entry/shots/trap-'
CASES = [('shell-r1-skip1-is', dict(trap=5, solid=1, radius=1, skip=1, thick=0.05)),
         ('shell-r05-skip1-is', dict(trap=5, solid=1, radius=0.5, skip=1, thick=0.05)),
         ('shell-r05-skip0-is', dict(trap=5, solid=1, radius=0.5, skip=0, thick=0.05)),
         ('shell-r1-skip1-added', dict(trap=5, solid=2, radius=1, skip=1, thick=0.05)),
         ('shell-r05-skip1-added', dict(trap=5, solid=2, radius=0.5, skip=1, thick=0.05)),
         ('ring-r05-skip1-is', dict(trap=6, solid=1, radius=0.5, skip=1, thick=0.05)),
         ('planes-r05-skip1-is', dict(trap=4, solid=1, radius=0.5, skip=1, thick=0.05)),
         ('cross-r05-skip1-is', dict(trap=1, solid=1, radius=0.5, skip=1, thick=0.05)),
         ('shell-r07-skip2-is', dict(trap=5, solid=1, radius=0.7, skip=2, thick=0.05))]
steps = [run.UP, dict(js=H + "$('ap-balls').click(); await sleep(100); await settle(); return 'balls';", wait='done', timeout=600)]
for name, c in CASES:
    steps.append(dict(js=H + "Object.assign(S.colour, %s); go(); await settle(); const g = grid(); return '%s: ' + g[0] + ' probes hit, ' + g[1] + ' on the outer ring; status ' + $('status').textContent;" % (str(c).replace("'", '"'), name),
                      wait='done', timeout=600, shot=P + name + '.png', clip='#stage'))
code, text, vals = run.shot(run.PAGE, steps, 'traps')
run.write('traps.log', text + 'exit %d\n' % code)
print(text[-3000:])
