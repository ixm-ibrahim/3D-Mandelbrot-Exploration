# Round 27, final (Track A): the page as it would be merged, measured once more

Page: `dist/r27-final.html` (894149 bytes, md5 417237ec7b6e93c12e7bf075f0dc670c), built with the command of
`out/r27/entry/BUILD.txt` under the name r27-final. It is byte for byte the fixer's `dist/r27-fix.html`; at the end
of my work the overlay still rebuilt to the same md5. Frozen page: `dist/r27-base.html`
(`python build.py --name r27-base --base base18a`, md5 4a91027c...). Window 1400x950, dark, unless a line says
otherwise. Every number below comes from a script in `mk/` run by me on that page; "seen" means I opened the picture.
Clicks, pointer moves and typed values are events made by script, not a real mouse or finger.

## In plain lines

- **Verdict: not ready, by the rule "ready only if 1 to 3 are clean".** 1 and 2 are clean. In 3 all six major
  defects are gone and so are eleven of the fourteen minor ones; three minor ones that the fixer reported as not
  repaired are still there, all of them at the 100 % end of the dial "Size of the neighbours" or under two pixels
  (section 3: A2, B, S). Nothing new of weight was found. If those three are accepted as they are, nothing I
  measured stands in the way of the merge.
- 1 Smoke: 90 of 90 steps ran and left a result, exit 0, no console errors.
- 2 Verdicts against `out/r25/klein/tree.py`, square grid, t = 1.4: the twin 0 of 20000 (in space) and 0 of 20000
  (flat cut), the same with 40 rounds; the shader 0 of 20164 (flat view) and 0 of 20480 (in space).
- 2 Six old states against the frozen page: 0 pixels differ in the picture, in all six.
- 2 First picture of the new group: 2075 ms to the first paint, 2338 ms finished (medians of 5); the first group on
  the same page 2638 and 2935 ms, on the frozen page 2625 and 2925 ms. The machine was slow while I measured (the
  others measured about 0.9 s); the new group is not slower than the old one.
- 3 Holes with the neighbours at 100 %: gone. 19 views with the eye outside every ball, 37625 rays each: no ray that
  stops nowhere goes through a ball.
- Merge rehearsal (my own page with round 26's four Learn files as they stood at 07:29): old smoke list 90 of 90,
  six old pictures 0 pixels, Learn with "A whole shape" works with Balls on balls behind it, no console errors.
  The Learn tab needs no change.

## 1. The old smoke lists

`mk/smoke27.py` -> `logs/smoke-all.log`, pictures `smoke/`. The list is put together the way round 22 ran it on
Version 18 (`out/r22/entry/NOTES.md`): `tools/smoke-v14.json` 62 steps, round 20's 5 (with round 22's one changed
line), round 22's 9 + 10 for its two entries, its second pass 3, its last step 1 = 90.

**90 steps, 90 result lines, no step without a result, exit 0, "no console errors"**, one run, 4 min 49 s.

## 2. The three numbers

### 2.1 Verdicts against tree.py (`mk/verd.py`, `mk/verd.js` -> `logs/verd.txt`)

The page is opened and the row Balls on balls is clicked; it gives mode k, group 1, t = 1.4, square grid, depth 16.

| what | points | differ from tree.py |
|---|---|---|
| twin `ballsInside`, in space, the page's depth (16) | 20000 random points of the box (749 inside) | 0 |
| twin, flat cut z = 0, depth 16 | 20000 (3544 inside) | 0 |
| twin, in space and flat cut, 40 rounds | 20000 + 20000 | 0 |
| shader (through `sampleSlice`, depth 16), flat view | 142 x 142 = 20164 grid points, moved by a random offset (2550 inside) | 0 |
| shader, in space, 20 random heights between -1.3 and 1.3 | 20 x 32 x 32 = 20480 (553 inside) | 0 |

A third voice, my own writing of the recipe of ROUND27.md section 1 in numpy: 0 differences from the twin and 0 from
tree.py in all four twin rows. The shader's points are a grid, not random points (sampleSlice reads a grid); the
square of the grid is 3.6 wide and high, so about a quarter of its points lie outside the box 3.6 x 2.6.
Only t = 1.4 and the square grid, as asked. Seen in passing at t = 1 in the 2D view (`logs/flat.txt`): the shader
differs from the twin at 36 of 360000 points at depth 16 and 54 at depth 40 (single precision at a skin; the
checkers found the same kind).

