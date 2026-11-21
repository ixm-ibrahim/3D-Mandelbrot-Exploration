"""Round 28, Track A, the final checker: the small defects the checkers reported (D2 to D7, E3, the sentence of E1),
gone through once more on dist/r28-final.html with REAL input (the dial checker's hand.py: mouse, keys, typed characters).
This script is mine; it does not use the fixer's small.py.

  python -B out/r28/final/mk/small7.py <wide|phone> [dark|light]   -> out/r28/final/logs/small7-<layout>.txt, pictures small7-*.png

Every line: what was done, then what the boxes show, what the state holds and the sentences under the note.
Nothing is judged here except where a line ends in OK / WRONG; the notes judge the rest from the lines.
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'ui', 'mk'))
from hand import Hand, ROOT

LAYOUT = sys.argv[1] if len(sys.argv) > 1 else 'wide'
THEME = sys.argv[2] if len(sys.argv) > 2 else 'dark'
SIZE = {'wide': '1400x950', 'phone': '390x800'}[LAYOUT]
PAGE = 'dist/r28-final.html'
LOG = os.path.join(FINAL, 'logs', 'small7-%s%s.txt' % (LAYOUT, os.environ.get('SMALL7_TAG', '')))
PICS = 'out/r28/final/shots'
lines, wrong = [], []

STATE = """
const box = id => $(id + 'Num').value;
const w = $('ballsWarn');
return { size: box('ballsSize'), rho: box('ballsRho'), depth: box('ballsDepth'), bt: S.k.bt, brho: S.k.brho, bit: S.k.bit, grid: S.k.bgrid, flat: !!S.flat,
  warn: vis(w) ? w.textContent : '', warnH: vis(w) ? Math.round(w.getBoundingClientRect().height) : 0, reach: L.ballsReach(), bound: S.view.bound,
  prog: String(L.R.sig || '').split('\\n')[0], failed: String(L.R.failed || ''), status: $('status').textContent, mode: S.mode, group: S.k.group };
