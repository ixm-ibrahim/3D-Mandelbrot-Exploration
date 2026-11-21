"""Which construct costs the compile time? One page, one Chrome: the scene program's source is taken from the page,
pieces of it are replaced by text, and each variant is compiled fresh (least of N).

  python out/r5/speed/cost.py <page> <m|k> [runs] [variant ...]

A variant is a list of "old => new" replacements on the full source (see VARIANTS). The page is not changed.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

CUT = ("col = cutFaceColour(vec3(p.xy, uCut), mix(uCutCol, uCutInk, 0.55 * smoothstep(0.36, 0.42, s)));",
       "col = mix(uCutCol, uCutInk, 0.55 * smoothstep(0.36, 0.42, s));")
FLAT = ("col = flatColour(slicePoint, d, uFlatH / uRes.y);", "col = vec3(d);")
SURF = ("vec3 alb = surfaceColour(p, nor, t);", "vec3 alb = vec3(0.5);")
INFLAT = ("return e > 0.0 ? outer : colInside(p, -d);", "return outer;")
PAL = ("vec3 pal(float t){", "vec3 pal(float t){ return vec3(fract(t)); }\nvec3 palOld(float t){")
SOLIDCOL = ("if (uTrapSolid < 0.5){\n    t = uTrapBy == 1", "{\n    t = uTrapBy == 1")
TS0 = ("TRAP_SOLIDS = true", "TRAP_SOLIDS = false")
TADD = ("void trapAdd(vec3 v, float it){", "void trapAdd(vec3 v, float it){ return; }\nvoid trapAddOld(vec3 v, float it){")
TONES = ("for (int i = 0; i < 4; i++) tone[i] = pal(0.25 * float(i));", "for (int i = 0; i < 4; i++) tone[i] = vec3(0.25 * float(i));")
KSOLID = ("bool trapSolid = uTrapSolid > 0.5;", "bool trapSolid = false;")
VARIANTS = {
    'full': [],
    'no-cut': [CUT],
    'no-flat': [FLAT],
    'no-surf': [SURF],
    'no-hooks': [CUT, FLAT, SURF],
    'no-inside-in-flat': [INFLAT],
    'pal-trivial': [PAL],
    'no-solid-colour': [SOLIDCOL],
    'no-tones-pal': [TONES],
    'ts0': [TS0],
    'ksolid0': [KSOLID],
    'trapadd-off': [TADD],
    'no-hooks+trapadd-off': [CUT, FLAT, SURF, TADD],
    'only-surf': [CUT, FLAT],
    'only-flat': [CUT, SURF],
    'only-cut': [FLAT, SURF],
}
JS = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
if (L.R) L.R.warmOn = false;
const compileSrc = (src0, runs) => { let m = 1e9; for (let i = 0; i < runs; i++){ const c = document.createElement('canvas'), g = c.getContext('webgl2'); const src = src0 + '\n// ' + Math.random() + '\nconst float uniq' + Math.floor(Math.random() * 1e9) + ' = ' + Math.random().toFixed(6) + ';\n';
  const vs = g.createShader(g.VERTEX_SHADER), fs = g.createShader(g.FRAGMENT_SHADER), p = g.createProgram();
  g.shaderSource(vs, '#version 300 es\nvoid main(){ vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2)); gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0); }'); g.shaderSource(fs, src);
  const t0 = performance.now(); g.compileShader(vs); g.compileShader(fs); g.attachShader(p, vs); g.attachShader(p, fs); g.linkProgram(p);
  const ok = g.getProgramParameter(p, g.LINK_STATUS); const dt = performance.now() - t0; if (!ok) return 'FAILED ' + (g.getShaderInfoLog(fs) || g.getProgramInfoLog(p)).slice(0, 300); m = Math.min(m, dt); const x = g.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); }
  return Math.round(m); };
"""


def main():
    page, kind = sys.argv[1], sys.argv[2]
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    names = sys.argv[4:] or list(VARIANTS)
    steps = [{'js': JS + ("$('mode-k').click(); " if kind == 'k' else '') + "L.syncControls(); L.refresh(false); return 'warm';", 'wait': 'done', 'timeout': 900}]
    for n in names:
        reps = json.dumps(VARIANTS[n])
        steps.append({'js': JS + "let s = L.R.want.src(); for (const [a, b] of %s){ if (!s.includes(a)) return '%s MISSING ' + a.slice(0, 40); s = s.split(a).join(b); } return 'COST %s ' + compileSrc(s, %d) + ' ms';" % (reps, n, n, runs), 'timeout': 900})
    path = os.path.join(HERE, 'cost-steps.json')
    json.dump(steps, open(path, 'w', encoding='utf-8'), indent=1)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--size', '1000x700', '--actions', path],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3600)
    out = (r.stdout or '') + (r.stderr or '')
    for l in out.splitlines():
        if 'COST' in l or 'MISSING' in l or 'FAILED' in l or 'PROBLEMS' in l or 'console.' in l:
            print(page, kind, l.split('result:')[-1].strip())
    print('exit', r.returncode)


if __name__ == '__main__':
    main()
