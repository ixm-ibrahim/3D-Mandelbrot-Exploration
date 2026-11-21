"""Build the test page and run one of the step lists below against it.

  python out/r5/page/run.py <name> [size] [theme]      e.g.  python out/r5/page/run.py fig4 1400x950 dark
                                                             python out/r5/page/run.py look 375x812 light

Step lists are Python here (not hand-written JSON) so the JavaScript needs no escaping. Pictures and the log go
to out/r5/page/, named <name>-<d|p><d|l>-... (d or p: desktop or phone width; d or l: dark or light). The look
list also stitches its pictures into sheets (sheet-look-..-a.png to -e.png).
Only one tools/shot.py may run at a time: the GPU is shared.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERE = 'out/r5/page/'
USE = ['src/body.html', 'src/css/00-base.css', 'src/js/75-presets.js', 'src/js/80-ui.js', 'src/js/90-boot.js', 'src/js/10-approaches.js']
PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const chosen = id => { const e = $(id); return e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : ''; };
const top = sel => { const e = document.querySelector(sel); window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - 84); };
const openAll = () => document.querySelectorAll('details.sec').forEach(d => { d.open = true; });
const grid = () => { let n = 0; const w = $('stage').clientWidth, h = $('stage').clientHeight; for (let i = 1; i < 8; i++) for (let j = 1; j < 8; j++) if (L.pick(w * i / 8, h * j / 8)) n++; return n; };
"""


def S(js, shot=None, clip=None, wait='done', timeout=300):
    a = {'js': PRE + js.strip()}
    if wait:
        a['wait'] = wait; a['timeout'] = timeout
    if shot:
        a['shot'] = HERE + shot
        if clip:
            a['clip'] = clip
    return a


