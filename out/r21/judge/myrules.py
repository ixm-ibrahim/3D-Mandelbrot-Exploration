"""Round 21, agent "judge": the rules under judgment, taken from the four searchers' folders, plus the two bench rules.

Nothing new is defined here. Each searcher's myrules.py is loaded under its own module name (they are all called
myrules.py) and the rules the searcher itself picked are wrapped with a prefix that says whose they are.

    import sys; sys.path.insert(0, 'out/r21/judge'); import myrules as J
    J.RULES            the ten rules that are judged, 'along' first
    J.get('sheet.evc005e70k16')

Definitions in full are in out/r21/judge/NOTES.md.
"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
R21 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(R21, 'lib'))
import mem as M


def load(folder):
    spec = importlib.util.spec_from_file_location('rules_' + folder, os.path.join(R21, folder, 'myrules.py'))
    mod = importlib.util.module_from_spec(spec); sys.modules['rules_' + folder] = mod; spec.loader.exec_module(mod)
    return mod


SHEET, ALONGMEM, SPAN, FRAME = load('sheet'), load('alongmem'), load('span'), load('frame')


def pick(mod, name):
    rules = list(getattr(mod, 'RULES'))
    return next(r for r in rules if r.name == name)


def wrap(r, name, label, plain):
    q = M.Rule(name, label, r.step, r.init); q.plain = plain; return q


_along = M.bench('along'); _one = M.bench('oneplane'); _lathe = M.bench('lathe')
ALONG = wrap(_along, 'along', 'bench: one-plane rule about a sheet that turns with the point (sin 4 phi), no memory',
             'Best so far ("Turning plane, along")')
ONEPLANE = wrap(_one, 'oneplane', 'bench: the one-plane rule, the sheet never moves', 'One fixed plane (the flat page)')
LATHE = wrap(_lathe, 'lathe', 'bench: every point squared in its own sheet (rings)', 'The flat set spun round (rejected)')

RULES = [
    ALONG,
    ONEPLANE,
    wrap(pick(SHEET, 'evc005e70k16'), 'sheet.evc005e70k16', 'sheet: eased votes; the point and c (16-fold) vote for the carried sheet',
         'The plane is voted on by every orbit point and by c'),
    wrap(pick(SHEET, 'ease'), 'sheet.ease', 'sheet: the sheet turns by d - sin(2d)/2 toward the point, then the one-plane square',
         'The plane jumps to a point that stands square to it'),
    wrap(pick(ALONGMEM, 'c_wake1'), 'alongmem.c_wake1', 'alongmem: first squaring is along, every later one the one-plane rule',
         'First step "along", then one fixed plane'),
    wrap(pick(ALONGMEM, 'c_wake2'), 'alongmem.c_wake2', 'alongmem: first two squarings are along, every later one the one-plane rule',
         'First two steps "along", then one fixed plane'),
    wrap(pick(SPAN, 'c_lag10'), 'span.c_lag10', 'span: one-plane rule about a plane that moves a tenth of the way to the plane of the point and c',
         'The plane leans a tenth of the way to the plane of the point and c'),
    wrap(pick(SPAN, 'c_page'), 'span.c_page', 'span: the point squared inside the plane of the point and c (the literal reading, partner c)',
         'Each point squared in the plane it makes with c'),
    wrap(pick(FRAME, 'area_1_px'), 'frame.area_1_px', 'frame: the page tips toward the plane of the last step, counted by the area it sweeps',
         'The plane leans toward the plane of the last step'),
    wrap(pick(FRAME, 'orb_inf_px'), 'frame.orb_inf_px', 'frame: the page IS the plane of the last two orbit points (the literal reading)',
         'The plane IS the plane of the last two orbit points'),
]
EXTRA = [LATHE, wrap(pick(SPAN, 'c_lag25'), 'span.c_lag25', 'span: as c_lag10 with a quarter of the way', 'quarter of the way'),
         wrap(pick(SHEET, 'vote4'), 'sheet.vote4', 'sheet: plain votes, flat page strength 4', 'plain votes')]


def get(name):
    return next(r for r in RULES + EXTRA if r.name == name)
