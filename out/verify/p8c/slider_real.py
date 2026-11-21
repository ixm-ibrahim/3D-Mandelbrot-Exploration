import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, os.path.join(ROOT, 'notes'))
from shot import WS, Page, CHROMES
import camera_real as CR
OUT = os.path.join(ROOT, 'out', 'verify', 'p8c')
L = 'window.squaringLab'


def say(*a):
    print(*a, flush=True)


def st(d):
    return d.js("const L=%s, $=id=>document.getElementById(id); return {dist:+L.cam.dist.toPrecision(6), zmin:L.S.view.zmin, zmax:L.S.view.zmax, h:+L.S.v2.h.toPrecision(6), hmin:L.S.v2.hmin, hmax:L.S.v2.hmax, near:$('camNear').value, far:$('camFar').value, val:$('camVal').textContent, top:$('camThumb').style.top, endA:$('camEndA').textContent, endB:$('camEndB').textContent, nearInv:$('camNear').getAttribute('aria-invalid'), farInv:$('camFar').getAttribute('aria-invalid'), kind:document.getElementById('stage').dataset.cam, bound:L.S.view.bound};" % L)


def key(d, name, vk, mods=0, text=None):
    d.p.call('Input.dispatchKeyEvent', type='rawKeyDown', key=name, code=name, windowsVirtualKeyCode=vk, modifiers=mods)
    if text:
        d.p.call('Input.dispatchKeyEvent', type='char', key=name, code=name, windowsVirtualKeyCode=vk, text=text)
    d.p.call('Input.dispatchKeyEvent', type='keyUp', key=name, code=name, windowsVirtualKeyCode=vk, modifiers=mods)


def typebox(d, sel, text, end='Enter'):
    d.click(sel); time.sleep(0.05)
    d.js("const e=document.querySelector(%s); e.focus(); e.select();" % json.dumps(sel))
    if text == '':
        key(d, 'Delete', 46)
    else:
        d.p.call('Input.insertText', text=text)
    if end == 'Enter':
        key(d, 'Enter', 13, text='\r')
    elif end == 'Escape':
        key(d, 'Escape', 27)
    elif end == 'blur':
        d.js("document.activeElement && document.activeElement.blur();")
    time.sleep(0.15)
    s0 = st(d)
    d.settle(); time.sleep(0.2)
    s = st(d); s['flagNear'] = s0['nearInv']; s['flagFar'] = s0['farInv']
    return s


def wheel(d, n, dy=100, sel='#view'):
    x, y = d.at(sel)
    d.mouse('mouseMoved', x, y)
    for _ in range(n):
        d.wheel(x, y, dy); time.sleep(0.02)
    d.settle(); time.sleep(0.15)


