"""Round 22, entry, second pass: the renamed dial of Pulled plane in a phone-sized window (390 x 844), and the texts
of both entries as the page shows them.   python out/r22/entry/phone.py   -> phone.log, phone-pulledplane.png"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

STEPS = [run.UP, dict(js=run.HEAD + """
$('mode-j').click(); await sleep(150); $('ap-pulledplane').click(); await sleep(300); S.c = [-1, 0, 0]; S.iter = 40; go(); await settle();
const W = window.innerWidth, wide = [];
for (const e of document.querySelectorAll('#pd-pulledplane *')) { const r = e.getBoundingClientRect(); if (r.width > 0 && (r.right > W + 1 || r.left < -1)) wide.push(e.tagName + ' ' + Math.round(r.left) + '..' + Math.round(r.right)); }
const lab = [...document.querySelectorAll('#pd-pulledplane label, #pd-pulledplane .label, #pd-pulledplane span')].filter(e => /How little a thing near the page turns it/i.test(e.textContent) && e.children.length === 0)[0];
const r = lab ? lab.getBoundingClientRect() : null;
const sw = document.scrollingElement.scrollWidth;
if (sw > W + 1) fail('the page scrolls sideways: ' + sw + ' in a window of ' + W);
if (wide.length) fail('wider than the window: ' + wide.slice(0, 5).join('; '));
if (!r) fail('the label of the second dial was not found');
const g = grid();
const el = $('pd-pulledplane'); el.scrollIntoView({ block: 'center' }); await sleep(300);
return JSON.stringify({ window: [W, window.innerHeight], scrollWidth: sw, label: [Math.round(r.left), Math.round(r.right), Math.round(r.height)], probes: g[0] });
""", wait='done', timeout=600, shot='out/r22/entry/phone-pulledplane.png')]

if __name__ == '__main__':
    code, text, vals = run.shot(run.PAGE, STEPS, 'phone-steps', '390x844')
    run.write('phone.log', text + 'exit %d\n' % code)
    print(text[-1500:]); print('exit', code)
    sys.exit(code)
