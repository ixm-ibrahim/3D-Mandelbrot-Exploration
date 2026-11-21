"""Generate a tools/shot.py action list that tests "Reset this section" for the given sections and context.
usage: python gen.py out.json context shots(0/1) section[,section...]
context: base | flat | fly | play
"""
import json, sys

HELP = r"""
const L = window.squaringLab, S = L.S;
window.__snap = () => {
  const o = {};
  document.querySelectorAll('aside.dials input, aside.dials select, #stage input').forEach(e => {
    const k = e.id || (e.name + '=' + e.value);
    if (e.type === 'radio' || e.type === 'checkbox') o['ctl:' + k] = e.checked;
    else if (e.tagName === 'SELECT') o['ctl:' + k] = e.selectedIndex + ':' + (e.selectedOptions[0] ? e.selectedOptions[0].textContent : '(blank)');
    else if (e.type === 'range') o['rng:' + k] = e.value;
    else o['ctl:' + k] = e.value;
  });
  document.querySelectorAll('aside.dials .dial, aside.dials .check-block, aside.dials .field-block, aside.dials label.check, aside.dials .field, aside.dials p.note[id]').forEach(e => {
    const c = e.querySelector('input,select'); const k = e.id || (c && c.id);
    if (k) o['hid:' + k + '/' + e.className.split(' ')[0]] = e.hidden;
  });
  document.querySelectorAll('.dial-play').forEach(b => { o['play:' + b.id] = b.getAttribute('aria-pressed'); });
  document.querySelectorAll('.dial-mode').forEach(b => { o['stepmode:' + b.id] = b.getAttribute('aria-pressed'); });
  for (const id of ['kleinNote', 'juliaNote', 'eqNote', 'eqErr', 'juliaSaveNote']) { const e = document.getElementById(id); o['txt:' + id] = e ? (e.hidden ? '[hidden]' : e.textContent) : null; }
  document.querySelectorAll('#sections > details').forEach(d => { o['sec:' + d.id] = (d.open ? 'open' : 'closed') + (d.hidden ? '/hidden' : ''); });
  o['camBtns'] = ['camArc', 'camFly'].map(id => { const b = document.getElementById(id); return b ? (b.getAttribute('aria-pressed') + '/' + b.className) : 'none'; }).join(' ');
  o['hint'] = document.querySelector('.hint').textContent;
  o['collapseAll'] = document.getElementById('collapseAll').textContent;
  o['rulesOn'] = [...document.querySelectorAll('.rule')].map(r => r.classList.contains('is-on') ? 1 : 0).join('');
  o['juliaOn'] = [...document.querySelectorAll('#juliaList .plist-row.is-on')].map(r => r.firstChild.textContent).join('|');
  const flat = (p, v) => { if (v && typeof v === 'object' && !Array.isArray(v)) { for (const k in v) flat(p + '.' + k, v[k]); } else if (typeof v !== 'function') o[p] = Array.isArray(v) ? JSON.stringify(v) : v; };
  flat('S', S); flat('cam', L.cam);
  const b = L.basis(); o['basis.pos'] = JSON.stringify(b.pos.map(x => +x.toFixed(5))); o['basis.f'] = JSON.stringify(b.f.map(x => +x.toFixed(5)));
  return o;
};
window.__diff = (a, b) => { const d = {}; for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) if (a[k] !== b[k]) d[k] = [a[k], b[k]]; return d; };
window.__vis = e => e.getClientRects().length > 0;
window.__fire = (e, t) => e.dispatchEvent(new Event(t, { bubbles: true }));
window.__simple = (root, done, log) => {
  root.querySelectorAll('.dial').forEach(d => {
    const num = d.querySelector('.num'), r = d.querySelector('input[type=range]');
    if (!__vis(d) || done.has(num.id)) return;
    const cur = parseFloat(num.value);
    const lo = r ? +r.min : cur - 1, hi = r ? +r.max : cur + 1, st = r ? +r.step : 0.01;
    let v = +(Math.round((lo + (hi - lo) * 0.73) / st) * st).toFixed(6);
    if (Math.abs(v - cur) < st * 1.5) v = +(Math.round((lo + (hi - lo) * 0.29) / st) * st).toFixed(6);
    num.focus(); num.value = String(v);
    num.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true }));
    num.blur();
    done.add(num.id); log.push(num.id + ':' + cur + '>' + num.value);
  });
  root.querySelectorAll('input[type=checkbox]').forEach(c => {
    if (!__vis(c.closest('label') || c) || done.has(c.id)) return;
    c.click(); done.add(c.id); log.push(c.id + '>' + c.checked);
  });
};
window.__changeAll = (root, noSelects) => {
  const done = new Set(), log = [], tried = new Set(), start = new Map();
  root.querySelectorAll('select').forEach(s => start.set(s, s.selectedIndex));
  const fix = () => {
    for (let it = 0; it < 200; it++) {
      let before; do { before = done.size; __simple(root, done, log); } while (done.size > before);
      if (noSelects) return;
      const sels = [...root.querySelectorAll('select')].filter(__vis).reverse();
      let moved = false;
      for (const s of sels) {
        const n = s.options.length;
        for (let k = 1; k < n && !moved; k++) {
          const i = (Math.max(start.get(s), 0) + k) % n, key = s.id + '#' + i;
          if (tried.has(key)) continue;
          tried.add(key); s.selectedIndex = i; __fire(s, 'change'); moved = true;
        }
        if (moved) break;
      }
      if (!moved) return;
    }
  };
  const radios = [...root.querySelectorAll('input[type=radio]')];
  if (radios.length) radios.forEach(r => { r.click(); log.push('radio ' + r.id); fix(); }); else fix();
  if (!noSelects) root.querySelectorAll('select').forEach(s => { if (s.selectedIndex === start.get(s)) { s.selectedIndex = (Math.max(s.selectedIndex, 0) + 1) % s.options.length; __fire(s, 'change'); } log.push(s.id + ' sel>' + s.selectedIndex); });
  const texts = { eq: 'z^n + c + 0.1', z0: 'c', juliaName: 'tester' };
  root.querySelectorAll('input[type=text]:not(.num)').forEach(t => { if (texts[t.id]) { t.focus(); t.value = texts[t.id]; __fire(t, 'input'); __fire(t, 'change'); t.blur(); log.push(t.id + ' text'); } });
  if (root.id === 'secCut' && !S.cutOn) { document.getElementById('cutOn').click(); log.push('cutOn back on'); }
  return log;
};
"""

