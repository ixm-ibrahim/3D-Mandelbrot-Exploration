"""The eyes: the walk results of a tag (logs/walk/<tag>-*.json), one short line a view on the screen, and the long
lines in logs/walk-<tag>.txt.   python out/r28/fix/eyes/mk/brief.py <tag> [view ...]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import walk
tag = sys.argv[1]; want = sys.argv[2:]
D = os.path.join(walk.EYES, 'logs', 'walk')
rs = []
for f in sorted(os.listdir(D), key=lambda f: os.path.getmtime(os.path.join(D, f))):
    if f.startswith(tag + '-') and f.endswith('.json'):
        rs.append(json.load(open(os.path.join(D, f), encoding='utf-8')))
with open(os.path.join(walk.EYES, 'logs', 'walk-%s.txt' % tag), 'w', encoding='utf-8', newline='\n') as f:
    for r in rs:
        f.write(walk.line(r) + '\n\n')
tot = dict(views=0, rays=0, stops=0, HOLES=0, THROUGH=0, OPEN=0, HB=0, TB=0, DO=0)
for r in rs:
    if want and r['view'] not in want:
        continue
    if r.get('flat'):
        print('%-26s 2D %s holes %d ghosts %d (solid only by depth %d of %d solid)' % (r['view'], r['size'], r['HOLES_wellInsideNotPainted'], r['GHOSTS_wellOutsidePainted'], r['solidOnlyByDepth'], r['solid'])); continue
    tot['views'] += 1; tot['rays'] += r['rays']; tot['stops'] += r['stops']; tot['HOLES'] += r['HOLES']; tot['THROUGH'] += r['SEEN_THROUGH']; tot['OPEN'] += r['IN_THE_OPEN']; tot['HB'] += max(0, r.get('HOLES_IN_A_BALL', 0)); tot['TB'] += max(0, r.get('SEEN_THROUGH_A_BALL', 0)); tot['DO'] += max(0, r.get('stopsOnDepthOnly', 0))
    print('%-26s %s stops %5d nowhere %5d | HOLES %d (>10px %d, longest %.1f, in a ball %s) THROUGH %d (a ball %s) | open78 %d OPEN %d (page %.1f px) | depth-only stops %s | page met>2px %d worst %.1f | pic bg-in-hits %d (patch %s) paint-in-miss %d (patch %s) | short>2 %d deep>2 %d | %s s'
          % (r['view'], r['size'], r['stops'], r['nowhere'], r['HOLES'], r['holesOver10px'], r['longestHolePx'], r.get('HOLES_IN_A_BALL', '?'), r['SEEN_THROUGH'], r.get('SEEN_THROUGH_A_BALL', '?'), r['stopsWithNoSolidIn78Probes'], r['IN_THE_OPEN'], r['openWorstPagePx'], r.get('stopsOnDepthOnly', '?'),
             r['pageMetOver2px'], r['pageMetWorstPx'], r['PICTURE_BG_WHERE_RAYS_STOP'], r.get('PICTURE_HOLE_PATCHES', '?'), r['PICTURE_PAINT_WHERE_NO_RAY_STOPS'], r.get('PICTURE_GHOST_PATCHES', '?'), r['stopsShortBy2px'], r['stopsDeepBy2px'], r['seconds']))
print('3D views %(views)d, rays %(rays)d, stops %(stops)d: HOLES %(HOLES)d (in a ball %(HB)d), SEEN THROUGH %(THROUGH)d (through a ball %(TB)d), IN THE OPEN %(OPEN)d; stops on what only the depth calls solid %(DO)d' % tot)
