"""Round 22, entry: the two entries at the end of APPROACHES, one wording fix in the texts. Run once."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(P, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old)
    s = s.replace(old, new)
rep('between 30 and 300 steps before it settles', 'between 30 and 200 steps before it settles')
OLD = """    slice: (ok, p, n = S.n) => wsSlice(ok, n),
  },
];"""
NEW = """    slice: (ok, p, n = S.n) => wsSlice(ok, n),
  },
  // ----- Round 22: the two near misses of round 21, each an entry of its own. They are the first entries whose orbit
  // carries something besides its point (CARRY, GL_CARRY). Both are built from Sphere inversions, one plane, so they
  // stand in its group, at the end of this list so that the entries before them keep their places. What their texts
  // say was measured in out/r21/judge/ (the rules alongmem.c_wake1 and sheet.evc005e70k16) and in out/r22/entry/.
  {
    id: 'alongonce', name: 'Along once, then one plane', group: 'inversions', glsl: GL_ALONGONCE, axis: () => [1, 0, 0], deMax: 0,
    tag: AO_TAG,
    params: [{ type: 'note', text: AO_NOTE }],
    formula: (p, n) => aoFormula(n),
    about: AO_ABOUT,
    roundNote: () => AO_CARD + TP_ROUND + AO_LATER + ', which keeps circles on the sphere as circles.',
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : ['part', AO_CARD + TP_CRUSH_ALONG + AO_LATER + ', which crushes the z-axis only.' + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', AO_CARD + TP_SMOOTH + (aprWhole(n) ? '' : TP_SMOOTH_OTHER) + aprTear(n, APR_HALF) + ' The rule changes after the first squaring, so an orbit is not one formula applied again and again.']),
    slice: (ok, p, n = S.n) => aoSlice(ok),
  },
  {
    id: 'pulledplane', name: 'Pulled plane', group: 'inversions', glsl: GL_PULLEDPLANE, axis: () => [1, 0, 0], deMax: 0,
    tag: PP_TAG,
    params: [
      { type: 'note', text: PP_NOTE },
      { type: 'dial', key: 'hold', label: 'Hold of the flat page at the start', min: 0, max: 1, step: 0.01, def: 0.05, xmax: 4, xhi: 100, help: PP_HELP_HOLD },
      { type: 'dial', key: 'ease', label: 'Ease of a pull', min: 0, max: 1, step: 0.01, def: 0.7, help: PP_HELP_EASE },
      { type: 'dial', key: 'cpull', label: 'Pull of c, times', min: 0, max: 64, step: 0.5, def: 16, xmax: 256, xhi: 10000, help: PP_HELP_CPULL },
    ],
    formula: (p, n) => ppFormula(p, n),
    about: PP_ABOUT,
    roundNote: () => PP_ROUND,
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : ['part', PP_CRUSH + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : ['no', ppSmooth(p, n)]),
    slice: (ok, p, n = S.n) => ppSlice(ok),
  },
];"""
rep(OLD, NEW)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