### 2.2 Six old states, pixel by pixel (`mk/same6.py` -> `logs/same6.txt`, pictures `same/`)

My own six states (not the fixer's fourteen), set by the same script on both pages:
the page as it opens; Mandelbrot, Lathe, power 3, 2D view; Julia, Mandelbulb, the rabbit's c, cut open at 0.05;
Julia, "Along once, then one plane", c = (-0.75, 0.1, 0.05), colour by escape count; Kleinian, first group, as it
opens; Kleinian, first group, list entry 3, 2D view, inside coloured by the trap.

**Picture alone (`#view`, the controls over it hidden): 0 pixels differ in all six** (862 x 701 each; 59223 to
593344 pixels of each picture are not background).

With the controls left on (`#stage`): 0 in five states, 106 pixels in "the page as it opens": two marks on the zoom
rail drawn one pixel higher. That is not the new page: the boxes of every piece of the rail are the same on both
pages to a thousandth of a pixel (`mk/rail.js`), and the frozen page differs from itself by the same 106 pixels
between runs. `logs/rail3.txt`, eight fresh runs with the two pages taken in turn: the first run of the frozen page
differs by those 106 pixels from each of the other seven (three of the frozen page, four of the final page), and
those seven agree in every pixel. (`logs/rail.txt`, three runs of one page and then three of the other: each page
agreed with itself and the two differed; `logs/rail2.txt`, one run of each: the two pages agree in every pixel.)
Seen: `same/diff-open-crop.png`.

### 2.3 Time to the first picture (`mk/speed.py` -> `logs/speed.txt`)

A fresh browser for every trial, one click, the clock from the click; three kinds in turn, 5 trials each.

| | first paint, ms | finished, ms |
|---|---|---|
| Balls on balls, by its row (final page) | 2421, 2543, 2075, 1986, 1899; median 2075 | 2683, 2796, 2338, 2246, 2147; median 2338 |
| first group, Show: Kleinian (final page) | 2638, 2338, 2272, 2741, 2785; median 2638 | 2935, 2626, 2577, 3013, 3104; median 2935 |
| first group (frozen page) | 2270, 2647, 2493, 2625, 2644; median 2625 | 2557, 2951, 2763, 2925, 2941; median 2925 |

New against old on the same page: 0.79 x (first paint), 0.80 x (finished); the slowest new trial against the fastest
old one 1.08 x. One program built per click in every trial. All numbers are about 2.5 times what the builder,
the checker and the fixer measured (0.8 to 1.1 s): other work was running on the machine. The limit of section 2.2
(no slower than twice the old group's) holds with room.

## 3. Every defect the checkers reported, on the final page

Scripts: `mk/holes.py` (3D picture; `logs/holes*.txt`, pictures `shots/holes*-*.png`), `mk/flat.py` (2D view at
100 %, saved model; `logs/flat.txt`), `mk/eyes.py` (`logs/eyes-wide.txt`, `logs/eyes-phone.txt`, pictures
`shots/eyes-*.png`), `mk/misc.py` (`logs/misc.txt`).

How the 3D picture was measured: `pick()` at every 4th pixel of every 4th row (37625 rays a view, other rays than the
fixer's). A ray that stops nowhere is walked with the exact inside test in quarter-pixel steps (my own writing of
the recipe, 300 rounds); through a ball for more than 2 px = a hole. For a ray that stops: the exact distance to the
nearest ball the search meets from the stopping point; further than 2 px and not beside a region that only the
page's depth calls solid = "in the open", and those are then probed 78 times within 2.5 px for a ball the search did
not meet. My ray geometry against the page's: the stop lies on my ray to 0.01 px in ordinary views (0.7 px where the
eye stands 0.00002 from a ball and single precision ends).

### Checker "arithmetic"

| id | was | now | measured |
|---|---|---|---|
| A1 major | holes in the 3D picture at 100 % | **gone** | 19 views with the eye outside every ball: 10 at 100 % or 99.4 % (square, honeycomb and line grid; the checker's close-up at depth 16 and 40; five eyes of my own; the start view; t = 1.003), 9 at 90.9 %, 55.56 % and 25 %. No ray stops nowhere in the 12 close-ups; in the 7 views where rays leave the picture, 400 of them walked each (183 in one): none meets a ball. Holes: 0. Seen, no black patch: `holes-t1-kiss-r16.png`, `holes-t1-kiss-r40.png`, `holes-t1003-kiss-r16.png`, `holes-t1-line-kiss-r16.png`, `holes-t1-own-far-r16.png`, `holes2-t1-own-eye-r16.png`, `holes2-t1-own-eye2-r16.png`, `holes4-t1-hex-own-eye-r16.png` |
| A2 minor | solid where there is no ball at 100 % | **still there, smaller, and said on the page** | 2D view at 100 %, 600 x 600 points of the framed view: painted although outside and nothing inside within 2 points: 504 points that the page's depth leaves undecided (63 at depth 40), which is the recipe, and 263 where the estimate reads under half a point (388 at depth 40); of those 263 a real ball smaller than my probes stands within 2 points at 201, so 62 of 360000 are left where the nearest ball the search meets is 2 to 2.4 points away. 3D, the checker's close-up: 3218 of 37625 stops stand beside a region only the depth calls solid (273 at depth 40). At 55.56 %: 0 and 0. The page says at 100: "...where the depth of the search runs out, the far balls and the places where two balls kiss come out swollen." New, small: at 99.4 % (t = 1.003) the same swelling is there (956 of 37625 stops) and that sentence is not shown, only the one about the Drawing radius |
| B minor | in the 3D picture the number given to the ray is longer than the true distance near a skin | **still there, by reading only** | `GL_BALLS`, last lines of `de()`: the certain room is not taken below `clamp(1 / uStepK, 1.25, 2)` ray thresholds; 1.25 as the page opens (ray step 0.8). The page offers no way to read that number, and I did not port the shader. What it does to the picture, measured: at 90.9 %, 55.56 % and 25 % (9 views) no stop is further than 2 px from a ball the search meets (furthest 1.8 px); between 1.3 and 2 px: 161 of 37625 and 207 of 37442 at 90.9 %, 0 to 5 a view at 55.56 % and 25 % |
| S minor | single stops in the open | **gone at 55.56 % and 90.9 %; still there at 100 % and 99.4 %** | 55.56 %, the checker's eye along the gap: 0 of 37062 stops further than 2 px (108 of 151281 before the fix); 8 more views at 90.9 %, 55.56 %, 25 %: 0. At 100 %, stops with nothing solid within 2.5 px by 78 probes: 81 of 37625 in the checker's close-up (furthest 111 px; the eye stands 0.00002 from a ball), 309 at depth 40 (31 px), 11 and 14 from my own two eyes (10 px, 3.7 px), 12 along the bar, 4 in the start view, 13 and 10 with the honeycomb grid, 0 with the line grid; at 99.4 %: 12 (7.5 px) |
| C to decide | Approach section on the page with Balls on balls | **decided as for the first group** | section not shown with either group on show; shown under Learn from both |

### Checker "eyes"

| id | was | now | measured |
|---|---|---|---|
| A major | after the click on the row the dials were above the window | **gone** | wide: picture 12 to 715, choice of group 140, note 247, three dials 380 / 494 / 629, Frame it ends at 769 of 950: all seven pieces in the window. Phone 390x800: picture 0 to 290, choice 442, note 549, first dial 682; the second dial is cut by the window's edge (796 to 830), the third and Frame it are a scroll further down. Seen: `eyes-wd-a1-right-after-the-row.png`, `eyes-ph-new-a-right-after-the-row.png` |
| B major | phone: the open list showed one and a half approaches | **gone** | list 169 px with 4 whole approaches; frozen page 170 px and 4. Seen: `eyes-ph-new-b-menu-open.png` |
| C major | untrue sentence about Three tones | **gone** | with a trap solid set from a script (1 and 2): one sentence, no Three tones sentence, the picture still draws |
| D major | Examples list neither working nor switched off | **gone (switched off with one sentence)** | the choice "In the 3D view the trap" and the Examples list are not shown; "Balls on balls has no trap solid, and so none of the examples, which are all trap solids: in this view the trap only colours the balls." Seen: `eyes-wd-cd-colour-section.png` |
| E major | another entry's table under the picture | **gone (switched off with one sentence)** | table not shown; "Balls on balls is not a rule that takes a point to a power and adds c, so it has no rows in this table." Seen: `eyes-wd-e-under-the-picture.png`. The section "One step, seen on directions" beside it still shows the approach's figures; the frozen page shows it in the Kleinian view too (`logs/misc.txt`) |
| F minor | at 100 no ball to be seen, the help said otherwise | **gone** | the sentence at 100 says what is on the screen, with its own form for the line grid and for the 2D view; at 98 % no sentence. Seen: `eyes-wd-f-100-panel.png`, `flat-t1-r16.png` |
| G minor | depth 1 to 4 looked broken | **gone** | slider from 5 to 40; a typed 1 gives 5 |
| H, L minor | helps untrue or too long | **gone** | three helps, one sentence each; the note three sentences |
| I minor | "Direction of the last step" one pale colour, no word | **gone** | one sentence in the 3D view |
| J minor | mirror discs in different colours, no word | **gone** | the first group's sentence shows for both groups |
| K minor | explanation box kept another entry's text | **gone** | with the pointer on the row the box shows the row's own four lines. Seen: `eyes-wd-k-pointer-on-the-row.png` |
| M minor | "t = 1.4" in a saved model | **gone** | a 48-cell model saved through the page's hook: "Made from: Balls on balls (slides by whole numbers and sphere inversions), neighbours 55.56 % of the middle ball, square grid, depth of search 16." |
| N minor | tooltip of Frame it | **gone** | "Move the camera to a view that shows the whole chain. A zoom limit or a Drawing radius that is in the way is moved as well." |
| O minor | Learn differed between the two groups | **gone** | Approach section and table: shown under Learn from both groups, the same after Learn from both; the row chosen under Learn leaves Learn |

Also on the final page: the old group's warnings stay silent for the new group (kleinTrouble "", kleinSwallowed
false, the old warning line and the "Start from" list not shown); Reset everything gives Mandelbrot, first group,
1.4 / square / 16. The fixer's list of controls (`out/r27/fix/mk/ui.js`, run by me on the final page,
`logs/ui-fixers-list.json`): 49 result lines, exit 0, no console errors, among them the picture export (1.04 MB)
and a 48-cell model.

