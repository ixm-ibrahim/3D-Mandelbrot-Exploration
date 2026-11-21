"""Round 13, steps: run out/r13/steps/test.js in dist/r13-steps.html and write the table of results.
  python out/r13/steps/run_tests.py [what ...]      what: ids of approaches, 'flat1', 'flat2', 'samples' (default: all)
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
IDS = ['mercator', 'fold', 'lathe', 'tilt', 'bulb', 'classic', 'split', 'softfold', 'axisbulb', 'pillow']


def main():
    what = sys.argv[1:] or IDS + ['flat1', 'flat2', 'extra', 'agree', 'samples']
    with open(os.path.join(HERE, 'test.js'), encoding='utf-8') as f:
        acts = [{'js': f.read()}]
    for w in what:
        if w == 'samples':
            acts.append({'js': "return '@@S' + window.__LT.samples()"})
        elif w == 'agree':
            acts.append({'js': "return '@@A' + window.__LT.agree()"})
        elif w == 'extra':
            acts.append({'js': "return '@@R' + JSON.stringify(window.__LT.extra())"})
        elif w.startswith('flat'):
            acts.append({'js': "return '@@R' + JSON.stringify(window.__LT.flat(%s))" % w[4:]})
        else:
            acts.append({'js': "return '@@R' + JSON.stringify(window.__LT.space3('%s'))" % w})
    path = os.path.join(HERE, 'actions.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(acts, f)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', os.path.join(ROOT, 'dist', 'r13-steps.html'),
                        '--actions', path], cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
    with open(os.path.join(HERE, 'raw.log'), 'w', encoding='utf-8') as f:
        f.write(p.stdout + '\n---- stderr\n' + p.stderr)
    rows, lines = [], []
    for line in p.stdout.splitlines():
        m = re.match(r'step \d+ result: (.*)$', line)
        if not m:
            continue
        val = json.loads(m.group(1))
        if not isinstance(val, str):
            continue
        if val.startswith('@@S'):
            with open(os.path.join(HERE, 'samples.txt'), 'w', encoding='utf-8') as f:
                f.write(val[3:])
        elif val.startswith('@@A'):
            with open(os.path.join(HERE, 'agree.txt'), 'w', encoding='utf-8') as f:
                f.write(val[3:])
        elif val.startswith('@@R'):
            rows += json.loads(val[3:])
    head = '%-74s %-34s %5s %9s %5s %4s %9s %5s %7s %6s %5s' % ('configuration', 'moves', 'pts', 'worst rel', 'fail', 'at0', 'jump mv', 'fail', 'worst', 'say', 'fail')
    lines.append(head)
    tot = dict(cfg=0, pts=0, checkFail=0, at0Fail=0, jumpMoves=0, jumpFail=0, jumpOrigin=0, jumpRatio=0, jumpOther=0, geomN=0, geomFail=0, keyFail=0, sayN=0, sayFail=0)
    for r in rows:
        lines.append('%-74s %-34s %5d %9.1e %5d %4d %9d %5d %6.2f%% %6d %5d' % (r['label'][:74], r['moves'][:34], r['n'], r['relMax'], r['checkFail'], r['at0Fail'],
                     r['jumpMoves'], r['jumpFail'], 100 * r['jumpWorst'], r['sayN'], r['sayFail']) + ('  jump: origin %d, ratio %d, other %d | geom %d fail %d | key %d' % (r['jumpOrigin'], r['jumpRatio'], r['jumpOther'], r['geomN'], r['geomFail'], r['keyFail'])) + ('  offLine=%d' % r['offLine'] if r.get('offLine') else ''))
        for n in r['notes']:
            lines.append('      ! ' + n)
        tot['cfg'] += 1; tot['pts'] += r['n']
        for k in ('checkFail', 'at0Fail', 'jumpMoves', 'jumpFail', 'jumpOrigin', 'jumpRatio', 'jumpOther', 'geomN', 'geomFail', 'keyFail', 'sayN', 'sayFail'):
            tot[k] += r[k]
    lines.append('TOTAL ' + json.dumps(tot))
    name = 'results-' + '-'.join(what) + '.txt' if sys.argv[1:] else 'results.txt'
    with open(os.path.join(HERE, name), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(l for l in lines if l.startswith(('TOTAL', '      !'))) [:6000])
    print('exit', p.returncode, '| rows', len(rows), '| tail of output:', p.stdout[-600:] if not rows else '')
    if p.stderr.strip():
        print('stderr:', p.stderr[-1500:])


main()
