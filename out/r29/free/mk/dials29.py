"""Round 29, Track A, builder, section 4 point 7: the dials, driven the way a hand drives them (real mouse presses,
moves and releases and real keys through Chrome's debugging port: out/r28/final/ui/mk/hand.py).

  python -B out/r29/free/mk/dials29.py <wide|phone> <light|dark> [part ...]   -> out/r29/free/logs/dials-<layout>-<theme>.txt
  parts (default all): free reach limits reset words frame mesh

free:   dragging or typing the size never changes the second sphere's number, and the other way round
reach:  every value from 2 to 100 can be had on the second sphere (slider, arrow keys, typed 62.5)
limits: typed limits (size 1 to 2000, second sphere 2 to 100, depth 1 to 1000)
reset:  Reset this section gives 55.56 / 100 / 16
words:  the sentences of docs/ROUND29.md section 2 at chosen states, 3D and 2D
frame:  Frame it shows the middle ball and both neighbours in every state of both panels (3D: the three balls lie in
        the picture as the camera sees them; 2D: in the view)
mesh:   a 3D model can be made at Y1 and at X1 (the page's own buttons; 48 cells through the page's test switch)
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); FREE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FREE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk')); sys.path.insert(0, HERE)
from hand import Hand
import kit29 as K

LAYOUT = sys.argv[1] if len(sys.argv) > 1 else 'wide'
THEME = sys.argv[2] if len(sys.argv) > 2 else 'light'
PARTS = sys.argv[3:] or ['free', 'reach', 'limits', 'reset', 'words', 'frame', 'mesh']
SIZE = {'wide': '1400x950', 'phone': '390x800'}[LAYOUT]
PAGE = os.environ.get('R29_PAGE', 'dist/r29-free.html')
TAG = 'dials-%s-%s' % (LAYOUT, THEME)
LOG = os.path.join(FREE, 'logs', TAG + ('' if len(sys.argv) <= 3 else '-' + '-'.join(PARTS)) + '.txt')
lines, wrong, checks = [], [], [0]

STATE = """
const dial = id => { const n = $(id + 'Num'), r = $(id); return { box: n.value, slider: r ? +r.value : null }; };
return { mode: S.mode, group: S.k.group, flat: !!S.flat, size: dial('ballsSize'), rho: dial('ballsRho'), depth: dial('ballsDepth'), grid: S.k.bgrid,
  bt: S.k.bt, brho: S.k.brho, bit: S.k.bit, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', status: $('status').textContent,
  prog: String(L.R.sig || '').split('\\n')[0], failed: String(L.R.failed || ''), bound: S.view.bound };
