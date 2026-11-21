"""Every trap solid example through its drop-down: what it set, how many probes hit, a picture.
  python out/r7/page/examples.py [tag]   -> out/r7/page/examples-<tag>.json, pictures ex-<tag>-<n>.png"""
import io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1] if len(sys.argv) > 1 else 'd'
PRE = r"""const L = squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) if (L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11)) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } return n + ' of 165 probes hit, ' + ring + ' on the outer ring'; };
const pickEx = i => { const e = $('trapExamples'); e.value = String(i + 1); e.dispatchEvent(new Event('change', { bubbles: true })); };
const state = () => { const e = $('trapExamples'), c = S.colour; return '[' + (e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : 'nothing') + '] mode ' + S.mode + ', c ' + S.c + ', trap ' + c.trap + ', solid ' + c.solid + ', thick ' + c.thick + ', skip ' + c.skip + ', radius ' + c.radius + ', cam ' + [cam.yaw, cam.pitch, cam.dist].map(x => +x.toFixed(3)) + ' target ' + cam.target.map(x => +x.toFixed(3)); };
"""
steps = [{'js': PRE + "document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); const e = $('trapExamples'), h = $('exampleHost'); return 'examples: ' + [...e.options].map(o => o.text).join(' | ') + '; groups ' + [...e.querySelectorAll('optgroup')].map(g => g.label) + '; on show ' + (h.getBoundingClientRect().width > 0) + '; reads [' + (e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : '') + ']; after ' + h.previousElementSibling.textContent.slice(0, 40);", 'wait': 'done', 'timeout': 240}]
for i in range(9):
    js = ("const g = grid(); " if i else "const g = 'start'; ") + "pickEx(%d); await sleep(300); return 'before: ' + g + '. now ' + state();" % i
    steps.append({'js': PRE + js, 'wait': 'done', 'timeout': 240, 'shot': 'out/r7/page/ex-%s-%d.png' % (tag, i + 1), 'clip': '#stage'})
steps.append({'js': PRE + "return 'last: ' + grid();"})
path = os.path.join(HERE, 'examples-%s.json' % tag)
io.open(path, 'w', encoding='utf-8', newline='\n').write(json.dumps(steps, indent=1, ensure_ascii=False))
print(len(steps), 'steps ->', path)
