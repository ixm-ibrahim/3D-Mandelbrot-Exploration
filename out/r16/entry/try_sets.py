import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run, sets
from sets import P, BAS, cam
from run import view3
def tries():
    out = []
    for nm, extra in (('de0', 'S.q.de = 0; '), ('de1', 'S.q.de = 1; '), ('steps', 'S.q.de = 3; S.q.steps = 2000; S.q.stepk = 0.5; '), ('it40', 'S.q.de = 3; S.q.steps = 260; S.q.stepk = 0.8; S.iter = 40; '), ('it40de0', 'S.q.de = 0; S.iter = 40; ')):
        out.append(('try-ta-%s' % nm, P('turnaway') + extra + view3('j', BAS)))
    out.append(('try-reset', P('turnaway') + 'S.q.de = 3; S.q.steps = 260; S.q.stepk = 0.8; S.iter = 14; ' + view3('j', BAS)))
    return out
sets.SETS['tries'] = tries
if __name__ == '__main__':
    sys.exit(run.run_set('tries', tries()))
