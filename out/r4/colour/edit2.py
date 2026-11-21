"""Second one-off edit of src/js/25-colour.js: on a trap solid the fine layers take the nearness colour (not the
palette's mean) when a nearness choice is on, and the starting point of a Julia orbit can be the step that touched."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '25-colour.js')
s = open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


rep('''// The colour an orbit trap gives, from the captured values. back and depth: see colPick.
vec3 colTrapPick(float back, float depth){''', '''// The colour an orbit trap gives, from the captured values. p: the point being coloured. back and depth: see colPick.
vec3 colTrapPick(vec3 p, float back, float depth){''')
i = s.index('  // The trap makes the solid, or part of it. Step, side and place are read from the step that touched the trap.')
j = s.index('// The colour for every mode that reads the palette (uColMode <= 5), from the captured values.')
s = s[:i] + '''  // The trap makes the solid, or part of it. Step, side and place are read from the step that touched the trap.
  vec4 touch = cTouch; float touchIt = cTouchIt, touchStr = cTouchStr;
  if (uTrapSkip == 0 && uColJulia > 0.5){
    // A Julia orbit starts at the point itself, which trapAdd never sees: with no steps skipped the trap shape
    // is part of the solid, touched at step 0. The scores of the later steps lack the stretch of the first step.
    float d0 = trapDist(p), first = clamp(abs(uPow) * pow(max(length(p), 1e-9), uPow - 1.0), 1e-9, 1e9);
    if (d0 - uTrapW < cTouchS / first){ touch = vec4(p - uTrapC, d0); touchIt = 0.0; touchStr = 1.0 / first; }
  }
  vec3 place = pal(uTrapBy == 1 ? 0.23 * touchIt : uTrapBy == 3 ? colSide(touch.xyz) : colWhere(touch.xyz));
  // Close to the set the solid is layer upon layer, each a share 1 / stretch of the thickness across. Once a
  // layer is thinner than a pixel or two its own colours can only sparkle. (A pixel is taken to be about 0.0015
  // of the distance from the camera across, which is right for the usual picture and only has to be roughly so.)
  float fine = smoothstep(0.5, 1.5, 0.0015 * max(depth, 0.0) * touchStr / max(uTrapW, 1e-6));
  // Step, side and place give way there to what such a pixel would average out to: the mean of the palette.
  if (uTrapBy == 1 || uTrapBy == 3 || uTrapBy == 5) return mix(place, uPalMean, fine);
  // The choices by nearness. Nearness is the same all over the trap's part of the solid, so that part shows
  // the place it was touched instead, and nearness is left to the rest, where it does vary: the fine layers,
  // and the set's own surface when the trap was added to it. On the trap's part the step that touched lies
  // within the thickness (a little more where the picture is fine).
  t = uTrapBy == 2 ? band - 0.1 * back : uTrapBy == 4 ? 0.15 + 0.85 * exp(-2.4 * pow(uGlowK * s, uGlowP)) : band;
  return mix(place, pal(t), max(fine, smoothstep(1.5, 2.5, touch.w / max(uTrapW, 1e-6))));
}
''' + s[j:]
rep('  if (uColMode <= 1) return colTrapPick(back, depth);', '  if (uColMode <= 1) return colTrapPick(p, back, depth);')
rep('  if (uInMode == 1) c = colTrapPick(-cIt, -1.0);', '  if (uInMode == 1) c = colTrapPick(p, -cIt, -1.0);')
rep('float gStr, cStr, gLogS, cLogS, gSteps, cSteps; vec3 cLast; bool gColIn = false;', 'float gStr, cStr, gLogS, cLogS, gSteps, cSteps, cTouchS; vec3 cLast; bool gColIn = false;')
rep('cTouch = gTouch; cTouchIt = gTouchIt; cTouchStr = gTouchStr; cStr = gStr;', 'cTouch = gTouch; cTouchIt = gTouchIt; cTouchStr = gTouchStr; cTouchS = gTouchS; cStr = gStr;')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
