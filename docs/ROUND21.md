# Round 21: rules with memory ("follow whatever new plane is made during the orbit")

Read this whole file before you start. It is the only briefing you get.

## 1. What this project is

A user who is not a mathematician is looking for the "right" 3D version of z -> z^2 + c. They judge by pictures
and plain words. A 3D rule here is F(v) = a "square" of the 3D point v, and the orbit is v -> F(v) + c.
The Julia set of c: all start points whose orbit stays bounded. The Mandelbrot solid: all c for which the orbit of
0 stays bounded. Axes: the flat page is the plane z = 0 (x to the right, y up); the x-axis is the real line.

The user's own tests for the right rule (all must hold):
1. The cut at z = 0 is exactly the flat (complex) picture, for Julia sets with c in the flat page and for the Mandelbrot solid.
2. Bodies and buds come from the power the way they do in the flat set, not from a dial that sets a number of planes.
3. No shards, no dust, no disconnected debris.
4. NOT "the flat set simply spun round the x-axis": no rings. A bud that is a ring round the x-axis is a fail.
5. A principled carry-over of what the flat rule does, not an arbitrary construction.
Their picture of "right": a body with smaller ROUND bodies on it in more than one direction, each with smaller ones
on it in turn ("bulbs growing between things in a natural way"). The best rule so far, in their words the closest,
is "Turning plane, along" (bench name `along`): for c = -1 a row of bodies each with eight round buds round it.
Its faults: for c off the x-axis (the rabbit, the Siegel disc) it gives one swollen lump with no separate bodies;
its Mandelbrot solid is a lumpy rock; close up its skin has thin fins.

Order of work, set by the user: Julia sets first (basilica c = -1, San Marco, airplane, rabbit, Siegel disc,
dendrite). A Mandelbrot solid is only interesting for a rule whose Julia sets are good. In this round Mandelbrot
pictures are still made for every rule, because the user's question is about the Mandelbrot solid, but a rule is
RANKED by its Julia sets first.

## 2. The user's question that this round answers

Earlier today the user asked: why not square every tested point about "the plane that c creates" (the flat sheet
that holds the x-axis and c)? Tested: the Mandelbrot solid is then exactly the flat set spun round the x-axis
(0 of 400,000 test points differ), because the orbit of 0 lands on c, c lies in its own sheet, and the sheet
carries the flat rule: the orbit never leaves the sheet.

The user's reply, verbatim: **"ok, how about following whatever new plane is made during the orbit?"**

So: the plane is not fixed and not given by c alone; it is made anew by the orbit as it goes, and each step uses
it. That needs the orbit to CARRY something besides the point: a rule with memory. Nothing in the lab does that
yet, and none of the earlier limits (which are about fixed rules F) has been checked for it.

## 3. What is already known (do not redo; build on it or attack it)

**The one-plane rule P** (bench `oneplane`, `S.oneplane` in `out/me/r16/scout.py`):
P(x, y, z) = f * (x^2 - y^2, 2xy, 2 r z), r = |v|, f = r^2 / (r^2 + z^2). It squares the length, is exactly complex
squaring on the flat page, keeps angles everywhere (it is the only such rule), and crushes the two directions
straight up and down. Its Julia sets are clean for every c but have their smaller bodies only round the flat page.
"P about the sheet at turn theta" means Rot_x(theta) P(Rot_x(-theta) v): the same rule with another sheet through
the x-axis in the place of the flat page.

**The lathe** (bench `lathe`): every point squared inside its own sheet through the x-axis. Everything it makes is
spun round the x-axis (rings). Rejected by the user.

**Claim S (symmetry), to be attacked in this round.** If a recipe for the orbit uses nothing but the x-axis, c and
the orbit's own points (no fixed direction or plane off the x-axis), then turning c round the x-axis turns the
whole orbit with it, so the Mandelbrot solid looks the same from every side of the x-axis. If its cut along the
flat page is also the flat Mandelbrot set, it IS the flat set spun. So a solid that is not spun needs something
fixed that is off the x-axis. In a rule with memory the natural fixed thing is where the carried plane STARTS: the
flat page.

