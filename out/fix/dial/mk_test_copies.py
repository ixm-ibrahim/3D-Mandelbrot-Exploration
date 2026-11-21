"""Throwaway copies of three files the dial group does not own, with the "other side" of the dial fixes filled in,
so the kit can be tried inside the lab before the page and the approaches engineers do their part:

  t-10-approaches.js   the Lift spec plays there and back (animate: 'bounce') and has a wide range
  t-80-ui.js           an "Extreme values" checkbox in the top row; wide ranges on Iterations, Depth of the search,
                       Ray steps and the Julia c dials
  t-90-boot.js         setExtreme and isExtreme on window.squaringLab

Build:  python build.py --name fix-dial-x --base base2 --use src/js/70-dial.js src/css/70-dial.css
            --swap js/10-approaches.js=out/fix/dial/t-10-approaches.js js/80-ui.js=out/fix/dial/t-80-ui.js js/90-boot.js=out/fix/dial/t-90-boot.js
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def copy(name, edits):
    s = io.open(os.path.join(ROOT, 'base2', 'js', name), encoding='utf-8').read()
    for old, new in edits:
        assert s.count(old) == 1, (name, s.count(old), old[:60])
        s = s.replace(old, new)
    io.open(os.path.join(HERE, 't-' + name), 'w', encoding='utf-8', newline='\n').write(s)
    print('wrote t-' + name)


copy('10-approaches.js', [
    ("key: 'lift', label: 'Lift toward the pole', min: -2, max: 2, step: 0.01, def: 0, lo: -6, hi: 6, animate: true,",
     "key: 'lift', label: 'Lift toward the pole', min: -2, max: 2, step: 0.01, def: 0, lo: -6, hi: 6, xmin: -6, xmax: 6, xlo: -20, xhi: 20, animate: 'bounce',"),
])
copy('80-ui.js', [
    ("addCheck('flatHost', 'flat',",
     "addCheck('flatHost', 'extreme', 'Extreme values', isExtreme, setExtreme, { def: false });\n  addCheck('flatHost', 'flat',"),
    ("{ hi: 400, int: true, def: 14, group: 'eq' }", "{ hi: 400, xmax: 1000, xhi: 100000, int: true, def: 14, group: 'eq' }"),
    ("kd('kiter', 'Depth of the search', 5, 150, 1, 'iter', { hi: 400, int: true });",
     "kd('kiter', 'Depth of the search', 5, 150, 1, 'iter', { hi: 400, xmax: 2000, xhi: 100000, int: true });"),
    ("'steps', { lo: 20, hi: 3000, int: true }", "'steps', { lo: 20, hi: 3000, xmax: 5000, int: true }"),
    ("{ lo: -8, hi: 8, def, group: 'julia' }", "{ lo: -8, hi: 8, xlo: -100, xhi: 100, def, group: 'julia' }"),
])
copy('90-boot.js', [
    ("resetGroup, JULIA_PRESETS,", "resetGroup, setExtreme, isExtreme, JULIA_PRESETS,"),
])
