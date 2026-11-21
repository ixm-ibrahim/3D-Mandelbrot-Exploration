"""Compile time and drawing time of whole pages, one after another, on whatever the GPU is doing right now.

  python out/me/perf.py <page> [<page> ...]      pages are names in dist/ without .html

For each page: the time to compile a fresh copy of the scene program (least of 3) and the time to draw the
finished picture (least of 5), for the opening Mandelbrot view, the Julia set for c = -1 and the opening Kleinian
view. Run it only while nothing else is using the GPU; it prints the clock so runs can be told apart.
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRE = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
if (L.R) L.R.warmOn = false;
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const draw = async () => { const t0 = performance.now(); L.touch(); await new Promise(r => { const f = () => L.idle() ? r() : setTimeout(f, 3); setTimeout(f, 40); }); return performance.now() - t0; };
const least = async n => { let m = 1e9; for (let i = 0; i < n; i++) m = Math.min(m, await draw()); return Math.round(m); };
const compile = () => { let m = 1e9; for (let i = 0; i < 3; i++){ const c = document.createElement('canvas'), g = c.getContext('webgl2'); const src = L.R.want.src() + '\n// ' + Math.random() + '\nconst float uniq' + Math.floor(Math.random() * 1e9) + ' = ' + Math.random().toFixed(6) + ';\n';
  const vs = g.createShader(g.VERTEX_SHADER), fs = g.createShader(g.FRAGMENT_SHADER), p = g.createProgram();
  g.shaderSource(vs, '#version 300 es\nvoid main(){ vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2)); gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0); }'); g.shaderSource(fs, src);
  const t0 = performance.now(); g.compileShader(vs); g.compileShader(fs); g.attachShader(p, vs); g.attachShader(p, fs); g.linkProgram(p);
  const ok = g.getProgramParameter(p, g.LINK_STATUS); const dt = performance.now() - t0; if (!ok) return 'FAILED ' + g.getShaderInfoLog(fs); m = Math.min(m, dt); const x = g.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); }
  return Math.round(m); };
"""
EXTRA = os.environ.get('PERF_JS', '')      # optional: state changes applied before each measurement

def steps():
    s = []
    def add(js, wait='done'):
        a = {'js': PRE + js, 'timeout': 900}
        if wait:
            a['wait'] = wait
        s.append(a)
    add(EXTRA + "go(); return 'warm m';")
    add("return 'M compile ' + compile() + ' ms, draw ' + await least(5) + ' ms, source ' + L.R.want.src().length + ' chars';", None)
    add("$('mode-j').click(); L.S.c = [-1, 0, 0]; " + EXTRA + "go(); return 'warm j';")
    add("return 'J draw ' + await least(5) + ' ms';", None)
    add("$('mode-k').click(); " + EXTRA + "go(); return 'warm k';")
    add("return 'K compile ' + compile() + ' ms, draw ' + await least(5) + ' ms, source ' + L.R.want.src().length + ' chars';", None)
    return s

for page in sys.argv[1:]:
    path = os.path.join(ROOT, 'out', 'me', 'perf-steps.json')
    json.dump(steps(), open(path, 'w', encoding='utf-8'), indent=1)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--size', '1100x760', '--actions', path],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=1800)
    out = (r.stdout or '') + (r.stderr or '')
    got = [l.split('result:')[1].strip().strip('"') for l in out.splitlines() if 'result:' in l and ('compile' in l or 'draw' in l)]
    print(time.strftime('%H:%M:%S'), page, '|', ' | '.join(got), '| exit', r.returncode)
    if r.returncode:
        print(out[-1500:])
