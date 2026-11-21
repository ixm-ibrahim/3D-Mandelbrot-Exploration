"""Contact sheets for the judge. One HTML page per picture kind (out/lab2/judge/sheets/<kind>.html) with every
candidate and baseline side by side, Depth colours on top (#plain) and default colours below (#default);
plus one page per view for the judge's own dial settings (sheets/v-<candidate>-<view>.html).
   python out/lab2/judge/sheets.py            writes the pages and sheets/shots.txt (page, actions file)
"""
import html, json, os
ROOT = 'out/lab2'
SH = ROOT + '/judge/sheets'
os.makedirs(SH, exist_ok=True)
CSS = ("body{margin:0;background:#101216;color:#e8e8e8;font:13px/1.3 system-ui,sans-serif}"
       "section{padding:6px 6px 2px;display:inline-block}h2{font-size:15px;margin:0 0 4px}"
       ".g{display:grid;gap:6px}.t{background:#1b1e24}.t b{display:block;padding:2px 5px;font-weight:600;white-space:nowrap;overflow:hidden}"
       ".t img{display:block;width:100%}.t .no{display:flex;align-items:center;justify-content:center;color:#777;aspect-ratio:864/703}")

def page(path, title, sections, cols, tile):
    parts = ['<!doctype html><meta charset="utf-8"><title>%s</title><style>%s</style>' % (html.escape(title), CSS)]
    for sid, head, tiles in sections:
        parts.append('<section id="%s"><h2>%s</h2><div class="g" style="grid-template-columns:repeat(%d,%dpx)">' % (sid, html.escape(head), cols, tile))
        for label, src in tiles:
            if src and os.path.exists(src):
                rel = os.path.relpath(src, os.path.dirname(path)).replace(os.sep, '/')
                parts.append('<div class="t"><b>%s</b><img src="%s"></div>' % (html.escape(label), rel))
            else:
                parts.append('<div class="t"><b>%s</b><div class="no">not drawn</div></div>' % html.escape(label))
        parts.append('</div></section><br>')
    open(path, 'w', encoding='utf-8').write('\n'.join(parts))

WAIT = "document.readyState === 'complete' && Array.from(document.images).every(i => i.complete)"
shots = []
def plan(name, ids):
    acts = [{"wait": WAIT, "timeout": 60}, {"sleep": 0.3}]
    for sid in ids:
        acts.append({"shot": "%s/%s-%s.png" % (SH, name, sid) if len(ids) > 1 else "%s/%s.png" % (SH, name), "clip": "#" + sid})
    json.dump(acts, open('%s/%s.json' % (SH, name), 'w', encoding='utf-8'))
    shots.append(name)

def find(folders, fname):
    for f in folders:
        p = '%s/%s' % (f, fname)
        if os.path.exists(p):
            return p
    return None

CANDS = [
    ('BASELINE inflated: Sphere inversions, 1 plane (current default)', [ROOT + '/judge/base-inflated']),
    ('BASELINE folded: Sphere inversions, 2 planes (jumps on seams)', [ROOT + '/judge/base-folded']),
    ('softfold: 2 planes, blend 0.25 (engineer default)', [ROOT + '/softfold']),
    ('axisbulb: k 1, wobble 0.2, reach 45 (engineer best)', [ROOT + '/axisbulb']),
    ('pillow2 / pillowboth (z=0 and y=0 exact)', [ROOT + '/pillow2/pillowboth', ROOT + '/judge/extra-pillowboth']),
    ('pillow2 / pillowsmooth (NOT exact on z=0)', [ROOT + '/pillow2/pillowsmooth', ROOT + '/judge/extra-pillowsmooth']),
]
KINDS = ['m3d-default', 'm3d-top', 'm3d-x', 'm3d-y', 'm3d-cut0', 'm3d-cut02', 'm2d-z000', 'm2d-z010', 'm2d-z025', 'm2d-z050',
         'j-bas-3d', 'j-bas-top', 'j-bas-x', 'j-bas-2d-z000', 'j-bas-2d-z020', 'j-rab-3d', 'j-off-3d', 'm3d-n3', 'm3d-n8']
for k in KINDS:
    secs = []
    for sid, prefix, word in (('plain', 'plain-', 'Depth from the camera'), ('default', '', 'default colours')):
        secs.append((sid, '%s  |  %s' % (k, word), [(lab, find(fs, prefix + k + '.png')) for lab, fs in CANDS]))
    page('%s/%s.html' % (SH, k), k, secs, 3, 520)
    plan(k, ['plain', 'default'])

VIEWS = ['j-bas-3d', 'j-bas-x', 'j-bas-2d-z020', 'j-rab-3d', 'j-off-3d', 'm3d-default', 'm2d-z025']
J = ROOT + '/judge'
VSETS = {
    'softfold': [('softfold planes 2 blend 0.10', J + '/v-softfold', 'p2-a10'), ('softfold planes 2 blend 0.25 (engineer)', ROOT + '/softfold', None),
                 ('softfold planes 2 blend 0.40', J + '/v-softfold', 'p2-a40'), ('softfold planes 2 blend 0.45', J + '/v-softfold', 'p2-a45'),
                 ('softfold planes 2 blend 0.49', J + '/v-softfold', 'p2-a49'), ('softfold planes 3 blend 0.35', J + '/v-softfold', 'p3-a35'),
                 ('softfold planes 4 blend 0.45', J + '/v-softfold', 'p4-a45'), ('softfold p2 0.25, NO distance estimate, 700 steps', J + '/v-softfold', 'p2-a25-de0'),
                 ('softfold p2 0.49, NO distance estimate, 700 steps', J + '/v-softfold', 'p2-a49-de0'), ('BASELINE folded', J + '/base-folded', None),
                 ('BASELINE inflated', J + '/base-inflated', None)],
    'axisbulb': [('axisbulb k 1 wobble 0.2 reach 45 (engineer)', ROOT + '/axisbulb', None), ('axisbulb k 1 wobble 0.4', J + '/v-axisbulb', 'k1-a040'),
                 ('axisbulb k 1 wobble 1.0 reach 90', J + '/v-axisbulb', 'k1-a100-r90'), ('axisbulb k 1 wobble -0.5', J + '/v-axisbulb', 'k1-am050'),
                 ('axisbulb k 1 wobble 0.25 reach 0', J + '/v-axisbulb', 'k1-a025-r0'), ('axisbulb k 5 wobble 0, NO dist. estimate, 700 steps', J + '/v-axisbulb', 'k5-a000-de0'),
                 ('axisbulb k -3 wobble 0.2, NO dist. estimate, 700 steps', J + '/v-axisbulb', 'km3-a020-de0'), ('axisbulb k 1 wobble 0.2 pinch 0.5', J + '/v-axisbulb', 'k1-a020-b050'),
                 ('lathe (engineer, for comparison)', ROOT + '/axisbulb/v-lathe', None), ('BASELINE folded', J + '/base-folded', None),
                 ('BASELINE inflated', J + '/base-inflated', None)],
}
for cand, tiles in VSETS.items():
    for v in VIEWS:
        ts = []
        for lab, folder, tag in tiles:
            ts.append((lab, '%s/%s--%s.png' % (folder, v, tag) if tag else '%s/plain-%s.png' % (folder, v)))
        name = 'v-%s-%s' % (cand, v)
        page('%s/%s.html' % (SH, name), name, [('s', '%s  |  %s dial settings  |  Depth from the camera' % (v, cand), ts)], 4, 392)
        plan(name, ['s'])
open(SH + '/shots.txt', 'w').write('\n'.join(shots) + '\n')
print(len(shots), 'pages')
