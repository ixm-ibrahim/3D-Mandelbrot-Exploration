# Round 13: a Learn tab (one step, shown move by move) and the picture pinned on phones

## What the user asked (2026-11-18, verbatim)

> * in the mobile view, can you have it such that the render is pinned to the top somehow so I don't have to
>   scroll after a parameter change and can just see it while I'm making changes?
> * I think it would be helpful to have a 4th learning tab, where it has a 2d and 3d option, showing the steps
>   of the visualized math that does a single iteration of any approach - this way, we can gain some visual
>   intuition.
> * On that note, back to the extension into 3d. I still don't understand how rotating about the z axis does
>   something significant in 2d but rotating about the w axis does nothing significant in 3d. Consider the 1d
>   case: how does a line rotate about the origin? well, it would appear to just flip back and forth on the
>   number line about the origin, but we can interpret what's really happening as it rotating about some hidden
>   axis, passing through some hidden space to go from one side to another. This can be extended into the 2d
>   case, right? hidden axis, hidden space, etc. [...] and then, same for the 3d case [...]

The user is not a mathematician, judges by pictures, and explores with sliders. The three "tabs" they mean are
the choices under **Show**: Mandelbrot, Julia, Kleinian. The fourth is **Learn**. Because of the third point the
Learn tab gets a **1D** option beside 2D and 3D: their own ladder (line, page, space), made visible.

## Base and files

`base13t/` (page `dist/v13t.html`) = Version 12's rules + round 12's page work as it stands + two hooks:

- `js/90-boot.js` calls `learnInit()` and `pinInit()` after `boot()` when they exist, and sets
  `window.squaringLab.learn = LEARN` and `window.squaringLab.learnPlan = learnPlan` when those names exist.
- `js/40-render.js`: `touch()` does nothing but call `learnTouch()` (when it exists) while `S.learn` is true.

**Round 13 writes new files only.** Other engineers are still working in `src/body.html`, `src/js/80-ui.js`,
`src/js/75-presets.js`, `src/js/90-boot.js`, `src/js/10-approaches.js` and `src/css/00-base.css`: do not edit any
file that already exists in `src/`. If you truly cannot do without a change to one, do not make it: describe
it exactly in your report under needs_from_others (file, the text it goes after, the text to add).

| who | new files |
|---|---|
| steps | `src/js/65-learn-steps.js` |
| view | `src/js/66-learn-view.js`, `src/css/65-learn.css` |
| pin | `src/js/85-pin.js`, `src/css/85-pin.css` |

Build: `python build.py --name r13-<you> --base base13t --use <your new files, as src/...>` (files that are not in
the base are added; JavaScript files are joined in file-name order inside one function scope, style sheets in
file-name order). Never plain `python build.py`. No git. No publishing. Scripts, logs, pictures under
`out/r13/<you>/`. `tools/shot.py` drives headless Chrome on the real GPU (`--help`; `--size WxH` sets the
window, so a phone is `--size 375x667`); set `PYTHONIOENCODING=utf-8`; one run at a time; write scripts to
files. `tools/smoke-v12.json` (58 steps, 1400x950) is the page's smoke test: read it, run it, do not change it.

Words on the page: plain, for a reader who is not a mathematician; sentence case; no em dashes; a control is
called by its label; nothing is claimed that was not measured. The page has a light and a dark theme
(`prefers-color-scheme`): use the colour tokens of `src/css/00-base.css` (`--paper`, `--panel`, `--stage`,
`--ink`, `--ink-2`, `--line`, `--brass` ...), never fixed colours.

---

## steps: the moves of one step, as numbers (`src/js/65-learn-steps.js`, no DOM)

One step of the lab is z → zⁿ + c (after the modifiers, when any is ticked). This module breaks that step into
a few simple **moves** for every approach, so that the view can play them one at a time. It is the truth the
whole tab rests on: the chain of moves must end exactly where the lab's own rule (`MATH[id]`, in
`10-approaches.js`) ends.

```js
// learnPlan({ space, id, params, n, c, abs, flip }) -> { moves: [Move], note }
//   space 1 | 2 | 3;  id an approach id;  params that approach's dials (S.param[id]);  n the power;
//   c a 3-vector;  abs [0|1, 0|1, 0|1] and flip [flip y, flip z]: the modifiers (S.abs, S.flip)
// Move = {
//   key,        // 'mirror' 'fold' 'turn' 'lean' 'spin' 'back' 'phase' 'own' 'stretch' 'shift'
//   name,       // one or two words for the list: 'Turn', 'Stretch', 'Add c'
//   say(a, b),  // one plain sentence with this point's own numbers; b = at(a, 1)
//   at(v, t),   // where the point v is after the fraction t of this move, 0 <= t <= 1; at(v, 0) = v
//   hinge(v),   // null, or a unit 3-vector: the line through the origin that this move turns v about
//   sheet(v),   // null, or [u, w]: two unit vectors that span the flat sheet v moves in
//   hidden,     // true when the point leaves the visible space on its way (the turn on a line)
// }
// learnRun(plan, v) -> [v0, v1, ..., vk]: the point after each move
// learnCheck(plan, v) -> the distance between vk and the lab's own rule applied to v (0 when the plan is true)
```

