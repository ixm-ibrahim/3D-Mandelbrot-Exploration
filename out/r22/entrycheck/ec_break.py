"""Round 22, entrycheck: try to break the two entries. One picture per scene into out/r22/entrycheck/break/, and what
the page says. Then the same picture again after switching to other entries and back (compared pixel by pixel).
  python out/r22/entrycheck/ec_break.py            -> break.log, break/*.png, break-switch.txt
  python out/r22/entrycheck/ec_break.py phone      -> phone.log, phone/*.png (window 390x844)
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drive

RAB = '[-0.122561, 0.744862, 0]'
BASE = "S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 40; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; S.cut = 0; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; S.colour.solid = 0; S.colour.mode = 0; S.q.de = 3; S.mode = 'j'; if (S.param.pulledplane) Object.assign(S.param.pulledplane, { hold: 0.05, ease: 0.7, cpull: 16 }); L.resetCam();"
SCENES = [
    ('01-basilica', ""),
    ('02-rabbit', "S.c = %s;" % RAB),
    ('03-siegel', "S.c = [-0.390541, -0.586788, 0];"),
    ('04-mandel', "S.mode = 'm'; S.iter = 30;"),
    ('05-pow1-julia', "S.n = 1; S.c = [0.1, 0, 0];"),
    ('06-pow1-mandel', "S.n = 1; S.mode = 'm';"),
    ('07-pow3-julia', "S.n = 3; S.c = [0.3, 0, 0];"),
    ('08-pow3-mandel', "S.n = 3; S.mode = 'm'; S.iter = 30;"),
    ('09-pow-2-julia', "S.n = -2; S.c = [-1, 0, 0]; S.iter = 30;"),
    ('10-pow-2-mandel', "S.n = -2; S.mode = 'm'; S.iter = 30;"),
    ('11-z2z3-julia', "S.eq = 'z^2 + z^3 + c'; S.c = [-0.2, 0, 0];"),
    ('12-z2z3-mandel', "S.eq = 'z^2 + z^3 + c'; S.mode = 'm'; S.iter = 30;"),
    ('13-mosaic', "S.mode = 'm'; S.mosaic = true; S.iter = 30;"),
    ('14-mosaic-flat', "S.mode = 'm'; S.mosaic = true; S.flat = true; S.iter = 30;"),
    ('15-rabbit-flat', "S.c = %s; S.flat = true; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.4;" % RAB),
    ('16-mandel-flat', "S.mode = 'm'; S.flat = true; S.iter = 30; S.v2.x = -0.5; S.v2.y = 0; S.v2.h = 3.2;"),
    ('17-flat-at-0.3', "S.flat = true; S.cut = 0.3; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.4;"),
    ('18-cut-0.2', "S.cutOn = true; S.cut = 0.2;"),
    ('19-c-off-plane', "S.c = [-1, 0, 0.3];"),
    ('20-c-turned-rabbit', "S.c = [-0.122561, 0.7335, 0.1293];"),
    ('21-trap-solid', "S.colour.solid = 1;"),
    ('22-trap-added', "S.colour.solid = 2;"),
    ('23-escape-count', "S.colour.mode = 2; S.c = %s;" % RAB),
    ('24-mandel-from-c', "S.mode = 'm'; S.z0 = 'c'; S.iter = 30;"),
    ('25-flip', "S.flip = [1, 1]; S.abs = [1, 0, 1];"),
    ('26-iter-200', "S.iter = 200;"),
    ('27-iter-1', "S.iter = 1;"),
    ('28-mandel-iter-100', "S.mode = 'm'; S.iter = 100;"),
    ('29-mandel-iter-14', "S.mode = 'm'; S.iter = 14;"),
]
PP = [
    ('30-hold-0', "S.param.pulledplane.hold = 0;"),
    ('31-ease-1', "S.param.pulledplane.ease = 1; S.c = %s;" % RAB),
    ('32-cpull-0', "S.param.pulledplane.cpull = 0; S.c = %s;" % RAB),
    ('33-cpull-256', "S.param.pulledplane.cpull = 256; S.c = %s;" % RAB),
    ('34-hold-4', "S.param.pulledplane.hold = 4;"),
    ('35-hold-0-mandel', "S.param.pulledplane.hold = 0; S.mode = 'm'; S.iter = 30;"),
]
HIDE = "document.querySelectorAll('#stage *').forEach(e => { if (e.tagName !== 'CANVAS' && !e.querySelector('canvas')) e.style.visibility = 'hidden'; });"


def scene(id_, name, set_, folder):
    js = drive.HEAD + "$('ap-%s').click(); await sleep(200); if (apId() !== '%s') fail('could not choose'); %s %s go(); await settle(); " % (id_, id_, BASE, set_) + HIDE + """
