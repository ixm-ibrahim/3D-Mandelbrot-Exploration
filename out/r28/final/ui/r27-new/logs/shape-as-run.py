# copy of out/r27/final/mk/shape.py as run by out/r28/final/ui/mk/old27.py: 0 fixed picture path(s) changed, nothing else
"""Round 27, final, merge rehearsal: round 26's Learn files and the overlay in one page (dist/r27-final-merge.html,
built by me from base18a + overlay + src/js/66-learn-view.js, 67-learn-shape.js, 68-learn-shape3d.js,
src/css/67-learn-shape.css as they stood when I built it; NOT the orchestrator's merge).
  R27_OUT=merge R27_PAGE=dist/r27-final-merge.html python out/r27/final/mk/shape.py   -> merge/logs/shape.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

if __name__ == '__main__':
    rd = lambda n: run.HEAD + open(os.path.join(HERE, n), encoding='utf-8').read()
    steps = [run.UP, dict(js=rd('shape.js'), shot=run.OUT + '/shots/shape-learn-whole-shape-3d.png'), dict(js=rd('shape2.js'), shot=run.OUT + '/shots/shape-after.png')]
    code, text, vals = run.shot(run.PAGE, steps, 'shape', '1400x950', 'dark')
    run.write('shape.log', text + 'exit %d\n' % code)
    lines = ['%s: exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'CONSOLE ERRORS OR A FAILURE: see shape.log')]
    for v in vals[1:]:
        try:
            d = json.loads(v)
        except ValueError:
            lines.append(str(v)[:400]); continue
        for k, w in d.items():
            lines.append('  %s: %s' % (k, json.dumps(w, ensure_ascii=False)))
    out = '\n'.join(lines) + '\n'
    run.write('shape.txt', out); print(out)
    if code != 0:
        print(text[-2500:])
