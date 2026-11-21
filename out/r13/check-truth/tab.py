"""Round 13, truth checker: what the Learn tab shows against the numbers. Writes tab.txt and pictures tab-*.png."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SHOT = 'out/r13/check-truth/'

HELP = r"""
window.__T = (() => {
  const SL = window.squaringLab, L = SL.learn, S = SL.S, APS = SL.APPROACHES, MATH = SL.MATH;
  const len = v => Math.hypot(v[0], v[1], v[2]), sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const modv = (v, space) => v.map((x, i) => { if (i >= space) return x; let y = S.abs[i] ? Math.abs(x) : x; if (i === 1 && S.flip[0]) y = -y; if (i === 2 && S.flip[1]) y = -y; return y; });
  function cpow(x, y, n) { const r = Math.hypot(x, y), th = Math.atan2(y, x), R = Math.pow(r, n); return [R * Math.cos(n * th), R * Math.sin(n * th), 0]; }
  function setAp(id) { S.approach = APS.findIndex(a => a.id === id); SL.refresh(); SL.touch(); }
  function check(label) {
    const st0 = L.state(), id = APS[S.approach].id, sp = st0.space;
    const plan = SL.learnPlan({ space: sp, id, params: S.param[id], n: S.n, c: st0.c, abs: S.abs, flip: S.flip });
    const pts = [st0.z.slice()]; for (const m of plan.moves) pts.push(m.at(pts[pts.length - 1], 1));
    let worst = 0, sayBad = 0, n = 0, posBad = 0; const sayEx = [];
    plan.moves.forEach((m, j) => { for (const t of [0, 0.5, 1]) {
      const st = L.goto(j, t), want = m.at(pts[j], t), e = len(sub(st.point, want)); worst = Math.max(worst, e); n++;
      if (!(st.move === j && Math.abs(st.t - t) < 1e-9)) posBad++;
      const s = m.say(pts[j], pts[j + 1]);
      if (!st.done && st.sentence !== s) { sayBad++; if (sayEx.length < 2) sayEx.push([st.sentence, s]); }
      const dom = document.getElementById('learnSay'); if (dom && !st.done && dom.textContent.trim() !== s.trim() && sayEx.length < 2) { sayBad++; sayEx.push(['DOM: ' + dom.textContent, s]); }
    } });
    const end = L.goto(plan.moves.length - 1, 1);
    const u = modv(st0.z, sp), ref = add(sp === 3 ? MATH[id](u, S.n, S.param[id]) : cpow(u[0], u[1], S.n), st0.c);
    return { label, id, space: sp, n: S.n, z: st0.z, c: st0.c, moves: st0.moves, namesOK: JSON.stringify(st0.moves) === JSON.stringify(plan.moves.map(m => m.name)), checked: n, worstPointGap: worst, posBad, sayBad, sayEx,
      endVsRule: len(sub(end.point, ref)), doneSentence: end.sentence, domSay: (document.getElementById('learnSay') || {}).textContent };
  }
  return { setAp, check, cpow };
})();
return 'ok';
"""

IDS = ['mercator', 'fold', 'lathe', 'tilt', 'bulb', 'classic', 'split', 'softfold', 'axisbulb', 'pillow']
acts = [
    {'js': "document.getElementById('mode-l').click(); return JSON.stringify({learn: window.squaringLab.S.learn, cls: document.body.className});", 'sleep': 0.5},
    {'js': HELP},
    {'js': "return JSON.stringify(window.__T.check('2D default'));"},
    {'js': "window.squaringLab.learn.set({space: 1}); return JSON.stringify(window.__T.check('1D default'));"},
]
for i in IDS:
    acts.append({'js': "window.squaringLab.learn.set({space: 3}); window.__T.setAp('%s'); return JSON.stringify(window.__T.check('3D %s'));" % (i, i)})
# other powers and a modifier
acts.append({'js': "const SL = window.squaringLab; SL.S.n = 3; SL.touch(); window.__T.setAp('lathe'); const a = window.__T.check('3D lathe n=3'); SL.S.n = -2; SL.touch(); const b = window.__T.check('3D lathe n=-2'); SL.S.flip = [0, 1]; SL.S.abs = [1, 0, 0]; SL.touch(); const c = window.__T.check('3D lathe n=-2 |x| flip z'); SL.S.flip = [0, 0]; SL.S.abs = [0, 0, 0]; SL.S.n = 2.5; SL.touch(); SL.learn.set({space: 1}); const d = window.__T.check('1D n=2.5'); SL.learn.set({space: 2}); const e = window.__T.check('2D n=2.5'); SL.S.n = 2; SL.touch(); return JSON.stringify([a, b, c, d, e]);"})
# the 1D orbit from the tab's own starting point: Next step again and again
acts.append({'js': """const SL = window.squaringLab, L = SL.learn; SL.S.n = 2; SL.touch(); L.reset && 0; L.set({space: 1, z: [-1.2, 0, 0], c: [-0.6, 0, 0], hidden: true}); const out = []; let x = -1.2;
for (let k = 0; k < 9; k++) { const st = L.goto(0, 0.5); out.push({ step: st.step, z: st.z, own: x, turn: st.sentence, pointMid: st.point }); x = x * x - 0.6; if (L.next() === false) break; }
return JSON.stringify(out);"""})
# pictures
def shot(name, js, clip='.bench-main'):
    acts.append({'js': js + " const st = window.squaringLab.learn.state(); return JSON.stringify({pic: '%s', sentence: st.sentence, point: st.point, z: st.z, move: st.move, t: st.t, moves: st.moves});" % name, 'sleep': 0.6, 'shot': SHOT + 'tab-' + name + '.png', 'clip': clip})

shot('1d-hidden-turn', "const SL = window.squaringLab, L = SL.learn; L.set({space: 1, z: [-1.2, 0, 0], c: [-0.6, 0, 0], hidden: true}); L.goto(0, 0.5);")
shot('1d-step4-turn', "const SL = window.squaringLab, L = SL.learn; L.next(); L.next(); L.next(); L.goto(0, 0.5);")
shot('2d-turn', "const SL = window.squaringLab, L = SL.learn; L.set({space: 2, z: [0.7, 0.4, 0], c: [-0.4, 0.3, 0]}); L.goto(0, 0.5);")
shot('2d-stretch-end', "const SL = window.squaringLab, L = SL.learn; L.goto(1, 1);")
shot('3d-lathe-turn', "const SL = window.squaringLab, L = SL.learn; L.set({space: 3, z: [0.6, 0.3, 0.4], c: [-0.3, 0.2, 0.1]}); window.__T.setAp('lathe'); L.goto(0, 0.5);")
shot('3d-lathe-flat-turn', "const SL = window.squaringLab, L = SL.learn; L.set({space: 3, z: [0.6, 0.5, 0], c: [-0.3, 0.2, 0.1]}); L.goto(0, 0.5);")
shot('3d-classic-lean', "const SL = window.squaringLab, L = SL.learn; L.set({space: 3, z: [0.6, 0.3, 0.4], c: [-0.3, 0.2, 0.1]}); window.__T.setAp('classic'); L.goto(1, 0.5);")
shot('3d-mercator-lean', "const SL = window.squaringLab, L = SL.learn; window.__T.setAp('mercator'); L.goto(1, 0.5);")
shot('3d-bulb-lean-end', "const SL = window.squaringLab, L = SL.learn; window.__T.setAp('bulb'); L.goto(1, 1);")
shot('3d-tilt-turn', "const SL = window.squaringLab, L = SL.learn; window.__T.setAp('tilt'); L.goto(0, 0.5);")
# the words on the page
acts.append({'js': "const SL = window.squaringLab, L = SL.learn, g = id => (document.getElementById(id) || {}).textContent; const o = {}; for (const sp of [1, 2, 3]) { L.set({space: sp}); L.state(); await new Promise(r => setTimeout(r, 300)); o[sp] = { notice: g('learnNotice'), hidden: g('learnHiddenNote'), note: g('learnNote') }; } return JSON.stringify(o);"})

path = os.path.join(HERE, 'actions-tab.json')
json.dump(acts, open(path, 'w', encoding='utf-8'))
cmd = [sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', os.path.join(ROOT, 'dist', 'r13-check-truth.html'), '--actions', path, '--size', '1400x950']
p = subprocess.run(cmd, cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8'), capture_output=True, text=True, encoding='utf-8')
out = []
for line in p.stdout.splitlines():
    m = re.match(r'step (\d+) result: (.*)$', line)
    if not m:
        out.append(line); continue
    try:
        val = json.loads(m.group(2))
        if isinstance(val, str) and val[:1] in '[{':
            val = json.loads(val)
    except Exception:
        val = m.group(2)
    out.append('--- step %s' % m.group(1))
    out.append(val if isinstance(val, str) else json.dumps(val, ensure_ascii=False, indent=1))
text = '\n'.join(out) + '\nexit %d\n' % p.returncode + ('stderr: ' + p.stderr[-3000:] if p.stderr.strip() else '')
open(os.path.join(HERE, 'tab.txt'), 'w', encoding='utf-8').write(text)
print('exit', p.returncode, 'lines', len(out))
