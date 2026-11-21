# Round 29: 67-learn-shape.js. "Each step: At once | Move by move" and "Dots: Few | Some | Many".
# With At once every call that draws or writes gets what it got before (the new arguments are null or undefined).
import sys
sys.dont_write_bytecode = True
from patchlib import Patch, frag

p = Patch('js/67-learn-shape.js')

# ----- the header and the state
p.rep("// learnShapeInit. With Follow = One point nothing here draws or listens.\n",
      "// learnShapeInit. With Follow = One point nothing here draws or listens.\n"
      "// (Round 29.) \"Each step: Move by move\" lays dots over the pictures and plays the moves inside each step on them;\n"
      "// \"At once\" is the behaviour described here, unchanged. See the part \"Each step: Move by move\" below.\n")
p.rep("  kind: 'm',                     // 'm' Mandelbrot shape | 'j' Julia shape | 'both'\n",
      "  kind: 'm',                     // 'm' Mandelbrot shape | 'j' Julia shape | 'both'\n"
      "  each: 'moves',                 // (round 29) 'once': a step shows only what it leaves | 'moves': the moves inside it, played on dots\n"
      "  dots: 'some',                  // 'few' | 'some' | 'many': how close the dots lie (LEARN_SHAPE_SPACING)\n"
      "  D: {},                         // D[kind]: the kept dots of that picture (learnShapeDots)\n"
      "  mv: { sig: null, moves: [], names: [], chips: [], keys: [] },   // the kept moves of one step (learnShapeMoves)\n"
      "  endSide: false,                // at the joint of two parts: stand at the end of the part before (a play of one part stopped there)\n"
      "  sig3: '', res3: null,          // what the 3D picture last drew, so that the same glass is not drawn twice (learnShapeSolid)\n")
p.rep("  ms: { frame: 0, map: 0, fill: 0, three: 0, mapLast: 0, mapSamples: 0, mapDens: 0 },\n",
      "  // (round 29) dots: the part of a redraw spent on the dots of Move by move\n"
      "  ms: { frame: 0, map: 0, fill: 0, three: 0, mapLast: 0, mapSamples: 0, mapDens: 0, dots: 0 },\n")

# ----- the new part, before the words
p.before("// ---------- the words\nfunction learnShapeWords() {\n", frag('67-moves.js') + "\n")

# ----- the words
p.rep("  const calm = Sh.playing && Sh.until === null && Sh.pos > 1e-9, pics = kind === 'both' ? 's' : '';\n",
      "  // (round 29) with \"Each step: Move by move\" every part of a step has its own sentence, also while the steps play\n"
      "  const mvOn = learnShapeMovesOn();\n"
      "  const calm = !mvOn && Sh.playing && Sh.until === null && Sh.pos > 1e-9, pics = kind === 'both' ? 's' : '';\n")
p.rep("  const where = whole ? `Step ${k} of ${N}: <b>${k === 0 ? 'the start' : 'what is left'}</b>` : `Step ${k + 1} of ${N}: <b>under way</b>`;\n"
      "  const read = whole ? (k === 0 ? 'the start' : `after ${k} step${k === 1 ? '' : 's'}`) : `step ${k + 1}`;\n"
      "  return { say, where, read, k, u, whole };\n",
      "  // (round 29) Move by move: between two whole steps the words are those of the part being played (unless nothing\n"
      "  // at all is left of the pictures: then the sentence above says so)\n"
      "  let part = null;\n"
      "  if (mvOn && !whole && k < N && !gone) { part = learnShapePartWords(k, learnShapePart(u)); say = part.say; }\n"
      "  const where = whole ? `Step ${k} of ${N}: <b>${k === 0 ? 'the start' : 'what is left'}</b>` : `Step ${k + 1} of ${N}: <b>${part ? part.label : 'under way'}</b>`;\n"
      "  const read = whole ? (k === 0 ? 'the start' : `after ${k} step${k === 1 ? '' : 's'}`) : part ? `step ${k + 1}: ${part.label}` : `step ${k + 1}`;\n"
      "  return { say, where, read, k, u, whole, part };\n")

# ----- the flat picture
p.rep("function learnShapeTint(M, k, u) {\n",
      "function learnShapeTint(M, k, u, keep) {\n"
      "  // (round 29) keep: Move by move draws the same backdrop frame after frame; when the canvas already holds the\n"
      "  // colours of this very picture they are not worked out again\n"
      "  if (keep) { const sig = [k, u, M.key, M.dens].join('|'), of = learnShapeCols(); if (M.tint === sig && M.tintOf === of) return; M.tint = sig; M.tintOf = of; } else M.tint = '';\n")
