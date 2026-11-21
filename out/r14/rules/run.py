"""Round 14, rules: checks and pictures of dist/r14-rules.html. Run from the project root, one at a time.

  python out/r14/rules/run.py checks            the numbers (checks.js)                         -> checks.txt
  python out/r14/rules/run.py pictures <set>    pictures and a contact sheet of one set         -> <set>-*.png, sheet-<set>.png
       sets: quat4 rotor kleinsq kleinsq2 rotorframe extra
  python out/r14/rules/run.py same              old entries before and after the hook           -> same.txt
  python out/r14/rules/run.py page              every new entry: texts, Learn tab, slice sample -> page.txt
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = 'dist/r14-rules.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
REL = 'out/r14/rules/'


def shot(page, steps, name, size=None):
    sj = os.path.join(HERE, name + '.json')
    json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj]
    if size:
        cmd += ['--size', size]
    p = subprocess.run(cmd, capture_output=True, env=ENV, cwd=ROOT)
    text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    lines = []
    for line in text.splitlines():
        m = re.match(r'(step \d+ result: )(".*")$', line)
        if m:
            try:
                lines.append(m.group(1) + json.loads(m.group(2))); continue
            except ValueError:
                pass
        lines.append(line)
    return p.returncode, '\n'.join(lines) + '\n'


def write(name, text):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


UP = {'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries: ' + L.APPROACHES.map(a => a.id).join(' ');", 'wait': 'done', 'timeout': 600}


def checks():
    steps = [UP, {'js': open(os.path.join(HERE, 'checks.js'), encoding='utf-8').read(), 'timeout': 900}]
    code, text = shot(PAGE, steps, 'checks-steps')
    write('checks.txt', text)
    print(text[-200:] if len(text) > 60000 else text)
    return code


def checks2():
    steps = [UP, {'js': open(os.path.join(HERE, 'checks2.js'), encoding='utf-8').read(), 'timeout': 1500}]
    code, text = shot(PAGE, steps, 'checks2-steps')
    write('checks2.txt', text)
    print(text)
    return code


HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const pick = id => { $('ap-' + id).click(); };
const par = (id, o) => { Object.assign(S.param[id], o); };
"""
RABBIT = '[-0.1226, 0.7449, 0]'


def view3(mode, c=None, extra=''):
    js = "$('mode-%s').click(); await sleep(150); S.flat = false; S.cutOn = false; " % mode
    if c:
        js += "S.c = %s; " % c
    return js + extra + " L.resetCam(); go(); await sleep(200);"


def view2(mode, c=None, x=0.0, h=3.2, extra=''):
    js = "$('mode-%s').click(); await sleep(150); S.cutOn = false; S.flat = true; S.cut = 0; S.v2.x = %s; S.v2.y = 0; S.v2.h = %s; " % (mode, x, h)
    if c:
        js += "S.c = %s; " % c
    return js + extra + " go(); await sleep(200);"


def five(i, pre=''):
    """the five pictures asked for: Mandelbrot solid, three Julia sets, the cut at z = 0 (Mandelbrot and the Julia set for c = -1)"""
    p = "pick('%s'); await sleep(250); %s" % (i, pre)
    return [
        (i + '-m', p + view3('m')),
        (i + '-j-basilica', p + view3('j', '[-1, 0, 0]')),
        (i + '-j-rabbit', p + view3('j', RABBIT)),
        (i + '-j-off-axis', p + view3('j', '[-1, 0.15, 0.1]')),
        (i + '-cut-m', p + view2('m', None, -0.5, 3.2)),
        (i + '-cut-j-basilica', p + view2('j', '[-1, 0, 0]', 0, 3.2)),
    ]


