"""Round 27, entry: the first group's part of the Kleinian panel on the new page and on the frozen page: the positions of
its pieces, relative to the first of them (the new page has the choice of group above it). -> logs/oldpanel.txt, shots/oldpanel-*.png"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
JS = run.HEAD + """
$('mode-k').click(); await sleep(200); await settle(); $('kleinPanel').scrollIntoView({ block: 'start' }); await sleep(200);
const ids = ['kleinPreset', 'kleinFrame', 'kleinNote', 'kmy', 'kmx', 'kmz', 'k3', 'kL', 'kiter', 'kinvr', 'kcx', 'kcy', 'kcz'], first = document.querySelector('#kleinPanel .sec-body p.note').getBoundingClientRect();
const rows = ids.map(id => { const b = $(id).getBoundingClientRect(); return id + ' ' + [b.left - first.left, b.top - first.top, b.width, b.height].map(x => Math.round(x * 10) / 10).join(' '); });
const reset = [...$('kleinReset').querySelectorAll('button')][0].getBoundingClientRect(); rows.push('reset ' + [reset.left - first.left, reset.top - first.top, reset.width, reset.height].map(x => Math.round(x * 10) / 10).join(' '));
return rows.join(' | ');
"""
out = {}
for tag, page in (('new', 'dist/r27-entry.html'), ('old', 'dist/r27-entry-base.html')):
    code, text, vals = run.shot(page, [run.UP, dict(js=JS, shot='out/r27/entry/shots/oldpanel-%s.png' % tag)], 'oldpanel-' + tag)
    out[tag] = vals[-1]
same = out['new'] == out['old']
text = 'first group, positions of its controls relative to its first note (left top width height):\nnew: %s\nold: %s\n%s\n' % (out['new'], out['old'], 'THE SAME on both pages' if same else 'THEY DIFFER')
run.write('oldpanel.txt', text); print(text)
