"""Print the judge's numbers as tables (reads out/r21/judge/num/*.json).   python out/r21/judge/table.py > out/r21/judge/numbers.txt"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ['along', 'oneplane', 'lathe', 'sheet.evc005e70k16', 'sheet.ease', 'sheet.vote4', 'alongmem.c_wake1', 'alongmem.c_wake2', 'span.c_lag10', 'span.c_lag25',
         'span.c_page', 'frame.area_1_px', 'frame.orb_inf_px']
D = {}
for nm in ORDER:
    p = os.path.join(HERE, 'num', nm + '.json')
    if os.path.exists(p):
        D[nm] = json.load(open(p))
pc = lambda a, b: 100.0 * a / max(b, 1)

print('FLAT PAGE (M.flat_check, 40,000 points, 60 steps): verdicts that differ from the complex orbit')
print('%-22s %6s %8s %6s %6s  %s' % ('rule', 'M', 'basilica', 'rabbit', 'Siegel', 'strays'))
for nm, d in D.items():
    f = d['flat']; print('%-22s %6d %8d %6d %6d  %.1e' % (nm, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page']))

print('\nTURNED (M.spun_check, 40,000 pairs, 40 steps): share of pairs whose verdict changes when turned round the x-axis')
print('%-22s %10s %10s %12s %12s' % ('rule', 'M differ', 'M inside', 'basilica diff', 'basilica in'))
for nm, d in D.items():
    s = d['spun']; print('%-22s %9.2f%% %9.2f%% %11.2f%% %11.2f%%' % (nm, 100 * s['mandel_differ'], 100 * s['mandel_inside'], 100 * s['basilica_differ'], 100 * s['basilica_inside']))

print('\nDOES THE SOLID STAY: inside points on a 120 x 120 x 120 grid (1,728,000 points; x -1.8..1.8, y and z -1.5..1.5)')
print('%-22s | %8s %8s %8s %7s | %8s %8s %8s %7s %7s' % ('rule', 'bas 30', 'bas 80', 'bas 200', 'kept', 'rab 30', 'rab 80', 'rab 200', 'kept80', 'kept200'))
for nm, d in D.items():
    b, r = d['vol']['basilica'], d['vol']['rabbit']
    print('%-22s | %8d %8d %8d %6.1f%% | %8d %8d %8d %6.1f%% %6.1f%%' % (nm, b['n30'], b['n80'], b['n200'], pc(b['n80'], b['n30']), r['n30'], r['n80'], r['n200'], pc(r['n80'], r['n30']), pc(r['n200'], r['n30'])))

print('\nPIECES at 80 steps on that grid (touching by face, edge or corner). bodies = pieces of 50 cells or more, specks = smaller.')
print('eroded = pieces of 30 cells or more after one layer of cells is peeled off (bodies that only touch come apart; a lump stays one).')
print('%-22s | %-34s | %-48s' % ('rule', 'basilica: bodies specks speck% eroded', 'rabbit: bodies specks speck% biggest% eroded [sizes of the biggest eroded pieces]'))
for nm, d in D.items():
    b, r = d['vol']['basilica'], d['vol']['rabbit']
    print('%-22s | %6d %6d %6.2f%% %6d          | %6d %6d %6.2f%% %7.1f%% %6d %s; the biggest peeled piece holds %.0f%% of what is left' % (
        nm, b['pieces80']['bodies'], b['pieces80']['specks'], 100 * b['pieces80']['speck_share'], b['eroded80']['pieces30'],
        r['pieces80']['bodies'], r['pieces80']['specks'], 100 * r['pieces80']['speck_share'], 100 * r['pieces80']['biggest_share'], r['eroded80']['pieces30'], r['eroded80']['sizes'][:6],
        100.0 * (r['eroded80']['sizes'][0] if r['eroded80']['sizes'] else 0) / max(r['eroded80']['left'], 1)))

print('\nPINCH: share of a small ball round the rabbit\'s pinch point that is inside (80 steps), off the page. Low and equal at both radii = bodies meet in a point; high = lump.')
for nm, d in D.items():
    p = d['pinch']; print('%-22s radius 0.12: %5.1f%%   radius 0.06: %5.1f%%' % (nm, 100 * p['r0.12'], 100 * p['r0.06']))

print('\nBODY OF THE FLAT PICTURE: flat-inside points lifted off the page, lost at 300 steps (count lost / count tried)')
print('%-22s | %-23s | %-23s | %-23s | %-23s' % ('rule', 'Mandelbrot 1e-6, 1e-3', 'basilica 1e-6, 1e-3', 'rabbit 1e-6, 1e-3', 'Siegel 1e-6, 1e-3'))
for nm, d in D.items():
    L = d['lift']; cells = ['%5d %5d / %5d' % (L[k]['lost_1e-06'], L[k]['lost_0.001'], L[k]['inside']) for k in ('mandelbrot', 'basilica', 'rabbit', 'siegel')]
    print('%-22s | %-23s | %-23s | %-23s | %-23s' % (nm, *cells))

for key, ttl in (('arcs_x0', 'x = 0 (round the basilica\'s middle body)'), ('arcs_xm1', 'x = -1 (round the basilica\'s side body)')):
    print('\nARCS on circles round the x-axis at %s, 80 steps: number of separate inside arcs / share of the circle inside' % ttl)
    rad = [a['radius'] for a in next(iter(D.values()))[key]]
    print('%-22s ' % 'radius' + ' '.join('%8.2f' % r for r in rad))
    for nm, d in D.items():
        print('%-22s ' % nm + ' '.join('%3d/%3.0f%%' % (a['arcs'], 100 * a['share']) for a in d[key]))
    print('widest arcs in degrees at the radius with the most arcs:')
    for nm, d in D.items():
        best = max(d[key], key=lambda a: (a['arcs'], a['share']))
        print('%-22s radius %.2f: %d arcs, %s' % (nm, best['radius'], best['arcs'], best['widest_deg']))
