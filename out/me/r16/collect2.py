"""Pull the reports of a workflow run out of its journal.
python out/me/r16/collect2.py <run id> <out json> [full]"""
import json, sys

run, outp = sys.argv[1], sys.argv[2]
full = len(sys.argv) > 3
BASE = (r"C:\Users\IbrahimMahmoud\.claude\projects\C--Users-IbrahimMahmoud-AppData-Local-Claude-Data-claude-pzs8sxrjxfjjc"
        r"-scratch-workspaces-18144097-1788-4c0f-b3ad-8a91f920f07b-76933351-09da-4379-8bd1-1c64ac9b94d1-scratch-2026-11-17-a06af1"
        r"\e5663631-12dd-4d44-80a0-26a1ab33a9ae\subagents\workflows")
J = "\\\\?\\" + BASE + "\\" + run + "\\journal.jsonl"
out = []
for line in open(J, encoding='utf-8'):
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get('type') == 'result':
        out.append(d.get('result') if 'result' in d else d.get('value'))
json.dump(out, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'reports')
for r in out:
    if not isinstance(r, dict):
        print(str(r)[:2000]); continue
    print('=' * 110)
    for k, v in r.items():
        if isinstance(v, str):
            print('##', k); print(v)
        elif isinstance(v, list):
            print('##', k, len(v))
            for it in v:
                if isinstance(it, dict):
                    if full or k != 'verdicts':
                        print('  -', json.dumps(it, ensure_ascii=False))
                    else:
                        print('  -', it.get('name'), '|', it.get('verdict'))
                else:
                    print('  -', it)