"""


def say(t):
    lines.append(t); print(t, flush=True)
    with open(LOG, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def st(h):
    h.done(); return h.js(STATE)


def show(what, s, verdict=''):
    say('%s\n      size %s | second sphere %s | depth %s | t %.8g rho %.8g | 2D %s | program %s | reach %s | Drawing radius %s\n      sentences (%d characters, %d px high): %s%s'
        % (what, s['size'], s['rho'], s['depth'], s['bt'], s['brho'], s['flat'], s['prog'], ('%.2f' % s['reach']) if isinstance(s['reach'], (int, float)) else s['reach'], s['bound'],
           len(s['warn']), s['warnH'], s['warn'] or '(none)', ('\n      -> ' + verdict) if verdict else ''))
    if s['failed']:
        say('      A PROGRAM FAILED: ' + s['failed']); wrong.append(what + ': program failed')


def judge(ok, text):
    if not ok:
        wrong.append(text)
    return ('OK: ' if ok else 'WRONG: ') + text


def reset(h):
    h.click('#ballsReset button'); return st(h)


def typed(h, dial, text, leave=None):
    h.type('#balls%sNum' % dial, text, leave=leave); return st(h)


def to_balls(h):
    if not h.js("return S.mode === 'k' && S.k.group === 1 && (!$('ballsPart').hidden && vis($('ballsDials')));"):
        if h.js("return vis($('apMenuBtn'));"):
            h.click('#apMenuBtn'); time.sleep(0.3); h.click('#ap-balls')
        else:
            h.click('#kleinGroup1')
    return st(h)


def flat(h, on):
    if h.js("return !!S.flat;") != on:
        h.click('#flat')
    return st(h)


def main():
    os.makedirs(os.path.join(ROOT, PICS), exist_ok=True)
    say('page %s, window %s, theme %s, started %s' % (PAGE, SIZE, THEME, time.strftime('%H:%M:%S')))
    with Hand(PAGE, SIZE, THEME) as h:
        s = to_balls(h); show('the row Balls on balls', s, judge(s['size'] == '55.56' and s['rho'] == '100' and s['depth'] == '16' and s['bt'] == 1.4 and not s['warn'], 'the entry opens as on Version 20 (55.56 / 100 / 16, t exactly 1.4, no sentence)'))

        say('\n--- D2: touching "within rounding" (second sphere 33.33, size 300)')
        reset(h); typed(h, 'Rho', '33.33'); s = typed(h, 'Size', '300'); show('typed second sphere 33.33, then size 300', s, judge('never ends' in s['warn'], 'the "never ends" sentence is shown in 3D'))
        h.click('#ballsFrame'); s = st(h); show('Frame it', s, judge('never ends' in s['warn'] and 'Drawing radius' not in s['warn'], 'after Frame it: "never ends", and nothing about the Drawing radius'))
        h.shot('%s/small7-%s-d2-3d.png' % (PICS, LAYOUT), '#stage')
        s = flat(h, True); show('the 2D view', s, judge('never ends' in s['warn'], 'the "never ends" sentence is shown in the 2D view'))
        h.click('#ballsFrame'); st(h); h.shot('%s/small7-%s-d2-2d.png' % (PICS, LAYOUT), '#stage')
        flat(h, False)
        reset(h); typed(h, 'Rho', '50'); s = typed(h, 'Size', '199.9'); show('for comparison: second sphere 50, size 199.9 (not touching as shown: 50 x 199.9 = 9995)', s, judge('never ends' not in s['warn'], 'no "never ends" at 199.9 / 50'))
        reset(h); typed(h, 'Rho', '25'); s = typed(h, 'Size', '400'); show('true touching: second sphere 25, size 400', s, judge('At 400 the chain never ends' in s['warn'], '"At 400 the chain never ends"'))

        say('\n--- D3: a number typed again into the second sphere\'s own box')
        reset(h); s = typed(h, 'Size', '150'); show('typed size 150', s)
        s = typed(h, 'Rho', '33.33'); show('typed 33.33 into the second sphere (the number it shows already), Enter', s)
        s = typed(h, 'Size', '200'); show('typed size 200', s, judge(s['rho'] == '33.33', 'the second sphere stays 33.33 (200 x 33.33 is under 100 x 100)'))
        reset(h); typed(h, 'Size', '150'); s = typed(h, 'Rho', '33.33', leave='tab'); s = typed(h, 'Size', '200'); show('the same, leaving the box with Tab instead of Enter', s, judge(s['rho'] == '33.33', 'the second sphere stays 33.33'))
        reset(h); typed(h, 'Size', '150'); h.click('#ballsRhoNum'); h.key('Escape'); s = typed(h, 'Size', '200'); show('only a click into the box and Escape (nothing typed), then size 200', s, judge(s['rho'] == '25', 'the second sphere still follows (25): nothing was typed'))

        say('\n--- D4: the builder\'s "follows" (a decision; shown here as it is)')
        reset(h); s = typed(h, 'Size', '150'); show('typed size 150', s)
        s = typed(h, 'Size', '250'); show('typed size 250', s)
        s = typed(h, 'Size', '90'); show('typed size 90', s)
        s = typed(h, 'Rho', '100'); show('typed second sphere 100', s)

        say('\n--- D5: typed 100.004')
        reset(h); s = typed(h, 'Size', '100.004'); show('typed size 100.004', s, judge(s['size'] == '100' and s['rho'] == '100' and s['bt'] == 1 and s['warn'].startswith('At 100 the chain never ends') and 'Past 100' not in s['warn'], 'reads 100, second sphere 100, t exactly 1, Version 20\'s touching sentence'))
        reset(h); s = typed(h, 'Size', '100.006'); show('typed size 100.006 (shown as 100.01)', s, judge(s['size'] == '100.01' and float(s['rho']) < 51 and 'Past 100' in s['warn'], 'reads 100.01, the second sphere gives way, "Past 100"'))
        reset(h); s = typed(h, 'Size', '100'); show('typed size 100', s, judge(s['bt'] == 1 and s['rho'] == '100', 't exactly 1, second sphere 100'))

        say('\n--- D6 a: the words on the second sphere\'s box and step buttons')
        reset(h)
        t = h.js("const d = $('ballsRhoNum'), el = d.closest('.dial') || d.parentElement.parentElement; return { box: d.title, up: (el.querySelector('.dial-up') || {}).title || '', down: (el.querySelector('.dial-down') || {}).title || '', help: ($('ballsRhoHelp') || {}).textContent || '', sizeHelp: ($('ballsSizeHelp') || {}).textContent || '', depthHelp: ($('ballsDepthHelp') || {}).textContent || '', sizeBox: $('ballsSizeNum').title, depthBox: $('ballsDepthNum').title };")
        say('      second sphere box tooltip: "%s" | step up: "%s" | step down: "%s"' % (t['box'], t['up'], t['down']))
        say('      -> ' + judge(t['box'] == 'From 2 to 50, or 100' and 'From 50 one step goes to 100.' in t['up'] and 'From 100 one step goes to 50.' in t['down'], 'the tooltips tell of the gap'))
        typed(h, 'Rho', '40'); typed(h, 'Rho', '100')
        t2 = h.js("const d = $('ballsRhoNum'), el = d.closest('.dial') || d.parentElement.parentElement; return { box: d.title, up: (el.querySelector('.dial-up') || {}).title || '', down: (el.querySelector('.dial-down') || {}).title || '' };")
        say('      after the dial was moved (40, then 100): box "%s" | up "%s" | down "%s"' % (t2['box'], t2['up'], t2['down']))
        say('      -> ' + judge(t2['box'] == 'From 2 to 50, or 100' and t2['up'].count('From 50 one step') == 1 and t2['down'].count('From 100 one step') == 1, 'still so, and not doubled'))
        say('\n--- D6 c: the help texts')
        n_sent = lambda x: len([p for p in x.replace('?', '.').replace('!', '.').split('. ') if p.strip()])
        for nm, tx in (('size', t['sizeHelp']), ('second sphere', t['help']), ('depth', t['depthHelp'])):
            say('      %s (%d sentence(s), %d words): "%s"' % (nm, n_sent(tx), len(tx.split()), tx))
        say('      size box tooltip "%s", depth box tooltip "%s"' % (t['sizeBox'], t['depthBox']))

        say('\n--- D6 b: a large size typed, before Frame it')
        reset(h); s = typed(h, 'Size', '2000'); show('typed size 2000, no Frame it', s, judge('cuts the two big neighbours open' in s['warn'] and 'far ends are not drawn' not in s['warn'], 'the sentence names the neighbours and Frame it'))
        h.shot('%s/small7-%s-d6b-2000-no-frame.png' % (PICS, LAYOUT), '#stage')
        h.click('#ballsFrame'); s = st(h); show('Frame it', s, judge('Drawing radius' not in s['warn'], 'after Frame it nothing about the Drawing radius'))
        h.shot('%s/small7-%s-d6b-2000-framed.png' % (PICS, LAYOUT), '#stage')

        say('\n--- D6 d: the longest block the ui checker met (second sphere 50, size 200, depth 3)')
        reset(h); typed(h, 'Rho', '50'); typed(h, 'Size', '200'); s = typed(h, 'Depth', '3'); show('second sphere 50, size 200, depth 3', s)
        say('\n--- the longest block that can arise now (second sphere 50, size 199.8, depth 1, Drawing radius 2)')
        reset(h); typed(h, 'Rho', '50'); typed(h, 'Size', '199.8'); typed(h, 'Depth', '1')
        # (the View section is folded as the page opens: it is opened with a real click before its dial is typed into.
        #  My first run did not do that; the "2" then went into the box that had the focus, the depth, and the line was void.)
        if not h.js("return $('secView').open;"):
            h.click('#secView > summary'); time.sleep(0.3)
        ok_click = h.click('#viewBoundNum')
        h.type('#viewBoundNum', '2'); s = st(h); show('second sphere 50, size 199.8, depth 1, Drawing radius typed 2 (the box could be clicked: %s)' % ok_click, s,
                                                     judge(s['depth'] == '1' and s['bound'] == 2 and 'cuts the two big neighbours open' in s['warn'] and 'too long for one picture' in s['warn'] and 'wall of colour' in s['warn'], 'all five things are said at once'))
        fit = h.js("const w = $('ballsWarn'); w.scrollIntoView({ block: 'center' }); await sleep(250); const b = w.getBoundingClientRect(), p = $('kleinPanel'), pb = p.getBoundingClientRect(); return { w: [Math.round(b.left), Math.round(b.width), Math.round(b.height)], parent: [Math.round(pb.left), Math.round(pb.width)], over: w.scrollWidth > w.clientWidth + 1, doc: document.documentElement.scrollWidth, win: innerWidth };")
        say('      the block: left %d, %d wide, %d high; its parent left %d, %d wide; text wider than its box: %s; the document is %d wide in a window of %d'
            % (fit['w'][0], fit['w'][1], fit['w'][2], fit['parent'][0], fit['parent'][1], fit['over'], fit['doc'], fit['win']))
        say('      -> ' + judge(not fit['over'] and fit['doc'] <= fit['win'] and fit['w'][0] >= fit['parent'][0] and fit['w'][0] + fit['w'][1] <= fit['parent'][0] + fit['parent'][1] + 1, 'the longest block stays inside the panel'))
        h.window_shot('%s/small7-%s-longest-block.png' % (PICS, LAYOUT))
        h.type('#viewBoundNum', '8'); s = st(h); say('      the Drawing radius put back: %s' % s['bound'])

        say('\n--- D7: a chain too long to frame that does not touch (second sphere 50, size 199.8)')
        reset(h); typed(h, 'Rho', '50'); typed(h, 'Size', '199.8'); h.click('#ballsFrame'); s = st(h); show('second sphere 50, size 199.8, Frame it', s, judge('too long for one picture' in s['warn'], '3D: a sentence says the chain is too long for one picture'))
        h.shot('%s/small7-%s-d7-3d.png' % (PICS, LAYOUT), '#stage')
        s = flat(h, True); h.click('#ballsFrame'); s = st(h); show('the 2D view, Frame it', s, judge('too long for one picture' in s['warn'], '2D: the same sentence'))
        flat(h, False)
        reset(h); typed(h, 'Size', '99'); h.click('#ballsFrame'); s = st(h); show('two equal spheres, size 99, Frame it (Version 20\'s own state)', s)
        s = flat(h, True); h.click('#ballsFrame'); s = st(h); show('  the 2D view', s); flat(h, False)

        say('\n--- E3: the depth sentence')
        reset(h); s = typed(h, 'Depth', '1'); show('depth 1', s, judge('broken shells' in s['warn'] and 'one wall of colour' in s['warn'], 'depth 1: decision 6\'s sentence and the add-on'))
        s = typed(h, 'Depth', '2'); show('depth 2', s, judge('broken shells' in s['warn'] and 'wall of colour' not in s['warn'], 'depth 2: decision 6\'s sentence alone'))
        s = typed(h, 'Depth', '4'); show('depth 4', s, judge('broken shells' in s['warn'], 'depth 4: the sentence'))
        s = typed(h, 'Depth', '5'); show('depth 5', s, judge(not s['warn'], 'depth 5: no sentence'))

        say('\n--- E1, the sentence: second sphere 50 away from touching')
        reset(h); typed(h, 'Size', '150'); s = typed(h, 'Rho', '50'); show('size 150, second sphere 50', s, judge('buds on a neighbour kiss' in s['warn'], 'a sentence speaks of the swollen kiss'))
        reset(h); typed(h, 'Size', '150'); s = typed(h, 'Rho', '49'); show('size 150, second sphere 49', s, judge('kiss' not in s['warn'], 'no kiss sentence at 49'))

        if LAYOUT == 'phone':
            say('\n--- D6 e (phone): where the sentences stand while the size dial is under the thumb')
            reset(h); typed(h, 'Size', '150')
            g = h.js("const d = $('ballsSizeNum'); d.scrollIntoView({ block: 'center' }); await sleep(250); const w = $('ballsWarn').getBoundingClientRect(), s = $('ballsSize').getBoundingClientRect(), st = $('stage').getBoundingClientRect(); const e = document.elementFromPoint(w.left + w.width / 2, Math.max(1, Math.min(innerHeight - 1, w.top + w.height / 2))); return { warn: [Math.round(w.top), Math.round(w.bottom)], slider: [Math.round(s.top), Math.round(s.bottom)], stage: [Math.round(st.top), Math.round(st.bottom)], h: innerHeight, on: e ? (e.id || e.tagName) : 'nothing', seen: !!e && ($('ballsWarn') === e || $('ballsWarn').contains(e)) };")
            say('      window %d high; the pinned picture from %d to %d; the sentences from %d to %d; the size slider from %d to %d; at the middle of the sentences the finger meets: %s'
                % (g['h'], g['stage'][0], g['stage'][1], g['warn'][0], g['warn'][1], g['slider'][0], g['slider'][1], g['on']))
            say('      -> the sentences are %s while the size slider is in the middle of the window' % ('IN SIGHT' if g['seen'] else 'OUT OF SIGHT (behind the pinned picture or scrolled away)'))
            h.window_shot('%s/small7-%s-d6e.png' % (PICS, LAYOUT))
        reset(h)
        probs = h.problems()
        say('\n--- console: %s' % ('no console errors or warnings' if not probs else '%d PROBLEM(S): ' % len(probs) + ' || '.join(p[:400] for p in probs[:12])))
        if probs:
            wrong.append('console problems')
    say('=== %d line(s) marked WRONG%s' % (len(wrong), ': ' + ' | '.join(wrong) if wrong else ''))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        say('THE SCRIPT STOPPED: ' + repr(e)); say(traceback.format_exc())
        say('=== so far %d line(s) marked WRONG: %s' % (len(wrong), ' | '.join(wrong)))
        sys.exit(1)
