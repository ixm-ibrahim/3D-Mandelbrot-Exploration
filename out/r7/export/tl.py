"""Time left, said against true, for one picture job.
python out/r7/export/tl.py <url> <4k|8k|typed|kfill|x2|flat4k> [tag] [setup-js]
Reads #exportStep every 250 ms. Prints when the first number appears, said/true ratios, and every rise."""
import json, re, sys, time
from drv import Lab, log, tl_report

url = sys.argv[1]; which = sys.argv[2]; tag = sys.argv[3] if len(sys.argv) > 3 else which
JOBS = {
    'typed': ('Typed', 'Extra fine', 'PNG', 1234, 778, ''),
    '4k': ('3840', 'Fine', 'JPG', None, None, ''),
    '4kpng': ('3840', 'As on screen', 'PNG', None, None, ''),
    '8k': ('7680', 'As on screen', 'WebP', None, None, ''),
    'x2': ('Twice', 'Fine', 'PNG', None, None, ''),
    # a picture that fills the frame: the Kleinian view
    'kfill': ('2560', 'Fine', 'JPG', None, None, "$('mode-k').click(); await sleep(200);"),
    'kfill4k': ('3840', 'Fine', 'JPG', None, None, "$('mode-k').click(); await sleep(200);"),
    'flat4k': ('3840', 'Fine', 'PNG', None, None, "$('flat').click(); await sleep(200);"),
}
size, quality, kind, w, h, setup = JOBS[which]
PASSES = {'Fine': 32, 'Extra fine': 64}.get(quality, 12)
lab = Lab(url=url)
try:
    lab.idle()
    if setup:
        lab.js(setup); lab.idle()
    lab.js("window.squaringLabExportTest = tiles => { window.__exportDebug = tiles; };")
    import os
    if os.environ.get('WAIT'):
        time.sleep(float(os.environ['WAIT']))
        log(tag, 'waited', os.environ['WAIT'], 's; warming:', lab.js("return [!!L.R.warming, L.R.warmOn, L.R.bgHeld];"))
    st = lab.start_job(size, quality, kind, w, h)
    log(tag, 'started', json.dumps(st, ensure_ascii=False))
    t0 = time.time()
    done = lab.job_wait(2100)
    en = lab.end_job()
    took = en['took']
    log(tag, 'ended' if done else 'TIMED OUT', round(time.time() - t0, 1), 's', json.dumps({k: v for k, v in en.items() if k != 'tl'}, ensure_ascii=False))
    log(tag, 'frame gaps over 40 ms (at ms, gap ms, step, job running):', en.get('gapsAt'))
    rows = tl_report(en['tl'], took)
    if rows:
        log(tag, 'first number at %.1f s: said %.0f s, true %.1f s' % (rows[0][0], rows[0][2], rows[0][3]))
        pick = rows[::max(1, len(rows) // 14)]
        log(tag, 'time left (at s, percent, said s, true s):', pick)
        ratios = [said / true for _, _, said, true in rows if true > 3]
        if ratios:
            log(tag, 'said/true: min %.2f median %.2f max %.2f over %d readings' % (min(ratios), sorted(ratios)[len(ratios) // 2], max(ratios), len(ratios)))
        rises = [(a[0], a[2], b[2]) for a, b in zip(rows, rows[1:]) if b[2] > a[2]]
        log(tag, 'rises (at s, from, to): %d' % len(rises), rises[:12])
    else:
        log(tag, 'no number was shown at all')
    # the percentage against the share of the time gone
    pcs = []
    for t, text in en['tl']:
        m = re.search(r'(\d+)%', text)
        if m: pcs.append((round(t / 1000, 1), int(m.group(1)), round(100 * t / took)))
    log(tag, 'percent shown against percent of the time gone (at s, shown, true):', pcs[::max(1, len(pcs) // 14)])
    log(tag, 'first readings:', en['tl'][:6])
    log(tag, 'last readings:', en['tl'][-3:])
    dbg = lab.js("return window.__exportDebug || null;")
    if dbg:
        n = len(dbg); withgpu = sum(1 for t in dbg if t['gpu'] > 0)
        sw = sum(t['w'] for t in dbg); sm = sum(t['ms'] for t in dbg)
        log(tag, 'tiles %d, with a GPU reading %d, felt cost in all %.0f ms, time in tiles %.0f ms, ratio %.2f' % (n, withgpu, sw, sm, sm / max(sw, 1e-9)))
        # per tile: felt share against true share of the time, in percent
        rows = {}
        for t in dbg: rows.setdefault(t['y0'], []).append(t)
        for y0 in sorted(rows, reverse=True):
            log(tag, 'row y0=%d  felt%%/true%%: ' % y0 + '  '.join('%4.1f/%4.1f' % (100 * t['w'] / sw, 100 * t['ms'] / sm) for t in rows[y0]))
        # the GPU's own count of the real pieces against the felt cost: milliseconds for one pass of the tile
        for y0 in sorted(rows, reverse=True):
            log(tag, 'row y0=%d  one pass, felt/real GPU ms: ' % y0 + '  '.join('%5.1f/%5.1f' % (t['gpu'] / t['felt'] * t['N'] / PASSES, (t['gMs'] / t['gPx'] * t['N'] / PASSES) if t.get('gPx') else -1) for t in rows[y0]))
        sg = sum(t['gMs'] * t['N'] / t['gPx'] for t in dbg if t.get('gPx'))
        log(tag, 'real GPU time of all tiles %.0f ms; felt %.0f ms; clock %.0f ms' % (sg, sw, sm))
        for y0 in sorted(rows, reverse=True):
            log(tag, 'row y0=%d  clock ms / real GPU ms: ' % y0 + '  '.join('%5.0f/%5.0f' % (t['ms'], (t['gMs'] * t['N'] / t['gPx']) if t.get('gPx') else -1) for t in rows[y0]))
        log(tag, 'clock ms for each unit of felt cost, tiles in the order drawn: ' + ' '.join('%.2f' % (t['ms'] / max(t['w'], 1e-9)) for t in dbg))
        log(tag, 'held back for the live picture:', lab.js("return L.R.bgHeld;"))
        log(tag, 'gpu ms: ' + ' '.join('%.2f' % t['gpu'] for t in dbg))
        log(tag, 'clock ms: ' + ' '.join('%.2f' % t['clock'] for t in dbg))
    log('problems', lab.problems())
finally:
    lab.close()
