"""Round 12, checker of the page: a few more looks.  python out/r12/check-page/make_extra.py -> extra.json, light.json"""
import io, json

OUT = 'out/r12/check-page/'
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { await sleep(250); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 100000) throw new Error('not finished after 100 s'); await sleep(50); } };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const apId = () => L.APPROACHES[L.S.approach].id;
const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
"""
steps = []


def step(js, shot=None, clip=None):
    a = {'js': PRE + js.strip()}
    if shot:
        a['shot'] = OUT + shot + '.png'
        if clip:
            a['clip'] = clip
    steps.append(a)


# what As it was found offers for every entry of the Julia list, under four approaches, at the opening iterations
step(r"""
await settle(); $('mode-j').click(); await sleep(200);
const first = 'on entering the Julia view (list reads ' + $('juliaPreset').selectedOptions[0].text + '): ' + (shown('juliaFound') ? $('juliaFound').textContent : 'no button');
const out = [first];
for (const ap of ['mercator', 'fold', 'lathe', 'softfold']) { $('ap-' + ap).click(); await sleep(100); const row = [];
  for (const g of $('juliaPreset').querySelectorAll('optgroup')) for (const o of g.children) { $('juliaPreset').value = o.value; $('juliaPreset').dispatchEvent(new Event('change', { bubbles: true })); await sleep(50); row.push(o.text + ' [' + g.label + ']: ' + (shown('juliaFound') ? $('juliaFound').textContent.replace('As it was found: ', '') : '-')); }
  out.push('UNDER ' + ap + ' -> ' + row.join(' | ')); }
return out;
""")
# Back to one plane from the Mandelbrot solid of another entry, with the 2D view on: only the approach should change
step(r"""
$('resetAll').click(); await sleep(300); $('ap-bulb').click(); $('flat').click(); type('powNum', '3'); await settle();
const before = [L.S.mode, L.S.flat, L.S.n, apId()].join(); $('fig4Back').click(); await settle(); const after = [L.S.mode, L.S.flat, L.S.n, apId()].join();
$('mode-k').click(); await settle(); const k0 = [L.S.mode, apId()].join(); $('fig4Back').click(); await settle();
return 'Back to one plane from the Mandelbrot 2D view of the Mandelbulb at power 3 (mode, 2D, power, approach): ' + before + ' -> ' + after + '; from the Kleinian view: ' + k0 + ' -> ' + [L.S.mode, apId()].join();
""")
# every choice of the three drop-downs of the tried entries redraws a different picture
step(r"""
$('resetAll').click(); await sleep(300); const out = [];
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = ''; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) s += L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11) ? '1' : '0'; return s; };
for (const [ap, key] of [['softfold', 'curve'], ['softfold', 'mix'], ['pillow', 'layout']]) { $('ap-' + ap).click(); await settle(); const e = $('par-' + ap + '-' + key), seen = [];
  for (const o of e.options) { e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); await settle(); const g = grid(); seen.push('"' + o.text + '" ' + (g.split('1').length - 1) + ' hits' + (seen.length && g === window.lastG ? ' (same probes as the choice before)' : '')); window.lastG = g; }
  out.push(ap + ', ' + e.closest('.field, .dial, div').querySelector('label').textContent.trim() + ': ' + seen.join('; ') + '; help: ' + (($('par-' + ap + '-' + key + 'Help') || {}).textContent || '(none found)').slice(0, 160)); e.value = e.options[0].value; e.dispatchEvent(new Event('change', { bubbles: true })); }
return out;
""", 'extra-pillow-smooth')
# the 2D view under the tried entries against the one-plane entry
step("$('resetAll').click(); await sleep(300); $('flat').click(); await settle(); return '2D view, one plane';", 'extra-2d-oneplane', '#stage')
step("$('ap-pillow').click(); await settle(); return '2D view, Pillow (creased, both planes exact)';", 'extra-2d-pillow', '#stage')
step("$('ap-softfold').click(); await settle(); return '2D view, Blended planes';", 'extra-2d-softfold', '#stage')
step("$('ap-axisbulb').click(); await settle(); return '2D view, Bulbs about the axis';", 'extra-2d-axisbulb', '#stage')
with io.open(OUT + 'extra.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(steps, f, indent=1, ensure_ascii=False)

light = [
    {'js': PRE + "await settle(); $('ap-pillow').click(); await settle(); const e = $('apgh-angles'); e.scrollIntoView({ block: 'start' }); window.scrollBy(0, -100); await sleep(200); return 'theme ' + document.documentElement.dataset.theme + ', heading colour ' + getComputedStyle(e).color + ' on ' + getComputedStyle(document.body).backgroundColor;", 'shot': OUT + 'light-375-list.png'},
    {'js': PRE + "const h = [...document.querySelectorAll('footer.why h3')].find(x => x.textContent.startsWith('Is there a quaternion rule')); h.scrollIntoView({ block: 'start' }); await sleep(200); return 'answer';", 'shot': OUT + 'light-375-answer.png'},
]
with io.open(OUT + 'light.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(light, f, indent=1, ensure_ascii=False)
print(len(steps), 'and', len(light), 'steps')
