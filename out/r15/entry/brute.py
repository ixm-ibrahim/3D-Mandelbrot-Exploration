"""Round 15, entry: turn the grids of brute.js (out/r15/entry/brute.txt) into pictures brute-<tag>-<k>.png."""
import base64, json, re
import numpy as np
from PIL import Image
import sys
t = open('out/r15/entry/' + (sys.argv[1] if len(sys.argv) > 1 else 'brute.txt'), encoding='utf-8').read()
o = json.loads(t.strip().splitlines()[-1])
for r in o:
    g = np.frombuffer(base64.b64decode(r['rows']), np.uint8).reshape(r['N'], r['N']).astype(float)
    its = r['its']
    im = np.zeros((r['N'], r['N'], 3), np.uint8)
    ins = g == 0
    v = np.clip((g - 1) / max(its - 1, 1), 0, 1)
    im[..., 0] = 14 + 60 * v; im[..., 1] = 18 + 90 * v; im[..., 2] = 30 + 150 * v
    im[ins] = (236, 226, 200)
    Image.fromarray(im).resize((560, 560), Image.NEAREST).save('out/r15/entry/brute-%s-%d.png' % (r['tag'], r['k']))
    print('brute-%s-%d.png: window %.2f wide round %s, plane y = %.4f, %d steps, in the solid: %.1f %%' % (r['tag'], r['k'], r['W'], r['t'], r['t'][1], its, 100 * r['inside']))
