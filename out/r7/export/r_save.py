"""export-2 and export-3: what "Save the file" says and does after a save that fails.
python out/r7/export/r_save.py <url> [tag]
Three fresh pages: (1) a hook that throws, then a good hook, then a host that answers with each refusal;
(2) a host whose use() throws twice and then works; (3) a host that has no downloads at all."""
import json, sys
from drv import Lab, log

url = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else 'save'
J = lambda o: json.dumps(o, ensure_ascii=False)
SMALL = "$('secExport').open = true; pick('exportSize', 'Typed'); await sleep(50); type('exportWNum', '400'); type('exportHNum', '300'); pick('exportQuality', 'As on screen'); pick('exportKind', 'PNG'); await sleep(50); $('exportStart').click();"


def page(hook=True):
    lab = Lab(url=url, hook=hook)
    lab.idle()
    lab.js(SMALL)
    lab.job_wait(120)
    return lab


# 1. the hook throws, then works; then the host answers
lab = page()
try:
    r = lab.js("""window.__rej = []; addEventListener('unhandledrejection', e => window.__rej.push(String(e.reason && e.reason.message || e.reason)));
window.squaringLabSaveHook = () => { throw new Error('hook says no'); };
$('exportSave').click(); await sleep(500);
const a = { msg: $('exportMsg').textContent, saveShown: shown('exportSave'), rejections: window.__rej.slice() };
window.files = []; window.squaringLabSaveHook = (name, blob) => { window.files.push({ name, blob }); };
$('exportSave').click(); await sleep(500);
const b = { msg: $('exportMsg').textContent, got: window.files.length };
return { hookThrows: a, thenGoodHook: b };""")
    log(tag, 'hook throws', J(r))
    lab.shot(tag + '-hook-throws.png', '#secExport')
    r = lab.js("""delete window.squaringLabSaveHook;
window.__calls = []; window.__mode = 'declined';
window.claude = { use: async what => { window.__calls.push('use:' + what); return { save: async o => { window.__calls.push('save:' + o.filename + ':' + (o.data && o.data.size)); if (window.__mode === 'ok') return {}; const e = new Error('no'); e.code = window.__mode; throw e; } }; } };
const out = {};
for (const mode of ['declined', 'rate_limited', 'too_large', 'rejected_extension', 'extension_not_enabled', 'something_new', 'ok']) {
  window.__mode = mode; $('exportSave').click(); await sleep(400);
  out[mode] = { msg: $('exportMsg').textContent, saveShown: shown('exportSave'), discardShown: shown('exportDiscard') };
}
out.calls = window.__calls.length;
return out;""")
    for k, v in r.items():
        log(tag, 'host answers', k, J(v))
    log(tag, 'problems', lab.problems())
finally:
    lab.close()

# 2. use() throws twice, then the host works
lab = page(hook=False)
try:
    r = lab.js("""window.__calls = []; window.__use = 0;
window.claude = { use: async what => { window.__calls.push('use:' + what); if (++window.__use <= 2) throw new Error('no downloads'); return { save: async o => { window.__calls.push('save:' + o.filename); return {}; } }; } };
const out = [];
for (let i = 0; i < 3; i++) { $('exportSave').click(); await sleep(400); out.push($('exportMsg').textContent); }
return { msgs: out, calls: window.__calls, saveShown: shown('exportSave') };""")
    log(tag, 'use() throws twice, then works', J(r))
    log(tag, 'problems', lab.problems())
finally:
    lab.close()

# 3. the host has no downloads
lab = page(hook=False)
try:
    r = lab.js("""window.__calls = [];
window.claude = { use: async what => { window.__calls.push('use:' + what); return null; } };
const out = [];
for (let i = 0; i < 2; i++) { $('exportSave').click(); await sleep(400); out.push($('exportMsg').textContent); }
return { msgs: out, calls: window.__calls, saveShown: shown('exportSave'), discardShown: shown('exportDiscard') };""")
    log(tag, 'host without downloads', J(r))
    lab.shot(tag + '-unavailable.png', '#secExport')
    log(tag, 'problems', lab.problems())
finally:
    lab.close()
