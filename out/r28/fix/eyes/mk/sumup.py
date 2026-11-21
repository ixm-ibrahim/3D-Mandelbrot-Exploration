"""The eyes: every count the notes quote, gathered from what the other scripts kept.
  python out/r28/fix/eyes/mk/sumup.py   -> logs/summary.txt"""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import views
E = os.path.dirname(HERE); L = os.path.join(E, 'logs')
out = []
SMALL = {'p2-start', 'p2-r2-start', 'p2-close', 'depth1', 'depth3', 'depth5', 'depth100', 'depth400', 'p150-depth1', 'p150-depth3', 'p150-depth5'}
NAMES = {'dw': 'dark, wide (1400x950)', 'lw': 'light, wide (1400x950)', 'dp': 'dark, phone (390x800)', 'lp': 'light, phone (390x800)'}


def what(tag, name):
    """the dials the page really held for this view"""
    f = os.path.join(E, 'rays', '%s-%s.json' % (tag, name))
    if not os.path.exists(f):
        return ''
    m = json.load(open(f, encoding='utf-8'))['meta']
    return 'size %.2f, second sphere %.2f %%, grid %d, depth %d' % (100 / (2 * m['k']['bt'] - 1), 100 * m['k']['brho'], m['k']['bgrid'], m['k']['bit'])


for tag in ('dw', 'lw', 'dp', 'lp'):
    rs = []
    for f in sorted(glob.glob(os.path.join(L, 'walk', tag + '-*.json')), key=os.path.getmtime):
        r = json.load(open(f, encoding='utf-8'))
        if not r.get('flat'):
            rs.append(r)
    if not rs:
        continue
    out.append('=== 3D views, %s: %d views' % (NAMES[tag], len(rs)))
    for group, test in (('with the size past 100', lambda r: r['p'] > 100.0001 and r['depth'] >= 5 and r['view'] not in SMALL),
                        ('small values and long searches (size 2; depth 5, 100, 400; size up to 100)', lambda r: (r['view'] in SMALL or r['p'] <= 100.0001) and r['depth'] >= 5),
                        ('depth 1 and 3 (the page says: broken shells)', lambda r: r['depth'] < 5)):
        g = [r for r in rs if test(r)]
        if not g:
            continue
        t = lambda k: sum(max(0, r.get(k, 0) or 0) for r in g)
        out.append('  %s: %d views, %d rays, %d stops | HOLES %d (through a ball: %d; the rest run through what only the depth calls solid) | SEEN THROUGH %d (through a ball: %d) | IN THE OPEN %d | '
                   'stops that stand only on what the depth calls solid: %d | picture painted as background where rays stop all round, as a patch: %d; painted where no ray stops all round, as a patch: %d'
                   % (group, len(g), t('rays'), t('stops'), t('HOLES'), t('HOLES_IN_A_BALL'), t('SEEN_THROUGH'), t('SEEN_THROUGH_A_BALL'), t('IN_THE_OPEN'), t('stopsOnDepthOnly'), t('PICTURE_HOLE_PATCHES'), t('PICTURE_GHOST_PATCHES')))
        for r in g:
            out.append('     %-26s (%s) stops %5d of %5d | holes %d (ball %d, longest %.1f px) | through %d (ball %d) | open %d | on depth-only solid %d | page\'s own measure: %d stops over 2 px, worst %.1f px | drawn in %d ms%s'
                       % (r['view'], what(tag, r['view']), r['stops'], r['rays'], r['HOLES'], r.get('HOLES_IN_A_BALL', -1), r['longestHolePx'], r['SEEN_THROUGH'], r.get('SEEN_THROUGH_A_BALL', -1), r['IN_THE_OPEN'], r.get('stopsOnDepthOnly', -1),
                          r['pageMetOver2px'], r['pageMetWorstPx'], r['drawMs'], '' if 'HOLES_IN_A_BALL' in r else '  (walked before the split by ball / depth was added)'))
for tag in ('dw', 'lw', 'dp', 'lp'):
    fs = sorted(glob.glob(os.path.join(L, 'flat2', tag + '-*.json')), key=os.path.getmtime)
    if not fs:
        continue
    out.append('=== 2D views, %s: %d views (GHOSTS = painted inside with nothing solid within about 1.5 px; holes = wholly solid with its 8 neighbours and not painted inside)' % (NAMES[tag], len(fs)))
    for f in fs:
        r = json.load(open(f, encoding='utf-8'))
        out.append('     %-26s size %.2f, second sphere %.2f %%, grid %d, depth %d | twin against my recipe: %d of %d pixel centres differ | GHOSTS %d (twin says outside at %d; nearest solid point %.1f px in the middle, %.1f px at most) | holes %d'
                   % (r['view'], r['p'], 100 * r['rho'], r['grid'], r['depth'], r['twinAgainstMine'], r['pixels'], r['GHOSTS'], r['ghostsTwinSaysOutside'], r['ghostRealDistMedianPx'], r['ghostRealDistMaxPx'], r['HOLES']))
    rs = [json.load(open(f, encoding='utf-8')) for f in fs]
    half = [r for r in rs if abs(r['rho'] - 0.5) < 1e-9]; other = [r for r in rs if abs(r['rho'] - 0.5) >= 1e-9]
    out.append('  second sphere exactly 50: %d views, GHOSTS %d, holes %d | any other second sphere: %d views, GHOSTS %d, holes %d | twin against my recipe, all views: %d of %d pixel centres differ'
               % (len(half), sum(r['GHOSTS'] for r in half), sum(r['HOLES'] for r in half), len(other), sum(r['GHOSTS'] for r in other), sum(r['HOLES'] for r in other), sum(r['twinAgainstMine'] for r in rs), sum(r['pixels'] for r in rs)))
out.append('=== a wider net (mk/fuzz.py)')
for f in sorted(glob.glob(os.path.join(L, 'fuzz-[0-9]*.txt'))):
    out.append('  ' + open(f, encoding='utf-8').read().strip().splitlines()[-1])
if os.path.exists(os.path.join(L, 'fuzz-summary.txt')):
    out.append('  ' + open(os.path.join(L, 'fuzz-summary.txt'), encoding='utf-8').read().strip())
out.append('=== old pictures (mk/same.py)')
for f in sorted(glob.glob(os.path.join(L, 'same-[0-9]*x*.txt'))):
    for ln in open(f, encoding='utf-8'):
        if ln.startswith('TOTAL') or 'page dist' in ln:
            out.append('  %s: %s' % (os.path.basename(f), ln.strip()))
for nm in ('same-twice.txt', 'same-phone-shift.txt', 'learn.txt', 'skin.txt'):
    f = os.path.join(L, nm)
    if os.path.exists(f):
        out.append('=== ' + nm)
        out += ['  ' + ln.rstrip()[:420] for ln in open(f, encoding='utf-8') if ln.strip()][-14:]
out.append('=== speed (mk/speed.py)')
for nm in ('speed-first-1400x950.txt', 'speed-past-1400x950.txt'):
    f = os.path.join(L, nm)
    if os.path.exists(f):
        for ln in open(f, encoding='utf-8'):
            if 'median' in ln or 'new against old' in ln or nm.startswith('speed-past'):
                out.append('  ' + ln.rstrip())
text = '\n'.join(out) + '\n'
open(os.path.join(L, 'summary.txt'), 'w', encoding='utf-8', newline='\n').write(text)
print(text)
