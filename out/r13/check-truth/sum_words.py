"""Summarise out/r13/check-truth/<name>.txt written by run.py for the words() checks."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1] if len(sys.argv) > 1 else 'words'
t = open(os.path.join(HERE, name + '.txt'), encoding='utf-8').read()
parts = re.split(r'--- step \d+\n', t)
out = []
for p in parts[2:]:
    p = p.split('\nno console')[0].split('\nexit')[0]
    try:
        d = json.loads(p)
    except Exception:
        out.append('unparsed ' + p[:900]); continue
    out.append('== %s space %s sentences %s problems %s sayNoB %s round2 %s roundLen %s unparsedKinds %s' % (d['id'], d['space'], d['sentences'], d['problems'], d['sayNoB'], d['round2'], d['roundLen'], d['unparsedKinds']))
    for k, v in sorted(d['byKind'].items(), key=lambda x: -x[1])[:16]:
        out.append('    %d %s' % (v, k))
    for e in d['examples'][:10]:
        out.append('      ex ' + json.dumps(e, ensure_ascii=False)[:700])
    for k, v in d['unparsed'][:10]:
        out.append('      un %d %s' % (v, k))
open(os.path.join(HERE, name + '.sum.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('written', len(out), 'lines')
