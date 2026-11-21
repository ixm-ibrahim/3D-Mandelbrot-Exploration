"""Round 28, dial checker (ui): "Frame it" in low, wide windows (found by sizes.py at 900x420): which windows cut the
picture, where, and from which size on. Also the frozen page in the same windows, to see what Version 20 does there.

  python -B out/r28/final/ui/mk/sizes2.py      -> out/r28/final/ui/logs/sizes2.txt, pictures out/r28/final/ui/shots/sizes2-*.png

Windows: 1366x640 and 1280x600 (a small laptop's browser), 1536x730, 1920x940, 1400x700, and two phones held
sideways (844x390, 915x412). For each: the row (real click), the size typed (real keys), Frame it (real click). The
picture is asked at 41 x 25 points (the lab's own pick); a hit in the outermost ring of points means the object
touches the edge of the picture there. Also read straight from the picture: the rows and columns of pixels at its
very edge that are not background (the controls over the picture are hidden for that one screenshot, by script).
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hand import Hand, ROOT, UI
import numpy as np
from PIL import Image

LOG = os.path.join(UI, 'logs', 'sizes2.txt'); SHOTS = 'out/r28/final/ui/shots'
lines, wrong = [], []
PROBE = """const w = $('stage').clientWidth, hh = $('stage').clientHeight, NX = 41, NY = 25; let n = 0; const side = { top: 0, bottom: 0, left: 0, right: 0 };
  for (let i = 0; i < NX; i++) for (let j = 0; j < NY; j++) { const hit = !!L.pick(w * (i + 0.5) / NX, hh * (j + 0.5) / NY); if (hit) { n++; if (j === 0) side.top++; if (j === NY - 1) side.bottom++; if (i === 0) side.left++; if (i === NX - 1) side.right++; } }
  return { hits: n, side, reach: L.ballsReach(), bound: S.view.bound, dist: L.cam.dist, stage: [w, hh], size: $('ballsSizeNum').value, rho: $('ballsRhoNum') ? $('ballsRhoNum').value : '100' };"""


def say(t):
    lines.append(t); print(t)
    open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def edge(path):
    """Pixels on the four edges of the saved picture that are not background (the colour of its top left corner)."""
    A = np.asarray(Image.open(os.path.join(ROOT, path)).convert('RGB')).astype(int)
    fg = np.abs(A - A[1, 1]).max(axis=2) > 24
    return {'top': int(fg[1].sum()), 'bottom': int(fg[-2].sum()), 'left': int(fg[:, 1].sum()), 'right': int(fg[:, -2].sum())}


def run(page, tag, size, ps):
    with Hand(page, size, 'dark') as h:
        h.click('#apMenuBtn'); time.sleep(0.4); h.click('#ap-balls'); h.done()
        if not h.js("return S.mode === 'k' && S.k.group === 1;"):
            say('%s, window %s: the row did not show Balls on balls' % (tag, size)); return
        for p in ps:
            h.click('#ballsReset button'); h.done()
            h.type('#ballsSizeNum', p); h.done()
            h.click('#ballsFrame'); h.done(); a = h.js(PROBE)
            h.js("for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden'; await sleep(150); return 1;")
            path = '%s/sizes2-%s-%s-size-%s.png' % (SHOTS, tag, size, p)
            h.shot(path, '#view')
            h.js("for (const e of $('stage').children) e.style.visibility = ''; return 1;")
            e = edge(path); cut = [k for k in ('top', 'bottom', 'left', 'right') if e[k] > 0]
            ok = not cut
            say('%s page, window %s (picture %d x %d, %.2f wide for 1 high), size %s (second sphere %s), Frame it: camera distance %.2f; probes on the outermost ring: %s; pixels of the object on the very edge of the picture: %s  -> %s' % (
                tag, size, a['stage'][0], a['stage'][1], a['stage'][0] / a['stage'][1], a['size'], a['rho'], a['dist'], json.dumps(a['side']), json.dumps(e),
                'OK, the whole chain is in the picture' if ok else 'CUT OFF at the ' + ' and '.join(cut)))
            if not ok:
                wrong.append('%s page, %s, size %s: cut at the %s' % (tag, size, p, ' and '.join(cut)))
        probs = h.problems()
        if probs:
            say('   console: ' + ' || '.join(x[:300] for x in probs[:5])); wrong.append('console')


def main():
    say('started %s' % time.strftime('%H:%M:%S'))
    for size in ('1366x640', '1280x600', '1536x730', '1920x940', '1400x700', '844x390', '915x412'):
        run('dist/r28-final.html', 'new', size, ('55.56', '101', '150', '300', '400'))
    for size in ('1366x640', '1280x600', '844x390'):
        run('dist/r28-base-final.html', 'frozen', size, ('55.56', '90', '100'))
    say('=== %d picture(s) cut off%s' % (len(wrong), ': ' + ' | '.join(wrong) if wrong else ''))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        say('THE SCRIPT STOPPED: ' + repr(e)); say(traceback.format_exc()); sys.exit(1)
