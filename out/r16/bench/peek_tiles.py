"""Working aid: paste chosen tiles of chosen rules side by side.  python peek_tiles.py out.png S rule1,rule2 tag1,tag2,..."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
out, S, rules, tags = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(','), sys.argv[4].split(',')
im = Image.new('RGB', (S * len(tags), S * len(rules)), (0, 0, 0))
for r, n in enumerate(rules):
    for k, t in enumerate(tags):
        p = os.path.join(HERE, 'tiles', n, t + '.png')
        if os.path.exists(p):
            im.paste(Image.open(p).convert('RGB').resize((S, S), Image.LANCZOS), (k * S, r * S))
im.save(os.path.join(HERE, 'logs', out)); print(im.size)
