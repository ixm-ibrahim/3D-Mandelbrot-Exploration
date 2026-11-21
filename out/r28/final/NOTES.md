# Round 28, Track A ("dials"): the final check

Page checked: `dist/r28-final.html`, built by me with the command of `out/r28/dials/BUILD.txt` under the name
`r28-final` (md5 4b03c1dc..., byte for byte the fixer's `dist/r28-fix.html`). Frozen page: `dist/r28-base-final.html`
(`build.py --name r28-base-final --base base20a`, md5 e741102e..., byte for byte `dist/r28-base.html`).
I did not build or repair this page and I changed nothing in the overlay. Everything of mine is in `out/r28/final/`.
Every number below comes from a script kept there and its log. "Seen" means I opened the picture.

## In plain lines

1. **Verdict: READY.** No major defect is left, and every picture with two equal spheres is the same to the pixel
   as on Version 20 (0 pixels differ).
2. Both majors are gone. The fans and bumps in the 2D view with the second sphere at 50: 12 views, 0 pixels
   painted where nothing is, and I looked at the pictures. Frame it in low, wide windows: 40 pictures in 8 windows
   (the three that were cut, two lower ones, the two the brief names, a tall one), 0 cut.
3. It is an object: on lists of balls for 6 settings of my own (3 million balls) no two balls cut into each other
   and the recipe agrees with the list; a second sphere of 70 % does cut (3 of 3).
4. One recipe, three voices, 6 settings of my own (4 of them with a smaller second sphere and neighbours past 100):
   the twin against the plain recipe 0 of 240000, the shader against the plain recipe 0 of 245292.
5. The distance is safe: never longer than the true distance to the nearest listed ball at 480000 points. The
   fixer's new room (the side spindle) holds no ball: 4.9 million points of it put to the plain recipe, 0 inside.
6. The picture is whole past 100: 16 views (10 wide dark, 3 wide light, 3 phone light), 513432 rays, 0 holes, 0
   stops in the open, 0 rays through a ball. I opened every picture.
7. Old pictures: 16 states (10 of Balls on balls with two equal spheres, 6 others) wide dark and again phone
   light: 0 pixels differ in each. The Learn tab, whole window: 0.
8. Old lists: the smoke list (90 steps), round 26's three lists and round 27's five scripts pass on the new page as
   on Version 20. No console error in any of my runs (about 74 browser launches, none stalled).
9. The dials, with real mouse, keys and finger: wide 127 right and 1 marked wrong that is the test's timing (shown
   below), phone 125 right and 0 wrong. 3000 random moves: no rule broken.
10. Speed: the first picture at the default takes 0.84 times what the frozen page takes (medians of 5, in turn).
11. What is left is minor: two faint things in the lighting, the length and place of the sentences, and four
    decisions that are the orchestrator's (the "follows" of the size dial first among them). Listed under "What is
    left".

## The overlay: every file, one line each

All under `out/r28/dials/overlay/js/` (five files, all JavaScript; no CSS, no `body.html`, no `90-boot.js`). Lines
against `base20a` from my own comparison (`logs/overlay-diffstat.txt`).

- `00-core.js` (2 lines in, 1 out): one new number in the state, `S.k.brho: 1`, the second sphere's radius.
- `32-balls.js` (384 in, 39 out): the recipe, the twin and the distance take the second sphere; the two give-way
  rules of the dials; reach, start view and Frame it for larger neighbours; the status sentences; and a second
  program text `GL_BALLS_RHO` for a smaller second sphere. Version 20's program text `GL_BALLS` is the same to the
  byte (5938 characters, `logs/frozen-text.txt`).
- `40-render.js` (15 in, 4 out): the second program under its own key `balls2`; the number t is held where the two
  spheres touch at the least; the other Balls program is prepared in the background while this entry is on show.
- `46-mesh.js` (3 in, 1 out): the sentence of a saved 3D model names the second sphere when it is not 100.
- `80-ui.js` (66 in, 9 out): the size dial to 400 (typed to 2000), the depth dial from 1 to 100 (typed to 1000),
  the new dial "Second sphere, % of the first" with its jump between 50 and 100, its help and its tooltips; "its
  three dials" became "its dials" beside the row of the Approach list.

Since the three checkers saw the page, only `32-balls.js` and `80-ui.js` changed (the fixer). The other three are
byte for byte what the checkers tested.

