"""A first look: the approaches and their dials, what the handle offers, how long the page takes to answer."""
import json, time
from clab import Lab, Log

log = Log("t0_probe")
t0 = time.time()
with Lab("r26-checka") as lab:
    log("page up after %.1f s" % (time.time() - t0))
    log(json.dumps(lab.js("return LAB.APPROACHES.map(a => [a.id, a.name, (a.params || []).filter(s => s.key !== undefined).map(s => s.key + '=' + s.def + ' [' + s.min + ',' + s.max + ']').join(' '), !!LAB.MATH[a.id], !!(LAB.CARRY && LAB.CARRY[a.id])]);"), ensure_ascii=False, indent=0))
    log(json.dumps(lab.js("return { keys: Object.keys(L.shape), s: [S.n, S.abs, S.flip, S.approach, S.eq, S.z0, S.iter, S.mode], tokens: ['--stage','--panel','--ink','--ink-2','--line','--brass','--ok','--bad','--warn'].map(k => k + ' ' + getComputedStyle(document.documentElement).getPropertyValue(k).trim()) };")))
    t = time.time()
    st = lab.js("const s = await shapeOn({ kind: 'm', space: 2, pos: 3 }); return s;")
    log("shape on after %.1f s" % (time.time() - t))
    log(json.dumps(st))
    log(json.dumps(lab.js("return L.state();")))
    lab.shot("out/r26/checka/t0-m3.png")
    t = time.time()
    st = lab.js("const s = L.shape.set({ space: 3 }); await sleep(600); return L.shape.state();")
    log("3D after %.1f s" % (time.time() - t))
    log(json.dumps(st))
    lab.shot("out/r26/checka/t0-m3-3d.png")
    log.problems(lab)
