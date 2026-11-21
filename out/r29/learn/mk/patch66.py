# Round 29: 66-learn-view.js. Show gets "A grid of points"; the third choice is renamed by space; the help is
# rewritten; one line under the select says what the extra points are. With the three old choices nothing that is
# drawn changes.
import sys
sys.dont_write_bytecode = True
from patchlib import Patch, frag

p = Patch('js/66-learn-view.js')

# the state: one more value of `show`
p.rep("  show: 'circle',                // 'point' | 'circle' | 'all': the companions\n",
      "  show: 'circle',                // 'point' | 'circle' | 'all' | 'grid': the extra points ('grid', round 29, is not laid out afresh)\n")

# the helpers, before the plan
p.before("// ---------- the plan: the moves of the step on show, and everything the picture needs from them\n", frag('66-grid.js'))

# the grid goes through the steps taken so far, as the point does
p.rep("  const orbit = [P.z.slice()];\n  while (orbit.length <= L.k && moves.length) {\n    const a = orbit[orbit.length - 1], r = run(a), e = r[r.length - 1];\n    if (len(e) > 8) break;\n    orbit.push(e);\n",
      "  const orbit = [P.z.slice()];\n"
      "  // (round 29) Show: A grid of points. These dots are not laid out afresh: like the point itself, each goes on from\n"
      "  // where the last step left it, through the same moves (for an entry whose orbit carries something: the moves of the\n"
      "  // point's own steps, as for every extra point). Worked out again from the fresh grid, as the point's steps are.\n"
      "  const gridStart = L.show === 'grid' ? learnVGridPoints(sp) : null;\n"
      "  let grid = gridStart;\n"
      "  while (orbit.length <= L.k && moves.length) {\n    const a = orbit[orbit.length - 1], r = run(a), e = r[r.length - 1];\n    if (len(e) > 8) break;\n    orbit.push(e);\n"
      "    if (grid) grid = grid.map(v => { const q = run(v); return q[q.length - 1]; });\n")

# the grid as the extra points of the step on show
p.rep("      follow.push(40, 110, 190, 260);\n    }\n  }\n  const comp = [base];\n",
      "      follow.push(40, 110, 190, 260);\n    }\n  } else if (grid) {\n"
      "    for (const v of grid) base.push(v);\n"
      "    for (const i of learnVGridMarked(gridStart, sp)) follow.push(i);\n"
      "  }\n  const comp = [base];\n")

# the frame holds the big circle the grid is laid over, and does not grow for dots that go far off
p.rep("    comp[0].forEach(v => see(v, 4)); comp[comp.length - 1].forEach(v => see(v, 4));\n",
      "    if (grid) { for (let i = 0; i < sp; i++) for (const s of [-2, 2]) { const v = [0, 0, 0]; v[i] = s; key.push(v); } }      // (round 29)\n"
      "    else { comp[0].forEach(v => see(v, 4)); comp[comp.length - 1].forEach(v => see(v, 4)); }\n")

# kept for the drawing: where the grid's dots started (their colours come from there)
p.rep("    moves, pts, paths, say, orbit, comp, follow, at, fault, away, end, sheets,\n",
      "    moves, pts, paths, say, orbit, comp, follow, at, fault, away, end, sheets, gridStart, gridCol: null, gridDark: null,\n")

# the drawing of the grid
p.rep("    } else {\n      const hues = [C.ok, C.bad, C.ink, C.warn];\n",
      frag('66-griddraw.js') + "    } else {\n      const hues = [C.ok, C.bad, C.ink, C.warn];\n")

# the words of the select follow the space; the line under it
p.rep("  for (const r of el.spaces) r.checked = +r.value === L.space;\n}\n// ---------- the clock: one frame redoes what is stale",
      "  for (const r of el.spaces) r.checked = +r.value === L.space;\n  learnVShowPaint();      // (round 29) the choices of Show, its help and the line under it\n}\n// ---------- the clock: one frame redoes what is stale")

# the select itself
p.rep("    { type: 'select', key: 'show', label: 'Show', def: 'circle', options: [['point', 'The point alone'], ['circle', 'A small circle round the point'], ['all', 'All directions at once']],\n"
      "      help: 'The companions take the same moves as the point, each by its own amount, so they show what a move does to everything near the point and not only to the point. On a line the circle is a short row of dots, and all directions is a row of dots along the line.' },\n"
      "  ], store, () => learnVChanged(), { idPrefix: 'learn-', group: 'learn' });\n",
      "    // (round 29: a fourth choice, the third named by what it is in the space on show, and a help that says what a\n"
      "    // direction is and which of the extra points are laid out afresh; see learnVShowOptions and learnVShowHelp)\n"
      "    { type: 'select', key: 'show', label: 'Show', def: 'circle', options: learnVShowOptions(L.space), help: learnVShowHelp(L.space) },\n"
      "  ], store, () => learnVChanged(), { idPrefix: 'learn-', group: 'learn' });\n"
      "  // one line under the select: what the extra points are right now, and whether they are laid out afresh\n"
      "  L.showCtl = L.dials.controls.find(c => c.id === 'learn-show') || null; L.showSig = L.space;\n"
      "  el.showLine = make('p', 'note learn-show-line'); el.showLine.id = 'learnShowLine'; el.showLine.hidden = true;\n"
      "  { const sel = el.panel.querySelector('#learn-show'), field = sel ? sel.closest('.field') : null; if (field) field.after(el.showLine); else el.panel.querySelector('#learnDials').appendChild(el.showLine); }\n")

# the test handle
p.rep("  if (o.show !== undefined && ['point', 'circle', 'all'].includes(o.show)) L.show = o.show;\n",
      "  if (o.show !== undefined && ['point', 'circle', 'all', 'grid'].includes(o.show)) L.show = o.show;\n")
p.rep("LEARN.reset = () => learnReset();\n",
      "LEARN.reset = () => learnReset();\n"
      "// (round 29) points(): the extra points of the step on show. start: where the first step found them (for the grid:\n"
      "// the fresh grid, before any step); now: where they are at this moment of the step; afresh: are they laid out anew\n"
      "// at every step; marked: the ones drawn larger; line: the sentence under the select Show.\n"
      "LEARN.points = () => {\n"
      "  const L = LEARN;\n"
      "  if (L.stale || !L.cache) learnVBuild();\n"
      "  const K = L.cache, a = learnVAt(), m = K.moves[a.j];\n"
      "  const now = !K.comp[0].length || !m ? K.comp[0] : a.t >= 1 ? K.comp[a.j + 1] : a.t <= 0 ? K.comp[a.j] : K.comp[a.j].map(v => K.at(m, v, a.t));\n"
      "  return { show: L.show, space: L.space, step: L.k, afresh: L.show !== 'grid', start: (K.gridStart || K.comp[0]).map(v => v.slice()), stepStart: K.comp[0].map(v => v.slice()),\n"
      "    now: now.map(v => v.slice()), end: K.comp[K.comp.length - 1].map(v => v.slice()), marked: K.follow.slice(), line: learnVShowLine(),\n"
      "    options: learnVShowOptions(L.space).map(o => o[1]), help: learnVShowHelp(L.space) };\n"
      "};\n")
p.write()
