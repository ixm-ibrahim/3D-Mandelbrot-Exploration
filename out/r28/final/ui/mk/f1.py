"""Round 28, dial checker (ui), section 1.4 f: the dials of Balls on balls driven with real input (hand.py).

  python -B out/r28/final/ui/mk/f1.py <wide|phone> <dark|light> [part ...]      -> out/r28/final/ui/logs/f1-<layout>-<theme>.txt
  parts (default all): open ends typed give jump frame leave flat2d export mesh reload deep

Every line of the log is one thing done and what the page then showed. Where docs/ROUND28.md section 1.2 fixes the
answer, the line ends with OK or WRONG (wanted ...). Where the text of 1.2 can be read two ways the line says NOTE.
All input is real (mouse, keys, typed characters) unless the line says "(by script)".
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hand import Hand, ROOT, UI

LAYOUT = sys.argv[1] if len(sys.argv) > 1 else 'wide'
THEME = sys.argv[2] if len(sys.argv) > 2 else 'dark'
PARTS = sys.argv[3:] or ['open', 'ends', 'typed', 'give', 'jump', 'frame', 'leave', 'flat2d', 'export', 'mesh', 'reload', 'deep']
SIZE = {'wide': '1400x950', 'phone': '390x800'}[LAYOUT]
PAGE = 'dist/r28-final.html'
TAG = 'f1-%s-%s' % (LAYOUT, THEME)
LOG = os.path.join(UI, 'logs', TAG + ('' if len(sys.argv) <= 3 else '-' + '-'.join(PARTS)) + '.txt')
SHOTS = 'out/r28/final/ui/shots'
lines, wrong = [], []

STATE = """
const dial = id => { const n = $(id + 'Num'), r = $(id), bx = n.closest('.dial-num'); return { box: n.value, slider: r ? +r.value : null, flag: bx.dataset.flag || '' }; };
return { mode: S.mode, group: S.k.group, flat: !!S.flat, size: dial('ballsSize'), rho: dial('ballsRho'), depth: dial('ballsDepth'), grid: S.k.bgrid,
  bt: S.k.bt, brho: S.k.brho, bit: S.k.bit, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', status: $('status').textContent,
  prog: String(L.R.sig || '').split('\\n')[0], failed: String(L.R.failed || ''), reach: L.ballsReach(), bound: S.view.bound, shown: (!$('ballsPart').hidden && vis($('ballsDials'))) };
