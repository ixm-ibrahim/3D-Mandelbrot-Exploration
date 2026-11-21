"""Round 13, truth checker: run a JS file in dist/r13-check-truth.html, then a list of calls, and print what they return.
  python out/r13/check-truth/run.py <file.js> <log name> [--size WxH] call1 call2 ...
Each call is a JavaScript expression; its JSON value is printed and written to the log.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def main():
    args = sys.argv[1:]
    size = None
    if '--size' in args:
        i = args.index('--size'); size = args[i + 1]; del args[i:i + 2]
    jsfile, logname, calls = args[0], args[1], args[2:]
    with open(os.path.join(HERE, jsfile), encoding='utf-8') as f:
        acts = [{'js': f.read() + '\nreturn "loaded";'}]
    for c in calls:
        acts.append({'js': 'return JSON.stringify(%s);' % c})
    path = os.path.join(HERE, 'actions-%s.json' % logname)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(acts, f)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', os.path.join(ROOT, 'dist', 'r13-check-truth.html'), '--actions', path]
    if size:
        cmd += ['--size', size]
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
    with open(os.path.join(HERE, logname + '.raw.log'), 'w', encoding='utf-8') as f:
        f.write(p.stdout + '\n---- stderr\n' + p.stderr + '\nexit %d\n' % p.returncode)
    out = []
    for line in p.stdout.splitlines():
        m = re.match(r'step (\d+) result: (.*)$', line)
        if not m:
            if not line.startswith('step'):
                out.append(line)
            continue
        try:
            val = json.loads(m.group(2))
            if isinstance(val, str) and val[:1] in '[{':
                val = json.loads(val)
        except Exception:
            val = m.group(2)
        out.append('--- step %s' % m.group(1))
        out.append(val if isinstance(val, str) else json.dumps(val, ensure_ascii=False, indent=1))
    text = '\n'.join(out) + '\nexit %d\n' % p.returncode
    if p.stderr.strip():
        text += 'stderr: ' + p.stderr[-3000:]
    with open(os.path.join(HERE, logname + '.txt'), 'w', encoding='utf-8') as f:
        f.write(text)
    print(text[-int(os.environ.get('TAIL', '14000')):])


main()
