"""Print checks.txt compactly: python out/r14/rules/show.py [section]"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(HERE, 'checks.txt'), encoding='utf-8').read()
m = re.search(r'step 2 result: (\{.*\n\})', t, re.S)
d = json.loads(m.group(1))
def fmt(x):
    if isinstance(x, float): return '%.3g' % x
    if isinstance(x, dict): return '{' + ', '.join('%s: %s' % (k, fmt(v)) for k, v in x.items()) + '}'
    if isinstance(x, list): return '[' + ', '.join(fmt(v) for v in x) + ']'
    return str(x)
for k, v in d.items():
    if len(sys.argv) > 1 and k not in sys.argv[1:]: continue
    print('== ' + k)
    if isinstance(v, list):
        for r in v: print('  ' + fmt(r))
    elif isinstance(v, dict):
        for kk, vv in v.items():
            if isinstance(vv, list) and vv and isinstance(vv[0], dict):
                print('  ' + kk + ':')
                for r in vv: print('     ' + fmt(r))
            else: print('  %s: %s' % (kk, fmt(vv)))
    else: print('  ' + fmt(v))
print(t.split('\n}')[-1].strip())