`at` is given any point, not only the one the user picked: the view also pushes a small circle of neighbours
and a grid of directions through the same move, and each of those points turns by its own amount.

Points are 3-vectors in every space (unused coordinates 0). Write r for the length, n for the power.

**On a page (space 2), every approach** (they all agree there; the note says so, and says the classic
Mandelbulb is the one that does not keep the flat plane): θ = atan2(y, x).
1. Turn: about the z-axis by t(n − 1)θ. Hinge: the z-axis. Sheet: the page.
2. Stretch: r → r^(1 + t(n − 1)).
3. Add c: v + t·c.

**On a line (space 1):** the lean φ is 0 for x ≥ 0 and 180° for x < 0.
1. Turn: in the plane of x and the hidden direction y, by t(n − 1)φ. `hidden: true`. For n = 2 a negative
   number swings through the hidden side and lands on the positive side; a positive number does not move.
2. Stretch. 3. Add c (its x only).

**In space (space 3), by approach.** Check each against `MATH[id]` and mirror its clamps and special cases.

- `mercator` (longitude λ = atan2(y, x), Mercator latitude m = atanh(z/r)):
  turn about the z-axis by t(n − 1)λ; lean: m → m(1 + t(n − 1)) along the point's own meridian (sheet: the
  z-axis and the point; hinge: the level line square to that sheet); if the Turn dial is not 0, turn about
  z by t·turn; if Lift is not 0, m → m + t·lift; stretch; add c.
- `fold`: first a fold: the turn about the x-axis that takes the point where `foldk(v, planes)` puts it (by
  t times the difference of the two spin angles; hinge: the x-axis). Then as `mercator` with no Turn.
- `lathe` (α = angle from the x-axis, u = the direction of (0, y, z)): turn: α → α(1 + t(n − 1)) in the sheet of
  the x-axis and the point; hinge: the line square to that sheet, e_x × u. If the spin multiplier is not 1,
  spin: the angle round the x-axis → that angle times (1 + t(spin − 1)). Stretch; add c.
- `tilt` (τ the tilt; a = (cos τ, −sin τ, 0) the tilted axis): the rule is turn(−(n − 1)τ about z) after the
  Lathe move about a. So: turn: the angle from a → that angle times (1 + t(n − 1)), in the sheet of a and the
  point (hinge square to that sheet); back: turn about the z-axis by −t(n − 1)τ; stretch; add c.
- `bulb` (latitude β, longitude φ, pole the z-axis): turn about z by t(n − 1)φ; lean: β → β(1 + t(n − 1)) in the
  meridian sheet (it may pass over the pole); the two phases when not 0; stretch; add c.
- `classic`: as `bulb` but the angle that is multiplied is the one measured from the z-axis.
- `split`: turn of the flat part (x, y) about z; stretch of the flat part; the height on its own: z is a
  number on a line, so its move is the line's move (it passes through 0, the shadow of a swing through a
  hidden direction); add c. For a negative power the rule ends with one sphere inversion: one more move, `own`.
- any other id (the entries under "Tried"): two moves and add c. `own`: the direction goes the short way
  round the sphere from where it is to where the rule sends it; stretch: the length goes to the rule's
  length. The note says that no simpler moves are written out for this entry.
- Modifiers, when ticked, are a first move `mirror` (a coordinate goes to its mirror value through 0).

**Tests you must run and report** (script under `out/r13/steps/`, run in the page with `tools/shot.py --js`):
for every approach id in `APPROACHES`, powers 2, 3, 5, −1, −2, 2.5, the dials at their starting values and at
two other settings each, 2,000 points: `learnCheck` at most 1e-9 times the size of the result;
`at(v, 0) = v`; no jump along a move (step t by 1/400: no step longer than 5% of the move's whole path plus a
small allowance; say where it fails, e.g. the antipode of an axis); the numbers inside `say` match `a` and `b`.
Spaces 1 and 2 against x^n and the complex power. Report every failure honestly; a plan that cannot be made
true for some power says so in its `note` and falls back to `own`.

Time: aim for 40 minutes, stop at 55.

---

## view: the Learn tab (`src/js/66-learn-view.js`, `src/css/65-learn.css`)

