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
- a **Custom approach**: a rule put together on the page from steps (lengths and angles, turns about any axis,
  sphere inversions, mirrors and folds, quaternions, matrices, adding c, single operations of arithmetic, and
  formulas of one's own). A step can be switched off, moved, or broken down: a block into its formulas, a formula
  into its single operations. A bar under the picture plays the steps, iteration by iteration, in the picture
  itself, with dots that show where the steps carry the solid's points and guides for the step on show: its axis,
  plane, sphere or arrow, and the way one ringed dot takes through it. A step that moves no point shows the value
  it works out for that dot. A rule can be saved under a name and loaded again, and the Mandelbrot and the Julia
  picture can be shown side by side.
  Thirty-two of the approaches of the list can be loaded as steps (`13-custom-rules.js`), each giving that approach's
  own numbers;
- a 3D view and a 2D view (the flat cut), cuts, colours, presets, and export of pictures and 3D models;
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

This is version 1.08. Each version is tagged, as `v1.08`.
