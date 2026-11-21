"""Round 23, judge: the three pictures for the user. Captions were written AFTER looking at look-1/2/3.png, and every
sentence says something that is seen in the tiles or measured in j1 .. j5 (NOTES.md says which).
Words follow docs/ROUND23.md section 4: at most two short sentences per caption, no internal names."""
import os


def make(sheet, four, COLS4, HERE):
    # ------------------------------------------------------------------ 1
    rows = [
        ('Two planes', 'c = -1: clean, blown-up bodies with crisp buds in four directions. Rabbit: it breaks into shards.', four('twoplane')),
        ('Along', 'c = -1: eight buds round every body, and buds on the buds. Rabbit: one swollen, ribbed lump.', four('along')),
        ('Along once, then one plane', 'c = -1: all eight buds on the middle body, fewer on the others. Rabbit: separate bodies, but the biggest extra body floats free of the rest.', four('alongonce')),
        ('New try, used for the first step only: the flat picture a second time, rolled up into a cone above and below',
         'Smooth, separate bodies; the extra round ones touch the middle body at single points. But they lean to one side, and only the middle body carries them.', four('cones1')),
        ('The same new try, used at every step', 'The extra bodies are still there, but everything is buried under scales and loose flakes.', four('cones')),
    ]
    sheet(os.path.join(HERE, '1-shapes.png'), 'The two favourites, "along once", and the best new try of this round', rows, COLS4,
          intro='Real shapes, drawn as rough blocks. Left half: c = -1. Right half: the rabbit. Each is shown from the front and from above.')
    # ------------------------------------------------------------------ 2
    two = lambda nm: [(nm, 'basilica', 'a'), (nm, 'rabbit', 'a')]
    rows = [
        ('Msltoe, about 2010: square about the nearer of two planes', 'c = -1: the same look as our "two planes". Rabbit: nothing survives at all.', two('o:sym2') + two('twoplane')),
        ('Eiffie, 2015: the same idea with four planes', 'c = -1: eight buds round each body, the look of our "along". Rabbit: one lump.', two('o:eiffie') + two('along')),
        ('Mandelbulb, power 2', 'Flakes and whiskers on both shapes.', two('o:mb2') + [None, None]),
        ('Bristorbrot', 'c = -1: four-sided, ridged bodies. Rabbit: one ridged slab.', two('o:bristor') + [None, None]),
    ]
    sheet(os.path.join(HERE, '2-what-others-found.png'), 'What others found (formulas taken from the program Mandelbulber)', rows,
          ['theirs, c = -1', 'theirs, rabbit', 'ours, c = -1', 'ours, rabbit'],
          intro='Left: their shapes. Right: our nearest rule, for comparison. None of the 17 formulas we could pin down has a rabbit with round buds all over; the Mandelbulb\'s own author writes that it is not the real thing.')
    # ------------------------------------------------------------------ 3
    rows = [
        ('"Along" for the first 1, 2, 3 steps (then one plane), and for every step',
         'One step: separate bodies. Each further step makes them run together, until the rabbit is one lump.',
         [('alongonce', 'rabbit', 'a', 'first step only'), ('r:along2', 'rabbit', 'a', 'first 2 steps'), ('r:along3', 'rabbit', 'a', 'first 3 steps'), ('along', 'rabbit', 'a', 'every step')]),
        ('The new try for the first 1, 2, 3 steps (then one plane), and for every step',
         'One step: smooth round bodies. More steps: stretched bodies, then thin blades, then a crust.',
         [('cones1', 'rabbit', 'a', 'first step only'), ('cones2', 'rabbit', 'a', 'first 2 steps'), ('cones3', 'rabbit', 'a', 'first 3 steps'), ('cones', 'rabbit', 'a', 'every step')]),
    ]
    sheet(os.path.join(HERE, '3-one-step-against-every-step.png'), 'The rabbit: what one special step does, and what repeating it does', rows, ['', '', '', ''],
          intro='Both tricks give separate bodies when they are used for one step, and both spoil the rabbit when they are used again and again. A rule that can do the same thing at every step is what is still missing.')