"""
CUT = 'Here the two spheres of the recipe cut into each other, so the balls run into one another. A smaller size or a smaller second sphere parts them again.'
LUMP = 'Far out everything is filled, so the picture is one lump as large as the Drawing radius.'
FILLED = 'The flat picture is filled completely.'


def say(text):
    lines.append(text); print(text, flush=True)
    with open(LOG, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def st(h):
    h.done()
    return h.js(STATE)


def ok(cond, what):
    checks[0] += 1
    if not cond:
        wrong.append(what)
    return 'OK' if cond else 'WRONG'


def near(a, b, tol=0.006):
    try:
        return abs(float(a) - float(b)) < tol
    except (TypeError, ValueError):
        return False


def typed(h, dial, text):
    h.type('#balls%sNum' % dial, text); return st(h)


def to_balls(h):
    if not h.js("return S.mode === 'k' && S.k.group === 1 && (!$('ballsPart').hidden && vis($('ballsDials')));"):
        if h.js("return vis($('apMenuBtn'));"):
            h.click('#apMenuBtn'); time.sleep(0.3); h.click('#ap-balls')
        else:
            h.click('#kleinGroup1')
    return st(h)


def grid(h, g):
    h.js("const e = $('ballsGrid'); e.value = '%d'; e.dispatchEvent(new Event('change', { bubbles: true })); return 1;" % g)
    return st(h)


def flat(h, on):
    if h.js("return !!S.flat;") != on:
        h.click('#flat')
    return st(h)


def main():
    with Hand(PAGE, SIZE, THEME) as h:
        say('page %s, %s (%s), %s theme' % (PAGE, LAYOUT, SIZE, THEME))
        s = to_balls(h)
        say('the row: size %s, second sphere %s, depth %s, program %s -> %s' % (s['size']['box'], s['rho']['box'], s['depth']['box'], s['prog'],
            ok(near(s['size']['box'], 55.56) and near(s['rho']['box'], 100) and s['prog'] == 'k-balls', 'the row does not open at 55.56 / 100')))

        if 'free' in PARTS:
            say('--- each dial sets its own number and nothing else')
            for text in ('150', '300', '101', '99.99', '2000', '80'):
                s = typed(h, 'Size', text)
                say('size typed %s: size shows %s, second sphere shows %s (rho %r), t %r, program %s -> %s' % (text, s['size']['box'], s['rho']['box'], s['brho'], s['bt'], s['prog'],
                    ok(near(s['size']['box'], text) and s['brho'] == 1 and near(s['rho']['box'], 100), 'typing size %s moved the second sphere' % text)))
            for text in ('62.5', '33.33', '50', '75', '99', '2'):
                before = h.js("return S.k.bt;")
                s = typed(h, 'Rho', text)
                say('second sphere typed %s: shows %s (rho %r), size shows %s, t unchanged %s -> %s' % (text, s['rho']['box'], s['brho'], s['size']['box'], s['bt'] == before,
                    ok(near(s['rho']['box'], text) and s['bt'] == before, 'typing second sphere %s moved the size' % text)))
            typed(h, 'Rho', '40'); typed(h, 'Size', '60')
            seen = h.drag('#ballsSize', 390, moves=14, read=lambda hh: hh.js("return [$('ballsSizeNum').value, $('ballsRhoNum').value, S.k.brho];"))
            s = st(h)
            rhos = sorted(set(str(v[1]) for v in seen)); sizes = [float(v[0]) for v in seen]
            say('size slider dragged from 60 to about 390 with the second sphere at 40: %d readings on the way, size from %.1f to %.1f, the second sphere showed %s throughout; at the end size %s, second sphere %s (rho %r), program %s -> %s'
                % (len(seen), min(sizes), max(sizes), rhos, s['size']['box'], s['rho']['box'], s['brho'], s['prog'], ok(rhos == ['40'] and s['brho'] == 0.4 and float(s['size']['box']) > 380, 'dragging the size moved the second sphere')))
            seen = h.drag('#ballsSize', 'left', moves=10, read=lambda hh: hh.js("return [$('ballsSizeNum').value, $('ballsRhoNum').value];")); s = st(h)
            say('size slider dragged past its left end: size %s, second sphere %s -> %s' % (s['size']['box'], s['rho']['box'], ok(near(s['size']['box'], 2) and near(s['rho']['box'], 40), 'the size slider\'s left end')))
            typed(h, 'Size', '150')
            before = h.js("return S.k.bt;")
            seen = h.drag('#ballsRho', 97, moves=14, read=lambda hh: hh.js("return [$('ballsSizeNum').value, $('ballsRhoNum').value, S.k.bt];")); s = st(h)
            sz = sorted(set(str(v[0]) for v in seen)); rr = [float(v[1]) for v in seen]
            say('second sphere slider dragged from 40 to 97 with the size at 150: %d readings, second sphere from %g to %g (values seen on the way: %s), the size showed %s throughout, t unchanged %s -> %s'
                % (len(seen), min(rr), max(rr), sorted(set(rr))[:12], sz, s['bt'] == before, ok(sz == ['150'] and s['bt'] == before and near(s['rho']['box'], 97), 'dragging the second sphere moved the size')))

        if 'reach' in PARTS:
            say('--- every value from 2 to 100 on the second sphere')
            typed(h, 'Size', '55.56')
            got = []
            for v in (100, 99, 76, 75, 74, 63, 51, 50, 49, 2, 60, 88):
                h.drag('#ballsRho', v); s = st(h); got.append((v, s['rho']['box'], s['brho']))
            bad = [g for g in got if not (near(g[1], g[0]) and abs(g[2] - g[0] / 100.0) < 1e-12)]
            say('slider dragged to 100, 99, 76, 75, 74, 63, 51, 50, 49, 2, 60, 88: the box showed %s -> %s' % ([g[1] for g in got], ok(not bad, 'the second sphere slider does not reach %s' % bad)))
            s = typed(h, 'Rho', '50'); seq = []
            for _ in range(3):
                h.key('ArrowUp'); seq.append(st(h)['rho']['box'])
            say('typed 50, then ArrowUp three times in the box: %s -> %s' % (seq, ok(seq == ['51', '52', '53'], 'ArrowUp from 50 does not go 51, 52, 53')))
            s = typed(h, 'Rho', '100'); seq = []
            for _ in range(3):
                h.key('ArrowDown'); seq.append(st(h)['rho']['box'])
            say('typed 100, then ArrowDown three times in the box: %s -> %s' % (seq, ok(seq == ['99', '98', '97'], 'ArrowDown from 100 does not go 99, 98, 97')))
            h.click('#ballsRho'); time.sleep(0.2); v0 = st(h)['rho']['box']; seq = []
            for kname in ('ArrowLeft', 'ArrowLeft', 'ArrowRight', 'ArrowRight', 'ArrowRight'):
                h.key(kname); seq.append(st(h)['rho']['box'])
            say('a click on the slider (it shows %s), then Left, Left, Right, Right, Right: %s -> %s' % (v0, seq, ok(len(set(seq)) >= 3 and all(abs(float(a) - float(b)) == 1 for a, b in zip([v0] + seq[:-1], seq)), 'the arrow keys on the second sphere slider do not step by 1')))
            s = typed(h, 'Rho', '62.5')
            say('typed 62.5: shows %s, rho %r, program %s -> %s' % (s['rho']['box'], s['brho'], s['prog'], ok(s['rho']['box'] == '62.5' and s['brho'] == 0.625, 'typed 62.5 is not 62.5')))
            s = typed(h, 'Rho', '62.555')
            say('typed 62.555: shows %s, rho %r -> %s' % (s['rho']['box'], s['brho'], ok(near(s['rho']['box'], 62.56, 0.011) and abs(s['brho'] - 0.6256) < 2e-4, 'typed 62.555 is not shown with two decimals')))
            seq = []
            for sel in ('.dial-up', '.dial-up', '.dial-down'):
                h.click('#ballsRhoNum ~ .dial-steps ' + sel); seq.append(st(h)['rho']['box'])
            say('the two small step buttons, from 62.56: up, up, down: %s -> %s' % (seq, ok(seq == ['63', '64', '63'], 'the step buttons of the second sphere do not go to the next whole number')))
            b = h.js("const n = $('ballsRhoNum'); return [n.title, n.closest('.dial').querySelector('.dial-up').title, n.closest('.dial').querySelector('.dial-down').title, $('ballsRhoHelp').textContent, $('ballsSizeHelp').textContent];")
            say('the box says "%s"; the step buttons say "%s" and "%s"' % (b[0], b[1], b[2]))
            say('help, second sphere: %s' % b[3]); say('help, size: %s' % b[4])
            ok('50' not in b[0] and 'jump' not in b[3] and 'made smaller' not in b[4], 'an old word of the jump or of the automatic rule is still on the page')

        if 'limits' in PARTS:
            say('--- typed limits')
            for dial, text, want in (('Size', '5000', 2000), ('Size', '0.2', 1), ('Size', '1', 1), ('Size', '2000', 2000), ('Rho', '1', 2), ('Rho', '250', 100), ('Rho', '0', 2), ('Depth', '0', 1), ('Depth', '5000', 1000), ('Depth', '16', 16)):
                s = typed(h, dial, text)
                got = s[{'Size': 'size', 'Rho': 'rho', 'Depth': 'depth'}[dial]]['box']
                say('%s typed %s: shows %s (t %r, rho %r, depth %r) -> %s' % (dial, text, got, s['bt'], s['brho'], s['bit'], ok(near(got, want), '%s typed %s gives %s, wanted %s' % (dial, text, got, want))))
            typed(h, 'Size', '60'); typed(h, 'Rho', '60'); typed(h, 'Depth', '20')      # (inside every slider's own range, so that each thumb can be moved)
            for sel, end, want in (('#ballsSize', 'right', 400), ('#ballsSize', 'left', 2), ('#ballsRho', 'left', 2), ('#ballsRho', 'right', 100), ('#ballsDepth', 'right', 100), ('#ballsDepth', 'left', 1)):
                h.drag(sel, end); s = st(h); got = s[{'#ballsSize': 'size', '#ballsRho': 'rho', '#ballsDepth': 'depth'}[sel]]['box']
                say('slider %s dragged past its %s end: shows %s -> %s' % (sel, end, got, ok(near(got, want), 'slider %s past %s gives %s' % (sel, end, got))))

        if 'reset' in PARTS:
            say('--- Reset this section')
            typed(h, 'Size', '300'); typed(h, 'Rho', '62.5'); typed(h, 'Depth', '40'); grid(h, 1)
            h.click('#ballsReset button'); s = st(h)
            say('after 300 / 62.5 / 40 / honeycomb, Reset this section: size %s, second sphere %s, depth %s, grid %s, t %r, rho %r, program %s, sentence "%s" -> %s'
                % (s['size']['box'], s['rho']['box'], s['depth']['box'], s['grid'], s['bt'], s['brho'], s['prog'], s['warn'], ok(s['bt'] == 1.4 and s['brho'] == 1 and s['bit'] == 16 and s['grid'] == 0 and s['warn'] == '', 'Reset this section')))

        if 'words' in PARTS:
            say('--- the sentences')
            h.click('#ballsReset button'); st(h)
            W = [('120', '100', False, [CUT, LUMP], ['never ends', 'too long', 'runs out', FILLED]),
                 ('120', '100', True, [CUT], [LUMP, FILLED, 'never ends']),
                 ('150', '100', True, [CUT, FILLED], [LUMP]),
                 ('400', '100', False, [CUT, LUMP], [FILLED]),
                 ('150', '75', False, [CUT, 'The second sphere is now 75 % of the first. Reset this section puts it back to 100.'], ['never ends', 'kiss']),
                 ('300', '50', False, [CUT, 'The second sphere is now 50 % of the first.'], ['buds on a neighbour kiss']),
                 ('100', '100', False, ['At 100 the chain never ends'], [CUT]),
                 ('133.33', '75', False, ['At 133.33 the chain never ends', 'The second sphere is now 75 % of the first.'], [CUT]),
                 ('200', '50', False, ['At 200 the chain never ends', 'The second sphere is now 50 % of the first.'], [CUT, 'buds on a neighbour kiss']),
                 ('80', '50', False, ['The second sphere is now 50 % of the first. Reset this section puts it back to 100.', 'With the second sphere at 50 the buds on a neighbour kiss'], [CUT]),
                 ('80', '75', False, ['The second sphere is now 75 % of the first. Reset this section puts it back to 100.'], [CUT, 'kiss', 'never ends']),
                 ('150', '33.33', False, ['The second sphere is now 33.33 % of the first. Reset this section puts it back to 100.'], [CUT, 'Past 100', 'follows']),
                 ('299', '33.33', False, ['Here the chain is too long for one picture, so Frame it shows a stretch of it.'], [CUT]),
                 ('55.56', '100', False, [], [' '])]
            for size, rho, fl, has, hasnt in W:
                typed(h, 'Size', size); typed(h, 'Rho', rho); flat(h, fl); h.click('#ballsFrame'); s = st(h)
                good = all(x in s['warn'] for x in has) and not any(x in s['warn'] for x in hasnt)
                say('size %s, second sphere %s, %s view (%s): "%s" -> %s' % (size, rho, '2D' if fl else '3D', s['prog'], s['warn'], ok(good, 'the sentence at %s / %s / %s' % (size, rho, '2D' if fl else '3D'))))
            flat(h, False)
            typed(h, 'Size', '55.56'); typed(h, 'Rho', '100'); s = typed(h, 'Depth', '3')
            say('depth 3: "%s" -> %s' % (s['warn'], ok('so few rounds' in s['warn'], 'the sentence for few rounds')))
            typed(h, 'Depth', '16')
            # the Drawing radius sentences: a small Drawing radius with large neighbours that do not fill the far distance, and with a chain
            typed(h, 'Size', '150'); typed(h, 'Rho', '33.33'); h.click('#ballsFrame'); st(h)
            h.js("S.view.bound = 1.2; L.syncControls(); L.touch(); return 1;"); s = st(h)
            say('150 / 33.33 with the Drawing radius set to 1.2: "%s" -> %s' % (s['warn'], ok('cuts the two big neighbours open' in s['warn'], 'the sentence for a Drawing radius that cuts the neighbours')))
            typed(h, 'Size', '90'); typed(h, 'Rho', '100'); h.js("S.view.bound = 2; L.syncControls(); L.touch(); return 1;"); s = st(h)
            say('90 / 100 with the Drawing radius set to 2: "%s" -> %s' % (s['warn'], ok('runs out past the Drawing radius' in s['warn'], 'the sentence for a chain that runs out past the Drawing radius')))
            h.click('#ballsFrame'); st(h)

        if 'frame' in PARTS:
            say('--- Frame it: the middle ball and both neighbours in the picture, every state of both panels')
            PROBE = """
              const p = %r, K2 = 1.05, rN = K2 * p / 200, xN = K2 / 2 + rN, w = $('stage').clientWidth, h = $('stage').clientHeight, asp = w / h;
              const balls = [[0, 0, 0, K2 / 2], [xN, 0, 0, rN], [-xN, 0, 0, rN]];
              if (S.flat) { const hw = S.v2.h * asp / 2, hh = S.v2.h / 2; let worst = 1e9;
                for (const b of balls) worst = Math.min(worst, hw - Math.abs(b[0] - S.v2.x) - b[3], hh - Math.abs(b[1] - S.v2.y) - b[3]);
                return { flat: true, margin: worst / S.v2.h, h: S.v2.h, hmax: S.v2.hmax || null }; }
              // 3D: the cone of each ball against the four sides of the picture (the same test for every ball)
              const b = L.basis(), f = S.view.fov, sub = (u, v) => [u[0] - v[0], u[1] - v[1], u[2] - v[2]], dot = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
              let worst = 1e9;
              for (const c of balls) { const v = sub(c, b.pos), z = dot(v, b.f), x = dot(v, b.right), y = dot(v, b.up), r = c[3];
                const mx = (f * asp * z - Math.abs(x)) / Math.hypot(1, f * asp) - r, my = (f * z - Math.abs(y)) / Math.hypot(1, f) - r;
                worst = Math.min(worst, mx / r, my / r, (z - r) / r); }
              return { flat: false, margin: worst, dist: L.cam.dist, bound: S.view.bound, zmax: S.view.zmax };"""
            for panel, which in ((K.PANEL_NEW, 'new'), (K.PANEL_OLD, 'old')):
                for (name, p, rs, g, depth) in panel:
                    if name == 'X9d':
                        continue
                    rs_txt = '%.2f' % rs if abs(rs - round(rs)) > 1e-9 else '%d' % rs
                    typed(h, 'Size', ('%.2f' % p).rstrip('0').rstrip('.')); typed(h, 'Rho', rs_txt); grid(h, g)
                    out = []
                    for fl in (False, True):
                        flat(h, fl); h.click('#ballsFrame'); s = st(h)
                        a = h.js(PROBE % float(p))
                        out.append(('2D' if fl else '3D', a))
                    good = all(a['margin'] >= 0 for _, a in out)
                    say('%-4s size %s second %s grid %d (%s): 3D the three balls keep %.2f of their own radius clear of the picture\'s sides (eye %.2f away, Drawing radius %.2f); 2D %.3f of the view\'s height clear (view %.3f high) -> %s'
                        % (name, s['size']['box'], s['rho']['box'], g, s['prog'], out[0][1]['margin'], out[0][1]['dist'], out[0][1]['bound'], out[1][1]['margin'], out[1][1]['h'], ok(good, 'Frame it at %s' % name)))
                    flat(h, False)
            grid(h, 0)

        if 'mesh' in PARTS:
            say('--- a 3D model at Y1 and at X1')
            for label, size, rho in (('Y1', '80', '75'), ('X1', '120', '100')):
                typed(h, 'Size', size); typed(h, 'Rho', rho); flat(h, False); h.click('#ballsFrame'); st(h)
                h.js("window.__saved = null; window.squaringLabSaveHook = (name, blob) => { window.__saved = { name, blob }; }; window.squaringLabMeshTest = { cells: 48 }; if ($('secMesh')) $('secMesh').open = true; return 1;")
                if h.js("return vis($('meshDiscard'));"):
                    h.click('#meshDiscard'); time.sleep(0.3)
                h.click('#meshStart'); time.sleep(0.5)
                h.page.wait("!window.squaringLab.meshBusy()", 900); time.sleep(0.4)
                if h.js("return vis($('meshSave'));"):
                    h.click('#meshSave'); time.sleep(1.5)
                r = h.js("""const sv = window.__saved; delete window.squaringLabMeshTest; delete window.squaringLabSaveHook;
                  if (!sv) return { none: true, msg: $('meshMsg') ? $('meshMsg').textContent : '' };
                  const bytes = new Uint8Array(await sv.blob.arrayBuffer()), text = new TextDecoder('latin1').decode(bytes.subarray(0, Math.min(bytes.length, 4000000)));
                  const made = [...new Set([...text.matchAll(/Made from[^\\r\\n]{0,500}/g)].map(m => m[0]))];
                  return { name: sv.name, bytes: bytes.length, made, msg: $('meshMsg') ? $('meshMsg').textContent.slice(0, 300) : '', facts: $('meshFacts') ? $('meshFacts').textContent.slice(0, 400) : '' };""")
                if r.get('none'):
                    say('%s: NO FILE; the page says "%s" -> %s' % (label, r['msg'], ok(False, 'no 3D model at ' + label)))
                else:
                    say('%s: file "%s", %d bytes; it says: %s; the page says "%s" %s -> %s' % (label, r['name'], r['bytes'], json.dumps(r['made'], ensure_ascii=False), r['msg'], r['facts'], ok(r['bytes'] > 2000, 'the 3D model at %s is empty' % label)))
                if h.js("return vis($('meshDiscard'));"):
                    h.click('#meshDiscard'); time.sleep(0.3)

        probs = h.problems()
        say('--- console: %s' % ('no errors or warnings' if not probs else '%d: %s' % (len(probs), probs[:6])))
        ok(not probs, 'console errors or warnings: %s' % probs[:3])
        say('RESULT %s: %d checks, %d wrong%s' % (TAG, checks[0], len(wrong), ': ' + '; '.join(wrong) if wrong else ''))


if __name__ == '__main__':
    main()
