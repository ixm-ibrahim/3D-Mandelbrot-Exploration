import json, sys, io
t = io.open(sys.argv[1], encoding='utf-8', errors='replace').read()
d = None
for i in range(len(t)):
    if t[i] == '{':
        try:
            d = json.JSONDecoder().raw_decode(t[i:])[0]
            if isinstance(d, dict) and ('pageRep' in d or 'result' in d): break
        except Exception:
            continue
if 'pageRep' not in d and 'result' in d: d = d['result']
io.open('notes/_r12_reports.json', 'w', encoding='utf-8').write(json.dumps(d, indent=1, ensure_ascii=False))
for c in d['checks']:
    print('===== CHECK:', c['summary'][:1500])
    print('smoke:', c.get('smoke', '')[:400])
    print('passed:', len(c['passed']), ' defects:', len(c['defects']))
print()
for x in d['defects']:
    print('-', x['id'], '[' + x['severity'] + ']', x['where'][:80], '::', x['what'][:420])
f = d['fixRep']
print('\n===== FIXER:', f['summary'][:3000])
print('files:', [p.split('scratch-2026-11-17-a06af1/')[-1] for p in f['files_changed']])
print('done:')
for x in f['done']: print('  +', x['what'][:260])
print('not_done:')
for x in f['not_done']: print('  -', x['what'][:300], '|| why:', x['why'][:400])
print('needs:', json.dumps(f.get('needs_from_others'), ensure_ascii=False)[:1500])
print('risks:', json.dumps(f.get('risks'), ensure_ascii=False)[:2500])
