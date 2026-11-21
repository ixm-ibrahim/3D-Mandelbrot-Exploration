"""Round 28, Track A, the fixer: the small defects (D2, D3, D5, D6, D7, E3, the sentence of E1, states written by hand),
each by the steps the checker gave, with REAL input (the dial checker's hand.py: mouse, keys, typed characters).

  python -B out/r28/fix/mk/small.py <tag>     -> out/r28/fix/logs/small-<tag>.txt
  (the page: the environment's FIX_PAGE, or dist/r28-fix.html; tag "before" with FIX_PAGE=dist/r28-dials.html)

Nothing is judged here: every line says what was done and what the page then showed (the two boxes, the state, the
sentence under the note, a tooltip). The before and the after file are read side by side.
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FIX, 'ui', 'mk'))
from hand import Hand

PAGE = os.environ.get('FIX_PAGE', 'dist/r28-fix.html')
tag = sys.argv[1] if len(sys.argv) > 1 else 'after'
LOG = os.path.join(FIX, 'logs', 'small-%s.txt' % tag); SHOTS = 'out/r28/fix/shots'
lines = []
READ = """return { size: $('ballsSizeNum').value, rho: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, t: S.k.bt, brho: S.k.brho, flat: S.flat, reach: L.ballsReach(), bound: S.view.bound,
  warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '', prog: String(L.R.sig || '').split('\\n')[0] };"""


def say(t):
    lines.append(t); print(t, flush=True)
    open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def show(h, what):
    a = h.js(READ)
    say('%s\n     -> size %s, second sphere %s, depth %s (t %.6f, radius %.6f; reach %s, Drawing radius %.2f; %s view)\n     -> sentence: "%s"' % (
        what, a['size'], a['rho'], a['depth'], a['t'], a['brho'], 'no end' if a['reach'] is None else '%.1f' % a['reach'], a['bound'], '2D' if a['flat'] else '3D', a['warn']))
    return a


def reset(h):
    h.click('#ballsReset button'); h.done()
    if h.js("return S.flat;"):
        h.click('#flat'); h.done()


def main():
    say('page %s, window 1400x950, dark, %s' % (PAGE, time.strftime('%H:%M:%S')))
    with Hand(PAGE, '1400x950', 'dark') as h:
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        show(h, 'the row Balls on balls')

        say('\n=== E1, the sentence: second sphere at 50 without touching')
        reset(h); h.type('#ballsSizeNum', '150'); h.done(); h.type('#ballsRhoNum', '50'); h.done(); h.click('#ballsFrame'); h.done()
        show(h, 'reset, size 150 typed, second sphere 50 typed, Frame it')
        h.type('#ballsRhoNum', '49'); h.done(); show(h, 'second sphere 49 typed')
        reset(h); h.type('#ballsRhoNum', '50'); h.done(); show(h, 'reset, second sphere 50 typed (size stays 55.56)')

        say('\n=== D2: touching within rounding')
        reset(h); h.type('#ballsRhoNum', '33.33'); h.done(); h.type('#ballsSizeNum', '300'); h.done()
        show(h, 'reset, second sphere 33.33 typed, size 300 typed')
        h.click('#ballsFrame'); h.done(); show(h, 'Frame it')
        h.shot('%s/small-%s-d2-3d.png' % (SHOTS, tag), '#stage')
        h.click('#flat'); h.done(); h.click('#ballsFrame'); h.done(); show(h, '2D view ticked, Frame it')
        h.click('#flat'); h.done()

        say('\n=== D7: a chain too long to frame that does not touch')
        reset(h); h.type('#ballsRhoNum', '50'); h.done(); h.type('#ballsSizeNum', '199.8'); h.done(); h.click('#ballsFrame'); h.done()
        show(h, 'reset, second sphere 50 typed, size 199.8 typed, Frame it')
        h.click('#flat'); h.done(); h.click('#ballsFrame'); h.done(); show(h, '2D view ticked, Frame it')
        h.click('#flat'); h.done()

        say('\n=== D3: a number typed again into the second sphere\'s own box')
        reset(h); h.type('#ballsSizeNum', '150'); h.done(); show(h, 'reset, size 150 typed')
        h.type('#ballsRhoNum', '33.33'); h.done(); show(h, '33.33 typed into the second sphere\'s own box, Enter')
        h.type('#ballsSizeNum', '200'); h.done(); show(h, 'size 200 typed')
        reset(h); h.type('#ballsSizeNum', '150'); h.done(); h.type('#ballsSizeNum', '250'); h.done(); show(h, 'for comparison: reset, size 150 typed, size 250 typed (nothing typed into the second sphere)')

        say('\n=== D5: a size typed with three decimals just over 100')
        reset(h); h.type('#ballsSizeNum', '100.004'); h.done(); show(h, 'reset, size 100.004 typed')
        reset(h); h.type('#ballsSizeNum', '100.01'); h.done(); show(h, 'reset, size 100.01 typed')
        reset(h); h.type('#ballsSizeNum', '100'); h.done(); show(h, 'reset, size 100 typed')

        say('\n=== D6 (a): the words on the second sphere\'s box and arrows')
        reset(h)
        t = h.js("const d = $('ballsRhoNum').closest('.dial'); return { box: $('ballsRhoNum').title, up: d.querySelector('.dial-up').title, down: d.querySelector('.dial-down').title, mode: d.querySelector('.dial-mode') ? d.querySelector('.dial-mode').textContent : '' };")
        say('as the page stands: box "%s" | up "%s" | down "%s" | step button reads %s' % (t['box'], t['up'], t['down'], t['mode']))
        h.click('#ballsRhoStep'); time.sleep(0.3)
        t = h.js("const d = $('ballsRhoNum').closest('.dial'); return { box: $('ballsRhoNum').title, up: d.querySelector('.dial-up').title, down: d.querySelector('.dial-down').title, mode: d.querySelector('.dial-mode').textContent };")
        say('after a click on the step button: box "%s" | up "%s" | down "%s" | step button reads %s' % (t['box'], t['up'], t['down'], t['mode']))
        h.click('#ballsRhoStep'); time.sleep(0.3)
        h.js("L.setExtreme && L.setExtreme(true); await sleep(200); L.setExtreme && L.setExtreme(false); await sleep(200); return 1;")
        t = h.js("const d = $('ballsRhoNum').closest('.dial'); return { box: $('ballsRhoNum').title, up: d.querySelector('.dial-up').title };")
        say('after Extreme ranges on and off (by script): box "%s" | up "%s"' % (t['box'], t['up']))

        say('\n=== D6 (b): a large size typed, before Frame it')
        reset(h); h.js("S.view.bound = 8; L.syncControls(); L.touch(); return 1;"); h.done()
        h.type('#ballsSizeNum', '2000'); h.done(); show(h, 'reset, Drawing radius 8 (by script), size 2000 typed, no Frame it')
        h.shot('%s/small-%s-d6b-2000-typed.png' % (SHOTS, tag), '#stage')
        h.click('#ballsFrame'); h.done(); show(h, 'Frame it')
        reset(h); h.js("S.view.bound = 8; L.syncControls(); L.touch(); return 1;"); h.done()
        h.type('#ballsSizeNum', '150'); h.done(); show(h, 'reset, Drawing radius 8 (by script), size 150 typed, no Frame it')

        say('\n=== D6 (c): the help under the size dial')
        say('"%s"' % h.js("return $('ballsSizeHelp').textContent;"))
        say('the help under the second sphere: "%s"' % h.js("return $('ballsRhoHelp').textContent;"))

        say('\n=== D6 (d): the longest block of sentences (spheres touching, a smaller second sphere, depth under 5)')
        reset(h); h.type('#ballsRhoNum', '50'); h.done(); h.type('#ballsSizeNum', '200'); h.done(); h.type('#ballsDepthNum', '1'); h.done(); h.click('#ballsFrame'); h.done()
        a = show(h, 'reset, second sphere 50, size 200, depth 1, Frame it'); say('     that is %d characters, %d words' % (len(a['warn']), len(a['warn'].split())))
        h.type('#ballsDepthNum', '3'); h.done(); a = show(h, 'depth 3'); say('     that is %d characters, %d words' % (len(a['warn']), len(a['warn'].split())))

        say('\n=== E3: what the sentence says at depth 1, 2, 4, 5')
        reset(h)
        for d in ('1', '2', '4', '5'):
            h.type('#ballsDepthNum', d); h.done(); show(h, 'depth %s typed' % d)

        say('\n=== states written by hand (no dial gives them)')
        reset(h)
        a = h.js("S.k.brho = 0.7; S.k.bt = 1.4; L.syncControls(); L.touch(); await sleep(300); return { shown: $('ballsRhoNum').value, prog: String(L.R.sig || '').split('\\n')[0], warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '' };")
        h.done(); a = h.js("return { shown: $('ballsRhoNum').value, prog: String(L.R.sig || '').split('\\n')[0], warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '' };")
        say('radius 0.7 written into the state: the box shows %s, the program on show is %s, sentence "%s"' % (a['shown'], a['prog'], a['warn']))
        a = h.js("""S.k.brho = 0.5; S.k.bt = 0.6; L.syncControls(); L.touch(); await sleep(300);
          const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, 0, 0, 4, 0, 64); L.releaseSnapshot(snap); let dif = 0;
          for (let j = 0; j < 64; j++) for (let i = 0; i < 64; i++) { const x = 4 * ((i + 0.5) / 64 - 0.5), y = 4 * ((j + 0.5) / 64 - 0.5); if ((arr[4 * (j * 64 + i) + 3] > 0) === L.ballsInside(x, y, 0)) dif++; }
          return { dif, size: $('ballsSizeNum').value };""")
        say('radius 0.5 with t = 0.6 written into the state (below the touching value 0.75): the picture\'s program and the twin with nothing passed give different verdicts at %d of 4096 points of the flat cut; the size box shows %s' % (a['dif'], a['size']))
        reset(h)
        probs = h.problems()
        say('\nconsole: %s' % ('no console errors or warnings' if not probs else ' || '.join(p[:300] for p in probs[:8])))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        say('THE SCRIPT STOPPED: ' + repr(e)); say(traceback.format_exc()); sys.exit(1)
