# Writes out/render/40-render-dbg.js: the live renderer plus instrumentation for timing tests.
#   R.log      every finished job: [kind, rows, wall ms, counted ms, exact, dt]
#   R.loopMax  the longest single run of loop(), and R.loopWhere what it was doing
s = open('src/js/40-render.js', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)


rep("    const job = R.pend, c = jobCost(job), ms = c.ms;\n",
    "    const dbgWall = performance.now() - R.pend.t0;\n"
    "    const job = R.pend, c = jobCost(job), ms = c.ms;\n"
    "    (R.log = R.log || []).push([job.kind, job.rows || 0, +dbgWall.toFixed(1), +c.ms.toFixed(2), c.exact ? 1 : 0, +R.dt.toFixed(1)]);\n")
rep("  fence({ kind: 'band', frac:", "  fence({ kind: 'band', rows, frac:")
rep("function loop(frame) {\n",
    "function loop(frame) {\n"
    "  const t = performance.now(); R.where = 'start'; loopIn(frame);\n"
    "  const d = performance.now() - t; if (d > (R.loopMax || 0)) { R.loopMax = d; R.loopWhere = R.where; }\n"
    "}\n"
    "function loopIn(frame) {\n")
rep("  const P = sceneAcquire();\n", "  R.where = 'acquire'; const P = sceneAcquire(); R.where = 'after acquire';\n")
rep("  if (R.wantPrev) { R.wantPrev = false; stageProgress(null); preview(P); return kick(); }\n",
    "  if (R.wantPrev) { R.wantPrev = false; stageProgress(null); R.where = 'preview'; preview(P); return kick(); }\n")
rep("  if (R.prog) { band(P); return kick(); }\n", "  if (R.prog) { R.where = 'band'; band(P); return kick(); }\n")
open('out/render/40-render-dbg.js', 'w', encoding='utf-8', newline='\n').write(s)