p.rep("function learnShapeFlat(g, P, k, u, quality, C, label, small) {\n",
      "// (Round 29.) mv: null with \"Each step: At once\"; with Move by move { k, ph, back }: the step the dots are at, the\n"
      "// part being played (null at a whole step) and how strongly the picture shows behind the dots. k and u are then\n"
      "// what the picture of starting places shows in that part (learnShapeBackdrop).\n"
      "function learnShapeFlat(g, P, k, u, quality, C, label, small, mv) {\n")
p.rep("  if (M.w && M.h) { learnShapeTint(M, k, u); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high'; g.drawImage(M.cv, M.bx, M.by, M.bw, M.bh); }\n",
      "  if (M.w && M.h) {\n"
      "    learnShapeTint(M, k, u, !!mv); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';\n"
      "    if (mv) g.globalAlpha = mv.back;\n"
      "    g.drawImage(M.cv, M.bx, M.by, M.bw, M.bh);\n"
      "    if (mv) g.globalAlpha = 1;\n"
      "  }\n")
p.rep("  // the big circle\n"
      "  g.beginPath(); g.arc(X(0), Y(0), 2 * P.s, 0, 2 * PI); g.strokeStyle = C.ink2; g.lineWidth = 1.25; g.globalAlpha = 0.8; g.setLineDash([4, 4]); g.stroke(); g.setLineDash([]); g.globalAlpha = 1;\n",
      "  // the big circle (while the dots are away from home it is drawn firmly: it is the line the throwing out is judged by)\n"
      "  g.beginPath(); g.arc(X(0), Y(0), 2 * P.s, 0, 2 * PI);\n"
      "  if (mv && mv.ph) { g.strokeStyle = C.ink; g.lineWidth = 1.6; g.globalAlpha = 0.9; g.stroke(); g.globalAlpha = 1; }\n"
      "  else { g.strokeStyle = C.ink2; g.lineWidth = 1.25; g.globalAlpha = 0.8; g.setLineDash([4, 4]); g.stroke(); g.setLineDash([]); g.globalAlpha = 1; }\n"
      "  if (mv) learnShapeDotsDraw(g, P, v => [X(v[0]), Y(v[1]), 0], P.s, mv.k, mv.ph, false);\n")

# ----- the 3D picture
p.rep("function learnShapeSolid(g, panes, k, u, quality, C, label, small, above) {\n",
      "// (Round 29.) mv: as for learnShapeFlat.\n"
      "function learnShapeSolid(g, panes, k, u, quality, C, label, small, above, mv) {\n")
p.rep("  try { res = T.draw(o); } catch (err) { if (!Sh.warned) { Sh.warned = true; console.warn('learnShape3d.draw failed', err); } }   // (said once, not once a frame)\n",
      "  // (round 29) Move by move: while only the dots move, the glass picture is the same from frame to frame. It is\n"
      "  // then not drawn again (its canvas keeps it), and behind the dots it shows as a faint ghost: by the opacity of\n"
      "  // its canvas, which costs the graphics card nothing.\n"
      "  const a3 = ap(), sig3 = mv ? JSON.stringify([o, a3.id, S.param[a3.id], S.n, S.abs, S.flip, T.canvas.clientWidth, T.canvas.clientHeight, window.devicePixelRatio]) : '';\n"
      "  if (mv && sig3 === Sh.sig3 && Sh.res3 && Sh.res3.ok) res = Sh.res3;\n"
      "  else {\n"
      "    try { res = T.draw(o); } catch (err) { if (!Sh.warned) { Sh.warned = true; console.warn('learnShape3d.draw failed', err); } }   // (said once, not once a frame)\n"
      "    Sh.sig3 = sig3; Sh.res3 = res;\n"
      "  }\n"
      "  const faint = mv && mv.back < 0.999 ? String(Math.round(mv.back * 1000) / 1000) : '';\n"
      "  if (T.canvas.style.opacity !== faint) T.canvas.style.opacity = faint;\n")
