"""M.mandel_sheet for the rules under judgment (cuts at 0, 11.25, 22.5, 45, 90 degrees, one cut across, the rough solid).

    python out/r21/judge/mandel.py a      the first five rules  -> mandel-a.png
    python out/r21/judge/mandel.py b      the other five        -> mandel-b.png
The solid is drawn at 40 steps instead of the library's 22 (rough blocks at 22 steps hide dust)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
if __name__ == '__main__':
    tag = sys.argv[1]; rules = J.RULES[:5] if tag == 'a' else J.RULES[5:]
    M.mandel_sheet(rules, os.path.join(J.HERE, 'mandel-%s.png' % tag), w=340, cw=270, ch=250, nd=220, steps=40, cut_steps=80, angles=(0.0, 11.25, 22.5, 45.0, 90.0))