def run(d):
    d.js("%s.R.warmOn=false; %s.S.q.aa=2; %s.touch(); window.scrollTo(0,0);" % (L, L, L)); d.settle()
    say('A default', st(d))
    d.p.wait(L + '.idle()', 180)
    d.p.shot(os.path.join(OUT, 's-01-default.png'), '#stage')
    x, y = d.at('#view'); d.mouse('mouseMoved', x, y)
    d.js("window.__tr=[]; const t0=performance.now(); const f=()=>{ window.__tr.push([Math.round(performance.now()-t0), +%s.cam.dist.toFixed(4), document.getElementById('camThumb').style.top, document.getElementById('camVal').textContent]); if(performance.now()-t0<900) requestAnimationFrame(f); }; requestAnimationFrame(f);" % L)
    for _ in range(4):
        d.wheel(x, y, 100); time.sleep(0.05)
    time.sleep(1.1)
    tr = d.js('return window.__tr;')
    say('B wheel trace (t, dist, thumb top, label) samples:', tr[0], tr[len(tr) // 4], tr[len(tr) // 2], tr[-1], 'frames', len(tr))
    say('B after 4 notches out', st(d))
    wheel(d, 40, 100); say('C wheel out 40 notches (expect stop at far 60)', st(d))
    d.p.wait(L + '.idle()', 180)
    d.p.shot(os.path.join(OUT, 's-02-far60.png'), '#stage')
    wheel(d, 100, -100); say('D wheel in 100 notches (expect stop at near 0.005)', st(d))
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()
    b = d.box('#camRail'); rx = b[0] + b[2] / 2
    d.mouse('mouseMoved', rx, b[1] + b[3] * 0.3)
    d.mouse('mousePressed', rx, b[1] + b[3] * 0.3, button='left', buttons=1, clickCount=1)
    time.sleep(0.3); d.settle(); s1 = st(d)
    for i in range(1, 9):
        d.mouse('mouseMoved', rx + 40, b[1] + b[3] * (0.3 + 0.05 * i), button='left', buttons=1); time.sleep(0.03)
    d.settle(); s2 = st(d)
    d.mouse('mouseMoved', rx + 200, b[1] + b[3] * 2.0, button='left', buttons=1); d.settle(); s3 = st(d)
    d.mouse('mouseReleased', rx + 200, b[1] + b[3] * 2.0, button='left', clickCount=1); d.settle()
    exp = lambda t: 0.005 * (60 / 0.005) ** t
    say('E rail press at 30%% -> dist %s (expect %.4g); drag to 70%% -> %s (expect %.4g); past the bottom -> %s (expect 60)' % (s1['dist'], exp(0.3), s2['dist'], exp(0.7), s3['dist']))
    d.mouse('mouseMoved', x, y); time.sleep(0.2); say('E after release, moving the mouse over the picture', st(d)['dist'])
    d.js("%s.resetCam(); %s.touch(); document.getElementById('camRail').focus();" % (L, L)); d.settle()
    for name, vk in (('ArrowDown', 40), ('ArrowUp', 38), ('PageDown', 34), ('Home', 36), ('End', 35)):
        key(d, name, vk); d.settle(); say('F rail key', name, '->', st(d)['dist'])
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()
    for sel, text, end in (('#camFar', '200', 'Enter'), ('#camFar', '0', 'Enter'), ('#camFar', '-5', 'Enter'), ('#camFar', 'abc', 'Enter'), ('#camFar', '', 'Enter'),
                           ('#camFar', '5000', 'Enter'), ('#camFar', '1e2', 'Enter'), ('#camFar', '300', 'blur'), ('#camFar', '77', 'Escape'),
                           ('#camNear', '0', 'Enter'), ('#camNear', '-1', 'Enter'), ('#camNear', 'near', 'Enter'), ('#camNear', '500', 'Enter'), ('#camNear', '0,5', 'Enter'),
                           ('#camNear', '2', 'Enter'), ('#camFar', '1', 'Enter'), ('#camFar', '3', 'Enter'), ('#camNear', '20', 'Enter'), ('#camNear', '0.005', 'Enter'), ('#camFar', '1000', 'Enter')):
        s = typebox(d, sel, text, end)
        say('G type %-8s %-6r %-6s -> near box %s far box %s | zmin %s zmax %s | dist %s label %s | flagged near=%s far=%s' % (sel, text, end, s['near'], s['far'], s['zmin'], s['zmax'], s['dist'], s['val'], s['flagNear'], s['flagFar']))
    wheel(d, 80, 100); s = st(d); say('H far=1000, wheel out 80 notches', s)
    d.p.wait(L + '.idle()', 180); d.p.shot(os.path.join(OUT, 's-03-far1000-bound8.png'), '#stage')
    typebox(d, '#camFar', '4'); d.settle(); say('I far=4', st(d))
    d.click('#reset'); d.settle(); time.sleep(0.3); s = st(d); say('I after the stage Reset button with far=4 (expect dist <= 4)', s)
    d.p.wait(L + '.idle()', 180); d.p.shot(os.path.join(OUT, 's-04-reset-beyond-far.png'), '#stage')
    wheel(d, 1, 100); say('I one notch out after that', st(d))
    d.js("document.getElementById('mode-k').click();"); time.sleep(0.5); d.settle(); say('I Kleinian chosen with far=4 (its start distance is 7)', st(d))
    d.js("document.getElementById('mode-m').click();"); time.sleep(0.5); d.settle()
    d.js("const b=[...document.querySelectorAll('button')].filter(b=>/Reset this section/.test(b.textContent)); const v=b.find(x=>x.closest('details') && /View/.test(x.closest('details').querySelector('summary').textContent)); window.__vr=v; if(v){v.closest('details').open=true; v.scrollIntoView({block:'center'});} return !!v;")
    typebox(d, '#viewBoundNum', '1000'); say('J typed drawing radius 1000 ->', st(d)['bound'])
    typebox(d, '#viewBoundNum', '0'); say('J typed drawing radius 0 ->', st(d)['bound'])
    typebox(d, '#viewBoundNum', '250'); say('J typed drawing radius 250 ->', st(d)['bound'], 'slider', d.js("const s=document.getElementById('viewBound'); return [s.min,s.max,s.value];"))
    d.p.shot(os.path.join(OUT, 's-09-view-section.png'))
    d.js("window.__vr.click();"); d.settle(); time.sleep(0.3); say('J after View section reset (expect far 60, radius 8)', st(d))
    d.js("window.scrollTo(0,0);")
    d.js("document.getElementById('flat').click();"); time.sleep(0.6); d.settle(); say('K 2D on', st(d))
    wheel(d, 4, 100); say('K 2D wheel out 4', st(d))
    wheel(d, 60, 100); say('K 2D wheel out 60 (expect h stops at 40)', st(d))
    d.p.wait(L + '.idle()', 180); d.p.shot(os.path.join(OUT, 's-05-flat-out40.png'), '#stage')
    for sel, text in (('#camFar', '5000'), ('#camFar', '0'), ('#camFar', 'x'), ('#camNear', '-3'), ('#camNear', '9999')):
        s = typebox(d, sel, text); say('K 2D type %s %r -> near box %s far box %s | hmin %s hmax %s | h %s | flagged %s %s' % (sel, text, s['near'], s['far'], s['hmin'], s['hmax'], s['h'], s['flagNear'], s['flagFar']))
    typebox(d, '#camNear', '0.0005'); typebox(d, '#camFar', '2000')
    wheel(d, 80, 100); say('K 2D far 2000 wheel out', st(d))
    d.p.wait(L + '.idle()', 180); d.p.shot(os.path.join(OUT, 's-06-flat-out2000.png'), '#stage')
    b = d.box('#camRail'); rx = b[0] + b[2] / 2
    d.mouse('mouseMoved', rx, b[1] + b[3] * 0.5); d.mouse('mousePressed', rx, b[1] + b[3] * 0.5, button='left', buttons=1, clickCount=1)
    d.mouse('mouseMoved', rx, b[1] + b[3] * 0.6, button='left', buttons=1); d.mouse('mouseReleased', rx, b[1] + b[3] * 0.6, button='left', clickCount=1); d.settle()
    say('K 2D rail drag to 60%% (expect h %.4g)' % (0.0005 * (2000 / 0.0005) ** 0.6), st(d))
    d.p.wait(L + '.idle()', 180); d.p.shot(os.path.join(OUT, 's-07-flat-rail.png'), '#stage')
    d.js("document.getElementById('flat').click();"); time.sleep(0.6); d.settle(); say('L back to 3D (expect the 3D limits and distance)', st(d))
    d.click('#camFly'); time.sleep(0.4); d.settle(); say('M fly', st(d), d.js("return [document.getElementById('camNear').hidden, document.getElementById('camFar').hidden];"))
    d.p.shot(os.path.join(OUT, 's-08-fly.png'), '#stage')
    d.click('#camArc'); time.sleep(0.4); d.settle()


def main():
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix='p8c-')
    proc = subprocess.Popen([chrome, '--headless=new', '--remote-debugging-port=%d' % port, '--user-data-dir=' + prof, '--no-first-run', '--no-default-browser-check',
                             '--disable-extensions', '--hide-scrollbars', '--window-size=1400,950', '--force-device-scale-factor=1', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        target = None
        for _ in range(100):
            try:
                with urllib.request.urlopen('http://127.0.0.1:%d/json/list' % port, timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get('type') == 'page']
                if pages:
                    target = pages[0]['webSocketDebuggerUrl']; break
            except Exception:
                pass
            time.sleep(0.2)
        page = Page(WS(target))
        for m in ('Runtime.enable', 'Log.enable', 'Page.enable'):
            page.call(m)
        page.call('Emulation.setDeviceMetricsOverride', width=1400, height=950, deviceScaleFactor=1, mobile=False)
        page.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-color-scheme', 'value': 'dark'}])
        page.call('Emulation.setFocusEmulationEnabled', enabled=True)
        d = CR.Drive(page)
        page.call('Page.navigate', url='file:///' + os.path.join(ROOT, 'dist', 'preview.html').replace('\\', '/'))
        page.wait("document.readyState === 'complete'", 30)
        page.wait(L + ' && ' + L + '.idle()', 240); time.sleep(0.3)
        try:
            run(d)
        except Exception as e:
            say('SCRIPT ERROR', repr(e))
        page.js('return 0;'); say('page problems:', page.problems[:10])
        try:
            page.call('Browser.close')
        except Exception:
            pass
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)


main()
