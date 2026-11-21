"""Round 27, fixer: defects A and B of the checker "eyes". What is on the screen right after the one click on the row
Balls on balls (no scrolling by the script), and how much of the Approach list a phone shows.

  python out/r27/fix/mk/land.py <page> <tag>     -> logs/land-<tag>.txt, shots/land-<tag>-<window>-*.png
Windows: 1400x950 and 390x800, dark. The same steps as the checker's steps/s11-land.json and the last step of s7.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

PREP = """window.L = window.squaringLab; window.sleep = ms => new Promise(r => setTimeout(r, ms));
window.settle = async () => { await sleep(120); while (!L.idle()) await sleep(25); await sleep(60); while (!L.idle()) await sleep(25); };
window.where = () => { const g = id => { const e = document.getElementById(id); if (!e) return null; const b = e.getBoundingClientRect(); return b.width || b.height ? [Math.round(b.top), Math.round(b.bottom)] : 'not shown'; };
  const rows = [...document.querySelectorAll('#rules .rule')], lb = document.getElementById('rules').getBoundingClientRect();
  const pinned = document.querySelector('.bench-main').getBoundingClientRect();
  return { scrollY: Math.round(scrollY), win: [innerWidth, innerHeight], pictureColumn: [Math.round(pinned.top), Math.round(pinned.bottom)], show: g('mode-k') && (() => { const b = document.querySelector('fieldset.mode').getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom)]; })(),
    menuBtn: g('apMenuBtn'), pop: g('apPop'), list: g('rules'), listHeight: Math.round(lb.height), cousin: g('apg-cousin'), row: g('ap-balls'),
    approachesWhollyInTheList: rows.filter(r => { const b = r.getBoundingClientRect(); return b.top >= lb.top - 0.5 && b.bottom <= lb.bottom + 0.5; }).length,
    kleinPanel: g('kleinPanel'), kleinGroup: g('kleinGroup'), ballsNote: g('ballsNote'), ballsSize: g('ballsSize'), ballsGrid: g('ballsGrid'), ballsDepth: g('ballsDepth'), ballsFrame: g('ballsFrame'), stage: g('stage'), secApproach: g('secApproach'), card: g('card') }; };
const b = document.getElementById('apMenuBtn'); if (innerWidth < 700) { b.scrollIntoView({block: 'center'}); await sleep(300); } const before = where(); b.click(); await sleep(400); return JSON.stringify({before, menuOpen: where()});"""
ROW = "document.getElementById('ap-balls').scrollIntoView({block: 'nearest'}); await sleep(100); const seen = where(); document.getElementById('ap-balls').click(); await settle(); await sleep(300); return JSON.stringify({rowBeforeTheClick: seen.row, pop: seen.pop, afterRow: where(), mode: L.S.mode, group: L.S.k.group});"

if __name__ == '__main__':
    page, tag = sys.argv[1], sys.argv[2]
    lines = []
    for size, short in (('1400x950', 'wd'), ('390x800', 'pd')):
        P = 'out/r27/fix/shots/land-%s-%s' % (tag, short)
        steps = [{'wait': 'done', 'timeout': 200}, {'js': PREP}, {'shot': P + '-0-menu-open.png'}, {'js': ROW}, {'shot': P + '-1-right-after-the-row.png'}]
        code, text, vals = run.shot(page, steps, 'land-%s-%s' % (tag, short), size, 'dark')
        lines.append('%s %s: exit %d, %s' % (page, size, code, 'no console errors' if 'no console errors' in text else 'SEE THE LOG'))
        for v in vals:
            try:
                d = json.loads(v)
            except ValueError:
                lines.append(str(v)[:400]); continue
            for k, w in d.items():
                lines.append('  %s: %s' % (k, json.dumps(w)))
    out = '\n'.join(lines) + '\n'
    run.write('land-%s.txt' % tag, out); print(out)