Words: 36 texts of the new group read from the page and searched for the words of ROUND27.md section 4: none in a
new text. One old sentence of Version 18 (the help of the ray-step dial, which got a bracket) uses "covers" as a
plain verb.

### Things I ran into that are not on the checkers' lists

- With the eye inside a ball the picture is black. The frozen page does the same with the eye inside the Mandelbrot
  solid and inside a pearl of the first group (`logs/misc.txt`): not a fault of the new group. Two of my first
  eyes were of that kind (the rows named "inside a ball" in `logs/holes2.txt`; in `logs/holes.txt` the rows
  t1-own-eye and kiss-own-eye are those two eyes and say nothing).
- The checker's close-up eye stands inside a ball when the grid is the honeycomb (`logs/holes3.txt`). So the fixer's
  line "100 %, honeycomb, close-up: 0" was a black picture and measured nothing. With my own eyes outside every ball
  the honeycomb close-ups at 100 % and 90.9 % have no hole (table above).

## 4. Pictures for the user (in this folder; whole window, 1400x950, dark, nothing drawn on them)

Made by `mk/pics.py`: a fresh page, the Approach list opened, one click on the row; then only the camera is turned.

- `user-1-front.png`: the object in the lab from the front (yaw -90 degrees, 0.22 above the flat plane), with the
  choice of group, the note and the three dials beside it.
