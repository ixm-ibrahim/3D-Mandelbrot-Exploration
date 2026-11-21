"""Round 12, checker of the page: press each button of the closing text from where it stands (scrolled down to it),
and see whether the picture comes into view.  python out/r12/check-page/make_scroll.py -> scroll-1400.json, scroll-375.json"""
import io, json

OUT = 'out/r12/check-page/'
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { await sleep(250); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 100000) throw new Error('not finished after 100 s'); await sleep(50); } };
const press = async id => { const b = $(id); b.scrollIntoView({ block: 'center' }); await sleep(250); const y0 = Math.round(scrollY), r0 = b.getBoundingClientRect(); const seen0 = r0.top >= 0 && r0.bottom <= innerHeight; b.click(); await sleep(900); await settle(); const r = $('stage').getBoundingClientRect(); const vis = Math.max(0, Math.min(r.bottom, innerHeight) - Math.max(r.top, 0));
  return b.textContent + ': button on screen before the click ' + seen0 + ', page scrolled from ' + y0 + ' to ' + Math.round(scrollY) + ', picture at ' + Math.round(r.top) + '..' + Math.round(r.bottom) + ' of ' + innerHeight + ' (' + Math.round(100 * vis / r.height) + '% on screen), approach ' + L.APPROACHES[L.S.approach].id + ', mode ' + L.S.mode + ', focus on ' + (document.activeElement.id || document.activeElement.tagName); };
"""
for tag in ('1400', '375'):
    steps = [{'js': PRE + "await settle(); return 'ready, window ' + innerWidth + 'x' + innerHeight + ', page ' + document.documentElement.scrollHeight + ' px tall';"}]
    for i, b in enumerate(['fig4Show', 'fig4Back', 'twinMerc', 'twinLathe', 'twinBulb', 'twinOff', 'quatShow', 'tiltShow']):
        steps.append({'js': PRE + "return await press('%s');" % b, 'shot': OUT + 'scroll-%s-%d-%s.png' % (tag, i + 1, b)})
    json.dump(steps, io.open(OUT + 'scroll-%s.json' % tag, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('written')
