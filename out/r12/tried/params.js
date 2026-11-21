const L = window.squaringLab, S = L.S, out = {};
for (const id of ['softfold', 'axisbulb', 'pillow']) {
  S.approach = L.APPROACHES.findIndex(a => a.id === id);
  out[id] = { param: S.param[id], index: S.approach, group: L.APPROACHES[S.approach].group };
}
S.approach = 0;
out.order = L.APPROACHES.map(a => a.id + ':' + a.group).join(' ');
out.selects = ['par-softfold-curve', 'par-softfold-mix', 'par-pillow-layout'].map(id => { const e = document.getElementById(id); return id + '=' + (e ? e.tagName + ' ' + [...e.options].map(o => o.text).join(' / ') : 'MISSING'); });
out.ids = ['ap-softfold', 'f-softfold', 'pd-softfold', 'par-softfold-planes', 'par-softfold-blend', 'ap-axisbulb', 'f-axisbulb', 'pd-axisbulb', 'par-axisbulb-k', 'par-axisbulb-wob', 'par-axisbulb-reach', 'par-axisbulb-pinch', 'ap-pillow', 'f-pillow', 'pd-pillow'].filter(id => !document.getElementById(id));
return JSON.stringify(out);
