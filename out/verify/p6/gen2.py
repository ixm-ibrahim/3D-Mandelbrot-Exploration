import json
D = "out/verify/p6/"
P = ("const L = window.squaringLab, $ = id => document.getElementById(id); "
     "const rows = () => [...document.querySelectorAll('#juliaList .plist-row')]; "
     "const item = t => [...document.querySelectorAll('#juliaList .plist-item')].find(x => x.textContent === t); "
     "const on = () => rows().filter(r => r.classList.contains('is-on')).map(r => r.firstChild.textContent); "
     "const saved = () => L.juliaSaved().map(p => p.name); "
     "const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; "
     "const nap = ms => new Promise(r => setTimeout(r, ms)); ")
acts = []
def A(js, **k):
    d = {"js": P + js}; d.update(k); acts.append(d)
A("L.R.warmOn = false; $('mode-j').click(); $('qUltra').click(); return { ls: (() => { try { return localStorage.getItem('squaringLab.juliaPoints.v1'); } catch (e) { return 'ERR ' + e; } })(), on: on(), note: $('juliaNote').textContent, heads: [...document.querySelectorAll('#juliaList .plist-head')].map(h => h.textContent), empty: (document.querySelector('.plist-empty') || {}).textContent, panelNote: document.querySelector('#juliaPanel .note').textContent, maxlength: $('juliaName').maxLength };", wait="done", timeout=300)
# 2 save with a name at a hand-set c
A("type('cxNum', '-0.5'); type('cyNum', '0.55'); type('czNum', '0.1'); await nap(50); const before = { on: on(), note: $('juliaNote').textContent }; $('juliaName').value = 'My point'; $('juliaSave').click(); await nap(50); return { before, saved: saved(), on: on(), note: $('juliaNote').textContent, nameBox: $('juliaName').value, saveNote: $('juliaSaveNote').hidden ? null : $('juliaSaveNote').textContent, ls: localStorage.getItem('squaringLab.juliaPoints.v1') };")
# 3 empty name, whitespace name
A("$('juliaName').value = ''; $('juliaSave').click(); $('juliaName').value = '   '; $('juliaSave').click(); await nap(50); return { saved: saved(), on: on() };")
# 4 long name (programmatic bypasses maxlength), brackets and quotes
A("type('cxNum', '0.3'); $('juliaName').value = 'Supercalifragilisticexpialidocious_no_spaces_at_all_in_this_very_long_name_that_goes_on_and_on_1234567890'; $('juliaSave').click(); type('cxNum', '0.31'); $('juliaName').value = '<b>bold</b> \"q\" \\'s\\' <img src=x onerror=window.__xss=1> &amp;'; $('juliaSave').click(); await nap(300); const r = rows().slice(0, 6).map(r => ({ t: r.firstChild.textContent, html: r.firstChild.innerHTML.slice(0, 120), w: Math.round(r.getBoundingClientRect().width), h: Math.round(r.getBoundingClientRect().height), aria: r.lastChild.getAttribute('aria-label') })); const host = $('juliaList'); return { saved: saved(), xss: window.__xss || 0, rows: r, listW: host.clientWidth, listSW: host.scrollWidth, imgs: host.querySelectorAll('img, b').length };",
  shot=D + "f-04-names.png", clip="#juliaPanel")