"""


def say(text):
    lines.append(text); print(text)
    with open(LOG, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def st(h):
    h.done()
    return h.js(STATE)


def brief(s):
    return ('' if s['mode'] == 'k' and s['group'] == 1 else '[NOT ON SHOW: mode %s, group %s] ' % (s['mode'], s['group'])) + 'size %s (slider %s%s), second sphere %s (slider %s%s), depth %s (slider %s%s) | t %.6g, rho %.6g%s' % (
        s['size']['box'], s['size']['slider'], ', flag ' + s['size']['flag'] if s['size']['flag'] else '',
        s['rho']['box'], s['rho']['slider'], ', flag ' + s['rho']['flag'] if s['rho']['flag'] else '',
        s['depth']['box'], s['depth']['slider'], ', flag ' + s['depth']['flag'] if s['depth']['flag'] else '',
        s['bt'], s['brho'], ' | sentence: ' + s['warn'] if s['warn'] else ' | no sentence')


def check(what, s, want=None, note=None):
    """want: dict of size / rho / depth as the boxes should show them (numbers), or None."""
    verdict = ''
    if want:
        bad = []
        for k, v in want.items():
            if k in ('size', 'rho', 'depth'):
                got = s[k]['box']
                try:
                    ok = abs(float(got) - v) < 0.006
                except ValueError:
                    ok = False
                if not ok:
                    bad.append('%s shows %s, wanted %s' % ({'size': 'size', 'rho': 'second sphere', 'depth': 'depth'}[k], got, v))
            elif k == 'warn_has':
                for piece in ([v] if isinstance(v, str) else v):
                    if piece not in s['warn']:
                        bad.append('the sentence lacks "%s"' % piece)
            elif k == 'warn_none':
                if s['warn']:
                    bad.append('a sentence is shown')
            elif k == 'warn_not':
                if v in s['warn']:
                    bad.append('the sentence has "%s"' % v)
            elif k == 'flag':
                dial, f = v
                if s[dial]['flag'] != f:
                    bad.append('the box is marked "%s", wanted "%s"' % (s[dial]['flag'], f))
            elif k == 't':
                if s['bt'] != v:
                    bad.append('t is %r, wanted exactly %r' % (s['bt'], v))
        verdict = '  -> OK' if not bad else '  -> WRONG: ' + '; '.join(bad)
        if bad:
            wrong.append(what + ': ' + '; '.join(bad))
    if s['failed']:
        verdict += '  PROGRAM FAILED: ' + s['failed']; wrong.append(what + ': a program failed')
    say('%s: %s%s%s' % (what, brief(s), verdict, '  NOTE: ' + note if note else ''))


def reset(h):
    h.click('#ballsReset button'); return st(h)


def typed(h, dial, text, leave=None):
    h.type('#balls%sNum' % dial, text, leave=leave); return st(h)


def to_balls(h):
    """The row in the Approach list, by a real click (the list is opened first, as a user must)."""
    if not h.js("return S.mode === 'k' && S.k.group === 1 && (!$('ballsPart').hidden && vis($('ballsDials')));"):
        if h.js("return vis($('apMenuBtn'));"):
            h.click('#apMenuBtn'); time.sleep(0.3)
            h.click('#ap-balls')
        else:
            h.click('#kleinGroup1')
    return st(h)


def main():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    say('page %s, window %s, theme %s, parts %s, started %s' % (PAGE, SIZE, THEME, ' '.join(PARTS), time.strftime('%H:%M:%S')))
    with Hand(PAGE, SIZE, THEME) as h:
        s0 = h.js("return { mode: S.mode, brho: S.k.brho, bt: S.k.bt, status: $('status').textContent };")
        say('as the page opens: mode %s, t %s, rho %s, status "%s"' % (s0['mode'], s0['bt'], s0['brho'], s0['status']))

        if 'open' in PARTS:
            h.click('#apMenuBtn'); time.sleep(0.3)
            h.hover('#ap-balls'); time.sleep(0.3)
            info = h.js("const b = $('apInfo'); return { head: $('apgh-cousin').textContent, row: $('ap-balls').textContent, title: $('ap-balls').title, info: vis(b) ? [...b.querySelectorAll('p')].map(p => p.textContent) : null };")
            say('the Approach list is open; heading "%s"; row "%s"; its tooltip "%s"; beside it while the mouse is over it: %s' % (info['head'], info['row'], info['title'], json.dumps(info['info'], ensure_ascii=False)))
            h.shot('%s/%s-approach-list-row.png' % (SHOTS, TAG))
            h.click('#ap-balls')
            s = st(h)
            check('one click on the row Balls on balls', s, dict(size=55.56, rho=100, depth=16, warn_none=1, t=1.4))
            say('   mode %s, group %s, program %s, status "%s", panel shown %s' % (s['mode'], s['group'], s['prog'], s['status'], s['shown']))
            if not (s['mode'] == 'k' and s['group'] == 1 and s['shown']):
                wrong.append('the row did not show Balls on balls')
            d = h.js("""const one = id => { const r = $(id), n = $(id + 'Num'); return { slider: [r.min, r.max, r.step], typed: [n.getAttribute('aria-valuemin'), n.getAttribute('aria-valuemax')], tip: n.title }; };
              return { size: one('ballsSize'), rho: one('ballsRho'), depth: one('ballsDepth') };""")
            for k, want in (('size', (['2', '400', '0.1'], ['1', '2000'])), ('rho', (['2', '100', '1'], ['2', '100'])), ('depth', (['1', '100', '1'], ['1', '1000']))):
                ok = d[k]['slider'] == want[0] and d[k]['typed'] == want[1]
                say('   dial %s: slider %s, typed %s, tooltip of the box "%s"  -> %s' % (k, d[k]['slider'], d[k]['typed'], d[k]['tip'], 'OK' if ok else 'WRONG, wanted %s %s' % want))
                if not ok:
                    wrong.append('dial %s has the wrong ends' % k)
            h.shot('%s/%s-as-the-row-gives-it.png' % (SHOTS, TAG))
        else:
            to_balls(h)

        if 'ends' in PARTS:
            say('--- both ends of every dial, by dragging the slider (real mouse)')
            reset(h)
            h.drag('#ballsSize', 'right'); s = st(h)
            check('size slider dragged past its right end', s, dict(size=400, rho=12.5, warn_has=['Past 100', '12.5 % of the first']))
            h.shot('%s/%s-size-400-after-drag-no-frame.png' % (SHOTS, TAG), '#stage')
            h.drag('#ballsSize', 'left'); s = st(h)
            check('size slider dragged past its left end', s, dict(size=2), note='the second sphere is %s now; by the letter of 1.2 point 4 it would still be 12.5 (2 x 0.125 is under 100), the builder lets it follow the size back up to 50' % s['rho']['box'])
            h.shot('%s/%s-size-2-after-drag.png' % (SHOTS, TAG), '#stage')
            s = reset(h)
            check('Reset this section', s, dict(size=55.56, rho=100, depth=16, warn_none=1, t=1.4))
            if s['brho'] != 1:
                wrong.append('after the reset rho is %r' % s['brho'])
            h.drag('#ballsRho', 'left'); s = st(h)
            check('second-sphere slider dragged past its left end', s, dict(size=55.56, rho=2, warn_has='2 % of the first'))
            h.shot('%s/%s-second-sphere-2.png' % (SHOTS, TAG), '#stage')
            h.drag('#ballsRho', 'right'); s = st(h)
            check('second-sphere slider dragged past its right end', s, dict(size=55.56, rho=100, warn_none=1))
            h.drag('#ballsDepth', 'left'); s = st(h)
            check('depth slider dragged past its left end', s, dict(depth=1, warn_has='so few rounds'))
            h.shot('%s/%s-depth-1.png' % (SHOTS, TAG), '#stage')
            h.drag('#ballsDepth', 'right'); s = st(h)
            check('depth slider dragged past its right end', s, dict(depth=100, warn_none=1))
            h.shot('%s/%s-depth-100.png' % (SHOTS, TAG), '#stage')
            # the drop-down, by keys: focus it with a click, then choose with the arrow keys
            opts = h.js("return [...$('ballsGrid').options].map(o => o.textContent);")
            say('Whole numbers offers: %s  -> %s' % (opts, 'OK (unchanged)' if opts == ['Square grid (four-fold)', 'Honeycomb grid (six-fold)', 'A line only (buds only round the flat picture)'] else 'WRONG'))
            for want in (1, 2, 0):
                h.js("const e = $('ballsGrid'); e.value = String(%d); e.dispatchEvent(new Event('change', { bubbles: true })); return 1;" % want)
                s = st(h)
                say('   Whole numbers set to entry %d (by script: the change event of the drop-down): grid %s, program %s, %s' % (want, s['grid'], s['prog'], brief(s)))
            s = reset(h)
            check('Reset this section', s, dict(size=55.56, rho=100, depth=16, warn_none=1, t=1.4))

        if 'typed' in PARTS:
            say('--- typed values past the ends (real keys: click into the box, Ctrl+A, the characters, Enter)')
            for text, want, flag in (('0', 1, 'clamped'), ('1', 1, ''), ('2000', 2000, ''), ('5000', 2000, 'clamped'), ('-5', 1, 'clamped'), ('abc', 55.56, 'invalid'), ('', 55.56, 'invalid'), ('1e3', 1000, ''), ('150,5', 150.5, ''), ('  99.994 ', 99.99, ''), ('100.004', 100, '')):
                reset(h); s = typed(h, 'Size', text)
                check('size: typed "%s"' % text, s, dict(size=want, flag=('size', flag)))
            for text, want, flag in (('0', 2, 'clamped'), ('1', 2, 'clamped'), ('2000', 100, 'clamped'), ('5000', 100, 'clamped'), ('-5', 2, 'clamped'), ('abc', 100, 'invalid'),
                                     ('50', 50, ''), ('51', 50, ''), ('60', 50, ''), ('75', 50, ''), ('75.5', 100, ''), ('76', 100, ''), ('99', 100, ''), ('2', 2, ''), ('33.3', 33.3, ''), ('50.4', 50, '')):
                reset(h); s = typed(h, 'Rho', text)
                check('second sphere: typed "%s"' % text, s, dict(rho=want, size=55.56, flag=('rho', flag)))
            for text, want, flag in (('0', 1, 'clamped'), ('1', 1, ''), ('2000', 1000, 'clamped'), ('5000', 1000, 'clamped'), ('-5', 1, 'clamped'), ('abc', 16, 'invalid'), ('4', 4, ''), ('5', 5, ''), ('2.6', 3, ''), ('1000', 1000, '')):
                reset(h); s = typed(h, 'Depth', text)
                w = dict(depth=want, flag=('depth', flag))
                if want < 5: w['warn_has'] = 'so few rounds'
                else: w['warn_none'] = 1
                check('depth: typed "%s"' % text, s, w)
            reset(h); s = typed(h, 'Size', '150', leave='tab')
            check('size: typed 150 and left the box with the Tab key (no Enter)', s, dict(size=150, rho=33.33))
            reset(h)

        if 'give' in PARTS:
            say('--- the two dials give way to each other (1.2 point 4)')
            reset(h); s = typed(h, 'Size', '101')
            check('size 101 from the start', s, dict(size=101, rho=49.5, warn_has=['Past 100', '49.5 % of the first']), note='1.2 says "at 101 the second sphere drops to 50 %": min(0.5, 50 / 101) is 49.5')
            s = typed(h, 'Size', '150')
            check('then size 150', s, dict(size=150), note='second sphere %s. The bare formula of point 4 would leave 49.5 (150 x 0.495 = 74 is under 100); the description "from 100 on it follows as 50 / p" gives 33.33' % s['rho']['box'])
            reset(h); s = typed(h, 'Size', '150')
            check('size 150 from the start', s, dict(size=150, rho=33.33, warn_has=['Past 100 the second sphere has to be smaller than the first, or the two would cut into each other.', 'It is now 33.33 % of the first.']))
            say('   program %s, status "%s"' % (s['prog'], s['status']))
            s = typed(h, 'Size', '250')
            check('then size 250', s, dict(size=250), note='second sphere %s (bare formula: 33.33 stays, 250 x 0.3333 = 83; "follows": 20)' % s['rho']['box'])
            s = typed(h, 'Size', '80')
            check('then back below 100: size 80', s, dict(size=80), note='second sphere %s. 1.2: "Coming back below 100 does not put rho back by itself"; bare formula: it stays what it was; the builder: 50' % s['rho']['box'])
            if abs(float(s['rho']['box']) - 100) < 0.01:
                wrong.append('coming back below 100 put the second sphere back to 100')
            if 'Reset this section' not in s['warn']:
                say('   NOTE: with the second sphere under 100 and the size under 100 no sentence names "Reset this section"')
            s = reset(h)
            check('Reset this section', s, dict(size=55.56, rho=100, depth=16, warn_none=1, t=1.4))
            s = typed(h, 'Rho', '30')
            check('second sphere 30 set on its own dial', s, dict(size=55.56, rho=30, warn_has='30 % of the first'))
            s = typed(h, 'Size', '200')
            check('then size 200 (200 x 0.30 = 60, nothing has to give)', s, dict(size=200, rho=30, warn_has='Past 100'))
            s = typed(h, 'Size', '400')
            check('then size 400 (400 x 0.30 = 120: the second sphere gives way to min(0.5, 50 / 400))', s, dict(size=400, rho=12.5))
            reset(h); s = typed(h, 'Size', '300')
            check('size 300 from the start', s, dict(size=300, rho=16.67))
            s = typed(h, 'Rho', '40')
            check('then second sphere 40 (300 x 0.40 = 120: the size gives way to 50 / 0.40)', s, dict(size=125, rho=40))
            s = typed(h, 'Rho', '100')
            check('then second sphere back to 100 (the size gives way to 50)', s, dict(size=50, rho=100, warn_none=1))
            reset(h); typed(h, 'Rho', '50'); s = typed(h, 'Size', '200')
            check('second sphere 50, then size 200 (200 x 0.5 = 100: the two spheres touch)', s, dict(size=200, rho=50, warn_has='At 200 the chain never ends'))
            h.shot('%s/%s-touch-rho50-size200-no-frame.png' % (SHOTS, TAG), '#stage')
            s = typed(h, 'Size', '200.1')
            check('then size 200.1 (just past touching)', s, dict(size=200.1, rho=24.99))
            reset(h); typed(h, 'Rho', '50'); typed(h, 'Size', '80'); s = typed(h, 'Rho', '100')
            check('second sphere 50, size 80, second sphere 100 (80 is under 100: nothing gives way)', s, dict(size=80, rho=100, warn_none=1))
            reset(h); s = typed(h, 'Size', '100')
            V20 = 'At 100 the chain never ends, so the picture shows a stretch of it, and the balls stand so close that they read as one bar with round holes; where the depth of the search runs out, the far balls and the places where two balls kiss come out swollen.'
            check('size 100 with two equal spheres', s, dict(size=100, rho=100))
            say('   the sentence is Version 20\'s word for word: %s' % ('yes  -> OK' if s['warn'] == V20 else 'NO  -> WRONG'))
            if s['warn'] != V20:
                wrong.append('the sentence at 100 is not Version 20\'s')
            h.click('#ballsSizeNum'); h.key('ArrowUp'); s = st(h)
            check('then the Arrow-up key in the size box (one step of 0.1 past 100)', s, dict(size=100.1, rho=49.95))
            h.key('ArrowDown'); s = st(h)
            check('then Arrow-down (back to 100)', s, dict(size=100), note='the second sphere is %s; the two spheres no longer touch, the picture at 100 is not the one of a moment ago' % s['rho']['box'])
            # a second sphere set by hand, then the size taken to where they touch and past
            reset(h); typed(h, 'Rho', '25'); s = typed(h, 'Size', '400')
            check('second sphere 25, size 400 (touching)', s, dict(size=400, rho=25, warn_has='At 400 the chain never ends'))
            s = typed(h, 'Size', '2000')
            check('then size 2000', s, dict(size=2000, rho=2.5))
            s = typed(h, 'Rho', '2')
            check('then second sphere 2', s, dict(size=2000, rho=2))
            s = typed(h, 'Rho', '50')
            check('then second sphere 50 (2000 x 0.5 = 1000: the size gives way to 100)', s, dict(size=100, rho=50))
            # the same value typed again on the second sphere's own dial: does it still follow the size?
            reset(h); typed(h, 'Size', '150'); typed(h, 'Rho', '33.33'); s = typed(h, 'Size', '200')
            check('size 150 (second sphere 33.33 by itself), 33.33 typed into the second sphere\'s own box, then size 200', s, dict(size=200),
                  note='second sphere %s: the hand typed 33.33 on its own dial, which "wins" by point 4, yet %s' % (s['rho']['box'], 'it was kept' if abs(float(s['rho']['box']) - 33.33) < 0.01 else 'it went on following the size (the box held that number already, so the page took it as nothing typed)'))
            reset(h)

        if 'jump' in PARTS:
            say('--- the jump between 50 and 100 of the second sphere')
            reset(h)
            box = lambda hh: hh.js("return [$('ballsRhoNum').value, +$('ballsRho').value, S.k.brho, $('ballsSizeNum').value];")
            seen = h.drag('#ballsRho', 66, moves=10, hold=True, read=box)
            say('second-sphere slider dragged down from 100 towards 66, button still held; box / thumb / rho after each move: %s' % ' '.join('%s/%g/%g' % (a, b, c) for a, b, c, _ in seen))
            mid = box(h); h.release(); s = st(h)
            check('let go at thumb %g' % mid[1], s, dict(rho=50 if mid[1] <= 75 else 100, size=55.56))
            say('   the thumb after letting go stands at %s' % s['rho']['slider'])
            seen = h.drag('#ballsRho', 90, moves=10, hold=True, read=box)
            say('dragged up from 50 towards 90, held: %s' % ' '.join('%s/%g/%g' % (a, b, c) for a, b, c, _ in seen))
            mid = box(h); h.release(); s = st(h)
            check('let go at thumb %g' % mid[1], s, dict(rho=100 if mid[1] > 75 else 50, size=55.56))
            say('   the thumb after letting go stands at %s' % s['rho']['slider'])
            h.drag('#ballsRho', 75); s = st(h)
            check('slider let go at 75', s, dict(rho=50)) if abs(s['rho']['slider'] - 50) < 1e-9 or True else None
            h.drag('#ballsRho', 100); st(h)
            h.drag('#ballsRho', 76); s = st(h)
            say('slider aimed at 76 from 100 and let go: second sphere %s, thumb %s' % (s['rho']['box'], s['rho']['slider']))
            # keys on the slider: give it the focus by pressing its thumb
            reset(h)
            x, y, _ = h.thumb('#ballsRho'); h.click_at(x, y); s = st(h)
            say('pressed the thumb at 100 to give the slider the focus: %s; focus on %s' % (brief(s), h.js("return document.activeElement.id;")))
            for keyname, want in (('ArrowLeft', 50), ('ArrowLeft', 49), ('ArrowRight', 50), ('ArrowRight', 100), ('ArrowRight', 100), ('ArrowDown', 50), ('ArrowUp', 100), ('PageDown', 50), ('PageUp', 100), ('Home', 2), ('ArrowLeft', 2), ('End', 100)):
                h.key(keyname); s = st(h)
                check('slider, key %s' % keyname, s, dict(rho=want, size=55.56))
            # keys in the typed box
            reset(h); h.click('#ballsRhoNum')
            for keyname, shift, want in (('ArrowDown', False, 50), ('ArrowDown', False, 49), ('ArrowUp', False, 50), ('ArrowUp', False, 100), ('ArrowUp', False, 100), ('ArrowDown', True, 50), ('ArrowDown', True, 40), ('ArrowUp', True, 50), ('ArrowUp', True, 100), ('PageDown', False, 50), ('PageUp', False, 100)):
                h.key(keyname, shift=shift); s = st(h)
                check('typed box, key %s%s' % ('Shift+' if shift else '', keyname), s, dict(rho=want, size=55.56))
            # the two small step buttons
            reset(h)
            for btn, want in (('down', 50), ('down', 49), ('up', 50), ('up', 100), ('up', 100)):
                h.click('#ballsRhoNum ~ .dial-steps .dial-%s' % btn); s = st(h)
                check('step button %s' % btn, s, dict(rho=want, size=55.56))
            # the jump while the size is past 100: second sphere 50 -> 100 by one arrow must take the size along
            reset(h); typed(h, 'Size', '150'); h.click('#ballsRhoNum'); h.key('ArrowUp'); s = st(h)
            check('size 150 (second sphere 33.33), Arrow-up in its box (the arrows of this dial go to the next whole number)', s, dict(rho=34, size=150))
            typed(h, 'Rho', '50'); h.click('#ballsRhoNum'); h.key('ArrowUp'); s = st(h)
            check('second sphere 50 at size 150, Arrow-up: across the gap to 100, and the size gives way to 50', s, dict(rho=100, size=50, warn_none=1))
            # a half-typed number and an arrow
            reset(h); h.click('#ballsRhoNum'); h.key('a', ctrl=True); h.chars('60'); h.key('ArrowUp'); s = st(h)
            check('"60" typed into the box (no Enter) and then Arrow-up', s, None, note='second sphere %s' % s['rho']['box'])
            reset(h)

        if 'frame' in PARTS:
            say('--- Frame it at 55.56, 150, 400 (and what a drag without it leaves)')
            PROBE = """
              const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0, left = 0, right = 0;
              for (let i = 0; i < 29; i++) for (let j = 0; j < 21; j++) { const hit = !!L.pick(w * (i + 0.5) / 29, h * (j + 0.5) / 21); if (hit) { n++; if (i === 0 || j === 0 || i === 28 || j === 20) ring++; if (i === 0) left++; if (i === 28) right++; } }
              // the two ends of the chain on the screen, if the camera can say where they are
              return { probes: 29 * 21, hits: n, onTheRim: ring, reach: L.ballsReach(), bound: S.view.bound, dist: L.cam.dist, v2h: S.v2.h, flat: !!S.flat, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', status: $('status').textContent };"""
            for p in ('55.56', '150', '400'):
                reset(h); typed(h, 'Size', p)
                a = h.js(PROBE)
                h.shot('%s/%s-size-%s-typed-before-frame.png' % (SHOTS, TAG, p), '#stage')
                h.click('#ballsFrame'); s = st(h); b = h.js(PROBE)
                h.shot('%s/%s-size-%s-framed-3d.png' % (SHOTS, TAG, p), '#stage')
                say('size %s typed, no Frame it: %d of %d probes hit, %d on the rim of the picture; reach %.3f, Drawing radius %.3f; sentence "%s"' % (p, a['hits'], a['probes'], a['onTheRim'], a['reach'], a['bound'], a['warn']))
                ok = b['onTheRim'] == 0 and b['bound'] >= b['reach'] and b['hits'] > 0
                say('size %s, Frame it: %d probes hit, %d on the rim; reach %.3f, Drawing radius %.3f, camera distance %.3f; sentence "%s"  -> %s' % (p, b['hits'], b['onTheRim'], b['reach'], b['bound'], b['dist'], b['warn'], 'OK (the whole chain is in the picture)' if ok else 'WRONG: the chain is not whole in the picture'))
                if not ok:
                    wrong.append('Frame it at %s does not show the whole chain' % p)
                h.click('#flat'); s = st(h)
                h.click('#ballsFrame'); s = st(h)
                c = h.js("""const N = 240, side = S.v2.h, asp = $('stage').clientWidth / $('stage').clientHeight; let rim = 0, inside = 0;
                  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) { const x = S.v2.x + side * asp * ((i + 0.5) / N - 0.5), y = S.v2.y + side * ((j + 0.5) / N - 0.5); if (L.ballsInside(x, y, +S.cut || 0)) { inside++; if (i === 0 || j === 0 || i === N - 1 || j === N - 1) rim++; } }
                  return { inside, rim, h: side, x: S.v2.x, y: S.v2.y, reach: L.ballsReach(), halfw: side * asp / 2, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', status: $('status').textContent, cut: S.cut };""")
                h.shot('%s/%s-size-%s-framed-2d.png' % (SHOTS, TAG, p), '#stage')
                ok2 = c['rim'] == 0 and c['halfw'] >= c['reach'] and c['inside'] > 0
                say('size %s, 2D view, Frame it: the view is %.3f high, half its width %.3f, reach %.3f; of 240 x 240 points of the view %d are inside, %d on its rim; sentence "%s"  -> %s' % (p, c['h'], c['halfw'], c['reach'], c['inside'], c['rim'], c['warn'], 'OK' if ok2 else 'WRONG: the chain is not whole in the 2D view'))
                if not ok2:
                    wrong.append('Frame it at %s, 2D view, does not show the whole chain' % p)
                h.click('#flat'); st(h)
            # the drag a user makes first: from the start view to 150, 300, 400, never pressing Frame it
            reset(h); h.click('#ballsFrame'); st(h)
            for p in (150, 300):
                h.drag('#ballsSize', p); s = st(h); a = h.js(PROBE)
                h.shot('%s/%s-dragged-to-%d-no-frame.png' % (SHOTS, TAG, p), '#stage')
                say('size slider dragged to about %d (it shows %s), Frame it not pressed: %d probes hit, %d on the rim; reach %.3f, Drawing radius %.3f; sentence "%s"' % (p, s['size']['box'], a['hits'], a['onTheRim'], a['reach'], a['bound'], a['warn']))
            reset(h); h.click('#ballsFrame'); st(h)

        if 'leave' in PARTS:
            say('--- leaving and coming back')
            reset(h); typed(h, 'Size', '150'); typed(h, 'Depth', '20'); s = st(h)
            check('set: size 150, depth 20', s, dict(size=150, rho=33.33, depth=20))
            h.click('#mode-m'); h.done()
            a = h.js("return { mode: S.mode, status: $('status').textContent, shown: (!$('ballsPart').hidden && vis($('ballsDials'))), prog: String(L.R.sig || '').split('\\n')[0] };")
            say('Show: Mandelbrot (real click): mode %s, the Balls part shown %s, status "%s"' % (a['mode'], a['shown'], a['status']))
            h.shot('%s/%s-left-for-mandelbrot.png' % (SHOTS, TAG), '#stage')
            h.click('#mode-k'); s = st(h)
            check('Show: Kleinian again', s, dict(size=150, rho=33.33, depth=20, warn_has='33.33 % of the first'))
            say('   group %s, program %s, status "%s"' % (s['group'], s['prog'], s['status']))
            h.click('#mode-j'); h.done()
            h.click('#apMenuBtn'); time.sleep(0.4); h.click('#rules .rule[data-ap="bulb"] .name'); h.done()      # (the name in the list, as a finger does; the round mark itself is too small a thing to aim at on a phone)
            a = h.js("return { mode: S.mode, ap: L.APPROACHES[S.approach].id, status: $('status').textContent };")
            say('Show: Julia, then the approach "%s" from the Approach list: mode %s, status "%s"' % (a['ap'], a['mode'], a['status']))
            h.click('#apMenuBtn'); time.sleep(0.3); h.click('#ap-balls'); s = st(h)
            check('back by the row in the Approach list', s, dict(size=150, rho=33.33, depth=20, warn_has='33.33 % of the first'))
            a = h.js("const w = $('stage').clientWidth, hh = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 29; i++) for (let j = 0; j < 21; j++) { const hit = !!L.pick(w * (i + 0.5) / 29, hh * (j + 0.5) / 21); if (hit) { n++; if (i === 0 || j === 0 || i === 28 || j === 20) ring++; } } return [n, ring, L.ballsReach(), S.view.bound];")
            say('   the row frames the camera: %d probes hit, %d on the rim, reach %.3f, Drawing radius %.3f  -> %s' % (a[0], a[1], a[2], a[3], 'OK' if a[1] == 0 and a[3] >= a[2] else 'WRONG'))
            if not (a[1] == 0 and a[3] >= a[2]):
                wrong.append('the row at 150 does not frame the whole chain')
            h.shot('%s/%s-back-by-the-row-150.png' % (SHOTS, TAG), '#stage')
            h.click('#kleinGroup0'); h.done()
            a = h.js("return { group: S.k.group, status: $('status').textContent, shown: (!$('ballsPart').hidden && vis($('ballsDials'))), old: vis($('kleinOld')), warnOld: vis($('kleinWarn')) ? $('kleinWarn').textContent : '', prog: String(L.R.sig || '').split('\\n')[0] };")
            say('Group: Pearls between two walls (real click): group %s, Balls part shown %s, old part shown %s, program %s, old group\'s warning "%s", status "%s"' % (a['group'], a['shown'], a['old'], a['prog'], a['warnOld'], a['status']))
            h.click('#kleinGroup1'); s = st(h)
            check('Group: Balls on balls again', s, dict(size=150, rho=33.33, depth=20, warn_has='33.33 % of the first'))
            h.shot('%s/%s-back-by-the-group-choice-150.png' % (SHOTS, TAG), '#stage')
            # Reset everything, then the row
            h.click('#resetAll'); h.done()
            a = h.js("return { mode: S.mode, bt: S.k.bt, brho: S.k.brho, bit: S.k.bit, group: S.k.group };")
            say('Reset everything: mode %s, group %s, t %r, rho %r, depth %r  -> %s' % (a['mode'], a['group'], a['bt'], a['brho'], a['bit'], 'OK' if (a['bt'], a['brho'], a['bit'], a['group']) == (1.4, 1, 16, 0) else 'WRONG'))
            if (a['bt'], a['brho'], a['bit'], a['group']) != (1.4, 1, 16, 0):
                wrong.append('Reset everything left t %r rho %r depth %r group %r' % (a['bt'], a['brho'], a['bit'], a['group']))
            s = to_balls(h)
            check('the row after Reset everything', s, dict(size=55.56, rho=100, depth=16, warn_none=1, t=1.4))
            # does the size dial still "follow" after Reset everything? size 60 must leave the second sphere at 100
            s = typed(h, 'Size', '60')
            check('then size 60', s, dict(size=60, rho=100, warn_none=1))
            reset(h)

        if 'flat2d' in PARTS:
            say('--- the 2D view')
            for p, rho in (('150', None), ('300', None), ('150', '50')):
                reset(h)
                if rho: typed(h, 'Rho', rho)
                typed(h, 'Size', p); h.click('#ballsFrame'); st(h)
                h.click('#flat'); st(h); h.click('#ballsFrame'); s = st(h)
                r = h.js("""const N = 200, side = S.v2.h, snap = L.takeSnapshot(), a = await L.sampleSlice(snap, S.v2.x, S.v2.y, side, +S.cut || 0, N); L.releaseSnapshot(snap);
                  let bad = 0, inside = 0; for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) { const x = S.v2.x + side * ((i + 0.5) / N - 0.5), y = S.v2.y + side * ((j + 0.5) / N - 0.5), d = a[4 * (j * N + i) + 3], tw = L.ballsInside(x, y, +S.cut || 0); if (tw) inside++; if ((!(d > 0)) !== tw) bad++; }
                  return { bad, inside, side, label: $('flatZ') ? $('flatZ').textContent : '', status: $('status').textContent };""")
                say('size %s%s, 2D view, framed: %s; the picture\'s own number against the twin at 200 x 200 points of the view (%d inside): %d differ; "%s"; status "%s"  -> %s' % (
                    p, ', second sphere ' + rho if rho else '', brief(s), r['inside'], r['bad'], r['label'], r['status'], 'OK' if r['bad'] <= 2 else 'WRONG'))
                if r['bad'] > 2:
                    wrong.append('2D view at %s: %d of 40000 verdicts differ from the twin' % (p, r['bad']))
                h.shot('%s/%s-2d-size-%s%s.png' % (SHOTS, TAG, p, '-rho' + rho if rho else ''), '#stage')
                h.click('#flat'); st(h)
            reset(h)

        if 'export' in PARTS:
            say('--- the picture export at 150 (the page\'s own buttons, real clicks; the file is caught by the page\'s test hook)')
            reset(h); typed(h, 'Size', '150'); h.click('#ballsFrame'); st(h)
            h.shot('%s/%s-export-150-on-screen.png' % (SHOTS, TAG), '#view')
            h.js("window.__saved = null; window.squaringLabSaveHook = (name, blob) => { window.__saved = { name, blob }; }; for (const d of document.querySelectorAll('details.sec')) if (d.contains($('exportPanel'))) d.open = true; return 1;")
            if h.js("return vis($('exportDiscard'));"):
                h.click('#exportDiscard'); time.sleep(0.3)
            h.click('#exportStart')
            ok = h.page.wait("!window.squaringLab.exportBusy()", 900); time.sleep(0.5)
            if h.js("return vis($('exportSave'));"):
                h.click('#exportSave'); time.sleep(1.0)
            r = h.js("""const sv = window.__saved; if (!sv) return { none: true, msg: $('exportMsg') ? $('exportMsg').textContent : '' };
              const bmp = await createImageBitmap(sv.blob), c = document.createElement('canvas'); c.width = bmp.width; c.height = bmp.height; const g = c.getContext('2d'); g.drawImage(bmp, 0, 0);
              const d = g.getImageData(0, 0, c.width, c.height).data; let fg = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - d[0]) + Math.abs(d[i + 1] - d[1]) + Math.abs(d[i + 2] - d[2]) > 24) fg++;
              const v = $('view'), t = document.createElement('canvas'); t.width = v.width; t.height = v.height;
              const buf = new Uint8Array(await sv.blob.arrayBuffer()); let b64 = ''; for (let i = 0; i < buf.length; i += 30000) b64 += String.fromCharCode.apply(null, buf.subarray(i, i + 30000));
              window.__b64 = btoa(b64);
              return { name: sv.name, bytes: sv.blob.size, w: c.width, h: c.height, share: fg / (c.width * c.height), msg: $('exportMsg') ? $('exportMsg').textContent : '', facts: $('exportFacts') ? $('exportFacts').textContent : '', view: [v.width, v.height] };""")
            if r.get('none'):
                say('NO FILE reached the save hook; the page says "%s"  -> WRONG' % r['msg']); wrong.append('the picture export gave no file')
            else:
                import base64
                b64 = h.js("return window.__b64;")
                with open(os.path.join(ROOT, SHOTS, TAG + '-export-150-file.png'), 'wb') as f:
                    f.write(base64.b64decode(b64))
                say('saved file "%s", %d bytes, %d x %d, %.1f %% of it not background; the page says "%s"; facts "%s"' % (r['name'], r['bytes'], r['w'], r['h'], 100 * r['share'], r['msg'][:200], r['facts'][:300]))
            h.js("delete window.squaringLabSaveHook; return 1;")
            reset(h)

        if 'mesh' in PARTS:
            say('--- the sentence of a saved 3D model (the page\'s own buttons; 48 cells through the page\'s test switch; the file is caught by the test hook)')
            for label, steps in (('the start (55.56, two equal spheres)', []), ('size 150', [('Size', '150')]), ('second sphere 50, size 55.56', [('Rho', '50')]), ('second sphere 25, size 300, honeycomb, depth 12', [('Rho', '25'), ('Size', '300'), ('Depth', '12'), 'hex'])):
                reset(h)
                for stp in steps:
                    if stp == 'hex':
                        h.js("const e = $('ballsGrid'); e.value = '1'; e.dispatchEvent(new Event('change', { bubbles: true })); return 1;")
                    else:
                        typed(h, stp[0], stp[1])
                h.click('#ballsFrame'); st(h)
                h.js("window.__saved = null; window.squaringLabSaveHook = (name, blob) => { window.__saved = { name, blob }; }; window.squaringLabMeshTest = { cells: 48 }; if ($('secMesh')) $('secMesh').open = true; return 1;")
                if h.js("return vis($('meshDiscard'));"):
                    h.click('#meshDiscard'); time.sleep(0.3)          # a finished model is on show: it must be discarded before another can be made
                h.click('#meshStart'); time.sleep(0.5)
                h.page.wait("!window.squaringLab.meshBusy()", 900); time.sleep(0.4)
                if h.js("return vis($('meshSave'));"):
                    h.click('#meshSave'); time.sleep(1.2)
                r = h.js("""const sv = window.__saved; delete window.squaringLabMeshTest; delete window.squaringLabSaveHook;
                  if (!sv) return { none: true, msg: $('meshMsg') ? $('meshMsg').textContent : '' };
                  const bytes = new Uint8Array(await sv.blob.arrayBuffer()), text = new TextDecoder('latin1').decode(bytes.subarray(0, Math.min(bytes.length, 4000000)));
                  const made = [...new Set([...text.matchAll(/Made from[^\\r\\n]{0,500}/g)].map(m => m[0]))];
                  return { name: sv.name, bytes: bytes.length, made, msg: $('meshMsg') ? $('meshMsg').textContent.slice(0, 300) : '', facts: $('meshFacts') ? $('meshFacts').textContent.slice(0, 400) : '' };""")
                if r.get('none'):
                    say('%s: NO FILE; the page says "%s"  -> WRONG' % (label, r['msg'])); wrong.append('mesh export gave no file at ' + label)
                else:
                    say('%s: file "%s", %d bytes; it says: %s; the page says "%s" %s' % (label, r['name'], r['bytes'], json.dumps(r['made'], ensure_ascii=False), r['msg'], r['facts']))
            reset(h)

        if 'reload' in PARTS:
            say('--- reload of the page')
            reset(h); typed(h, 'Size', '150'); s = st(h)
            h.reload()
            a = h.js("return { mode: S.mode, group: S.k.group, bt: S.k.bt, brho: S.k.brho, bit: S.k.bit, status: $('status').textContent, shown: (!$('ballsPart').hidden && vis($('ballsDials'))) };")
            say('size 150, then the page loaded again: mode %s, group %s, t %r, rho %r, depth %r, Balls part shown %s, status "%s"  -> %s' % (a['mode'], a['group'], a['bt'], a['brho'], a['bit'], a['shown'], a['status'], 'OK (the page opens as new; it keeps nothing between visits, as on Version 20)' if (a['bt'], a['brho'], a['bit']) == (1.4, 1, 16) else 'WRONG'))
            s = to_balls(h)
            check('the row after the reload', s, dict(size=55.56, rho=100, depth=16, warn_none=1, t=1.4))
            s = typed(h, 'Size', '80')
            check('then size 80', s, dict(size=80, rho=100, warn_none=1))
            reset(h)

        if 'deep' in PARTS:
            say('--- the deepest search and the fewest rounds')
            for label, steps in (('size 100, depth 1000', [('Size', '100'), ('Depth', '1000')]), ('second sphere 50, size 200, depth 1000', [('Rho', '50'), ('Size', '200'), ('Depth', '1000')]), ('size 150, depth 1000', [('Size', '150'), ('Depth', '1000')]),
                                 ('depth 1', [('Depth', '1')]), ('depth 2', [('Depth', '2')]), ('depth 3', [('Depth', '3')]), ('depth 4', [('Depth', '4')]), ('size 150, depth 2', [('Size', '150'), ('Depth', '2')])):
                reset(h)
                for d, v in steps[:-1]:
                    typed(h, d, v)
                h.click('#ballsFrame'); st(h)
                t0 = time.time(); s = typed(h, steps[-1][0], steps[-1][1]); dt = time.time() - t0
                name = label.replace(' ', '-').replace(',', '')
                h.shot('%s/%s-%s.png' % (SHOTS, TAG, name), '#stage')
                say('%s: finished within %.1f s of the last key (the wait itself costs about 0.5 s); %s; status "%s"' % (label, dt, brief(s), s['status']))
            reset(h)

        if 'extras' in PARTS:
            from f1_extras import extras
            extras(h, say, check, st, reset, typed, to_balls, brief, wrong, SHOTS, TAG)

        probs = h.problems()
        say('--- console: %s' % ('no console errors or warnings' if not probs else '%d PROBLEM(S): ' % len(probs) + ' || '.join(p[:400] for p in probs[:12])))
        if probs:
            wrong.append('console problems: %d' % len(probs))
    say('=== %d line(s) marked WRONG%s' % (len(wrong), ': ' + ' | '.join(wrong) if wrong else ''))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        say('THE SCRIPT STOPPED: ' + repr(e)); say(traceback.format_exc())
        say('=== so far %d line(s) marked WRONG: %s' % (len(wrong), ' | '.join(wrong)))
        sys.exit(1)
