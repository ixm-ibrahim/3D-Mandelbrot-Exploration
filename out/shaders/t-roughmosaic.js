//#
// Rough mode in the mosaic: which rule cuts the sets into slabs? Count the pixels that are not background.
window.bandRows = 120;
const L = window.squaringLab, G = L.GLSL(), gl = L.gl();
const sub = (s, a, b) => { if (!s.includes(a)) throw new Error('missing: ' + a); return s.split(a).join(b); };
L.S.mosaic = true; L.cam.dist = 3;
const sets = {
  now: G,
  'no longer strides': { ...G, GL_TAIL: sub(G.GL_TAIL, 'if (ahead < 1e8) stride = clamp(', 'if (false) stride = clamp(') },
  'no ahead hits': { ...G, GL_TAIL: sub(G.GL_TAIL, '} else if (d < tol || ahead < e) conv = true;', '} else if (d < tol) conv = true;') },
  'neither': { ...G, GL_TAIL: sub(sub(G.GL_TAIL, 'if (ahead < 1e8) stride = clamp(', 'if (false) stride = clamp('), '} else if (d < tol || ahead < e) conv = true;', '} else if (d < tol) conv = true;') },
};
const lit = (P, o) => {
  const prog = window.progOf(P); window.drawOnce(prog, o); window.drawOnce(prog, o);
  const W = gl.canvas.width, H = gl.canvas.height, px = new Uint8Array(W * H * 4);
  gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, px);
  let n = 0; for (let i = 0; i < px.length; i += 4) if (Math.abs(px[i] - px[0]) + Math.abs(px[i + 1] - px[1]) + Math.abs(px[i + 2] - px[2]) > 12) n++;
  return (100 * n / (W * H)).toFixed(1) + '%';
};
const out = ['one neighbour: ' + lit(G, { nt: 1, analytic: false })];
for (const k in sets) out.push(k + ': ' + lit(sets[k], { nt: 0, analytic: false }));
return out;
