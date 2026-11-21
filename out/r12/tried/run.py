"""Round 12, tried rules: checks of dist/r12-tried.html. Run from the project root, one at a time.

  python out/r12/tried/run.py math       MATH against the flat complex power, texts dry run  -> math.txt
  python out/r12/tried/run.py pictures   every entry: Mandelbrot solid and the Julia set c = -1 -> m-<id>.png, j-<id>.png, sheet.png
  python out/r12/tried/run.py time       time until idle and until every program is prepared, 3 runs per page -> time.txt
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = 'dist/r12-tried.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
IDS = ['mercator', 'fold', 'lathe', 'tilt', 'bulb', 'classic', 'split', 'softfold', 'axisbulb', 'pillow']


def shot(page, steps, name):
    sj = os.path.join(HERE, name + '.json')
    json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj],
                       capture_output=True, env=ENV, cwd=ROOT)
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


def math():
    steps = [{'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries';", 'wait': 'done', 'timeout': 300},
             {'js': open(os.path.join(HERE, 'checks.js'), encoding='utf-8').read()}]
    code, text = shot(PAGE, steps, 'math-steps')
    write('math.txt', text)
    m = re.search(r'step 2 result: (\{.*?\n\})', text, re.S)
    if not m:
        print(text[-3000:]); return code
    data = json.loads(m.group(1))
    out = ['%d points on each plane. Worst |F - z^n| / |z^n|; "bad" = points off by more than 1e-9.' % data['points'], '']
    for r in data['rows']:
        cells = []
        for k, v in r.items():
            if re.match(r'n-?[\d.]+$', k):
                cells.append('%s: %.2e (bad %d%s)' % (k, v, r['bad' + k[1:]], '' if 'z0_' + k[1:] not in r else ', z exactly 0' if r['z0_' + k[1:]] else ', z not exactly 0'))
        out.append('%-9s %-34s %-6s %s' % (r['id'], r['label'], r['plane'], ' | '.join(cells)))
    out += ['', 'text problems: %s' % (data['textProblems'] or 'none'), 'texts with a long dash: %d' % data['dashes'], ''] + data['list']
    out += ['', 'shot.py exit code %d' % code, text.split('\n}')[-1].strip()]
    write('math-table.txt', '\n'.join(out) + '\n')
    print('\n'.join(out))
    return code


HEAD = """
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
"""


def pictures():
    steps = [{'js': "const L = window.squaringLab; return 'page up, ' + L.APPROACHES.length + ' entries: ' + L.APPROACHES.map(a => a.id).join(' ');", 'wait': 'done', 'timeout': 300}]
    names = []

    def step(js, name):
        steps.append({'js': HEAD + js + " return '" + name + " approach ' + L.APPROACHES[L.S.approach].id + ' mode ' + L.S.mode + ' failed ' + L.R.failed;",
                      'timeout': 600, 'wait': 'done', 'shot': 'out/r12/tried/' + name + '.png', 'clip': '#stage canvas'})
        names.append(name)

    for i in IDS:
        step("$('ap-%s').click(); await sleep(300); $('mode-m').click(); await sleep(200); L.S.cutOn = false; L.S.flat = false; L.resetCam(); go(); await sleep(200);" % i, 'm-' + i)
        step("$('mode-j').click(); await sleep(200); L.S.c = [-1, 0, 0]; L.resetCam(); go(); await sleep(200);", 'j-' + i)
    # the Pillow's other layout
    step("L.S.param.pillow.layout = 1; $('mode-m').click(); await sleep(200); L.resetCam(); go(); await sleep(200);", 'm-pillow-smooth')
    step("$('mode-j').click(); await sleep(200); L.S.c = [-1, 0, 0]; L.resetCam(); go(); await sleep(200);", 'j-pillow-smooth')
    steps.append({'js': "const L = window.squaringLab; return 'end: failed ' + L.R.failed + ', status ' + document.getElementById('status').textContent;"})
    code, text = shot(PAGE, steps, 'pictures-steps')
    write('pictures.log', text)
    print(text)
    # how much of each picture is not background, so an empty picture cannot pass as drawn
    from PIL import Image
    rep = []
    for n in names:
        im = Image.open(os.path.join(HERE, n + '.png')).convert('RGB')
        w, h = im.size
        bg = im.getpixel((2, 2))
        px = im.resize((w // 4, h // 4), Image.NEAREST).getdata()
        solid = sum(1 for p in px if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 24)
        rep.append('%-18s %dx%d  not background: %.1f %%' % (n, w, h, 100.0 * solid / len(px)))
    write('pictures-filled.txt', '\n'.join(rep) + '\n')
    print('\n'.join(rep))
    order = ['m-' + i for i in IDS] + ['m-pillow-smooth'] + ['j-' + i for i in IDS] + ['j-pillow-smooth']
    subprocess.call([sys.executable, os.path.join(ROOT, 'out', 'me', 'sheet.py'), 'out/r12/tried/sheet.png', '11', '0.3'] + ['out/r12/tried/%s.png' % n for n in order], cwd=ROOT, env=ENV)
    return code


TIMER = """
const L = window.squaringLab;
window.__t = null;
let idleAt = null;
const iv = setInterval(() => {
  const now = performance.now();
  if (idleAt === null && L.idle()) idleAt = now;
  if (idleAt !== null && L.idle() && !L.R.warming && !L.R.warmT) {
    clearInterval(iv);
    window.__t = JSON.stringify({ entries: L.APPROACHES.length, idle_ms: Math.round(idleAt), prepared_ms: Math.round(now), failed: String(L.R.failed) });
  }
}, 20);
return 'timer started at ' + Math.round(performance.now()) + ' ms, idle already: ' + L.idle();
"""


def time_():
    out, best = [], {}
    for run in range(3):
        for page in ('dist/v12a.html', PAGE):
            steps = [{'js': TIMER, 'wait': 'window.__t', 'timeout': 400}, {'js': 'return window.__t;'}]
            code, text = shot(page, steps, 'time-steps')
            m = re.search(r'step 2 result: (\{.*\})', text)
            line = 'run %d %-20s exit %d %s' % (run + 1, page, code, m.group(1) if m else text[-400:].replace('\n', ' / '))
            if 'PAGE PROBLEMS' in text:
                line += '  PAGE PROBLEMS: ' + text.split('PAGE PROBLEMS')[1][:400].replace('\n', ' / ')
            print(line); out.append(line)
            if m:
                d = json.loads(m.group(1))
                b = best.setdefault(page, {'idle_ms': 1e18, 'prepared_ms': 1e18})
                b['idle_ms'] = min(b['idle_ms'], d['idle_ms']); b['prepared_ms'] = min(b['prepared_ms'], d['prepared_ms'])
            write('time.txt', '\n'.join(out) + '\n')
    for page, b in best.items():
        line = 'least of 3: %-20s first picture fully drawn %.2f s, every program prepared %.2f s' % (page, b['idle_ms'] / 1000, b['prepared_ms'] / 1000)
        print(line); out.append(line)
    write('time.txt', '\n'.join(out) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit({'math': math, 'pictures': pictures, 'time': time_}[sys.argv[1]]())
