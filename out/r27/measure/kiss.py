"""Round 27, measure, part 4: kiss against pinch. The same close-up of one meeting point in three pictures.

    python out/r27/measure/kiss.py numbers     how much of a small circle round the meeting point is outside -> kiss.log
    python out/r27/measure/kiss.py picture     kiss.png

The meeting point of the middle body with its left neighbour:
    true c = -1      at alpha = (1 - sqrt 5) / 2 = -0.618...   (the rule pushes away from it: a pinch)
    true c = -0.75   at alpha = -0.5                           (the rule neither pushes nor pulls there: a kiss)
    balls object     at x = -k2 / 2 = -0.525                   (two round balls: a kiss)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballkit as K

K2, T0 = 1.05, 1.40
G = K.Grid('line')
CASES = [('True flat picture, c = -1', 'a pinch', lambda x, y, n: K.julia(x, y, -1.0, 0.0, n), (1 - np.sqrt(5)) / 2, 700),
         ('True flat picture, c = -0.75', 'a kiss', lambda x, y, n: K.julia(x, y, -0.75, 0.0, n), -0.5, 3000),
         ('Balls on balls', 'a kiss', lambda x, y, n: K.inside_picture(x, y, 0 * x, G, 2 * T0, 80, K2) == 1, -K2 / 2, 0)]


def numbers():
    log = open(os.path.join(HERE, 'kiss.log'), 'w')

    def say(s):
        print(s); log.write(s + '\n'); log.flush()
    say('How much of a small circle round the meeting point lies OUTSIDE (degrees of 360), at radius d')
    say('   d         c = -1      c = -0.75    balls object')
    a = (np.arange(36000) + 0.5) / 36000 * 2 * np.pi
    for d in (0.1, 0.03, 0.01, 0.003, 0.001, 0.0003):
        row = []
        for name, kind, f, x0, n in CASES:
            steps = n if n == 0 else (max(n, int(4 / d ** 2)) if 'c = -0.75' in name else 3000)
            if steps > 400000:
                row.append(float('nan')); continue
            v = f(x0 + d * np.cos(a), d * np.sin(a), steps); row.append(360.0 * (1 - v.mean()))
        say('   %-7g   %8.3f    %8.4f     %8.3f' % (d, *row))
    say('(c = -0.75 needs about 1 / (2 d^2) steps to throw a point out from the distance d; the circle at d was given 4 / d^2 steps; nan = not run)')
    log.close()


def picture():
    w, h, ss = 520, 390, 2; halves = (0.3, 0.03, 0.003); pad = 10; t0 = time.time()
    W = pad + 3 * (w + pad); H = 104 + 3 * (h + 34) + 58
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Kiss against pinch: the point where the middle body meets its left neighbour', fill=(240, 240, 245), font=K.font(27))
    for j, (name, kind, f, x0, n) in enumerate(CASES):
        x = pad + j * (w + pad)
        d.text((x, 54), '%s: %s' % (name, kind), fill=(235, 220, 170), font=K.font(21))
        for i, hw in enumerate(halves):
            y = 104 + i * (h + 34)
            xs = x0 - hw + (np.arange(w * ss) + 0.5) * 2 * hw / (w * ss); ys = hw * h / w - (np.arange(h * ss) + 0.5) * 2 * hw / (w * ss)
            Xg, Yg = np.meshgrid(xs, ys); cov = np.asarray(f(Xg, Yg, n), float).reshape(h, ss, w, ss).mean((1, 3))
            im.paste(Image.fromarray(K.paint(cov, fg=(232, 224, 200), bg=(22, 28, 44))), (x, y + 24))
            d.text((x + 2, y), ('the meeting point', '10 times closer', '100 times closer')[i], fill=(170, 178, 192), font=K.font(16))
            print(name, hw, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    y = 104 + 3 * (h + 34)
    d.text((pad, y + 4), 'A pinch looks the same however close you come: two bodies end in a point and the outside keeps its wedge. A kiss flattens out: the outside thins to nothing.', fill=(200, 205, 215), font=K.font(17))
    d.text((pad, y + 28), 'Round balls can only kiss. The true picture of c = -0.75 kisses too (closer than balls do); the true picture of c = -1 pinches.', fill=(200, 205, 215), font=K.font(17))
    im.save(os.path.join(HERE, 'kiss.png')); print('wrote kiss.png', im.size)


if __name__ == '__main__':
    numbers() if (sys.argv[1] if len(sys.argv) > 1 else 'numbers') == 'numbers' else picture()
