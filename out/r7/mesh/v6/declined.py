"""Tester "mesh": what Save the file does when the save is refused. Two fresh results, one refusal each."""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drive as D

VIS = "const vis = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };"
MAKE = ("window.__files = []; $('secMesh').open = true; pick('meshCells', '96'); $('meshStart').click(); await sleep(100); let n = 0;"
        "while (L.meshBusy() && n++ < 4000) await sleep(50); return $('meshMsg').textContent;")
proc, prof, page = D.launch()
out = {}
try:
    D.load(page)
    # 1. the host's save is declined by the user
    out['made1'] = D.js(page, "delete window.squaringLabSaveHook;" + MAKE)
    out['declined'] = D.js(page, VIS + "const old = window.claude; let calls = 0; window.claude = { use: async () => ({ save: async () => { calls++; throw { code: 'declined' }; } }) };"
                                 "let r; try { $('meshSave').click(); await sleep(1200); r = { calls, msg: $('meshMsg').textContent, saveShown: vis('meshSave'), discardShown: vis('meshDiscard') }; } finally { window.claude = old; } return r;")
    # then a save that works, to see the model is still there
    out['after_declined'] = D.js(page, "window.squaringLabSaveHook = (name, blob) => { window.__files.push({ name, size: blob.size }); }; $('meshSave').click(); await sleep(600);"
                                       "return { files: window.__files, msg: $('meshMsg').textContent };")
    D.js(page, "$('meshDiscard').click(); return 1;")
    # 2. the test hook throws
    out['made2'] = D.js(page, MAKE)
    out['hook_throws'] = D.js(page, VIS + "window.squaringLabSaveHook = () => { throw new Error('the hook refuses'); }; $('meshSave').click(); await sleep(800);"
                                    "return { msg: $('meshMsg').textContent, saveShown: vis('meshSave') };")
    out['after_throw'] = D.js(page, "window.__files = []; window.squaringLabSaveHook = (name, blob) => { window.__files.push({ name, size: blob.size }); }; $('meshSave').click(); await sleep(800);"
                                    "return { files: window.__files, msg: $('meshMsg').textContent };")
    out['problems'] = list(page.problems)
    try: page.call('Browser.close')
    except Exception: pass
finally:
    try: proc.wait(timeout=8)
    except Exception: proc.kill()
    shutil.rmtree(prof, ignore_errors=True)
with open(os.path.join(HERE, 'runs', 'special-declined.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False)[:3000])
