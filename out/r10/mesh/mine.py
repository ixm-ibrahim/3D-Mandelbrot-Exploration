"""Runs of engineer "mesh" (round 10), called through drive.py: python out/r10/mesh/drive.py <page> special:<name>."""
import json, os, time


def offs(page, D, v):
    return D.js(page, "$('secMesh').open = true; type('meshOffset', '%s'); return $('meshOffset').value;" % v)


def largest(page, D, on):
    return D.js(page, "if ($('meshLargest').checked !== %s) $('meshLargest').click(); return $('meshLargest').checked;" % ('true' if on else 'false'))


def show(D, names):
    for n in names:
        p = os.path.join(D.HERE, 'runs', n + '.json')
        if not os.path.exists(p):
            print('    %s: no run' % n); continue
        r = json.load(open(p, encoding='utf-8'))
        f = r['after']['facts']
        print('    %s: Size %r | Pieces %r\n      warn: %s' % (n, f[5] if len(f) > 5 else None, f[7] if len(f) > 7 else None, r['after']['warn'] or '(none)'), flush=True)


def standard(page, prof, D):
    """The tester's seven standard jobs."""
    for subject, cells in (('mandel', '128'), ('rabbit', '128'), ('julia1', '128,256'), ('cut', '128'), ('klein', '128'), ('trapsolid', '128')):
        D.subject_page(page, subject)
        for c in cells.split(','):
            D.run_job(page, prof, subject, c)


def ex(page, prof, D):
    """t9-mesh-1 and t9-mesh-5: the three Julia examples, at the starting offset and at offset 0."""
    D.subject_page(page, 'exurchins')
    D.run_job(page, prof, 'exurchins', '128')
    D.run_job(page, prof, 'exurchins', '256')
    offs(page, D, '0'); D.run_job(page, prof, 'exurchins', '128', name='exurchins0-128')
    D.subject_page(page, 'exbubbles')
    D.run_job(page, prof, 'exbubbles', '128')
    offs(page, D, '0'); D.run_job(page, prof, 'exbubbles', '128', name='exbubbles0-128')
    D.subject_page(page, 'exarches')
    D.run_job(page, prof, 'exarches', '128')
    show(D, ['exurchins-128', 'exurchins-256', 'exurchins0-128', 'exbubbles-128', 'exbubbles0-128', 'exarches-128'])


def ex2(page, prof, D):
    """More of the same: bubbles and arches at 256, the urchins with every piece."""
    D.subject_page(page, 'exbubbles')
    D.run_job(page, prof, 'exbubbles', '256')
    D.subject_page(page, 'exarches')
    D.run_job(page, prof, 'exarches', '256')
    offs(page, D, '0'); D.run_job(page, prof, 'exarches', '128', name='exarches0-128')
    show(D, ['exbubbles-256', 'exarches-256', 'exarches0-128'])


def warn(page, prof, D):
    """t9-mesh-3 and t9-mesh-4: what the panel says."""
    D.subject_page(page, 'trapsolid')
    for c in ('192', '256'):
        D.run_job(page, prof, 'trapsolid', c)
    D.subject_page(page, 'negpow')
    for c in ('96', '128', '256'):
        D.run_job(page, prof, 'negpow', c)
    largest(page, D, False)
    D.run_job(page, prof, 'negpow', '128', name='negpow-128-all')
    D.subject_page(page, 'mosaic')
    D.run_job(page, prof, 'mosaic', '128')
    show(D, ['trapsolid-128', 'trapsolid-192', 'trapsolid-256', 'negpow-96', 'negpow-128', 'negpow-256', 'negpow-128-all', 'mosaic-128'])


def big(page, prof, D):
    """The large ones: trap solid and power -2 at 512, the Kleinian view at 512 with every piece at offset 0 (PLY only, zip not kept)."""
    D.subject_page(page, 'trapsolid')
    D.run_job(page, prof, 'trapsolid', '512')
    D.subject_page(page, 'negpow')
    D.run_job(page, prof, 'negpow', '512')
    D.subject_page(page, 'klein')
    D.js(page, "for (const id of ['meshStl', 'meshObj']) if ($(id).checked) $(id).click(); return 1;")
    offs(page, D, '0'); largest(page, D, False)
    D.run_job(page, prof, 'klein', '512', name='klein-512-allpieces-offset0', keep_zip=False)
    show(D, ['trapsolid-512', 'negpow-512', 'klein-512-allpieces-offset0'])


def cut0(page, prof, D):
    """The thin coloured line round a cut face at offset 0 (round 9, item 1): the opening solid cut at z = 0, seen from above."""
    D.SUBJECTS['cutm'] = "$('cutOn').click(); await sleep(200); L.cam.pitch = 1.05; L.touch(); await sleep(200); return 'cutOn ' + L.S.cutOn + ' at z = ' + L.S.cut + ', pitch ' + L.cam.pitch;"
    D.subject_page(page, 'cutm')
    D.run_job(page, prof, 'cutm', '128')
    offs(page, D, '0'); D.run_job(page, prof, 'cutm', '128', name='cutm-128-off0')
    offs(page, D, '2'); D.run_job(page, prof, 'cutm', '128', name='cutm-128-off2')


def add(page, prof, D):
    """A trap that is added to the solid (opening Mandelbrot set with the sphere shell): the set's own thin parts and the trap's layers together."""
    D.subject_page(page, 'trapadd')
    D.run_job(page, prof, 'trapadd', '128')
    show(D, ['trapadd-128'])
