"""Reviewer check 5: what does the panel's hair number give the FLAT SET ITSELF?
The cut at 0 degrees (the flat plane, upper half) of the one-plane rule is the flat set exactly. Same tiles, same number.
python out/r18/review/flat_hair.py -> close/flat-<set>.json, close/flat-<set>-worst6.png"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import close_sens as C
C.ANGLES = (0.0,); keep = os.path.join(HERE, 'close')
for tag in ('basilica', 'sanmarco', 'airplane', 'cauliflower'):
    for ext in ('.json', '-worst6.png'):                      # keep the earlier one-plane results
        p = os.path.join(keep, 'oneplane-%s%s' % (tag, ext))
        if os.path.exists(p): os.replace(p, p.replace('oneplane-', 'oneplane120-'))
    C.OFFS = (-0.5, 0.35, -0.8, -0.2, 0.7); C.ANGLES = (0.0,)
    # the builder's flag is defined by the first two angles; at one angle every (first two offsets) tile is 'builders'
    C.go('oneplane', tag)
    for ext in ('.json', '-worst6.png'):
        os.replace(os.path.join(keep, 'oneplane-%s%s' % (tag, ext)), os.path.join(keep, 'flat-%s%s' % (tag, ext)))