def fig4(tag):
    return [
        S("L.R.warmOn = false; L.S.q.aa = 4; L.touch(); return 'open';"),
        # from the Kleinian view with the 2D view on, a cut, a modifier, a trap solid and a sweeping Lift dial
        S(r"""
$('ap-mercator').click(); type('par-mercator-liftNum', '0.4'); $('par-mercator-liftPlay').click();
$('mode-k').click(); $('flat').click(); L.S.cutOn = true; L.S.cut = 0.2; L.S.abs = [1, 0, 0]; L.S.colour.solid = 1; L.S.n = 3; L.syncControls(); L.touch();
await sleep(300);
$('fig4Show').click(); await sleep(400);
const S = L.S, p = S.param.mercator, bad = [];
if (S.mode !== 'j' || !$('mode-j').checked) bad.push('mode');
if (S.flat || $('flat').checked) bad.push('2D view');
if (S.c.join() !== '-1,0,0' || $('cxNum').value !== '-1' || $('cyNum').value !== '0' || $('czNum').value !== '0') bad.push('c dials ' + [$('cxNum').value, $('cyNum').value, $('czNum').value]);
if (L.APPROACHES[S.approach].id !== 'mercator' || !$('ap-mercator').checked) bad.push('approach');
if (p.planes !== 2 || $('par-mercator-planesNum').value !== '2') bad.push('planes ' + $('par-mercator-planesNum').value);
if (p.turn !== 0 || p.lift !== 0 || $('par-mercator-liftNum').value !== '0') bad.push('turn or lift ' + JSON.stringify(p) + ' box ' + $('par-mercator-liftNum').value);
if (S.n !== 2 || $('powNum').value !== '2') bad.push('power ' + $('powNum').value);
if (S.eq !== 'z^n + c' || S.cutOn || $('cutOn').checked || S.abs.join() !== '0,0,0' || $('absx').checked || S.colour.solid !== 0) bad.push('equation, cut, modifiers or trap solid');
if (chosen('juliaPreset') !== 'Basilica') bad.push('list shows ' + chosen('juliaPreset'));
if ($('juliaPanel').hidden || !$('kleinPanel').hidden || $('secApproach').hidden) bad.push('panels');
await sleep(1200);
if (L.S.param.mercator.lift !== 0) bad.push('the Lift sweep kept running: ' + L.S.param.mercator.lift);
if (bad.length) fail('Show Figure 4 left: ' + bad.join('; '));
return 'figure 4 set from the Kleinian 2D view; As it was found hidden: ' + $('juliaFound').hidden + '; stage top ' + Math.round($('stage').getBoundingClientRect().top);
""", tag + '-fig4.png', '#stage'),
        S(r"""
$('fig4Back').click(); await sleep(300);
const p = L.S.param.mercator;
if (p.planes !== 1 || $('par-mercator-planesNum').value !== '1') fail('Back to one plane left planes at ' + p.planes);
if ($('par-mercator-turn').closest('.dial').hidden) fail('the Turn dial did not come back with one plane');
if (L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0') fail('Back to one plane changed more than the planes');
return 'one plane; As it was found hidden: ' + $('juliaFound').hidden + ' title: ' + $('juliaFound').title;
""", tag + '-oneplane.png', '#stage'),
        # Back to one plane from the Kleinian view, and from another approach
        S(r"""
type('par-mercator-planesNum', '3'); $('ap-lathe').click(); $('mode-k').click(); await sleep(200);
$('fig4Back').click(); await sleep(300);
if (L.S.mode !== 'j' || !$('mode-j').checked) fail('from the Kleinian view, Back to one plane should go to the Julia set');
if (L.APPROACHES[L.S.approach].id !== 'mercator' || !$('ap-mercator').checked || L.S.param.mercator.planes !== 1 || $('par-mercator-planesNum').value !== '1') fail('approach or planes not shown');
return 'back to one plane from Kleinian + Lathe';
"""),
        # As it was found
        S(r"""
openAll();
pick('juliaPreset', 'Cracked Basilica'); await sleep(200);
const out = [];
if ($('juliaFound').hidden) fail('As it was found should show for an entry found with two planes while Planes is 1');
out.push($('juliaFound').title);
const cam = [L.cam.yaw, L.cam.pitch, L.cam.dist].join(), it = L.S.iter;
$('juliaFound').focus(); $('juliaFound').click(); await sleep(200);
if (L.S.param.mercator.planes !== 2 || $('par-mercator-planesNum').value !== '2') fail('As it was found did not set Planes to 2');
if (L.S.iter !== it || [L.cam.yaw, L.cam.pitch, L.cam.dist].join() !== cam || L.S.c.join() !== '-1,0.045,0.026') fail('As it was found changed more than the planes');
if (!$('juliaFound').hidden) fail('As it was found should hide once nothing differs');
if (document.activeElement === document.body) fail('focus was lost when the button went');
pick('juliaPreset', 'Douady rabbit'); await sleep(200);
if ($('juliaFound').hidden) fail('the rabbit records one plane and 24 iterations: the button should show');
out.push($('juliaFound').title);
$('juliaFound').click(); await sleep(200);
if (L.S.param.mercator.planes !== 1 || L.S.iter !== 24 || $('iterNum').value !== '24') fail('As it was found did not set one plane and 24 iterations');
$('ap-lathe').click(); type('iterNum', '14'); await sleep(200);
pick('juliaPreset', 'Cracked Basilica'); await sleep(200);
if (!$('juliaFound').hidden) fail('under another approach the planes do not count: the button should hide');
pick('juliaPreset', 'Douady rabbit'); await sleep(200);
if ($('juliaFound').hidden) fail('iterations count under every approach');
out.push($('juliaFound').title);
$('ap-mercator').click(); pick('juliaPreset', 'Cracked Basilica'); await sleep(200); $('juliaFound').click();
const g = [...$('juliaPreset').querySelectorAll('optgroup')].map(x => x.label + ': ' + [...x.children].map(o => o.text).join(', '));
top('#juliaPanel');
return out.concat(g);
""", tag + '-found.png'),
    ]


