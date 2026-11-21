"""Round 28, truth checker: the exact steps named in my notes for the give-way of the two dials, on the page.
  python out/r28/fix/truth/mk/i_steps.py      -> out/r28/fix/truth/logs/i_steps.txt
(Typed values, made by script as in i_walk.py. After each step: the second sphere and the size the page holds, and
what the bare formula of decision 4 would hold: "size set to p with p rho > 100: rho becomes min(0.5, 50 / p)";
"second sphere set to rho with p rho > 100: p becomes 50 / rho"; nothing else changes.)"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pagerun as R
STEPS = [['size', 150], ['size', 250], ['size', 90], ['size', 300], ['size', 99.99], ['second', 20], ['size', 250], ['size', 600], ['second', 100], ['size', 101], ['size', 199], ['size', 201], ['second', 60], ['second', 80], ['size', 2000], ['size', 5000], ['second', 1], ['reset', 0]]
JS = """
const ST = %s, out = [];
$('ap-balls').click(); await settle();
const type = (id, v) => { const n = $(id); n.focus(); n.value = String(v); n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true })); };
const read = () => ({ rho: S.k.brho, t: S.k.bt, size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, warn: (() => { const w = $('ballsWarn'); return w && w.getClientRects().length ? w.textContent : ''; })() });
out.push(read());
for (const [what, v] of ST) {
  if (what === 'size') type('ballsSizeNum', v); else if (what === 'second') type('ballsRhoNum', v);
  else { const b = Array.from(document.querySelectorAll('button')).find(b => /Reset this section/.test(b.textContent) && b.getClientRects().length && $('kleinPanel').contains(b)); if (b) b.click(); }
  await settle(); out.push(read());
}
return JSON.stringify(out);
"""
code, text, vals = R.run(R.PAGE, [JS % json.dumps(STEPS)], 'i_steps')
rows = json.loads(vals[-1]); lines = ['page %s, exit %d, %s' % (R.PAGE, code, 'no console errors' if R.clean(text) else 'CONSOLE')]
rho, p = rows[0]['rho'], 100 / (2 * rows[0]['t'] - 1)                       # what the bare formula holds
lines.append('as opened: second sphere %s, size %s' % (rows[0]['second'], rows[0]['size']))
for (what, v), s in zip(STEPS, rows[1:]):
    if what == 'size':
        p = min(max(float(v), 1.0), 2000.0)
        if p * rho > 100 * (1 + 1e-9):
            rho = max(0.02, min(0.5, 50 / p))
    elif what == 'second':
        rho = 1.0 if v > 75 else min(0.5, max(0.02, v / 100))
        if p * rho > 100 * (1 + 1e-9):
            p = 50 / rho
    else:
        rho, p = 1.0, 100 / 1.8
    same = abs(s['rho'] - rho) < 1e-9 and abs(100 / (2 * s['t'] - 1) - p) < 1e-6
    lines.append('%-7s %-8s -> the page: second sphere %-6s size %-8s | the bare formula: second sphere %-6.5g size %-8.6g | %s | "%s"' % (what, v if what != 'reset' else '', s['second'], s['size'], 100 * rho, p, 'the same' if same else 'DIFFERENT', s['warn']))
    rho, p = s['rho'], 100 / (2 * s['t'] - 1)                               # go on from where the page is
out = '\n'.join(lines) + '\n'; open(os.path.join(R.LOGS, 'i_steps.txt'), 'w', encoding='utf-8', newline='\n').write(out); print(out)
