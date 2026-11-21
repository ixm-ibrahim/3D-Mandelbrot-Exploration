import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
s=open(sys.argv[1],encoding='utf-8').read()
skip=set(sys.argv[2:])
pos=0
for m in re.finditer(r'step \d+ result: (.*)',s):
    d=json.loads(m.group(1)); pos=m.end()
    if not isinstance(d,dict): print(d); continue
    for k,v in d.items():
        if k in skip: continue
        print('==',k)
        if isinstance(v,list):
            for x in v: print('  ',x)
        elif isinstance(v,dict):
            print(json.dumps(v,ensure_ascii=False,indent=1))
        else: print('  ',v)
print(s[pos:])