SECT = {
    'mandel': ('m', '#mandelPanel'), 'julia': ('j', '#juliaPanel'), 'klein': ('k', '#kleinPanel'),
    'approach': ('m', '#secApproach'), 'eq': ('m', '#secEq'), 'mod': ('m', '#secMod'), 'cut': ('m', '#secCut'),
    'colour': ('m', '#secColour'), 'view': ('m', '#secView'), 'q': ('m', '#secQuality'),
}
CTX = {
    'base': '',
    'flat': "document.getElementById('flat').click();",
    'fly': "document.getElementById('camFly').click();",
    'play': "document.getElementById('ap-mercator').click(); document.getElementById('par-mercator-turnPlay').click();",
}
PERTURB = "L.cam.yaw += 0.37; L.cam.pitch -= 0.2; L.cam.dist *= 0.8; S.v2.x += 0.21; S.v2.h *= 0.8; L.viewChanged(); L.touch();"


def steps(sec, ctx, shots, mode=None, tag=None):
    m, root = SECT[sec]
    m = mode or m
    tag = tag or ('%s-%s' % (sec, ctx) + ('' if mode is None else '-' + mode))
    out = []
    out.append({"js": "location.reload(); return null;", "sleep": 1.5})
    out.append({"wait": "document.readyState === 'complete' && window.squaringLab && window.squaringLab.S", "timeout": 60})
    out.append({"js": HELP + ("document.getElementById('mode-%s').click();" % m if m != 'm' else '') + CTX[ctx] +
                "document.querySelector('%s').open = true; return null;" % root, "sleep": 0.6})
    if shots:
        out.append({"wait": "done", "timeout": 300, "shot": "out/verify/p8a/%s-0fresh.png" % tag, "clip": "#stage"})
    out.append({"js": "const L = window.squaringLab, S = L.S; window.__A = __snap(); " + PERTURB +
                " const log = __changeAll(document.querySelector('%s')); return '%s CHANGES: ' + log.join('  ');" % (root, tag), "sleep": 0.8})
    out.append({"js": "window.__B = __snap(); const d = __diff(__A, __B); return '%s CHANGED KEYS (' + Object.keys(d).length + '): ' + Object.keys(d).join(' ');" % tag})
    if shots:
        out.append({"wait": "done", "timeout": 300, "shot": "out/verify/p8a/%s-1changed.png" % tag, "clip": "#stage"})
        out.append({"js": "window.__B = __snap(); return null;"})
    out.append({"js": "document.querySelector('%s .dial-reset').click(); return null;" % root, "sleep": 0.8})
    out.append({"js": "window.__C = __snap(); return { tag: '%s', notRestoredToFresh_A_vs_C: __diff(__A, __C), resetChanged_B_vs_C: Object.keys(__diff(__B, __C)).join(' ') };" % tag})
    if shots:
        out.append({"wait": "done", "timeout": 300, "shot": "out/verify/p8a/%s-2reset.png" % tag, "clip": "#stage"})
        out.append({"js": "window.squaringLab.touch(); return null;", "sleep": 0.5})
        out.append({"wait": "done", "timeout": 300, "shot": "out/verify/p8a/%s-3redrawn.png" % tag, "clip": "#stage"})
    return out


if __name__ == '__main__':
    path, ctx, shots, secs = sys.argv[1], sys.argv[2], sys.argv[3] == '1', sys.argv[4].split(',')
    mode = sys.argv[5] if len(sys.argv) > 5 else None
    acts = []
    for s in secs:
        acts += steps(s, ctx, shots, mode)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(acts, f, indent=1)
    print(len(acts), 'steps')