`learnInit()` (called after `boot()`) builds everything by script; `LEARN` is the module's state object;
`learnTouch()` is called whenever the lab's settings change (a dial of the approach, the power, a modifier).
`hooks.refresh` (see `00-core.js`) is the list of functions `refresh()` calls last: push yours onto it.

**Turning it on.** A fourth choice **Learn** under Show, after Kleinian (add the radio `mode-l` to the
`fieldset.mode`; the grid there has three columns, make it four in your own style sheet). `S.mode` keeps its
value ('m', 'j' or 'k'); Learn is `S.learn = true` beside it. `refresh()` re-ticks the radio of `S.mode` every
time it runs, so tick `mode-l` again in your refresh hook while Learn is on, and listen on the fieldset in the
capture phase so that `S.learn` is right before the page's own handlers run. While Learn is on: `body` has the
class `is-learn`; the solid's canvas, the camera overlays on the stage, the zoom buttons, the 2D view tick box
and the sections that mean nothing here (Mandelbrot, Julia and Kleinian options, Cut, Colour, View, Quality,
Save a picture, Save a 3D model) are hidden by your style sheet, never by changing their `hidden` state.
Approach, Equation (for the power) and Modifiers stay. Leaving Learn: `S.learn = false`, the class goes,
`touch()` draws the solid again. "Reset everything" also puts Learn back to its starting state.

**What the stage shows** (a second canvas inside `#stage`, Canvas 2D, sharp on high-density screens, redrawn
only when something changes or an animation runs; no WebGL):

- Space **1D · 2D · 3D** (a row of three choices at the top of the Learn panel; starts at 2D).
- The axes that the space has, the origin, a faint unit circle (2D) or unit sphere outline (3D), light grid.
- The point z as a dot with an arm from the origin; the point c as a second, differently marked dot.
- While a move plays: the hinge (a line, labelled "hinge"), the sheet the point moves in (a faint disc or
  wedge), the path the point has swept so far, and the angle or length that is changing, with its numbers
  (for example "37° → 74°", "1.20 → 1.44").
- Companions, so that the eye sees what the move does to everything near the point, not only to the point: a
  small circle of dots round the point (it shows the squash), and as a choice "Show: the point · a small
  circle round it · all directions" where "all directions" is dots on the unit circle (2D) or about 300 dots
  on the unit sphere (3D) with a few of them coloured so that they can be followed. All are moved with `at`.
- After the last move: the start as a ghost, the whole path, the new point. "Next step" goes on from the new
  point, and the orbit so far stays as a trail. When the point has run away (length over 8) the text says so.
- **The hidden direction.** In 1D and 2D a tick box "Show the hidden direction" tips the picture into a 3D
  view: in 1D the line gains the faint plane the negative number swings through; in 2D the page is seen at a
  slant with the z-axis standing on it as the hinge of the turn. It is off at first in 2D and ON at first in
  1D (without it the 1D turn is a point jumping, which is the very thing the user asked about). In 3D there is
  no such box; a line of text says that the hinge of a turn of space is, seen from 4D, a whole sheet: the
  hinge line together with the fourth direction.
- In a tipped view and in 3D, dragging turns the view (one finger on a phone), pinch or wheel zooms, a button
  resets it. In the flat 2D and 1D views dragging the dot moves the point z (and dragging the c mark moves c).
  Big enough to grab with a thumb (44 px targets).

**The transport**, directly under the stage inside `.bench-main` (the pin engineer pins that whole block on
phones, so on a phone the picture and these controls stay in view together; keep the block compact: on a
375 x 667 window the stage plus transport is at most 60% of the height while Learn is on, so give the stage a
smaller height under `.is-learn` at narrow widths):

- the sentence of the current move (`say`), in an `aria-live="polite"` line, large enough to read on a phone;
- a slider across the whole step (0 to the number of moves), so that the user can drag a move back and forth
  by hand; Play/Pause, Back one move, Forward one move, Next step, Start again; a speed choice.

**The Learn panel** in the controls column (a `details.sec` like the others, first in `#sections`):

- Space; the point z (dials for the coordinates the space has; use the page's dial kit, `buildControls` in
  `70-dial.js`, as the other panels do) and the point c; "Start at 0, like the Mandelbrot set" and "Use the c
  of the Julia tab"; Show (the companions); the list of moves as buttons (the current one marked; pressing one
  plays it); the note of the plan.