p.rep("    g.lineWidth = 1; g.setLineDash([2, 4]); g.globalAlpha = 0.4; g.stroke(); g.setLineDash([]); g.globalAlpha = 1;\n"
      "    if (Sh.kind === 'm') { g.restore(); continue; }\n",
      "    g.lineWidth = 1; g.setLineDash([2, 4]); g.globalAlpha = 0.4; g.stroke(); g.setLineDash([]); g.globalAlpha = 1;\n"
      "    // (round 29) the dots of Move by move; while they are away from home the big ball's outline is drawn firmly\n"
      "    if (mv && mv.ph) { g.beginPath(); g.arc(mid[0], mid[1], 2 * pr.s, 0, 2 * PI); g.strokeStyle = C.ink; g.lineWidth = 1.6; g.globalAlpha = 0.85; g.stroke(); g.globalAlpha = 1; }\n"
      "    if (mv) learnShapeDotsDraw(g, P, to, pr.s, mv.k, mv.ph, true);\n"
      "    if (Sh.kind === 'm') { g.restore(); continue; }\n")

# ----- a frame
p.rep("  if (three) note = learnShapeSolid(g, panes, k, u, quality, C, label, small, above);\n"
      "  else for (const P of panes) learnShapeFlat(g, P, k, u, flatQ, C, label, small);\n",
      "  // (round 29) Move by move: the part of the step being played (null at a whole step), what the picture of\n"
      "  // starting places shows in it and how strongly (bd), and what the pictures need to draw the dots (mv). With\n"
      "  // At once: no part, the picture of the slider's own position at full strength, and no dots.\n"
      "  Sh.ms.dots = 0;\n"
      "  const mvOn = learnShapeMovesOn(), ph = mvOn && u > 1e-9 && k < N ? learnShapePart(u) : null;\n"
      "  const bd = ph ? learnShapeBackdrop(k, ph, three) : { k, u, back: 1 }, mv = mvOn ? { k, ph, back: bd.back } : null;\n"
      "  if (three) note = learnShapeSolid(g, panes, bd.k, bd.u, quality, C, label, small, above, mv);\n"
      "  else for (const P of panes) learnShapeFlat(g, P, bd.k, bd.u, flatQ, C, label, small, mv);\n")
p.rep("      if (i === 0) label(W.read, P.x + 10, P.y + (small ? 32 : 35), W.whole ? C.brass : C.bad, 'left', small ? 12.5 : 14, 600, box);\n",
      "      // (round 29: in a part of a step the corner names the part, where there is room; only the throwing out is in the warning colour)\n"
      "      if (i === 0) label(W.part && narrow ? `step ${W.k + 1}` : W.read, P.x + 10, P.y + (small ? 32 : 35), W.whole ? C.brass : W.part && W.part.key !== 'gone' ? C.ink : C.bad, 'left', small ? 12.5 : 14, 600, box);\n"
      "      // (and, where the corner has room for a third line, what a dot is)\n"
      "      if (i === 0 && mv && !small && !narrow) label('each dot: one starting place', P.x + 10, P.y + 54, C.ink2, 'left', 12, 500, box);\n")

# ----- the panel's words
p.rep("  if (Sh.dials) Sh.dials.sync();\n}\nfunction learnShapePaint() {\n",
      "  // (round 29) what the choice Each step does\n"
      "  if (E.eachHelp) set(E.eachHelp, Sh.each === 'moves'\n"
      "    ? 'Dots are laid over the picture, one for each starting place, and every step is played on them part by part: where the dots are now, the moves of the rule one after another, the throwing out, and the way back home. Each dot keeps its colour, and a few are drawn larger so that you can follow them. Dots chooses how many there are. (The last move, Slide, is the one that One point calls Add c.)'\n"
      "    : 'Each step shows only what it leaves. Move by move shows the moves inside each step, played on dots.');\n"
      "  if (Sh.dials) Sh.dials.sync();\n}\nfunction learnShapePaint() {\n")

