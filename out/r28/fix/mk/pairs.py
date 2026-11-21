"""Round 28, the fixer: before and after side by side (left: the page as the checkers had it, right: repaired).
  python out/r28/fix/mk/pairs.py   -> out/r28/fix/shots/pair-*.png"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE); R28 = os.path.dirname(FIX)
PAIRS = [
    ('pair-e1-2d-bud-kiss', os.path.join(FIX, 'eyes', 'shots', 'before-p150-r50-2d-budkiss.png'), os.path.join(FIX, 'eyes', 'shots', 'after-p150-r50-2d-budkiss.png')),
    ('pair-e1-2d-bud-kiss-depth100', os.path.join(FIX, 'eyes', 'shots', 'before-p150-r50-2d-budkiss-d100.png'), os.path.join(FIX, 'eyes', 'shots', 'after-p150-r50-2d-budkiss-d100.png')),
    ('pair-e1-2d-size200', os.path.join(FIX, 'eyes', 'shots', 'before-p200-r50-2d.png'), os.path.join(FIX, 'eyes', 'shots', 'after-p200-r50-2d.png')),
    ('pair-e1-3d-bud-kiss', os.path.join(R28, 'eyes', 'shots', 'dw-p150-r50-budkiss.png'), os.path.join(FIX, 'eyes', 'shots', 'after-p150-r50-budkiss.png')),
    ('pair-d1-844x390-size400', os.path.join(FIX, 'ui', 'shots', 'before', 'sizes2-new-844x390-size-400.png'), os.path.join(FIX, 'ui', 'shots', 'sizes2-new-844x390-size-400.png')),
    ('pair-d1-844x390-size300', os.path.join(FIX, 'ui', 'shots', 'before', 'sizes2-new-844x390-size-300.png'), os.path.join(FIX, 'ui', 'shots', 'sizes2-new-844x390-size-300.png')),
]
for name, a, b in PAIRS:
    if not (os.path.exists(a) and os.path.exists(b)):
        print('missing for', name, os.path.exists(a), os.path.exists(b)); continue
    A, B = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
    w = A.width + B.width + 12; h = max(A.height, B.height)
    im = Image.new('RGB', (w, h), (255, 255, 255)); im.paste(A, (0, 0)); im.paste(B, (A.width + 12, 0))
    im.save(os.path.join(FIX, 'shots', name + '.png')); print('wrote', name, im.size)
