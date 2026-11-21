"""Round 28, Track A, builder, test 6: drag and type through the give-way rules, with REAL mouse and keys (drive28).

  python out/r28/dials/mk/dials28.py [wide|phone] [page]   -> out/r28/dials/logs/dials-<wide|phone>.txt

Every line says what was done, what the page then holds, and OK or WRONG against what docs/ROUND28.md section 1.2
asks for (points 2 to 6). "p" is what the size dial shows, "second" what the second-sphere dial shows.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drive28 as D

STATE = ("return JSON.stringify({ p: $('ballsSizeNum').value, second: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, t: S.k.bt, rho: S.k.brho, bit: S.k.bit, grid: S.k.bgrid, mode: S.mode, group: S.k.group, "
         "sizeThumb: $('ballsSize').value, rhoThumb: $('ballsRho').value, depthThumb: $('ballsDepth').value, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', status: $('status').textContent, prog: String(L.R.sig).replace(/\\n/g, '/').slice(0, 12) });")
lines = []; wrong = 0


def say(s):
    print(s); lines.append(s); sys.stdout.flush()


def st(lab):
    return json.loads(lab.js(STATE))


def near(a, b, tol=0.011):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def check(lab, what, **want):
    """want: p, second, depth (numbers shown), warn_has / warn_not (text), t / rho (state)."""
    global wrong
    s = st(lab); bad = []
    for k in ('p', 'second', 'depth'):
        if k in want and not near(s[k], want[k]):
            bad.append('%s shows %s, should show %s' % (k, s[k], want[k]))
    for k in ('t', 'rho'):
        if k in want and not near(s[k], want[k], 1e-9):
            bad.append('%s is %r, should be %r' % (k, s[k], want[k]))
    for frag in want.get('warn_has', []):
        if frag not in s['warn']:
            bad.append('the sentence lacks "%s"' % frag)
    for frag in want.get('warn_not', []):
        if frag in s['warn']:
            bad.append('the sentence should not say "%s"' % frag)
    if 'warn_is' in want and s['warn'] != want['warn_is']:
        bad.append('the sentence should be "%s"' % want['warn_is'])
    if bad:
        wrong += 1
    say('%-6s %s -> p %s, second %s, depth %s (t %.6g, rho %.6g; program %s)%s%s' % ('OK' if not bad else 'WRONG', what, s['p'], s['second'], s['depth'], s['t'], s['rho'], s['prog'],
                                                                             ' | "' + s['warn'] + '"' if s['warn'] else '', ' *** ' + '; '.join(bad) if bad else ''))
    return s


def reset(lab):
    lab.click('#ballsReset button'); time.sleep(0.15)


PAST = 'Past 100 the second sphere has to be smaller than the first'
NOW = 'The second sphere is now'
FEW = 'With so few rounds'

if __name__ == '__main__':
    a = sys.argv[1:]
    kind = a[0] if a and a[0] in ('wide', 'phone') else 'wide'
    page = a[1] if len(a) > 1 else 'dist/r28-dials.html'
    size = '390x800' if kind == 'phone' else '1400x950'
    with D.Lab(page, size, 'dark') as lab:
        say('page %s, window %s' % (page, size))
        # the user's way in: the Approach list, then the row
        lab.js("$('ap-balls').click(); await settle(); return 1;"); lab.done()
        check(lab, 'the row Balls on balls', p=55.56, second=100, depth=16, t=1.4, rho=1, warn_is='')
        s = st(lab)
        say('       sliders: size %s, second sphere %s, depth %s' % tuple(lab.js("return ['ballsSize', 'ballsRho', 'ballsDepth'].map(id => $(id).min + ' to ' + $(id).max + ' (typed ' + $(id + 'Num').getAttribute('aria-valuemin') + ' to ' + $(id + 'Num').getAttribute('aria-valuemax') + ')');")))

        say('--- A. typing the size past 100')
        lab.type('#ballsSizeNum', '150'); check(lab, 'typed size 150', p=150, second=33.33, warn_has=[PAST, '33.33 % of the first'])
        lab.type('#ballsSizeNum', '300'); check(lab, 'typed size 300 (the second sphere follows as 50 / p)', p=300, second=16.67, warn_has=[PAST, '16.67 %'])
        lab.type('#ballsSizeNum', '101'); check(lab, 'typed size 101', p=101, second=49.5, warn_has=[PAST])
        lab.type('#ballsSizeNum', '80'); check(lab, 'typed size 80 (back below 100: the second sphere is not put back)', p=80, second=50, warn_has=[NOW, '50 % of the first', 'Reset this section'], warn_not=[PAST])
        reset(lab); check(lab, 'Reset this section', p=55.56, second=100, depth=16, t=1.4, rho=1, warn_is='')

        say('--- B. dragging the size slider from where it opens to about 250, then back to about 60')
        seen = lab.drag('#ballsSize', 250, 10, read=st)
        say('       on the way: ' + ', '.join('p %s second %s' % (x['p'], x['second']) for x in seen))
        ok = all((float(x['p']) <= 100 and near(x['second'], 100)) or (float(x['p']) > 100 and near(x['second'], round(min(50.0, 5000 / float(x['p'])), 2), 0.02)) for x in seen)
        global_wrong = 0 if ok else 1; wrong += global_wrong
        say('%-6s every step of the drag has the second sphere at 100 up to size 100 and at 50 / p %% past it' % ('OK' if ok else 'WRONG'))
        s = check(lab, 'let go', warn_has=[PAST])
        ok = float(s['p']) > 200 and near(s['second'], round(5000 / float(s['p']), 2), 0.02) and near(s['sizeThumb'], s['p'], 0.06)
        wrong += 0 if ok else 1; say('%-6s after letting go the thumb stands at what the dial shows (%s) and the second sphere is 50 / p' % ('OK' if ok else 'WRONG', s['sizeThumb']))
        seen = lab.drag('#ballsSize', 60, 8, read=st)
        say('       on the way back: ' + ', '.join('p %s second %s' % (x['p'], x['second']) for x in seen))
        s = check(lab, 'let go at about 60', second=50, warn_has=[NOW], warn_not=[PAST])
        reset(lab)

        say('--- C. the second sphere set by hand stays until the size would make the spheres cut into each other')
        lab.type('#ballsRhoNum', '30'); check(lab, 'typed second sphere 30', p=55.56, second=30, t=1.4, rho=0.3, warn_has=[NOW, '30 % of the first'])
        lab.type('#ballsSizeNum', '200'); check(lab, 'typed size 200 (200 x 0.30 = 60: no need to give way)', p=200, second=30, warn_has=[PAST, '30 %'])
        lab.type('#ballsSizeNum', '400'); check(lab, 'typed size 400 (400 x 0.30 = 120: gives way)', p=400, second=12.5, warn_has=[PAST, '12.5 %'])
        lab.type('#ballsSizeNum', '2000'); check(lab, 'typed size 2000', p=2000, second=2.5)
        lab.type('#ballsSizeNum', '5000'); check(lab, 'typed size 5000 (past the end: held at 2000)', p=2000, second=2.5)
        lab.type('#ballsSizeNum', '0.2'); check(lab, 'typed size 0.2 (past the end: held at 1)', p=1, second=50)
        reset(lab)

        say('--- D. the second sphere moved: the size gives way')
        lab.type('#ballsSizeNum', '300'); check(lab, 'typed size 300', p=300, second=16.67)
        lab.type('#ballsRhoNum', '40'); check(lab, 'typed second sphere 40 (300 x 0.40 = 120: the size becomes 50 / 0.40)', p=125, second=40, warn_has=[PAST, '40 %'])
        lab.type('#ballsRhoNum', '100'); check(lab, 'typed second sphere 100 (the size becomes 50)', p=50, second=100, rho=1, t=1.5, warn_is='')
        lab.type('#ballsRhoNum', '20'); check(lab, 'typed second sphere 20 (50 x 0.20 = 10: the size stays)', p=50, second=20)
        reset(lab)

        say('--- E. the jump between 50 and 100')
        for typed, want in (('60', 50), ('75', 50), ('76', 100), ('99', 100), ('51', 50), ('1', 2), ('0', 2), ('250', 100), ('33.33', 33.33), ('50', 50)):
            lab.type('#ballsRhoNum', typed); check(lab, 'typed second sphere %s' % typed, second=want)
        lab.click('#ballsRhoNum'); lab.key('ArrowUp'); check(lab, 'arrow up in the box at 50', second=100)
        lab.key('ArrowDown'); check(lab, 'arrow down in the box at 100', second=50)
        lab.key('ArrowDown'); check(lab, 'arrow down in the box at 50', second=49)
        lab.key('ArrowUp'); check(lab, 'arrow up in the box at 49', second=50)
        lab.click('#ballsRhoNum + .dial-steps .dial-up')
        check(lab, 'the small up button at 50', second=100)
        lab.click('#ballsRhoNum + .dial-steps .dial-down'); check(lab, 'the small down button at 100', second=50)
        lab.click('#ballsRhoNum + .dial-steps .dial-down'); check(lab, 'the small down button at 50', second=49)
        lab.type('#ballsRhoNum', '50')
        x, y = lab.thumb_x('#ballsRho'); lab.click_at(x, y)                    # the slider has the focus now
        s = check(lab, 'a click on the slider thumb at 50', second=50)
        lab.key('ArrowRight'); check(lab, 'arrow right on the slider at 50', second=100)
        lab.key('ArrowLeft'); s = check(lab, 'arrow left on the slider at 100', second=50)
        lab.key('ArrowLeft'); check(lab, 'arrow left on the slider at 50', second=49)
        reset(lab)
        seen = lab.drag('#ballsRho', 30, 10, read=st)
        say('       dragging the second sphere from 100 down to about 30: ' + ', '.join('%s (thumb %s)' % (x['second'], x['rhoThumb']) for x in seen))
        ok = all(near(x['second'], 100) if float(x['rhoThumb']) > 75 else near(x['second'], 50) if float(x['rhoThumb']) > 50 else near(x['second'], x['rhoThumb']) for x in seen)
        wrong += 0 if ok else 1; say('%-6s on the way the dial shows 100 while the thumb is above 75, 50 between 50 and 75, the thumb\'s own value below' % ('OK' if ok else 'WRONG'))
        check(lab, 'let go at about 30')
        seen = lab.drag('#ballsRho', 66, 6, read=st, hold=True)
        s1 = st(lab); lab.release(); s2 = check(lab, 'dragged up to about 66 and let go (the nearer of the two is 50)', second=50)
        ok = near(s2['rhoThumb'], 50); wrong += 0 if ok else 1
        say('%-6s while held the thumb stood at %s and the dial showed %s; let go, the thumb goes to %s' % ('OK' if ok else 'WRONG', s1['rhoThumb'], s1['second'], s2['rhoThumb']))
        lab.drag('#ballsRho', 90, 6); s2 = check(lab, 'dragged up to about 90 and let go', second=100)
        ok = near(s2['rhoThumb'], 100); wrong += 0 if ok else 1; say('%-6s the thumb goes to %s' % ('OK' if ok else 'WRONG', s2['rhoThumb']))
        reset(lab)

        say('--- F. where the two spheres touch, and the depth')
        lab.type('#ballsRhoNum', '50'); lab.type('#ballsSizeNum', '200')
        check(lab, 'second sphere 50, then size 200 (200 x 0.50 = 100: they touch)', p=200, second=50, t=0.75, rho=0.5, warn_has=['At 200 the chain never ends', PAST])
        lab.type('#ballsSizeNum', '200.1'); check(lab, 'typed size 200.1 (past touching: gives way)', p=200.1, second=24.99, warn_has=[PAST], warn_not=['never ends'])
        reset(lab)
        lab.type('#ballsSizeNum', '100'); check(lab, 'typed size 100 with two equal spheres', p=100, second=100, t=1, rho=1, warn_has=['At 100 the chain never ends'], warn_not=[PAST, NOW])
        reset(lab)
        lab.type('#ballsDepthNum', '4'); check(lab, 'typed depth 4', depth=4, warn_has=[FEW])
        lab.type('#ballsDepthNum', '0'); check(lab, 'typed depth 0 (held at 1)', depth=1, warn_has=[FEW])
        lab.type('#ballsDepthNum', '5'); check(lab, 'typed depth 5', depth=5, warn_not=[FEW])
        lab.type('#ballsDepthNum', '5000'); check(lab, 'typed depth 5000 (held at 1000)', depth=1000)
        lab.type('#ballsDepthNum', '16')
        lab.drag('#ballsDepth', 'right', 5); check(lab, 'depth slider dragged past its right end', depth=100)
        lab.drag('#ballsDepth', 'left', 5); check(lab, 'depth slider dragged past its left end', depth=1, warn_has=[FEW])
        reset(lab)
        lab.drag('#ballsSize', 'right', 6); check(lab, 'size slider dragged past its right end', p=400, second=12.5)
        lab.drag('#ballsSize', 'left', 6); check(lab, 'size slider dragged past its left end', p=2, second=50)
        lab.drag('#ballsRho', 'left', 6); check(lab, 'second-sphere slider dragged past its left end', second=2)
        lab.drag('#ballsRho', 'right', 6); check(lab, 'second-sphere slider dragged past its right end', second=100)
        reset(lab); check(lab, 'Reset this section', p=55.56, second=100, depth=16, t=1.4, rho=1, warn_is='')

        say('--- G. leaving and coming back, the 2D view, Frame it, Reset everything')
        lab.type('#ballsSizeNum', '150'); lab.click('#ballsFrame'); lab.done()
        s = check(lab, 'size 150, Frame it', p=150, second=33.33)
        say('       ' + lab.js("return 'camera ' + (+L.cam.dist.toFixed(2)) + ' away, reach ' + (+L.ballsReach().toFixed(3)) + ', Drawing radius ' + S.view.bound + ', picture ' + $('status').textContent;"))
        lab.js("$('mode-m').click(); await settle(); return 1;"); lab.done()
        say('       the Mandelbrot view: ' + lab.js("return 'mode ' + S.mode + ', ' + $('status').textContent + ', Kleinian panel hidden: ' + $('kleinPanel').hidden;"))
        lab.js("$('ap-balls').click(); await settle(); return 1;"); lab.done()
        check(lab, 'back by the row in the Approach list (the dials are as they were left)', p=150, second=33.33, warn_has=[PAST])
        lab.js("$('kleinGroup0').click(); await settle(); return 1;"); lab.done()
        say('       the first group: ' + lab.js("return 'group ' + S.k.group + ', balls part hidden: ' + $('ballsPart').hidden + ', ' + $('status').textContent + ', program ' + String(L.R.sig).replace(/\\n/g, '/');"))
        lab.js("$('kleinGroup1').click(); await settle(); return 1;"); lab.done()
        check(lab, 'back by the choice of group', p=150, second=33.33, warn_has=[PAST])
        lab.js("S.flat = true; L.syncControls(); L.refresh(false); await settle(); return 1;"); lab.done()
        check(lab, 'the 2D view', p=150, second=33.33)
        lab.type('#ballsRhoNum', '50'); lab.type('#ballsSizeNum', '200'); lab.done()
        check(lab, 'the 2D view where they touch', warn_has=['At 200 the chain never ends', 'small circles between the large ones'])
        lab.js("S.flat = false; L.syncControls(); L.refresh(false); await settle(); return 1;"); lab.done()
        check(lab, 'the 3D view where they touch', warn_has=['At 200 the chain never ends', 'small balls between the large ones'])
        lab.click('#resetAll'); lab.done()
        say('       Reset everything: ' + lab.js("return 'mode ' + S.mode + ', group ' + S.k.group + ', t ' + S.k.bt + ', rho ' + S.k.brho + ', depth ' + S.k.bit + ', grid ' + S.k.bgrid + ', ' + $('status').textContent;"))
        s = st(lab); ok = s['mode'] == 'm' and s['group'] == 0 and s['t'] == 1.4 and s['rho'] == 1 and s['bit'] == 16
        wrong += 0 if ok else 1; say('%-6s Reset everything puts all of it back' % ('OK' if ok else 'WRONG'))

        say('--- H. the sentence of a saved 3D model')
        lab.js("$('ap-balls').click(); await settle(); return 1;"); lab.done()
        # (one model a visit: on the wide window with the neighbours at 150, on the phone as the object opens)
        for size_, rho_ in ((('150', None),) if kind == 'wide' else (('55.56', '100'),)):
            if rho_:
                lab.type('#ballsRhoNum', rho_)
            lab.type('#ballsSizeNum', size_); lab.click('#ballsFrame'); lab.done()
            sm = check(lab, 'before the model: size %s' % size_, p=float(size_))
            lab.js("window.__saved = null; window.squaringLabSaveHook = (name, blob) => { window.__saved = { name, blob }; }; window.squaringLabMeshTest = { cells: 40 }; $('meshStart').click(); return 1;")
            began = False
            for _ in range(1200):
                busy = lab.js("return L.meshBusy();")
                began = began or busy
                if began and not busy:
                    break
                time.sleep(0.25 if began else 0.05)
                if not began and _ > 200:
                    break
            made = lab.js("if ($('secMesh')) $('secMesh').open = true; await sleep(100); $('meshSave').click(); await sleep(900); delete window.squaringLabMeshTest; delete window.squaringLabSaveHook; const s = window.__saved; if (!s) return 'nothing was saved: ' + ($('meshMsg') ? $('meshMsg').textContent : '');"
                          " const bytes = new Uint8Array(await s.blob.arrayBuffer()), text = new TextDecoder('latin1').decode(bytes.subarray(0, Math.min(bytes.length, 4000000)));"
                          " return [...new Set([...text.matchAll(/Made from[^\\r\\n]{0,400}/g)].map(m => m[0]))].join(' || ');")
            want_second = size_ == '150'
            ok = began and (('second sphere 33.33 % of the first' in made) if want_second else ('second sphere' not in made and 'neighbours 55.56 %' in made))
            wrong += 0 if ok else 1
            say('%-6s a model at size %s (the job ran: %s): "%s"' % ('OK' if ok else 'WRONG', size_, began, made))
        prob = lab.problems()
        say('console: ' + ('no errors' if not prob else '%d PROBLEMS: ' % len(prob) + ' | '.join(p[:300] for p in prob[:6])))
        wrong += 1 if prob else 0
    say('lines marked WRONG: %d' % wrong)
    os.makedirs(os.path.join(os.path.dirname(HERE), 'logs'), exist_ok=True)
    with open(os.path.join(os.path.dirname(HERE), 'logs', 'dials-%s.txt' % kind), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