## What is left

Nothing major. Minor, and for the orchestrator to weigh:

1. **The "follows" of the size dial (D4): still there, a decision.** Once the size dial has set the second sphere,
   moving the size keeps moving it: 150 then 250 gives 20 (the bare formula of 1.2 point 4 keeps 33.33); back to
   90 gives 50 and it stays. In 3000 random moves the second sphere moved 630 times with the size, 278 of them
   without having to. Every such state is an object. A sentence now says so ("It follows the size until you set it
   yourself."). To get the bare formula: drop `|| (BALLS_DIAL.follows && rho < 1)` in `ballsSetShare`.
2. **Sentences beyond the list of decision 6**, each answering a reported defect: "Here the chain is too long for
   one picture, so Frame it shows a stretch of it."; "The Drawing radius in the View section cuts the two big
   neighbours open. Frame it makes room for them."; "With the second sphere at 50 the buds on a neighbour kiss, and
   where the depth of the search runs out those places come out swollen."; and two add-ons, "It follows the size
   until you set it yourself." and "With a single round most of the picture is one wall of colour.". Decision 6's
   own sentences stand word for word. No word of section 4's forbidden list in any of them (`logs/vocab.txt`).
3. **"Within rounding" is the fixer's reading**: the "never ends" sentence shows where the two shown numbers
   multiply to 100 x 100 within their two decimals (33.33 with 300: yes; 50 with 199.9: no, it gets "too long").
4. **A typed size with more than two decimals** counts as shown when the second sphere is smaller (100.004 reads
   100 and is 100; 100.006 reads 100.01 and gives way); with two equal spheres it is taken as it came.
5. **E2, pale patches on the bare skin of a large neighbour: still there, minor.** 98.7 against 101.7 of 255, gone
   with shadows off (the same numbers as before the repair). Seen at 400 with the second sphere at 25, faint.
6. **E4, black crescents beside the middle ball at 1000: still there, minor.** Seen. The lab's own lighting.
7. **The sentences can add up (D6 d): still there in part, minor.** The checker's case is 404 characters (was
   504). The longest block I could make (second sphere 50, size 199.8, depth 1, Drawing radius 2) is 607
   characters, 223 px high; it stays inside the panel, wide and phone.
8. **On the phone the sentences stand above the dials (D6 e): still there in part, minor.** With the size dial in
   the middle of the window they are in sight (seen); scrolled further up they go behind the pinned picture.
9. **A chain too long to frame with two equal spheres (size 99): as on Version 20.** Left so on purpose.
10. **Threads that only the depth of the search calls solid can be passed by a ray.** In two close views of a bud
    kiss 13 rays do (before the repair: 1), and 55 at the rim of the two swollen lobes where the spheres touch (55
    before the repair as well). None goes through a ball. Not seen as a fault in the pictures.
11. **Limits, unchanged**: hair points in the flat cut and far balls in single precision; shader and twin apart at
    single points of Version 20's own program (1 of 21609 in my setting with two equal spheres; never too long).
12. The dial checker's remark that "second sphere" may not be plain to a non-mathematician stands. Not a defect.

Not done by me: the dials were driven in the dark theme only (the fit of the panel in all four layouts); the saved
picture and the saved 3D model on the wide window only; the truth checker's 90 lists and 20 settings were not
repeated (6 and 6 of my own instead).

## Section 1.4, measured once more

