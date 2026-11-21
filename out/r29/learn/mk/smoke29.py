"""Round 29, track "learn": the old smoke list of 90 steps, put together exactly as out/r28/final/ui/mk/smoke28.py does
it (tools/smoke-v14.json 62 + round 20's 5 with round 22's one changed line + round 22's 9 + 10 + 3 + 1), with every log
and picture kept in out/r29/learn/smoke/ (nothing is written under out/r22, out/r27 or out/r28; run with python -B).

  python -B out/r29/learn/mk/smoke29.py <page> <tag>
      -> out/r29/learn/smoke/<tag>.log, <tag>-steps.json, <tag>-results.json; pictures in out/r29/learn/smoke/pics-<tag>/
  python -B out/r29/learn/mk/smoke29.py compare <tag a> <tag b>
      -> out/r29/learn/smoke/cmp-<a>-<b>.txt: the result lines word for word, the pictures pixel by pixel
"""
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
OUT = os.path.join(ROOT, 'out', 'r29', 'learn', 'smoke')
os.makedirs(OUT, exist_ok=True)
sys.dont_write_bytecode = True

if sys.argv[1] == 'compare':
    import numpy as np
    from PIL import Image
    ta, tb = sys.argv[2], sys.argv[3]
    A = json.load(open(os.path.join(OUT, ta + '-results.json'), encoding='utf-8'))
    B = json.load(open(os.path.join(OUT, tb + '-results.json'), encoding='utf-8'))
    out = ['steps with a result: %s %d, %s %d' % (ta, len(A), tb, len(B))]
    same = 0
    for k in sorted(set(A) | set(B), key=int):
        if A.get(k) == B.get(k):
            same += 1
        else:
            out.append('step %s differs:\n    %s: %s\n    %s: %s' % (k, ta, str(A.get(k))[:900], tb, str(B.get(k))[:900]))
    out.append('result lines that are the same word for word: %d of %d' % (same, len(set(A) | set(B))))
    pa, pb = os.path.join(OUT, 'pics-' + ta), os.path.join(OUT, 'pics-' + tb)
    names = sorted(set(os.listdir(pa)) | set(os.listdir(pb)))
    ident = 0
    for n in names:
        a, b = os.path.join(pa, n), os.path.join(pb, n)
        if not (os.path.exists(a) and os.path.exists(b)):
            out.append('   %s: only on one page' % n); continue
        X = np.asarray(Image.open(a).convert('RGB')).astype(int); Y = np.asarray(Image.open(b).convert('RGB')).astype(int)
        if X.shape != Y.shape:
            out.append('   %s: sizes differ %s %s' % (n, X.shape, Y.shape)); continue
        d = np.abs(X - Y).max(axis=2); nd = int((d > 0).sum())
        if nd == 0:
            ident += 1
        else:
            out.append('   %s: %d of %d pixels differ (largest difference %d of 255)' % (n, nd, d.size, int(d.max())))
    out.append('pictures saved by the list: %d; the same to the pixel on both pages: %d' % (len(names), ident))
    text = '\n'.join(out) + '\n'
    open(os.path.join(OUT, 'cmp-%s-%s.txt' % (ta, tb)), 'w', encoding='utf-8', newline='\n').write(text)
    print(text)
    sys.exit(0)

R22 = os.path.join(ROOT, 'out', 'r22', 'entry')
sys.path.insert(0, R22)
import smoke as S22          # round 22's list (it brings round 20's along)
import second                # round 22's second pass

page, tag = sys.argv[1], sys.argv[2]
base = json.load(open(os.path.join(ROOT, 'tools', 'smoke-v14.json'), encoding='utf-8'))
old = base + [dict(s) for s in S22.S20.NEW]
n_changed = 0
for s in old:
    if S22.OLD_LINE in s.get('js', ''):
        s['js'] = s['js'].replace(S22.OLD_LINE, S22.NEW_LINE); n_changed += 1
assert n_changed == 1, n_changed
steps = old + S22.steps_for('alongonce') + S22.steps_for('pulledplane') + second.STEPS + S22.LAST
steps = [dict(s) for s in steps]
pics = 'pics-' + tag
os.makedirs(os.path.join(OUT, pics), exist_ok=True)
for s in steps:
    if 'shot' in s:
        s['shot'] = 'out/r29/learn/smoke/' + pics + '/' + os.path.basename(s['shot'])
sj = os.path.join(OUT, tag + '-steps.json')
json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
t0 = time.time()
p = subprocess.run([sys.executable, '-B', os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj, '--size', '1400x950'],
                   capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1'), cwd=ROOT)
text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
lines, results = [], {}
for line in text.splitlines():
    m = re.match(r'step (\d+) result: (.*)$', line)
    if m:
        try:
            v = json.loads(m.group(2)); results[m.group(1)] = v
            if isinstance(v, str):
                line = 'step %s result: ' % m.group(1) + (v if len(v) < 1500 else v[:300] + ' ... (%d characters)' % len(v))
        except ValueError:
            pass
    lines.append(line)
json.dump(results, open(os.path.join(OUT, tag + '-results.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
got = set(int(k) for k in results)
with_js = [i + 1 for i, s in enumerate(steps) if 'js' in s]
tail = 'page %s\nsteps: %d (with js: %d); result lines: %d; steps with js and no result line: %s; exit %d; %s; took %.0f s\n' % (
    page, len(steps), len(with_js), len(got), [i for i in with_js if i not in got] or 'none', p.returncode,
    'no console errors' if 'no console errors' in text else 'CONSOLE ERRORS OR A FAILURE: see the lines above', time.time() - t0)
with open(os.path.join(OUT, tag + '.log'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n' + tail)
print('\n'.join(lines[-6:])); print(tail)
sys.exit(p.returncode)
