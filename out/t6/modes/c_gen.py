import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = "out/t6/modes/c"
os.makedirs(os.path.join(HERE, "c"), exist_ok=True)
PRE = """const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const snap = () => JSON.stringify({ c: S.c, cam: [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => +x.toFixed(5)), v2: [S.v2.x, S.v2.y, S.v2.h], iter: S.iter, planes: S.param.mercator.planes, kiter: S.k.iter, k: [S.k.mx, S.k.my, S.k.mz, S.k.three, S.k.L, S.k.invR, S.k.cx, S.k.cy, S.k.cz], n: S.n, ap: S.approach, mode: S.mode });
const diff = (a, b) => { a = JSON.parse(a); b = JSON.parse(b); return Object.keys(a).filter(k => JSON.stringify(a[k]) !== JSON.stringify(b[k])); };
const groups = id => [...$(id).children].map(e => e.tagName === 'OPTGROUP' ? e.label + ':' + e.children.length : 'opt:' + e.text + (e.disabled ? '(disabled)' : ''));
const pickText = (id, t) => { const e = $(id), o = [...e.options].find(x => x.text.includes(t)); if (!o) return 'NO OPTION ' + t; e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); return o.text; };
const chosen = id => { const e = $(id); return e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : ''; };
const vis = id => { const e = $(id); return !!e && !e.hidden && e.getBoundingClientRect().width > 0; };
try {
"""
POST = "\n} catch (err) { return 'ERROR ' + (err && err.stack || err); }"
steps = []
def step(js, shot=None, wait=True, clip="#view"):
    s = {"js": PRE + js + POST}
    if wait: s["wait"] = "done"; s["timeout"] = 120
    if shot: s["shot"] = "%s/%s.png" % (OUT, shot); s["clip"] = clip
    steps.append(s)