| | what | reused / mine | script, log | result |
| --- | --- | --- | --- | --- |
| a | no two balls cut; recipe = list | truth checker's `a_object.py`, `tkit.py`; settings mine | `mk/a5.py`, `truth/logs/a_object.txt` | 6 settings (two equal spheres 55.56 square, 75 honeycomb; second sphere 50 at 150 square and 120 honeycomb; 20 at 480 honeycomb; 33.33 at 150 line), 2966578 balls: 0 pairs cut. 120000 points: outside but in a listed ball 0; a ball large enough and not listed 0; 12 in balls below the list's size. 70 %: cut in 3 of 3 (deepest 0.066 to 0.111). |
| b | three voices | truth checker's `bc_page.py`; settings mine | `mk/bc5.py`, `truth/logs/bc_summary.txt` | 6 settings (A as the page opens; 80 honeycomb; 150 / 50 square; 120 / 50 honeycomb depth 24; 210 / 45 line; 480 / 20 square depth 30). Twin against plain recipe 0 of 240000; twin with nothing passed the same; shader against plain recipe: flat 0 of 122412, in space 0 of 122880. |
| c | the distance | the same | the same | `ballsEstimate` longer than the true distance: 0 of 480000 (box, mid, top, edge; 6 settings). Shader's own number beyond single precision: 0 of 120337. |
| c | the side spindle | mine | `mk/side7.py`, `logs/side7.txt` | 108 settings (second sphere 50 down to 2, three grids), 4895878 points of it: 0 inside by the plain recipe. A spindle 1.5 times as wide: points inside in 10 settings, so the test can fail. Reasoned by me as well: the argument above `GL_BALLS_RHO` holds. |
| c | rays | eyes checker's `rays.py`, `walk.py`; 3 views mine | `logs/walk-summary.txt` | 16 views past 100: HOLES 0, IN THE OPEN 0, through a ball 0; 70 rays pass a depth-only thread (see 10 above; `logs/walk-summary-before-the-fixer.txt`). Picture against the rays: 0 patches either way. |
| c | 2D view | eyes checker's `flat2.py`; 4 views mine | `logs/q1-flat2.txt` | 12 views (second sphere 50, 49.9, 49; three grids; depth 16, 40, 100): 0 ghost pixels, 0 holes; twin against recipe 0 of 604262 in each. |
| d | old pictures | eyes checker's `same.py`, `same_twice.py` | `eyes/logs/same-1400x950-dark.txt`, `same-390x800-light.txt` | 16 states, picture alone: 0 pixels, wide dark and phone light. Learn tab, whole window: 0. Whole window wide: 26 pixels in one row of two states, the zoom handle; the frozen page differs from itself there by 9, 17, 28 (`eyes/logs/same-twice.txt`). Phone: three windows stand scrolled elsewhere, the same content (`logs/phoneshift.txt`, seen). |
| e | smoke list | dial checker's `smoke28.py`, `cmp_smoke.py` | `ui/logs/smoke-new.log`, `cmp-smoke.txt` | 90 steps, 90 results, exit 0, no console errors. 87 lines word for word the frozen page's; 2 a gliding camera, 1 counts 79 dials (78). 51 of 54 pictures the same; the 3 others were caught while drawing (one seen: only the status line differs). |
| e | round 26, round 27 | dial checker's `old26.py`, `old27.py` | `mk/cmp_old.py`, `logs/cmp-old.txt` | use, spot, phone: exit 0, the kept lines of Version 20 but for clock values. verd, shape, same6, flat, holes: every line letter for letter the dial checker's, which he held against Version 20's. |
| f | the dials | dial checker's `f1.py`, `words.py`, `fuzz.js` | `ui/logs/f1-*.txt`, `words-*.txt`, `fuzz.json` | Wide: 127 OK, 1 WRONG (typed 5000: the mark "clamped" was gone when read). The mark is a flash of 1.4 s and the picture took longer; read at once it is there 3 of 3 (`mk/flag5000.py`, `logs/flag5000.txt`). Phone: 125 OK, 0 wrong. Panel fits in 20 states, four layouts. 3000 moves: no rule broken. |
| f | small defects | mine, real input | `mk/small7.py`, `logs/small7-wide-second.txt`, `small7-phone.txt` | 26 OK and 0 wrong, wide and phone. (My first wide run typed the Drawing radius into a folded section; kept as `small7-wide-first-run.txt`.) |
| f | states by hand | mine | `mk/byhand.py`, `logs/byhand.txt` | 70 % is drawn as 50, 90 % as 100, t below touching as touching, 1 % as 2: twin and shader 0 of 4096 apart in each. |
| g | speed | eyes checker's `speed.py` | `eyes/logs/speed-first-1400x950.txt`, `speed-past-1400x950.txt` | First picture: new 2072 ms, frozen 2462 ms (medians of 5): 0.84 times; background preparing off: 0.78 times. 150 right after the first picture 1.5 to 1.6 s, 5 s later 0.9 to 1.0 s; 300: 0.6 to 0.8 s; Frame it 0.3 to 0.6 s. Loaded machine. |

Nothing outside `out/r28/final/` and my two pages in `dist/` was written (`logs/untouched.txt`).

## Every defect the checkers reported