# ----- the transport's words and marks
p.rep("  if (Math.abs(+E.pos.value - Sh.pos) > 1e-6) E.pos.value = Sh.pos;\n"
      "  E.pos.setAttribute('aria-valuetext', W.whole ? (W.k === 0 ? 'The start' : `What is left after ${W.k} of ${N} steps`) : `Step ${W.k + 1} of ${N}, ${Math.round(W.u * 100)} percent`);\n",
      "  // (round 29) Move by move: the slider goes through the parts of a step, so the hand needs finer notches\n"
      "  const fine = learnShapeMovesOn() ? '0.005' : '0.05';\n"
      "  if (E.pos.step !== fine) E.pos.step = fine;\n"
      "  if (Math.abs(+E.pos.value - Sh.pos) > 1e-6) E.pos.value = Sh.pos;\n"
      "  E.pos.setAttribute('aria-valuetext', W.whole ? (W.k === 0 ? 'The start' : `What is left after ${W.k} of ${N} steps`)\n"
      "    : W.part ? `Step ${W.k + 1} of ${N}, ${W.part.label}, ${Math.round(W.part.t * 100)} percent` : `Step ${W.k + 1} of ${N}, ${Math.round(W.u * 100)} percent`);\n"
      "  learnShapeChips(W);\n"
      "  // A low phone window: with the row of Each step and Dots (44 px) the picture's block would be taller than the pin\n"
      "  // of 85-pin.js holds at the top of the window (PIN_MOST of it), and the picture would scroll away with the page,\n"
      "  // which it did not before this row was there. In such a window the two choices stand in the panel only.\n"
      "  // (280: the transport with that row, the gap above it and the pin's 6 px, measured; 236: without the row. Where the\n"
      "  // picture would not be held even without the row, the row stays.)\n"
      "  { const pin = typeof PIN !== 'undefined' ? PIN : null, most = typeof PIN_MOST !== 'undefined' ? PIN_MOST : 0.72;\n"
      "    const low = !!pin && pin.can && pin.want && pin.small > 0 && matchMedia('(max-width: 620px)').matches\n"
      "      && stage.offsetHeight + 280 > pin.small * most - 2 && stage.offsetHeight + 236 <= pin.small * most;\n"
      "    if (E.bar.classList.contains('is-low') !== low) E.bar.classList.toggle('is-low', low); }\n"
      "  // (while Move by move plays, the sentence changes with every part: a reader that speaks the page is not sent each one)\n"
      "  { const live = Sh.playing && W.part ? 'off' : 'polite'; if (E.say.getAttribute('aria-live') !== live) E.say.setAttribute('aria-live', live); }\n"
      "  for (const r of E.eachs) r.checked = r.value === Sh.each;\n"
      "  for (const s of E.dotSels) { if (s.value !== Sh.dots) s.value = Sh.dots; s.disabled = Sh.each !== 'moves'; }\n")
p.rep("  const a = ap(), sig = [Sh.kind, L.space, S.n, S.abs, S.flip, a.id, JSON.stringify(S.param[a.id]), Sh.c, Sh.threeTried, !!Sh.three, Sh.note, Sh.side].join('|');\n",
      "  const a = ap(), sig = [Sh.kind, L.space, S.n, S.abs, S.flip, a.id, JSON.stringify(S.param[a.id]), Sh.c, Sh.threeTried, !!Sh.three, Sh.note, Sh.side, Sh.each].join('|');\n")

# ----- the clock
p.rep("    const dt = clamp(now - Sh.last, 0, 80), T = LEARN_SHAPE_SECONDS[LEARN.speed] || LEARN_SHAPE_SECONDS.normal, stop = Sh.until === null ? N : Math.min(N, Sh.until);\n",
      "    // (round 29) Move by move plays the parts of a step one after another, and so takes longer for a step\n"
      "    const TS = learnShapeMovesOn() ? LEARN_SHAPE_MOVE_SECONDS : LEARN_SHAPE_SECONDS;\n"
      "    const dt = clamp(now - Sh.last, 0, 80), T = TS[LEARN.speed] || TS.normal, stop = Sh.until === null ? N : Math.min(N, Sh.until);\n")
p.rep("      if (pos >= stop - 1e-9) { pos = stop; Sh.playing = false; Sh.until = null; }\n",
      "      if (pos >= stop - 1e-9) { pos = stop; Sh.playing = false; Sh.until = null; Sh.endSide = Math.abs(stop - Math.round(stop)) > 1e-9; }\n")
p.rep("  Sh.until = until === undefined ? null : until;\n",
      "  Sh.until = until === undefined ? null : until; Sh.endSide = false;\n")
p.rep("  learnShapeStop();\n  pos = clamp(+pos || 0, 0, N);\n"
      "  Sh.pos = Math.abs(pos - Math.round(pos)) < 0.02 ? Math.round(pos) : pos;     // close to a whole step is the whole step\n",
      "  learnShapeStop(); Sh.endSide = false;\n  pos = clamp(+pos || 0, 0, N);\n"
      "  // close to a whole step is the whole step (round 29: with Move by move only very close, or the first part of a step could not be gone through by hand)\n"
      "  Sh.pos = Math.abs(pos - Math.round(pos)) < (learnShapeMovesOn() ? 0.004 : 0.02) ? Math.round(pos) : pos;\n")

