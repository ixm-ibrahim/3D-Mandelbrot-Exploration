import json, sys, subprocess, os
# usage: python mk.py name   (reads name.js: steps separated by lines starting with '//# ' holding json opts)
name = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, name + '.js'), encoding='utf-8').read()
steps = []
cur = None
for line in src.split('\n'):
    if line.startswith('//# '):
        cur = json.loads(line[4:] or '{}'); cur['js'] = ''; steps.append(cur)
    elif cur is not None:
        cur['js'] += line + '\n'
for s in steps:
    if 'shot' in s: s['shot'] = 'out/verify/p12/' + s['shot']
    if not s['js'].strip(): del s['js']
json.dump(steps, open(os.path.join(here, name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
