"""Recheck of export-1 with the first check's own run (out/t6/export/a_sizes.py) on dist/v8.html.
python out/t9/export/a_sizes.py [typed|4k|8k]"""
import json, os, re, sys, time
from drv import Lab, HERE, log, open_rgb, blank, compare, seams, tl_report

which = sys.argv[1] if len(sys.argv) > 1 else '4k'
JOBS = {
    'typed': ('Typed', 'Extra fine', 'PNG', 1234, 778),
    '4k': ('3840', 'Fine', 'JPG', None, None),
    '8k': ('7680', 'As on screen', 'WebP', None, None),
}
lab = Lab()
try:
    lab.idle()
    info = lab.js("return { canvas: [$('view').width, $('view').height], note: $('exportSizeNote').textContent, size: chosen('exportSize'), quality: chosen('exportQuality'), kind: chosen('exportKind'), open: $('secExport').open, sizes: [...$('exportSize').options].map(o => o.text), qualities: [...$('exportQuality').options].map(o => o.text), kinds: [...$('exportKind').options].map(o => o.text), lede: $('exportPanel').querySelector('p').textContent };")
    log('page', json.dumps(info, ensure_ascii=False))
    lab.stage_shot('A-stage.png')
    for key in [which]:
        size, quality, kind, w, h = JOBS[key]
        st = lab.start_job(size, quality, kind, w, h)
        log(key, 'started', json.dumps(st, ensure_ascii=False))
        t0 = time.time()
        done = lab.job_wait(2100)
        en = lab.end_job()
        took = en['took']
        log(key, 'ended' if done else 'TIMED OUT', round(time.time() - t0, 1), 's', json.dumps({k: v for k, v in en.items() if k != 'tl'}, ensure_ascii=False))
        rows = tl_report(en['tl'], took)
        if rows:
            log(key, 'first number at %.1f s: said %.0f s, true %.1f s' % (rows[0][0], rows[0][2], rows[0][3]))
            pick = rows[::max(1, len(rows) // 16)]
            log(key, 'time left (at s, percent, said s, true s):', pick)
            ratios = [said / true for _, _, said, true in rows if true > 3]
            if ratios:
                log(key, 'said/true: min %.2f median %.2f max %.2f over %d readings' % (min(ratios), sorted(ratios)[len(ratios) // 2], max(ratios), len(ratios)))
            rises = [(a[0], a[2], b[2]) for a, b in zip(rows, rows[1:]) if b[2] > a[2]]
            log(key, 'rises (at s, from, to): %d' % len(rises), rises[:12])
        else:
            log(key, 'no number was shown at all')
        pcs = []
        for t, text in en['tl']:
            m = re.search(r'(\d+)%', text)
            if m: pcs.append((round(t / 1000, 1), int(m.group(1)), round(100 * t / took)))
        log(key, 'percent shown against percent of the time gone (at s, shown, true):', pcs[::max(1, len(pcs) // 16)])
        drops = [(a[0], a[1], b[1]) for a, b in zip(pcs, pcs[1:]) if b[1] < a[1]]
        log(key, 'percent going down: %d' % len(drops), drops[:8])
        log(key, 'first readings:', en['tl'][:8])
        log(key, 'last readings:', en['tl'][-4:])
        if not done or not en['saveShown']:
            continue
        lab.shot('A-%s-panel.png' % key, '#secExport')
        path, r = lab.save('A-' + key)
        log(key, 'saved', json.dumps(r, ensure_ascii=False))
        if not path:
            continue
        im, fmt = open_rgb(path)
        log(key, 'file', path, fmt, im.size, json.dumps(blank(im)))
        log(key, 'against the stage', json.dumps(compare(im, 'A-stage.png', 'A-%s-pair.png' % key)))
        log(key, 'tile borders', json.dumps(seams(im)))
        im.resize((960, round(960 * im.size[1] / im.size[0]))).save(os.path.join(HERE, 'A-%s-small.png' % key))
    log('problems', lab.problems())
finally:
    lab.close()
