"""Round 12, tried rules: read back what the page shows for the three new entries (formula, note, scorecard). -> card.txt, panel-<id>.png"""
import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R
JS = io.open(os.path.join(HERE, 'card.js'), encoding='utf-8').read()
GO = ' L.syncControls(); L.refresh(false); L.touch();'
steps = [{'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up';", 'wait': 'done', 'timeout': 300}]
for name, ap, extra in [('softfold', 'softfold', ''), ('softfold pinch', 'softfold', 'S.param.softfold.mix = 2;' + GO),
                        ('axisbulb', 'axisbulb', ''), ('axisbulb multiplier 5', 'axisbulb', 'S.param.axisbulb.k = 5;' + GO),
                        ('pillow creased', 'pillow', ''), ('pillow smooth', 'pillow', 'S.param.pillow.layout = 1;' + GO)]:
    st = {'js': JS.replace('__AP__', ap).replace('__EXTRA__', extra).replace('__NAME__', name), 'wait': 'done', 'timeout': 300}
    if not extra:
        st['shot'] = 'out/r12/tried/panel-%s.png' % ap
    steps.append(st)
code, text = R.shot(R.PAGE, steps, 'card-steps')
R.write('card.txt', text)
print(text)
sys.exit(code)