# 5 save twice the same thing
A("type('cxNum', '0.2'); $('juliaName').value = 'Twice'; $('juliaSave').click(); $('juliaName').value = 'Twice'; $('juliaSave').click(); await nap(50); return { saved: saved(), on: on(), note: $('juliaNote').textContent };", shot=D + "f-05-twice.png", clip="#juliaPanel")
# 6 delete the first of the duplicates, then check which went
A("const dels = [...document.querySelectorAll('#juliaList .plist-del')]; const n = saved().length; const twice = rows().filter(r => r.firstChild.textContent === 'Twice'); twice[0].lastChild.focus(); twice[0].lastChild.click(); await nap(50); return { before: n, saved: saved(), focus: document.activeElement && (document.activeElement.id || document.activeElement.tagName), delText: dels[0].textContent, delAria: dels[0].getAttribute('aria-label') };")
# 7 move away, then jump to saved 'My point': dials, highlight
A("item('Dendrite').click(); await nap(50); const a = { c: L.S.c.slice(), on: on(), planes: L.S.param.mercator.planes }; item('My point').click(); await nap(50); return { a, c: L.S.c.slice(), dials: [$('cxNum').value, $('cyNum').value, $('czNum').value], on: on(), note: $('juliaNote').textContent, planes: L.S.param.mercator.planes, cam: [L.cam.yaw, L.cam.pitch, L.cam.dist] };", wait="done", timeout=300)
# 8 reload
A("setTimeout(() => location.reload(), 30); return 'reloading';", sleep=3, wait="document.readyState === 'complete' && window.squaringLab && window.squaringLab.juliaSaved", timeout=60)
A("L.R.warmOn = false; $('mode-j').click(); $('qUltra').click(); await nap(100); return { saved: saved(), full: L.juliaSaved().slice(0, 2), rows: rows().slice(0, 7).map(r => r.firstChild.textContent), on: on() };", wait="done", timeout=300, shot=D + "f-09-after-reload.png", clip="#juliaPanel")
# 10 saved point after reload jumps and restores
A("item('My point').click(); await nap(50); return { c: L.S.c.slice(), dials: [$('cxNum').value, $('cyNum').value, $('czNum').value], on: on(), note: $('juliaNote').textContent };", wait="done", timeout=300, shot=D + "f-10-saved-jump.png", clip="#stage")
# 11 highlight after moving c by hand: typed, slider, reset
A("item('Basilica').click(); await nap(50); const a = on(); type('cyNum', '0.01'); await nap(50); const b = { on: on(), note: $('juliaNote').textContent }; type('cyNum', '0'); await nap(50); const c = on(); const s = $('cx'); s.value = '-0.9'; s.dispatchEvent(new Event('input', { bubbles: true })); await nap(50); const d = { on: on(), note: $('juliaNote').textContent, c: L.S.c.slice() }; document.querySelector('#juliaReset .dial-reset').click(); await nap(50); return { picked: a, moved: b, movedBack: c, slider: d, afterReset: { on: on(), c: L.S.c.slice(), note: $('juliaNote').textContent } };")
# 12 saved point equal to a preset: two highlighted?
A("item('Basilica').click(); $('juliaName').value = 'My basilica'; $('juliaSave').click(); await nap(50); return { on: on(), note: $('juliaNote').textContent };", shot=D + "f-12-two-on.png", clip="#juliaPanel")
# 13 fly mode then preset
A("$('camFly').click(); await nap(400); const a = { fly: L.S.view.fly, cam: $('stage').dataset.cam, pos: L.basis().pos.slice() }; item('Airplane').click(); await nap(500); return { a, fly: L.S.view.fly, cam: $('stage').dataset.cam, viewFly: $('viewFly').checked, hint: (document.querySelector('.hint') || {}).textContent, pos: L.basis().pos.slice(), camState: [L.cam.yaw, L.cam.pitch, L.cam.dist] };", wait="done", timeout=300, shot=D + "f-13-fly-preset.png", clip="#stage")
# 14 fly mode: move, save own point, go elsewhere, come back: same view?
A("$('camFly').click(); await nap(400); const cv = $('view'); cv.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyD', key: 'd', bubbles: true })); await nap(900); window.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyD', key: 'd', bubbles: true })); await nap(400); const b0 = L.basis(); const p0 = b0.pos.slice(); $('juliaName').value = 'Fly view'; $('juliaSave').click(); await nap(50); item('Dendrite').click(); await nap(400); item('Fly view').click(); await nap(600); const b1 = L.basis(); return { keys: Object.keys(b0), p0, p1: b1.pos.slice(), flyAfter: L.S.view.fly, moved: Math.hypot(p0[0] - b1.pos[0], p0[1] - b1.pos[1], p0[2] - b1.pos[2]) };", wait="done", timeout=300)
json.dump(acts, open(D + "func1.json", "w", encoding="utf-8"), ensure_ascii=False)