| id | now | how I know |
| --- | --- | --- |
| E1 (major) 2D fans and bumps at 50 | **gone** | 12 views, 0 ghosts (were 142, 388, 152, 1434, 99, 77); seen `eyes/shots/dw-p150-r50-2d.png`, `dw-p200-r50-2d.png`, `dw-p150-r50-2d-budkiss-d100.png`. A sentence speaks of the swollen kiss in 3D. |
| D1 (major) Frame it in low, wide windows | **gone** | 40 of 40 whole, 0 edge pixels, 0 probes on the rim; seen `ui/shots/sizes2-new-844x390-size-400.png`, `-915x412-size-300.png`. |
| D2 touching within rounding | gone | 33.33 with 300: "At 300 the chain never ends ...", 3D, after Frame it, 2D. |
| D3 a number typed again | gone | 150, 33.33 typed again (Enter or Tab), 200: stays 33.33. A click and Escape: still follows. |
| D4 "follows" | still there, minor: a decision | see "What is left" 1 |
| D5 typed 100.004 | gone | reads 100, second sphere 100, t exactly 1, Version 20's sentence. |
| D6 a tooltips of the second sphere | gone | "From 2 to 50, or 100"; the steps tell of the gap, not doubled after the dial moved. |
| D6 b "far ends are not drawn" at 2000 | gone | the neighbours and Frame it are named; gone after Frame it. Seen. |
| D6 c help of the size dial | gone | one sentence, 38 words. |
| D6 d long block | still there in part, minor | 404 characters, 142 px (was 504, 182) |
| D6 e phone, sentences above the dials | still there in part, minor | see "What is left" 8 |
| D7 chain too long, not touching | gone for a smaller second sphere; as Version 20 for two equal spheres | sentence in 3D and 2D at 199.8 with 50 |
| E2 pale patches | still there, minor | 98.7 against 101.7; `eyes/logs/skin.txt` |
| E3 depth 1 is a wall, not shells | gone | add-on sentence at depth 1 only; seen `ui/shots/f1-wide-dark-depth-1.png` |
| E4 black crescents at 1000 | still there, minor | seen `eyes/shots/dw-p1000-start.png` |
| truth 1: spindle as written in 1.3 | not the page's | the page uses the right one |
| truth 2: size moves the second sphere more often | = D4 | |
| truth 3: hair points in the flat cut | a limit, minor | 0 of 122412 in my six settings |
| truth 4: one launch that stood still | not seen | about 74 launches |
| truth 5: states by hand only | gone | `logs/byhand.txt` |
| truth 6: far balls, single precision | a limit, minor | not measured again |

## The pictures for the user

Real screenshots of the lab, light theme, 1400x950, nothing drawn on them (`mk/pics2.py`, `logs/pics2.txt`; the
size typed and Frame it pressed with real keys and mouse). I opened all three: whole balls, no holes, the dials and
the sentence in sight beside the picture.

- `out/r28/final/user-1-150.png`: "Size of the neighbours at 150. The two neighbours are now larger than the
  middle ball."
- `out/r28/final/user-2-300.png`: "Size of the neighbours at 300. The buds on the neighbours are smaller and stand
  further apart."
- `out/r28/final/user-3-along.png`: "The same object at 150, seen along the chain."

What the eye should know (seen by the dial checker, still so): the picture jumps at 100; after a long drag the
neighbours fill the picture until Frame it is pressed; back below 100 the old look returns only with "Reset this
section" (a sentence says so).

## Files (all under out/r28/final/)

- `mk/adopt.py`: the three checkers' own scripts copied to `truth/mk`, `eyes/mk`, `ui/mk`, pointed at my page and
  folder, nothing else changed (I added seven views of my own to my copy of `eyes/mk/views.py`).
- Mine: `mk/a5.py`, `bc5.py`, `side7.py`, `small7.py`, `d1.py`, `byhand.py`, `flag5000.py`, `rays_before.py`,
  `cmp_old.py`, `phoneshift.py`, `sumwalk.py`, `vocab.py`, `pics.py`, `pics2.py`; `mk/q1.sh` to `q7.sh` are the
  order the browser scripts ran in, one at a time.
- `logs/`, `truth/logs/`, `eyes/logs/`, `ui/logs/`; pictures in `eyes/shots/`, `ui/shots/`, `shots/`, `cand/`.
