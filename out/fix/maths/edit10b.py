# Second pass over src/js/10-approaches.js and 20-formula.js: shorter panel texts.
import io, sys
def edit(p, pairs):
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit('expected one match in %s for: %s' % (p, old[:70]))
        s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
edit('src/js/10-approaches.js', [
 ("one about each of n points spaced evenly round the unit circle, the results added together, then one more inversion of the sum. Swap the circles for spheres and the same recipe works on points in space. Cut the solid at z = 0 and the slice is exactly the ordinary 2D Mandelbrot or Julia set of the same power: the 2D view shows it. Slices at other heights are different shapes. Worked out, the recipe multiplies two angles by n: the longitude, and the latitude as a Mercator map stretches it (more and more toward the poles). It reproduces the Julia sets in Václav Kučera’s paper (Bridges 2019): one plane gives his inflated sets, two planes his fully 3D figure (the Julia set at c = (−1, 0, 0), seen straight down).',",
  "one about each of n points spaced evenly round the unit circle, the results added, then one more inversion of the sum. Swap the circles for spheres and the same recipe works in space. Cut the solid at z = 0 and the slice is exactly the ordinary 2D Mandelbrot or Julia set of the same power (the 2D view shows it). Slices at other heights are different shapes. Worked out, the recipe multiplies two angles by n: the longitude, and the latitude as a Mercator map stretches it. One plane gives the inflated sets in Václav Kučera’s paper (Bridges 2019), two planes his fully 3D figure.',"),
 ("text: 'The number of planes is a free choice: nothing in this rule fixes it, and it has nothing to do with the power. With p planes the solid has 2p fins around the x-axis, whatever n is. So the fins match the power only when p is half of n: 4 planes for n = 8, 3 for n = 6, 2 for n = 4. Fins always come in pairs, so an odd power has no exact match: the nearest choices give n − 1 or n + 1 fins. No value is the correct one. Kučera’s 3D figure uses 2 planes at n = 2, which is the starting value here.' },",
  "text: 'The number of planes is a free choice: nothing in this rule fixes it. With p planes the solid has 2p fins around the x-axis, whatever the power is, so fins and power match only when p is half of n (4 planes for n = 8, 3 for n = 6, 2 for n = 4). Fins come in pairs, so an odd power has no exact match. No value is the correct one. Kučera’s 3D figure uses 2 planes at n = 2, the starting value here.' },"),
 ("const APR_SLICE_TURNS = ' Away from 0 the slice at z = 0 is no longer the plain 2D picture: for the Mandelbrot solid it is that picture turned, for a Julia set it is a different set.';",
  "const APR_SLICE_TURNS = ' Away from 0 the slice at z = 0 is no longer the plain 2D picture: it is that picture turned (Mandelbrot) or a different set (Julia).';"),
 ("help: 'This approach’s version of the Mandelbulb’s longitude phase: added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis, and Julia sets change shape.' + APR_SLICE_TURNS },",
  "help: 'This approach’s version of the Mandelbulb’s longitude phase, added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis, and Julia sets change shape.' + APR_SLICE_TURNS },"),
])
edit('src/js/20-formula.js', [
 ("z0: 'c', target: [0, 0, 0], dist: 6.5, julia: { dist: 4.8 },", "z0: 'c', target: [0, 0, 0], dist: 6.5,"),
])
print('ok')
