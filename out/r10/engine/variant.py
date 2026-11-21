"""Test copies of 30-shaders.js with one change to the shadow ray each, built as pages dist/r10-eng-<tag>.html.
  python out/r10/engine/variant.py <tag> [<tag> ...]      (tags: see VAR)"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SH_Q = "else if (phase == PH_SHADOW){ q = p + nor * 2.0 * e + L * ts; qn = min(nt, 1); dir = L; }"
SH_S = "if (res >= 0.005 && ts <= 5.0 && n < uShSteps){ ts += empty ? leave : min(clamp(d, 2.0 * e, 0.35), leave); continue; }"
SH_0 = "n = 0; ts = 4.0 * e;"
VAR = {
    't1': [(SH_S, SH_S.replace("clamp(d, 2.0 * e, 0.35)", "clamp(d, 2.0 * e, min(0.35, 0.5 * ts))"))],
    't2': [(SH_Q, SH_Q.replace("nor * 2.0 * e", "nor * 4.0 * e")), (SH_0, "n = 0; ts = 8.0 * e;")],
    't3': [(SH_Q, SH_Q.replace("qn = min(nt, 1);", "qn = nt;"))],
    't4': [(SH_Q, SH_Q.replace("nor * 2.0 * e", "nor * 4.0 * e"))],
    't5': [(SH_0, "n = 0; ts = 12.0 * e;")],
    't6': [(SH_S, SH_S.replace("clamp(d, 2.0 * e, 0.35)", "clamp(d, 2.0 * e, min(0.35, 0.5 * ts))")), (SH_Q, SH_Q.replace("qn = min(nt, 1);", "qn = nt;"))],
}
src = open(os.path.join(ROOT, 'src', 'js', '30-shaders.js'), encoding='utf-8').read()
for tag in sys.argv[1:]:
    s = src
    for a, b in VAR[tag]:
        assert s.count(a) == 1, (tag, a, s.count(a)); s = s.replace(a, b)
    p = os.path.join(HERE, 'var', '30-%s.js' % tag)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    r = subprocess.run([sys.executable, 'build.py', '--name', 'r10-eng-' + tag, '--base', 'base10a', '--use', 'src/js/25-colour.js', 'src/js/40-render.js',
                        '--swap', 'js/30-shaders.js=out/r10/engine/var/30-%s.js' % tag], cwd=ROOT, capture_output=True, text=True)
    print(tag, r.stdout.strip(), r.stderr.strip()[:300])
