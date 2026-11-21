"""Write out/r5/page/labels.json: list every label, option, button and note of each section, per mode."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
JS = r"""
const out = {};
const txt = e => (e.textContent || '').replace(/\s+/g, ' ').trim();
const grab = root => {
  const r = [];
  root.querySelectorAll('label, button, select, summary, legend, p').forEach(e => {
    if (e.closest('[hidden]')) return;
    if (e.tagName === 'SELECT') r.push('SELECT#' + e.id + ': ' + [...e.querySelectorAll('optgroup')].map(g => '[' + g.label + ']').join(' ') + ' :: ' + [...e.options].map(o => o.text).join(' | '));
    else r.push(e.tagName + (e.id ? '#' + e.id : '') + (e.htmlFor ? '(for ' + e.htmlFor + ')' : '') + ': ' + txt(e));
  });
  return r;
};
const nap = ms => new Promise(r => setTimeout(r, ms));
for (const m of ['m', 'j', 'k']) {
  document.getElementById('mode-' + m).click(); await nap(300);
  out[m] = {};
  document.querySelectorAll('#sections > details.sec').forEach(d => { if (!d.hidden) d.open = true; });
  await nap(200);
  document.querySelectorAll('#sections > details.sec').forEach(d => { if (!d.hidden) out[m][d.id] = grab(d); });
}
out.top = grab(document.querySelector('.dials .toprow')).concat(grab(document.querySelector('fieldset.mode')));
document.getElementById('mode-m').click(); await nap(200);
document.getElementById('flat').click(); await nap(400);
out.flat = {};
['secColour', 'secView', 'secQuality', 'secCut'].forEach(id => { out.flat[id] = grab(document.getElementById(id)); });
return out;
"""
steps = [{"wait": "done", "timeout": 120}, {"js": JS}]
json.dump(steps, open(os.path.join(HERE, 'labels.json'), 'w', encoding='utf-8'))
