"""Engineer "dial", round 10: the arrows at both ends of EVERY number box, usual ranges and extreme ranges.

  python out/r10/dial/ends.py dist/v9m.html before
  python out/r10/dial/ends.py dist/r10-dial.html after

For each box: the arrows on the dial's own (fine) step; from three steps above the low typed limit, down six times
and up six times; from three steps below the high typed limit, up six times and down six times; ten steps at once
(Shift) into each limit, one more press, and ten steps back. Presses are scripted clicks on the arrow buttons
(the page's own handler for keyboard and scripted clicks); values are typed into the box and committed with Enter.
Writes out/r10/dial/ends-<tag>.json and prints one line per box and range.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402
drive.URL = sys.argv[1]
drive.HERE = HERE
tag = sys.argv[2]
for s in (sys.stdout, sys.stderr):
    s.reconfigure(encoding="utf-8", errors="replace")

WALK = r"""
const out = [];
for (const n of [...document.querySelectorAll('input[id$=Num]')].filter(n => n.closest('.dial'))) {
  const id = n.id.replace(/Num$/, ''), e = n.closest('.dial'), s = document.getElementById(id), t = document.getElementById(id + 'Step');
  const up = e.querySelector('.dial-up'), down = e.querySelector('.dial-down');
  const lo = +n.getAttribute('aria-valuemin'), hi = +n.getAttribute('aria-valuemax');
  const whole0 = t ? t.getAttribute('aria-pressed') === 'true' : false;
  if (whole0) t.click();                                   // the dial's own step, not whole numbers
  const odd = /^Odd/.test(n.title);
  const f = t ? +t.textContent.replace('±', '') : odd ? 2 : 1;
  const base = s ? +s.min : lo;
  const dec = x => +x.toFixed(8);
  const type = v => { n.focus(); n.value = String(v); n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true })); n.blur(); };
  const press = (b, shift) => { b.dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 0, shiftKey: !!shift })); return n.value; };
  const v0 = n.value;
  const a = dec(base + Math.ceil((lo + 2.5 * f - base) / f - 1e-9) * f), z = dec(base + Math.floor((hi - 2.5 * f - base) / f + 1e-9) * f);
  const row = { id, label: (e.querySelector('label') || {}).textContent.trim().slice(0, 40), step: f, lo, hi, slider: s ? [+s.min, +s.max, +s.step] : null };
  type(a); row.low = [n.value]; for (let i = 0; i < 6; i++) row.low.push(press(down)); for (let i = 0; i < 6; i++) row.low.push(press(up));
  type(z); row.high = [n.value]; for (let i = 0; i < 6; i++) row.high.push(press(up)); for (let i = 0; i < 6; i++) row.high.push(press(down));
  type(a); row.low10 = [n.value, press(down, true), press(down), press(up, true), press(up)];
  type(z); row.high10 = [n.value, press(up, true), press(up), press(down, true), press(down)];
  type(lo); row.fromLo = [n.value, press(up), press(up), press(down), press(down), press(down)];
  type(hi); row.fromHi = [n.value, press(down), press(down), press(up), press(up), press(up)];
  type(v0);
  if (whole0) t.click();
  row.back = [n.value, v0, t ? t.textContent : null];
  out.push(row);
}
return out;
"""

page, proc, prof = drive.launch()
d = drive.Drive(page); d.load(); drive.open_all(d)
d.click(drive.E("qUltra")); d.idle(300)
res = {}
for mode in ("usual", "extreme"):
    if mode == "extreme":
        d.click(drive.E("extreme"))
    res[mode] = d.js(WALK)
    for r in res[mode]:
        print("%s %s '%s' step %s typed %s..%s | low %s | high %s | ten down %s | ten up %s | from lo %s | from hi %s" % (
            mode, r["id"], r["label"], r["step"], r["lo"], r["hi"], r["low"], r["high"], r["low10"], r["high10"], r["fromLo"], r["fromHi"]), flush=True)
    bad = [r["id"] for r in res[mode] if r["back"][0] != r["back"][1]]
    print("info  %s: %d boxes walked; start value not back in: %s" % (mode, len(res[mode]), bad), flush=True)
with open(os.path.join(HERE, "ends-%s.json" % tag), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
drive.finish(page, proc, prof, "ends")