- **What to notice**, one short paragraph per space, from these facts only:
  - 1D: on a line a number leans one of two ways from the positive side: 0° or 180°. Doubling 180° gives
    360°, which is 0° again. That is why a negative number times itself is positive. To get there the point
    swings through a direction the line does not have.
  - 2D: on a page every lean from 0° to 360° exists, and the swing fits inside the page. The hinge of the
    turn is the one line the page does not have, the z-axis. Going from a line to a page is the big step: two
    leans become all of them, and the picture goes from a plain stretch of the line (from −2 to ¼) to the
    Mandelbrot set.
  - 3D: in space a point still leans away from the x-axis by one angle. What is new is the direction it
    leans in, a second angle. A turn of space needs three numbers (two to aim its hinge, one for how far), and
    a point supplies only two. Each approach fills in the missing one in its own way, which is why there are
    several approaches and no single right one. Watch the hinge: under "Quaternion square (Lathe)" it is a
    different line for every point, and it is the z-axis exactly when the point lies in the flat plane.
- If the equation is not zⁿ + c, a note: Learn shows the plain rule zⁿ + c.

**For tests**, `LEARN` carries methods that need no pixels: `LEARN.set({ space, z, c, show, hidden })`,
`LEARN.goto(move, t)`, `LEARN.next()`, `LEARN.state()` → `{ on, space, z, c, move, t, moves: [names], sentence,
point, orbit }`. Until the steps engineer's file exists, work against your own stand-in with the same
interface (`--swap js/65-learn-steps.js=out/r13/view/stub.js`), flat and `lathe` only; switch to the real file
(`src/js/65-learn-steps.js`) as soon as it is there, and report which one your final checks ran on.

Before you report: screenshots of 1D (hidden direction shown, mid-turn), 2D flat, 2D tipped, 3D under
`lathe`, `mercator`, `tilt`, `bulb` and one "Tried" entry, mid-move, at 1400x950 and at 375x667, light and
dark (`tools/shot.py --theme`); Learn on and off again leaves the solid drawn as before (same picture, no
console errors); `tools/smoke-v12.json` passes on your page.

Time: aim for 70 minutes, stop at 90.

---

## pin: the picture stays in view on a phone (`src/js/85-pin.js`, `src/css/85-pin.css`)

Today: wider than 920 px the picture column (`.bench-main`) is sticky and stays in view; at 920 px and
narrower the page is one column and the picture scrolls away, so after moving a dial the user must scroll up
to see what it did.

Wanted: at 920 px and narrower, when the window is tall enough to leave room for the controls (decide the
limit and say it; a phone held sideways is too low), `.bench-main` stays pinned to the top of the window while
the controls scroll under it. Everything through your own style sheet and `pinInit()`.

- Opaque (the page colour), above the controls, with a hairline below so the edge reads. The row
  `.toprow` in the controls is sticky at the top too: while the picture is pinned it must not slide under or
  over it (let it scroll with the page there, or stick below the pinned block; say which you chose and why).
- Compact when pinned: the hint under the picture is not needed while pinned; the status line may stay if it
  is one line. Between 621 and 920 px the picture is 58% of the window height today, too much to pin: reduce it
  while pinned so that at least 45% of the window is left for the controls. A change of the picture's height
  draws the solid again, so the height must not change while the page scrolls: only when the pin goes on or
  off or the window changes.
- The Learn tab (another engineer, same round) puts its own controls under the stage inside `.bench-main`
  and gives the stage a smaller height there. Pin the block whatever it holds, and measure it (ResizeObserver)
  rather than assume a height: publish it as a CSS variable so that
  `.dials ... { scroll-margin-top: ... }` clears the pinned block when the browser scrolls a focused control
  into view.
- A small button to unpin and pin again ("Unpin picture" / "Pin picture"), reachable with a thumb, remembered
  for the next visit (localStorage inside try/catch; the page must work with storage blocked). Pinned is the
  starting state.
- The on-screen keyboard: when a number box has focus and the visible window (`window.visualViewport`) is too
  low to show the pinned picture and the box together, the pin lets go until the keyboard closes.
- The page's buttons that scroll the picture into view (`uiShowStage()` in `80-ui.js`) must still end with
  the picture in view. Nothing changes wider than 920 px.

Before you report, on `--size 375x667`, `390x844`, `768x1024` and `667x375`: screenshots at the top of the page
and after scrolling to the Approach section and to the end of the controls; proof that the solid is not drawn
again by scrolling (the status line and `window.squaringLab.R` do not change); a dial moved while scrolled down
changes the pinned picture; focus on a control far down scrolls it clear of the pinned block; unpin and pin
again; the light and the dark theme. `tools/smoke-v12.json` passes at 1400x950.

Time: aim for 30 minutes, stop at 45.

---

## Report (every engineer)

summary; files_changed; done (what, evidence); not_done (what, why); names_added; needs_from_others; risks.
Say what you measured and what you only reasoned.
