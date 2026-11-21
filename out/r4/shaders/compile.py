"""Compile time only, several pages one after another (least of 3 each): orbit scene, then Kleinian."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab, timing_js
for page in sys.argv[1:]:
    steps = [{'js': lab.PRE + timing_js.T + "L.S.q.aa = 1; go(); return 'warm';", 'wait': 'done', 'timeout': 600},
             {'js': lab.PRE + timing_js.T + "return 'COMPILE orbit ' + compile();", 'timeout': 600},
             {'js': lab.PRE + timing_js.T + "$('mode-k').click(); L.S.q.aa = 1; go(); return 'k';", 'wait': 'done', 'timeout': 600},
             {'js': lab.PRE + timing_js.T + "return 'COMPILE klein ' + compile();", 'timeout': 600}]
    code, log = lab.shot('dist/%s.html' % page, steps, 'compile-' + page)
    print(page, ' | '.join(l.split('result:')[1].strip() for l in log.splitlines() if 'COMPILE' in l), '| exit', code)
