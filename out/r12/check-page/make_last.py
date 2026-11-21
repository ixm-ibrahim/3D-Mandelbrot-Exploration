"""Round 12, checker of the page.  python out/r12/check-page/make_last.py
-> smoke-part.json: steps 1, 7, 8, 37, 38, 44 of tools/smoke-v12.json (to see them fail on the page before round 12)
-> card.json: every entry, the scorecard and the step figures: no 'undefined' or 'NaN' in what is on show
-> julia-notes check printed: every note of data/julia-presets.json is in src/js/75-presets.js"""
import io, json, re

OUT = 'out/r12/check-page/'
a = json.load(open('tools/smoke-v12.json', encoding='utf-8'))
part = []
for n in (1, 7, 8, 37, 38, 44):
    s = dict(a[n - 1])
    s.pop('shot', None); s.pop('clip', None)
    part.append(s)
json.dump(part, io.open(OUT + 'smoke-part.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)

PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { await sleep(250); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 100000) throw new Error('not finished after 100 s'); await sleep(50); } };
"""
steps = [{'js': PRE + r"""
await settle(); document.querySelectorAll('details').forEach(d => { d.open = true; }); const out = [];
for (const mode of ['m', 'j']) { $('mode-' + mode).click(); for (const a of L.APPROACHES) { $('ap-' + a.id).click(); await settle(); const t = document.body.innerText; const m = t.match(/.{0,50}(undefined|NaN|\[object|Infinity).{0,50}/g); const card = $('card').innerText.replace(/\s+/g, ' ');
  out.push(a.id + ' ' + mode + ': ' + (m ? 'ODD TEXT: ' + m.slice(0, 3).join(' // ') : 'no odd text') + '; scorecard ' + card.length + ' characters' + (mode === 'm' && a.group === 'tried' ? ': ' + card.slice(0, 700) : '')); } }
return out;
"""},
         {'js': PRE + "$('mode-m').click(); $('ap-pillow').click(); await settle(); $('card').scrollIntoView({ block: 'start' }); await sleep(200); return 'scorecard of Pillow';", 'shot': OUT + 'card-pillow.png'},
         {'js': PRE + "$('step2d').scrollIntoView({ block: 'center' }); await sleep(300); return 'step figures under Pillow: ' + $('cap2d').textContent.slice(0, 100) + ' / ' + $('cap3d').textContent.slice(0, 160);", 'shot': OUT + 'step-pillow.png'}]
json.dump(steps, io.open(OUT + 'card.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)

js = open('src/js/75-presets.js', encoding='utf-8').read()
data = json.load(open('data/julia-presets.json', encoding='utf-8'))
items = data if isinstance(data, list) else data.get('presets') or data.get('entries') or next(v for v in data.values() if isinstance(v, list))
missing = [p['name'] for p in items if p.get('note') and json.dumps(p['note'], ensure_ascii=False) not in js]
print(len(items), 'Julia entries in data/julia-presets.json; notes not found word for word in src/js/75-presets.js:', missing or 'none')
print('entries by planes:', {k: sum(1 for p in items if p.get('planes') == k) for k in (1, 2)})