# second run: other approach / power / equation / storage blocked
acts = []
A("L.R.warmOn = false; $('mode-j').click(); $('qFast').click(); item('Douady rabbit').click(); await nap(50); return { iter: L.S.iter, planes: L.S.param.mercator.planes };", wait="done", timeout=300)
A("$('ap-lathe').click(); await nap(100); item('Douady rabbit').click(); await nap(50); const pl0 = L.S.param.mercator.planes; item('Basilica').click(); await nap(100); return { approach: L.S.approach, planesBefore: pl0, planesAfter: L.S.param.mercator.planes, iter: L.S.iter, note: $('juliaNote').textContent };", wait="done", timeout=300, shot=D + "g-02-lathe-basilica.png", clip="#stage")
A("item('Douady rabbit').click(); await nap(100); return { note: $('juliaNote').textContent, title: item('Douady rabbit').title };", wait="done", timeout=300, shot=D + "g-03-lathe-rabbit.png", clip="#stage")
A("$('ap-classic').click(); await nap(100); item('Dendrite').click(); await nap(100); return { note: $('juliaNote').textContent };", wait="done", timeout=300, shot=D + "g-04-classic-dendrite.png", clip="#stage")
A("$('ap-mercator').click(); await nap(100); type('powNum', '3'); item('Basilica').click(); await nap(100); return { n: L.S.n, note: $('juliaNote').textContent, on: on() };", wait="done", timeout=300, shot=D + "g-05-pow3-basilica.png", clip="#stage")
A("type('powNum', '-2'); item('Douady rabbit').click(); await nap(100); return { n: L.S.n, note: $('juliaNote').textContent };", wait="done", timeout=300, shot=D + "g-06-powm2-rabbit.png", clip="#stage")
A("type('powNum', '2'); const e = $('eqPreset'); const opts = [...e.options].map(o => o.text); e.selectedIndex = 3; e.dispatchEvent(new Event('change', { bubbles: true })); await nap(100); item('Basilica').click(); await nap(100); return { opts, eq: L.S.eq, z0: L.S.z0, note: $('juliaNote').textContent, c: L.S.c.slice() };", wait="done", timeout=300, shot=D + "g-07-eq-basilica.png", clip="#stage")
A("document.querySelector('#eqReset .dial-reset').click(); await nap(100); const it0 = L.S.iter; item('Douady rabbit').click(); await nap(100); const it1 = L.S.iter; item('Basilica').click(); await nap(100); return { eq: L.S.eq, iterAfterReset: it0, iterAfterRabbit: it1, iterAfterBasilica: L.S.iter, iterDial: $('iterNum').value, planes: L.S.param.mercator.planes };", wait="done", timeout=300)
# storage blocked, saving and deleting
A("Object.defineProperty(window, 'localStorage', { configurable: true, get() { throw new Error('storage is blocked'); } }); $('juliaName').value = 'Blocked'; $('juliaSave').click(); await nap(50); const a = { saved: saved(), note: $('juliaSaveNote').hidden ? null : $('juliaSaveNote').textContent }; $('juliaName').value = 'Blocked 2'; $('juliaSave').click(); await nap(50); const b = { saved: saved(), note: $('juliaSaveNote').hidden ? null : $('juliaSaveNote').textContent }; return { a, b };", shot=D + "g-09-blocked.png", clip="#juliaPanel")
A("document.querySelector('#juliaList .plist-del').click(); await nap(50); const afterDel = { saved: saved(), note: $('juliaSaveNote').hidden ? null : $('juliaSaveNote').textContent }; delete window.localStorage; return { afterDel, ls: localStorage.getItem('squaringLab.juliaPoints.v1') };")
json.dump(acts, open(D + "func2.json", "w", encoding="utf-8"), ensure_ascii=False)