**The scout (the orchestrator's quick look, `out/r21/me/follow.py`, pictures `out/r21/me/follow-julia-quick.png`,
`follow-mandel-quick.png`; the same rules are `M.SCOUT` in the library).** The orbit carries a sheet through the
x-axis, which starts as the flat page; each point is squared by P about the carried sheet.
- `fixed`: the sheet never moves = the one-plane rule.
- `lag25`, `lag50`, `lag75`: before each squaring the sheet moves that share of the way to the point's own sheet.
- `delay`: each point is squared about the sheet of the point before it.
- `first`: the first squaring about the flat page, every later one about the point's own sheet.
- `own`: the point's own sheet at once = the lathe.
Seen at low resolution: the family runs from the one-plane rule to the lathe. Where the sheet follows closely the
bodies get ribs and rings like the lathe's; where it lags, the Mandelbrot solid off the flat page is a smooth blob
with no buds, and the rabbit is a layered lump; `delay` shatters the rabbit and the Siegel disc into dust; `lag50`
has a tear (the half-way blend can cancel). Nothing showed round buds off the flat page that are not rings.
All seven are exact on the flat page (0 verdicts of 8,000 differ, for the Mandelbrot set and three Julia sets).
This is a quick look at one corner. Your job is the rest of the space, or to show that the corner was misjudged.

**Limits known for FIXED rules** (checked by a second party, not by a mathematician; they may not hold with memory):
C1: for c off the x-axis, no second plane besides c's own can be kept by the rule and show the flat picture.
C3: on the Mandelbrot solid of a smooth fixed rule, buds attach along lines, not as round balls all over.
Parity and count: planes that are sent INTO the flat page (not kept) come in threes at least and bring fins.

## 4. The library (use it; do not write your own iteration)

`out/r21/lib/mem.py` (read its docstring and the `SCOUT` rules; about 250 lines). From the project root:

    import sys; sys.path.insert(0, 'out/r21/lib'); import mem as M
    r = M.Rule('myname', 'plain words for what it does', step, init)     # see the docstring for step and init
    M.flat_check(r)            # is the flat page exact? counts verdicts that differ from the complex orbit
    M.spun_check(r)            # share of test points whose verdict changes when turned round the x-axis (0 = spun)
    M.julia_sheet([r1, r2, M.bench('along')], 'out/r21/<you>/julia.png')         # rough solids of six Julia sets
    M.mandel_sheet([r1, r2], 'out/r21/<you>/mandel.png')                         # cuts and the rough solid
    M.cut_axis(r, 22.5, 600, 400, 60, c=(-1, 0, 0)); M.cut_across(...); M.solid(...); M.shade(...); M.shade_solid(...)

`M.bench(name)` wraps a fixed rule of the bench (`along`, `oneplane`, `lathe`, `away`, `m_w3`, ...) so the same
tools draw it. Building blocks: `M.sq_about` (P, or any fixed F, about a carried sheet), `M.sheet_of`, `M.blend`.
A carried state can be anything: a sheet, a full frame (nine arrays), earlier points, counters.
Speed: a rough solid takes 5 to 20 s, a cut 1 to 5 s. Use `python out/r21/lib/mem.py` to see the numbers for the scout.

Put your rules in `out/r21/<your name>/myrules.py` as a list `RULES = [M.Rule(...), ...]`, your scripts and
pictures in the same folder, and your findings in `out/r21/<your name>/NOTES.md` (NOT report.md).

## 5. Rules of the house

- Work from the project root (the folder that holds `docs/`, `out/`, `src/`). Run python with `PYTHONIOENCODING=utf-8`.
- Write Python files with the Write tool, not with shell heredocs (backslashes get mangled).
- Do NOT touch `src/`, `base*/`, `dist/`, `tools/`, `squaring-lab.html`, `notes/`, `docs/`, `out/r21/lib/`, or any other
  agent's folder. No browser, no page build, no publishing. Several agents run at once: keep each run under about
  10 minutes and do not start more than one heavy run at a time.
- LOOK at every picture you rely on (Read the PNG) before you say what it shows. Say for each statement whether it
  is measured (a number you computed), seen (in a picture you looked at) or reasoned.
- Known traps. (a) A cut along a plane that is a mirror plane of the rule hides its faults: also cut at 11.25,
  22.5 and 33.75 degrees and across the x-axis. (b) Rough blocks at 20 to 30 steps hide dust and slow leaks: for
  any rule you praise, compare the volume at 30 and at 80 steps, and look at one close-up. (c) "Round buds" seen
  from one side may be rings: always check a cut ACROSS the x-axis or `M.spun_check`, and look from a second
  eye position (the `cam` argument).
- A rule must be exact on the flat page (`M.flat_check`: all counts 0) or it is out, whatever else it does.
- Report failures as plainly as successes. "Nothing in my family passes, and here is why" is a full result.
  Do not dress a ring, a lump or dust as a success.

## 6. What a success would look like

A rule with memory, exact on the flat page, whose basilica has separate bodies with ROUND buds in more than two
directions that are not rings (as `along` has), AND whose rabbit has separate bodies (which `along` has not), with
no dust. Only then: a Mandelbrot solid that is not spun and has round buds off the flat page.
Compare everything to `M.bench('along')` and `M.bench('oneplane')` drawn by the same tools.
