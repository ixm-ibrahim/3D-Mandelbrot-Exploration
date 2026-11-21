"""Build dist/fix-shaders-ab.html: the new shader file plus the old one under OLD_ names, with a switch and a
timer, so both can be timed back to back in one page.
  window.__sh(old)            use the old (true) or new (false) shaders from now on
  await window.__bench(n)     -> { old: ms, new: ms } least time of n full-size single passes each, alternating
usage: python out/fix/shaders/ab.py [old.js] [new.js]"""
import os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
old = open(os.path.join(ROOT, sys.argv[1] if len(sys.argv) > 1 else 'base2/js/30-shaders.js'), encoding='utf-8').read()
new = open(os.path.join(ROOT, sys.argv[2] if len(sys.argv) > 2 else 'src/js/30-shaders.js'), encoding='utf-8').read()
names = ['VERT', 'GL_HEAD', 'GL_ORBIT', 'GL_KLEIN', 'GL_TAIL', 'BLIT']
for n in names:
    old = re.sub(r'^const %s = ' % n, 'const OLD_%s = ' % n, old, flags=re.M)
for n in ['GL_HEAD', 'GL_ORBIT', 'GL_KLEIN', 'GL_TAIL']:
    new = re.sub(r'^const %s = ' % n, 'let %s = ' % n, new, flags=re.M)
extra = r"""
const NEW_SH = [GL_HEAD, GL_ORBIT, GL_KLEIN, GL_TAIL];
window.__sh = old => {
  [GL_HEAD, GL_ORBIT, GL_KLEIN, GL_TAIL] = old ? [OLD_GL_HEAD, OLD_GL_ORBIT, OLD_GL_KLEIN, OLD_GL_TAIL] : NEW_SH;
  progs.clear(); R.sig = ''; touch();
};
window.__bench = async (n, opts) => {
  const out = { old: 1e9, new: 1e9 }, px = new Float32Array(4);
  const once = async which => {
    window.__sh(which === 'old');
    let P; for (;;) { P = sceneAcquire(); if (typeof P !== 'string' || P !== 'wait') break; await new Promise(r => setTimeout(r, 50)); }
    if (typeof P === 'string') throw new Error('no program: ' + P);
    ensureTargets();
    const W = canvas.width, H = canvas.height;
    const o = Object.assign({ w: W, h: H, off: [0, 0], px: 1, nt: sceneDe(), steps: S.q.steps, normEps: S.q.smooth, ao: S.q.ao, shadow: S.q.shadow, sharp: S.q.normals === 'sharp' }, opts || {});
    for (let k = 0; k < 2; k++) {   // the first draw with a program can include driver work: time the second
      gl.bindFramebuffer(gl.FRAMEBUFFER, prev.fbo); gl.viewport(0, 0, W, H); gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
      setScene(P, o);
      gl.finish(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.FLOAT, px);
      const t0 = performance.now();
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.FLOAT, px);
      const ms = performance.now() - t0;
      if (k === 1) out[which] = Math.min(out[which], ms);
    }
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  };
  for (let i = 0; i < n; i++) { await once('old'); await once('new'); }
  window.__sh(false);
  return { old: +out.old.toFixed(1), new: +out.new.toFixed(1), ratio: +(out.new / out.old).toFixed(3) };
};
"""
path = os.path.join(ROOT, 'out', 'fix', 'shaders', 'ab-shaders.js')
open(path, 'w', encoding='utf-8').write(new + '\n' + old + '\n' + extra)
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'build.py'), '--name', 'fix-shaders-ab', '--base', 'base2', '--swap', 'js/30-shaders.js=out/fix/shaders/ab-shaders.js'], cwd=ROOT))
