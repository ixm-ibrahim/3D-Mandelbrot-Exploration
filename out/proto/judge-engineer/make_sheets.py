"""Contact sheets: one HTML page per picture kind, every candidate and baseline side by side, labelled."""
import os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ['m3d-default', 'm3d-top', 'm3d-x', 'm3d-y', 'm3d-cut0', 'm3d-cut02', 'm2d-z000', 'm2d-z010', 'm2d-z025', 'm2d-z050',
         'j-bas-3d', 'j-bas-top', 'j-bas-x', 'j-bas-2d-z000', 'j-bas-2d-z020', 'j-rab-3d', 'm3d-n3', 'm3d-n8']
COLS = [('radial', 'CANDIDATE pillow / radial (from the centre)', '../../radial/'),
        ('sine', 'CANDIDATE pillow / sine (barycentric sines)', '../../sine/'),
        ('twoplane', 'CANDIDATE pillow / twoplane (from the altitude midpoint)', '../../twoplane/'),
        ('base-inflated', 'BASELINE mercator, planes = 1 ("inflated")', '../base-inflated/'),
        ('base-folded', 'BASELINE mercator, planes = 2 (current default, "folded")', '../base-folded/'),
        ('base-bulb', 'BASELINE bulb, power 2', '../base-bulb/')]
os.makedirs(os.path.join(HERE, 'sheets'), exist_ok=True)
for k in KINDS:
    cells = []
    for name, label, rel in COLS:
        path = os.path.normpath(os.path.join(HERE, 'sheets', rel, k + '.png'))
        if os.path.exists(path):
            cells.append('<figure><figcaption>%s</figcaption><img src="%s%s.png"></figure>' % (html.escape(label), rel, k))
        else:
            cells.append('<figure><figcaption>%s</figcaption><div class="none">no picture</div></figure>' % html.escape(label))
    page = ('<!doctype html><meta charset="utf-8"><title>%s</title><style>body{margin:0;background:#111;color:#eee;font:15px system-ui,sans-serif}'
            'h1{font-size:18px;margin:6px 10px}.g{display:grid;grid-template-columns:repeat(3,640px);gap:6px;padding:0 6px}'
            'figure{margin:0}figcaption{font-weight:600;padding:3px 2px;height:20px}img{width:640px;height:520px;object-fit:contain;background:#000;display:block}'
            '.none{width:640px;height:520px;background:#222;display:flex;align-items:center;justify-content:center}</style>'
            '<h1>%s</h1><div class="g">%s</div>') % (k, k, ''.join(cells))
    open(os.path.join(HERE, 'sheets', k + '.html'), 'w', encoding='utf-8').write(page)
print('wrote', len(KINDS), 'sheets')
