"""Runs of engineer "mesh" (round 9), called through drive.py: python out/r9/mesh/drive.py <page> special:<name>."""
import json, os, time


def offs(page, D, v):
    return D.js(page, "type('meshOffset', '%s'); return $('meshOffset').value;" % v)


def largest(page, D, on):
    return D.js(page, "if ($('meshLargest').checked !== %s) $('meshLargest').click(); return $('meshLargest').checked;" % ('true' if on else 'false'))


def only_ply(page, D):
    return D.js(page, "for (const id of ['meshStl', 'meshObj']) if ($(id).checked) $(id).click(); return [$('meshStl').checked, $('meshObj').checked, $('meshPly').checked];")


def standard(page, prof, D):
    """The tester's seven standard jobs."""
    for subject, cells in (('mandel', '128'), ('rabbit', '128'), ('julia1', '128,256'), ('cut', '128'), ('klein', '128'), ('trapsolid', '128')):
        D.subject_page(page, subject)
        for c in cells.split(','):
            D.run_job(page, prof, subject, c)


def cutface(page, prof, D):
    """Item 1: a cut solid seen so that the cut face fills the picture (from above, a little tilted), three solids."""
    for subject, pre in (('cutm', ""), ('cutj', "$('mode-j').click(); await sleep(300); pick('juliaPreset', 'Basilica'); await sleep(200); $('juliaFrame').click(); await sleep(200);"),
                         ('cutr', "$('mode-j').click(); await sleep(300); pick('juliaPreset', 'Douady rabbit'); await sleep(200); $('juliaFrame').click(); await sleep(200);")):
        D.SUBJECTS[subject] = pre + "$('cutOn').click(); await sleep(200); L.cam.pitch = 1.05; L.touch(); await sleep(200); return 'cutOn ' + L.S.cutOn + ' at z = ' + L.S.cut + ', pitch ' + L.cam.pitch;"
        D.subject_page(page, subject)
        D.run_job(page, prof, subject, '128')
        if subject == 'cutm':
            D.run_job(page, prof, subject, '256')
            offs(page, D, '0'); D.run_job(page, prof, subject, '128', name='cutm-128-off0')
            offs(page, D, '2'); D.run_job(page, prof, subject, '128', name='cutm-128-off2')
    # the cut face painted by the inside colouring
    D.SUBJECTS['cutp'] = "$('cutOn').click(); await sleep(200); L.cam.pitch = 1.05; L.touch(); await sleep(200); const e = $('col-cutFace'); if (!e) fail('no col-cutFace'); if (!e.checked) e.click(); await sleep(200); pick('col-inMode', 'How deep inside'); await sleep(200); return 'cut face painted: ' + e.checked + ', inside by ' + L.S.colour.inMode;"
    D.subject_page(page, 'cutp')
    D.run_job(page, prof, 'cutp', '128')


def first(page, prof, D):
    """Item 2: what the progress line says while the first model of a formula waits for its program."""
    for subject in ('mandel', 'klein', 'negpow'):
        D.subject_page(page, subject)
        D.run_job(page, prof, subject, '128', name='first-%s-a' % subject)
        D.run_job(page, prof, subject, '128', name='first-%s-b' % subject)
        rec = [json.load(open(os.path.join(D.HERE, 'runs', 'first-%s-%s.json' % (subject, x)), encoding='utf-8')) for x in 'ab']
        for r in rec:
            print('    %s: %.2f s: %s' % (r['job'], r['seconds'], ' | '.join('%.2f %s' % (l[0], l[1]) for l in r['line'][:6])), flush=True)


def neg(page, prof, D):
    """Item 3 (mesh-2): the negative power at three resolutions, starting offsets 0.5, 1 and 1.5, largest piece and every piece. PLY only."""
    D.subject_page(page, 'negpow')
    only_ply(page, D)
    cells = os.environ.get('NEG_CELLS', '128,256,512').split(',')
    offsets = os.environ.get('NEG_OFFS', '0.5,1,1.5').split(',')
    for c in cells:
        for off in offsets:
            offs(page, D, off)
            for keep in (True, False):
                largest(page, D, keep)
                D.run_job(page, prof, 'negpow', c, name='negpow-%s-off%s-%s' % (c, off, 'largest' if keep else 'all'))


def warn(page, prof, D):
    """Item 3: what the panel says for a solid finer than the grid, and that the other warning is as it was."""
    D.subject_page(page, 'negpow')
    D.run_job(page, prof, 'negpow', '128', name='warn-negpow-128')
    largest(page, D, False)
    D.run_job(page, prof, 'negpow', '128', name='warn-negpow-128-all')
    D.run_job(page, prof, 'negpow', '256', name='warn-negpow-256-all')
    D.subject_page(page, 'mandel')
    print('  mosaic:', D.js(page, "$('m-mosaic').click(); await sleep(300); return [L.S.mosaic, L.S.cutOn];"), flush=True)
    page.wait(D.shot.DONE, 300); time.sleep(0.5)
    D.run_job(page, prof, 'mosaic', '128', name='warn-mosaic-128')
    for n in ('warn-negpow-128', 'warn-negpow-128-all', 'warn-negpow-256-all', 'warn-mosaic-128'):
        r = json.load(open(os.path.join(D.HERE, 'runs', n + '.json'), encoding='utf-8'))
        print('    %s: Pieces %r\n      warn: %s' % (n, r['after']['facts'][7] if len(r['after']['facts']) > 7 else None, r['after']['warn']), flush=True)
