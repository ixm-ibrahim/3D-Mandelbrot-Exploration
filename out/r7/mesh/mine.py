"""Extra runs of engineer "mesh" (fix pass 7), called through drive.py: special:<name> looks here first."""
import json, os, time


def offs(page, D, v):
    return D.js(page, "type('meshOffset', '%s'); return $('meshOffset').value;" % v)


def r7base(page, prof, D):
    """mesh-4 and mesh-2 as the tester filed them, plus offset 0 on the negative power."""
    D.subject_page(page, 'rabbit')
    for off in ('0', '0.5', '2'):
        offs(page, D, off)
        D.run_job(page, prof, 'rabbit', '128', name='rabbit-128-off%s' % off)
    D.subject_page(page, 'negpow')
    D.run_job(page, prof, 'negpow', '128', name='negpow-128-def')
    offs(page, D, '0')
    D.run_job(page, prof, 'negpow', '128', name='negpow-128-off0')
    D.run_job(page, prof, 'negpow', '512', name='negpow-512-off0')
    D.js(page, "$('meshLargest').click(); return $('meshLargest').checked;")
    D.run_job(page, prof, 'negpow', '128', name='negpow-128-off0-all')
    D.run_job(page, prof, 'negpow', '512', name='negpow-512-off0-all')


def sizes(page, prof, D):
    """The standard model of the usual pictures at 128 and 512, default offset."""
    for subject in ('mandel', 'rabbit', 'julia1'):
        D.subject_page(page, subject)
        for cells in ('128', '512'):
            D.run_job(page, prof, subject, cells, name='%s-%s-def' % (subject, cells))


def neg(page, prof, D):
    """The negative power with every piece kept, at several offsets."""
    D.subject_page(page, 'negpow')
    D.js(page, "$('meshLargest').click(); return $('meshLargest').checked;")
    for off in ('0.5', '1', '2'):
        offs(page, D, off)
        D.run_job(page, prof, 'negpow', '128', name='negpow-128-off%s-all' % off)
    offs(page, D, '0.5')
    D.run_job(page, prof, 'negpow', '512', name='negpow-512-off0.5-all')
    offs(page, D, '2')
    D.run_job(page, prof, 'negpow', '512', name='negpow-512-off2-all')


def final(page, prof, D):
    """The standard models at 128 and 512, and one job each for the warnings and the readme."""
    for subject in ('mandel', 'rabbit', 'julia1'):
        D.subject_page(page, subject)
        for cells in ('128', '512'):
            D.run_job(page, prof, subject, cells, name='%s-%s' % (subject, cells))
    for subject in ('klein', 'trapsolid', 'negpow', 'cut'):
        D.subject_page(page, subject)
        D.run_job(page, prof, subject, '128', name='%s-128' % subject)
    D.subject_page(page, 'mandel')
    print('  mosaic:', D.js(page, "$('m-mosaic').click(); await sleep(300); return [L.S.mosaic, L.S.cutOn];"), flush=True)
    page.wait(D.shot.DONE, 300); time.sleep(0.5)
    page.shot(os.path.join(D.HERE, 'pics', 'mosaic.png'), '#stage')
    D.run_job(page, prof, 'mosaic', '128', name='mosaic-128')
    page.shot(os.path.join(D.HERE, 'pics', 'panel-mosaic-done.png'), '#secMesh')


def ev(page, prof, D):
    """The reproductions of mesh-4, mesh-2, mesh-3 and mesh-6 on the final build."""
    D.subject_page(page, 'rabbit')
    for off in ('0', '0.5', '2'):
        offs(page, D, off)
        D.run_job(page, prof, 'rabbit', '128', name='ev-rabbit-128-off%s' % off)
    D.subject_page(page, 'negpow')
    D.run_job(page, prof, 'negpow', '128', name='ev-negpow-128')
    page.shot(os.path.join(D.HERE, 'pics', 'ev-panel-negpow-128.png'), '#secMesh')
    D.run_job(page, prof, 'negpow', '512', name='ev-negpow-512')
    D.js(page, "$('meshLargest').click(); return $('meshLargest').checked;")
    D.run_job(page, prof, 'negpow', '128', name='ev-negpow-128-all')
    D.subject_page(page, 'trapsolid')
    D.run_job(page, prof, 'trapsolid', '128', name='ev-trapsolid-128')
    D.subject_page(page, 'julia1')
    D.run_job(page, prof, 'julia1', '128', name='ev-julia1-128')
    D.subject_page(page, 'klein')
    D.run_job(page, prof, 'klein', '128', name='ev-klein-128')
    D.subject_page(page, 'mandel')
    print('  mosaic:', D.js(page, "$('m-mosaic').click(); await sleep(300); return [L.S.mosaic, L.S.cutOn];"), flush=True)
    page.wait(D.shot.DONE, 300); time.sleep(0.5)
    page.shot(os.path.join(D.HERE, 'pics', 'mosaic.png'), '#stage')
    D.run_job(page, prof, 'mosaic', '128', name='ev-mosaic-128')