def look(tag):
    """The look-over of the new controls: viewport pictures of each, stitched into sheets by sheets()."""
    return [
        S(r"""
L.R.warmOn = false; L.S.q.aa = 2; L.touch(); openAll();
window.lookFiles = []; window.squaringLabSaveHook = (n, b) => window.lookFiles.push(n + ' ' + b.size);
const r = document.querySelector('.dials').getBoundingClientRect();
return { scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth, dials: [Math.round(r.left), Math.round(r.width)] };
"""),
        S(r"""
pick('exportSize', 'Typed'); await sleep(100);
const box = w => [...$('exportPanel').querySelectorAll('.dial')].find(e => !e.hidden && new RegExp(w, 'i').test(e.querySelector('label').textContent)).querySelector('input.num');
for (const e of [box('width'), box('height')]) { e.value = '256'; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }
$('exportStart').click(); await sleep(300); return 'picture job started';
""", wait='!window.squaringLab.exportBusy()'),
        S(r"""top('#secExport'); await sleep(250); return $('exportPanel').innerText.replace(/\s+/g, ' ').slice(0, 700);""", tag + '-1-export.png', wait=None),
        S(r"""window.squaringLabMeshTest = { cells: 48 }; $('meshStart').click(); await sleep(300); return 'model job started';""", wait='!window.squaringLab.meshBusy()'),
        S(r"""top('#secMesh'); await sleep(250); return $('meshPanel').innerText.replace(/\s+/g, ' ').slice(0, 1200);""", tag + '-2-mesh.png', wait=None),
        # trap solid in the Mandelbrot picture
        S(r"""delete window.squaringLabMeshTest; pick('col-solid', 'Is the solid'); window.scrollTo(0, 0); return 'trap solid, Mandelbrot';""", tag + '-s1-solid-m.png', '#stage'),
        S(r"""
const n = grid(); $('cutOn').click(); await sleep(100);
if (!shown('col-cutFace')) fail('no cut face tick box'); $('col-cutFace').click();
return 'trap solid in Mandelbrot mode: ' + n + ' of 49 probes hit it; cut open, cut face coloured';
""", tag + '-s2-cutface.png', '#stage'),
        S(r"""top('#secColour'); await sleep(250); return [...document.querySelectorAll('#colDials label')].filter(e => e.getBoundingClientRect().width > 0).map(e => e.textContent.trim());""", tag + '-3-col3d.png', wait=None),
        S(r"""$('col-cutFace').scrollIntoView({ block: 'center' }); await sleep(250); return 1;""", tag + '-4-col3d-low.png', wait=None),
        # the 2D view: outline, glow, inside colours
        S(r"""
$('col-cutFace').click(); $('cutOn').click(); pick('col-solid', 'Colours the surface'); $('flat').click(); await sleep(200);
pick('col-inMode', 'How quickly'); await sleep(100); pick('col-inPal', 'Fire'); type('col-edgeNum', '2'); type('col-edgeGlowNum', '12'); window.scrollTo(0, 0);
return 'inside colouring: mode ' + L.S.colour.inMode + ', palette ' + L.S.colour.inPal + '; reverse box shown: ' + shown('col-inRev');
""", tag + '-s3-inside.png', '#stage'),
        S(r"""$('col-inMode').scrollIntoView({ block: 'center' }); await sleep(250); return 1;""", tag + '-5-col2d.png', wait=None),
        # Kleinian: an entry of the new group, and a trap solid
        S(r"""
document.querySelector('#colReset .dial-reset').click(); $('flat').click(); $('mode-k').click(); await sleep(200);
const g = [...$('kleinPreset').querySelectorAll('optgroup')].find(x => x.label === 'Turning-out sphere'), names = [...g.children].map(o => o.text);
pick('kleinPreset', names[0]); $('kleinFrame').click(); window.scrollTo(0, 0);
return { entries: names.length, names };
""", tag + '-s4-klein-entry.png', '#stage'),
        S(r"""pick('col-solid', 'Is the solid'); return 'trap solid, Kleinian';""", tag + '-s5-solid-k.png', '#stage'),
        S(r"""const n = grid(); top('#kleinPanel'); await sleep(250); return 'trap solid in Kleinian mode: ' + n + ' of 49 probes hit it';""", tag + '-6-klein.png', wait=None),
        # Julia: the list with its new heading and "As it was found"
        S(r"""
pick('col-solid', 'Colours the surface'); $('mode-j').click(); await sleep(200); pick('juliaPreset', 'Cracked Basilica'); await sleep(200);
top('#juliaPanel'); await sleep(250);
return 'As it was found shown: ' + shown('juliaFound') + ' / ' + $('juliaFound').title;
""", tag + '-7-julia.png'),
        # closing texts
        S(r"""const h = [...document.querySelectorAll('footer.why h2')].find(e => e.textContent.startsWith('Questions')); window.scrollTo(0, h.getBoundingClientRect().top + window.scrollY - 10); await sleep(250); return 1;""", tag + '-f1.png', wait=None),
        S(r"""window.scrollBy(0, window.innerHeight - 110); await sleep(250); return 1;""", tag + '-f2.png', wait=None),
        S(r"""window.scrollBy(0, window.innerHeight - 110); await sleep(250); return 1;""", tag + '-f3.png', wait=None),
        S(r"""window.scrollBy(0, window.innerHeight - 110); await sleep(250); return 1;""", tag + '-f4.png', wait=None),
        S(r"""window.scrollBy(0, window.innerHeight - 110); await sleep(250); return [...document.querySelectorAll('footer.why [hidden]')].length + ' hidden elements in the closing texts; page bottom reached: ' + (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2);""", tag + '-f5.png', wait=None),
        # the buttons in the closing text: the picture must come into view
        S(r"""
$('fig4Show').scrollIntoView({ block: 'center' }); await sleep(200); $('fig4Show').click(); await sleep(1500);
const r = $('stage').getBoundingClientRect();
return 'after Show Figure 4 the stage is at ' + Math.round(r.top) + ' to ' + Math.round(r.bottom) + ' of ' + window.innerHeight;
""", tag + '-8-fig4.png'),
    ]


