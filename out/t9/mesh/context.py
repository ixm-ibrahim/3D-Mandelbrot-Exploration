"""Tester "mesh", second check: walk-1 on dist/v8.html. A model job, the graphics context lost in the middle of it.
  python out/t9/mesh/context.py
Part A is the first check's own steps on a fresh page (Start the model at the standard resolution, lose the context 1.2 s
later). Part B the same at 512 cells so that the loss falls into the building of the mesh. After each: restore, read the
panel, start again and see whether a model comes."""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drive as D

VIS = "const vis = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };"
LOSE = ("const gl = $('view').getContext('webgl2'); window.__ext = window.__ext || gl.getExtension('WEBGL_lose_context'); window.__ext.loseContext();"
        "await sleep(300); return gl.isContextLost();")
REST = "window.__ext.restoreContext(); await sleep(400); return $('view').getContext('webgl2').isContextLost();"
PANEL = VIS + ("return { busy: L.meshBusy(), msg: $('meshMsg').textContent, step: $('meshStep').textContent, warn: $('meshWarn').hidden ? '' : $('meshWarn').textContent,"
               " startShown: vis('meshStart'), cancelShown: vis('meshCancel'), saveShown: vis('meshSave'), idle: L.idle(), status: ($('status') || {}).textContent };")
proc, prof, page = D.launch()
out = {}
try:
    for part, cells, delay in (('A', '128', 1.2), ('B', '512', 2.5)):
        D.load(page)
        o = out[part] = {}
        D.js(page, "window.__files = []; window.squaringLabSaveHook = (name, blob) => { window.__files.push({ name, size: blob.size }); }; $('secMesh').open = true; pick('meshCells', '%s'); return 1;" % cells)
        o['status_before'] = D.js(page, "return ($('status') || {}).textContent;")
        D.js(page, "$('meshStart').click(); return 1;")
        time.sleep(delay)
        o['running'] = D.js(page, PANEL)
        o['lost'] = D.js(page, LOSE)
        time.sleep(2)
        o['panel_while_lost'] = D.js(page, PANEL)
        page.shot(os.path.join(HERE, 'pics', 'context-%s-lost.png' % part), '#secMesh')
        o['still_lost_after_restore'] = D.js(page, REST)
        ok = page.wait(D.shot.DONE, 300)
        time.sleep(1)
        o['panel_after_restore'] = D.js(page, PANEL); o['idle_after_restore'] = bool(ok)
        # start again: does a model come?
        D.js(page, "pick('meshCells', '96'); if ($('meshStart').getBoundingClientRect().width > 0) $('meshStart').click(); return 1;")
        t0 = time.time(); time.sleep(0.3)
        while time.time() - t0 < 300 and D.js(page, "return L.meshBusy();"):
            time.sleep(0.3)
        o['second_job'] = D.js(page, PANEL); o['second_job_s'] = round(time.time() - t0, 1)
        o['second_facts'] = D.js(page, "return [...$('meshFacts').children].map(e => e.textContent);")
        page.shot(os.path.join(HERE, 'pics', 'context-%s-end.png' % part), '#secMesh')
        o['problems'] = list(page.problems)
    try: page.call('Browser.close')
    except Exception: pass
finally:
    try: proc.wait(timeout=8)
    except Exception: proc.kill()
    shutil.rmtree(prof, ignore_errors=True)
os.makedirs(os.path.join(HERE, 'runs'), exist_ok=True)
with open(os.path.join(HERE, 'runs', 'special-context.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
