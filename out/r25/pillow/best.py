"""Round 25, section "pillow": the rules of this section, by name.

    import sys; sys.path.insert(0, 'out/r25/pillow'); import best; r = best.rule()          # the skew pillow
    best.rule('tetra')   best.rule('skew-mirror')   best.rule('square')

The skew pillow is the nearest thing of this section for c = -1 (separate round bodies with egg-shaped bodies on
them); it is NOT a rule that passes: rough rabbit, a lump for the rabbit's mirror image, one-sided. See NOTES.md.

Every rule is  F(v) = |v|^2 * G(direction of v),  G = the mirror doubling z -> 2 conj(z) on a four-corner pillow
(pil.py), layout with the belt angle-true (kind 'JA'). The pillow's two periods have the same length (nothing else
is chosen):
    square   rho = 0,   H = 1            the two seams one above the other (round 15's square pillow, new layout)
    tetra    rho = 1/2, H = sqrt(3)/2    the two seams crossed: the regular tetrahedron
    skew     rho = 1/4, H = sqrt(15)/4   the top seam turned 135 degrees against the bottom one; 'skew-mirror' = rho 3/4
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P

KINDS = {
    'square': (0.0, 1.0, 'square pillow: the two seams one above the other'),
    'tetra': (0.5, np.sqrt(3) / 2, 'tetrahedron pillow: the two seams crossed'),
    'skew': (0.25, np.sqrt(15) / 4, 'skew pillow: the top seam turned 135 degrees against the bottom one'),
    'skew-mirror': (0.75, np.sqrt(15) / 4, 'skew pillow, the mirror image'),
}


def rule(name='skew', kind='JA'):
    rho, H, label = KINDS[name]
    return P.rule(rho, H, kind, name=name, label=label)