- `user-2-end-on.png`: along the chain, zoomed to 2.6: the buds sit four-fold round it.
- `user-3-flat-view.png`: the box "2D view" ticked: a chain of circles with buds.

I looked at all three and at the candidates I did not take (`shots/cand-*.png`: as it opens, end-on from the start
distance, from above, which looks much like the front because the buds sit four-fold).

## 5. Merge notes for the orchestrator

### 5.1 The overlay: eleven files, what each changes against base18a

| file | lines against base18a | what |
|---|---|---|
| `js/32-balls.js` | new, 266 | the whole object: names and texts, the twin `ballsInside`, `ballsEstimate` (with the spindle), `ballsReach`, start view and `ballsFrame`, `ballsTrouble`, and the scene program `GL_BALLS` (it declares its own uniforms uBT and uBGrid; `30-shaders.js` is untouched) |
| `css/86-balls.css` | new, 35 | the row and its heading in the open Approach menu (with a form for narrow windows), the choice of group, the two parts of the Kleinian panel, the sentence that stands in for the table (`body.balls-on`) |
| `body.html` | +16 -0 | Kleinian panel: `#kleinGroup` (two radios) at the top, the first group's pieces unchanged inside `#kleinOld`, new `#ballsPart` (note, warning, dials host, Frame it, reset host); one sentence `#ballsCardNote` in `section.score` |
| `js/00-core.js` | +2 -1 | `S.k` gains `group: 0, bt: 1.4, bgrid: 0, bit: 16` |
| `js/25-colour.js` | +21 -12 | `colBalls()`; no trap solid for the new group (colSolidOn, colTrapOn, colProgramNeeds, uTrapSolid) and one sentence for it; the trap-solid choice and the Three tones sentence kept to the other views; flat-cut rule and step limit for the new group; the first group's own notes kept to the first group; one sentence for "Direction of the last step" in 3D |
| `js/40-render.js` | +19 -6 | `sceneKlein()`; program and cache key 'balls'; uIter, uBT, uBGrid; for the new group twice the ray steps and the ray step up to 0.9 |
| `js/46-mesh.js` | +5 -0 | `meshWhat()`: the sentence that describes a saved model of the new group |
| `js/50-camera.js` | +8 -2 | `camBalls()`; the new group's start view in `camHome`; no list camera and no trap stand-back for it |
| `js/75-presets.js` | +4 -3 | `kleinTrouble` and `kleinSwallowed` silent for the new group; the Kleinian examples belong to the first group (`exampleFits`, `applyExample` sets group 0) |
| `js/80-ui.js` | +86 -6 | `UI_GROUPS` gains 'balls'; `refresh()` sets `body.balls-on`; `uiBallsShow`, `uiBallsInfo`; the choice of group, the three dials, Frame it, the panel reset; the row `#ap-balls` under the list (a button after `#rules`, not in `APPROACHES`); the keyboard path past the last approach; `uiResetAll` sets group 0; two brackets in the Quality helps |
| `js/90-boot.js` | +3 against `src/`, +6 against base18a | puts ballsInside, ballsEstimate, ballsReach, ballsFrame, ballsShow, ballsOn and BALLS on `window.squaringLab` |

