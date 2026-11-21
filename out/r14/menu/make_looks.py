"""Write the action files for the menu's screenshots (round 14, menu engineer).

  python out/r14/menu/make_looks.py   -> out/r14/menu/looks-<tag>.json, one per window size and theme
Run each with:
  python tools/shot.py --url dist/r14-menu.html --size 1400x950 --theme light --actions out/r14/menu/looks-wide-light.json
Pictures go to out/r14/menu/looks/.
"""
import io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const hover = id => document.querySelector('#rules .rule[data-ap="' + id + '"] .name').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'mouse' }));
"""


def looks(tag, phone):
    out = 'out/r14/menu/looks/%s-' % tag
    steps = []

    def step(js, shot=None, clip=None, sleep=0.4):
        a = {'js': PRE + js.strip()}
        steps.append(a)
        if sleep:
            steps.append({'sleep': sleep})
        if shot:
            b = {'shot': out + shot + '.png'}
            if clip:
                b['clip'] = clip
            steps.append(b)

    step("L.R.warmOn = false; L.S.q.aa = 2; L.touch(); return 'page opened';", sleep=2.5)
    step("$('apMenuBtn').scrollIntoView({ block: 'center' }); return 'closed, scrollY ' + scrollY;" if phone else "return 'closed';", '1-closed')
    step("$('apMenuBtn').dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 })); await sleep(200); return 'open: list ' + JSON.stringify($('apPop').getBoundingClientRect()) + ' window ' + innerWidth + ' x ' + innerHeight + ', list scrolls: ' + ($('rules').scrollHeight > $('rules').clientHeight);", '2-open')
    step("hover('tilt'); const b = $('apInfo'); return 'hover on tilt: ' + b.textContent.slice(0, 80) + ' box ' + JSON.stringify(b.getBoundingClientRect()) + '; explanations that need scrolling inside their box: ' + L.APPROACHES.filter(a => { hover(a.id); return b.scrollHeight > b.clientHeight + 1; }).map(a => a.id + ' ' + b.scrollHeight + '/' + b.clientHeight).join(', ') + (hover('tilt'), '');", '3-open-hover')
    step("const last = L.APPROACHES[L.APPROACHES.length - 1].id; $('rules').scrollTop = 9999; hover(last); return 'hover on the last entry ' + last + ', info height ' + $('apInfo').getBoundingClientRect().height + ' of scroll ' + $('apInfo').scrollHeight;", '4-open-hover-last')
    step("$('ap-bulb').click(); await sleep(200); return 'bulb chosen by a script click on the open list; list hidden: ' + $('apPop').hidden + ', button: ' + $('apMenuName').textContent;", '5-bulb', sleep=2.5)
    step("$('apMenuBtn').click(); await sleep(150); const k = (el, key) => el.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true })); k(document.activeElement, 'ArrowDown'); k(document.activeElement, 'ArrowDown'); const f = document.activeElement; return 'keyboard: focus on ' + f.id + ', focus ring ' + !!document.querySelector('#rules .rule.is-focus') + ', explanation shown ' + !$('apInfo').hidden + ', chosen still ' + $('apMenuName').textContent;", '5b-keyboard-focus')
    step("document.activeElement.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true })); $('apAboutBtn').click(); $('apAboutBtn').scrollIntoView({ block: 'nearest' }); return 'about open: ' + $('apAbout').textContent.slice(0, 80) + '; box ' + JSON.stringify($('apAbout').getBoundingClientRect());", '6-about')
    step("$('apAboutBtn').click(); $('mode-l').click(); await sleep(300); " + ("$('secApproach').scrollIntoView({ block: 'start' }); " if phone else "") + "return 'learn on; equation part height ' + $('secEq').getBoundingClientRect().height;", '7-learn')
    step("$('apMenuBtn').click(); await sleep(200); hover('classic'); return 'learn, menu open';", '8-learn-open')
    step("$('apMenuBtn').click(); $('mode-m').click(); await sleep(200); document.querySelectorAll('details.sec').forEach(d => { d.open = d.id === 'secApproach'; }); " + ("$('secApproach').scrollIntoView({ block: 'start' }); " if phone else "") + "return 'whole section';", '9-section', clip='#secApproach', sleep=1.5)
    path = os.path.join(ROOT, 'out', 'r14', 'menu', 'looks-%s.json' % tag)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(steps, f, indent=1, ensure_ascii=False)
    print('%d actions -> %s' % (len(steps), os.path.relpath(path, ROOT)))


for tag, phone in [('wide-light', False), ('wide-dark', False), ('phone-light', True), ('phone-dark', True)]:
    looks(tag, phone)
