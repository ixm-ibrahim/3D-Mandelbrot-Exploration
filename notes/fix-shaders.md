# fix-shaders: what changed in `src/js/30-shaders.js` after the testers' round

Only `src/js/30-shaders.js` was edited, and only the ray march inside `main()` in `GL_TAIL` (plus one constant).
`GL_HEAD`, `GL_ORBIT`, `GL_KLEIN`, `VERT`, `BLIT`, every uniform and every hook are as they were.
Test page: `python build.py --name fix-shaders --base base2 --use src/js/30-shaders.js`.
Scripts and pictures: `out/fix/shaders/`. Smoke test on `dist/fix-shaders.html`: exit 0, no console errors
(`out/fix/shaders/smoke.log`).

Time ran out after the user's two new items. The testers' list was read but not worked through: see "Not done".

## What was found (Douady rabbit, Julia preset, one plane, 24 iterations)

Tool: `out/fix/shaders/dbg.py` makes a copy of the shader that tints every lit pixel by how its march ended
(red: out of steps, green: closed in between an outside and an inside point, blue: estimate fell under the
threshold, white: stopped just under it from the inside). Pictures `t2-*.png` (before) and `t4-*.png` (after).

1. **The glow around the solid with the rough estimate (user item a) was a bug.** With no neighbouring orbits
   the march trusts only the sign of the estimate, and a ray that runs alongside the solid reads a tiny distance
   at every step. Its stride sat at the least stride (half a pixel), so 260 steps carried it about 0.65 units,
   less than the length of a lobe. It ran out of steps in mid-air, and the old rule "out of steps still counts
   as a hit" then shaded thin air: a smooth band hugging the silhouette, coloured by an orbit that was nowhere
   near the surface (`t2-balrough-close.png`: the red band).
2. **The estimate with neighbouring orbits reads many times too short on this solid.** That is not a bug in the
   estimate: one plane gives a solid whose surface carries very thin fins and hairs, and the estimate feels them.
   Consequence: Balanced and Fine draw the solid "one pixel of estimate" fat, which here is several real pixels,
   and the rough estimate (which only stops inside the solid) draws it thin and ragged. Left as it is: testers
   asked for the thin parts to keep their body (p5-1).
3. **Slices with the exact estimate (user item b).** No ray lands inside and none runs out of steps at Balanced
   or Fine (all blue). The march simply stopped at the first sample under one pixel, anywhere between 0.2 and
   1 pixel of estimate, a different place for neighbouring rays. Depth differs by under a pixel, but the shadow
   and crevice queries start from that point and, where the estimate reads short, their result depends on how
   far under the threshold the ray happened to stop. That gave striped and chequered patches in shaded hollows
   (`c-b0-terr.png`). With the rough estimate there are true rings on smooth flanks: hits reached two different
   ways (extrapolated from outside, or closed in from both sides) alternate in bands.

## What changed

All in the `PH_MARCH` branch of `main()`.

- **Hits are brought onto one level.** With neighbouring orbits (`uNT` 1 or 3) the surface is now defined as the
  place where the estimate reads `LEVEL` (0.8) pixels. The estimate is shifted by that amount, so the existing
  "stepped over the surface" logic works on the level. A sample under the level but outside the solid is slid
  back along the straight line between it and the last sample above the level. That costs no extra distance
  query. A sample inside the solid is closed in on as before, and the hit is then the outside end of the gap, so
  it is coloured from an orbit that leaves like every other hit. Strides are still taken from the unshifted
  estimate, so the march takes the same steps as before.
- **Rays that crawl alongside the solid get past it** (rough estimate only). Each stride in a row held at the
  least stride lets the next be a quarter of a least stride longer (counter `crawl`), never past the point where
  the surface seems to be. Reset as soon as a normal stride is taken.
- **Out of steps is a hit only near the surface** (`near`): with the rough estimate when the extrapolated
  surface is within 8 pixels or the ray already has the surface between two points; otherwise when the estimate
  reads under 3 pixels above the level. Anything else shows the background.

## Names added

| Name | Where | Meaning |
|---|---|---|
| `LEVEL` | `GL_TAIL`, constant, 0.8 | with neighbouring orbits, the estimate (in pixels) at which a ray has hit |
| `crawl` | `main()`, int | strides in a row that were held at the least stride (rough estimate) |
| `near` | `main()`, bool, per step | the surface is within a few pixels of this sample: an out-of-steps ray may count as a hit |