SETS = {
    'quat4': lambda: (
        five('quat4', "par('quat4', { w: 0, tilt: 0, cw: 0 });")
        + [('quat4-m-w03', "pick('quat4'); par('quat4', { w: 0.3, tilt: 0, cw: 0 });" + view3('m')),
           ('quat4-m-w06', "pick('quat4'); par('quat4', { w: 0.6, tilt: 0, cw: 0 });" + view3('m')),
           ('quat4-m-tilt45', "pick('quat4'); par('quat4', { w: 0, tilt: 45, cw: 0 });" + view3('m')),
           ('quat4-m-tilt90', "pick('quat4'); par('quat4', { w: 0, tilt: 90, cw: 0 });" + view3('m')),
           ('quat4-cut-m-w03', "pick('quat4'); par('quat4', { w: 0.3, tilt: 0, cw: 0 });" + view2('m', None, -0.5, 3.2)),
           ('quat4-cut-m-tilt45', "pick('quat4'); par('quat4', { w: 0, tilt: 45, cw: 0 });" + view2('m', None, -0.5, 3.2)),
           ('quat4-j-basilica-cw03', "pick('quat4'); par('quat4', { w: 0, tilt: 0, cw: 0.3 });" + view3('j', '[-1, 0, 0]')),
           ('quat4-j-rabbit-cw03', "pick('quat4'); par('quat4', { w: 0, tilt: 0, cw: 0.3 });" + view3('j', RABBIT)),
           ('quat4-j-rabbit-tilt40', "pick('quat4'); par('quat4', { w: 0, tilt: 40, cw: 0 });" + view3('j', RABBIT)),
           ('quat4-j-rabbit-w02', "pick('quat4'); par('quat4', { w: 0.2, tilt: 0, cw: 0 });" + view3('j', RABBIT)),
           ('quat4-j-classic', "pick('quat4'); par('quat4', { w: 0, tilt: 0, cw: 0.5 });" + view3('j', '[-0.2, 0.6, 0.2]')),
           ('quat4-j-off-axis-cw04-tilt30', "pick('quat4'); par('quat4', { w: 0.1, tilt: 30, cw: 0.4 });" + view3('j', '[-1, 0.15, 0.1]')),
           ('lathe-m', "pick('lathe'); await sleep(250);" + view3('m')),
           ('lathe-j-rabbit', "pick('lathe'); await sleep(250);" + view3('j', RABBIT)),
           ]),
    'rotor': lambda: (
        five('rotor', "par('rotor', { lon: 0, lat: 90 });")
        + [('rotor-m-x', "pick('rotor'); par('rotor', { lon: 0, lat: 0 });" + view3('m')),
           ('rotor-m-lon40', "pick('rotor'); par('rotor', { lon: 40, lat: 0 });" + view3('m')),
           ('rotor-m-lat30', "pick('rotor'); par('rotor', { lon: 0, lat: 30 });" + view3('m')),
           ('rotor-cut-m-x', "pick('rotor'); par('rotor', { lon: 0, lat: 0 });" + view2('m', None, -0.5, 3.2)),
           ('rotor-cut-m-lon40', "pick('rotor'); par('rotor', { lon: 40, lat: 0 });" + view2('m', None, -0.5, 3.2)),
           ('rotor-cut-m-lat30', "pick('rotor'); par('rotor', { lon: 0, lat: 30 });" + view2('m', None, -0.5, 3.2)),
           ('rotor-j-rabbit-x', "pick('rotor'); par('rotor', { lon: 0, lat: 0 });" + view3('j', RABBIT)),
           ('lathe-m', "pick('lathe'); await sleep(250);" + view3('m')),
           ]),
    'kleinsq': lambda: (
        five('kleinsq')
        + [('kleinsq-cut-j-rabbit', "pick('kleinsq');" + view2('j', RABBIT, 0, 3.2)),
           ('kleinsq-m-n3', "pick('kleinsq'); S.n = 3;" + view3('m')),
           ('kleinsq-cut-m-n3', "pick('kleinsq'); S.n = 3;" + view2('m', None, 0, 3.2)),
           ('kleinsq-m-n4', "pick('kleinsq'); S.n = 4;" + view3('m') + " S.n = 2;"),
           ('mercator-m', "S.n = 2; pick('mercator'); await sleep(250);" + view3('m')),
           ('mercator-j-basilica', "pick('mercator');" + view3('j', '[-1, 0, 0]')),
           ('mercator-cut-m', "pick('mercator');" + view2('m', None, -0.5, 3.2)),
           ('mercator-cut-j-basilica', "pick('mercator');" + view2('j', '[-1, 0, 0]', 0, 3.2)),
           ]),
    'kleinsq2': lambda: (
        five('kleinsq2')
        + [('kleinsq2-j-x-03', "pick('kleinsq2');" + view3('j', '[0.3, 0, 0]')),
           ('kleinsq2-j-x-175', "pick('kleinsq2');" + view3('j', '[-1.75, 0, 0]')),
           ('fold-m', "pick('fold'); await sleep(250);" + view3('m')),
           ('fold-j-basilica', "pick('fold');" + view3('j', '[-1, 0, 0]')),
           ('fold-j-off-axis', "pick('fold');" + view3('j', '[-1, 0.15, 0.1]')),
           ]),
    'rotorframe': lambda: (
        five('rotorframe')
        + [('lathe-m', "pick('lathe'); await sleep(250);" + view3('m')),
           ('bulb-m', "pick('bulb'); await sleep(250);" + view3('m')),
           ('lathe-j-rabbit', "pick('lathe');" + view3('j', RABBIT)),
           ('bulb-j-rabbit', "pick('bulb');" + view3('j', RABBIT)),
           ('rotorframe-m-n3', "pick('rotorframe'); S.n = 3;" + view3('m')),
           ('rotorframe-m-n8', "pick('rotorframe'); S.n = 8;" + view3('m') + " S.n = 2;"),
           ]),
}


