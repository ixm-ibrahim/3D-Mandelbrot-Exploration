# 3D Mandelbrot Exploration

A search for the right way to carry the flat rule z → z² + c into three dimensions, and the tool built to look at
every attempt: the **3D Squaring Lab**, one web page with no dependencies.

The starting point was Kučera, "New Generalizations of Quadratic Julia Sets to 3D" (sphere inversions in place of
squaring). The paper's text is not in this repository.

## The lab

`squaring-lab.html` is the built page. Open it in a browser. It holds:

- an **Approach** list: every 3D rule that was tried, each as its own entry, with its dials;
- a 3D view and a 2D view (the flat cut), cuts, colours, presets, export of pictures and 3D models;
- **Balls on balls**, a picture made only of slides by whole numbers and sphere inversions. It has no c and is not
  the goal, but its placement and spacing of bodies is the look the 3D basilica should have;
- a **Learn** tab that plays one step of a rule move by move, for one point or for a whole shape.

## What the right rule has to pass

1. The flat cut z = 0 is exactly the flat picture of z² + c.
2. The number of bulbs follows from the power, as it does in the flat picture.
3. No shards and no smear.
4. No rings (the flat picture merely spun round a line), and it works for the rabbit, not only for c = −1.
5. It is a principled carry-over from 2D, with nothing picked by hand.

No rule passes all five yet. `notes/_state.md` is the running log of what was tried and why each attempt failed.

## Layout

| Path | What it is |
| --- | --- |
| `src/` | The lab's source: `head.html`, `body.html`, `css/*.css`, `js/*.js` |
| `build.py` | Joins `src/` into one page. `python build.py` writes `squaring-lab.html` and `dist/preview.html` |
| git tags | Every published version is a tag: `git checkout v21` gives Version 21, `v23` is the newest |
| `tools/` | Test tools. `tools/shot.py` drives the page in headless Chrome and takes pictures |
| `docs/` | The brief of each round of work (`ROUND29.md` and `ROUND29-LEARN.md` are the newest) |
| `notes/` | The log (`_state.md`), reports and small scripts |
| `out/` | Each round's scripts, notes and logs. The pictures, 3D models and number caches they produced are left out of the repository (about 15 GB) |
| `tests/`, `data/` | Test pages and the preset lists |

All JavaScript files are joined into one function scope in file-name order, and only `90-boot.js` runs code when
the page loads.
