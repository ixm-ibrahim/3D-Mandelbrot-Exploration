import json, re, sys, io
src = io.open('out/verify/text/dump.txt', encoding='utf-8').read().splitlines()
for line in src:
    m = re.match(r'step (\d+) result: (.*)$', line)
    if not m: continue
    v = json.loads(m.group(2))
    if isinstance(v, str):
        try: v = json.loads(v)
        except Exception: pass
    n = m.group(1)
    with io.open('out/verify/text/step%s.txt' % n, 'w', encoding='utf-8') as f:
        if isinstance(v, dict):
            for k, x in v.items(): f.write('== %s ==\n%s\n' % (k, x))
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, dict):
                    for k, y in x.items(): f.write('%s: %s\n' % (k, y))
                    f.write('-----\n')
                else: f.write(str(x) + '\n')
        else: f.write(str(v))
