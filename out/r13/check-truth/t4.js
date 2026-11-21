// Round 13, truth checker: on a line, how fast does the rounding left in the hidden direction grow from step to step?
(() => {
  const SL = window.squaringLab, learnPlan = SL.learnPlan;
  window.__G = () => {
    const out = [];
    for (const [z0, c] of [[0, -2], [0, -1.8], [-1.2, -0.6], [0.5, -1.9], [0, -1.5], [0, -1]]) {
      const p = learnPlan({ space: 1, id: 'lathe', n: 2, c: [c, 0, 0] });
      let q = [z0, 0, 0], x = z0, firstMinus = null, visible = null, away = null, sideFlips = 0, lastSide = 0, negSteps = 0;
      for (let k = 1; k <= 400; k++) {
        if (q[0] < 0 && Math.abs(q[1]) < 1e-6 * Math.abs(q[0])) { negSteps++; const s = p.moves[0].say(q); if (/−360°/.test(s) && firstMinus === null) firstMinus = k; const side = Math.sign(p.moves[0].at(q, 0.5)[1]); if (lastSide && side !== lastSide) sideFlips++; lastSide = side; }
        for (const m of p.moves) q = m.at(q, 1);
        x = x * x + c;
        if (visible === null && Math.abs(q[1]) > 0.01) visible = { step: k, point: q.slice(), trueX: x };
        if (Math.hypot(q[0], q[1]) > 8) { away = { step: k, trueX: x }; break; }
      }
      out.push({ z0, c, firstStepWhoseSentenceSaysMinus360: firstMinus, stepsFromANegativeNumber: negSteps, timesTheSwingChangedSides: sideFlips, hiddenPartOver001: visible, ranAway: away });
    }
    return out;
  };
})();
