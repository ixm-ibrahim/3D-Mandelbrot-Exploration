"""Working aid: python out/r18/panel/montage.py <tile name> <out name> <rule> [<rule> ...] [sets=a,b,c]
One row per panel set, one column per rule, the named tile. Writes look/<out name>.png."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel as P

if __name__ == '__main__':
    tname, oname = sys.argv[1], sys.argv[2]
    rules = [a for a in sys.argv[3:] if not a.startswith('sets=')]
    tags = P.TAGS
    for a in sys.argv[3:]:
        if a.startswith('sets='):
            tags = a[5:].split(',')
    S = 260
    im = Image.new('RGB', (110 + S * len(rules), 24 + S * len(tags)), (12, 14, 20)); d = ImageDraw.Draw(im); f = P.turns.font(14)
    for j, r in enumerate(rules):
        d.text((114 + j * S, 4), r, fill=(230, 230, 230), font=f)
    for i, t in enumerate(tags):
        d.text((4, 30 + i * S), t, fill=(230, 230, 230), font=f)
        for j, r in enumerate(rules):
            im.paste(P.tile(r, t, tname, S - 4), (110 + j * S, 24 + i * S))
    os.makedirs(os.path.join(HERE, 'look'), exist_ok=True)
    im.save(os.path.join(HERE, 'look', oname + '.png'))
    print(os.path.join(HERE, 'look', oname + '.png'))