# ----- back to how it opens
p.rep("  Sh.kind = 'm'; Sh.c = LEARN_V_START[2].c.slice(); Sh.pos = 0; Sh.gone = ''; Sh.thin = ''; Sh.place = null; Sh.above = {};\n",
      "  Sh.kind = 'm'; Sh.c = LEARN_V_START[2].c.slice(); Sh.pos = 0; Sh.gone = ''; Sh.thin = ''; Sh.place = null; Sh.above = {};\n"
      "  Sh.each = 'moves'; Sh.dots = 'some'; Sh.endSide = false; Sh.D = {}; Sh.sig3 = '';      // (round 29)\n")

# ----- building it: the transport
p.rep("    '<p class=\"learn-say\" id=\"learnShapeSay\" aria-live=\"polite\"></p>' +\n",
      "    '<p class=\"learn-say\" id=\"learnShapeSay\" aria-live=\"polite\"></p>' +\n"
      "    // (round 29) the names of the parts of one step, with Each step: Move by move\n"
      "    '<div class=\"learn-ticks learn-shape-parts\" id=\"learnShapeParts\" role=\"group\" aria-label=\"The parts of one step\" hidden></div>' +\n")
p.rep("    seg('learnShapeSpaceBar', '2', '2D', '2D page') + seg('learnShapeSpaceBar', '3', '3D', '3D space') + '</fieldset></div></div>');\n",
      "    seg('learnShapeSpaceBar', '2', '2D', '2D page') + seg('learnShapeSpaceBar', '3', '3D', '3D space') + '</fieldset></div>' +\n"
      "    // (round 29) how a step is shown: only what it leaves, or the moves inside it, played on dots; and how many dots\n"
      "    '<div class=\"learn-shape-pick learn-shape-how\"><span class=\"label learn-shape-cap\" aria-hidden=\"true\">Each step</span><fieldset class=\"learn-shape-seg\" id=\"learnShapeEachBar\"><legend class=\"learn-shape-legend\">Each step</legend>' +\n"
      "    seg('learnShapeEachBar', 'once', 'At once', 'Each step shows only what it leaves') + seg('learnShapeEachBar', 'moves', 'Move by move', 'The moves inside each step, played on dots') + '</fieldset>' +\n"
      "    '<label class=\"learn-shape-dots\"><span class=\"label learn-shape-cap\">Dots</span><select id=\"learnShapeDotsBar\"><option value=\"few\">Few</option><option value=\"some\">Some</option><option value=\"many\">Many</option></select></label></div></div>');\n")

# ----- building it: the panel
p.rep("  el.eqNote.after(kind);\n  E.helpJ = kind.querySelector('#learnShapeHelpJ'); E.helpBoth = kind.querySelector('#learnShapeHelpBoth');\n",
      "  el.eqNote.after(kind);\n  E.helpJ = kind.querySelector('#learnShapeHelpJ'); E.helpBoth = kind.querySelector('#learnShapeHelpBoth');\n"
      "  // (round 29) Each step: At once | Move by move, and Dots: here with a line of help, and in the transport\n"
      "  const each = make('div', 'sec-inner learn-only-shape', '<fieldset class=\"learn-follow\" id=\"learnShapeEach\"><legend class=\"label\">Each step</legend>' +\n"
      "    seg('learnShapeEach', 'once', 'At once') + seg('learnShapeEach', 'moves', 'Move by move') + '</fieldset>' +\n"
      "    '<p class=\"note\" id=\"learnShapeEachHelp\"></p>' +\n"
      "    '<div class=\"field\"><label class=\"label\" for=\"learnShapeDots\">Dots</label><select id=\"learnShapeDots\"><option value=\"few\">Few</option><option value=\"some\">Some</option><option value=\"many\">Many</option></select></div>');\n"
      "  each.id = 'learnShapeEachBlock';\n"
      "  kind.after(each);\n"
      "  E.eachHelp = each.querySelector('#learnShapeEachHelp'); E.parts = E.bar.querySelector('#learnShapeParts');\n"
      "  E.eachs = [...each.querySelectorAll('input[name=learnShapeEach]'), ...E.bar.querySelectorAll('input[name=learnShapeEachBar]')];\n"
      "  E.dotSels = [each.querySelector('#learnShapeDots'), E.bar.querySelector('#learnShapeDotsBar')];\n"
      "  const pickEach = e => { if (e.target.name === 'learnShapeEach' || e.target.name === 'learnShapeEachBar') LEARN.shape.set({ each: e.target.value }); };\n"
      "  each.addEventListener('change', pickEach); E.bar.querySelector('#learnShapeEachBar').addEventListener('change', pickEach);\n"
      "  for (const s of E.dotSels) s.addEventListener('change', () => LEARN.shape.set({ dots: s.value }));\n")

