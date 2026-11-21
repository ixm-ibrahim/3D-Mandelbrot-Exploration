"""One sheet for the orchestrator: the pictures the recommendation rests on, stacked, with plain captions."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import truth as T
parts = [('zoom-shoulder-final.png', '1. Basilica: the same patch of the middle body\'s skin (0.44 wide, between the plane at 0 and the plane at 60 degrees). Two planes: clean. Along: round bumps, two fins. Wind forms: pleats and plates; the wider the exact band, the less of them.'),
         ('hair-m_w3-basilica.png', '2. Basilica skin point by point, sinus form (m_w3): three worst and three typical tiles of 120. Red = thin fins, purple = film. Not clean at any tile width.'),
         ('hair-w_c15-basilica.png', '3. The same for the recommended form (w_c15: exact band 15 degrees, straight ramp): less of it, still not clean (32 of 35 tiles over the line at the widest tile; turning along: 4 of 35).'),
         ('vol-rabbit-axis-final.png', '4. Rabbit seen along the x-axis. Along: a layered lump. Sinus: a six-armed star of blades and loose flakes. Bands: six fat arms of faceted bodies with round buds. None is balls meeting at points.'),
         ('vol-rabbit-above-final.png', '5. Rabbit seen from above the flat plane: three copies of the flat rabbit crossing on the x-axis.'),
         ('vol-siegel-above-final.png', '6. Siegel disc. One plane gives a smooth pillow (not shown). Sinus: a wire skeleton that drains away. Bands: a ragged six-armed mass. No smooth body in any form.'),
         ('vol-basyz-final.png', '7. The basilica nudged off both planes, c = (-1, 0.05, 0.03). Along keeps its buds. Every wind form crumples; the recommended form stays thickest and does not drain; the smooth 15 degree band thins.')]
ims = [Image.open(os.path.join(HERE, p)).convert('RGB') for p, _ in parts]
W = max(i.width for i in ims); H = sum(i.height + 34 for i in ims) + 50
im = Image.new('RGB', (W, H), (12, 13, 18)); dr = ImageDraw.Draw(im); f = T.font(17)
dr.text((8, 10), 'Round 20, profiles: "wind, then square" with the sinus profile and with exact bands. Voxel views are rough (257 a side); cuts are point by point.', fill=(240, 240, 240), font=T.font(20))
y = 50
for (p, cap), i in zip(parts, ims):
    dr.text((8, y + 6), cap, fill=(225, 225, 225), font=f); im.paste(i, (0, y + 34)); y += i.height + 34
im.save(os.path.join(HERE, 'sheet-profiles.png')); print('wrote sheet-profiles.png', im.size)
