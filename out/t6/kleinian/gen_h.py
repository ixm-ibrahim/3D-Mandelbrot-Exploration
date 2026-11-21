import json, sys
sys.path.insert(0, 'out/t6/kleinian')
src = open('out/t6/kleinian/gen.py', encoding='utf-8').read()
PRE = src.split('PRE = r"""')[1].split('"""')[0]
H = 'out/t6/kleinian/h/'
def st(code, shot, t=600): return {'js': PRE + code, 'wait': 'done', 'timeout': t, 'shot': H + shot, 'clip': '#stage'}
hits = "const g = grid(12, 8); return { k: kNow(), warn: $('kleinWarn').hidden ? '' : $('kleinWarn').textContent, hits: g.join('').split('1').length - 1, of: 96 };"
steps = [
 st("$('mode-k').click(); await sleep(100); type('kinvrNum', '3'); return { k: kNow(), warn: $('kleinWarn').hidden ? '' : $('kleinWarn').textContent };", 'radius3-slider-top.png'),
 {'js': PRE + hits},
 st("type('kinvrNum', '10'); return { k: kNow(), warn: $('kleinWarn').hidden ? '' : $('kleinWarn').textContent };", 'radius10-typed-top.png'),
 {'js': PRE + hits},
 st("type('kinvrNum', '1.2'); pickAt('kleinPreset', 4); $('kleinFrame').click(); document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); await sleep(100); pick('col-solid', 'Is the solid'); $('qFine').click(); return { k: kNow(), solid: L.S.colour.solid, q: JSON.stringify(L.S.q) };", 'e03-solid-fine.png', 900),
 st("L.cam.dist = 20; L.touch(); return { cam: camNow() };", 'e03-solid-fine-far.png', 900),
]
json.dump(steps, open('out/t6/kleinian/h.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
