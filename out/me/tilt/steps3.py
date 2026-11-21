"""Load test of the split approach list: python out/me/tilt/steps3.py -> out/me/tilt/steps3.json"""
import io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HEAD = """
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
"""
steps = []
def step(js, name, shot=True):
    s = {"js": HEAD + js, "timeout": 900, "wait": "done"}
    if shot:
        s["shot"] = "out/me/tilt/t-" + name + ".png"; s["clip"] = "#stage canvas"
    steps.append(s)

# numbers first: every rule against the complex power in the plane z = 0, and off the plane against its own claim
step("""
const cpow = (x, y, n) => { const r = Math.hypot(x, y), a = Math.atan2(y, x) * n, R = Math.pow(r, n); return [R * Math.cos(a), R * Math.sin(a)]; };
const out = {};
for (const a of L.APPROACHES) {
  const q = {}; (a.params || []).filter(s => s.key !== undefined).forEach(s => { q[s.key] = s.def; });
  if (a.id === 'tilt') q.tilt = 40;
  let worst = 0, offPlane = 0;
  for (const n of [2, 3, -1, 2.5]) for (let k = 0; k < 400; k++) {
    const x = Math.sin(k * 12.9898) * 1.7, y = Math.cos(k * 78.233) * 1.7;
    if (n === 2.5 && Math.abs(Math.atan2(y, x)) > 3.0) continue;   // stay off the branch cut
    const v = L.MATH[a.id]([x, y, 0], n, q), w = cpow(x, y, n), s = Math.hypot(w[0], w[1]) || 1;
    worst = Math.max(worst, Math.hypot(v[0] - w[0], v[1] - w[1], v[2]) / s);
  }
  out[a.id] = worst.toExponential(1);
}
return JSON.stringify(out) + ' | groups: ' + L.APPROACHES.map(a => a.id + ':' + a.group).join(' ');
""", "numbers", shot=False)
for aid in ['mercator', 'fold', 'lathe', 'tilt', 'bulb', 'classic', 'split']:
    step("$('ap-%s').click(); await sleep(400); $('mode-m').click(); await sleep(200); L.resetCam(); go(); await sleep(200); return '%s: ' + L.APPROACHES[L.S.approach].name + ' | uA ' + JSON.stringify(Object.values(L.S.param['%s']));" % (aid, aid, aid), "m-" + aid)
step("$('ap-fold').click(); await sleep(300); $('mode-j').click(); await sleep(200); L.S.c = [-1, 0, 0]; L.resetCam(); go(); await sleep(200); return 'fold, basilica (Figure 4 look expected)';", "j-fold-bas")
step("$('ap-mercator').click(); await sleep(300); L.S.param.mercator.turn = 40; go(); await sleep(200); return 'one plane, turn 40';", "j-merc-turn40")

io.open(os.path.join(ROOT, 'out', 'me', 'tilt', 'steps3.json'), 'w', encoding='utf-8').write(json.dumps(steps, indent=1))
print(len(steps), 'steps')
