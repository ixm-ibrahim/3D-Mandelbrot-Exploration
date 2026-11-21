# Section 4.1 of docs/ROUND29-LEARN.md: the numbers of the dots.
#   python out/r29/learn/mk/dotcheck.py 2d|3d|quick [out file]
# For every case chk.js (read its header) measures the dots of Move by move against the lab's own rule.
import io, json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand

what = sys.argv[1] if len(sys.argv) > 1 else 'quick'
dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'out', 'r29', 'learn', 'numbers-%s.txt' % what)
page = os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')
CS = {'basilica': [-1, 0, 0], 'rabbit': [-0.1226, 0.7449, 0], 'outside': [0.9, 0.8, 0]}
cases = []
if what in ('2d', 'quick'):
    for dots in (('some',) if what == 'quick' else ('few', 'some', 'many')):
        for n in (2, 3, 2.5, -2):
            for mods in (([0, 0, 0], [0, 0]), ([1, 0, 0], [1, 0])) + ((([0, 1, 0], [0, 0]),) if what == '2d' else ()):
                cases.append(dict(space=2, kind='m', c=[0, 0, 0], cname='-', dots=dots, n=n, abs=mods[0], flip=mods[1]))
                for cname in ('basilica', 'rabbit', 'outside'):
                    cases.append(dict(space=2, kind='j', c=CS[cname], cname=cname, dots=dots, n=n, abs=mods[0], flip=mods[1]))
if what in ('3d', 'quick'):
    cases.append('3d')

lines = []


def say(s):
    print(s, flush=True)
    lines.append(s)


worst = dict(joint0=0, jointEnd=0, oneStep=0, iterated=0, chain=0)
tot = dict(cases=0, steps=0, outTwin=0, outPic=0, picAsked=0, thrownBad=0, errors=0)
with Hand(page, '1400x950', 'dark') as h:
    h.page.js(io.open(os.path.join(HERE, 'chk.js'), encoding='utf-8').read() + '\nreturn 1;')
    ids = h.js("return L.APPROACHES.map(a => a.id);")
    if '3d' in cases:
        cases.remove('3d')
        c3 = [-0.3, 0.2, 0.1]
        for dots in (('some',) if what == 'quick' else ('few', 'some', 'many')):
            for ap in ids:
                for n in (2, 3):
                    cases.append(dict(space=3, kind='m', c=[0, 0, 0], cname='-', dots=dots, n=n, abs=[0, 0, 0], flip=[0, 0], ap=ap, gpu=(dots != 'many' or n == 2)))
                    cases.append(dict(space=3, kind='j', c=c3 if dots != 'few' else [-1, 0, 0], cname='c3' if dots != 'few' else 'basilica', dots=dots, n=n, abs=[0, 0, 0], flip=[0, 0], ap=ap, gpu=(dots != 'many' or n == 2)))
        # the modifiers in space, for a few approaches
        for ap in ('mercator', 'lathe', 'pulledplane'):
            cases.append(dict(space=3, kind='j', c=c3, cname='c3', dots='some', n=2, abs=[1, 0, 1], flip=[1, 0], ap=ap, gpu=True))
    say('%d cases on %s' % (len(cases), page))
    say('space kind c        dots  n    mods      approach     | dots stay steps | joint0  jointEnd oneStep  iterated chain    | out: twin pic | thrown')
    t0 = time.time()
    for cfg in cases:
        r = h.js("return window.__chk(%s);" % json.dumps(cfg))
        if r.get('error'):
            tot['errors'] += 1
            say('ERROR %s: %s' % (json.dumps(cfg), r['error']))
            continue
        tot['cases'] += 1; tot['steps'] += r['steps']; tot['outTwin'] += r['outTwin']; tot['thrownBad'] += r['thrownBad']
        if r['outPic'] >= 0:
            tot['outPic'] += r['outPic']; tot['picAsked'] += r['dots']
        for k in worst:
            v = r[k] if r[k] is not None else float('inf')
            worst[k] = max(worst[k], v)
        mods = ''.join(str(x) for x in cfg['abs']) + '/' + ''.join(str(x) for x in cfg['flip'])
        say('%dD    %s    %-8s %-5s %-4s %-9s %-12s | %4d %4d %5d | %.1e  %.1e  %.1e  %.1e  %.1e  | %4d %4s | %d  %s' % (
            cfg['space'], cfg['kind'], cfg['cname'], cfg['dots'], cfg['n'], mods, cfg.get('ap', ''), r['dots'], r['stay'], r['steps'],
            r['joint0'], r['jointEnd'], r['oneStep'], r['iterated'], r['chain'], r['outTwin'], r['outPic'] if r['outPic'] >= 0 else '-', r['thrownBad'],
            ('names ' + '/'.join(r['names'])) if cfg['space'] == 3 and cfg['kind'] == 'm' and cfg['dots'] != 'many' else (' pic differs at ' + json.dumps(r.get('picDots')) if r.get('outPic', 0) > 0 else '')))
    S0 = h.js("S.approach = 0; S.n = 2; S.abs = [0, 0, 0]; S.flip = [0, 0]; return 1;")
    say('')
    say('%d cases, %d dot-steps, %.0f s' % (tot['cases'], tot['steps'], time.time() - t0))
    say('largest differences: ' + ', '.join('%s %.2e' % (k, v) for k, v in worst.items()))
    say('thrown out at another step than the twin says: %d dots;  than the fine picture says: %d of %d dots asked;  steps with the wrong dots thrown out: %d;  errors: %d' % (
        tot['outTwin'], tot['outPic'], tot['picAsked'], tot['thrownBad'], tot['errors']))
    bad = h.problems()
    say('console: ' + (json.dumps(bad[:8]) if bad else 'no error or warning'))
io.open(dest, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
