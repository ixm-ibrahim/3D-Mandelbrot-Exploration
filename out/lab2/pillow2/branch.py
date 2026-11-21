"""Sideways stretch of each squaring rule's direction map around the direction (-1, 0, 0) (where the basilica's
main touching point -0.618 and the Mandelbrot set's -0.75 lie) and along the rest of the circle z = 0.
   python out/lab2/pillow2/branch.py  -> branch.json"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], '64', '0']
import importlib.util
spec = importlib.util.spec_from_file_location('rules', os.path.join(HERE, 'checks_rules.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = {}
def unit(x, y, z):
    r = np.sqrt(x * x + y * y + z * z); return x / r, y / r, z / r
for rule in ('merc1', 'merc2', 'radial', 'both', 'smooth'):
    sq = m.RULES[rule]
    row = {}
    for eps in (1e-2, 1e-3):
        phi = np.radians(np.arange(0.5, 360, 1.0))          # azimuth around the x axis, 0 = +y, 90 = +z
        x, y, z = unit(-np.ones_like(phi), eps * np.cos(phi), eps * np.sin(phi))
        fx, fy, fz = unit(*sq(x, y, z))
        ang = np.arctan2(np.hypot(fy, fz), fx) / eps          # angular distance of the image from +x, per unit input
        az = np.degrees(np.unwrap(np.arctan2(fz, fy)))
        row['eps %g' % eps] = dict(stretch_min=round(float(ang.min()), 4), stretch_max=round(float(ang.max()), 4),
                                   stretch_in_plane=round(float(ang[0]), 4), stretch_straight_up=round(float(ang[90]), 4),
                                   turns_of_image_azimuth=round(float(abs(az[-1] - az[0]) / 360), 2))
    # along the circle z = 0: sideways (latitude) stretch against the in-plane stretch (2 for an exact rule)
    th = np.radians(np.arange(0.25, 360, 0.5)); e = 1e-5
    x, y, z = unit(np.cos(th), np.sin(th), e * np.ones_like(th))
    fx, fy, fz = unit(*sq(x, y, z))
    side = np.abs(np.arcsin(np.clip(fz, -1, 1))) / e
    row['along z=0'] = dict(sideways_min=round(float(side.min()), 3), sideways_5pct=round(float(np.percentile(side, 5)), 3),
                            sideways_median=round(float(np.median(side)), 3), sideways_95pct=round(float(np.percentile(side, 95)), 3),
                            sideways_max=round(float(side.max()), 3),
                            at_deg={str(a): round(float(side[np.argmin(np.abs(np.degrees(th) - a))]), 3) for a in (0, 20, 45, 60, 90, 120, 150, 180)})
    out[rule] = row
    print(rule, json.dumps(row))
json.dump(out, open(os.path.join(HERE, 'branch.json'), 'w'), indent=1)
