"""Print the output of tools/shot.py with each step result spread over lines."""
import json, sys

for line in sys.stdin:
    line = line.rstrip()
    if 'result:' in line:
        head, body = line.split('result:', 1)
        try:
            v = json.loads(body)
        except Exception:
            print(line[:400]); continue
        print(head + 'result:')
        if isinstance(v, dict):
            for k, x in v.items(): print('   %s: %s' % (k, json.dumps(x, ensure_ascii=False)))
        elif isinstance(v, list):
            for x in v: print('   ' + (x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)))
        else:
            print('   ' + str(v))
    elif len(line) > 300 and 'rows.push' in line:
        continue
    else:
        print(line[:400])
