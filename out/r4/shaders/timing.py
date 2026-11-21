"""Compile time and drawing time, old against new, pages run back to back. Least of 3 each."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab
T = r"""
const draw = async () => { const t0 = performance.now(); L.touch(); await new Promise(r => { const f = () => L.idle() ? r() : setTimeout(f, 3); setTimeout(f, 40); }); return performance.now() - t0; };
const least = async n => { let m = 1e9; for (let i = 0; i < n; i++) m = Math.min(m, await draw()); return Math.round(m); };
const compile = () => { let m = 1e9; for (let i = 0; i < 3; i++){ const c = document.createElement('canvas'), g = c.getContext('webgl2'); const src = L.R.want.src() + '\n// ' + Math.random() + '\nconst float uniq' + Math.floor(Math.random() * 1e9) + ' = ' + Math.random().toFixed(6) + ';\n';
  const vs = g.createShader(g.VERTEX_SHADER), fs = g.createShader(g.FRAGMENT_SHADER), p = g.createProgram();
  g.shaderSource(vs, '#version 300 es\nvoid main(){ vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2)); gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0); }'); g.shaderSource(fs, src);
  const t0 = performance.now(); g.compileShader(vs); g.compileShader(fs); g.attachShader(p, vs); g.attachShader(p, fs); g.linkProgram(p);
  const ok = g.getProgramParameter(p, g.LINK_STATUS); const dt = performance.now() - t0; if (!ok) return 'FAILED ' + g.getShaderInfoLog(fs); m = Math.min(m, dt); const x = g.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); }
  return Math.round(m); };
"""
def steps(tag):
    S = lambda name, js: {'js': lab.PRE + T + js, 'wait': 'done', 'timeout': 600}
    return [
      S('warm', "$('qBal').click(); L.S.q.aa = 4; go(); return 'warm';"),
      S('m', "return 'TIME %s mandel-bal ' + await least(3) + ' compile ' + compile();" % tag),
      S('r0', "scene('rabbit'); $('qBal').click(); L.S.q.aa = 4; go(); return 'set';"),
      S('r', "return 'TIME %s rabbit-close-bal ' + await least(3);" % tag),
      S('u0', "scene('mandelfar'); $('qUltra').click(); go(); return 'set';"),
      S('u', "return 'TIME %s mandel-ultra ' + await least(5);" % tag),
      S('k0', "$('mode-k').click(); $('qBal').click(); L.S.q.aa = 4; go(); return 'set';"),
      S('k', "return 'TIME %s klein-bal ' + await least(3) + ' compile ' + compile();" % tag),
    ]
rows = []
for rnd in range(2):
    for tag, page in (('old', 'r4-shaders-base'), ('new', sys.argv[1] if len(sys.argv) > 1 else 'r4-shaders')):
        code, log = lab.shot('dist/%s.html' % page, steps(tag), 'timing-%s-%d' % (tag, rnd))
        for l in log.splitlines():
            if 'TIME' in l: print(rnd, l.strip()); rows.append(l)
        if code: print('exit', code, log[-400:])
