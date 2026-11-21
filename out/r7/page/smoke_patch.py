"""Round 7: the changes to out/r4/page/make_smoke.py, applied once (the copy before is make_smoke.before.py).
A record, not a tool: make_smoke.py is the source. One check was added to make_smoke.py by hand afterwards (step 15:
coming in close on a solid of ordinary size must not show the sentence about a large radius)."""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'out', 'r4', 'page', 'make_smoke.py')
s = io.open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


# where --mine writes
rep("  python out/r4/page/make_smoke.py --mine     -> out/r5/page/smoke-mine.json, screenshots to out/r5/page/smoke/",
    "  python out/r4/page/make_smoke.py --mine     -> out/r7/page/smoke-mine.json, screenshots to out/r7/page/smoke/")
rep("SHOTS = 'out/r5/page/smoke/' if MINE else 'out/'", "SHOTS = 'out/r7/page/smoke/' if MINE else 'out/'")
rep("path = os.path.join(ROOT, 'out', 'r5', 'page', 'smoke-mine.json') if MINE", "path = os.path.join(ROOT, 'out', 'r7', 'page', 'smoke-mine.json') if MINE")

# helper: probes with the outer ring
rep("const hits = s => s.split('1').length - 1;\n",
    "const hits = s => s.split('1').length - 1;\n"
    "// 15 x 11 probes: [hits, hits on the outermost row or column]. A solid that is whole in the picture has (nearly) none on the ring.\n"
    "const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) if (L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11)) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } return [n, ring]; };\n")

# step 1: the first screen (layout-4)
rep("L.R.warmOn = false; L.S.q.aa = 3; L.touch();\nreturn 'default; sections: ' + order;",
    "const box = $('stage').getBoundingClientRect(), btn = $('reset').getBoundingClientRect();\n"
    "if (scrollY !== 0 || box.top < 0 || box.bottom > innerHeight || btn.bottom > innerHeight) fail('when the page opens the whole picture with its buttons should be on the first screen: picture ' + Math.round(box.top) + ' to ' + Math.round(box.bottom) + ' of ' + innerHeight);\n"
    "L.R.warmOn = false; L.S.q.aa = 3; L.touch();\nreturn 'default; picture at ' + Math.round(box.top) + ' to ' + Math.round(box.bottom) + ' of ' + innerHeight + '; sections: ' + order;")

# step 7: texts
rep("'Every rule has a mirror twin', 'the pictures match pixel for pixel', 'None of the three is Figure 4', 'It is not finished'])",
    "'Every rule has a mirror twin', 'the pictures match pixel for pixel', 'None of the three is Figure 4', 'It is not finished',\n"
    "  'shows the beads as separate discs', 'came out as one piece at every height that was tried', 'a tiny circle drawn on the ball is still a circle', 'like a cushion with a front and a back',\n"
    "  'the jump does not show', 'it is moved just far enough'])")
rep("for (const t of ['cannot be built from inversions', 'rebuilt by eye', 'the bounded piece that is left', 'sampling its derivative', 'pole phase'])",
    "for (const t of ['cannot be built from inversions', 'rebuilt by eye', 'the bounded piece that is left', 'sampling its derivative', 'pole phase', 'one smooth piece at every height', 'keeps angles true', 'wind it three times', 'hides the jump'])")
rep("if (!!$('powStep') === !!L.APPROACHES[L.S.approach].integerOnly)",
    "// the trap solid examples: a list right under \"In the 3D view the trap\", nine entries under three headings\n"
    "const ex = $('trapExamples');\n"
    "if (!ex || ex.options.length !== 10 || [...ex.querySelectorAll('optgroup')].map(g => g.label).join() !== 'Mandelbrot,Julia,Kleinian') fail('the Examples list should hold nine trap solids under Mandelbrot, Julia and Kleinian');\n"
    "if (!has('Examples') || $('exampleHost').previousElementSibling !== $('col-solid').closest('.field')) fail('the Examples list should stand right under In the 3D view the trap');\n"
    "if (!!$('powStep') === !!L.APPROACHES[L.S.approach].integerOnly)")

