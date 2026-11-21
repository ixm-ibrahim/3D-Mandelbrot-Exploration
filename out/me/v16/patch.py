"""Version 16 join (idempotent). Run from the workspace root: python out/me/v16/patch.py
1. 40-render.js: an entry may cap the distance estimate (deMax). The two turning-plane entries set it to 0 (Rough),
   because the other two estimates draw fog (away) or false sheets (along) for them.
2. 10-approaches.js: deMax on both entries; their notes say what the page now does; the 'along' text says what the
   point-by-point cuts of out/me/r16/truth2.py show between the planes (thin fins and tufts of hair)."""
import io, sys

def sub(s, old, new, name, count=1):
    if new in s and old not in s:
        print('  already:', name); return s
    if s.count(old) != count:
        sys.exit(f'PATCH FAILED ({name}): found {s.count(old)} times, wanted {count}')
    print('  done:', name)
    return s.replace(old, new)

p = 'src/js/40-render.js'
s = io.open(p, encoding='utf-8').read()
s = sub(s,
        "function sceneDe(q = S.q) { const d = q.de === undefined ? 3 : +q.de; return d >= 3 ? 3 : d >= 1 ? 1 : 0; }",
        "// An entry may cap the estimate (deMax): for some rules the finer estimates draw things that are not there.\n"
        "function sceneDeCap() { const a = typeof APPROACHES !== 'undefined' && S ? APPROACHES[S.approach] : null; return a && a.deMax !== undefined ? a.deMax : 3; }\n"
        "function sceneDe(q = S.q) { const d = Math.min(q.de === undefined ? 3 : +q.de, sceneDeCap()); return d >= 3 ? 3 : d >= 1 ? 1 : 0; }",
        'render: deMax cap')
io.open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'src/js/10-approaches.js'
s = io.open(p, encoding='utf-8').read()
s = sub(s, "id: 'turnaway', name: 'Turning plane, away', group: 'inversions', glsl: GL_TURNAWAY, axis: () => [1, 0, 0],",
        "id: 'turnaway', name: 'Turning plane, away', group: 'inversions', glsl: GL_TURNAWAY, axis: () => [1, 0, 0], deMax: 0,", 'away deMax')
s = sub(s, "id: 'turnalong', name: 'Turning plane, along', group: 'inversions', glsl: GL_TURNALONG, axis: () => [1, 0, 0],",
        "id: 'turnalong', name: 'Turning plane, along', group: 'inversions', glsl: GL_TURNALONG, axis: () => [1, 0, 0], deMax: 0,", 'along deMax')
s = sub(s, "const TP_ROUGH = 'Set “Distance estimate”, under Quality and speed, to “Rough” to see this rule in 3D.';",
        "const TP_ROUGH = 'The lab always draws this rule with “Distance estimate” at “Rough”, whatever that setting says. Raise Iterations to 40 or more to see the bodies come apart: at 14 they are still joined by necks and look ribbed.';",
        'TP_ROUGH')
s = sub(s, "const TP_NOTE_AWAY = TP_ROUGH + ' With “Exact”, the setting the page opens with, the 3D picture of this rule is wrong: it shows a streaked spindle of fog where the solid is a row of bodies (checked against cuts worked point by point). Measured",
        "const TP_NOTE_AWAY = TP_ROUGH + ' With “Exact” the 3D picture of this rule would be wrong: a streaked spindle of fog where the solid is a row of bodies (checked against cuts worked point by point). Measured",
        'note away')
s = sub(s, "const TP_NOTE_ALONG = 'Measured at power 2:",
        "const TP_NOTE_ALONG = TP_ROUGH + ' Measured at power 2:", 'note along head')
s = sub(s, "With “Distance estimate” at “Exact”, the setting the page opens with, the 3D picture can show a thin flat sheet in the planes y = z and y = −z beside the points where two bodies touch. That sheet is not part of the solid (points on it were tested one by one), and “Rough” does not draw it. At a whole power n, 2n planes",
        "With “Exact” the 3D picture would show a thin flat sheet in the planes y = z and y = −z beside the points where two bodies touch. That sheet is not part of the solid (points on it were tested one by one). At a whole power n, 2n planes",
        'note along sheet')
s = sub(s, "Where it falls short: the buds are ribbed, with spiky crowns, not smooth round bodies. The rule also folds",
        "Where it falls short: between the four planes the skin is smooth only from a distance. Cuts worked point by point at 80 steps show thin fins and tufts of hair standing on it there, and the buds have spiky crowns. The rule also folds",
        'about along')
s = sub(s, "const TP_TAG_ALONG = 'Square each point by the one-plane rule about a plane that turns with the point. Four planes carry the flat set and nothing tears. For c = −1 it gives separate bodies with buds in eight directions and smaller buds on those, but the Mandelbrot solid is a lumpy rock with no bulbs.';",
        "const TP_TAG_ALONG = 'Square each point by the one-plane rule about a plane that turns with the point. Four planes carry the flat set and nothing tears. For c = −1 it gives separate bodies with buds in eight directions and smaller buds on those, with thin fins and hair between the planes close up. The Mandelbrot solid is a lumpy rock with no bulbs.';",
        'tag along')
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
