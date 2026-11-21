"""Round 12, checker of the page: where the page stops after a button of the closing text is pressed at phone width,
sampled over 4 seconds.  python out/r12/check-page/make_scroll2.py -> scroll2.json (new buttons first), scroll2-old.json (buttons Version 11 has)"""
import io, json

OUT = 'out/r12/check-page/'
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { await sleep(250); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 100000) throw new Error('not finished after 100 s'); await sleep(50); } };
const press = async id => { const b = $(id); if (!b) return id + ': this page has no such button'; b.scrollIntoView({ block: 'center' }); await sleep(400); const y0 = Math.round(scrollY), h0 = document.documentElement.scrollHeight; b.click(); const ys = []; for (let k = 0; k < 20; k++) { await sleep(200); ys.push(Math.round(scrollY)); } await settle(); const r = $('stage').getBoundingClientRect(); const vis = Math.max(0, Math.min(r.bottom, innerHeight) - Math.max(r.top, 0));
  return b.textContent + ': from ' + y0 + ', page height ' + h0 + ' -> ' + document.documentElement.scrollHeight + ', scroll position every 0.2 s: ' + ys.join(' ') + '; in the end picture at ' + Math.round(r.top) + '..' + Math.round(r.bottom) + ' (' + Math.round(100 * vis / r.height) + '% on screen), top of the picture in the page at ' + Math.round(r.top + scrollY); };
"""


def write(name, ids):
    steps = [{'js': PRE + "await settle(); return 'ready';"}]
    for b in ids:
        steps.append({'js': PRE + "return await press('%s');" % b})
    json.dump(steps, io.open(OUT + name + '.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)


write('scroll2', ['quatShow', 'tiltShow', 'quatShow', 'fig4Show', 'fig4Back', 'fig4Show', 'twinMerc', 'twinOff'])
write('scroll2-old', ['fig4Show', 'fig4Back', 'fig4Show', 'twinMerc', 'twinLathe', 'twinOff'])
print('written')