# step 15: the sentence for a large radius; Kleinian names fit
rep("document.querySelector('#kleinReset .dial-reset').click();\nif (!$('kleinWarn').hidden) fail('the warning should go when the values are back on an entry');\n",
    "document.querySelector('#kleinReset .dial-reset').click();\nif (!$('kleinWarn').hidden) fail('the warning should go when the values are back on an entry');\n"
    "// a turning-out sphere so large that the solid swallows the camera: a sentence says so, and goes from far enough away\n"
    "L.cam.dist = 7; L.touch(); type('kinvrNum', '3'); await sleep(250);\n"
    "if ($('kleinWarn').hidden || !$('kleinWarn').textContent.includes('grown past the camera')) fail('a turning-out radius of 3 fills the picture and the page should say so');\n"
    "L.cam.dist = 45; L.touch(); await sleep(250);\n"
    "if (!$('kleinWarn').hidden) fail('from far enough away the sentence about the large radius should go');\n"
    "type('kinvrNum', '1.5'); L.cam.dist = 7; L.touch(); await sleep(250);\n"
    "if (!$('kleinWarn').hidden) fail('a radius of 1.5 is whole in the picture and should not show the sentence');\n"
    "document.querySelector('#kleinReset .dial-reset').click();\n"
    "// every name can be read in the closed list\n"
    "const ks = $('kleinPreset'), kcs = getComputedStyle(ks), kc = document.createElement('canvas').getContext('2d');\n"
    "kc.font = kcs.fontWeight + ' ' + kcs.fontSize + ' ' + kcs.fontFamily;\n"
    "const long = [...ks.options].filter(o => kc.measureText(o.text).width > ks.clientWidth - parseFloat(kcs.paddingLeft) - parseFloat(kcs.paddingRight) - 18).map(o => o.text);\n"
    "if (long.length) fail('Kleinian names too long for the closed list: ' + long.join(' | '));\n")

# Show Figure 4: a far zoom limit and a drawing radius of the user's in the way
rep("$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absx').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');\nawait sleep(200);\n$('fig4Show').click(); await sleep(400);",
    "$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absx').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');\n"
    "L.S.view.zmax = 3; L.S.view.bound = 1.5; L.syncControls(); L.viewChanged();   // a far zoom limit and a drawing radius that would not let the solid fit\n"
    "await sleep(200);\n$('fig4Show').click(); await sleep(400);")
rep("if (bad.length) fail('Show Figure 4 did not set: ' + bad.join('; '));\n",
    "if (Math.abs(L.cam.dist - 4.8) > 0.05 || L.S.view.zmax < L.cam.dist || L.S.view.bound < 2) bad.push('the framing: camera at ' + L.cam.dist.toFixed(2) + ', far limit ' + L.S.view.zmax + ', drawing radius ' + L.S.view.bound);\n"
    "if (bad.length) fail('Show Figure 4 did not set: ' + bad.join('; '));\n")
rep("const two = probes();\nif (hits(two) < 5) fail('the picture of Figure 4 is empty: ' + hits(two) + ' of 49 probes hit');\n",
    "const two = probes(), whole = grid();\nif (hits(two) < 5) fail('the picture of Figure 4 is empty: ' + hits(two) + ' of 49 probes hit');\n"
    "if (whole[1] > 4) fail('the picture of Figure 4 is not whole in the frame: ' + whole[1] + ' probes hit on the outer ring');\n")
# the twins: a far limit in the way as well
rep("$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absy').click(); $('flipy').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');\nawait sleep(200);\n$('twinMerc').click(); await sleep(400);\ntwinState('Twin of Sphere inversions', 'mercator');",
    "$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absy').click(); $('flipy').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');\n"
    "L.S.view.zmax = 3; L.syncControls(); L.viewChanged();   // a far zoom limit that would not let the solid fit\n"
    "await sleep(200);\n$('twinMerc').click(); await sleep(400);\ntwinState('Twin of Sphere inversions', 'mercator');\n"
    "if (L.cam.dist < 5.5 || L.S.view.zmax < L.cam.dist) fail('the twin button did not stand back for the whole solid: camera at ' + L.cam.dist.toFixed(2) + ', far limit ' + L.S.view.zmax);")
rep("const twinPicture = name => { const h = hits(probes()); if (h < 5) fail('the picture of the twin of ' + name + ' is empty: ' + h + ' of 49 probes hit'); return h; };",
    "const twinPicture = name => { const h = hits(probes()), g = grid(); if (h < 5) fail('the picture of the twin of ' + name + ' is empty: ' + h + ' of 49 probes hit'); if (g[1] > 8) fail('the twin of ' + name + ' is not whole in the frame: ' + g[1] + ' probes hit on the outer ring'); return h; };")

# the examples: new steps before "24 collapse all"
EX = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'smoke_examples.txt'), encoding='utf-8').read()
rep("# 24 collapse all, also for the sections of the other modes\n", EX + "\n# 24 collapse all, also for the sections of the other modes\n")
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('make_smoke.py patched')
