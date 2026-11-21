"""Pull the two engineers' reports of round 16 out of the workflow journal into notes/_r16_reports.json."""
import json, os, sys

J = (r"C:\Users\IbrahimMahmoud\.claude\projects\C--Users-IbrahimMahmoud-AppData-Local-Claude-Data-claude-pzs8sxrjxfjjc"
     r"-scratch-workspaces-18144097-1788-4c0f-b3ad-8a91f920f07b-76933351-09da-4379-8bd1-1c64ac9b94d1-scratch-2026-11-17-a06af1"
     r"\e5663631-12dd-4d44-80a0-26a1ab33a9ae\subagents\workflows\wf_c88d693d-f0e\journal.jsonl")
path = "\\\\?\\" + J
res = []
for line in open(path, encoding='utf-8'):
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get('type') == 'result':
        res.append(d)
out = []
for d in res:
    r = d.get('result') if 'result' in d else d.get('value')
    out.append(r)
json.dump(out, open('notes/_r16_reports.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'reports')
for r in out:
    if isinstance(r, dict):
        print('KEYS', list(r.keys()))
        for k, v in r.items():
            if isinstance(v, str):
                print('##', k); print(v)
            elif isinstance(v, list):
                print('##', k, len(v))
                for it in v:
                    print('  -', json.dumps(it, ensure_ascii=False) if not isinstance(it, str) else it)
        print('=' * 100)
    else:
        print(type(r), str(r)[:3000])
