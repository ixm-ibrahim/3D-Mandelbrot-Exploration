    } else if (L.show === 'grid') {
      // (round 29) A grid of points: each dot in the colour of the place it started from, a handful larger, with a
      // ring where this step found them. The big circle they were laid out over (in space the big ball's outline) is
      // drawn too. A dot that has gone out of the picture is not drawn; the frame does not grow to hold it.
      const dark = learnVDark();
      if (!K.gridCol || K.gridDark !== dark) { K.gridDark = dark; K.gridCol = K.gridStart.map(v => learnVDotColour(v, sp, dark)); }
      if (vk === 'f2' || vk === 'h2') { trace(circle(ex, ey, 2), true); stroke(C.ink2, 1.25, 0.6, [4, 4]); }
      else if (vk === 's3') { g.beginPath(); g.arc(P.o[0], P.o[1], 2 * P.s, 0, 2 * PI); stroke(C.ink2, 1.25, 0.5, [4, 4]); }
      const qs = now.map(v => P.to(v)), seen = q => isFinite(q[0]) && isFinite(q[1]) && q[0] > -10 && q[0] < w + 10 && q[1] > -10 && q[1] < h + 10;
      const order = now.map((v, i) => i);
      if (P.cam) order.sort((a, b) => qs[a][2] - qs[b][2]);      // the far ones first
      const r0 = vk === 'f1' ? 2.4 : sp === 3 ? 2.3 : small ? 2.2 : 2.8;
      for (const i of order) {
        const q = qs[i];
        if (K.follow.includes(i) || !seen(q)) continue;
        g.beginPath(); g.arc(q[0], q[1] + lift, r0 + 0.9, 0, 2 * PI); fill(C.stage, 0.9);
        g.beginPath(); g.arc(q[0], q[1] + lift, r0, 0, 2 * PI); fill(K.gridCol[i], P.cam && sp === 3 ? 0.6 + 0.4 * clamp((q[2] + 2) / 4, 0, 1) : 1);
      }
      K.follow.forEach(i => {
        const q = qs[i], q0 = P.to(K.comp[0][i]);
        if (seen(q0)) { g.beginPath(); g.arc(q0[0], q0[1] + lift, 6.5, 0, 2 * PI); stroke(K.gridCol[i], 1.5, 0.85); }
        if (!seen(q)) return;
        g.beginPath(); g.arc(q[0], q[1] + lift, 7.6, 0, 2 * PI); fill(C.stage);
        g.beginPath(); g.arc(q[0], q[1] + lift, 6.4, 0, 2 * PI); stroke(C.ink, 1.4, 1);
        g.beginPath(); g.arc(q[0], q[1] + lift, 4.9, 0, 2 * PI); fill(K.gridCol[i]);
      });
