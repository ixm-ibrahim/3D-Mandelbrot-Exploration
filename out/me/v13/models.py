import io, json
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
"""
WAIT = '!window.squaringLab.meshBusy || !window.squaringLab.meshBusy()'
s = []
def job(setup, name):
    s.append({"js": PRE + "window.smokeFiles = window.smokeFiles || []; window.squaringLabSaveHook = (n, b) => { window.smokeFiles.push({ name: n, size: b.size }); }; L.R.warmOn = false; window.squaringLabMeshTest = { cells: 64 };\n" + setup + "\nawait sleep(300); $('secMesh').open = true; $('meshStart').click(); await sleep(300); return '" + name + " started';", "wait": WAIT, "timeout": 600})
    s.append({"js": PRE + "const before = window.smokeFiles.length; if (!shown('meshSave')) fail('" + name + ": no file to save: ' + ($('meshMsg') ? $('meshMsg').textContent : '')); $('meshSave').click(); await sleep(600); const f = window.smokeFiles[before]; if (!f || !f.name.endsWith('.zip') || f.size < 1000) fail('" + name + ": bad file ' + JSON.stringify(f)); return '" + name + " -> ' + f.name + ', ' + f.size + ' bytes; message: ' + ($('meshMsg') ? $('meshMsg').textContent.slice(0, 160) : '');"})
job("$('mode-k').click();", "Kleinian model")
job("pick('trapExamples', 'Chain of bubbles');", "Chain of bubbles model")
job("$('resetAll').click(); await sleep(400); $('ap-tilt').click(); await sleep(300);", "twisted square model")
io.open('out/me/v13/models.json', 'w', encoding='utf-8').write(json.dumps(s))
print(len(s), 'steps')
