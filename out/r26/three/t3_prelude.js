// Test helper for out/r26/three: put one learnShape3d view on top of the page in a box of a known size.
// Loaded into the page by t3_run.py as the first action of every run. Not part of the lab.
window.T3 = (() => {
  const L = window.squaringLab, M = L.learnShape3d;
  const box = document.createElement('div');
  box.id = 't3box';
  box.style.cssText = 'position:fixed;left:0;top:0;width:600px;height:450px;z-index:99999;overflow:hidden';
  document.body.appendChild(box);
  const view = M.make();
  if (view) { view.canvas.style.cssText = 'width:100%;height:100%;display:block'; box.appendChild(view.canvas); }
  const hex = h => { h = h.trim(); if (h.length === 4) h = '#' + h[1] + h[1] + h[2] + h[2] + h[3] + h[3]; const v = parseInt(h.slice(1), 16); return [(v >> 16 & 255) / 255, (v >> 8 & 255) / 255, (v & 255) / 255]; };
  const cols = warnKey => { const cs = getComputedStyle(document.documentElement), g = k => hex(cs.getPropertyValue(k)); const c = { bg: g('--stage'), body: g('--brass'), warn: g(warnKey || '--bad'), ink: g('--ink') }; box.style.background = cs.getPropertyValue('--stage'); return c; };
  const setAp = (id, params) => { const i = L.APPROACHES.findIndex(a => a.id === id); if (i < 0) throw new Error('no approach ' + id); L.S.approach = i; if (params) Object.assign(L.S.param[id], params); return i; };
  const size = (w, h) => { box.style.width = w + 'px'; box.style.height = h + 'px'; };
  const VIEW = { yaw: -0.62, pitch: 0.4, zoom: 1 };
  // one pane filling the box
  const one = (kind, c, levels, extra) => Object.assign({ panes: [{ kind, rect: [0, 0, box.clientWidth, box.clientHeight] }], c: c || [0, 0, 0], levels, quality: 'still', colours: cols() }, VIEW, extra || {});
  // the levels the page would ask for at the slider position pos (whole or between two steps)
  // (the same numbers as learnShapeLevels in 67-learn-shape.js as it stood on 19 Nov, 23:42: solid 1, ghost 0.22,
  // the ghost pushed 0.55 of the way to the ink colour, the skin of shape k tinted while the bite is taken)
  const ease = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  const levelsAt = pos => {
    const k = Math.floor(pos + 1e-9), u = pos - k, solid = 1, ghost = 0.22, grey = 0.55, out = [];
    if (u < 1e-9) { out.push({ k, alpha: solid, tint: 0 }); if (k > 0) out.push({ k: k - 1, alpha: ghost, tint: 0, ghost: grey }); }
    else {
      out.push({ k: k + 1, alpha: solid * ease(0.1, 0.9, u), tint: 0 });
      out.push({ k, alpha: solid + (ghost - solid) * ease(0.3, 1, u), tint: ease(0, 0.25, u) * (1 - ease(0.6, 1, u)), ghost: grey * ease(0.6, 1, u) });
      if (k > 0) out.push({ k: k - 1, alpha: ghost * (1 - ease(0, 0.6, u)), tint: 0, ghost: grey });
    }
    return out.filter(l => l.alpha > 0.004);
  };
  return { L, M, view, box, cols, setAp, size, one, levelsAt, VIEW };
})();
