"""Reviewer: one sheet of the pictures behind the review's main findings. python out/r18/review/review_sheet.py"""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
def font(s):
    for p in ('C:/Windows/Fonts/segoeui.ttf', 'C:/Windows/Fonts/arial.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, s)
    return ImageFont.load_default()
F1, F2 = font(30), font(40)
W = 2544
ROWS = [
 ('close/flat-basilica-worst6.png', 'A. The FLAT basilica itself (the flat plane, nothing 3D). The panel\'s hair number gives these tiles 1.2 to 2.0; its line for "clean" is 0.3.\n    By eye: clean arcs with round buds. The number reads ordinary buds as hair, so the flat set itself fails "clean close up".'),
 ('close/twoplane-basilica-worst6.png', 'B. Two planes (the reference look), basilica: the six worst of 120 tiles: 0.32, 0.19, 0.18, 0.17, 0.17, 0.15 (the panel\'s own 12 tiles: 0.15).\n    By eye: clean. The 0.32, over the line, is one small bud.'),
 ('close/twoplane-sanmarco-worst6.png', 'C. Two planes, San Marco: six worst of 120: 0.52, 0.48, 0.45, 0.40, 0.38, 0.32 (the panel\'s own 12 tiles: 0.25 = pass). 10 of 120 tiles are over the line.\n    By eye: a few thin slivers lying along the skin, and buds leaning on it. Nearly clean, but the number says fail.'),
 ('close/p_tt1024-basilica-worst6.png', 'D. p_tt1024 (the "best newcomer"), basilica: six worst of 120: 5.08, 4.37, 3.93, 3.54, 2.21, 0.94 (the panel\'s own 12 tiles: 0.26 = PASS).\n    By eye: a film of loose dust over the skin half-way between the two special planes (first five), slanting fins at 33.75 degrees (last). Not clean.'),
 ('close/along-basilica-worst6.png', 'E. Turning plane along, basilica: six worst of 120: 2.04, 1.96, 1.62, 1.51, 1.47, 1.41. By eye: combs of thin fins in tiles 1, 3, 4, 5 (a real fault).\n    Tiles 2 and 6 are its own exact plane at 45 degrees: the flat outline, clean by eye, yet scored 1.96 and 1.41: the number cannot tell fins from buds.'),
 ('close/along-airplane-worst6.png', 'F. Turning plane along, airplane: all six worst tiles (0.66 to 0.47) are on its own exact plane at 45 degrees: the flat airplane\'s strings of beads, read as hair.\n    Away from that plane the worst of 105 tiles is 0.12: its airplane skin is clean, as the panel says.'),
]
ims = [(Image.open(os.path.join(HERE, p)).convert('RGB'), t) for p, t in ROWS]
lab = Image.open(os.path.join(HERE, 'lab-vs-bench-rabbit30.png')).convert('RGB')
dr0 = Image.open(os.path.join(HERE, 'drain-along-rabbit30.png')).convert('RGB'); dr0 = dr0.resize((784, int(dr0.height * 784 / dr0.width)), Image.LANCZOS)
H = 70 + sum(im.height + 100 for im, _ in ims) + 100 + lab.height + 110 + dr0.height + 30
S = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(S)
d.text((16, 10), 'Round 18 review: what the close cut measures, and what is there for a c in no special plane', fill=(240, 240, 240), font=F2)
y = 70
for im, t in ims:
    d.multiline_text((16, y + 6), t, fill=(225, 225, 225), font=F1, spacing=6); y += 92
    S.paste(im, (0, y)); y += im.height + 8
d.multiline_text((16, y + 6), 'G. Rabbit turned 30 degrees out of the flat plane, turning plane along, the cut at z = 0. Left: the lab\'s picture labelled 40 iterations (cream = inside, area 0.92).\n    Right: the same cut worked point by point at 40 steps: dust (area 0.20). The lab\'s cream matches about 18 steps, not 40.', fill=(225, 225, 225), font=F1, spacing=6); y += 96
S.paste(lab, (0, y)); S.paste(dr0, (lab.width + 30, y + 120))
d.multiline_text((lab.width + 30, y + 10), 'H. The same solid at 14, 20, 40, 80 steps:\n    volume 1.20, 0.78, 0.18, 0.009. It drains away.', fill=(225, 225, 225), font=F1, spacing=6)
S = S.crop((0, 0, W, y + lab.height + 20)); S.save(os.path.join(HERE, 'review-sheet.png')); print(S.size)
