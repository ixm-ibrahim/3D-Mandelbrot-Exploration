"""A soft copy of the smoke test: a failing step reports 'FAILED: ...' and the run goes on."""
import io, json
steps = json.load(io.open('tools/smoke-v9m.json', encoding='utf-8'))
for s in steps:
    if 'js' in s:
        s['js'] = 'try {\n' + s['js'] + '\n} catch (e) { return "FAILED: " + (e && e.message || e); }'
    if 'shot' in s:
        s['shot'] = s['shot'].replace('out/', 'out/me/v12b/shots/', 1)
io.open('out/me/v12b/smoke-soft.json', 'w', encoding='utf-8').write(json.dumps(steps))
print(len(steps), 'steps')
