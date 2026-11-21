"""Run A: three sizes (typed, 4K, 8K), each file type, each quality, at the opening settings.
python out/t6/export/a_sizes.py [which]   which: typed | 4k | 8k | all"""
import json, sys, time
from drv import Lab, log, open_rgb, blank, compare, seams, tl_report

which = sys.argv[1] if len(sys.argv) > 1 else 'all'
JOBS = {
    'typed': ('Typed', 'Extra fine', 'PNG', 1234, 778),
    '4k': ('3840', 'Fine', 'JPG', None, None),
    '8k': ('7680', 'As on screen', 'WebP', None, None),
}
lab = Lab()
try:
    lab.idle()
    info = lab.js("return { canvas: [$('view').width, $('view').height], stage: [$('stage').clientWidth, $('stage').clientHeight], note: $('exportSizeNote').textContent, size: chosen('exportSize'), quality: chosen('exportQuality'), kind: chosen('exportKind'), open: $('secExport').open, lede: $('exportPanel').querySelector('p').textContent };")
    log('page', json.dumps(info, ensure_ascii=False))
    lab.stage_shot('A-stage.png')
    for key in (JOBS if which == 'all' else [which]):
        size, quality, kind, w, h = JOBS[key]
        st = lab.start_job(size, quality, kind, w, h)
        log(key, 'started', json.dumps(st, ensure_ascii=False))
        t0 = time.time()
        done = lab.job_wait(2100)
        en = lab.end_job()
        log(key, 'ended' if done else 'TIMED OUT', round(time.time() - t0, 1), 's', json.dumps({k: v for k, v in en.items() if k != 'tl'}, ensure_ascii=False))
        rows = tl_report(en['tl'], en['took'])
        if rows:
            pick = rows[::max(1, len(rows) // 12)]
            log(key, 'time left (at s, percent, said s, true s):', pick)
            ratios = [said / true for _, _, said, true in rows if true > 3]
            if ratios:
                log(key, 'said/true: min %.2f median %.2f max %.2f over %d readings' % (min(ratios), sorted(ratios)[len(ratios) // 2], max(ratios), len(ratios)))
        log(key, 'first and last readings:', en['tl'][:3], en['tl'][-2:])
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
        im.resize((960, round(960 * im.size[1] / im.size[0]))).save(__import__('os').path.join(__import__('drv').HERE, 'A-%s-small.png' % key))
    log('problems', lab.problems())
finally:
    lab.close()
