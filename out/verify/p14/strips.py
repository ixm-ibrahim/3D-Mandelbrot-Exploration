import json, os, subprocess, sys
ROOT = os.getcwd()
OUT = 'out/verify/p14'
HEAD = "const L = window.squaringLab, $ = id => document.getElementById(id); const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; "
DEG = [-180, -135, -90, -45, 0, 45, 90, 135]
LIFT = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
def setup(ap, n, mode='m', extra=''):
    return HEAD + "document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); $('mode-%s').click(); $('ap-%s').click(); $('qFast').click(); L.R.warmOn = false; L.S.n = %s; L.S.iter = 10; L.syncControls(); %s L.cam.target = [0,0,0]; L.cam.dist = 4.2; L.refresh(false); return JSON.stringify({cam: [L.cam.yaw, L.cam.pitch, L.cam.dist], n: L.S.n, p: L.S.param['%s']});" % (mode, ap, n, extra, ap)
def strip(name, ap, key, vals, n=8, mode='m', extra=''):
    acts = [{"js": setup(ap, n, mode, extra), "wait": "done", "timeout": 400}]
    for v in vals:
        acts.append({"js": HEAD + "type('par-%s-%sNum', '%s'); return '%s=' + L.S.param['%s']['%s'] + ' n=' + L.S.n;" % (ap, key, v, key, ap, key),
                     "wait": "done", "timeout": 400, "shot": "%s/%s_%s.png" % (OUT, name, str(v).replace('-', 'm')), "clip": "#stage"})
    p = '%s/%s.json' % (OUT, name)
    json.dump(acts, open(p, 'w'))
    return name, p, vals
P1 = "type('par-mercator-planesNum', '1');"
jobs = {
 'a': [strip('bulb_lat_n8', 'bulb', 'lat', DEG), strip('bulb_lon_n8', 'bulb', 'lon', DEG),
       strip('classic_theta_n8', 'classic', 'theta', DEG), strip('classic_phi_n8', 'classic', 'phi', DEG),
       strip('merc_lift_n8', 'mercator', 'lift', LIFT, extra=P1), strip('merc_turn_n8', 'mercator', 'turn', DEG, extra=P1)],
 'b': [strip('bulb_lat_n2', 'bulb', 'lat', DEG[::2], n=2), strip('bulb_lat_nm2', 'bulb', 'lat', DEG[::2], n=-2),
       strip('classic_theta_n2', 'classic', 'theta', DEG[::2], n=2), strip('classic_theta_nm2', 'classic', 'theta', DEG[::2], n=-2),
       strip('merc_lift_n2', 'mercator', 'lift', LIFT[::2], n=2, extra=P1), strip('merc_lift_nm2', 'mercator', 'lift', LIFT[::2], n=-2, extra=P1),
       strip('bulb_lat_julia8', 'bulb', 'lat', DEG[::2], mode='j'), strip('merc_lift_julia8', 'mercator', 'lift', LIFT[::2], mode='j', extra=P1),
       strip('merc_lift_n8_planes2', 'mercator', 'lift', LIFT[::2])],
}
which = jobs[sys.argv[1]]
env = dict(os.environ, PYTHONIOENCODING='utf-8')
procs = [(name, vals, subprocess.Popen([sys.executable, 'tools/shot.py', '--actions', p], stdout=open('%s/%s.log' % (OUT, name), 'w', encoding='utf-8'), stderr=subprocess.STDOUT, env=env)) for name, p, vals in which]
from PIL import Image
for name, vals, pr in procs:
    rc = pr.wait()
    print(name, 'exit', rc)
    ims = []
    for v in vals:
        f = '%s/%s_%s.png' % (OUT, name, str(v).replace('-', 'm'))
        if os.path.exists(f): ims.append(Image.open(f).convert('RGB'))
    if not ims: continue
    w = 420; ims = [im.resize((w, int(im.height * w / im.width))) for im in ims]
    cols = 4 if len(ims) <= 8 else 5
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * ims[0].height), (0, 0, 0))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * im.height))
    sheet.save('%s/sheet_%s.png' % (OUT, name))
