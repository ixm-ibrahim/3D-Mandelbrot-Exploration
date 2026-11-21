"""Round 23, judge, check 5: how often a rule lays the directions over each other, and whether it folds.

    python out/r23/judge/j5_cover.py

On a fine grid of directions (latitude, longitude) the direction of the square is taken, and by small differences the
area factor with its sign (positive = laid down the right way round, negative = turned over = folded).
  covers  = sum of the signed area / area of the sphere (how many times the directions are laid over each other, net)
  folded  = share of the directions with a negative area factor
  squeeze = share of the directions where the larger stretch is more than 2 (4) times the smaller
Also the stretch along and across the circle 60 degrees up (for the cones: both should be 2).
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jl as L

nla, nlo = 1800, 3600; e = 1e-6
la = (np.arange(nla) + 0.5) / nla * np.pi - np.pi / 2; lo = (np.arange(nlo) + 0.5) / nlo * 2 * np.pi - np.pi
LA, LO = np.meshgrid(la, lo, indexing='ij'); wgt = np.cos(LA)


def dirs(F, la_, lo_):
    X, Y, Z = F(np.cos(la_) * np.cos(lo_), np.cos(la_) * np.sin(lo_), np.sin(la_)); n = np.sqrt(X * X + Y * Y + Z * Z)
    return np.stack([X / n, Y / n, Z / n])


for nm, F in (('one plane', L.P), ('cones (welded)', L.CONES), ('along', L.ALONG), ('two planes', L.TWOPLANE)):
    G = dirs(F, LA, LO); Ga = (dirs(F, LA + e, LO) - dirs(F, LA - e, LO)) / (2 * e); Gb = (dirs(F, LA, LO + e) - dirs(F, LA, LO - e)) / (2 * e) / np.cos(LA)
    det = -np.einsum('i...,i...->...', G, np.cross(Ga, Gb, axis=0))          # minus: (north, east, outward) is a left-handed frame
    ok = np.isfinite(det) & (np.abs(det) < 1e4)
    covers = float((det * wgt)[ok].sum() / wgt[ok].sum()); folded = float((wgt * (det < 0))[ok].sum() / wgt[ok].sum())
    a = (Ga * Ga).sum(0); b = (Ga * Gb).sum(0); d = (Gb * Gb).sum(0); tr = a + d; dd = np.sqrt(np.maximum(tr * tr / 4 - (a * d - b * b), 0))
    s1 = np.sqrt(np.maximum(tr / 2 + dd, 0)); s2 = np.sqrt(np.maximum(tr / 2 - dd, 1e-300)); ratio = s1 / s2
    i60 = int(np.argmin(np.abs(la - np.radians(60.0))))
    print('%-15s covers %.4f | folded %.4f %% | squeezed more than 2 to 1: %.1f %%, more than 4 to 1: %.1f %% | at %.2f degrees up: stretch along the circle %.4f .. %.4f, across it %.4f .. %.4f'
          % (nm, covers, 100 * folded, 100 * float((wgt * (ratio > 2))[ok].sum() / wgt[ok].sum()), 100 * float((wgt * (ratio > 4))[ok].sum() / wgt[ok].sum()),
             np.degrees(la[i60]), np.sqrt(d[i60]).min(), np.sqrt(d[i60]).max(), np.sqrt(a[i60]).min(), np.sqrt(a[i60]).max())); sys.stdout.flush()
