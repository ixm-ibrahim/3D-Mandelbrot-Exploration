"""Round 15B, shadow: paste a few pictures side by side into one small picture to look at (python look.py out.png a b c ...)."""
import sys
from PIL import Image
D = 'out/r15/shadow/'
names = sys.argv[2:]
cols = min(len(names), 4); rows = (len(names) + cols - 1) // cols
TW, TH = 480, 458
sheet = Image.new('RGB', (cols * TW, rows * TH), (0, 0, 0))
for k, n in enumerate(names):
    im = Image.open(D + n + '.png').convert('RGB')
    if im.size[0] > 800:
        im = im.crop((0, 0, 735, im.size[1]))
    im.thumbnail((TW, TH), Image.LANCZOS)
    sheet.paste(im, ((k % cols) * TW, (k // cols) * TH))
sheet.save(D + sys.argv[1])