def pictures(name):
    steps = [UP]
    names = []
    for n, js in SETS[name]():
        steps.append({'js': HEAD + js + " return '" + n + ": approach ' + L.APPROACHES[S.approach].id + ', mode ' + S.mode + ', n ' + S.n + ', flat ' + S.flat + ', params ' + JSON.stringify(S.param[L.APPROACHES[S.approach].id]) + ', failed ' + L.R.failed;",
                      'timeout': 900, 'wait': 'done', 'shot': REL + n + '.png', 'clip': '#stage canvas'})
        names.append(n)
    steps.append({'js': "const L = window.squaringLab; return 'end: failed ' + L.R.failed + ', status ' + document.getElementById('status').textContent;"})
    code, text = shot(PAGE, steps, 'pictures-' + name + '-steps')
    write('pictures-' + name + '.log', text)
    print(text)
    from PIL import Image
    rep = []
    for n in names:
        im = Image.open(os.path.join(HERE, n + '.png')).convert('RGB')
        w, h = im.size
        bg = im.getpixel((2, 2))
        px = im.resize((w // 4, h // 4), Image.NEAREST).getdata()
        solid = sum(1 for p in px if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 24)
        rep.append('%-32s %dx%d  not background: %.1f %%' % (n, w, h, 100.0 * solid / len(px)))
    write('pictures-' + name + '-filled.txt', '\n'.join(rep) + '\n')
    print('\n'.join(rep))
    subprocess.call([sys.executable, os.path.join(ROOT, 'out', 'me', 'sheet.py'), REL + 'sheet-' + name + '.png', '6', '0.34'] + [REL + n + '.png' for n in names], cwd=ROOT, env=ENV)
    return code


# Old entries before and after the hook: the same pictures from dist/v14a.html and from the test page, compared pixel by pixel.
def same():
    shots = [('mercator', 'm', None), ('lathe', 'j', RABBIT), ('fold', 'j', '[-1, 0, 0]'), ('tilt', 'j', '[-1, 0.15, 0.1]'), ('bulb', 'j', RABBIT), ('split', 'j', '[-1, 0, 0]')]
    out = []
    for tag, page in (('before', 'dist/v14a.html'), ('after', PAGE)):
        steps = [UP]
        for i, mode, c in shots:
            steps.append({'js': HEAD + "pick('%s'); await sleep(250);" % i + view3(mode, c) + " return '%s %s';" % (i, mode), 'timeout': 900, 'wait': 'done',
                          'shot': REL + 'same-%s-%s-%s.png' % (tag, i, mode), 'clip': '#stage canvas'})
        if tag == 'after':   # quat4 with its dials at 0 against the Lathe, on the same page
            for i in ('lathe', 'quat4'):
                steps.append({'js': HEAD + "pick('%s'); await sleep(250);" % i + view3('m') + " return '%s m';" % i, 'timeout': 900, 'wait': 'done', 'shot': REL + 'same-zero-%s-m.png' % i, 'clip': '#stage canvas'})
                steps.append({'js': HEAD + "pick('%s'); await sleep(250);" % i + view3('j', RABBIT) + " return '%s j';" % i, 'timeout': 900, 'wait': 'done', 'shot': REL + 'same-zero-%s-j.png' % i, 'clip': '#stage canvas'})
            for i in ('lathe', 'rotor'):
                steps.append({'js': HEAD + "pick('%s'); await sleep(250); if (S.param.rotor) par('rotor', { lon: 0, lat: 0 });" % i + view3('j', '[-1, 0.15, 0.1]') + " return '%s j';" % i, 'timeout': 900, 'wait': 'done', 'shot': REL + 'same-axisx-%s-j.png' % i, 'clip': '#stage canvas'})
        code, text = shot(page, steps, 'same-%s-steps' % tag)
        out.append('%s: exit %d %s' % (page, code, 'PAGE PROBLEMS' if 'PAGE PROBLEMS' in text else ''))
        write('same-%s.log' % tag, text)
    from PIL import Image, ImageChops
    def cmp(a, b, label):
        A = Image.open(os.path.join(HERE, a)).convert('RGB'); B = Image.open(os.path.join(HERE, b)).convert('RGB')
        if A.size != B.size:
            return '%-28s sizes differ %s %s' % (label, A.size, B.size)
        d = ImageChops.difference(A, B).getdata()
        diff = sum(1 for p in d if p != (0, 0, 0)); big = sum(1 for p in d if max(p) > 8)
        return '%-28s %dx%d  pixels that differ: %d (%.4f %%), by more than 8 of 255: %d' % (label, A.size[0], A.size[1], diff, 100.0 * diff / len(d), big)
    for i, mode, c in shots:
        out.append(cmp('same-before-%s-%s.png' % (i, mode), 'same-after-%s-%s.png' % (i, mode), 'before/after %s %s' % (i, mode)))
    out.append(cmp('same-zero-lathe-m.png', 'same-zero-quat4-m.png', 'lathe / quat4 at 0, m'))
    out.append(cmp('same-zero-lathe-j.png', 'same-zero-quat4-j.png', 'lathe / quat4 at 0, j'))
    out.append(cmp('same-axisx-lathe-j.png', 'same-axisx-rotor-j.png', 'lathe / rotor axis x, j'))
    write('same.txt', '\n'.join(out) + '\n')
    print('\n'.join(out))
    return 0


PAGE_JS = open(os.path.join(HERE, 'page.js'), encoding='utf-8').read() if os.path.exists(os.path.join(HERE, 'page.js')) else ''


def page():
    steps = [UP, {'js': PAGE_JS, 'timeout': 900}]
    code, text = shot(PAGE, steps, 'page-steps')
    write('page.txt', text)
    print(text)
    return code


if __name__ == '__main__':
    cmd = sys.argv[1]
    sys.exit({'checks': checks, 'checks2': checks2, 'same': same, 'page': page}[cmd]() if cmd != 'pictures' else pictures(sys.argv[2]))
