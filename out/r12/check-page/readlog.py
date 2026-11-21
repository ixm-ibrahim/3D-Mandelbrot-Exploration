# Print the results of a shot.py log in a readable form:  python out/r12/check-page/readlog.py list-1400 [first step] [width]
import re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
name = sys.argv[1]
first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
width = int(sys.argv[3]) if len(sys.argv) > 3 else 600
for line in open('out/r12/check-page/%s.log' % name, encoding='utf-8'):
    m = re.match(r'step (\d+) result: (.*)', line)
    if not m:
        if re.search(r'TIMED|PROBLEM|exit code|Error|console|started|ended', line) or line.startswith('  '):
            print(line.rstrip()[:900])
        continue
    n = int(m.group(1))
    if n < first:
        continue
    try:
        v = json.loads(m.group(2))
    except Exception:
        v = m.group(2)
    print('--- step', n)
    if isinstance(v, dict):
        for k, x in v.items():
            if isinstance(x, list) and x and len(json.dumps(x, ensure_ascii=False)) > width:
                print('  ', k, ':')
                for y in x:
                    print('      ', str(y)[:width])
            else:
                print('  ', k, ':', (json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x)[:width])
    elif isinstance(v, list):
        for x in v:
            print('  ', str(x)[:width])
    else:
        print('  ', str(v)[:width])
