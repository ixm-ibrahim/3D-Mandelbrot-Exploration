# Round 23, outside2: what is published (searched 2026-11-19)

How each entry was read is marked: **[text]** = I read the paper's text (extracted from the PDF), **[abstract]** = abstract
or publisher page only, **[snippet]** = search-result excerpt only. Nothing here is from memory alone.

## A. Extensions of z^2 from the flat plane into space (the closest literature to this project)

1. **On Poincaré extensions of rational maps.** C. Cabrera, P. Makienko, G. Sienra. Conform. Geom. Dyn. 19 (2015);
   arXiv:1305.7164. https://arxiv.org/abs/1305.7164 **[text]**
   - Section 4.1 gives the extension of Q(z) = z^2 to the upper half-space:
     Q^(x, y, t) = ( |p|^2 (x^2 - y^2) / (|p|^2 + t^2), |p|^2 2xy / (|p|^2 + t^2), |p|^2 2t|p| / (|p|^2 + t^2) ).
     **This is the lab's one-plane rule, term for term** (measured: 7e-15 over 200,000 points, `check1.py` A).
   - It is w * w for a multiplication of space points that they construct: commutative, associative, equal to the complex
     product on the flat plane, |a * b| = |a||b|. In plain terms: lengths multiply, longitudes add, Mercator latitudes add
     (measured: 1e-14). They define Q_c^ = (add c) o Q^, the filled set K(Q_c^), and draw its cut by the upright half-plane
     for c = 0.25, -0.75, -0.77, -1, -1.28. Also: "all conformally natural extensions of R are homotopic" and if there are
     two there are uncountably many (Prop. 22): mathematics does not single out one extension.
2. **Conformally natural extensions revisited.** C. L. Petersen, 2011, arXiv:1102.1470. https://arxiv.org/abs/1102.1470
   **[abstract]** The Douady-Earle (conformal barycentre) extension applied to rational maps of the sphere gives
   real-analytic maps of hyperbolic 3-space; written to answer Thurston's question about a 3-manifold of a rational map.
   Gives us: the one extension that commutes with every sphere-inversion map. Built here (`de.py`): it is the one-plane
   rule to within 1.2 degrees.
