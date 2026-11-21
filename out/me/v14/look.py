"""My own look at the joined page (v14b): the menu with all 15 entries, wide and phone."""
import io, json, os, sys
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const hover = id => document.querySelector('#rules .rule[data-ap="' + id + '"] .name').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'mouse' }));
"""
def looks(tag, phone):
    out = 'out/me/v14/%s-' % tag
    steps = []
    def step(js, shot=None, sleep=0.5):
        steps.append({'js': PRE + js.strip()})
        if sleep: steps.append({'sleep': sleep})
        if shot: steps.append({'shot': out + shot + '.png'})
    scroll = "$('apMenuBtn').scrollIntoView({ block: 'center' }); " if phone else ""
    step("L.R.warmOn = false; L.S.q.aa = 2; L.touch(); return 'entries ' + L.APPROACHES.map(a => a.id).join(' ') + ' | groups ' + L.APPROACH_GROUPS.map(g => g.id).join(' ');", sleep=2.5)
    step(scroll + "return 'closed';", '1-closed')
    step("$('apMenuBtn').dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 })); await sleep(200); return 'open; list scrolls: ' + ($('rules').scrollHeight > $('rules').clientHeight) + ' ' + $('rules').scrollHeight + '/' + $('rules').clientHeight;", '2-open')
    step("hover('kleinsq'); const b = $('apInfo'); return 'hover kleinsq: ' + b.textContent.length + ' chars, box ' + Math.round(b.getBoundingClientRect().height) + ' of ' + b.scrollHeight;", '3-hover-kleinsq')
    step("$('ap-quat4').click(); await sleep(300); return 'chosen: ' + $('apMenuName').textContent + '; dials shown: ' + ['w','tilt','cw'].map(k => !!$('par-quat4-' + k) && $('par-quat4-' + k).getBoundingClientRect().width > 0).join();", '4-quat4', sleep=3)
    step("const e = $('par-quat4-w'); e.value = 0.3; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); await sleep(200); return 'w = ' + L.S.param.quat4.w;", '5-quat4-w03', sleep=3)
    step("$('apAboutBtn').click(); $('apAboutBtn').scrollIntoView({ block: 'nearest' }); return 'about: ' + $('apAbout').textContent.slice(0, 200);", '6-about')
    step("$('apAboutBtn').click(); $('ap-kleinsq2').click(); await sleep(200); $('mode-j').click(); await sleep(200); return 'kleinsq2 julia: ' + $('apMenuName').textContent + ' c ' + JSON.stringify(L.S.c || L.S.jc || null);", '7-kleinsq2-julia', sleep=3.5)
    step("$('ap-rotorframe').click(); await sleep(200); $('mode-m').click(); return 'rotorframe m';", '8-rotorframe', sleep=3.5)
    step("$('ap-rotor').click(); await sleep(200); return 'rotor: lat ' + L.S.param.rotor.lat + ' lon ' + L.S.param.rotor.lon + '; failed ' + JSON.stringify(L.R.failed || null);", '9-rotor', sleep=3.5)
    p = 'out/me/v14/look-%s.json' % tag
    json.dump(steps, io.open(p, 'w', encoding='utf-8', newline='\n'), indent=1)
    print(p)
looks('wide', False); looks('phone', True)