def sheets(tag, phone):
    """Stitch the look-over pictures of one width and theme into sheets (out/r5/page/sheet-<tag>-*.png)."""
    from PIL import Image

    def tiles(names, box=None, scale=1.0):
        out = []
        for n in names:
            path = os.path.join(ROOT, HERE, '%s-%s.png' % (tag, n))
            if not os.path.exists(path):
                continue
            im = Image.open(path).convert('RGB')
            if box and not phone:
                im = im.crop((box[0], 0, min(box[1], im.width), im.height))
            if scale != 1.0:
                im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
            out.append(im)
        return out

    def sheet(name, ims):
        if not ims:
            return
        w = sum(i.width for i in ims) + 8 * (len(ims) - 1); h = max(i.height for i in ims)
        sh = Image.new('RGB', (w, h), (128, 128, 128)); x = 0
        for i in ims:
            sh.paste(i, (x, 0)); x += i.width + 8
        sh.save(os.path.join(ROOT, HERE, 'sheet-%s-%s.png' % (tag, name)))
        print('sheet-%s-%s.png %dx%d' % (tag, name, w, h))

    col = (948, 1342)   # the controls column at 1400 wide
    sheet('a', tiles(['1-export', '2-mesh', '3-col3d', '4-col3d-low'], col))
    sheet('b', tiles(['5-col2d', '6-klein', '7-julia'], col) + tiles(['8-fig4'], None, 1.0 if phone else 0.4))
    sheet('c', tiles(['s1-solid-m', 's2-cutface', 's3-inside', 's4-klein-entry', 's5-solid-k'], None, 0.9 if phone else 0.36))
    sheet('d', tiles(['f1', 'f2', 'f3'], (60, 800)))
    sheet('e', tiles(['f4', 'f5'], (60, 800)))


LISTS = {'fig4': fig4, 'look': look}


def main():
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception: pass
    name = sys.argv[1]
    size = sys.argv[2] if len(sys.argv) > 2 else '1400x950'
    theme = sys.argv[3] if len(sys.argv) > 3 else 'dark'
    tag = '%s-%s%s' % (name, 'p' if size.startswith('375') else 'd', theme[0])
    steps = LISTS[name](tag)
    path = os.path.join(ROOT, HERE, tag + '.json')
    json.dump(steps, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    subprocess.check_call([sys.executable, os.path.join(ROOT, 'build.py'), '--name', 'r5-page', '--base', 'base5', '--use'] + USE, cwd=ROOT)
    log = os.path.join(ROOT, HERE, tag + '.log')
    with open(log, 'w', encoding='utf-8') as f:
        code = subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/r5-page.html', '--size', size, '--theme', theme, '--actions', path], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
    print(open(log, encoding='utf-8').read())
    print('exit', code, '->', HERE + tag + '.log')
    if name == 'look':
        sheets(tag, size.startswith('375'))
    sys.exit(code)


if __name__ == '__main__':
    main()