3. **Extending rational maps.** G. J. Martin. Conform. Geom. Dyn. 8 (2004) 158-166.
   https://www.ams.org/journals/ecgd/2004-08-07/S1088-4173-04-00115-8/home.html **[abstract]** When does a rational map
   extend to a uniformly quasiregular map of the upper half-space: yes near z^d with a Cantor Julia set, and (per
   ref. 1's remark, **[text]**) "for most rational maps these extensions do not exist".
4. **Extending rational expanding Thurston maps.** D. Meyer, J. Münch, 2025, arXiv:2510.18015.
   https://arxiv.org/abs/2510.18015 **[abstract]** A postcritically finite rational map whose Julia set is the whole sphere
   extends to a quasiregular map of a neighbourhood of the unit sphere in R^3, iterates uniformly quasiregular on
   shrinking neighbourhoods. Gives us: "evenly expanding direction maps" (the pillow kind) are the ones known to thicken
   into space with bounded squeeze.

## B. The mathematicians' 3D power map (the lab's "Square pillow") and its relatives

5. **Uniformly quasiregular mappings of Lattès type.** V. Mayer. Conform. Geom. Dyn. 1 (1997) 104-111. **[snippet, via
   refs. 6, 7, 8]** The power map P_d is defined by Z(d x) = P_d(Z(x)), Z the Zorich map (the space version of e^z).
   Gives us: the published 3D analogue of z^d; all iterates squeeze by a bounded amount.
6. **Lattès-type uniformly quasiregular mappings and their Julia sets** (poster), R. Kangaslampi.
   https://math.aalto.fi/~rkangasl/rnc_poster.pdf **[snippet]** "a 4-to-1 map on the 3-sphere", Julia set a 2-sphere:
   power 2 in 3D covers 4 times (2^(3-1)), which is the pillow's count.
7. **Strongly automorphic mappings and Julia sets of uniformly quasiregular mappings.** A. Fletcher, D. Macclure, 2017,
   arXiv:1703.02455. https://arxiv.org/abs/1703.02455 **[text, first 100,000 characters]** Julia sets of these maps are
   the whole space (Lattès kind), a quasi-sphere (power kind) or a quasi-disc (Chebyshev kind). Nothing else occurs.
8. **Permutable quasiregular maps.** A. Tsantaris, arXiv:1912.04152 **[snippet]**; **Uniformly quasiregular maps with
   toroidal Julia sets**, R. Kangaslampi, K. Peltonen, J.-M. Wu, Conform. Geom. Dyn. 16 (2012),
   https://www.ams.org/ecgd/2012-16-04/S1088-4173-2012-00235-4/ **[snippet; page refused the fetch]**: first maps of this
   kind whose Julia set is a 2-torus.
9. **Rigidity in holomorphic and quasiregular dynamics.** G. J. Martin, V. Mayer. Trans. AMS 355 (2003) 4349-4363.
   https://www.ams.org/journals/tran/2003-355-11/S0002-9947-03-03160-X **[snippet]** Conjecture (open): a non-injective
   uniformly quasiregular map of the n-sphere, n >= 3, with Julia set of positive measure is of Lattès type.
10. **On Lattès maps.** J. Milnor, arXiv:math/0402147. https://arxiv.org/abs/math/0402147 **[snippet]** Rational maps
    with a flat orbifold metric are exactly power maps, Chebyshev maps and Lattès maps (torus folded by a small group).
    Gives us: "the same spacing everywhere" on a sphere of directions means a Lattès map, with its corner points.
11. **Interpolating quasiregular power mappings.** J. Burkart, A. Fletcher, D. Nicks, 2024, arXiv:2411.10190.
    https://arxiv.org/abs/2411.10190 **[abstract]** In R^3, power maps of different degrees can be joined across round
    shells by a quasiregular map; Julia components that are round spheres. Gives us: gluing different rules by radius is
    legitimate mathematics, but it yields nested spheres, not buds.

## C. Is there a published 3D z^2 + c or 3D Mandelbrot set of this kind?

12. **Quasiregular dynamics on the n-sphere.** A. Fletcher, D. Nicks. Ergodic Theory Dynam. Systems 31 (2011);
    arXiv:0909.0217. https://arxiv.org/abs/0909.0217 **[text]** Theorem 1.1: a quasiregular map of polynomial type whose
    degree exceeds its inner dilatation K_I has a non-empty open escaping set with perfect boundary; Theorem 1.2: the
    escaping set is connected and the boundary is bounded and completely invariant. Sharp: the winding map
    (r, phi, y) -> (r, k phi, y) has degree k, K_I = k and nothing escapes. Theorem 2.2 (Martio): near a point of local
    index i, |f(y) - f(x)| <= C |y - x|^a with a = (i / K_I)^(1/(n-1)).
    Gives us: "pillow + c" (degree 4) has a well-defined bounded Julia-like boundary if its K_I < 4. Nobody draws it.
13. **Quasiregular mappings of polynomial type in R^2**, A. Fletcher, D. Goodman, arXiv:1006.0622; **An analogue of
    Green's functions for quasiregular maps**, Broderius, Fletcher, arXiv:2408.11256 **[snippets]**: Mandelbrot-like sets
    for squeezed quadratic maps, in the PLANE only. My searches found no paper that defines or draws a connectedness
    locus for "power map plus a constant" in R^3.
14. **Julia sets of Zorich maps**, A. Tsantaris, arXiv:2012.11053; **Explosion points and topology of Julia sets of Zorich
    maps**, arXiv:2107.13322 **[snippets]**: the 3D exponential family; hairs and "hairy surfaces"; no z^2 + c.
15. **New generalizations of quadratic Julia sets to 3D.** V. Kučera, Bridges 2019, 441-444.
    https://archive.bridgesmathart.org/2019/bridges2019-441.html (`notes/paper-kucera.txt`, **[text]**). The truly 3D
    construction is "so far unfortunately limited to c in R". No follow-up paper found by search.

## D. Stated obstructions

16. **Remarks on Martio's conjecture.** V. Tengvall, arXiv:2006.15101. https://arxiv.org/abs/2006.15101 **[text]**
    - Generalised Liouville theorem (Gehring 1962, Reshetnyak 1967): non-constant 1-quasiregular maps in dimension
      n >= 3 are restrictions of Möbius maps.
    - Martio, Rickman, Väisälä 1971: there is e(n) > 0 such that K_I(f) < 1 + e(n) forces a local homeomorphism.
    - Martio's conjecture (open): K_I < 2 forces a local homeomorphism for n >= 3. The m-to-1 winding map
      (r, theta, z) -> (r, m theta, z) branches on a line and has K_I = m.
17. **Zorich's theorem** (1967): a locally homeomorphic quasiregular map of R^n, n >= 3, is a homeomorphism.
    https://en.wikipedia.org/wiki/Zorich%27s_theorem , https://encyclopediaofmath.org/wiki/Zorich_theorem **[snippet]**
    Gives us: a bounded-squeeze 3D "square" MUST have branch lines. (Chernavskii: the branch set has topological
    dimension at most n - 2: lines in 3D, never isolated points; snippet.)
18. **On symmetry properties of quaternionic analogs of Julia sets.** A. Bogush et al., arXiv:nlin/0105060.
    https://arxiv.org/abs/nlin/0105060 **[snippet]** For the quadratic quaternion map the set is fixed by two numbers and
    is obtained by rotating a 2D Julia set: the quaternion square spins the flat set (the lab's Lathe).
19. **Mandelbulb, Mandelbrot, Mandelring and Hopfbrot.** O. Knill, 2023, arXiv:2305.17848
    https://arxiv.org/abs/2305.17848 ; https://mathworld.wolfram.com/Hopfbrot.html **[abstract, snippet]** The
    Hopf-coordinate power map lives in R^4; its 3D traces are the White-Nylander Mandelbulbs. Connectedness of
    Mandelbulbs is stated as open.
20. **Surgery on postcritically finite rational maps by blowing up an arc.** K. Pilgrim, Tan Lei, arXiv:math/9512221.
    https://arxiv.org/abs/math/9512221 **[snippet]** The operation used in construction K2 (`constructions.md`).
21. **Reformulating multiplication for Mandelbrot-like sets in 3D.** E. Zimmermann, S. Bruckner, Bridges 2025, 373-380.
    https://archive.bridgesmathart.org/2025/bridges2025-373.html **[text]** States "there is no analogue description in
    3-space"; experiments with a cross-product multiplication with two free coefficient functions. Art, not a carry-over.

Not read, only seen in result lists: "The inverse iteration method for Julia sets in the 3-dimensional space"
(arXiv:1311.6462); Fletcher, Stoertz, "Spiders' webs of doughnuts" (arXiv:1807.07166; Cantor Julia sets in R^3).
