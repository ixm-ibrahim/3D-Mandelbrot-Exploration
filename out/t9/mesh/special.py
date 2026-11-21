"""The special runs of tester "mesh": cancel and a second job, changing everything while a job runs, panel options."""
import json, os, time

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = "const vis = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };"


def note(name, data):
    with open(os.path.join(HERE, 'runs', name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print('  %s: %s' % (name, json.dumps(data, ensure_ascii=False)), flush=True)


def cancel(page, prof, D):
    D.subject_page(page, 'klein')
    out = {}
    out['start'] = D.js(page, VIS + "window.__files = []; window.squaringLabSaveHook = (name, blob) => { window.__files.push({ name, blob }); };"
                              "$('secMesh').open = true; pick('meshCells', '512'); $('meshStart').focus(); $('meshStart').click(); await sleep(60);"
                              "return { busy: L.meshBusy(), focus: document.activeElement.id, cancelShown: vis('meshCancel'), startShown: vis('meshStart'), bar: $('meshBar').getAttribute('aria-valuenow') };")
    time.sleep(2.0)
    out['mid'] = D.js(page, "return { busy: L.meshBusy(), step: $('meshStep').textContent, bar: $('meshBar').getAttribute('aria-valuenow') };")
    out['cancel'] = D.js(page, VIS + "const t0 = performance.now(); $('meshCancel').click(); let n = 0; while (L.meshBusy() && n++ < 2000) await sleep(5);"
                               "return { ms: Math.round(performance.now() - t0), busy: L.meshBusy(), msg: $('meshMsg').textContent, startShown: vis('meshStart'), cancelShown: vis('meshCancel'), saveShown: vis('meshSave'),"
                               " focus: document.activeElement.id, files: window.__files.length };")
    note('special-cancel', out)
    D.page_shot = page.shot(os.path.join(HERE, 'pics', 'panel-cancelled.png'), '#secMesh')
    # a second job straight after the cancel: must give the same model as the plain 96 job
    D.run_job(page, prof, 'klein', '96', name='klein-96-aftercancel')
    # save twice, a hook that throws, discard
    out2 = {}
    D.js(page, "window.__files = []; pick('meshCells', '96'); $('meshStart').click(); let n = 0; await sleep(100); while (L.meshBusy() && n++ < 4000) await sleep(50); return 1;")
    out2['save1'] = D.js(page, "$('meshSave').click(); await sleep(500); return { files: window.__files.length, msg: $('meshMsg').textContent };")
    out2['save2'] = D.js(page, "$('meshSave').click(); await sleep(500); return { files: window.__files.length, msg: $('meshMsg').textContent, same: window.__files.length > 1 && window.__files[0].blob.size === window.__files[1].blob.size };")
    out2['hookThrows'] = D.js(page, VIS + "window.squaringLabSaveHook = () => { throw new Error('the hook refuses'); }; $('meshSave').click(); await sleep(600);"
                                    "return { msg: $('meshMsg').textContent, saveShown: vis('meshSave'), discardShown: vis('meshDiscard') };")
    out2['declined'] = D.js(page, VIS + "delete window.squaringLabSaveHook; const old = window.claude; window.claude = { use: async () => ({ save: async () => { throw { code: 'declined' }; } }) };"
                                  "let r = null; try { $('meshSave').click(); await sleep(900); r = { msg: $('meshMsg').textContent, saveShown: vis('meshSave') }; } finally { window.claude = old; }"
                                  "window.squaringLabSaveHook = (name, blob) => { window.__files.push({ name, blob }); }; return r;")
    out2['discard'] = D.js(page, VIS + "$('meshDiscard').focus(); $('meshDiscard').click(); await sleep(100); return { startShown: vis('meshStart'), saveShown: vis('meshSave'), msg: $('meshMsg').textContent, focus: document.activeElement.id };")
    out2['noKinds'] = D.js(page, VIS + "for (const id of ['meshStl', 'meshObj', 'meshPly']) if ($(id).checked) $(id).click(); await sleep(50); $('meshStart').click(); await sleep(300);"
                                 "const r = { busy: L.meshBusy(), msg: $('meshMsg').textContent, startShown: vis('meshStart') }; for (const id of ['meshStl', 'meshObj', 'meshPly']) if (!$(id).checked) $(id).click(); return r;")
    note('special-saves', out2)


def perturb(page, prof, D):
    D.subject_page(page, 'mandel')
    change = ("$('mode-k').click(); await sleep(150); L.cam.yaw += 1.3; L.cam.dist *= 0.6; L.touch(); await sleep(150); $('qUltra').click(); await sleep(150);"
              "$('mode-j').click(); await sleep(150); pick('juliaPreset', 'Douady rabbit'); await sleep(100); $('cutOn').click(); type('cut', '0.2'); type('viewBound', '1');"
              "return { busy: L.meshBusy(), mode: L.S.mode, c: L.S.c, cutOn: L.S.cutOn, bound: L.S.view.bound, step: $('meshStep').textContent };")
    try:
        D.js(page, "if (!$('viewBound')) fail('no viewBound'); return 1;")
    except Exception:
        change = change.replace("type('viewBound', '1');", "L.S.view.bound = 1; L.touch();")
    D.run_job(page, prof, 'mandel', '512', extra_during=(0.0, change), name='mandel-512-perturbed')
    page.shot(os.path.join(HERE, 'pics', 'after-perturb.png'), '#stage')


def edge(page, prof, D):
    # option by option, each on a fresh page
    D.subject_page(page, 'rabbit')
    D.js(page, "type('meshOffset', '0'); return $('meshOffset').value;")
    D.run_job(page, prof, 'rabbit', '128', name='rabbit-128-offset0')
    D.js(page, "type('meshOffset', '2'); return $('meshOffset').value;")
    D.run_job(page, prof, 'rabbit', '128', name='rabbit-128-offset2')
    D.js(page, "type('meshOffset', '0.5'); type('meshMm', '250'); $('meshObj').click(); $('meshPly').click(); return [$('meshMm').value, $('meshObj').checked, $('meshPly').checked];")
    D.run_job(page, prof, 'rabbit', '128', name='rabbit-128-250mm-stlonly')
    D.subject_page(page, 'negpow')
    D.js(page, "$('meshLargest').click(); return $('meshLargest').checked;")
    D.run_job(page, prof, 'negpow', '128', name='negpow-128-allpieces')
    D.subject_page(page, 'mandel')
    print('  2D view:', D.js(page, "$('flat').click(); await sleep(300); return L.S.flat;"), flush=True)
    page.wait(D.shot.DONE, 300)
    page.shot(os.path.join(HERE, 'pics', 'flat-before-job.png'), '#stage')
    D.run_job(page, prof, 'mandel', '128', name='mandel-128-from2d')
    D.subject_page(page, 'mandel')
    print('  mosaic:', D.js(page, "const e = $('m-mosaic') || [...document.querySelectorAll('#mandelPanel input[type=checkbox]')].find(x => /mosaic/i.test(x.closest('label, .field, div').textContent)); if (!e) fail('no mosaic tick box'); e.click(); await sleep(300); return [e.id, L.S.mosaic, L.S.cutOn];"), flush=True)
    page.wait(D.shot.DONE, 300); time.sleep(0.5)
    page.shot(os.path.join(HERE, 'pics', 'mosaic.png'), '#stage')
    D.run_job(page, prof, 'mosaic', '128', name='mosaic-128')
    # the largest job with every loose piece kept: the heaviest thing the panel can be asked for on the opening views
    D.subject_page(page, 'klein')
    D.js(page, "$('meshLargest').click(); type('meshOffset', '0'); return [$('meshLargest').checked, $('meshOffset').value];")
    D.run_job(page, prof, 'klein', '512', name='klein-512-allpieces-offset0', keep_zip=False)