No new uniforms, no new state fields, no change to the contract.

## Speed (one page, old and new shaders alternated, least of 3 single full passes, `out/fix/shaders/ab.py` + `bench.json`)

| Scene | old ms | new ms | new / old |
|---|---|---|---|
| Rabbit, Balanced | 75.1 | 72.4 | 0.96 |
| Rabbit, Balanced, rough estimate | 75.7 | 56.7 | 0.75 |
| Rabbit, Balanced, close up | 267.9 | 244.0 | 0.91 |
| Default Mandelbrot, Balanced | 60.5 | 63.9 | 1.06 |
| Default Mandelbrot, Ultra fast | 8.9 | 6.9 | 0.78 |

An earlier attempt (level at 0.5 pixel, closing in with extra queries) cost 20 to 28% at Balanced and was dropped.

## Checked after the last build (`out/fix/shaders/f-*.png`, `c-f-*.png`)

- Glow with the rough estimate: gone on the rabbit at Balanced, default camera and close up
  (`c-b0-default.png` and `c-b0-close.png` before, `c-n1-default.png`, `c-n1-close.png`, `c-f-rabbit.png` after).
- **Slices at Fine: NOT cured.** The chequered patches in the shaded hollows of the rabbit close up look the same
  after the change as before (`c-b0-terr.png` before, `c-f-terr.png` after). Bringing the hit onto one level was
  therefore not the cause of those patches, or not the whole cause. The level change is harmless in the pictures
  looked at and in the timings, but its benefit is unproven: whoever continues may keep it or take it out
  (`LEVEL`, the `d -= LEVEL * e` line, the "slide back" branch and `(1.0 - LEVEL) * e`), leaving `crawl` and
  `near`, which are what removed the glow.
- Basilica and the classic Mandelbulb at power 8 at Balanced, and the default Kleinian view, draw as clean solids.
  The default Mandelbrot at Ultra fast (`f-mandel-ultra.png`) is at least as grainy as the testers' picture
  (`out/verify/p5/mandel-qUltra.png`, taken at another window size) and looks dustier round the edge. Likely
  cause: with 90 steps many rays among the thin fins run out of steps, and those now show the background where
  they used to be filled in as hits. Not compared like for like. If it is judged worse, loosen `near` for the
  rough estimate (the `8.0 * e`) or count a ray that is still crawling (`crawl > 0`) as near.
  Fine was only looked at on the rabbit; Ultra fast only on the rabbit and the default Mandelbrot.

## Not done, and what the next person should know

- **Next thing to try for the slices at Fine:** the patches sit only in shadow, so look at the shadow and crevice
  queries, not the march: they start `2e` off the surface and judge by `10 * d / ts` with an estimate that reads
  many times too short there. Switch shadows off, then crevice shading off, on `fine-close` in
  `out/fix/shaders/t5.json` to see which one draws the pattern.

- **Rings with the rough estimate remain** on smooth flanks seen at a slant (rabbit, Balanced with the rough
  estimate: `c-n1-default.png`, left). Cause as in finding 3: hits declared from outside (`ahead < e`) and hits
  closed in from both sides alternate in bands, and the sampled slope differs between them because some of its
  four samples fall inside the solid, where the estimate has another scale. Ideas not tried: end every rough hit
  the same way (always step past the surface, then close in), or take the slope from points pushed outward.
  Removing the `ahead < e` rule would lose more thin parts (p5-1), so it was kept.
- **The fat look at Balanced against the thin look of the rough estimate** (finding 2) is unchanged. A level
  lower than 0.8 makes the exact picture thinner but needs more steps.
- The last version of the rough ending (`if (!rough) t = tOut`) was built and passed the smoke test, but its
  pictures were only looked at briefly.
- **Testers' list, not started:** p5-1, p5-2, p5-3, p5-6, p5-7 (rough and one-neighbour estimates), p8b-1, p8b-2
  (Kleinian estimate; `notes/klein-kde-exact.glsl` was not adopted or tested here, so the 0.5 cap on the step
  share in `40-render.js` must stay), p9-1, p9-2 (planes = 1 was not checked on its own), p11-1 (2D mosaic
  ground), p15-2, p15-3, p15-5 (negative powers and n = 1). p5-3 (stray dots, lambda, Ultra fast) is probably
  helped by the out-of-steps rule but was not re-run.
- The first owner's debug idea is worth keeping: tinting by how the march ended found both causes in two pictures.
