"""Round 12, tried rules: shader against MATH for the three new entries. python out/r12/tried/run_glsl.py -> glsl.txt, glsl-table.txt"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R
steps = [{'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries';", 'wait': 'done', 'timeout': 300},
         {'js': open(os.path.join(HERE, 'glsl.js'), encoding='utf-8').read()}]
code, text = R.shot(R.PAGE, steps, 'glsl-steps')
R.write('glsl.txt', text)
m = re.search(r'step 2 result: (\{.*?\n\})', text, re.S)
if not m:
    print(text[-3000:]); sys.exit(code or 1)
d = json.loads(m.group(1))
out = ['renderer: %s' % d.get('renderer'), 'error = |glsl - js| / (1 + |js|), 1280 points per power', '']
for r in d['rows']:
    out.append('%s %s' % (r['id'], r['q']))
    for n, e in r['pw'].items():
        out.append('   %-4s median %.1e  99.9th %.1e  worst %.1e  over 2e-3: %d of %d' % (n, e['median'], e['p999'], e['worst'], e['over2e3'], e['points']))
    out.append('   sqr %.1e  cmap %.1e  mul against one plane %s  z = 0 in, z not 0 out: %d  finite: %s %s' % (r['sqr'], r['cmap'], ('%.1e' % r['mulAgainstOnePlane']) if 'mulAgainstOnePlane' in r else 'n/a', r['zleak'], r['finite'], r.get('notFinite', '')))
out += ['', 'shot.py exit code %d' % code, text.split('\n}')[-1].strip()]
R.write('glsl-table.txt', '\n'.join(out) + '\n')
print('\n'.join(out))
