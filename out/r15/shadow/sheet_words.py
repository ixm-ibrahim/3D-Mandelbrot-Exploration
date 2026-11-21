"""Round 15B, shadow: the words of the contact sheet (make_sheet.py). Counts are by eye, from these pictures."""

NOTE = ('Pillow from 4D (closed form), drawn by the lab\'s own 3D picture. What came out: the cut at z = 0 is exactly the flat set at every power (same pixels as Sphere inversions, one plane). '
        'In that plane the main body carries power minus 1 lobes: 1, 2, 3, 4 at the powers 2 to 5 (by eye). Off the plane there is NO count of bodies that follows the power: what stands out there are thin fins, '
        'arms and spikes in the plane y = 0, where the seams and corners of the pillow grid lie (4 arms at power 3, a crown of spikes above at the powers 4 and 5, a trunk below at power 2). '
        'The solids are lopsided above and below the plane except at power 3. Close up at power 2 the skin is streaked sheets and blades, like stirred paint, not smaller bodies. '
        'Power 3 close up (2 places): leafy buds on buds like coral on top, feathered blades at an arm\'s end.\n'
        'How far to trust these pictures (measured at power 2, 567 rays per picture): the drawn skin stands about 0.02 in front of the true set in the middle case, and on one ray in ten more than 0.1; '
        'at 1 to 5 stops in 100 a point-by-point test found nothing of the set within 0.05. Thin fins and streaks have next to nothing behind them.')


def power_row(n, lobes, what):
    return ('Power %d: the Mandelbrot solid. %s' % (n, what), [
        ('f-n%d-m' % n, 'opening view'), ('f-n%d-above' % n, 'from above (looking down the z-axis)'), ('f-n%d-below' % n, 'from below'),
        ('f-n%d-alongx' % n, 'along the x-axis (z is up)'), ('f-n%d-side' % n, 'from the side, along the y-axis (z is up)'),
        ('p4-n%d-cut' % n, 'cut at z = 0: the flat set of z^%d + c,\n%s by eye' % (n, lobes))])


ROWS = [
    power_row(2, '1 lobe (the round body on the left)', 'One lopsided block: shallow above the plane, a long trunk below it, fins along the edges. Not the same above and below.'),
    power_row(3, '2 lobes', 'Mirror-symmetric above and below. A block with 4 arms in the plane y = 0, each ending in knobbly buds, and one bunch of buds on each of the 2 lobes in the plane z = 0.'),
    power_row(4, '3 lobes', 'Lopsided the other way: tall spikes above (in the plane y = 0), knobbly buds round the lower rim. From below, 3 lobes show.'),
    power_row(5, '4 lobes', 'A crown of tall spikes above (in the plane y = 0), knobbly buds round the lower rim. From below, 4 lobes show.'),
    ('Power 2, Julia sets (camera pulled back: the solids reach far below the plane z = 0)', [
        ('f-j-basilica', 'c = -1, opening view'), ('f-j-basilica-side', 'c = -1 from the side (z is up)'), ('f-j-rabbit', 'the rabbit, c = (-0.12, 0.74, 0)'),
        ('f-j-rabbit-side', 'the rabbit from the side'), ('f-j-offaxis', 'c = (-1, 0.15, 0.1)'), ('f-j-c03', 'c = (0.3, 0, 0): a block with the flat set\nas its lid')]),
    ('Power 2, Julia sets from above, and their cuts at z = 0 (each is the flat Julia set, pixel for pixel)', [
        ('f-j-basilica-above', 'c = -1 from above'), ('f-j-rabbit-above', 'the rabbit from above'), ('f-j-c03-side', 'c = 0.3 from the side'),
        ('p4-j-basilica-cut', 'cut at z = 0, c = -1'), ('p4-j-rabbit-cut', 'cut at z = 0, the rabbit'), ('p4-j-c03-cut', 'cut at z = 0, c = 0.3')]),
    ('Close-up 1, power 2, c = -1: the top of the middle body (left three), and the skin above the point where two flat bodies touch, (-0.618, 0, 0) (right three). Camera 1, 0.25 and 0.06 away, with 14, 20 and 26 steps', [
        ('p4-close-bas-body-1', 'body: camera 1 away'), ('p4-close-bas-body-2', 'body: 0.25 away (smooth, grainy)'), ('p4-close-bas-body-3', 'body: 0.06 away (smooth, grainy)'),
        ('p4-close-bas-meet-1', 'meeting place: camera 1 away'), ('p4-close-bas-meet-2', 'meeting place: 0.25 away'), ('p4-close-bas-meet-3', 'meeting place: 0.06 away')]),
    ('Close-up 2, power 2: the rabbit, the skin of a body (left three), and the Mandelbrot solid above the place where its two flat bodies touch, (-0.75, 0, 0) (right three): streaked sheets at every depth', [
        ('p4-close-rab-body-1', 'rabbit: camera 1 away'), ('p4-close-rab-body-2', 'rabbit: 0.25 away'), ('p4-close-rab-body-3', 'rabbit: 0.06 away'),
        ('p4-close-m-bud-1', 'Mandelbrot solid: camera 1 away'), ('p4-close-m-bud-2', 'Mandelbrot solid: 0.25 away'), ('p4-close-m-bud-3', 'Mandelbrot solid: 0.06 away')]),
    ('Close-up 3, POWER 3, the Mandelbrot solid: its top, looking toward the bunch of buds on a lobe (left three), and the end of one of the four arms (right three)', [
        ('p4-close-n3-bud-1', 'top: camera 1 away'), ('p4-close-n3-bud-2', 'top: 0.25 away (leafy buds on buds)'), ('p4-close-n3-bud-3', 'top: 0.06 away'),
        ('p4-close-n3-arm-1', 'arm end: camera 1 away'), ('p4-close-n3-arm-2', 'arm end: 0.25 away (feathered blades)'), ('p4-close-n3-arm-3', 'arm end: 0.06 away')]),
]