# ----- for tests and the console
p.rep("// set({ on, kind, space, c, pos }): any of them. on: true switches Learn on as well, with Follow = A whole shape.\n",
      "// set({ on, kind, space, c, pos, each, dots }): any of them. on: true switches Learn on as well, with Follow = A whole shape.\n"
      "// (round 29) each: 'once' | 'moves' (Each step: At once | Move by move); dots: 'few' | 'some' | 'many'.\n")
p.rep("  if (o.kind !== undefined && ['m', 'j', 'both'].includes(o.kind)) Sh.kind = o.kind;\n",
      "  if (o.kind !== undefined && ['m', 'j', 'both'].includes(o.kind)) Sh.kind = o.kind;\n"
      "  if (o.each !== undefined && ['once', 'moves'].includes(o.each) && o.each !== Sh.each) { Sh.each = o.each; Sh.endSide = false; Sh.sig3 = ''; }\n"
      "  if (o.dots !== undefined && ['few', 'some', 'many'].includes(o.dots)) Sh.dots = o.dots;\n")
p.rep("    follow: L.follow, quality: Sh.quality, side: Sh.side, ms: Object.assign({}, Sh.ms), three: Sh.last3,\n",
      "    follow: L.follow, quality: Sh.quality, side: Sh.side, ms: Object.assign({}, Sh.ms), three: Sh.last3,\n"
      "    // (round 29) each, dots: the two new choices. part: the part of the step being played (null at a whole step and\n"
      "    // with At once): its key ('out', 'move', 'gone', 'home'), its name, its number i of n, how far through it (t), and\n"
      "    // for a move its number. parts: the names of the parts of one step, in order. shown: picture by picture, how many\n"
      "    // dots there are and how many are on show at this step.\n"
      "    each: Sh.each, dots: Sh.dots, part: W.part ? { key: W.part.key, label: W.part.label, i: W.part.i, n: W.part.n, t: W.part.t, move: W.part.key === 'move' ? W.part.j : -1 } : null,\n"
      "    parts: Sh.each === 'moves' ? learnShapeMoves().chips.slice() : [],\n"
      "    shown: on && Sh.each === 'moves' ? learnShapeKinds().map(kd => { const D = learnShapeDots(kd); return { kind: kd, all: D.dots.length, on: D.dots.filter(d => d.out > W.k).length }; }) : [],\n")
p.before("LEARN.shape = {\n", frag('67-handle.js'))
p.rep("  glass: LEARN_SHAPE_GLASS,      // the numbers of the 3D picture's glass, for trying others (then: set({}) draws again)\n",
      "  glass: LEARN_SHAPE_GLASS,      // the numbers of the 3D picture's glass, for trying others (then: set({}) draws again)\n"
      "  // (round 29) the dots of Each step: Move by move (see learnShapeDotsOut, learnShapeChainOut, learnShapeDotsAt)\n"
      "  dots: kind => learnShapeDotsOut(kind), chain: (kind, k) => learnShapeChainOut(kind, k), dotsAt: (kind, pos) => learnShapeDotsAt(kind, pos),\n"
      "  playPart: i => { learnShapePlayPart(i); return learnShapeState(); },\n"
      "  numbersAt: (kind, pts) => learnShapeNumbersAt(kind, pts),      // 2D: the fine picture's own numbers at any points\n"
      "  // what the last redraw took (ms; see LEARN_SHAPE.ms) and where the slider stood, read without drawing anything\n"
      "  timing: () => Object.assign({ pos: LEARN_SHAPE.pos, playing: LEARN_SHAPE.playing }, LEARN_SHAPE.ms),\n"
      "  // 3D: the picture's own program asked about a level cut of the big ball (learnShape3d's slice(), with the c on show)\n"
      "  slice3: (kind, opt) => (LEARN_SHAPE.three && typeof LEARN_SHAPE.three.slice === 'function' ? LEARN_SHAPE.three.slice(kind === 'j' ? 'j' : 'm', LEARN_SHAPE.c, opt) : null),\n"
      "  quiet: LEARN_SHAPE_QUIET, moveSeconds: LEARN_SHAPE_MOVE_SECONDS,\n")
p.write()
