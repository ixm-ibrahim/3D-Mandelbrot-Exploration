// A FAKE of learnShape3d, for testing builder "core"'s calling code only (round 26). It is never part of src/.
// It keeps to the contract of docs/ROUND26.md section 4: make() -> { canvas, draw(o), slice(), dispose() }, out(),
// ok(), note(). Its "picture" is a flat stand-in: per pane, one disc per skin (smaller for a later step), with the
// opacity and the tint it was asked for. Every call of draw(o) is kept in window.__fake3d.calls so a test can read
// what the page asked for. It has no proj(), so the page's own camera arithmetic is what places the diamond.
const learnShape3d = (() => {
  const log = (window.__fake3d = { calls: [], made: 0, fail: false });
  const hex = c => 'rgb(' + c.map(x => Math.round(Math.max(0, Math.min(1, x)) * 255)).join(',') + ')';
  function make() {
    if (log.noGl) return null;
    log.made++;
    const canvas = document.createElement('canvas');
    function draw(o) {
      const t0 = performance.now();
      log.calls.push(JSON.parse(JSON.stringify(o)));
      if (log.calls.length > 400) log.calls.splice(0, 200);
      if (log.fail) return { ok: false, ms: 0, note: 'The fake was told to fail.' };
      const w = canvas.clientWidth, h = canvas.clientHeight;
      if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
      const g = canvas.getContext('2d'), C = o.colours;
      g.fillStyle = hex(C.bg); g.fillRect(0, 0, w, h);
      for (const P of o.panes) {
        const [x, y, pw, ph] = P.rect, R = 0.4 * Math.min(pw, ph) * o.zoom;
        g.save(); g.beginPath(); g.rect(x, y, pw, ph); g.clip();
        for (const L of o.levels.slice().sort((a, b) => a.k - b.k)) {
          const col = C.body.map((b, i) => b + (C.warn[i] - b) * (L.tint || 0));
          g.globalAlpha = 0.6 * L.alpha; g.fillStyle = hex(col);
          g.beginPath(); g.arc(x + pw / 2, y + ph / 2, R * (1 - L.k / 24) * (P.kind === 'j' ? 0.9 : 1), 0, 2 * Math.PI); g.fill();
          g.globalAlpha = Math.min(1, 0.4 + L.alpha); g.strokeStyle = hex(col); g.lineWidth = 1.5; g.stroke();
        }
        g.globalAlpha = 1; g.fillStyle = hex(C.ink); g.font = '12px monospace';
        g.fillText('FAKE 3D ' + P.kind + ' ' + o.quality + ' yaw ' + o.yaw.toFixed(2) + ' pitch ' + o.pitch.toFixed(2) + ' levels ' + o.levels.map(l => l.k + ':' + l.alpha.toFixed(2) + ':' + (l.tint || 0).toFixed(2)).join(' '), x + 10, y + ph - 40);
        g.restore();
      }
      return { ok: true, ms: performance.now() - t0, note: '' };
    }
    return { canvas, draw, slice: () => null, dispose() { if (canvas.parentNode) canvas.parentNode.removeChild(canvas); } };
  }
  // the JavaScript twin: for the fake, the flat rule in the flat plane and "thrown out at once" off it
  function out(p, kind, c, maxK) {
    if (Math.abs(p[2]) > 1e-12) return 0;
    return window.squaringLab.learn.shape.out2([p[0], p[1]], kind, c, maxK);
  }
  return { make, out, ok: () => !log.fail, note: () => (log.fail ? 'The fake was told to fail.' : '') };
})();
