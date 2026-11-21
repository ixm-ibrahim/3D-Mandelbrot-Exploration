"""Summarise audit-<tag>.json: every distinct finding once, with the states it shows in."""
import json, sys, collections
tag = sys.argv[1]
rep = json.load(open('audit-%s.json' % tag, encoding='utf-8'))
def show(key, fmt, limit=40):
    seen = collections.OrderedDict()
    for st, a in rep['states'].items():
        for it in a.get(key, []):
            k = fmt(it)
            seen.setdefault(k, []).append(st)
    print('== %s: %d distinct' % (key, len(seen)))
    for k, sts in list(seen.items())[:limit]:
        print('   %s   [%s]' % (k, ','.join(sts) if len(sts) < 6 else '%d states' % len(sts)))
J = lambda o: json.dumps(o, ensure_ascii=False)
print('TAG', tag, {k: (a['vw'], a['scrollW'], a['pageH'], a['coarse']) for k, a in list(rep['states'].items())[:2]})
show('offside', J); show('cut', lambda i: J({k: i[k] for k in ('el', 'by', 'box', 'clip', 'text')}))
show('squeezed', J); show('overlap', J)
show('textOverControl', J); show('textOverText', J)
show('noName', J); show('noVisibleLabel', J, 80)
show('lowContrast', lambda g: J({k: g[k] for k in ('el', 'ratio', 'need', 'size', 'fg', 'bg', 'op', 'solid', 'dis', 'text', 'n')}))
show('onPicture', lambda g: J({k: g[k] for k in ('el', 'ratio', 'size', 'fg', 'bg', 'text')}))
show('tinyText', J)
if '--small' in sys.argv: show('smallTargets', J, 120)
for st in ('m3d', 'm2d'):
    a = rep['states'].get(st)
    if a:
        print('== stage %s box %s covered %.1f%%' % (st, a['stage']['box'], a['stage']['covered']))
        for it in a['stage']['items']: print('   ', J(it))
        print('   clash', J(a['stage']['clash']))
print('problems', rep.get('problems'))
print('jobs', J(rep['states'].get('jobs-done', {}).get('set'))[:2500])
print('job-running set', J(rep['states'].get('job-running', {}).get('set'))[:900])