const g = grid(), st = $('status') ? $('status').textContent : '', em = $('emptyNote') && !$('emptyNote').hidden ? $('emptyNote').textContent : '';
const a = L.APPROACHES[S.approach], q = S.param[a.id];
const t = [a.formula(q, S.n), a.crush(q, S.n)[1], a.smooth(q, S.n)[1], a.slice(true, q, S.n), a.roundNote(q, S.n), $('card') ? $('card').innerText : ''].join(' ');
return '%s %s: ' + g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring' + (L.R.failed ? '; PROGRAM FAILED: ' + L.R.failed : '') + (/undefined|NaN|Infinity/.test(t) ? '; BAD TEXT: ' + (t.match(/.{0,60}(undefined|NaN|Infinity).{0,40}/) || [''])[0] : '') + (em ? '; note on the stage: ' + em.slice(0, 160) : '') + '; status: ' + st.slice(0, 90);
""" % (id_, name)
    return dict(js=js, wait='done', timeout=900, shot='out/r22/entrycheck/%s/%s-%s.png' % (folder, id_, name), clip='#stage canvas')


def main():
    steps = [drive.UP]
    for id_ in ('alongonce', 'pulledplane'):
        for name, set_ in SCENES + (PP if id_ == 'pulledplane' else []):
            steps.append(scene(id_, name, set_, 'break'))
    # switching back and forth: the same picture each time, to the pixel
    order = ['alongonce', 'pulledplane', 'turnalong', 'mercator', 'pulledplane', 'windsq', 'alongonce', 'lathe', 'mercator', 'turnalong', 'pulledplane', 'alongonce']
    seen = {}
    for id_ in order:
        seen[id_] = seen.get(id_, 0) + 1
        steps.append(scene(id_, 'switch%d' % seen[id_], "S.c = [-1, 0, 0]; S.iter = 30;", 'switch'))
    # ... and in the Mandelbrot view with the three-neighbour 2D picture in between
    for id_ in ['alongonce', 'pulledplane', 'alongonce', 'pulledplane']:
        seen[id_] = seen.get(id_, 0) + 1
        steps.append(scene(id_, 'switch%d' % seen[id_], "S.mode = 'm'; S.flat = %s; S.iter = 30; S.v2.x = -0.5; S.v2.y = 0; S.v2.h = 3.2;" % ('true' if seen[id_] in (4,) else 'true'), 'switch'))
    for d in ('break', 'switch'):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    code, text, vals = drive.shot(drive.PAGE, steps, 'break-steps', '1400x950')
    drive.write('break.log', text + 'exit %d\n' % code)
    print(text[-9000:]); print('exit', code)
    import numpy as np
    from PIL import Image
    rep = []
    for id_, n in seen.items():
        ims = []
        for k in range(1, n + 1):
            p = os.path.join(HERE, 'switch', '%s-switch%d.png' % (id_, k))
            if os.path.exists(p):
                ims.append((k, np.asarray(Image.open(p).convert('RGB'), np.int16)))
        flat_from = {'alongonce': 4, 'pulledplane': 4}.get(id_, 99)
        for grp in ([x for x in ims if x[0] < flat_from], [x for x in ims if x[0] >= flat_from]):
            for k, im in grp[1:]:
                a = grp[0][1]
                if a.shape != im.shape:
                    rep.append('%s: picture %d has another size than picture %d' % (id_, k, grp[0][0])); continue
                d = np.abs(a - im).max(-1)
                rep.append('%-12s picture %d against picture %d: %d of %d pixels differ (largest %d of 255); not background: %d' % (id_, k, grp[0][0], (d > 0).sum(), d.size, d.max(), (np.abs(a - a[2, 2]).max(-1) > 6).sum()))
    drive.write('break-switch.txt', '\n'.join(rep) + '\n'); print('\n'.join(rep))
    return code


def phone():
    os.makedirs(os.path.join(HERE, 'phone'), exist_ok=True)
    steps = [drive.UP]
    for id_ in ('alongonce', 'pulledplane'):
        steps.append(dict(js=drive.HEAD + """
$('mode-j').click(); await sleep(200);
const r = $('ap-%(id)s'); if (!r) fail('no entry in the list');
r.click(); await sleep(300); if (apId() !== '%(id)s') fail('could not choose');
S.c = [-1, 0, 0]; S.iter = 30; S.n = 2; S.eq = 'z^n + c'; L.resetCam(); go(); await settle();
const g = grid(), W = window.innerWidth, wide = [...document.querySelectorAll('body *')].filter(e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0 && (b.right > W + 1 || b.left < -1) && getComputedStyle(e).position !== 'fixed' && !e.closest('[hidden]'); }).slice(0, 6).map(e => e.tagName + '#' + e.id + '.' + String(e.className).slice(0, 30) + ' ' + Math.round(e.getBoundingClientRect().left) + '..' + Math.round(e.getBoundingClientRect().right));
const dials = [...document.querySelectorAll('[id^="par-%(id)s-"]')].map(e => e.id + ':' + Math.round(e.getBoundingClientRect().width));
return '%(id)s at ' + W + 'x' + window.innerHeight + ': ' + g[0] + ' probes hit; page scroll width ' + document.documentElement.scrollWidth + '; stage ' + $('stage').clientWidth + 'x' + $('stage').clientHeight + '; wider than the window: ' + JSON.stringify(wide) + '; dials: ' + dials.join(' ') + (L.R.failed ? '; PROGRAM FAILED ' + L.R.failed : '');
""" % dict(id=id_), wait='done', timeout=600, shot='out/r22/entrycheck/phone/%s-1-top.png' % id_))
        steps.append(dict(js=drive.HEAD + """
const sec = $('secApproach'); sec.scrollIntoView({ block: 'start' }); await sleep(300);
const btn = $('apAboutBtn'), box = $('apAbout'); if (box.hidden) { btn.click(); await sleep(200); }
const b = box.getBoundingClientRect();
return 'approach section: ' + Math.round(sec.getBoundingClientRect().width) + ' wide; about box ' + Math.round(b.width) + ' x ' + Math.round(b.height) + ', ' + box.textContent.length + ' characters; menu name: ' + $('apMenuName').textContent;
""", wait='done', timeout=300, shot='out/r22/entrycheck/phone/%s-2-approach.png' % id_))
    code, text, vals = drive.shot(drive.PAGE, steps, 'phone-steps', '390x844')
    drive.write('phone.log', text + 'exit %d\n' % code)
    print(text[-5000:]); print('exit', code)
    return code


if __name__ == '__main__':
    sys.exit(phone() if len(sys.argv) > 1 and sys.argv[1] == 'phone' else main())
