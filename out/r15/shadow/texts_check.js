// Round 15B, shadow: the entry's texts as the page gives them, at a few powers (runs in the page).
const L = window.squaringLab, a = L.APPROACHES.find(x => x.id === 'pillow4d'), out = {};
out.groups = L.APPROACH_GROUPS ? L.APPROACH_GROUPS.map(g => g.id) : 'not exported';
out.index = L.APPROACHES.indexOf(a); out.name = a.name; out.group = a.group; out.tag = a.tag;
out.note = a.params[0].text.length + ' characters'; out.about = a.about.length + ' characters';
for (const n of [2, 3, 4, 5, 10, 2.5, 1, -2, 0]) {
  out['n=' + n] = { formula: a.formula({}, n), round: a.roundNote(), crush: a.crush({}, n), smooth: a.smooth({}, n), sliceOk: a.slice(true, {}, n), sliceNot: a.slice(false, {}, n),
    math: L.MATH.pillow4d([0.3, 0.4, 0.2], n, {}), mathFlat: L.MATH.pillow4d([0.3, 0.4, 0], n, {}) };
}
const bad = JSON.stringify(out).match(/—|undefined|NaN/g);
out.badWords = bad ? bad.length : 0;
return JSON.stringify(out, null, 1);
