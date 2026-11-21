"""Round 12, checker of the page: whole-window screenshots of the Approach list and of the new answers, as a
reader sees them while scrolling.  python out/r12/check-page/make_views.py -> views-1400.json, views-375.json"""
import io, json

OUT = 'out/r12/check-page/'
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { await sleep(250); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 100000) throw new Error('not finished after 100 s'); await sleep(50); } };
// put an element at the top of what can be seen, below anything that sticks to the top of the window
const show = async (e, off) => { e.scrollIntoView({ block: 'start' }); await sleep(120); let cover = 0; for (const s of document.querySelectorAll('*')) { const cs = getComputedStyle(s); if (cs.position === 'sticky' || cs.position === 'fixed') { const r = s.getBoundingClientRect(); if (r.top <= 1 && r.height > 0 && r.height < innerHeight * 0.8 && r.bottom > cover) cover = r.bottom; } } const sc = (function p(n) { while (n && n !== document.body) { const cs = getComputedStyle(n); if (/(auto|scroll)/.test(cs.overflowY) && n.scrollHeight > n.clientHeight + 2) return n; n = n.parentElement; } return document.scrollingElement; })(e.parentElement); sc.scrollBy(0, e.getBoundingClientRect().top - cover - 6 + (off || 0)); await sleep(200); return 'scroller ' + (sc.id || sc.tagName) + ', covered at the top ' + Math.round(cover) + ' px, element now at ' + Math.round(e.getBoundingClientRect().top); };
"""


def build(tag):
    steps = []

    def step(js, shot=None):
        a = {'js': PRE + js.strip()}
        if shot:
            a['shot'] = OUT + 'view-%s-%s.png' % (tag, shot)
        steps.append(a)

    step("await settle(); $('ap-split').click(); await settle(); return await show($('secApproach'));", 'list-a')
    step("return await show($('secApproach'), innerHeight * 0.75);", 'list-b')
    step("return await show($('secApproach'), innerHeight * 1.5);", 'list-c')
    step("$('ap-softfold').click(); await settle(); return await show(document.querySelector('.rule[data-ap=softfold]'));", 'softfold-a')
    step("return await show($('pd-softfold'));", 'softfold-b')
    step("return await show($('par-softfold-curve').closest('.field') || $('par-softfold-curve'), -200);", 'softfold-c')
    step("$('ap-axisbulb').click(); await settle(); return await show($('pd-axisbulb'));", 'axisbulb-b')
    step("$('ap-pillow').click(); await settle(); return await show(document.querySelector('.rule[data-ap=pillow]'));", 'pillow-a')
    step("return await show($('pd-pillow'), -150);", 'pillow-b')
    step("$('ap-tilt').click(); await settle(); return await show(document.querySelector('.rule[data-ap=tilt]'));", 'tilt-a')
    step("$('ap-fold').click(); await settle(); return await show($('apgh-inversions') || document.querySelector('.rule-group-head'));", 'fold-a')
    # the closing text: the two new answers and the Figure 4 answer
    step("$('ap-mercator').click(); await settle(); const h = [...document.querySelectorAll('footer.why h3')].find(x => x.textContent.startsWith('Is there a quaternion rule')); return await show(h);", 'answer-quaternion-a')
    step("const h = [...document.querySelectorAll('footer.why h3')].find(x => x.textContent.startsWith('Is there a quaternion rule')); return await show(h, innerHeight * 0.8);", 'answer-quaternion-b')
    step("const h = [...document.querySelectorAll('footer.why h3')].find(x => x.textContent.startsWith('Could the hidden rotation axis')); return await show(h);", 'answer-axis')
    step("const h = [...document.querySelectorAll('footer.why h3')].find(x => x.textContent.startsWith('Where is the look of Figure 4')); return await show(h);", 'answer-fig4-a')
    step("const h = $('fig4Show'); const r = await show(h, -80); const b = [...document.querySelectorAll('footer.why .row-btns')].map(d => [...d.children].map(x => x.textContent + ' ' + Math.round(x.getBoundingClientRect().left) + '..' + Math.round(x.getBoundingClientRect().right) + ' y' + Math.round(x.getBoundingClientRect().top)).join(' | ')); return { r, rows: b, pageWidth: document.documentElement.scrollWidth + ' of ' + innerWidth, triedNote: $('triedNote').textContent };", 'answer-fig4-b')
    step("const h = $('twinMerc'); return await show(h, -200);", 'answer-twin')
    # the Julia panel with As it was found on show
    step("$('mode-j').click(); const e = $('juliaPreset'); const o = [...e.options].find(x => x.text.startsWith('Cracked Basilica')); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); await settle(); const r = await show($('juliaPanel')); const f = $('juliaFound'), row = f.closest('.pick-row'); return { r, button: f.textContent, buttonBox: Math.round(f.getBoundingClientRect().left) + '..' + Math.round(f.getBoundingClientRect().right), rowBox: Math.round(row.getBoundingClientRect().left) + '..' + Math.round(row.getBoundingClientRect().right), pageWidth: document.documentElement.scrollWidth + ' of ' + innerWidth };", 'julia-found')
    step("$('ap-fold').click(); const e = $('juliaPreset'); const o = [...e.options].find(x => x.text.startsWith('Douady rabbit')); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); await settle(); const f = $('juliaFound'), row = f.closest('.pick-row'); await show($('juliaPanel')); return { button: f.textContent, buttonBox: Math.round(f.getBoundingClientRect().left) + '..' + Math.round(f.getBoundingClientRect().right), rowBox: Math.round(row.getBoundingClientRect().left) + '..' + Math.round(row.getBoundingClientRect().right), wraps: f.getBoundingClientRect().height };", 'julia-found-rabbit')
    with io.open(OUT + 'views-%s.json' % tag, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(steps, f, indent=1, ensure_ascii=False)
    print(len(steps), 'steps ->', OUT + 'views-%s.json' % tag)


build('1400')
build('375')
