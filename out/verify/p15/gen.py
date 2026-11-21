import json, os, subprocess, sys
ROOT = os.getcwd()
OUT = 'out/verify/p15'
APS = ['mercator', 'lathe', 'bulb', 'classic', 'split']
NS = ['-1', '-2', '-3', '-4', '-8', '-2.5', '0', '0.5', '1', '1.5']
HEAD = "const L = window.squaringLab, $ = id => document.getElementById(id); const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; "
def info(extra=''):
    return ("return JSON.stringify({n: L.S.n, ap: L.APPROACHES[L.S.approach].id, mode: L.S.mode, dist: L.cam.dist, target: L.cam.target, v2: L.S.v2, bound: L.S.view.bound, "
            "status: $('status').textContent, eqErr: $('eqErr').hidden ? '' : $('eqErr').textContent, glfail: !$('glfail').hidden" + extra + "});")
procs = []
for kind in ('2d', '3d'):
    for ap in APS:
        acts = []
        first = HEAD + "L.R.warmOn = false; "
        if kind == '2d':
            first += "L.S.q.aa = 2; L.syncControls(); $('flat').click(); "
        else:
            first += "$('qFast').click(); "
        first += "$('ap-%s').click(); return 'start %s %s';" % (ap, kind, ap)
        acts.append({"js": first, "wait": "done", "timeout": 400})
        for mode in ('m', 'j'):
            for n in NS:
                extra = ''
                if kind == '3d' and mode == 'm' and n in ('-2', '0', '0.5', '1', '-2.5'):
                    extra = ", card: $('card').innerText.slice(0, 2500), f: $('f-%s').textContent" % ap
                js = HEAD + "$('mode-%s').click(); type('powNum', '%s'); L.resetCam(); L.touch(); await new Promise(r => setTimeout(r, 150)); " % (mode, n) + info(extra)
                tag = n.replace('-', 'm').replace('.', 'p')
                acts.append({"js": js, "wait": "done", "timeout": 400, "shot": "%s/%s-%s-%s-n%s.png" % (OUT, kind, ap, mode, tag), "clip": "#stage"})
        path = "%s/steps-%s-%s.json" % (OUT, kind, ap)
        json.dump(acts, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
        log = open("%s/log-%s-%s.txt" % (OUT, kind, ap), 'w', encoding='utf-8')
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        procs.append(subprocess.Popen([sys.executable, 'tools/shot.py', '--actions', path], stdout=log, stderr=subprocess.STDOUT, env=env))
for p in procs:
    p.wait()
print('all done', [p.returncode for p in procs])
