"""Round 28, truth checker, an addition to 1.4 a: is EVERY state the dials lead to an object?

  python out/r28/fix/truth/mk/i_walk.py      -> out/r28/fix/truth/logs/i_walk.txt

Section 1.4 a says for which (second sphere, size) the thing is an object: second sphere 100 and size <= 100, or
second sphere <= 50 and size x second sphere <= 100 x 100. My lists confirm that (a_object.py) and show that anything
else overlaps (a_past.py, and the values between 50 and 100). So the page must never hold anything else. Here the two
dials are moved 600 times at random (typed values, also far outside the ends and inside the gap; slider positions;
the reset button now and then), and after every move the state is read: S.k.brho, S.k.bt, and what the two boxes show.
(The events are made by script, not by a real mouse: this is a test of where the state can go, not of the handling.
The builder's mk/dials28.py and the dial checker use real keys.)
Also written down, for the orchestrator: how often the page's answer to a move of the SIZE differs from the letter of
decision 4 ("rho becomes min(0.5, 50 / p) when p rho > 100", and nothing otherwise), which is the builder's first known gap.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import pagerun as R

rng = np.random.default_rng(600)
ops = []
for i in range(600):
    k = rng.random()
    if k < 0.34:
        v = rng.choice([rng.uniform(1, 2000), rng.uniform(90, 110), rng.uniform(190, 210), rng.uniform(100, 400), 0.5, 2500.0, 100.0, 200.0, 400.0, 100.01, 99.99, 1.0, 2000.0])
        ops.append(['typeSize', round(float(v), 2)])
    elif k < 0.62:
        v = rng.choice([rng.uniform(0, 120), rng.uniform(40, 100), 50.0, 51.0, 75.0, 75.01, 76.0, 100.0, 2.0, 1.0, 99.0, 49.9, 25.0])
        ops.append(['typeRho', round(float(v), 2)])
    elif k < 0.8:
        ops.append(['slideSize', round(float(rng.uniform(2, 400)), 1)])
    elif k < 0.97:
        ops.append(['slideRho', int(rng.integers(2, 101))])
    else:
        ops.append(['reset', 0])

JS = """
const OPS = %s, out = [];
$('ap-balls').click(); await settle();
const type = (id, v) => { const n = $(id); n.focus(); n.value = String(v); n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true })); };
const slide = (id, v) => { const r = $(id); r.value = String(v); r.dispatchEvent(new Event('input', { bubbles: true })); r.dispatchEvent(new Event('change', { bubbles: true })); };
const resetBtn = () => Array.from(document.querySelectorAll('button')).find(b => /Reset this section/.test(b.textContent) && b.getClientRects().length && b.closest('section, details, .group, div') && (b.closest('#kleinPanel') || $('kleinPanel').contains(b)));
const read = () => ({ rho: S.k.brho, t: S.k.bt, size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, warn: (() => { const w = $('ballsWarn'); return w && w.getClientRects().length ? w.textContent : ''; })() });
out.push(['open', 0, read()]);
let hadReset = !!resetBtn();
for (const [op, v] of OPS) {
  if (op === 'typeSize') type('ballsSizeNum', v);
  else if (op === 'typeRho') type('ballsRhoNum', v);
  else if (op === 'slideSize') slide('ballsSize', v);
  else if (op === 'slideRho') slide('ballsRho', v);
  else if (op === 'reset') { const b = resetBtn(); if (b) b.click(); }
  await sleep(15);
  out.push([op, v, read()]);
}
await settle();
return JSON.stringify({ hadReset, out, sig: String(L.R.sig || ''), failed: L.R.failed || '' });
"""

if __name__ == '__main__':
    code, text, vals = R.run(R.PAGE, [JS % json.dumps(ops)], 'i_walk')
    d = json.loads(vals[-1]); rows = d['out']
    lines = ['page %s, exit %d, %s; a reset button was found: %s; program at the end "%s", failed "%s"' % (R.PAGE, code, 'no console errors' if R.clean(text) else 'CONSOLE: see logs/i_walk.log', d['hadReset'], d['sig'].replace('\n', '/'), d['failed'])]
    bad = 0; shown_bad = 0; letter = 0; nsize = 0; follow = 0; seen = set(); prev = rows[0][2]; kinds = {}
    for op, v, s in rows:
        rho, t = s['rho'], s['t']; p = 100 / (2 * t - 1)
        ok = (rho == 1 or (0.02 - 1e-12 <= rho <= 0.5 + 1e-12)) and p * rho <= 100 * (1 + 1e-9) and t >= (1 + rho) / 2 - 1e-12 and 1 - 1e-9 <= p <= 2000 * (1 + 1e-9)
        if not ok:
            bad += 1; lines.append('   NOT AN OBJECT after %s %s: second sphere %.6g, size %.6g (size x second sphere = %.6g)' % (op, v, rho, p, p * rho))
        try:
            shown_ok = abs(float(s['size']) - p) <= 0.0051 + 1e-9 and abs(float(s['second']) - 100 * rho) <= 0.0051
        except ValueError:
            shown_ok = False
        if not shown_ok:
            shown_bad += 1
            if shown_bad <= 12:
                lines.append('   the boxes do not show the state after %s %s: boxes "%s" and "%s", state size %.4f, second sphere %.4f' % (op, v, s['size'], s['second'], p, 100 * rho))
        if op in ('typeSize', 'slideSize'):
            nsize += 1
            want_p = min(max(float(v), 1.0 if op == 'typeSize' else 2.0), 2000.0 if op == 'typeSize' else 400.0)
            r0 = prev['rho']
            by_letter = max(0.02, min(0.5, 50 / want_p)) if want_p * r0 > 100 * (1 + 1e-9) else r0
            if abs(rho - by_letter) > 1e-9:
                letter += 1
                if letter <= 8:
                    lines.append('   beyond the letter of decision 4: size set to %.2f while the second sphere was %.4g %%: by the letter it stays/becomes %.4g %%, the page made it %.4g %%' % (want_p, 100 * r0, 100 * by_letter, 100 * rho))
        kinds[op] = kinds.get(op, 0) + 1
        seen.add((round(rho, 6), round(p, 3))); prev = s
    lines.append('%d moves (%s), %d different states met.' % (len(rows) - 1, ', '.join('%s %d' % kv for kv in sorted(kinds.items()) if kv[0] != 'open'), len(seen)))
    lines.append('States that are NOT an object (second sphere between 50 and 100, or size x second sphere > 100 x 100, or t below (1 + rho) / 2, or a size outside 1..2000): %d' % bad)
    lines.append('Moves after which the two boxes do not show the state (to 0.005): %d' % shown_bad)
    lines.append('Moves of the size (%d) after which the second sphere is not what the letter of decision 4 gives: %d (the builder\'s "follows" rule; every one of them is still an object)' % (nsize, letter))
    rhos = sorted(set(r for r, _ in seen)); lines.append('Second spheres met: least %.4g, most below 1: %.4g, and 1: %s' % (rhos[0], max([r for r in rhos if r < 1] or [0]), 1.0 in rhos))
    out = '\n'.join(lines) + '\n'
    open(os.path.join(R.LOGS, 'i_walk.txt'), 'w', encoding='utf-8', newline='\n').write(out); print(out)
    json.dump(rows, open(os.path.join(R.LOGS, 'i_walk-states.json'), 'w', encoding='utf-8'))
