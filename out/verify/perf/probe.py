from lib import *
d, proc, prof = launch()
try:
    d.load()
    print(d.js('return [!!document.getElementById("m-mosaic"), !!document.getElementById("col-trap"), !!document.getElementById("powNum"), !!document.getElementById("flat"), [...document.querySelectorAll("[id$=Play]")].map(e => e.id), window.squaringLab.R.par ? 1 : 0, window.squaringLab.R.tq ? 1 : 0, document.getElementById("view").width, document.getElementById("view").height, window.squaringLab.R.ps, window.squaringLab.R.dt];'))
    print(d.js('const g = document.getElementById("view").getContext("webgl2"); const e = g.getExtension("WEBGL_debug_renderer_info"); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : "?";'))
    print(d.box("#view"), d.box("#stage"))
    print(d.p.problems)
finally:
    close(d, proc, prof)
