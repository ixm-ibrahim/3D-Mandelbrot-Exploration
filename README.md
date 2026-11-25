# 3D Mandelbrot Exploration

A search for the right way to carry the flat rule z → z² + c into three dimensions, and the tool built to look at
every attempt: the **3D Squaring Lab**, one web page that uses no libraries.

The starting point was Kučera, "New Generalizations of Quadratic Julia Sets to 3D" (sphere inversions in place of
squaring). The paper's text is not in this repository.

**[docs/vision.md](docs/vision.md)** says what the finished fractal should look like, how a rule is judged, what has
come closest and what is known not to work. No rule passes yet.

## The lab

`squaring-lab.html` is the built page. It holds:

- an **Approach** list: the 3D rules that were tried and kept, each as its own entry;
- a **Custom approach**: a rule put together on the page from steps (lengths and angles, rotations about any axis,
  sphere inversions, mirrors and folds, quaternions, matrices, adding c, single operations of arithmetic, and
  formulas of one's own). A length is measured straight, the Manhattan way (|x| + |y| + |z|) or by its largest
  part, or in the twin of either of those that leaves the flat cut as it is, and a sphere inversion moves every point, or only the points on one side of its sphere. A rule has three sections: steps taken once before the iterations, the steps of every
  iteration, and steps taken once after the last iteration. A step that moves a point works on the point z, on
  c, or on a point the rule has named, in whichever section it stands, and a change of c lasts for the rest of
  the orbit. A formula has the length and the two angles of every point, written after the point, as in `z.phi` and `c.phi`,
  and its box wraps and grows with its text. A step can name a function of the rule's own, with a name, the
  names of what it is given and a formula, and every step after it can call that function in its formulas. A step can be switched off, moved, made another kind where it stands, saved with its settings under a name to be
  added again from the list of steps, or broken down: a
  block into its formulas, a formula into its single operations. Steps that stand next to each other can be
  selected, with a Shift-click for a run or a Ctrl-click one by one, and saved under a name as one step that holds
  them. It is moved, switched, played and added again as one, it can be opened to change the steps inside, and
  breaking it down sets them free. The rule works out the same with it or without. The list of steps can be searched, and its groups shut. A bar under the picture plays the steps,
  iteration by iteration from the first or straight through them all, in the picture itself, at three speeds, with dots that show where the
  steps carry the solid's points and guides for the step on show: its axis, plane, sphere or arrow, and the way
  one ringed dot takes through it. A step that moves no point shows the value it works out for that dot. The
  steps taken once are played at the two ends. A point is thrown out when an iteration is done and it lies beyond
  the bailout radius: the dots and the surface both change then, and not in the middle of a step. The dots and the
  surface can each be drawn fainter. A step that is switched off can still be played, to see what it
  would do where it stands: the rule stays without it. A dot of a Mandelbrot picture is drawn on its own c until its
  first iteration, which only puts it there, is done, so a step that changes c before the iterations moves the
  dots. A step that works on c anywhere else, or on a named point, shows that point of the ringed dot as a
  ring of its own. The play has the choices of the Learn tab: dots, the surface or both; how many dots there are, where they start (a
  full grid, level sheets, shells) and how far out; what their colours say; whose orbits are drawn; and whether
  new dots come in for those thrown out. A rule can be saved under a name and loaded again, and the Mandelbrot
  and the Julia picture stand side by side, or the one that is chosen stands alone.
  Thirty-two of the approaches of the list can be loaded as steps (`13-custom-rules.js`), each giving that approach's
  own numbers, and its own picture with the bailout radius at 64;
- a 3D view and a 2D view (the flat cut), cuts, colours, presets, and export of pictures and 3D models. On a wide
  window the picture's lower and right edges can be dragged to set its size. The camera takes the picture's new
  shape, so nothing is stretched, and the room that is freed goes to the controls, or in the custom approach to
  the steps, which then stand beside the picture;
- **Balls on balls**, a picture made only of slides by whole numbers and sphere inversions. It has no c and is not
  the goal, but its placement and spacing of bodies is the look the 3D basilica should have;
- a **Learn** tab that plays one step of a rule move by move, for one point or for a whole shape.

## Building and checking

    python build.py          # joins src/ into squaring-lab.html and dist/preview.html
    python tools/smoke.py    # draws every approach as a Julia set and as a Mandelbrot set; fails on any page error

`squaring-lab.html` is the page as it is published: the host supplies the document around it. To open the lab from
disk, use `dist/preview.html`, the same page inside a complete document.

`tools/compare.py` draws a fixed set of views before and after a change and lists the ones that differ. The page
draws the same picture every time, so any difference is a real change.

`tools/shot.py` drives the page from the command line or from Python: it runs JavaScript in it, waits for the
picture, and saves screenshots. The tools need Chrome or Edge and nothing else.

## Layout

| Path | What it is |
| --- | --- |
| `src/` | The lab's source: `head.html`, `body.html`, `css/*.css`, `js/*.js` |
| `build.py` | Joins `src/` into one page |
| `squaring-lab.html` | The built page |
| `docs/` | `vision.md`: the goal, the tests, and the state of the search. `img/`: its pictures |
| `tools/` | `smoke.py`, `compare.py` and `shot.py` |

All JavaScript files are joined into one function scope in file-name order, so the number at the front of a file
name is its place in the page. Only `90-boot.js` runs code when the page loads. Each 3D rule is one entry in
`src/js/10-approaches.js`. The custom approach is the one entry whose rule is written on the page: `12-custom.js`
reads its steps into shader text and into the same rule in JavaScript, and `82-custom-ui.js` is its panel.

This is version 1.23. Each version is tagged, as `v1.23`.