### 5.2 Files that round 26 also changes

Compared at 07:10 and again at 08:31: `src/` differs from `base18a/` in `js/66-learn-view.js` (changed),
`js/67-learn-shape.js`, `js/68-learn-shape3d.js`, `css/67-learn-shape.css` (new) and `js/90-boot.js` (three lines
added at the end). The overlay holds none of the first four. **The one file both rounds change is `js/90-boot.js`.**

In `out/r27/entry/overlay/js/90-boot.js` round 27's lines are **26, 27 and 28** (two comment lines and the line
`if (typeof ballsInside === 'function') Object.assign(window.squaringLab, { ballsInside, ... });`), standing after
the line about `isExtreme` and before `boot();`. Round 26's lines are 35 to 37 of that file (32 to 34 of
`src/js/90-boot.js`). `diff src/js/90-boot.js out/r27/entry/overlay/js/90-boot.js` shows those three added lines
and nothing else, so today the overlay's file can be copied over `src/`'s; if round 26 touches the file again, add
the three lines before `boot();` instead.

For the other ten files `src/` equals `base18a/` today (`cmp`, eight files; the two new ones do not exist in
`src/`), so each overlay file can be copied to the same path under `src/`.

### 5.3 The Learn tab

**No change is needed.** Measured on the final page (Version 18's Learn): Learn opens the same from both Kleinian
groups, and the row chosen under Learn leaves Learn. Measured again on my rehearsal page with round 26's files
(5.5). The one thing the overlay relies on: `uiBallsShow` leaves Learn by `$('mode-k').click()`.

### 5.4 After the merge with round 26, check again

1. The old smoke lists on the merged page (90 of 90, no console errors), and round 26's own lists.
2. The pictures of old states against the frozen page, the picture alone (my six: `mk/same6.py`; the fixer's
   fourteen: `out/r27/fix/mk/same.py`). With the controls left on, the zoom rail's marks can differ by a pixel
   between two runs of one and the same page.
3. Learn with "A whole shape" on, with Balls on balls behind it and with the first group behind it: the Approach
   section and the table are on show under Learn and put away afterwards; the row Balls on balls chosen under Learn
   leaves Learn (`mk/shape.py`).
4. The twin against tree.py and the shader against the twin (`mk/verd.py`), one close-up at 100 % for holes
   (`mk/holes.py t1-kiss-r16`), and the landing after the click on the row, wide and phone (`mk/eyes.py`).
5. That `window.squaringLab` carries both rounds' names (ballsInside and learnShape3d).
6. Compile messages of the shaders and the time to the first picture: I did not hook the compiler; the arithmetic
   checker did, on the page before the fixes.

### 5.5 A rehearsal of the merge (mine, not the orchestrator's)

`dist/r27-final-merge.html` = base18a + the overlay + `src/js/66-learn-view.js` (md5 6b7be75d...),
`67-learn-shape.js` (b8516890...), `68-learn-shape3d.js` (a2975963...), `src/css/67-learn-shape.css` (d1feab5a...)
as they stood at 07:29 (the same md5 at 08:31). `dist/r27-final-r26only.html` = base18a + those four + `src/`'s
90-boot.js. Logs and pictures in `merge/`.

- Old smoke list on the rehearsal page: 90 steps, 90 results, exit 0, no console errors (`logs/smoke-merge.log`;
  12 minutes, the machine was busy).
- My six old states, rehearsal page against the round-26-only page: 0 pixels in the picture, in all six
  (`merge/logs/same6.txt`).
- Learn (`merge/logs/shape.txt`): LEARN.shape, learnShape3d and ballsInside are all on the handle; with Balls on
  balls behind it "A whole shape" starts in 3D (two pictures, 16 steps, its own test says the 3D picture is in
  order) and in 2D; the row Balls on balls chosen from there leaves Learn; Learn again, Show: Kleinian, the first
  group, Learn from the first group, Mandelbrot, Reset everything: the Approach section and the table are on show
  and put away exactly as on the final page; no console errors. Seen: `merge/shots/shape-learn-whole-shape-3d.png`.
- My list for the eyes checker's defects, on the rehearsal page (`merge/logs/eyes-wide.txt`): the same results as
  on the final page, no console errors.
- Not done on the rehearsal page: round 26's own tests, the phone, the 3D measurements, the time.

## 6. Where the user finds the entry

Open the Approach list (the button under "Approach and equation" that shows the name of the approach); at the
bottom of the open list, under the small heading "A cousin, not a rule", click **Balls on balls**. The page goes to
the Kleinian view with the picture and its three dials in the window. The other way: Show: Kleinian, then the choice
"Group" at the top of the panel "Kleinian group".

## 7. Not checked

- A real mouse, finger or keyboard; the keyboard path to the row.
- The verdicts at t = 1 and 2.5 and with the other two grids (asked for: square, 1.4 only); the distance against
  exact lists of balls; defect B as a number.
- Whether the stops "with nothing solid within 2.5 px" at 100 % sit on balls smaller than my 78 probes can find; a
  hole narrower than 4 pixels between the rays I asked.
- Sizes between 99.4 % and 100 % and between 90.9 % and 99.4 % in 3D; depths other than 16 and 40.
- The Fine / Fast / Ultra fast presets, the fly camera, extreme ranges, a lost graphics context, the published host,
  a slow graphics card (the new group may take twice the ray steps).
- The light theme (dark only); the phone beyond the open menu and the landing after the click.
- Shader compile messages. A saved model opened in another program.
- Anything against `src/` itself: the rehearsal used four files of round 26 as they stood at 07:29, and round 26
  may still change them.

## 8. Files

- `mk/run.py` (the driver), `mk/smoke27.py`, `mk/verd.py` + `verd.js`, `mk/same6.py`, `mk/rail.py`, `rail.js`,
  `rail2.py`, `rail3.py`, `mk/speed.py`, `mk/holes.py`, `mk/flat.py`, `mk/eyes.py`, `mk/misc.py`, `mk/pics.py`, `mk/shape.py` +
  `shape.js`, `shape2.js`.
- `logs/`: one `.txt` per script with the numbers above, the raw `.log` beside it. `logs/holes.txt` is the first
  pass (11 views), `holes2.txt` the second (new eyes, the 78 probes), `holes3.txt` and `holes4.txt` the other grids.
- `shots/`, `same/`, `smoke/`, `merge/`: pictures.
- Left in `dist/`: `r27-final.html`, `r27-base.html`, `r27-final-merge.html`, `r27-final-r26only.html`.
