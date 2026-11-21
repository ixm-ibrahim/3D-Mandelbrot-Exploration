# Round 22, section "judge": is it true, and can the user read it?

I did not do the work of the five sections. Everything below marked **[M]** is a number I computed again with my own
scripts (the orbits are the library's `rule.step`; the loops, rings, grids and counts are mine), **[S]** is seen in a
picture I opened, **[R]** is reasoned. Internal names are used here; `ANSWERS.md` and the five pictures use the
user's words only. No `src/`, no browser, nothing written outside `out/r22/judge/`.

## 1. Files

| file | what |
|---|---|
| `ANSWERS.md` | the answers to Q1..Q4 (at most six sentences each, each marked), the stretch question, "may be told / may NOT be told" |
| `1-how-a-bud-is-made.png` .. `5-new-tries.png` | the five pictures for the user, in the order of the questions (section 3) |
| `fixpics.py` | makes the five pictures from the sections' pictures (text bands only) |
| `jlib.py` | my tools: `follow` (orbit positions), `one` (one step), `arcs`, `ring` |
| `j1_buds.py` -> `j1_buds.txt` | bud census on four rings, the one-step law, a thrown-in bud followed, buds ON a bud |
| `j2_lump.py` -> `j2_lump.txt` | where the rabbit's orbits end, the height table and the box above the meeting point, walls, "along once" pieces, the resting place, along's pages |
| `j3_stab.py` -> `j3_stab.txt` | inside-out shares, the two stretch formulas, bud shapes, along against lathe, the line above the meeting point, overlap of rabbits |
| `j4_mandel.py` -> `j4_mandel.txt` | top bud arcs, along once against one plane (2,000,000 c), along against the spun flat set, pulled plane's upright copy, bud roundness, the 5.36 lift, tilted c |
| `j5_design.py` -> `j5_design.txt` | the hinged rule: equals along on the x-axis, flat check and lift test, volumes / leaks / pieces for seven c, rings round the hinge; preturn's upright page |
| `j6_extra.py` -> `j6_extra.txt` | pulled plane and along once on the rabbit; do the hinged pages last; one San Marco ring |
| `j7_places.py` -> `j7_places.txt` | places one squaring sends onto one spot, seven rules |

All runs together took under five minutes of machine time; the longest (`j2_lump.py`) 109 s.

## 2. The central claims, re-measured

### buds (all confirmed) [M, `j1_buds.txt`, `j3_stab.txt`]

| claim | theirs | mine |
|---|---|---|
| ring through the top bud of the middle body (x = 0, radius 0.6436), 2,880 places, 80 steps | lathe whole ring; oneplane 2 x 13.4; along 8 x 12.1; once 8 (13.9 / 13.1 / 12.1); pulled 4 (17.9 / 14.1) | the same, to the digit |
| ring through the side bud of the left body | along 16 (12.6, 7.6 at 26.9 deg, 4.1); once 6 (13.9, 8.4); pulled 4 (20.4, 6.9); oneplane 2 | the same |
| rings three and four steps out | along 16, once 2, pulled 4, oneplane 2 | the same (widths 8.1 / 6.6 / 8.4) |
| one-step law on the first ring | inside up to 0.0743 / outside from 0.0756 (oneplane), 0.0653 / 0.0666 (along) | 0.0743 / 0.0756 and 0.0653 / 0.0666 |
| the thrown-in bud at 26.87 deg | page at 13.2 deg, 0.0726 off; lands x = 0.0008, 0.6423 from the axis; then x = -1.4123, 0.0145 from the axis | 13.21 deg, 0.0726; 0.0008, 0.6423; -1.4123, 0.0145 |
| buds on a bud (read off a picture by them; "automatic count unreliable") | along 16, oneplane 2, once 2, pulled 2 | ring of radius 0.0807 round the stalk through the small bud's middle (found as a preimage of 0), 80 and 200 steps: along 16 arcs of 2 degrees or more (plus 4 slivers of under a degree: their "20") for the big bud in the flat, the slanted AND the upright page; oneplane 2; once 2; pulled 2 small buds (its other two arcs are the long big bud itself crossing the ring) |
| bud shapes round the left body, long : thick | along 0.91 (flat, upright), 1.47 (26.9 deg), 2.84 (slanted) | 0.91, 1.47, 2.86 |

Bud centres were not copied from the reports: I found them as preimages of 0 under z^2 - 1.

### lump (confirmed; two small differences of definition) [M, `j2_lump.txt`]

| claim | theirs | mine |
|---|---|---|
| every staying orbit of along's rabbit ends on the flat three-cycle | 8,800 of 8,800 (56^3 grid) | 400,000 random starts: 19,800 inside at 80 steps, 19,798 still there at step 729, all 19,798 within 1e-6 of a flat cycle point, height under 3e-28. Same for oneplane (5,457), once (8,273), lathe (18,215), alonghinge (7,042) |
| c = -1 + 0.2i | all on the flat two-cycle | along 6,610 of 6,610, oneplane 5,751 of 5,751 (3,000 steps) |
| Siegel disc, median height after 10 / 100 / 1,000 steps | along 0.018 / 0.0016 / 0.0006; oneplane 0.22 / 0.079 / 0.023 | along 0.018 / 0.0016 / 0.0006; oneplane 0.19 / 0.077 / 0.023 |
| height multiplier above the meeting point (heights 0.005 .. 0.6) | along 1.11 1.07 1.00 0.85 0.52 0.07 -0.33 -0.71; oneplane 1.11 .. 1.02 .. 1.06; lathe -0.55 | identical |
| box round the meeting point, share inside by height band | along 72 / 73 / 74 / 76 / 74; oneplane 66 / 58 / 34 / 4 / 0 | along 71 / 73 / 74 / 76 / 73 (and 75 above 0.3); oneplane 66 / 59 / 35 / 4 / 0 |
| wall share of the skin (96^3) | along 14.4 %, lathe 14.5 %, once 0.4 %, oneplane 0.1 % | along 14.4 %, lathe 13.6 %, once 0.8 %, oneplane 0.4 % (my count of "skin" and my box differ a little from theirs; the design section also got 0.4 % for oneplane) |
| 72.8 % of along's rabbit is not in one plane's | | 72.9 % |
| resting place of along | (-0.2764, 0.4816, +-0.0754), stretches 0.798 / 1.100 / 1.100 | the same (Newton from their value; one step moves it 6e-17) |
| pieces of "along once" | 85.51 / 7.24 / 7.24 % | 85.53 / 7.23 / 7.23 % (128^3, gaps of two cells bridged). On a 96^3 grid the same bridging joins them into one piece, so the count depends on the grid; the gap is real at 128^3 |
| where one step puts the loose pieces | all into the body round c^2 + c, median height 0.089 | all 3,074 blocks of each nearest c^2 + c, median height 0.089, largest 0.237, all inside the one-plane rabbit |
| along's pages against the flat picture | basilica 0 differ in all pages; rabbit 0 / 7,748 / 9,714 at 0 / 45 / 90 degrees | identical |
| one step of along sends 8 places onto c^2 + c, oneplane 2 | | 8 (6 off the page) and 2 (`j7_places.txt`) |

### stability (numbers confirmed; two statements wrong) [M, `j3_stab.txt`]

- Inside out: along 44.5 %, oneplane 0.0 %, lathe 49.9 %; keeps shapes 21.4 / 32.3 / 7.4 %. Confirmed.
- One plane's longest / shortest stretch = (1 + sin^2 L) / cos L: 1.241, 2.121, 4.844 measured = formula. Confirmed,
  so the briefing's "only the one-plane rule keeps angles everywhere" is indeed wrong for small balls.
- Beside along's slanted page, off-page / in-page stretch = 2 cos t - 1: seven directions, four digits. Confirmed.
- Along's image within 36.6 degrees of the lathe's (median 10.9), up to 179.8 from one plane's. Confirmed.
- Rabbit: 68.6 % of along's solid inside the lathe's, 27.0 % inside one plane's. Confirmed.
- **WRONG: "straight above the rabbit's pinch point along has no matter (reach 0.000, like one-plane) ... the lump is
  not joined there".** On the line straight above the meeting point along's rabbit is inside from height 0.030 to
  0.107 and from 0.327 to 0.599 (869 of 1,600 heights, 300 steps); only the lowest 0.03 is empty. Their "reach"
  must have stopped at the first empty point. One plane: 0 of 1,600. Lathe: 0.001 to 0.564. This agrees with the
  lump section (the space over the meeting point is filled) and removes the only disagreement between the two.
- **WRONG: "the four diagonal buds of the middle body are nearly bare (one small bud at the tip)"** [their S, from
  a cut across the x-axis]. A ring round the stalk of the slanted big bud holds 16 small buds (5.6 to 14.8 degrees
  wide, same at 80 and 200 steps), as `buds-on-a-bud.png` shows. A cut across the x-axis shows only the two that lie
  in it. The caption of `keeps-shapes.png` repeats the wrong statement, so that picture is not passed on.
- Not re-measured: the deeper generations (6.76 and 19.36 to 1), the pull at every flat cycle, away.

### mandel (confirmed) [M, `j4_mandel.txt`]

| claim | theirs | mine |
|---|---|---|
| top bud swung round the x-axis, 1,440 places, 600 steps | lathe 360; oneplane 2 x 2.75; once the same; pulled 4 x 8.75; along 4 x 26.25 + 4 x 2.25 | the same; along's wide arcs 25.75 to 26.75, and nine more slivers of one or two places (17 arcs in all) |
| along once against one plane | 8 of 2,000,000 differ | 4 of 2,000,000 (another sample); slab: 34 differ of 163,698 kept. Nearly, not exactly, the same |
| along against the spun flat set, 60,000 c | 4,071 / 4,221 / 3,708 both | 4,126 / 4,267 / 3,752; still leaking (4,379 at 80 steps) |
| pulled plane's upright cut against the flat set | 372 of 336,000, within 0.053 of the axis | 384, within 0.052 |
| top bud: sideways reach / reach along x | oneplane 0.19, pulled 0.60, along 1.77 | 0.19, 0.58, 1.75 (once 0.19; lathe never ends) |
| lift of the returning point under one plane | 5.36 | 5.36 |
| one plane with the bud's middle tilted 2 degrees or more keeps no start point | 0 of 300,000 | 0 of 300,000 at 2, 5, 20 degrees (3,933 at 1 degree, where the orbit of c also stays) |

Not re-measured: the buds of period 4 and 5, the buds on the x-axis, "21.6 % never repeat", the control rule `flip`.

### design (confirmed; it claims no winner, and there is none) [M, `j5_design.txt`, `j6_extra.txt`, `j7_places.txt`]

| claim | theirs | mine |
|---|---|---|
| alonghinge = along for c on the x-axis | 0 of 200,000 at four c | 0 of 200,000 at c = -1, -0.75, -1.7549, 0.2 |
| flat check, lift test | 0 differ; all lifted points stay | hinge, preturn, capfold45: 0 differ for M, basilica, rabbit, Siegel; lifted: 2,939 of 2,939 and 2,686 of 2,686 (hinge) |
| volumes 96^3, 80 steps, oneplane / along / hinge | rabbit 11,668 / 42,808 / 15,168; Siegel 31,584 / 43,012 / 17,790; period 4: 9,368 / 76,216 / 10,296 | 11,668 / 42,808 / 15,168; 31,584 / 43,012 / 17,790; 9,368 / 76,258 / 10,288 |
| height multiplier above the meeting point, hinge | -1.11 at every height | -1.11 at every height |
| box above the meeting point, hinge | 68.5 / 54.1 / 21.2 / 0.9 / 0.0 | 68 / 54 / 22 / 1 / 0 |
| every orbit of the hinged rabbit ends on the flat cycle | 4,436 of 4,436 | 7,042 of 7,042 |
| walls, hinge | 5.6 % | 5.7 % |
| leak 30 -> 80 steps | rabbit 0.8 %, Siegel 9.2 % | 0.7 %, 9.2 %; and the Siegel disc loses another 3.6 % between 80 and 300 steps |
| rings round the hinge (rabbit) | radius 0.46: 24 arcs, 138 degrees; 0.50: 34 arcs | 24 arcs, 137.8 degrees; 34 arcs (24 of them under one degree) |
| a page through the hinge after one / two steps | on a plane to 6.7e-16; then median 0.45 off | on the plane to 5.6e-16; then median 0.12 off in my sample (other sample box): scattered either way |
| preturn's upright page | 0 of 14,064 and 0 of 12,994 differ | 0 and 0 |
| places per spot | oneplane 2, along 4 (lump: 8 onto c^2 + c), capfold45 6, preturn 8 or 6 | oneplane 2 (none from off the page), along 4 to 8, capfold45 6, preturn 6, hinge 4 to 8 |
| "1.5 % of the hinged rabbit's blocks in pieces under 8 blocks" | 1.5 % | 0.1 % when blocks that touch at an edge or corner count as joined; I could not reproduce 1.5 % |

More on the hinged rule that the design section did not have [M]: for c = -0.6 + 0.4i (one big body, no meeting
point; the "hinge" then runs through the resting point of the flat picture) its shape is 21,454 blocks against one
plane's 37,096 and along's 36,322, in 69 pieces. It is not a candidate, and the design section does not say it is.
Nothing in the design report claims to beat along, so there was nothing to try to fail beyond this.

The design section's argument (a) [R, checked by me as an argument]: if every body is carried ONTO a body by a step
(true where the step does not fold) and every staying orbit ends on the flat cycle (measured), each body holds a
place that lands exactly on a cycle point after some steps; if only two places land on each spot of the page and
both are in the page (measured for one plane), that place is in the page, so every body is cut by the flat page.
The argument holds for one plane. For rules that fold it is not airtight, as the report says.

## 3. The pictures: read as someone who knows no mathematics

Twelve pictures were offered for the user. Five go on, in the order of the questions.

| # | file here | from | changed? | answers |
|---|---|---|---|---|
| 1 | `1-how-a-bud-is-made.png` | `buds/bud-two-steps.png` | ONE line added to the heading: what a "page" is (the book comparison). The picture speaks of pages in every row and never said what one is. Nothing else touched | Q1, Q3 |
| 2 | `2-buds-on-a-bud.png` | `buds/buds-on-a-bud.png` | copied unchanged. Its counts (16 / 2 / 2 / 2) are now measured, not only read off | Q1, Q3 |
| 3 | `3-rabbit-same-bodies.png` | `lump/lump-bodies.png` | first caption: "A wall has no thickness" replaced by "We found no gap between them" (the first was not shown) | Q2, Q3 |
| 4 | `4-why-the-bodies-run-together.png` | `lump/lump-why.png` | copied unchanged | Q2 |
| 5 | `5-new-tries.png` | `design/q4-tries.png` | four sentences added at the bottom ("What the orbits say, in short"), so that the picture answers Q4 and not only shows tries | Q4 |

Only text bands were touched (a blank band inserted, or a caption band painted over and rewritten in the same
font); I checked that the band I inserted into held no picture pixel, and opened all three changed pictures after
the change [S]. I re-rendered no computed panel; the panels are the sections' own, and I trust them as far as my
counts check them (2 / 16 / 6 big-dot groups in picture 1, 16 / 2 small buds in picture 2, the filled space in
pictures 3 and 4, the hinged rabbit's separate bodies in picture 5).

What a reader may still trip on:
- Picture 1 uses "jump" and "step" for the same thing, and in its third row "pale = from here a point stays".
- Picture 2: the pulled plane's flat-page bud is drawn as a tall oval; that is the bud being long round the x-axis.
- Picture 3: the along solid is a striped patchwork; the caption carries the meaning, the tile only shows "one lump".
- Picture 4: the trails are side views of orbits that leave the cut; a dot is every third step (said in the heading).
- Picture 5: "spine of the book" leans on picture 1's new line; the solids are rough blocks from one eye position.
  The first of the four added sentences is reasoned (a proof for rules that do not fold space), not measured.

The seven that do not go on:
- `buds/ball-rib-ring.png`: true as far as I checked (the widths and the law are the census numbers), but it is
  2,600 pixels tall, its sentences are about how fast a page turns against a point ("runs ahead twice as fast"),
  and its "ribs" row shows a solid that looks like a mess of ridges. Spare.
- `stability/keeps-shapes.png`: its first caption says the slanted buds of the middle body "come out nearly bare".
  Wrong (section 2). Its colour map is also the nearest thing to a chart in the set. Not to be shown as it is.
- `stability/rabbit-pages.png`: slices along pages through the x-axis. One plane's row ends "nothing of the rabbit's
  shape off the flat page", which a reader takes to mean the shape is thin; the slices simply miss bodies that do
  not sit on the x-axis. Misleading; not shown.
- `lump/lump-loose.png`: true and readable (re-measured: all points of the loose bodies land in the one body).
  Spare; picture 3's last row already shows the loose body. Its last sentence (why nothing joins them) is reasoned.
- `mandel/c-swung-out.png`: true (2 / 2 / 4 / 29 of 72 fit my arcs) and in plain words, but long, and about the
  Mandelbrot solid, which Q1 to Q4 do not ask about first. The best spare if the user asks about that solid.
- `mandel/bud-from-above.png`: top row true (0.19 / 0.58 / 1.75 measured) and clear; bottom row's first and last
  tiles say little. Spare.
- `design/q4-second-page.png`: true (0 of 12,994 places differ, re-measured) but it is a side finding. Spare.

## 4. What is wrong or overstated in the reports (collected)

1. stability: "above the rabbit's pinch point along has nothing; the lump is not joined there". Wrong (section 2).
2. stability: "the four diagonal buds of the middle body are nearly bare", also in the caption of `keeps-shapes.png`. Wrong.
3. lump, picture caption: "A wall has no thickness". Not shown (their own notes say so); reworded in picture 3.
4. design: "1.5 % of the hinged rabbit's blocks in pieces under 8 blocks". I get 0.1 %; the loose arcs are seen in
   the cut, but the number depends on what counts as touching.
5. design: "scattered by the second step (median 0.45)". Scattered, yes; the median is 0.12 in my sample.
6. lump: wall share of one plane 0.1 %, once 0.4 %. Mine 0.4 % and 0.8 %. Same conclusion.
7. mandel: "along: 4 arcs of 26.25 and 4 of 2.25". Plus nine slivers of one or two places; widths 25.75 to 26.75.
8. lump, pieces: "along once" is three pieces on my 128^3 grid (theirs: 160^3); on a 96^3 grid the same bridging joins them.
9. buds: the reading "a fin is a bud flattened at a fold" rests on six traced points (they say so). The stability
   section's law is measured only for buds that live on a slanted page.
10. The orchestrator's `one-step-ring.png` says the ring lands "inside the left-hand body"; x = -1.384 is in the
    small body at the far left (-1.507 .. -1.272). [R, from where the bodies of the flat basilica end]
11. Round 21: "along once has exactly one plane's Mandelbrot solid" and "bare side bodies". Both corrected by this
    round's sections and confirmed here (4 of 2,000,000 differ; six buds on the side bodies).

## 5. Not done

- I re-rendered no picture panel and drew no new picture; three of the five are the sections' pictures with text
  mended, two are unchanged copies.
- Not re-measured: later generations of the thin buds (7 and 19 to 1); the six traced fin points; the pull at each
  flat cycle; cycles off the page beyond "where do orbits end"; the Mandelbrot buds of period 4 and 5 and those on
  the x-axis; "21.6 % never repeat"; the control rule `flip`; the five failing design rules beyond the flat check
  and lift test of two of them (their spikes and dust are seen in `q4-tries.png` and the working sheets only);
  the counts for c = -1 + 0.03i and 0.1i.
- San Marco: I re-counted one ring (oneplane 2, along 8, once 8, pulled 4, lathe whole ring); my other three rings
  were badly placed (wholly inside a body) and say nothing. San Marco stays "counted, not looked at".
- The Siegel disc: only how fast orbits sink to the flat page (along, one plane) and the hinged rule's volume and leak.
- The design section's proofs were read as arguments, not written out or checked line by line.
- The lab entries (Part A) are not my section; I did not look at them.
- Cuts at 11.25, 22.5, 33.75 degrees: none made by me; my checks were rings, grids, lines and random points.
- 30 against 80 against 300 steps: done for the hinged rule on seven c and for the rabbit under four rules; the bud
  rings at 80 (and 200 for the buds on a bud, 300 for bud shapes).