step("""L.R.warmOn = false; const st = document.createElement('style'); st.textContent = '#stage > *:not(canvas){visibility:hidden !important}'; document.head.appendChild(st);
const fl = $('flat').getBoundingClientRect(), mm = $('mode-m').getBoundingClientRect();
$('mode-j').click(); await sleep(50);
return { flatTop: fl.top, modeTop: mm.top, juliaGroups: groups('juliaPreset'), chosen: chosen('juliaPreset'), found: vis('juliaFound'), del: vis('juliaDelete') };""", "j0-open")
step("""const a = snap(); const t = pickText('juliaPreset', 'abbit'); await sleep(50); const b = snap(); return { picked: t, changed: diff(a, b), c: S.c, note: $('juliaNote').textContent.slice(0, 160), found: vis('juliaFound') };""", "j1-rabbit-entry")
step("""const a = snap(); $('juliaFrame').click(); await sleep(1500); const b = snap(); return { frameIt: diff(a, b), cam: JSON.parse(b).cam };""", "j2-rabbit-framed")
step("""const a = snap(); const t = pickText('juliaPreset', 'Flint'); await sleep(50); const b = snap(); const fv = vis('juliaFound'), tip = $('juliaFound').title; $('juliaFound').click(); await sleep(50); const c2 = snap(); return { picked: t, entryChanged: diff(a, b), foundShown: fv, tip, asFoundChanged: diff(b, c2), planes: S.param.mercator.planes, iter: S.iter, foundAfter: vis('juliaFound') };""", "j3-flint-as-found")
step("""S.param.mercator.planes = 1; S.iter = 14; S.c = [0.31, 0.52, 0.07]; L.syncControls(); L.refresh(false); await sleep(50);
const own = chosen('juliaPreset'); $('juliaName').value = 'My test point'; $('juliaSave').click(); await sleep(80);
const g1 = groups('juliaPreset'), ch1 = chosen('juliaPreset'), del1 = vis('juliaDelete'), note = $('juliaSaveNote').textContent;
const a = snap(); pickText('juliaPreset', 'abbit'); await sleep(50); pickText('juliaPreset', 'My test point'); await sleep(50); const b = snap();
let stored = null; try { stored = localStorage.getItem('squaringLab.juliaPoints.v1'); } catch (e) { stored = 'blocked'; }
$('juliaDelete').click(); await sleep(80);
return { ownShown: own, afterSave: g1.slice(0, 3), chosenAfterSave: ch1, deleteShown: del1, saveNote: note, backToSaved: diff(a, b), cNow: S.c, stored, afterDelete: groups('juliaPreset').slice(0, 3), chosenAfterDelete: chosen('juliaPreset'), deleteShownAfter: vis('juliaDelete') };""", None)
step("""$('mode-k').click(); await sleep(100); const g = groups('kleinPreset'), ch0 = chosen('kleinPreset');
const a = snap(); const o = [...$('kleinPreset').querySelectorAll('optgroup')].find(x => /Turning/.test(x.label)).children[3]; $('kleinPreset').value = o.value; $('kleinPreset').dispatchEvent(new Event('change', { bubbles: true })); await sleep(50); const b = snap();
return { kleinGroups: g, opens: ch0, picked: o.text, entryChanged: diff(a, b), k: JSON.parse(b).k, note: $('kleinNote').textContent.slice(0, 140) };""", "k1-turning-entry")
step("""const a = snap(); $('kleinFrame').click(); await sleep(1500); const b = snap(); const fr = diff(a, b);
S.k.my = 1.93; L.syncControls(); L.refresh(false); await sleep(50); return { frameIt: fr, ownShown: chosen('kleinPreset'), warn: vis('kleinWarn') ? $('kleinWarn').textContent.slice(0, 120) : '' };""", "k2-framed-own")
step("""L.resetAll(); await sleep(100); $('m-mosaic').click(); await sleep(50); return { mosaic: S.mosaic, cutOn: S.cutOn, cut: S.cut, cellDial: vis('m-mosaicCell') };""", "m1-mosaic-3d")
step("""$('flat').click(); await sleep(50); return { flat: S.flat, flatZ: $('flatZ').textContent };""", "m2-mosaic-2d")
step("""$('m-mosaic').click(); await sleep(50); return { mosaic: S.mosaic, flat: S.flat, cutOn: S.cutOn };""", "m3-2d-plain")
step("""$('flat').click(); await sleep(50); const i = L.APPROACHES.findIndex(a => a.id === 'bulb'); $('ap-bulb').click(); await sleep(50); S.n = 8; S.param.bulb.lat = 40; L.syncControls(); L.refresh(false);
const d = $('par-bulb-lat'); const box = d ? d.closest('.dial') || d.parentElement.parentElement : null;
return { ap: S.approach === i, latDial: !!d, lonDial: !!$('par-bulb-lon'), buttonsNearLat: box ? [...box.querySelectorAll('button')].map(b => b.getAttribute('aria-label') || b.title || b.textContent).slice(0, 8) : [] };""", "p1-bulb-n8-lat40")
step("""S.param.bulb.lat = 0; $('ap-classic').click(); await sleep(50); S.param.classic.theta = 40; L.syncControls(); L.refresh(false); return { theta: !!$('par-classic-theta'), phi: !!$('par-classic-phi') };""", "p2-classic-n8-theta40")
step("""S.param.classic.theta = 0; $('ap-mercator').click(); await sleep(50); S.n = 2; S.param.mercator.turn = 40; S.param.mercator.lift = 0.3; L.syncControls(); L.refresh(false); return { turn: vis('par-mercator-turn'), lift: vis('par-mercator-lift') };""", "p3-inversions-turn40-lift03")
for ap in ["mercator", "lathe", "bulb", "classic", "split"]:
    step("""S.param.mercator.turn = 0; S.param.mercator.lift = 0; $('ap-%s').click(); await sleep(50); S.n = -2; L.syncControls(); L.refresh(false); const p = $('pow'); return { ap: L.APPROACHES[S.approach].id, n: S.n, powBox: p ? p.value : null, stageNote: vis('stageNote'), whole: vis('powWhole') };""" % ap, "n-%s-neg2" % ap)
sides = {"a": (0.6, 0.45), "b": (3.9, -0.5)}
cs = {"basilica": [-1, 0, 0], "rabbit": [-0.123, 0.745, 0], "c285": [0.285, 0.01, 0], "c46": [-0.4, 0.6, 0]}
first = True
for ap in ["mercator", "lathe"]:
    for cn, c in cs.items():
        for sn, (yaw, pitch) in sides.items():
            for flip in (0, 1):
                step("""%s S.mode = 'j'; S.approach = L.APPROACHES.findIndex(a => a.id === '%s'); S.n = 2; S.c = %s; S.flip = [0, %d]; S.flat = false; S.cutOn = false; S.q.aa = 2;
L.cam.yaw = %s; L.cam.pitch = %s; L.cam.dist = 4.6; L.cam.target = [0, 0, 0]; L.syncControls(); L.refresh(false); return { flipBox: $('flipz').checked };""" % ("L.resetAll(); await sleep(100);" if first else "", ap, json.dumps(c), flip, yaw, pitch), "t-%s-%s-%s-f%d" % (ap, cn, sn, flip))
                first = False
json.dump(steps, open(os.path.join(HERE, "c_steps.json"), "w"), indent=1)
print(len(steps))
