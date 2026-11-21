# Copy tools/smoke-v12.json with only the screenshot paths redirected to out/r12/check-page/smoke/,
# so the checker's run does not overwrite the page engineer's pictures. Steps are otherwise untouched.
import json, os, sys
src = 'tools/smoke-v12.json'
dst = 'out/r12/check-page/smoke-v12-copy.json'
a = json.load(open(src, encoding='utf-8'))
n = 0
for s in a:
    if 'shot' in s:
        old = s['shot']
        s['shot'] = 'out/r12/check-page/smoke/' + os.path.basename(old)
        n += 1
os.makedirs('out/r12/check-page/smoke', exist_ok=True)
json.dump(a, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(a), 'steps,', n, 'shot paths redirected')
# dump the js of every step to a text file for reading
with open('out/r12/check-page/smoke-steps.txt', 'w', encoding='utf-8') as f:
    for i, s in enumerate(a):
        f.write('\n===== STEP %d =====\n' % (i + 1))
        for k in s:
            if k != 'js':
                f.write('%s: %s\n' % (k, s[k]))
        f.write(s.get('js', '') + '\n')
