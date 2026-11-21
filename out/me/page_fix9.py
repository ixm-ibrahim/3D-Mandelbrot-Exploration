"""Page fixes after the second check (orchestrator): t9-words-1, -2, -3, t9-solids-1, t9-dials-1, t9-kleinian-2.

Run once from the project root: python out/me/page_fix9.py
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def patch(rel, pairs):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding='utf-8').read()
    for a, b in pairs:
        if b in s and a not in s:
            continue                       # already done
        assert s.count(a) == 1, '%s: expected one place for: %s' % (rel, a[:90])
        s = s.replace(a, b)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('patched', rel)


# ---- closing text
patch('src/body.html', [
    # t9-words-1: the condition under which flip z leaves a Julia set alone
    ("For Sphere inversions and the Lathe, a Julia set whose c lies in that plane does not change at all: the pictures match pixel for pixel.",
     "For the Lathe, and for Sphere inversions with its dials at their starting values (Planes 1, Turn 0, Lift 0), a Julia set whose c lies in that plane does not change at all: the pictures match pixel for pixel."),
    # t9-words-2: what the twin's slices really keep
    ("Under Sphere inversions the thin lens becomes a tall body, and its slices keep the outline of the Mandelbrot set far above the plane.",
     "Under Sphere inversions the thin lens becomes a tall body, and its slices keep a smoothed outline of the Mandelbrot set up to about half its height, where the slice of the plain rule is already a round disc and soon after that empty."),
    # t9-words-3: two of the fifteen entries also switch the third map off
    ("They keep groups that were already in the list and move only the sphere.",
     "They keep the μ of groups that were already in the list and move the sphere. Two of them, the 1/3 cusp entries, also switch the third map off."),
])

# ---- examples put the trap centre back (t9-solids-1); the Drawing radius sentence stands on its own (t9-kleinian-2)
patch('src/js/75-presets.js', [
    ("const EXAMPLE_KEYS = ['trap', 'solid', 'thick', 'skip', 'radius'];   // the fields of S.colour an example sets",
     "const EXAMPLE_KEYS = ['trap', 'solid', 'thick', 'skip', 'radius'];   // the fields of S.colour an example sets\n"
     "const EXAMPLE_CENTRE = ['tx', 'ty', 'tz'];   // the trap centre: every example puts it back to the middle, where its picture was chosen"),
    ("  return EXAMPLE_KEYS.every(key => presetSame(S.colour[key], e[key]));\n}",
     "  return EXAMPLE_KEYS.every(key => presetSame(S.colour[key], e[key])) && EXAMPLE_CENTRE.every(key => presetSame(S.colour[key], 0));\n}"),
    ("  EXAMPLE_KEYS.forEach(key => { S.colour[key] = e[key]; });\n  presetCam(",
     "  EXAMPLE_KEYS.forEach(key => { S.colour[key] = e[key]; });\n  EXAMPLE_CENTRE.forEach(key => { S.colour[key] = 0; });\n  presetCam("),
    ("      + (kleinReach() > S.view.bound ? ' The solid now also reaches past the Drawing radius in the View section, so from further away only its middle is drawn until that is raised too.' : ''));\n  }",
     "      + (kleinReach() > S.view.bound ? ' The solid now also reaches past the Drawing radius in the View section, so from further away only its middle is drawn until that is raised too.' : ''));\n  }\n"
     "  // from further away the same solid is no longer in the camera's way, and that is when the cut shows\n"
     "  else if (S.mode === 'k' && !S.flat && kleinReach() > S.view.bound) out.push('The solid reaches past the Drawing radius in the View section, so only its middle is drawn. Raise the Drawing radius to see all of it.');"),
])

patch('src/js/80-ui.js', [
    ("uiOnce('klein', JSON.stringify(S.k) + (kleinSwallowed() ? (kleinReach() > S.view.bound ? '|near, cut' : '|near') : ''), uiKleinMark);",
     "uiOnce('klein', JSON.stringify(S.k) + (kleinSwallowed() ? '|near' : '') + (kleinReach() > S.view.bound ? '|cut' : ''), uiKleinMark);"),
    ("`${S.mode}|${S.c}|${JSON.stringify(S.k)}|${EXAMPLE_KEYS.map(key => S.colour[key])}`",
     "`${S.mode}|${S.c}|${JSON.stringify(S.k)}|${[...EXAMPLE_KEYS, ...EXAMPLE_CENTRE].map(key => S.colour[key])}`"),
    ("the trap shape, what the trap does, its thickness, skipped steps and radius, and the camera. Everything else stays as you left it,",
     "the trap shape, what the trap does, its thickness, skipped steps and radius, the trap centre (back to the middle), and the camera. Everything else stays as you left it,"),
    # t9-dials-1: Reset everything also puts the two save panels' settings back (a job that is running keeps its own copy)
    ("  resetGroup(UI_GROUPS);\n  S.cutOn = false;",
     "  resetGroup(UI_GROUPS);\n  resetGroup(['export', 'mesh']);   // the settings of the two save panels; a job that is running keeps its own copy\n  if (typeof exportSizeNote === 'function') exportSizeNote();\n  S.cutOn = false;"),
])
print('done')
