// The custom approach on the page. Under the picture stand the bar that plays the steps (#cuBar) and the steps
// themselves with their tools (#cuDock); the approach's panel in the controls column holds the help and the rule
// as text. The rule itself is in 12-custom.js; this file only changes S.custom and shows it.
const CUI = {
  undo: [],              // earlier rules, as text, newest last
  hot: false,            // a slider or a number box of a step is being moved (one undo entry for the whole move)
  before: 0,             // the approach that was chosen before the custom one (the button goes back to it)
  formula: new Set(),    // 'step id:key' of the settings whose menu stands on "a formula"
  playing: false, raf: 0, last: 0,
  until: null,           // a play of one step alone stops here (how far through the iteration's steps); null: at the iteration's end
  barSig: '', now: null, // what the bar last showed; the id of the step it marked
  look: null,            // the id of a step that moves no point and whose name was clicked: its value is on show
  wasOn: false,          // the custom approach was on show when customSync last looked
  saved: [],             // the rules the user has saved: [{ name, rule }], rule as cuRuleText writes it
  kept: [],              // the steps the user has saved: [{ name, kind, p }]
  home: null,            // the start distance of the camera for what customSync last saw (null: a Kleinian picture)
};
// Saved rules are kept in localStorage; where that is blocked every access throws, and the list stays empty.
const CU_SAVED_KEY = 'squaringLab.customSaved';
function cuSavedLoad() {
  try {
    const list = JSON.parse(localStorage.getItem(CU_SAVED_KEY) || '[]');
    CUI.saved = (Array.isArray(list) ? list : []).filter(x => x && typeof x.name === 'string' && cuRuleOf(x.rule)).slice(0, 60).map(x => ({ name: x.name.slice(0, 40), rule: x.rule }));
  } catch (err) { CUI.saved = []; }
}
function cuSavedStore() {
  try { localStorage.setItem(CU_SAVED_KEY, JSON.stringify(CUI.saved)); return true; } catch (err) { return false; }
}
// Saved steps: a step with its settings, kept under a name. They have the first group of the list of kinds
// (83-custom-pick.js; their values there are @0, @1, ...). One that is added, or chosen under Change, is an
// ordinary step of its kind with those settings, which carries the name. They are kept in localStorage like the
// saved approaches; where that is blocked they last for the visit.
const CU_KEPT_KEY = 'squaringLab.customSteps';
function cuKeptOf(x) {
  const B = x && CU_BLOCKS[x.kind], p = {};
  if (!B || typeof x.name !== 'string' || !x.name.trim()) return null;
  for (const sp of B.params) { const v = x.p && x.p[sp.key]; if (typeof v === 'string' || typeof v === 'number') p[sp.key] = String(v).slice(0, 400); }
  return { name: x.name.trim().slice(0, 40), kind: x.kind, p };
}
function cuKeptLoad() {
  try { const list = JSON.parse(localStorage.getItem(CU_KEPT_KEY) || '[]'); CUI.kept = (Array.isArray(list) ? list : []).map(cuKeptOf).filter(Boolean).slice(0, 60); } catch (err) { CUI.kept = []; }
}
function cuKeptStore() {
  try { localStorage.setItem(CU_KEPT_KEY, JSON.stringify(CUI.kept)); return true; } catch (err) { return false; }
}
const cuKeptAt = v => (String(v)[0] === '@' ? CUI.kept[+String(v).slice(1)] || null : null);
// The button beside "Add step": its value is what Add step adds (a kind, or a saved step), and it shows that by
// name. value: a new choice; left out, the one it has is shown afresh. A choice that is no more gives way to the
// first kind.
function cuAddSet(value) {
  const btn = $('cuAddSel');
  if (value !== undefined) btn.value = String(value);
  if (!cuKeptAt(btn.value) && !CU_BLOCKS[btn.value]) btn.value = Object.keys(CU_BLOCKS).find(k => CU_BLOCKS[k].group === CU_GROUPS[0]);
  const mine = cuKeptAt(btn.value);
  btn.textContent = mine ? mine.name : CU_BLOCKS[btn.value].title;
}
// Gives a saved step another name, on the list and on every step of the approach that carries it. Returns what
// stands in the way, as a sentence, or '' when it is done.
function cuKeptRename(k, name) {
  const mine = CUI.kept[k], as = String(name).trim().slice(0, 40);
  if (!mine || !as || as === mine.name) return '';
  if (CUI.kept.some((s, j) => j !== k && s.name.toLowerCase() === as.toLowerCase())) return 'Another saved step has that name already.';
  const steps = S.custom.steps.filter(st => st.name === mine.name);
  if (steps.length) cuSnap();
  mine.name = as;
  for (const st of steps) st.name = as;
  cuKeptStore();
  if (steps.length) cuChanged(true);
  cuAddSet();
  return '';
}
// Takes a saved step off the list. The button beside "Add step" goes on showing the step it showed.
function cuKeptDrop(k) {
  const v = $('cuAddSel').value, at = v[0] === '@' ? +v.slice(1) : -1;
  if (!CUI.kept[k]) return;
  CUI.kept.splice(k, 1);
  cuKeptStore();
  cuAddSet(at === k ? '' : at > k ? '@' + (at - 1) : v);
}
// Makes a step one of the saved steps where it stands: its kind, its settings and its name.
function cuTake(st, mine) {
  for (const f of [...CUI.formula]) if (f.startsWith(st.id + ':')) CUI.formula.delete(f);
  st.kind = mine.kind; st.p = { ...Object.fromEntries(CU_BLOCKS[mine.kind].params.map(sp => [sp.key, sp.def])), ...mine.p }; st.name = mine.name;
  cuSetSec(st, cuSecOf(st));
  S.custom.steps = cuSorted(S.custom.steps);
}
// Saves a step as it is now under a name. A name that is taken already gets this step in the place of the earlier one.
function cuKeep(st, name) {
  const entry = cuKeptOf({ name, kind: st.kind, p: st.p }), at = CUI.kept.findIndex(s => s.name.toLowerCase() === entry.name.toLowerCase());
  if (at < 0 && CUI.kept.length >= 60) { cuSay('Sixty steps are saved already. To make room, choose one beside “Add step” and press Delete.'); return; }
  if (at >= 0) CUI.kept[at] = entry; else CUI.kept.push(entry);
  const held = cuKeptStore();
  cuSnap(); st.name = entry.name;
  cuAddSet('@' + (at >= 0 ? at : CUI.kept.length - 1));
  cuChanged(true);
  cuSay((at >= 0 ? `“${entry.name}” is saved again, as this step is now.` : `Saved as “${entry.name}”. It is in the list of steps, which opens beside “Add step” and under “Change”: at the top, under “Your saved steps”.`)
    + (held ? '' : ' This browser’s storage is blocked or full, so it is kept for this visit only.'));
}
// The menu of rules to load: the user's saved ones (values s0, s1, ...) above the lab's own (0, 1, ...).
function cuStartMenu(value) {
  const sel = $('cuStart'), opt = (v, t) => `<option value="${v}">${cuEsc(t)}</option>`;
  const starts = lab => CU_STARTS.map((s, k) => (!!s.lab === lab ? opt(k, s.name) : '')).join('');
  sel.innerHTML = (CUI.saved.length ? `<optgroup label="Your saved approaches">${CUI.saved.map((s, k) => opt('s' + k, s.name)).join('')}</optgroup>` : '')
    + `<optgroup label="The lab’s approaches, as steps">${starts(true)}</optgroup><optgroup label="Other approaches to start from">${starts(false)}</optgroup>`;
  if (value !== undefined && [...sel.options].some(o => o.value === String(value))) sel.value = String(value);
  $('cuDelBtn').hidden = sel.value[0] !== 's';
}
const cuEsc = t => String(t).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const cuStepAt = id => S.custom.steps.findIndex(s => String(s.id) === String(id));
const cuShort = x => String(+(+x).toFixed(4));
const cuOn = () => ap().id === 'custom' && S.mode !== 'k';
const cuSpec = (st, key) => CU_BLOCKS[st.kind].params.find(x => x.key === key);
const CU_HELP = `<p class="note"><b>A point</b> is written <code>vec(x, y, z)</code>, as in <code>vec(0, 0, 1)</code> for one step straight up. Every box for a point takes that, a name such as <code>c</code> or <code>z</code>, or a formula.</p>
<p class="note"><b>A formula step</b> is one line, <code>name = formula</code>. The name <code>z</code> is the point: a line that starts <code>z =</code> moves it. Any other name is yours and can be used in every step after it.</p>
<p class="note"><b>Given:</b> <code>z</code> the point, <code>c</code>, <code>n</code> the Power dial, <code>pi</code>; every point as a length and two angles, written after the point: <code>z.radius</code> (how far from the middle), <code>z.theta</code> (the angle round the upright axis) and <code>z.phi</code> (the angle of the height above the flat plane), so that <code>sph(z.radius, z.theta, z.phi)</code> is z itself, and the same for c and for a point you have named, as in <code>c.phi</code> (<code>radius</code>, <code>theta</code> and <code>phi</code> alone are short for those of z); and from the orbit <code>first</code> (its first point), <code>last</code> (the point of the iteration before), <code>point(2)</code> (its second point, and so on by number; <code>point(0)</code> is the point this iteration began with and <code>point(-1)</code> the one before), <code>mean</code> (the average of its points so far) and <code>count</code> (which iteration this is). <code>z</code> is always the point where it is now, after the steps before this one.</p>
<p class="note"><b>Three sections.</b> The steps under “Every iteration” are the part that is repeated. The steps under “Once, before the iterations” are taken one time, before iteration 1: they move the point where it starts. The steps under “Once, after the iterations” are taken one time, after the last iteration. A slider can be used by every step after it, in any section; any other name stays in its own section.</p>
<p class="note"><b>Works on.</b> A step that moves a point has a “Works on” menu: the point <code>z</code>, <code>c</code>, or a point you have named in an earlier step of the same section, as in <code>w = z</code>. A formula can change c too: <code>c = c*0.9</code>. A change of c lasts: the orbit carries the new c on to its next iteration. Before the iterations a step that changes c can use c, n, numbers and sliders, but not z: for c’s own angle there write <code>c.phi</code>, not <code>z.phi</code>.</p>
<p class="note"><b><code>same(x)</code></b> is for the picture’s distance estimate, which follows a few orbits right beside each point: inside it they take the value the point itself has. Use it for a value that jumps from one point to its neighbour, such as a box’s middle.</p>
<p class="note"><b>A value the orbit keeps</b> (a kind of step) gives a name that does not start afresh: what it holds when an iteration ends is what it holds in the next. Any later step may give it a new value, as in <code>total = total + radius</code>.</p>
<p class="note"><b>Kinds:</b> a number, a point with the parts <code>.x .y .z</code>, a quaternion <code>quat(w, x, y, z)</code>, and a matrix <code>mat( )</code> of nine numbers row by row, or of three points as its columns.</p>
<p class="note"><b>Signs:</b> <code>+ − * / ^</code>, and <code>&lt; &gt; &lt;= &gt;= == !=</code>, which give 1 or 0. A number times a point stretches it, a matrix times a point moves it, and two quaternions multiply as quaternions.</p>
<p class="note"><b>Numbers:</b> <code>sin cos tan asin acos atan atan2(y, x) sinh cosh tanh atanh exp log sqrt abs floor ceil round fract sign min max mod pow clamp(x, lo, hi) mix(a, b, t) step smoothstep rad(degrees) deg(radians) if(test, a, b)</code>. Angles are in radians, in what <code>sin</code>, <code>cos</code> and <code>tan</code> take, in what <code>asin</code>, <code>acos</code>, <code>atan</code> and <code>atan2</code> give, and in <code>z.theta</code> and <code>z.phi</code>: write <code>rad(90)</code> for 90°, and <code>deg(z.phi)</code> for an angle in degrees, which is what a box that asks for degrees needs.</p>
<p class="note"><b>Points:</b> <code>len dot cross unit dist abs each(a, b) flat(v) lon(v) lat(v) sph(length, lon, lat) rot(v, axis, angle) invert(v, centre, radius) mirror(v, normal) cpow(v, n) conj(v)</code>.</p>
<p class="note"><b>Quaternions and matrices:</b> <code>asquat(v)</code> reads a point as x + yi + zj and <code>aspoint(q)</code> reads it back; <code>quat(v) vec(q) re(q) conj(q) inv(q) q^n qrot(axis, angle) rot(v, q)</code>; <code>rotmat(axis, angle) transpose(m) det(m) inv(m)</code>.</p>`;

// The menu of a number or a point setting: where its value comes from. Returns { mode, html } for the value the
// step holds now: mode is the menu's choice ('#num' a number, '#xyz' three numbers, '#f' a formula, or the name
// or formula the choice stands for), html the menu's options.
function cuSource(st, sp) {
  const raw = String(st.p[sp.key] === undefined ? sp.def : st.p[sp.key]).trim(), scope = cuProgram().scopes[st.id] || [], flat = t => t.replace(/\s+/g, '');
  const mine = scope.filter(x => x[1] === (sp.type === 'vec' ? 'v' : 's')).map(x => x[0]);
  let opts, mode;
  if (sp.type === 'vec') {
    const pick = sp.picks.find(o => flat(o[1]) === flat(raw));
    opts = [...sp.picks.map(o => [o[1], o[0]]), ['#xyz', 'my own numbers x, y, z'], ...mine.map(name => [name, 'your point ' + name]), ['#f', 'a formula']];
    mode = CUI.formula.has(st.id + ':' + sp.key) ? '#f' : pick ? pick[1] : cuXyz(raw) ? '#xyz' : mine.includes(raw) ? raw : '#f';
  } else {
    // n, and the length and the two angles of every point at hand, each written after its point: of z, of c and of
    // the rule's own points. An angle is in radians, so a setting in degrees gets deg( ) of it. Before the
    // iterations a step that changes c cannot read z, and is not offered what belongs to z. A setting that holds
    // one of the short names (theta for z.theta) shows as that choice.
    const ang = name => (sp.deg ? `deg(${name})` : name), unit = sp.deg ? ', in degrees' : '';
    const polar = (pre, the, its) => [[pre + 'radius', `${pre}radius: how far ${the} is from the middle`], [ang(pre + 'theta'), `${ang(pre + 'theta')}: ${its} angle round the upright axis${unit}`], [ang(pre + 'phi'), `${ang(pre + 'phi')}: the angle of ${its} height${unit}`]];
    const noZ = cuSecOf(st) === 'pre' && st.p.on === 'c';
    const given = [['n', `n (Power dial: ${cuShort(S.n)})`], ...(noZ ? [] : polar('z.', 'z', 'z’s')), ...polar('c.', 'c', 'c’s'), ...scope.filter(x => x[1] === 'v').flatMap(x => polar(x[0] + '.', x[0], x[0] + '’s'))];
    opts = [['#num', 'a number'], ...given, ...mine.map(name => [name, 'your number ' + name]), ['#f', 'a formula']];
    const full = raw.replace(/(^|[^\w.])(radius|theta|phi)(?![\w(])/g, '$1z.$2');
    mode = CUI.formula.has(st.id + ':' + sp.key) ? '#f' : cuIsNum(raw) ? '#num' : given.some(o => o[0] === full) ? full : mine.includes(raw) ? raw : '#f';
  }
  return { mode, html: opts.map(o => `<option value="${cuEsc(o[0])}"${o[0] === mode ? ' selected' : ''}>${cuEsc(o[1])}</option>`).join('') };
}
// The points a step can work on, as the options of its "Works on" menu: z, c, and the points that the steps of its
// section before it have named. A name the step holds that is none of these stays in the menu, so that it shows.
function cuTargets(st) {
  const now = String(st.p.on === undefined ? 'z' : st.p.on), mine = (cuProgram().scopes[st.id] || []).filter(x => x[1] === 'v').map(x => x[0]);
  const opts = [['z', 'the point z'], ['c', 'c'], ...mine.map(name => [name, 'your point ' + name])];
  if (!opts.some(o => o[0] === now)) opts.push([now, now + ' (not a point here)']);
  return opts.map(o => `<option value="${cuEsc(o[0])}"${o[0] === now ? ' selected' : ''}>${cuEsc(o[1])}</option>`).join('');
}
// One setting of a step, as a row of the step's body.
function cuRow(st, sp) {
  const key = sp.key, id = `cu-${st.id}-${key}`, raw = String(st.p[key] === undefined ? sp.def : st.p[key]), lab = cuEsc(sp.label);
  const text = extra => `<input type="text" id="${id}" class="cu-in" data-key="${key}" value="${cuEsc(raw)}" spellcheck="false" autocomplete="off" autocapitalize="off"${extra || ''}>`;
  const box = (own, more) => `<input type="number" ${own ? `id="${id}" ` : ''}class="cu-in cu-nbox" data-num="${key}" step="${sp.step || 'any'}" value="${cuIsNum(raw) ? cuNum(raw) : ''}"${more || ''}>`;
  const range = `<input type="range" class="cu-range" data-num="${key}" aria-label="${lab}, slider">`;
  // a formula has a box as wide as the step, which wraps its text and is as tall as the text needs (cuAreasFit)
  const area = extra => `<textarea class="cu-in cu-area" data-key="${key}" rows="1" spellcheck="false" autocomplete="off" autocapitalize="off"${extra || ''}>${cuEsc(raw)}</textarea>`;
  let cell, under = '';
  if (sp.type === 'choice') cell = `<select id="${id}" class="cu-in" data-key="${key}">${sp.options.map(o => `<option value="${o[0]}"${o[0] === st.p[key] ? ' selected' : ''}>${cuEsc(o[1])}</option>`).join('')}</select>`;
  else if (sp.type === 'target') cell = `<select id="${id}" class="cu-in cu-on-pick" data-key="${key}" title="The point this step works on: the point z, c, or a point that an earlier step of this section has named.">${cuTargets(st)}</select>`;
  else if (sp.type === 'text') cell = area(` id="${id}"`);
  else if (sp.type === 'name') cell = text();
  else if (sp.type === 'any') cell = text(` list="cu-dl-${st.id}"`) + range;
  else if (sp.type === 'num' && (sp.bare || sp.fixed)) cell = cuIsNum(raw) ? box(true) : text();
  else if (sp.type === 'num' && sp.own) cell = box(true) + range;
  else {
    const src = cuSource(st, sp), xyz = sp.type === 'vec' ? cuXyz(raw) : null;
    cell = `<select id="${id}" class="cu-src" data-src="${key}" title="Where this value comes from">${src.html}</select>`;
    if (src.mode === '#f') under = area(` aria-label="${lab}, formula"`);   // on a line of its own, under the menu
    else if (xyz) cell += '<span class="cu-xyz">' + xyz.map((x, k) => `<label>${'xyz'[k]}<input type="number" class="cu-in cu-nbox" data-xyz="${key}" step="0.05" value="${x}" aria-label="${lab}, ${'xyz'[k]}"></label>`).join('') + '</span>';
    else if (src.mode === '#num') cell += box(false, ` aria-label="${lab}, number"`) + range;
  }
  return `<div class="cu-row${sp.type === 'text' ? ' cu-row-text' : ''}" data-row="${key}"><label class="label" for="${id}">${lab}</label><div class="cu-cell">${cell}</div>${under}</div>`;
}
// A formula's box is as tall as its text needs at the width it has now. root: one step; left out, the whole list.
function cuAreasFit(root) {
  for (const t of (root || $('cuSteps')).querySelectorAll('.cu-area')) { t.style.height = 'auto'; t.style.height = t.scrollHeight + 2 + 'px'; }
}
// A slider shows only while its setting is a plain number, and reaches as far as that number.
function cuRangeSync(li, st) {
  li.querySelectorAll('.cu-range').forEach(r => {
    const sp = cuSpec(st, r.dataset.num), raw = st.p[sp.key];
    r.hidden = !cuIsNum(raw);
    if (r.hidden) return;
    let lo = sp.min === undefined ? -4 : sp.min, hi = sp.max === undefined ? 4 : sp.max;
    if (sp.ranged) { lo = cuNum(st.p.min); hi = cuNum(st.p.max); if (!(hi > lo)) { lo = 0; hi = 1; } }
    const x = cuNum(raw);
    lo = Math.min(lo, x); hi = Math.max(hi, x);
    r.min = lo; r.max = hi; r.step = sp.step && !sp.ranged ? sp.step : (hi - lo) / 200; r.value = x;
  });
}
// The names a formula of this step can use, for the lists its boxes offer.
const cuNamesHtml = st => Object.keys(CU_GIVEN).concat(Object.keys(CU_POLAR).flatMap(k => ['z.' + k, 'c.' + k]), (cuProgram().scopes[st.id] || []).map(x => x[0])).map(name => `<option value="${name}">`).join('');
// The three sections of the list, each with a line that says when its steps are taken.
const CU_SEC_SAY = {
  pre: ['Once, before the iterations', 'Taken one time, before iteration 1.'],
  main: ['Every iteration', 'Taken in every iteration, in this order. This is the part that is repeated.'],
  post: ['Once, after the iterations', 'Taken one time, after the last iteration. A point these steps land beyond the bailout radius is thrown out, as in any iteration.'],
};
// Can a step go one place earlier (d = -1) or later (d = 1)? Inside its section it changes places with its
// neighbour. From the end of its section it goes over to the section beside, where its kind may stand there.
function cuCanMove(st, d) {
  const steps = S.custom.steps, other = steps[steps.indexOf(st) + d], sec = cuSecOf(st), k = CU_SECS.indexOf(sec) + d;
  if (other && cuSecOf(other) === sec) return true;
  return k >= 0 && k < CU_SECS.length && st.kind !== 'keep';
}
function cuStepEl(st, i) {
  const B = CU_BLOCKS[st.kind], li = document.createElement('li'), k = i + 1;
  li.className = 'cu-step' + (st.on === false ? ' is-off' : ''); li.dataset.id = st.id;
  const tool = (act, label, title, text, off) => `<button type="button" class="cu-tool" data-act="${act}" aria-label="${label}" title="${title}"${off ? ' disabled' : ''}>${text}</button>`;
  li.innerHTML = `<div class="cu-head"><label class="cu-on" title="Switch this step off to see the solid without it."><input type="checkbox" data-act="on"${st.on === false ? '' : ' checked'} aria-label="Step ${k} is on"><span class="cu-no">${k}</span></label>` +
    `<button type="button" class="cu-title" data-act="show" title="Show this step in the play: one that moves the point is played from its start to its end, and one that only works a value out shows that value.">${st.name ? `${cuEsc(st.name)}<span class="cu-of-kind">${cuEsc(B.title)}</span>` : cuEsc(B.title)}</button><span class="cu-flag">now</span>` +
    tool('remove', `Remove step ${k}`, 'Remove', '✕') + '<span class="cu-tools">' +
    tool('up', `Move step ${k} earlier`, 'Move earlier. From the first place of its section a step goes over to the section before.', '←', !cuCanMove(st, -1)) +
    tool('down', `Move step ${k} later`, 'Move later. From the last place of its section a step goes over to the section after.', '→', !cuCanMove(st, 1)) +
    (B.basic ? '' : tool('break', `Break step ${k} down`, B.plain ? 'Show this formula as its single operations, each a step of its own.' : 'Show this step as the formulas it is made of, each a step you can change. Those can be broken down again.', 'Break down')) +
    (st.kind === 'formula' ? '' : tool('reset', `Reset step ${k}`, 'Put the settings of this step back to what a new step of this kind has. A name it gives stays.', 'Reset')) +
    tool('kind', `Change the kind of step ${k}`, 'Make this step another kind, or one of your saved steps, here in its place. Settings that both kinds have are kept.', 'Change') +
    tool('save', `Save step ${k} under a name`, 'Keep this step with its settings under a name. It then stands in the list of steps, under “Your saved steps”, to be added again anywhere.', 'Save') +
    '</span></div>' +
    (B.grid ? `<div class="cu-body">${B.params.filter(sp => sp.type === 'target').map(sp => cuRow(st, sp)).join('')}</div>` : '') +
    `<div class="cu-body${B.grid ? ' cu-grid' : ''}">${B.params.filter(sp => !B.grid || sp.type !== 'target').map(sp => cuRow(st, sp)).join('')}</div><datalist id="cu-dl-${st.id}">${cuNamesHtml(st)}</datalist><p class="err cu-err" hidden></p>`;
  cuRangeSync(li, st);
  return li;
}
function cuRender() {
  const host = $('cuSteps'), steps = S.custom.steps;
  host.textContent = '';
  for (const sec of CU_SECS) {
    const box = document.createElement('div'), mine = steps.filter(st => cuSecOf(st) === sec);
    box.className = 'cu-sec'; box.dataset.sec = sec;
    box.innerHTML = `<p class="cu-sec-head"><span class="label">${CU_SEC_SAY[sec][0]}</span> <span class="note">${cuEsc(CU_SEC_SAY[sec][1])}${mine.length ? '' : ' No step stands here.'}</span></p><ol class="cu-steps"></ol>`;
    for (const st of mine) box.lastElementChild.appendChild(cuStepEl(st, steps.indexOf(st)));
    host.appendChild(box);
  }
  $('cuEmpty').hidden = steps.length > 0;
  CUI.now = null; CUI.barSig = '';
  cuAreasFit();
}
// The menus and name lists follow the rule without the boxes being made again: a name may have come or gone, and
// the Power dial may have moved.
function cuOptionsSync() {
  document.querySelectorAll('#cuSteps .cu-step').forEach(li => {
    const st = S.custom.steps[cuStepAt(li.dataset.id)];
    if (!st) return;
    li.querySelectorAll('.cu-src').forEach(sel => { const src = cuSource(st, cuSpec(st, sel.dataset.src)); sel.innerHTML = src.html; sel.value = src.mode; });
    li.querySelectorAll('.cu-on-pick').forEach(sel => { sel.innerHTML = cuTargets(st); });
    li.querySelector('datalist').innerHTML = cuNamesHtml(st);
  });
}
// Under each step that cannot be read, why.
function cuErrors() {
  const errs = cuProgram().errs;
  document.querySelectorAll('#cuSteps .cu-step').forEach(li => {
    const p = li.querySelector('.cu-err'), msg = errs[li.dataset.id] || '';
    p.textContent = msg ? 'This step is left out: ' + msg : ''; p.hidden = !msg;
    li.classList.toggle('is-bad', !!msg);
  });
}
function cuSnap() {
  const t = cuRuleText();
  if (CUI.undo[CUI.undo.length - 1] !== t) CUI.undo.push(t);
  if (CUI.undo.length > 40) CUI.undo.shift();
}
// After the rule changed. render: the list itself changed (a step added, moved, removed, a menu turned), not only a value.
function cuChanged(render) {
  S.custom.rev = (S.custom.rev || 0) + 1;
  if (render) cuRender();
  cuStore();
  cuErrors();
  $('cuUndo').disabled = CUI.undo.length === 0;
  if ($('cuTextBox').open) $('cuText').value = cuRuleText();
  if (ap().id === 'custom') uiApproachParam();
  cuBarSync(); cuOverDraw();
}
function cuUse(rule) {
  Object.assign(S.custom, { steps: rule.steps, next: rule.next, bail: rule.bail, rough: !!rule.rough, play: null });
  CUI.formula.clear(); cuPlayStop();
  cuChanged(true);
}
function cuSay(text) { const p = $('cuSay'); p.textContent = text || ''; p.hidden = !text; }
// Makes a step another kind where it stands. A setting that both kinds have (the same key, the same sort of value)
// is kept, and so is the name the step gives; the rest are the new kind's own. A kind that belongs to one section
// (a value the orbit keeps) takes the step to that section.
function cuSwap(st, kind) {
  const A = CU_BLOCKS[st.kind], B = CU_BLOCKS[kind], p = {}, named = blk => blk.params.find(sp => sp.type === 'name');
  for (const sp of B.params) {
    const old = A.params.find(o => o.key === sp.key && o.type === sp.type), x = old ? st.p[sp.key] : undefined;
    p[sp.key] = x !== undefined && (sp.type !== 'choice' || sp.options.some(o => o[0] === x)) ? x : sp.def;
  }
  const a = named(A), b = named(B);
  if (b) p[b.key] = a ? st.p[a.key] : cuFresh(cuTaken(S.custom.steps))(b.def);
  for (const f of [...CUI.formula]) if (f.startsWith(st.id + ':')) CUI.formula.delete(f);
  st.kind = kind; st.p = p; delete st.name;   // it is no longer the saved step it was named after
  // a kind that belongs to one section takes the step there
  cuSetSec(st, cuSecOf(st));
  S.custom.steps = cuSorted(S.custom.steps);
}
function cuSetSec(st, sec) { if (sec === 'main') delete st.sec; else st.sec = sec; }

// The bar under the picture: which iteration is on show, how far through its steps, and the buttons that move it.
const CU_SPEEDS = { slow: 3.2, normal: 1.6, fast: 0.8 };   // seconds a play takes for one step
function cuPlayStop() { CUI.playing = false; CUI.until = null; const b = $('cuPlay'); if (b) b.textContent = 'Play'; }
// A switched-off step that is tried (cuPeek) has a place of its own on the bar for as long as the play stands in it.
// cuPeekSlot is that place, { sec, a }: from a to a + 1 in u (null: no step is tried). cuPeekOut is where a place u
// of the bar lies once the step is no longer counted: what came after it is one lower, and among the steps taken
// once before, which are counted back from 0, what came before it is one higher. cuUnpeek ends the trial: the play
// then stands where that step is, without it.
function cuPeekSlot() {
  const id = cuPeek();
  if (id === null) return null;
  const me = cuProgram().run.find(s => s.id === id), list = cuPlayable(me.sec);
  return { sec: me.sec, a: (me.sec === 'pre' ? -list.length : me.sec === 'post' ? cuMoving().length : 0) + list.findIndex(s => s.id === id) };
}
const cuPeekOut = (slot, u) => (slot.sec === 'pre' ? (u <= slot.a ? u + 1 : Math.max(u, slot.a + 1)) : u >= slot.a + 1 ? u - 1 : Math.min(u, slot.a));
function cuUnpeek() {
  const pl = S.custom.play, slot = cuPeekSlot();
  if (pl && pl.peek !== undefined) S.custom.play = { pass: pl.pass, u: slot ? cuPeekOut(slot, pl.u) : pl.u };
}
function cuGo(pass, u, look) {
  // a move out of the place of the step that is tried, or to another iteration, ends the trial
  const slot = cuPeekSlot(), was = S.custom.play;
  let peek;
  if (slot) {
    if (clamp(Math.round(pass), cuFirst(), cuPasses()) === was.pass && u >= slot.a && u <= slot.a + 1) peek = was.peek;
    else { u = cuPeekOut(slot, u); S.custom.play = { pass: was.pass, u: was.u }; }
  }
  const np = cuPasses();
  pass = clamp(Math.round(pass), cuFirst(), np); u = clamp(u, cuLow(pass), cuHigh(pass));
  S.custom.play = peek !== undefined ? { pass, u, peek } : pass >= np && u >= cuHigh(np) ? null : { pass, u };
  CUI.look = look === undefined || !S.custom.play ? null : look;
  cuBarSync(); cuOverDraw();
  // The picture changes only when a pass is done (cuPlayPic). Between those moments the dots alone are drawn
  // afresh, and the picture goes on getting finer.
  const pic = JSON.stringify(cuPlayPic());
  if (pic !== CUI.pic) { CUI.pic = pic; touch(); }
}
function cuPlayFrame(now) {
  CUI.raf = 0;
  if (!CUI.playing || !cuOn()) { cuPlayStop(); return; }
  // a frame's own time can lie before the click that started the play: the play never runs backwards
  const at = cuPlayAt(), hi = cuHigh(at.pass), dt = clamp((now - CUI.last) / 1000, 0, 0.1);
  CUI.last = now;
  let u = at.u + dt / (CU_SPEEDS[S.custom.speed] || CU_SPEEDS.normal);
  const stop = CUI.until === null ? hi : Math.min(CUI.until, hi);
  // Play stops when the iteration is done, or runs on into the next one where that is asked for (through). One
  // step that is shown by itself (until) always ends with that step.
  if (u >= stop && CUI.until === null && S.custom.through !== false && at.pass < cuPasses()) { cuGo(at.pass + 1, cuLow(at.pass + 1)); CUI.raf = requestAnimationFrame(cuPlayFrame); return; }
  if (u >= stop) { u = stop; cuPlayStop(); }
  cuGo(at.pass, u);
  if (CUI.playing) CUI.raf = requestAnimationFrame(cuPlayFrame);
}
function cuBarSync() {
  if (!cuOn() || !$('cuAt')) return;
  const at = cuPlayAt(), mov = cuMoving(), m = mov.length, np = cuPasses(), lead = cuLead(), first = cuFirst(), lo = cuLow(at.pass), hi = cuHigh(at.pass), steps = S.custom.steps;
  const sig = [at.pass, at.u, at.end, np, lead, lo, hi, S.iter, S.custom.bail, S.custom.rough, S.custom.rev, CUI.playing, CUI.look, cuPeek()].join('|');
  if (sig === CUI.barSig) return;
  CUI.barSig = sig;
  const it = $('cuIt'), all = $('cuItAll'), slider = $('cuAt');
  it.min = 1; it.max = np + lead;
  if (document.activeElement !== it) it.value = at.pass + lead;
  if (document.activeElement !== all) all.value = S.iter;
  const top = hi > lo ? hi : lo + 1;   // an iteration with no place to stand in still has a slider, which stays at its start
  slider.min = lo; slider.max = top; slider.disabled = !m || hi <= lo;
  if (Math.abs(+slider.value - at.u) > 1e-4) slider.value = at.u;
  $('cuEnd').classList.toggle('is-on', at.end); $('cuEnd').setAttribute('aria-pressed', String(at.end));
  const start = !at.end && at.pass === first && at.u === lo;
  $('cuFirst').classList.toggle('is-on', start); $('cuFirst').setAttribute('aria-pressed', String(start));
  for (const id of ['cuPlay', 'cuStepPrev', 'cuStepNext']) $(id).disabled = !m;
  if (document.activeElement !== $('cuBail')) $('cuBail').value = cuShort(S.custom.bail);
  $('cuRoughOn').checked = !!S.custom.rough;
  $('cuBailR').value = S.custom.bail;
  // One mark on the slider for every step a play can stand in, with the step's number in the list. The first
  // iteration has the steps taken once before in front of it, and the last has those taken once after behind it.
  // The iteration of a Mandelbrot picture that only puts each point on its c has no step of its own to stand in.
  const no = id => cuStepAt(id) + 1, span = top - lo;
  const marks = [...(lo < 0 ? cuPlayable('pre').map((s, j) => [lo + j + 1, s]) : []), ...(hi >= m ? mov.map((s, j) => [j + 1, s]) : []), ...(hi > m ? cuPlayable('post').map((s, j) => [m + j + 1, s]) : [])];
  // the mark of a switched-off step that is tried stands in brackets
  const peek = cuPeek(), ticks = marks.map(([u, s]) => u + ':' + no(s.id)).join(',') + '|' + peek;
  if ($('cuTicks').dataset.sig !== ticks) {
    $('cuTicks').dataset.sig = ticks;
    $('cuTicks').innerHTML = marks.map(([u, s]) => `<button type="button" data-u="${u}" style="left:${(100 * (u - lo) / span).toFixed(2)}%" title="To the end of step ${no(s.id)}${s.id === peek ? ', which is switched off and only tried here' : ''}">${s.id === peek ? `(${no(s.id)})` : no(s.id)}</button>`).join('');
  }
  // the words, and the step they are about
  const w = cuPlaySec(at), whole = Math.abs(w.x - Math.round(w.x)) < 1e-6, j = whole ? Math.round(w.x) - 1 : Math.floor(w.x), cur = m && j >= 0 && !at.end ? w.list[j] : null;
  const named = st => { const t = CU_BLOCKS[st.kind].title; return `step ${no(st.id)}, ${st.name ? `“${st.name}”` : t[0].toLowerCase() + t.slice(1)}` + (st.p.on && st.p.on !== 'z' ? ` (on ${st.p.on})` : ''); };
  const title = s => named(steps[cuStepAt(s.id)]);
  const I = at.pass + lead, far = cuShort(S.custom.bail);
  // a step that moves no point and is looked at: the play stands where that step is
  const seen = at.end || CUI.look === null ? null : steps[cuStepAt(CUI.look)] || null, sec = seen ? cuSecOf(seen) : w.sec;
  const where = sec === 'pre' ? 'Before the iterations' : sec === 'post' ? 'After the last iteration' : `Iteration ${I}`;
  // the iteration of a Mandelbrot picture that moves no dot, in a sentence
  const still = 'In a Mandelbrot picture z starts at the middle, so iteration 1 only puts each dot on its own c, where it is drawn already.';
  const begin = `Every point no further than ${far} from the middle is in.` + (lead && at.pass === first ? ' ' + still : '');
  // a switched-off step that is tried: the play shows what it would do, and your approach stays without it
  const tried = cur && cur.id === peek && !seen;
  $('cuNow').textContent = seen ? `${where}, at ${named(seen)}. It moves no point: what it works out is shown for the ringed dot.`
    : tried ? `${where}, ${whole ? 'after trying' : 'trying'} ${title(cur)}. It is switched off, so your approach leaves it out: this is only what it would do here.`
    : !m ? 'No step of “Every iteration” that is switched on moves the point, so there is nothing to play.'
    : at.end ? `The finished solid: all ${S.iter} iterations${cuHasPost() ? ', and the steps taken once after them' : ''}. It is every starting point that was never thrown out.`
    : w.sec === 'pre' && w.x === 0 ? `The very start, before ${title(w.list[0])}. Every point no further than ${far} from the middle is in.`
    : w.sec === 'pre' ? `Before the iterations, ${whole ? 'after' : 'during'} ${title(cur)}.` + (w.x < w.list.length ? '' : lead ? ' ' + still : ` Iteration ${I} is about to begin.`)
    : w.sec === 'post' ? `After the last iteration, ${whole ? 'after' : 'during'} ${title(cur)}.`
    : at.pass === first && at.u === 0 ? `The start. ${begin}`
    : whole && at.u === 0 ? `Iteration ${I} is about to begin. On show is what is left after ${I - 1}.`
    : whole ? `Iteration ${I}, after ${title(cur)}.` + (at.u < m ? '' : hi > m ? ' The iterations are done. The steps taken once, after them, come next.' : ` That is what is left after ${I} iteration${I === 1 ? '' : 's'}.`)
    : `Iteration ${I}, during ${title(cur)}.`;
  const now = seen ? String(seen.id) : cur ? String(cur.id) : w.sec === 'pre' && w.list[0] && !at.end ? String(w.list[0].id) : null;
  if (now !== CUI.now) {
    CUI.now = now;
    document.querySelectorAll('#cuSteps .cu-step').forEach(li => li.classList.toggle('is-now', li.dataset.id === now));
    const li = now && document.querySelector(`#cuSteps .cu-step[data-id="${now}"]`), dock = $('cuDock');
    // bring the marked step into view inside the list of steps, which scrolls by itself on a wide window
    if (li && dock.scrollHeight > dock.clientHeight + 4) {
      // a step in the first row of its section comes into view with the section's heading
      const box = li.closest('.cu-sec'), top = box && box.querySelector('.cu-step'), ref = top && top.offsetTop === li.offsetTop ? box : li;
      const a = li.getBoundingClientRect(), r = ref.getBoundingClientRect(), b = dock.getBoundingClientRect();
      const bar = dock.querySelector('.cu-tools-row').offsetHeight + 6;   // the tools stay at the top of the list
      if (r.top < b.top + bar || a.bottom > b.bottom) dock.scrollTop += r.top - b.top - bar;
    }
  }
}
// Show or put away what belongs to the custom approach, after the approach, the mode or the power changed.
function customSync() {
  const on = cuOn();
  // The centre of a Mandelbrot picture. The lab's own rules turn about the middle of their solid, at -0.6 along x,
  // and the custom approach about the origin (camHome). A centre that is still where the page put it goes along
  // when the approach changes between the two; one that was moved stays where it is.
  // The distance likewise. The custom approach's start view stands back for the ball its dots start in: a camera
  // that is still at the start distance of the approach it leaves goes to the start distance of the one it comes to.
  const home = S.mode === 'k' ? null : camHome();
  if (on !== CUI.wasOn) {
    CUI.wasOn = on;
    const h = camHome().target, t = cam.target, known = p => p[1] === 0 && p[2] === 0 && (p[0] === 0 || p[0] === -0.6);
    if (S.mode === 'm' && known(h)) {
      if (known(t) && t[0] !== h[0]) { cam.target = h.slice(); touch(); }
      if (S.v2.y === 0 && (S.v2.x === 0 || S.v2.x === -0.6)) S.v2.x = h[0];
    }
    if (home && CUI.home !== null && !S.view.fly && cam.dist === CUI.home && cam.dist !== clampDist(home.dist)) { cam.dist = clampDist(home.dist); touch(); }
  }
  CUI.home = home ? clampDist(home.dist) : null;
  document.body.classList.toggle('is-custom', on);
  $('cuBar').hidden = $('cuDock').hidden = !on;
  if (on && cuBoth()) $('juliaPanel').hidden = false;   // the Julia half takes its c from this panel
  if (!on) { cuPlayStop(); return; }
  if (document.activeElement !== $('cuN')) $('cuN').value = cuShort(S.n);
  cuOptionsSync();
  CUI.barSig = ''; cuBarSync();
}

function customInit() {
  const C = S.custom, opt = (v, t) => `<option value="${v}">${cuEsc(t)}</option>`;
  $('pd-custom').innerHTML = `<p class="note">Your steps stand under the picture, with the bar that plays them. A step works on the point z and hands it to the next one. One run through the steps is one iteration.</p>
<details class="cu-more" open><summary>What a formula can use</summary>${CU_HELP}</details>
<details class="cu-more" id="cuTextBox"><summary>Your approach as text</summary>
  <p class="note">Copy this text to keep an approach or to send it to someone. To use an approach you were sent, paste it here and press the button.</p>
  <textarea id="cuText" rows="5" spellcheck="false" aria-label="Your approach as text"></textarea>
  <div class="row-btns"><button class="btn" id="cuTextUse" type="button">Use this text</button></div>
</details>`;
  $('cuBar').innerHTML = `<div class="cu-bar-row">
  <span class="label">Iteration</span>
  <button class="btn" id="cuItPrev" type="button" aria-label="The iteration before" title="The iteration before">◀</button>
  <input type="number" id="cuIt" class="cu-in cu-nbox" step="1" aria-label="The iteration on show">
  <span class="cu-of">of</span>
  <input type="number" id="cuItAll" class="cu-in cu-nbox" step="1" min="2" max="400" aria-label="Iterations in all" title="How many iterations the finished solid takes: the Iterations dial of the page.">
  <button class="btn" id="cuItNext" type="button" aria-label="The iteration after" title="The iteration after">▶</button>
  <span class="cu-gap"></span>
  <button class="btn" id="cuFirst" type="button" aria-pressed="false" title="Back to the very start: before the first iteration, and before the steps taken once before it">Start</button>
  <button class="btn" id="cuStepPrev" type="button" title="Back one step">◀ Step</button>
  <button class="btn cu-play" id="cuPlay" type="button" title="Plays the steps of one iteration. Press again for the next iteration.">Play</button>
  <button class="btn" id="cuStepNext" type="button" title="On one step">Step ▶</button>
  <button class="btn" id="cuEnd" type="button" aria-pressed="true" title="All the iterations: the solid as the page usually shows it">Finished solid</button>
  <label class="cu-group" title="How fast Play takes the steps."><span class="label">Speed</span><select id="cuSpeed">${opt('slow', 'Slow')}${opt('normal', 'Normal')}${opt('fast', 'Fast')}</select></label>
  <label class="check" title="Ticked: Play runs on from one iteration into the next, to the finished solid. Unticked: Play stops when the iteration is done, and pressing it again takes the next one."><input type="checkbox" id="cuThrough"> <span>Play all iterations</span></label>
</div>
<div class="cu-track"><input type="range" id="cuAt" min="0" max="1" step="0.005" value="0" aria-label="How far through the steps of this iteration"><div class="cu-ticks" id="cuTicks"></div></div>
<p class="cu-now" id="cuNow" role="status"></p>
<div class="cu-bar-row cu-bar-small">
  <label class="label" for="cuBail">Bailout radius</label>
  <input type="number" id="cuBail" class="cu-in cu-nbox" min="1.2" max="64" step="0.1">
  <input type="range" id="cuBailR" class="cu-range" min="1.2" max="16" step="0.1" aria-label="Bailout radius, slider">
  <span class="note">A point is thrown out, and its dot goes, when an iteration ends with it further than this from the middle: beyond the dashed circle.</span>
</div>
<div class="cu-bar-row cu-bar-small">
  <label class="cu-group" title="What a play shows. Dots: some points of the solid, each drawn where the steps have carried it by now, with the picture faint behind them. Surface: the solid alone. Both: the dots over the solid at its full strength."><span class="label">Show</span><select id="cuSee">${opt('dots', 'Dots')}${opt('skin', 'Surface')}${opt('both', 'Both')}</select></label>
  <label class="cu-group" title="How strongly the dots are drawn, from faint to full."><span class="label">Dots opacity</span><input type="range" id="cuDotsA" class="cu-range" min="5" max="100" step="5"></label>
  <label class="cu-group" title="How strongly the surface is drawn, from see-through to full. With Show at Dots it is fainter still, so that the dots stand out."><span class="label">Surface opacity</span><input type="range" id="cuSkinA" class="cu-range" min="0" max="100" step="5"></label>
  <label class="cu-group" title="How many dots there are when the first iteration begins: the Learn tab’s four choices, with as many dots as it has."><span class="label">How many</span><select id="cuCount">${opt('few', 'Few')}${opt('some', 'Some')}${opt('many', 'Many')}${opt('most', 'Very many')}</select></label>
  <label class="cu-group" title="Where the dots start: on a full grid, on level sheets one above the other, on shells (one ball inside the other), or on sheets and shells together."><span class="label">Laid out as</span><select id="cuLay">${opt('grid', 'Full grid')}${opt('sheets', 'Sheets')}${opt('shells', 'Shells')}${opt('both', 'Sheets and shells')}</select></label>
  <label class="cu-group" title="The dots start in a ball of this radius about the middle, and the layout is stretched to fill it. It is never larger than the bailout radius. Reset view shows all of this ball."><span class="label">Out to</span><input type="number" id="cuReach" class="cu-in cu-nbox" min="0.25" max="16" step="0.25" aria-label="How far from the middle the dots start"></label>
  <label class="cu-group" title="What a dot’s colour says about the place it started from: which way from the middle, how high, how far from the middle, or how far and how high together. A dot keeps its colour."><span class="label">Coloured by</span><select id="cuTint">${opt('dir', 'Which way it started')}${opt('height', 'How high it started')}${opt('dist', 'How far out it started')}${opt('mix', 'How far out and how high')}</select></label>
  <label class="cu-group" title="Whose whole path is drawn: the way a dot has come from its starting place, iteration by iteration, and through the steps of the iteration on show."><span class="label">Orbits</span><select id="cuOrbits">${opt('few', 'A few dots, drawn larger')}${opt('all', 'Every dot')}${opt('none', 'None')}</select></label>
  <label class="check" title="Ticked: as dots are thrown out, dots that start between the ones that are left take their place, so there are always about as many. Such a dot has taken every step so far and was only not drawn. Not ticked: the dots of the start, fewer with every iteration."><input type="checkbox" id="cuRefill" checked> <span>Add new dots as dots are thrown out</span></label>
</div>
<div class="cu-bar-row cu-bar-small">
  <label class="check" title="What the step on show works with: the axis of a rotation, the plane of a mirror, the sphere of an inversion, the arrow of a slide. One dot gets a ring, and its way through the step is drawn."><input type="checkbox" id="cuGuidesOn" checked> <span>Guides</span></label>
  <label class="check" title="One number in place of the neighbouring orbits when the finished solid is drawn: quicker and plainer. Many of the lab’s own approaches are drawn this way, and they come with it ticked. A play always uses the fine estimate, and so does an approach with a step taken once that moves the point."><input type="checkbox" id="cuRoughOn"> <span>Plain distance estimate</span></label>
  <label class="check" title="The Mandelbrot picture on the left and the Julia picture on the right, with one camera. The Julia half uses the c of the Julia panel, which then shows in the column on the right."><input type="checkbox" id="cuBothOn"> <span>Mandelbrot and Julia side by side</span></label>
  <span class="note" id="cuDotsSay" hidden></span>
</div>`;
  $('cuDock').innerHTML = `<div class="cu-tools-row">
  <span class="cu-group"><button type="button" class="cu-in cu-pick-btn" id="cuAddSel" value="" aria-haspopup="dialog" aria-expanded="false" title="What Add step adds: a kind of step, or one of your saved steps. Click for the list, which can be searched."></button><select id="cuAddSec" aria-label="The section the new step goes to" title="Where the new step goes: among the steps of every iteration, or among those taken once, before or after the iterations.">${opt('main', 'to every iteration')}${opt('pre', 'to once, before')}${opt('post', 'to once, after')}</select><button class="btn" id="cuAddBtn" type="button">Add step</button></span>
  <span class="cu-group"><select id="cuStart" aria-label="An approach to load: one you saved, or one to start again from"></select><button class="btn" id="cuStartBtn" type="button" title="Puts these steps in the place of yours. Undo brings yours back.">Load</button><button class="btn" id="cuDelBtn" type="button" hidden title="Takes the chosen saved approach off the list. Your steps on the page stay.">Delete</button></span>
  <span class="cu-group"><input type="text" id="cuSaveName" class="cu-in" maxlength="40" placeholder="Name for this approach" aria-label="The name to save this approach under" autocomplete="off" spellcheck="false"><button class="btn" id="cuSaveBtn" type="button" title="Keeps the steps as they are now, under this name, in the list beside it. Saved approaches stay in this browser.">Save</button></span>
  <button class="btn" id="cuUndo" type="button" disabled>Undo</button>
  <span class="cu-group"><label class="label" for="cuN" title="The Power dial of the page. A step whose menu says “n (Power dial)” follows it.">Power n</label><input type="number" id="cuN" class="cu-in cu-nbox" step="0.1"></span>
  <p class="note cu-say" id="cuSay" role="status" hidden></p>
</div>
<div class="cu-secs" id="cuSteps"></div>
<p class="note" id="cuEmpty" hidden>There are no steps, so every point stays where it is. Add a step, or load an approach to start from.</p>`;
  const list = $('cuSteps'), at = e => { const li = e.target.closest('.cu-step'); return li ? { li, i: cuStepAt(li.dataset.id), st: C.steps[cuStepAt(li.dataset.id)] } : {}; };
  // a number moved, by its box or its slider, or one of a point's three numbers: nothing else changes, so the picture follows at once
  // A formula is one line, however many rows its box shows: Enter takes it as it is, and a line break that comes
  // with pasted text becomes a space. When the list gets another width the boxes are fitted again, a frame later,
  // so that the list's new height is no answer to its own change.
  list.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.classList.contains('cu-area')) { e.preventDefault(); e.target.blur(); } });
  let wide = 0;
  new ResizeObserver(() => { if (list.clientWidth !== wide) { wide = list.clientWidth; requestAnimationFrame(() => cuAreasFit()); } }).observe(list);
  list.addEventListener('input', e => {
    const t = e.target, { li, st } = at(e), key = t.dataset.num || t.dataset.xyz;
    if (li && t.classList.contains('cu-area')) { if (/[\r\n]/.test(t.value)) t.value = t.value.replace(/\s*[\r\n]+\s*/g, ' '); cuAreasFit(li); return; }
    if (!st || !key) return;
    let next;
    if (t.dataset.num) { if (t.value === '' || !isFinite(+t.value)) return; next = cuShort(t.value); }
    else {
      const boxes = [...li.querySelectorAll(`[data-xyz="${key}"]`)];
      if (boxes.some(b => b.value === '' || !isFinite(+b.value))) return;
      next = `vec(${boxes.map(b => cuShort(b.value)).join(', ')})`;
    }
    if (!CUI.hot) { cuSnap(); CUI.hot = true; }
    st.p[key] = next;
    if (t.dataset.num) li.querySelectorAll(`[data-num="${key}"], [data-key="${key}"]`).forEach(o => { if (o !== t) o.value = next; });
    cuChanged(false);
  });
  list.addEventListener('change', e => {
    const t = e.target, { li, st } = at(e);
    if (!st) return;
    cuSay('');
    if (t.dataset.act === 'on') { cuSnap(); st.on = t.checked; li.classList.toggle('is-off', !t.checked); cuChanged(false); return; }
    if (t.dataset.num || t.dataset.xyz) { CUI.hot = false; cuRangeSync(li, st); cuOptionsSync(); cuOverDraw(); return; }   // taken already, as it moved
    if (t.dataset.src) {
      const key = t.dataset.src, sp = cuSpec(st, key), v = t.value, f = st.id + ':' + key;
      cuSnap();
      CUI.formula.delete(f);
      if (v === '#f') CUI.formula.add(f);
      else if (v === '#num') { if (!cuIsNum(st.p[key])) st.p[key] = cuIsNum(sp.def) ? sp.def : cuShort(S.n); }
      else if (v === '#xyz') { if (!cuXyz(st.p[key])) st.p[key] = 'vec(1, 0, 0)'; }
      else st.p[key] = v;
      cuChanged(true);
      const box = list.querySelector(`.cu-step[data-id="${st.id}"] [data-row="${key}"] .cu-in`) || $(`cu-${st.id}-${key}`);
      if (box) box.focus({ preventScroll: true });
      return;
    }
    if (t.dataset.key) {
      const sp = cuSpec(st, t.dataset.key);
      cuSnap();
      st.p[sp.key] = t.value.trim() || sp.def; t.value = st.p[sp.key];
      cuChanged(false);
      cuRangeSync(li, st); cuOptionsSync(); cuAreasFit(li);
    }
  });
  list.addEventListener('click', e => {
    const b = e.target.closest('.cu-tool, .cu-title'), { i, st } = b ? at(e) : {};
    if (!st) return;
    cuSay('');
    const act = b.dataset.act;
    if (act === 'show') {
      cuUnpeek();   // a step that was tried before this click is left first
      const me = cuProgram().run.find(s => s.id === st.id), sec = cuSecOf(st), now = cuPlayAt(), np = cuPasses(), held = S.custom.play;
      if (cuProgram().errs[st.id] || !me) { cuSay('This step cannot be read yet, so the play has no place for it.'); return; }
      // A step that is switched off and changes a point is tried: for as long as the play stands in it, it counts
      // among the steps a play can stand in, and the rule itself stays without it.
      const tried = st.on === false && !!me.on;
      if (tried) S.custom.play = { pass: now.pass, u: now.u, peek: st.id };
      const mov = cuMoving(), list = cuPlayable(sec), j = list.findIndex(s => s.id === st.id);
      const none = text => { if (tried) S.custom.play = held; cuSay(text); };
      if (!mov.length) { none('No step of “Every iteration” that is switched on moves the point, so there is no play to stand in.'); return; }
      if (!list.length) { none('No step of this section moves the point or changes c, so the play has no place there to stand in.'); return; }
      cuPlayStop();
      // Where the section lies on the bar. The steps taken once stand before the first pass and after the last;
      // a step of every iteration is shown in the iteration on show, or in the first that moves a dot: from the
      // finished solid, and from the iteration of a Mandelbrot picture that only puts each point on its c.
      const base = sec === 'pre' ? -list.length : sec === 'post' ? mov.length : 0, pass = sec === 'pre' ? cuFirst() : sec === 'post' ? np : now.end ? 1 : Math.max(1, now.pass);
      if (j < 0) {
        // A step that moves no point has nothing to play. The play stands where the step is (before the next step
        // of its section that a play can stand in), and what the step works out is shown for the ringed dot.
        const k = list.findIndex(s => s.ord > me.ord);
        cuGo(sec === 'main' && k < 0 && np > 1 ? Math.min(pass, np - 1) : pass, base + (k < 0 ? list.length : k), st.id);
        cuSay(S.custom.play ? 'This step moves no point. What it works out is shown for the ringed dot, in the line under the bar and, for a point, as an arrow over the picture.'
          : 'This step comes after the last step that moves the point, and nothing follows it, so there is no place to stand and look at it.');
        return;
      }
      // play this step from its start to its end
      if (tried) { S.custom.play = { pass, u: base + j, peek: st.id }; cuSay('This step is switched off. The play shows what it would do here, and your approach stays without it.'); }
      cuGo(pass, base + j);
      CUI.until = base + j + 1; CUI.playing = true; CUI.last = performance.now(); $('cuPlay').textContent = 'Pause';
      if (!CUI.raf) CUI.raf = requestAnimationFrame(cuPlayFrame);
      return;
    }
    if (act === 'save') {
      // the step's name gives way to a box for the name to keep it under, with Save and Cancel beside it
      const li = b.closest('.cu-step'), name = li.querySelector('.cu-title'), row = document.createElement('span');
      if (li.classList.contains('is-naming')) return;
      row.className = 'cu-naming';
      row.innerHTML = `<input type="text" class="cu-in" maxlength="40" spellcheck="false" autocomplete="off" aria-label="The name to save step ${i + 1} under" value="${cuEsc(st.name || CU_BLOCKS[st.kind].title)}">` +
        '<button type="button" class="cu-tool" data-act="save-ok">Save</button><button type="button" class="cu-tool" data-act="save-no">Cancel</button>';
      name.hidden = true; name.after(row); li.classList.add('is-naming');
      const box = row.firstChild;
      box.addEventListener('keydown', ev => {
        if (ev.key === 'Enter') { ev.preventDefault(); row.querySelector('[data-act=save-ok]').click(); }
        else if (ev.key === 'Escape') row.querySelector('[data-act=save-no]').click();
      });
      box.focus(); box.select();
      cuSay('Type a name for this step, then press Save or Enter.');
      return;
    }
    if (act === 'save-ok' || act === 'save-no') {
      const li = b.closest('.cu-step'), row = li.querySelector('.cu-naming'), as = row.querySelector('input').value.trim();
      row.remove(); li.querySelector('.cu-title').hidden = false; li.classList.remove('is-naming');
      if (act === 'save-ok' && as) cuKeep(st, as);
      return;
    }
    if (act === 'kind') {
      // the list of kinds opens under the button; a choice changes the step where it stands
      cuPickOpen(b, st.kind, kind => {
        const mine = cuKeptAt(kind);
        if (!mine && (kind === st.kind || !CU_BLOCKS[kind])) return;
        cuSnap();
        if (mine) cuTake(st, mine); else cuSwap(st, kind);
        cuChanged(true);
        const again = list.querySelector(`.cu-step[data-id="${st.id}"] [data-act="kind"]`);
        if (again) again.focus({ preventScroll: true });
      });
      return;
    }
    if (act === 'break') {
      let parts;
      try { parts = st.kind === 'formula' ? cuSplit(st.p.text, cuProgram().scopes[st.id] || [], cuTaken(C.steps)) : cuBroken(st, cuTaken(C.steps)); }
      catch (err) { cuSay('This step cannot be broken down yet: ' + err.message); return; }
      if (!parts) { cuSay('This step is one operation already.'); return; }
      if (C.steps.length - 1 + parts.length > CU_MAX_STEPS) { cuSay(`An approach can hold ${CU_MAX_STEPS} steps, and breaking this one down would pass that.`); return; }
      cuSnap();
      C.steps.splice(i, 1, ...parts.map(x => Object.assign(cuStepOf(x.kind, x.p, C.next++, cuSecOf(st)), { on: st.on !== false })));
    } else if (act === 'reset') {
      // back to the settings of a new step of this kind; the name it gives stays, since later steps may use it
      cuSnap();
      for (const sp of CU_BLOCKS[st.kind].params) { if (sp.type !== 'name') st.p[sp.key] = sp.def; CUI.formula.delete(st.id + ':' + sp.key); }
      delete st.name;
    } else {
      cuSnap();
      if (act === 'remove') C.steps.splice(i, 1);
      else {
        // inside its section a step changes places with its neighbour; from the end of the section it goes over
        // to the section beside, and its place in the list stays
        const d = act === 'up' ? -1 : 1, other = C.steps[i + d], sec = cuSecOf(st);
        if (!cuCanMove(st, d)) return;
        if (other && cuSecOf(other) === sec) C.steps.splice(i + d, 0, C.steps.splice(i, 1)[0]);
        else cuSetSec(st, CU_SECS[CU_SECS.indexOf(sec) + d]);
      }
    }
    cuChanged(true);
    const again = act === 'remove' || act === 'break' ? null : list.querySelector(`.cu-step[data-id="${st.id}"] [data-act="${act}"]`);
    if (again && !again.disabled) again.focus({ preventScroll: true });
  });
  $('cuAddBtn').addEventListener('click', () => {
    cuSay('');
    if (C.steps.length >= CU_MAX_STEPS) { cuSay(`An approach can hold ${CU_MAX_STEPS} steps.`); return; }
    cuSnap();
    // one of the saved steps comes with its settings and its name
    const asked = $('cuAddSec').value, mine = cuKeptAt($('cuAddSel').value), st = mine ? cuStepOf(mine.kind, { ...mine.p }, C.next++, asked) : cuStepOf($('cuAddSel').value, {}, C.next++, asked);
    const named = st.kind === 'slider' ? 'name' : st.p.out !== undefined ? 'out' : '';
    if (mine) st.name = mine.name;
    if (named) st.p[named] = cuFresh(cuTaken(C.steps))(st.p[named]);   // a name the rule does not have yet
    // the step goes to the end of its section; a kind that belongs to one section goes there whatever was asked
    const sec = cuSecOf(st), rank = CU_SECS.indexOf(sec);
    cuSetSec(st, sec);
    C.steps.splice(C.steps.filter(x => CU_SECS.indexOf(cuSecOf(x)) <= rank).length, 0, st);
    cuChanged(true);
    if (sec !== asked) cuSay('A value the orbit keeps goes from one iteration to the next, so it stands under “Every iteration”.');
    const li = list.querySelector(`.cu-step[data-id="${st.id}"]`), f = li && li.querySelector('.cu-in, .cu-src');
    if (li) li.scrollIntoView({ block: 'nearest' });
    if (f) f.focus({ preventScroll: true });
  });
  cuSavedLoad(); cuStartMenu();
  cuKeptLoad(); cuAddSet('');
  // the button beside "Add step" opens the list of steps, and a choice there is what Add step adds
  $('cuAddSel').addEventListener('click', () => {
    const btn = $('cuAddSel');
    if (CUP.anchor === btn) cuPickClose(true); else cuPickOpen(btn, btn.value, v => cuAddSet(v));
  });
  $('cuStart').addEventListener('change', () => {
    const v = $('cuStart').value;
    $('cuDelBtn').hidden = v[0] !== 's';
    if (v[0] === 's') $('cuSaveName').value = CUI.saved[+v.slice(1)].name;   // saving under this name again replaces it
  });
  $('cuStartBtn').addEventListener('click', () => {
    const v = $('cuStart').value;
    if (v[0] === 's') {
      const mine = CUI.saved[+v.slice(1)], rule = mine && cuRuleOf(mine.rule);
      if (!rule) return;
      cuSnap(); cuUse(rule);
      cuSay(`“${mine.name}” is loaded. Undo brings the steps you had back.`);
      return;
    }
    // One of the lab's approaches comes with the distance estimate its own picture is drawn with: the plain one
    // where the approach asks for that. Its bailout radius starts at 2, as for any approach, so that the dots of a
    // play go where they leave the ball they start in; the lab's own picture throws a point out beyond 64.
    const k = +v, steps = cuStartSteps(k), lab = CU_STARTS[k].lab ? APPROACHES.find(x => x.id === CU_STARTS[k].lab) : null;
    C.reach = CU_STARTS[k].reach || 2; $('cuReach').value = cuShort(C.reach);   // how far out the dots start comes with the rule
    cuSnap(); cuUse({ steps, next: steps.length + 1, bail: CU_STARTS[k].bail || CU_BAIL, rough: !!lab && lab.deMax === 0 });
    cuSay('Loaded. Undo brings your own steps back.' + (lab ? ' The bailout radius stands at 2. The lab’s own picture of this approach uses 64: set it there for exactly that picture.' : '') + (CU_STARTS[k].say ? ' ' + CU_STARTS[k].say : ''));
  });
  $('cuSaveBtn').addEventListener('click', () => {
    const name = $('cuSaveName').value.trim().slice(0, 40);
    if (!name) { cuSay('Type a name for the approach in the box beside Save first.'); $('cuSaveName').focus(); return; }
    const at = CUI.saved.findIndex(s => s.name.toLowerCase() === name.toLowerCase()), entry = { name, rule: JSON.parse(cuRuleText()) }, was = CUI.saved.slice();
    if (at >= 0) CUI.saved[at] = entry; else CUI.saved.push(entry);
    if (!cuSavedStore()) { CUI.saved = was; cuSay('This browser would not keep the approach: its storage is blocked or full. The text under “Your approach as text”, in the column on the right, can be copied and kept instead.'); return; }
    cuStartMenu('s' + (at >= 0 ? at : CUI.saved.length - 1));
    cuSay((at >= 0 ? `“${name}” now holds the steps as they are.` : `Saved as “${name}”.`) + ' It is in the list beside Load, under “Your saved approaches”, and is kept in this browser.');
  });
  $('cuSaveName').addEventListener('keydown', e => { if (e.key === 'Enter') $('cuSaveBtn').click(); });
  $('cuDelBtn').addEventListener('click', () => {
    const v = $('cuStart').value, k = +v.slice(1), mine = v[0] === 's' ? CUI.saved[k] : null;
    if (!mine) return;
    CUI.saved.splice(k, 1);
    cuSavedStore(); cuStartMenu();
    cuSay(`“${mine.name}” is off the list. The steps on the page are as they were.`);
  });
  $('cuUndo').addEventListener('click', () => {
    const t = CUI.undo.pop();
    if (t === undefined) return;
    cuSay('');
    cuUse(cuRuleOf(JSON.parse(t)) || { steps: [], next: 1, bail: C.bail });
  });
  $('cuN').addEventListener('change', () => { const v = +$('cuN').value; if (isFinite(v)) { S.n = v; syncControls(); refresh(); } });
  $('cuTextBox').addEventListener('toggle', () => { if ($('cuTextBox').open) $('cuText').value = cuRuleText(); });
  $('cuTextUse').addEventListener('click', () => {
    let rule = null;
    try { rule = cuRuleOf(JSON.parse($('cuText').value)); } catch (err) { /* not a rule */ }
    if (!rule) { cuSay('That text is not an approach: nothing was changed. An approach is the text this box shows for your own steps.'); return; }
    cuSnap(); cuUse(rule); cuSay('The approach from the text is in use. Undo brings the earlier one back.');
  });
  // the bar
  const move = d => { const p = cuPlayAt(); cuPlayStop(); if (d < 0 && p.pass === cuFirst()) cuGo(p.pass, -1e9); else cuGo(p.pass + d, 1e9); };
  $('cuItPrev').addEventListener('click', () => move(-1));
  $('cuItNext').addEventListener('click', () => move(1));
  $('cuIt').addEventListener('change', () => { cuPlayStop(); cuGo((+$('cuIt').value || 1) - cuLead(), 1e9); CUI.barSig = ''; cuBarSync(); });
  $('cuItAll').addEventListener('change', () => { const v = Math.round(+$('cuItAll').value); if (v >= 1 + cuLead()) { S.iter = Math.min(v, 400); syncControls(); touch(); } CUI.barSig = ''; cuBarSync(); });
  $('cuStepPrev').addEventListener('click', () => {
    const p = cuPlayAt(), m = cuMoving().length;
    cuPlayStop();
    let u = Math.ceil(p.u - 1e-9) - 1, pass = p.pass;
    if (u < cuLow(pass)) { if (pass > cuFirst()) { pass--; u = m - 1; } else u = cuLow(pass); }
    cuGo(pass, u);
  });
  $('cuStepNext').addEventListener('click', () => {
    const p = cuPlayAt();
    cuPlayStop();
    let u = Math.floor(p.u + 1e-9) + 1, pass = p.pass;
    if (u > cuHigh(pass)) { if (pass < cuPasses()) { pass++; u = 1; } else u = cuHigh(pass); }
    cuGo(pass, u);
  });
  $('cuPlay').addEventListener('click', () => {
    if (CUI.playing) { cuPlayStop(); CUI.barSig = ''; cuBarSync(); return; }
    const p = cuPlayAt(), m = cuMoving().length;
    if (!m) return;
    // from the end of an iteration the play goes on with the next one; from the finished solid it starts over
    if (p.u >= cuHigh(p.pass) - 1e-9) S.custom.play = p.end ? { pass: cuFirst(), u: cuLow(cuFirst()) } : { pass: p.pass + 1, u: 0 };
    else if (!S.custom.play) S.custom.play = { pass: p.pass, u: p.u };
    CUI.playing = true; CUI.last = performance.now(); $('cuPlay').textContent = 'Pause';
    if (!CUI.raf) CUI.raf = requestAnimationFrame(cuPlayFrame);
  });
  $('cuEnd').addEventListener('click', () => { cuPlayStop(); cuGo(1e9, 1e9); });
  $('cuFirst').addEventListener('click', () => { cuPlayStop(); cuGo(cuFirst(), -1e9); });
  $('cuAt').addEventListener('input', () => { cuPlayStop(); cuGo(cuPlayAt().pass, +$('cuAt').value); });
  $('cuTicks').addEventListener('click', e => { const b = e.target.closest('button'); if (b) { cuPlayStop(); cuGo(cuPlayAt().pass, +b.dataset.u); } });
  const bail = v => { if (isFinite(+v) && +v > 0) { S.custom.bail = cuBailOf(v); cuStore(); cuBarSync(); touch(); } };
  $('cuRoughOn').addEventListener('change', () => { S.custom.rough = $('cuRoughOn').checked; cuStore(); touch(); });
  $('cuBail').addEventListener('input', () => bail($('cuBail').value));
  $('cuBailR').addEventListener('input', () => bail($('cuBailR').value));
  // the button under the Approach menu: to the custom approach, and back to the approach before it
  const mine = APPROACHES.findIndex(a => a.id === 'custom');
  $('apCustomBtn').addEventListener('click', () => {
    if (S.approach === mine) S.approach = CUI.before === mine ? 0 : CUI.before;
    else { CUI.before = S.approach; S.approach = mine; }
    uiApMenu(false);
    refresh();
  });
  cuRender(); cuErrors();
  hooks.refresh.push(customSync); hooks.view.push(cuBarSync);
  cuOverInit();
  customSync();
}

// What is drawn over the picture: the dots and the guides while a play is under way, and the names of the two
// halves while both pictures are on show. All of it is worked out here, in JavaScript, and drawn on a canvas of its
// own with the picture's camera.
//
// The dots. The solid is drawn where its points started, so a step that only rotates points changes nothing in it.
// The dots are some of those points, each drawn where the steps have carried it by now, with a short tail that says
// where it just came from. The bar has the Learn tab's choices for them: dots, the surface or both; how many there
// are; where they start (a full grid, level sheets, shells, or sheets and shells together) and how far out; what a
// dot's colour says about that place; whose orbits are drawn; and whether new dots come in for the ones that are
// thrown out. A handful are drawn larger, and the orbits are the whole paths of those, or of every dot.
//
// The guides. What the step on show works with: the axis of a rotation, the plane of a mirror, the sphere of an
// inversion, the arrow of a slide. One dot gets a ring and stands for the others: its way through the step is drawn
// from start to end, and whatever the step works out afresh for every point (an axis that follows the point, say)
// is drawn as it is for that dot. A step that moves no point has a value in place of a move, and its guide is that
// value for the ringed dot.
//
// A step that works on another point than z (on c, or on a point the rule has named) moves no dot. Its guides are
// drawn for that point of the ringed dot, which gets a ring of its own and its way through the step.
//
// c. The steps taken once before the iterations are played before the first iteration. In a Mandelbrot picture every
// point has its own c and starts z at the middle, and the first iteration only puts it on that c: a dot is drawn on
// its c from the start, so a step that changes c there moves the dots, and that first iteration moves none. A Julia
// picture has one c before its iterations, which such a step moves as a ring of its own.
const CU_DOTS_TRIES = [60000, 400000], CU_DOTS_MISS = 6000, CU_DOTS_SLICE = 22, CU_DOTS_TAIL = 0.18, CU_DOTS_PLAIN = 2500, CU_PATHS = 6, CU_WAY = 10;
const CUD = { cv: null, found: {}, mark: {}, big: {}, info: {}, drawn: '', tmr: 0 };
// the modifiers of the page, which every step of an orbit begins with
const cuMod = z => [S.abs[0] ? Math.abs(z[0]) : z[0], (S.abs[1] ? Math.abs(z[1]) : z[1]) * (S.flip[0] ? -1 : 1), (S.abs[2] ? Math.abs(z[2]) : z[2]) * (S.flip[1] ? -1 : 1)];
// Where the starting point p is when the pass `pass` begins, with what its orbit carries: { z, st, c, was, sec }, or
// null when it was thrown out before that. was: where it was when each pass before began. mode: 'j' a Julia
// picture, 'm' a Mandelbrot one, where the pass 0 finds every point at the middle (lead). A pass below the first
// is the very start, before the steps taken once (sec 'pre'); the pass after the last of the iterations is where
// the steps taken once after them begin (sec 'post').
function cuDotAt(p, pass, bail, mode) {
  const car = CARRY.custom, jul = mode === 'j', c = jul ? S.c.slice(0, 3) : p, n = S.n, was = [], from = jul ? p : [0, 0, 0], post = cuPasses() + 1;
  if (pass < (jul ? 1 : cuFirst())) return { z: from, st: car.start(), c, was, sec: 'pre' };
  let z = cuPreZ(from, c), st = car.start(), done = 0;
  if (!(len(z) <= bail)) return null;
  if (pass < 1) return { z, st, c, was, sec: 'main', lead: true };
  const want = Math.min(pass, post) - 1;   // the passes that count and lie before this one
  for (let turn = 0; turn < want + 2; turn++) {
    const mid = carOrigin(z);              // a turn that starts at the middle does not count: it carries the point to its own c
    if (!mid && done === want) break;
    if (!(len(z) <= bail)) return null;
    if (!mid) { was.push(z); done++; }
    const v = cuMod(z);
    st = car.step(st, v, c); z = cuRun(v, st.cm, n, st);
  }
  return len(z) <= bail ? { z, st, c, was, sec: pass >= post ? 'post' : 'main' } : null;
}
// What a dot begins the pass on show with: the point after the page's modifiers, and its orbit's state (before the
// iterations: the point as it is, and c as the orbit gets it). It is kept with the dot, as are the names it has
// when the step on show is about to begin (e, for the step at eo), so that a frame of a play works out that one
// step alone. cuPart: where the dot is at t of the way through the step at `ord` (what: 'on' where the point is
// that the step changes, 'c' what the dot's c is then). cuDotC: the c its pass begins with, which before the
// iterations is the c of the picture. cuWhole: where the whole pass leaves it. cuDotEnv: its names as the step at `ord` begins. cuEndOf: where the q-th of the steps a play can stand
// in leaves it; cuWayOf: points on its way through that step. A dot is made afresh whenever the rule, the picture
// or the pass changes.
function cuBegin(d) {
  if (!d.b) {
    if (d.sec === 'pre') d.b = { v: d.z, s: { cm: cuCmap(d.c) } };
    else { const v = cuMod(d.z); d.b = { v, s: CARRY.custom.step(d.st, v, d.c) }; }
  }
  return d.b;
}
const cuDotC = d => (d.sec === 'pre' ? d.c : cuBegin(d).s.cm);
const cuDotEnv = (d, ord) => { const b = cuBegin(d); return cuEnvAt(b.v, cuDotC(d), S.n, d.sec === 'pre' ? null : b.s, ord, d.sec); };
const cuWhole = d => { const b = cuBegin(d); return cuRun(b.v, cuDotC(d), S.n, d.sec === 'pre' ? null : b.s, undefined, d.sec); };
function cuPart(d, ord, t, what) {
  if (d.eo !== ord) {
    d.e = d.eo !== undefined && d.eo < ord ? cuEnvOn(d.e, d.eo, ord) : cuDotEnv(d, ord);
    d.eo = ord;
  }
  return cuStepOn(d.e, ord, t, what);
}
function cuEndOf(d, mov, q) { const e = d.ends || (d.ends = {}), o = mov[q].ord; return e[o] || (e[o] = cuPart(d, o, 1)); }
function cuWayOf(d, mov, q) {
  const w = d.ways || (d.ways = {}), o = mov[q].ord;
  if (!w[o]) { w[o] = []; for (let a = 1; a <= CU_WAY; a++) w[o].push(cuPart(d, o, a / CU_WAY)); }
  return w[o];
}
// The dot's names when the step at `ord` has been taken, whether that step is switched on or not.
function cuDotEnvAfter(d, ord) {
  const E0 = cuDotEnv(d, ord), s = cuProgram().at[ord], E = { ...E0, v: E0.v.slice(), tt: 1 };
  if (s) for (const f of s.fns) f(E);
  return E;
}
// The dot one pass on, or null when that pass throws it out. post: the pass it comes to is the one after the last
// iteration.
function cuDotNext(d, bail, post) {
  const z = cuWhole(d);   // the whole pass, which also leaves in the orbit's state what the orbit keeps
  if (!(len(z) <= bail)) return null;
  if (d.sec === 'pre') return { z, st: CARRY.custom.start(), c: d.c, was: [], p: d.p, col: d.col, sec: 'main', lead: cuFirst() < 1 && carOrigin(z) };
  return { z, st: { ...cuBegin(d).s }, c: d.c, was: d.lead ? [] : d.was.concat([d.z]), p: d.p, col: d.col, sec: post ? 'post' : 'main' };
}
// Where the dots start: the Learn tab's own layouts (learnShapeLayout: a full grid, level sheets, shells, or sheets
// and shells together) with its spacings for "How many". They are made for a ball of radius 2 and are stretched to
// the ball the dots start in (cuReach). The places come in an order that is mixed, the same way every time, so that
// the first few of them are spread over the whole ball.
function cuDotPlaces(lay, gap) {
  const L = learnShapeLayout(true, gap, lay), out = L.pts.slice();
  let seed = 12345;
  for (let i = out.length - 1; i > 0; i--) {
    seed = (Math.imul(seed, 1103515245) + 12345) & 0x7fffffff;
    const j = Math.floor(seed / 0x80000000 * (i + 1)), t = out[i];
    out[i] = out[j]; out[j] = t;
  }
  out.gap = L.gap;
  return out;
}
// The dots for the pass on show (a pass of the iterations, the one below the first for the very start, or the one
// above the last for the steps taken once after): of the places of the layout, those whose points are still in. With "Add new dots"
// ticked, places between them are tried (the Learn tab's, learnShapeCandidate) until there are as many dots as there
// were places at the start; without it the dots get fewer from iteration to iteration. The same places are tried in
// the same order every time, so a dot that is still in keeps its place and its colour.
// The search is done a slice of a frame at a time, and the list grows until it is `done`. Where the dots of the
// iteration before are at hand they are each taken on by one iteration, which gives the same list for less work.
// The places tried for new dots are limited (thirty for each dot of the start, within CU_DOTS_TRIES), and a long
// run of them that all fail ends the search: a thin solid can leave fewer dots than there were at the start.
// The list carries `start`, how many places the layout has; `sig`, what it was made for, and `base`, the same
// without the pass; `gap`, how far apart the places lie. A dot carries p, the place it started from.
function cuDotsFind(pass, mode) {
  const C = S.custom, bail = cuBailOf(C.bail), reach = cuReach(), refill = C.refill !== false;
  const lay = ['grid', 'sheets', 'shells'].includes(C.lay) ? C.lay : 'both', gaps = LEARN_SHAPE_SPACING[3], gap = gaps[C.count] || gaps.some;
  const base = [C.rev, mode === 'j' ? S.c.join(',') : '', S.n, bail, reach, S.abs, S.flip, S.z0, gap, lay, C.tint, refill, theme.dark, cuPasses(), cuFirst()].join('|');
  let T = CUD.found[mode];
  if (!T || T.base !== base) T = CUD.found[mode] = { base, by: new Map(), places: null, lay, k: reach / 2, bail, mode, tint: C.tint, refill };
  let dots = T.by.get(pass);
  if (!dots) {
    dots = Object.assign([], { sig: base + '|' + pass, base, pass, sec: pass < (mode === 'j' ? 1 : cuFirst()) ? 'pre' : pass > cuPasses() ? 'post' : 'main', start: 0, gap: 0, done: false, src: null, pos: 0, next: 0, miss: 0 });
    const before = T.by.get(pass - 1);
    T.by.set(pass, dots);
    if (T.by.size > 4) T.by.delete(T.by.keys().next().value);
    if (mode === 'm' && S.z0.trim() !== '0') { dots.done = true; return dots; }   // a start value of its own: the page has no JavaScript for it
    if (!T.places) { T.places = cuDotPlaces(lay, gap); T.tries = clamp(30 * T.places.length, CU_DOTS_TRIES[0], CU_DOTS_TRIES[1]); }
    dots.start = T.places.length; dots.gap = T.places.gap * T.k;
    if (before && before.done) { dots.src = before; dots.next = before.next; dots.miss = before.miss; }
  }
  if (!dots.done) cuDotsMore(dots, T);
  return dots;
}
function cuDotsMore(dots, T) {
  const t0 = performance.now(), dark = theme.dark;
  let n = 0;
  const late = () => ++n % 48 === 0 && performance.now() - t0 > CU_DOTS_SLICE;
  const again = () => { if (!CUD.tmr) CUD.tmr = setTimeout(() => { CUD.tmr = 0; CUD.drawn = ''; cuOverDraw(); }, 4); };
  const make = q => {
    const p = scl(q, T.k), d = cuDotAt(p, dots.pass, T.bail, T.mode);
    if (d) { d.p = p; d.col = learnShapeDotColour(q, true, dark, T.tint); dots.push(d); }   // the Learn tab's colours, for its own ball
    return !!d;
  };
  if (dots.src) {
    while (dots.pos < dots.src.length) { const d = cuDotNext(dots.src[dots.pos++], T.bail, dots.sec === 'post'); if (d) dots.push(d); if (late()) return again(); }
  } else {
    while (dots.pos < T.places.length) { make(T.places[dots.pos++]); if (late()) return again(); }
  }
  // new dots for the ones thrown out; a long run of places that all fail means next to nothing is left to start from
  if (T.refill) while (dots.length < dots.start && dots.next < T.tries && dots.miss < CU_DOTS_MISS) {
    const q = learnShapeCandidate(true, T.lay, dots.next++);
    if (q) dots.miss = make(q) ? 0 : dots.miss + 1;
    if (late()) return again();
  }
  dots.done = true; dots.src = null;
}
// what the dots, the handful and the guides were made for: the list as far as it has been found
const cuDotsSig = dots => dots.sig + '|' + (dots.done ? 'all' : dots.length);
// The step on show, for the dots and the guides: { sec, pass, ord, t, id, on }, or null at the finished solid. sec:
// the section the play stands in. Between two steps it is the one just taken, at its end. on: the point that step
// changes ('z', 'c' or a name of the rule's own). look: the step whose name was clicked and that changes no point
// (CUI.look); the play then stands where that step is, and lookOrd is its place among the steps.
function cuShown() {
  if (!cuPlayNow()) return null;
  const at = cuPlayAt(), st = CUI.look === null ? null : S.custom.steps[cuStepAt(CUI.look)], me = st ? cuProgram().run.find(r => r.id === st.id) : null;
  let w = cuPlaySec(at);
  // the end of the last iteration is also where the steps taken once after begin: a step of theirs that is looked
  // at has the play stand there as the start of its own section
  if (me && me.sec === 'post' && w.sec === 'main' && at.pass === cuPasses() && at.u === cuMoving().length && cuPlayable('post').length) w = { sec: 'post', pass: at.pass, list: cuPlayable('post'), x: 0 };
  const k = Math.round(w.x), whole = Math.abs(w.x - k) < 1e-6 && k >= 1;
  const s = whole ? w.list[k - 1] : w.list[Math.min(Math.floor(w.x), w.list.length - 1)];
  const out = { sec: w.sec, pass: at.pass, ord: s.ord, t: whole ? 1 : w.x - Math.floor(w.x), id: s.id, on: s.on };
  if (st && me && me.sec === w.sec) { out.look = st.id; out.lookOrd = me.ord; }
  return out;
}
// The value of a setting where its text alone says it is the same for every point (a typed point, a number, c in a
// Julia picture whose iterations leave c alone, a formula of those), or null where it follows the point or a name
// the rule made.
function cuFixed(text, kind, mode) {
  try {
    const node = cuParse(String(text), { vars: new Map(), zero: [], uses: new Set(), K: [], internal: false });
    let fixed = node.t === kind;
    (function walk(tr) {
      if (tr.leaf === undefined) (tr.a || [tr.of]).forEach(walk);
      else if (/^[A-Za-z]/.test(tr.leaf) && tr.leaf !== 'pi' && tr.leaf !== 'n' && !(tr.leaf === 'c' && mode === 'j' && !cuProgram().cRun)) fixed = false;
      if (tr.fn === 'point') fixed = false;
    })(node.tree);
    return fixed ? node.js({ z: [0, 0, 0], c: cuCmap(S.c.slice(0, 3)), n: S.n, K: [], v: [], tt: 1, first: [0, 0, 0], last: [0, 0, 0], mean: [0, 0, 0], count: 0 }) : null;
  } catch (err) { return null; }   // a name of the rule's own, or a formula that cannot be read
}
// The value a formula has for a point with the names E, of whatever kind it is: { t, value }, or null.
function cuValueAny(text, E) {
  try {
    const P = cuProgram(), node = cuParse(String(text), { vars: P.varsOf[E.sec] || P.vars, zero: [], uses: new Set(), K: [], internal: false });
    return { t: node.t, value: node.js(E) };
  } catch (err) { return null; }
}
// The value of a setting when it comes out the same for each of these dots, which is taken to mean that it is the
// same for every point (a slider, a number the steps before worked out from n); null where it differs.
function cuSame(text, kind, envs) {
  const vals = envs.map(E => cuValueFor(text, kind, E));
  if (vals.some(v => v === null)) return null;
  const flat = v => (Array.isArray(v) ? v : [v]), a = flat(vals[0]), size = Math.max(1, ...a.map(Math.abs));
  return vals.every(v => flat(v).every((x, i) => Math.abs(x - a[i]) <= 1e-9 * size)) ? vals[0] : null;
}
// The dots that can stand for the others in a pass, the best first: those that stay at a middling distance from
// the middle through all the steps of the pass, and that start off every axis and every flat plane. What is drawn
// for such a dot sits well inside the picture, and nothing about it is a special case.
function cuMarkOf(mode, dots) {
  const sig = cuDotsSig(dots), kept = CUD.mark[mode];
  if (kept && kept.sig === sig) return kept.order;
  const mov = cuPlayable(dots.sec), few = dots.slice(0, mov.length > 12 ? 40 : 80);
  const rows = few.map(d => {
    const end = cuWhole(d), at = mov.map(m => len(cuPart(d, m.ord, 0))).concat(len(end));
    // a dot that is at the middle still is judged by where its pass leaves it
    const q = len(d.z) > 1e-9 ? d.z : end, l = len(q) || 1, skew = Math.min(Math.abs(q[0]), Math.abs(q[1]), Math.abs(q[2])) / l;
    return { d, most: Math.max(...at), least: Math.min(...at), skew };
  });
  // nearly as far out as the dots usually get, and no further than a solid reaches: near enough to stay in view,
  // far enough for its circles to show
  const sizes = rows.map(r => r.most).sort((a, b) => a - b), aim = Math.min(0.8 * sizes[sizes.length >> 1], 1.5);
  const rank = r => (r.skew > 0.25 ? (r.least > 0.4 * aim ? 0 : 1) : 2);
  const order = rows.sort((a, b) => rank(a) - rank(b) || Math.abs(a.most - aim) - Math.abs(b.most - aim)).map(r => r.d);
  CUD.mark[mode] = { sig, order };
  return order;
}
// The handful of dots that are drawn larger, to be followed with the eye: the best of cuMarkOf; the dots that were
// followed in the pass shown before, while they are still in; and more that lie far from those and from one
// another when the pass begins. Of these, dots that are still in when the pass ends come first, so that the
// handful stays on show through all its steps.
function cuHandful(mode, dots) {
  const sig = cuDotsSig(dots), kept = CUD.big[mode];
  if (kept && kept.sig === sig) return kept.big;
  const bail = cuBailOf(S.custom.bail), pool = dots.slice(0, 300), big = cuMarkOf(mode, dots).slice(0, 1), key = d => d.p.join(',');
  const place = d => (len(d.z) > 1e-9 ? d.z : d.p);   // dots that are at the middle still are told apart by where they start
  if (big.length && kept && kept.base === dots.base) {
    const by = new Map(dots.map(d => [key(d), d]));
    for (const k of kept.keys) { const d = by.get(k); if (d && !big.includes(d) && big.length < CU_PATHS) big.push(d); }
  }
  const stays = pool.filter(d => len(cuWhole(d)) <= bail);
  for (const from of [stays, pool]) while (big.length && big.length < CU_PATHS) {
    let best = null, far = -1;
    for (const d of from) {
      if (big.includes(d)) continue;
      let near = Infinity;
      for (const q of big) near = Math.min(near, len(sub(place(d), place(q))));
      if (near > far) { far = near; best = d; }
    }
    if (!best) break;
    big.push(best);
  }
  CUD.big[mode] = { sig, base: dots.base, keys: big.map(key), big };
  return big;
}
// What is worked out once for the step on show and kept while the play stays in it. M: the ringed dot, which is
// the best of cuMarkOf that this step moves (still: it moves none of them), with its names as the step begins
// (env), the point the step changes (on), where that point is then and where the step leaves it (zs, ze), and for a
// step that is looked at, its names after that step (after). The point is the dot itself for a step that works on
// z; for a step that works on c or on a point of the rule's own it is that point of the ringed dot. tests: the
// names of the ringed dot and two of the handful (see cuSame). path: the way the point takes through the step.
function cuStepInfo(shown, mode, dots) {
  const sig = [cuDotsSig(dots), shown.ord, shown.look].join('|'), kept = CUD.info[mode];
  if (kept && kept.sig === sig) return kept;
  const info = { sig, M: null, tests: null, path: [] };
  CUD.info[mode] = info;
  if (!dots.length) return info;
  const looked = shown.look !== undefined, ord = shown.ord, on = looked ? 'z' : shown.on || 'z';
  const at = (d, t) => cuPart(d, ord, t, looked ? undefined : 'on');
  const far = d => { const a = at(d, 0); return len(sub(at(d, 1), a)) / Math.max(1, len(a)); };
  let mover = null;
  if (!looked && on !== 'z') {
    // another point than z: a dot whose point the step moves a good way, at a middling distance from the middle
    const aim = 0.6 * cuReach(), few = dots.slice(0, 300).map(d => ({ d, far: far(d), l: len(at(d, 0)) })).filter(o => o.far > 1e-6);
    few.sort((x, y) => Math.abs(x.l - aim) - Math.abs(y.l - aim));
    mover = (few.find(o => o.far > 0.2) || few[0] || {}).d || null;
  } else if (!looked) mover = cuMarkOf(mode, dots).find(d => far(d) > 1e-6) || dots.find(d => far(d) > 1e-6) || null;
  const mark = mover || cuMarkOf(mode, dots)[0], lead = [mark, ...cuHandful(mode, dots).filter(d => d !== mark)];
  const envs = lead.slice(0, 3).map(d => cuDotEnv(d, ord));
  info.M = { dot: mark, on, still: !looked && !mover, env: envs[0], zs: at(mark, 0), ze: at(mark, 1), after: looked && shown.lookOrd >= 0 ? cuDotEnvAfter(mark, shown.lookOrd) : null };
  if (envs.length > 1) info.tests = envs;
  for (let j = 0; j <= 96; j++) info.path.push(at(mark, j / 96));
  return info;
}
// The guides of one step that moves a point, as shapes in space: { line: [a, b] }, { arrow: [a, b] },
// { ring: [centre, normal, radius] } and { disc: [centre, normal, radius] } (a ring that is filled: a plane), each
// with an optional label; a ring or disc may be `solid`, a line `faint`. R: the size to draw them at. M and tests:
// see cuStepInfo; without a dot (M null) only what is the same for every point can be drawn. who: what the point is
// called where it is not the ringed dot itself (c, or a point of that dot); it then stands in the words in the
// dot's place, and whoever calls says whether the step moves it. Returns { shapes, notes }.
function cuGuides(st, R, mode, M, tests, who) {
  const p = st.p, shapes = [], notes = [], O = [0, 0, 0], AX = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  // a point that a step has flung far off is drawn no further than this from the middle
  const top = 3 * cuBailOf(S.custom.bail), cap = v => (len(v) > top ? scl(v, top / len(v)) : v);
  if (M) M = { ...M, zs: cap(M.zs), ze: cap(M.ze) };
  let own = false;
  const value = (key, kind) => {
    const x = tests ? cuSame(p[key], kind, tests) : cuFixed(p[key], kind, mode);
    if (x !== null || !M) return x;
    const y = cuValueFor(p[key], kind, M.env);
    if (y !== null) own = true;
    return y;
  };
  const vec = key => value(key, 'v'), num = key => value(key, 's');
  const sphere = (c, r, label, solid) => { AX.forEach((k, i) => shapes.push({ ring: [c, k, r], solid, label: i ? '' : label })); };
  const axis = (a, label) => { const u = norm(a); shapes.push({ line: [scl(u, -1.25 * R), scl(u, 1.25 * R)], label }); return u; };
  const missing = what => notes.push(M ? `The ${what} of this step cannot be worked out here, so it is not drawn.` : `The ${what} of this step follows the point, and no dot is left to show it for.`);
  // a rotation about the axis u: the circle the ringed dot goes round, and the spokes to where it starts and ends.
  // Returns the middle of that circle, or null when the dot lies on the axis and has no circle.
  const round = u => {
    if (!M) { shapes.push({ ring: [O, u, 0.9 * R], label: 'the rotation goes round' }); return O; }
    const C = scl(u, dot(M.zs, u));
    if (len(sub(M.zs, C)) < 1e-9 * Math.max(1, len(M.zs))) { notes.push('The ringed dot lies on the axis here, so the rotation leaves it where it is.'); return null; }
    shapes.push({ ring: [C, u, len(sub(M.zs, C))], label: 'the ringed dot goes round this circle' }, { line: [C, M.zs], faint: true }, { line: [C, M.ze], faint: true });
    return C;
  };
  const B = CU_BLOCKS[st.kind];
  if (st.kind === 'lon' || st.kind === 'rot') {
    const a = vec('axis');
    if (!a) missing('axis');
    else if (!(len(a) > 1e-9)) notes.push('The axis has no length here, so there is nothing to rotate about.');
    else {
      const u = axis(a, 'axis'), f = st.kind === 'lon' ? vec('from') : null, flat = f ? sub(f, scl(u, dot(f, u))) : null;
      if (flat && !(len(flat) > 1e-9)) notes.push('“Angle counted from” points along the axis here, so there is no direction to count the angle from, and the step puts every point on the axis.');
      else {
        const C = round(u);
        if (st.kind === 'lon' && !f) missing('direction the angle is counted from');
        else if (flat && C) shapes.push({ arrow: [C, add(C, scl(norm(flat), M ? Math.max(len(sub(M.zs, C)), 0.25 * R) : 0.9 * R))], label: 'angle 0: the angle is counted from here' });
      }
    }
  } else if (st.kind === 'lat' || st.kind === 'merc') {
    const a = vec('axis'), down = st.kind === 'lat' && p.from === 'axis';
    if (!a) missing('axis');
    else if (!(len(a) > 1e-9)) notes.push('The axis has no length here, so there is no height to count.');
    else {
      const u = axis(a, down ? 'axis: the angle is counted down from it' : 'axis: the height is counted along it'), r = M ? len(M.zs) : 0.9 * R;
      shapes.push({ ring: [O, u, r], label: st.kind === 'merc' ? 'height 0' : down ? '90° down from the axis' : 'the angle is counted up from this circle' });
      const w = M ? sub(M.zs, scl(u, dot(M.zs, u))) : null;
      if (w && !(len(w) > 1e-9 * Math.max(r, 1e-30))) notes.push('The ringed dot lies on the axis here.');
      if (w && len(w) > 1e-9 * Math.max(r, 1e-30)) shapes.push({ ring: [O, norm(cross(u, w)), r], solid: true, label: 'the ringed dot moves along this circle' }, { line: [O, M.zs], faint: true }, { line: [O, M.ze], faint: true });
    }
  } else if (st.kind === 'len') {
    sphere(O, 1, 'length 1: points here stay');
    if (M && len(M.zs) > 1e-9) shapes.push({ line: [O, scl(norm(M.zs), Math.max(len(M.zs), len(M.ze), 1))], faint: true, label: 'the ringed dot moves along this line' });
  } else if (st.kind === 'scale') {
    const k = num('by');
    sphere(O, 1, 'length 1');
    if (k === null) missing('number');
    else {
      if (Math.abs(k) > 1e-9) sphere(O, Math.abs(k), 'where length 1 lands', true);
      if (k < 0) notes.push('A number below 0 also carries every point through the middle to the other side.');
    }
  } else if (st.kind === 'inv') {
    const c = vec('centre'), r = num('radius');
    if (!c || r === null) missing('sphere');
    else if (!(Math.abs(r) > 1e-9)) notes.push('The radius is 0 here, so every point lands on the centre.');
    else {
      sphere(c, Math.abs(r), 'the sphere: what is inside it goes outside, and the other way');
      if (M) { const far = len(sub(M.zs, c)) > len(sub(M.ze, c)) ? M.zs : M.ze; shapes.push({ line: [c, far], faint: true, label: 'the ringed dot moves along this line from the centre' }); }
    }
  } else if (st.kind === 'mirror' || st.kind === 'fold') {
    const nrm = vec('normal'), at = vec('through');
    if (!nrm || !at) missing('plane');
    else if (!(len(nrm) > 1e-9)) notes.push('“The plane is square to” has no length here, so there is no plane.');
    else {
      const u = norm(nrm);
      shapes.push({ disc: [at, u, 1.1 * R], label: 'the plane' }, { arrow: [at, add(at, scl(u, 0.6 * R))], label: st.kind === 'fold' ? 'the side that is kept' : 'square to the plane' });
      notes.push(st.kind === 'fold' ? 'A point on the kept side stays. A point on the other side goes straight across the plane, to the same distance on the kept side.' : 'Every point goes straight across the plane, to the same distance on the other side.');
    }
  } else if (st.kind === 'foldx' || st.kind === 'softx') {
    const x = num(st.kind === 'foldx' ? 'planes' : 'angle');
    if (x === null) missing(st.kind === 'foldx' ? 'number of creases' : 'mirror’s angle');
    else { const G = st.kind === 'foldx' ? cuFoldShapes(x, R) : cuSoftShapes(x, R); shapes.push(...G.shapes); notes.push(G.note); }
  } else if (st.kind === 'addc' || st.kind === 'shift') {
    const w = st.kind === 'addc' ? vec('what') : vec('by'), k = st.kind === 'addc' ? num('times') : 1;
    if (!w || k === null) missing('slide');
    else shapes.push({ arrow: own ? [M.zs, add(M.zs, scl(w, k))] : [O, scl(w, k)], label: own ? 'the ringed dot slides by this' : 'every point slides by this' });
  } else if (st.kind === 'quatpow') {
    axis([1, 0, 0], 'the x-axis: each point rotates away from it');
    const side = M ? [0, M.zs[1], M.zs[2]] : null;
    if (side && len(side) > 1e-9) shapes.push({ disc: [O, norm(cross([1, 0, 0], side)), Math.max(len(M.zs), len(M.ze), 0.25 * R)], label: 'the flat sheet that holds the x-axis and the ringed dot: the dot stays in it' }, { line: [O, M.zs], faint: true }, { line: [O, M.ze], faint: true });
  } else if (st.kind === 'quatturn') {
    const q = ['x', 'y', 'z'].map(num);
    if (q.some(x => x === null)) missing('axis');
    else if (!(len(q) > 1e-9)) notes.push('This quaternion has no i, j or k part, so it rotates nothing.');
    else round(axis(q, 'axis: the i, j and k parts'));
  } else if (st.kind === 'quatmul' || st.kind === 'matrix') {
    // a move that takes straight lines to straight lines: where one step along x, along y and along z land
    let img = null;
    if (st.kind === 'matrix') {
      const m = [0, 1, 2, 3, 4, 5, 6, 7, 8].map(k => num('m' + k));
      if (!m.some(x => x === null)) img = e => [m[0] * e[0] + m[1] * e[1] + m[2] * e[2], m[3] * e[0] + m[4] * e[1] + m[5] * e[2], m[6] * e[0] + m[7] * e[1] + m[8] * e[2]];
    } else {
      const q = ['x', 'y', 'z', 'w'].map(num);
      if (!q.some(x => x === null)) img = e => { const a = [e[1], e[2], 0, e[0]], r = p.side === 'left' ? cuQmul(q, a) : cuQmul(a, q); return [r[3], r[0], r[1]]; };
      notes.push('The point is read as the quaternion x + yi + zj and multiplied. The k part of the answer is dropped.');
    }
    if (!img) missing(st.kind === 'matrix' ? 'matrix' : 'quaternion');
    else AX.forEach((e, i) => shapes.push({ line: [O, e], faint: true }, { arrow: [O, img(e)], label: `where 1 along ${'xyz'[i]} lands` }));
  }
  if (!B.tween && st.kind !== 'inv') notes.push('This step has no in-between of its own, so the play carries each point straight from where the step finds it to where the step puts it, or round the middle when its length stays the same.');
  if (own) notes.push('What this step works with is not the same for every point: it is drawn as it is for the ringed dot.');
  // that no dot moves is the first thing to say about a step
  if (M && M.still && !who) notes.unshift(M.on === 'z' && M.dot.sec === 'pre' && mode === 'm' ? 'In a Mandelbrot picture z starts at the middle, and this step leaves the middle where it is: no dot moves.'
    : mode === 'm' && cuCstep() && M.dot.sec === 'main' && M.dot.was.length === 0 ? `No dot moves here: step ${cuStepAt(cuCstep().id) + 1}, before the iterations, already put each one where this step would.`
    : 'No dot moves here: each already lies where this step would put it.');
  if (who) {
    const Who = who[0].toUpperCase() + who.slice(1), told = t => t.replace(/the ringed dot/g, who).replace(/The ringed dot/g, Who);
    for (const sh of shapes) if (sh.label) sh.label = told(sh.label);
    return { shapes, notes: notes.map(told) };
  }
  return { shapes, notes };
}
// What a fold along the x-axis works with, at the size R: the x-axis, the creases (planes that all hold it, the
// first of them half of 180°/k from the flat plane and the rest 180°/k apart), and the flat plane, about which the
// wedge lies that stays. Returns { shapes, note }.
function cuFoldShapes(k, R) {
  const n = clamp(Math.round(k), 2, 8), half = cuShort(90 / n), shapes = [{ line: [[-1.25 * R, 0, 0], [1.25 * R, 0, 0]], label: 'the x-axis: every crease runs along it' }];
  shapes.push({ disc: [[0, 0, 0], [0, 0, 1], R], solid: true, label: `the flat plane: what lies within ${half}° of it stays` });
  for (let j = 0; j < n; j++) { const a = (j + 0.5) * PI / n; shapes.push({ disc: [[0, 0, 0], [0, -Math.sin(a), Math.cos(a)], R], label: j ? '' : 'a crease: what lies beyond it is folded back' }); }
  return { shapes, note: `What lies within ${half}° of the flat plane stays, and the rest is folded into that wedge across the creases.` };
}
// The same for a mirror at an angle along the x-axis: the x-axis and the two mirrors, deg° from the flat plane.
function cuSoftShapes(deg, R) {
  const a = deg * PI / 180, O = [0, 0, 0];
  return { shapes: [{ line: [[-1.25 * R, 0, 0], [1.25 * R, 0, 0]], label: 'the x-axis: both mirrors run along it' },
    { disc: [O, [0, -Math.sin(a), Math.cos(a)], R], solid: true, label: 'a mirror: what is steeper than it is laid back across it' }, { disc: [O, [0, Math.sin(a), Math.cos(a)], R], solid: true, label: '' }],
  note: `What lies steeper than ${cuShort(deg)}° from the flat plane is mirrored back towards it, and the soft corner rounds the crease off.` };
}
// The guide of a step that moves no point: what it works out, for the ringed dot. A point is an arrow from the
// middle; anything else is said in words.
function cuValueGuide(st, mode, M) {
  const shapes = [], notes = [], O = [0, 0, 0], pt = v => `(${v.map(cuShort).join(', ')})`;
  const name = st.kind === 'slider' || st.kind === 'keep' ? String(st.p.name) : st.kind === 'formula' ? cuHalves(String(st.p.text)).target : String(st.p.out);
  const val = M && M.after && name ? cuValueAny(name, M.after) : null;
  if (!val) { notes.push(M ? 'What this step works out cannot be shown here.' : 'No dot is left to show this step for.'); return { shapes, notes }; }
  const x = val.value, who = st.kind === 'slider' ? 'This number is the same for every point: ' : 'This step moves no point. For the ringed dot, ';
  if (val.t === 's') notes.push(`${who}${name} = ${cuShort(x)}` + (/^f_(asin|acos|atan|atan2|rad|lon|lat)$/.test(st.kind) ? `, an angle of ${cuShort(x * 180 / PI)}°.` : '.'));
  else if (val.t === 'v') { shapes.push({ arrow: [O, x], label: name }); notes.push(`${who}${name} = ${pt(x)}: the arrow from the middle.`); }
  else if (val.t === 'q') {
    notes.push(`${who}${name} = ${cuShort(x[3])} + ${cuShort(x[0])}i + ${cuShort(x[1])}j + ${cuShort(x[2])}k` + (len(x.slice(0, 3)) > 1e-9 ? ': the line is the axis it would rotate a point about.' : '.'));
    if (len(x.slice(0, 3)) > 1e-9) shapes.push({ line: [scl(norm(x.slice(0, 3)), -1), norm(x.slice(0, 3))], label: name });
  } else {
    notes.push(`${who}${name} is the matrix with the rows ${[0, 1, 2].map(r => pt([x[r], x[r + 3], x[r + 6]])).join(', ')}: the arrows are where 1 along x, y and z land.`);
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]].forEach((e, i) => shapes.push({ line: [O, e], faint: true }, { arrow: [O, cuMV(x, e)], label: `where 1 along ${'xyz'[i]} lands` }));
  }
  return { shapes, notes };
}
function cuOverDraw() {
  const cv = CUD.cv;
  if (!cv) return;
  const stage = $('stage'), w = stage.clientWidth, h = stage.clientHeight, dpr = Math.min(devicePixelRatio || 1, 2), C = S.custom;
  const on = cuOn() && !S.learn, both = on && !!C.both, see = ['skin', 'both'].includes(C.see) ? C.see : 'dots', dotsOn = see !== 'skin', guidesOn = C.guides !== false;
  const play = on && !S.flat ? cuShown() : null, at = dotsOn || guidesOn ? play : null, b = basis(), say = $('cuDotsSay');
  // with the dots alone on show, the picture behind them is faint while a play is under way
  document.body.classList.toggle('cu-faint', !!play && see === 'dots');
  const sig = [both, w, h, dpr, theme.brass, theme.ink2, theme.dark, at ? [at.sec, at.pass, at.ord, at.t, at.look, at.on, see, guidesOn, C.count, C.lay, C.tint, C.orbits, C.dotsA, C.refill, C.reach, C.rev, C.bail, S.mode, S.c, S.n, S.abs, S.flip, S.z0, b.pos, b.right, b.up, S.view.fov] : ''].join('|');
  if (sig === CUD.drawn) return;
  CUD.drawn = sig;
  if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
  const g = cv.getContext('2d'), font = getComputedStyle(document.body).fontFamily;
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, w, h);
  // one pane, or the two halves: the Mandelbrot picture on the left and the Julia one on the right
  const panes = both ? [{ mode: 'm', x0: 0, x1: w / 2, name: 'Mandelbrot: each point is its own c' }, { mode: 'j', x0: w / 2, x1: w, name: 'Julia: c from the dials' }] : [{ mode: S.mode, x0: 0, x1: w }];
  if (both) {
    g.strokeStyle = theme.ink2; g.lineWidth = 1; g.globalAlpha = 0.6; g.beginPath(); g.moveTo(w / 2, 0); g.lineTo(w / 2, h); g.stroke(); g.globalAlpha = 1;
    g.font = '600 13px ' + font; g.textBaseline = 'top'; g.fillStyle = theme.ink2;
    for (const P of panes) g.fillText(P.name, P.x0 + (P.mode === 'm' ? 64 : 12), 10);
  }
  if (!at) { say.hidden = true; return; }
  const bail = cuBailOf(C.bail), reach = cuReach(), fov = S.view.fov, eye = len(b.pos), notes = [], ink = theme.dark ? '#fff' : '#000';
  // tgt: the point the step on show works on, where that is not z (c, or a point of the rule's own). early: the play
  // stands among the steps taken once, before.
  const looked = at.look !== undefined, tgt = !looked && at.on && at.on !== 'z' ? at.on : null, early = at.sec === 'pre', st = C.steps[cuStepAt(looked ? at.look : at.id)] || null;
  const orbits = ['all', 'none'].includes(C.orbits) ? C.orbits : 'few', mov = cuPlayable(at.sec), np = cuPasses();
  const add1 = line => { if (line && !notes.includes(line)) notes.push(line); };
  for (const P of panes) {
    const cx = (P.x0 + P.x1) / 2, words = [], far = 6 * Math.max(bail, 2);
    const scr = p => {
      if (!(len(p) <= far)) return null;   // far off, or not a number
      const q = sub(p, b.pos), zc = dot(q, b.f);
      return zc > 0.02 ? [cx + dot(q, b.right) / (zc * fov) * h / 2, h / 2 - dot(q, b.up) / (zc * fov) * h / 2, zc] : null;
    };
    // a line through points in space, added to the path being drawn; it breaks where a point cannot be shown
    const trace = pts => { let pen = false; for (const p of pts) { const q = scr(p); if (!q) { pen = false; continue; } if (pen) g.lineTo(q[0], q[1]); else g.moveTo(q[0], q[1]); pen = true; } };
    const path = pts => { g.beginPath(); let pen = false, last = null, prev = null; for (const p of pts) { const q = scr(p); if (!q) { pen = false; continue; } if (pen) g.lineTo(q[0], q[1]); else g.moveTo(q[0], q[1]); pen = true; prev = last; last = q; } g.stroke(); return [prev, last]; };
    const head = (back, tip) => {   // an arrow head, in the picture's plane
      if (!tip || !back) return;
      const d = [tip[0] - back[0], tip[1] - back[1]], l = Math.hypot(d[0], d[1]);
      if (!(l > 0.5)) return;
      const u = [d[0] / l, d[1] / l];
      g.beginPath(); g.moveTo(tip[0], tip[1]); g.lineTo(tip[0] - 10 * u[0] + 5 * u[1], tip[1] - 10 * u[1] - 5 * u[0]); g.lineTo(tip[0] - 10 * u[0] - 5 * u[1], tip[1] - 10 * u[1] + 5 * u[0]); g.closePath(); g.fill();
    };
    const circ = (q, r) => { g.beginPath(); g.arc(q[0], q[1], r, 0, 2 * PI); };
    // a circle in space: its middle, the direction it is square to, its radius
    const hoop = (c, k, r) => { const e1 = norm(cross(k, Math.abs(k[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0])), e2 = cross(k, e1), pts = []; for (let q = 0; q <= 96; q++) { const a = 2 * PI * q / 96; pts.push(add(c, add(scl(e1, r * Math.cos(a)), scl(e2, r * Math.sin(a))))); } return pts; };
    g.save(); g.beginPath(); g.rect(P.x0, 0, P.x1 - P.x0, h); g.clip();
    g.setLineDash([]); g.lineJoin = g.lineCap = 'round';
    // A Julia picture has no iteration that only carries each point to its c. While the Mandelbrot half takes that
    // one, the Julia half waits where its own first iteration begins.
    const idle = P.mode === 'j' && at.sec === 'main' && at.pass < 1, sh = idle ? { ...at, ord: mov[0].ord, t: 0 } : at;
    // The pass whose dots are on show: the very start for the steps taken once before the iterations, and the pass
    // after the last for those taken once after.
    const key = early ? (P.mode === 'j' ? 0 : cuFirst() - 1) : at.sec === 'post' ? np + 1 : idle ? 1 : at.pass;
    // A Mandelbrot picture starts z at the middle for every point, and its first iteration only puts each point on
    // its own c. Until that is done a dot is drawn on its c, as the steps taken once have changed it by now, and not
    // at the middle: one dot for one point, as in the Learn tab. No step of that first iteration moves a dot.
    const onC = P.mode === 'm' && cuLead() === 1 && (early || (at.sec === 'main' && at.pass < 1)), waits = onC && !early;
    // The point the step works on is shown by the dots themselves where it is z, or c while the dots are drawn on
    // their c. Otherwise it gets a ring of its own, and `who` is what it is called: the one c of a Julia picture
    // before its iterations, or that point of the ringed dot.
    const own = tgt && !(onC && tgt === 'c'), who = !own ? null : P.mode === 'j' && tgt === 'c' && early ? 'c' : `the ringed dot’s ${tgt}`;
    // the step on show is the j-th of its section that a play can stand in; has any dot left the place it began at
    const j = Math.max(0, mov.findIndex(m => m.ord === sh.ord)), away = !idle && !onC && (at.sec === 'post' || (at.sec === 'main' && at.pass > (P.mode === 'j' ? 1 : 0)) || j > 0 || sh.t > 0);
    // The guides are drawn over the dots, at the size of what the camera sees, so that an axis or a plane fills
    // the picture whether points are thrown out beyond 2 or beyond 64. One dot stands for the others: it gets a ring.
    const all = cuDotsFind(key, P.mode), info = guidesOn && st && !idle && !waits ? cuStepInfo(sh, P.mode, all) : null, mark = info && info.M ? info.M.dot : null;
    const R = clamp(0.62 * eye * fov * Math.min(1, (P.x1 - P.x0) / h), 0.4, bail);
    // the rim of the big ball, as the eye sees it
    if (dotsOn && bail < 0.9 * eye) {
      const e = scl(b.pos, 1 / eye);
      g.strokeStyle = theme.ink2; g.lineWidth = 1.25; g.globalAlpha = 0.6; g.setLineDash([4, 4]);
      path(hoop(scl(e, bail * bail / eye), e, bail * Math.sqrt(1 - bail * bail / (eye * eye))));
      g.setLineDash([]); g.globalAlpha = 1;
    }
    // the dots on show, each where it is now: the handful (and the ringed one) apart from the rest. A far dot is
    // fainter than a near one. Very many dots are drawn as plain squares without tails, which is several times faster.
    const hand = new Set(dotsOn ? cuHandful(P.mode, all) : []), shown = dotsOn ? all : mark ? [mark] : [], small = [], large = [];
    if (mark) hand.add(mark);
    const plain = shown.length > CU_DOTS_PLAIN, gapPx = (all.gap || 0.2) * h / (2 * fov);
    const rad = zc => clamp(0.09 * gapPx / zc, 1.4, 3.6), shade = zc => 0.4 + 0.6 * clamp((eye + reach - zc) / (2 * reach), 0, 1);
    // where a dot is drawn, and where it was a moment before (for its tail)
    const place = (d, back) => (waits ? cuWhole(d) : cuPart(d, sh.ord, Math.max(0, sh.t - back), onC ? 'c' : undefined));
    const moving = sh.t > 0 && !waits && (!onC || tgt === 'c');
    let turned = !onC, tested = 0;   // of the first sixty dots, none has come nearer to the middle or gone further from it in this step
    // A point is thrown out when a pass is done: until the last step of the pass has been taken whole, a dot that
    // is beyond the bailout radius is drawn all the same, since a later step may bring it back.
    const passDone = sh.t >= 1 && j === mov.length - 1, dA = clamp(+C.dotsA || 1, 0.05, 1);
    let beyond = false;
    for (const d of shown) {
      const now = place(d, 0);
      if (!onC && tested < 60) { tested++; const before = len(cuPart(d, sh.ord, 0)); if (Math.abs(len(now) - before) > 1e-6 * Math.max(before, 1e-6)) turned = false; }
      if (!(len(now) <= bail)) { if (passDone && d !== mark) continue; beyond = beyond || !passDone; }   // thrown out, once the pass is done
      const A = scr(now);
      if (A) (hand.has(d) ? large : small).push({ A, B: !plain && moving ? scr(place(d, CU_DOTS_TAIL)) : null, d, now, r: rad(A[2]), al: shade(A[2]) });
    }
    // The whole path of a dot up to now, in two parts: where it was when each iteration so far began (old), and
    // its way through the steps of the iteration on show (cur). fine: those steps as the curves they are;
    // otherwise straight from the end of one step to the end of the next.
    const orbitOf = (o, fine) => {
      const d = o.d, v = cuBegin(d).v, cur = [d.z];
      if (v.some((x, k) => x !== d.z[k])) cur.push(v);   // the page's modifiers, which every iteration begins with
      for (let q = 0; q < j; q++) { if (fine) cur.push(...cuWayOf(d, mov, q)); else cur.push(cuEndOf(d, mov, q)); }
      if (fine && sh.t >= 1) cur.push(...cuWayOf(d, mov, j));
      else if (sh.t > 0) {
        const m = fine ? Math.max(1, Math.ceil(CU_WAY * sh.t)) : 1;
        for (let a = 1; a < m; a++) cur.push(cuPart(d, sh.ord, sh.t * a / m));
        cur.push(o.now);
      }
      return { old: d.was.concat([d.z]), cur };
    };
    const tail = (o, r) => { if (o.B) { g.strokeStyle = o.d.col; g.globalAlpha = 0.55 * o.al * dA; g.lineWidth = Math.max(1, 0.6 * r); g.beginPath(); g.moveTo(o.B[0], o.B[1]); g.lineTo(o.A[0], o.A[1]); g.stroke(); } };
    // every dot's orbit: thin lines, the dots of one colour in one go (the handful get theirs further down)
    if (dotsOn && orbits === 'all' && away) {
      const by = new Map();
      for (const o of small) { let l = by.get(o.d.col); if (!l) by.set(o.d.col, l = []); l.push(o); }
      g.lineWidth = 1; g.globalAlpha = 0.3 * dA;
      for (const [col, l] of by) { g.strokeStyle = col; g.beginPath(); for (const o of l) { const t = orbitOf(o, false); trace(t.old); trace(t.cur); } g.stroke(); }
    }
    small.sort((x, y) => y.A[2] - x.A[2]);   // the far ones first
    for (const o of small) {
      if (plain) { const q = 0.89 * o.r; g.globalAlpha = o.al * dA; g.fillStyle = o.d.col; g.fillRect(o.A[0] - q, o.A[1] - q, 2 * q, 2 * q); continue; }
      tail(o, o.r);
      g.globalAlpha = o.al * dA; g.fillStyle = o.d.col;
      circ(o.A, o.r); g.fill();
      if (o.r >= 2) { g.strokeStyle = 'rgba(0, 0, 0, 0.6)'; g.lineWidth = 0.8; g.stroke(); }
    }
    g.globalAlpha = 1;
    // a Mandelbrot picture whose steps taken once have moved the start: every dot stands on that one spot still
    if (P.mode === 'm' && early && !onC && dotsOn && small.length > 1 && len(sub(small[0].now, small[1].now)) < 1e-9) words.push([small[0].now, 'every dot is here: z starts at one place for all of them']);
    // The line under the bar, in the order of what matters most: what keeps the dots from showing, then what the
    // step on show does (the guides), then the rest. Only its beginning is shown (see the end of this function).
    if (shown.length || dotsOn) add1(P.mode === 'm' && S.z0.trim() !== '0' ? 'There are no dots while the Mandelbrot set starts z at something other than 0.'
      : !all.length && all.done ? 'No dot is left: the solid is too thin here for the dots to find it.' : '');
    if (info) {
      const G = looked ? cuValueGuide(st, P.mode, info.M) : cuGuides(st, R, P.mode, info.M, info.tests, who);
      for (const s of G.shapes) {
        g.strokeStyle = theme.brass; g.fillStyle = theme.brass; g.globalAlpha = s.faint ? 0.6 : 0.95; g.lineWidth = 1.6;
        if (s.ring || s.disc) {
          const [c, k, r] = s.ring || s.disc, pts = hoop(c, k, r);
          if (s.disc) {   // a plane: the circle filled, so that it reads as a sheet
            const flat = pts.map(scr);
            if (flat.every(q => q)) { g.globalAlpha = 0.2; g.beginPath(); flat.forEach((q, i) => (i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]))); g.closePath(); g.fill(); }
            g.globalAlpha = 0.45; g.lineWidth = 1; g.setLineDash([]); path([pts[0], pts[48]]); path([pts[24], pts[72]]);
            g.globalAlpha = 0.95; g.lineWidth = 1.6;
          }
          g.setLineDash(s.solid ? [] : [5, 4]); path(pts); g.setLineDash([]);
          if (s.label) words.push([pts[12], s.label]);
        } else {
          const [p0, p1] = s.line || s.arrow, pts = [];
          for (let q = 0; q <= 24; q++) pts.push(add(p0, scl(sub(p1, p0), q / 24)));
          g.setLineDash(s.faint ? [2, 4] : []); g.lineWidth = s.arrow ? 2.2 : 1.6;
          const [, tip] = path(pts);
          g.setLineDash([]);
          if (s.arrow) head(scr(add(p0, scl(sub(p1, p0), 0.9))), scr(p1));
          if (s.label) words.push([tip && !scr(p1) ? pts.filter(scr).pop() : p1, s.label]);
        }
      }
      // the way the ringed dot takes through the step (or the point of it that the step works on), in ink: a small
      // circle where it starts, an arrow head where it ends
      const way = looked ? [] : info.path;
      if (way.length) {
        g.setLineDash([]); g.globalAlpha = 0.95; g.lineWidth = 2.2; g.strokeStyle = g.fillStyle = ink;
        const [back, tip] = path(way), from = scr(way[0]);
        head(back, tip);
        if (from && tip && Math.hypot(tip[0] - from[0], tip[1] - from[1]) > 14) {
          circ(from, 4); g.stroke();
          words.push([way[0], 'before'], [way.filter(scr).pop(), 'after']);
        }
      }
      // the point the step works on, where the dots do not show it: a ring of its own, where it is now
      if (own && info.M) {
        const now = cuPart(info.M.dot, sh.ord, sh.t, 'on'), q = scr(now), still = info.M.still;
        if (q) {
          g.setLineDash([]); g.globalAlpha = 1; g.strokeStyle = 'rgba(0, 0, 0, 0.7)'; g.lineWidth = 4.5; circ(q, 6.5); g.stroke();
          g.strokeStyle = theme.brass; g.lineWidth = 2.2; circ(q, 6.5); g.stroke();
          words.push([now, who + (still ? ': this step leaves it where it is' : '')]);
        }
        add1(who === 'c' ? 'A Julia picture has one c for all its points (the ring), ' + (still ? 'and this step leaves it where it is: nothing moves.' : 'so this step moves that ring and no dot.')
          : `This step works on ${tgt}, not on z: the ring is ${who}, ` + (still ? 'which it leaves where it is here.' : 'and no dot moves.'));
      } else if (onC && tgt === 'c') add1('In a Mandelbrot picture each dot is drawn on its own c, so this step moves the dots.');
      g.globalAlpha = 1;
      G.notes.forEach(add1);
    }
    if (dotsOn && all.length) {
      if (idle) add1('Julia waits here: its points start where they stand, so it has no iteration that only adds c.');
      if (C.refill === false) add1(`${both ? (P.mode === 'm' ? 'Mandelbrot: ' : 'Julia: ') : ''}${all.length} of the ${all.start} dots of the start are still in.`);
      if (turned && sh.t > 0 && !looked && !tgt) add1('This step leaves each point as far from the middle as it was.');
      if (beyond) add1(`A dot beyond the dashed circle stays until ${at.sec === 'main' ? 'the iteration is' : 'these steps are'} done: a point is thrown out only if it ends beyond it.`);
    }
    // the handful, over the guides: each one's orbit in its own colour, then the dot itself, larger
    large.sort((x, y) => y.A[2] - x.A[2]);
    if (dotsOn && orbits !== 'none' && away) for (const o of large) {
      const t = orbitOf(o, true);
      for (const [pts, al] of [[t.old, 0.5], [t.cur, 1]]) {
        g.strokeStyle = 'rgba(0, 0, 0, 0.6)'; g.lineWidth = 4; g.globalAlpha = 0.7 * al * dA; g.beginPath(); trace(pts); g.stroke();
        g.strokeStyle = o.d.col; g.lineWidth = 1.8; g.globalAlpha = al * dA; g.beginPath(); trace(pts); g.stroke();
      }
    }
    const big = r => 1.5 * Math.max(r, 1.8) + 1;
    for (const o of large) {
      const r = big(o.r);
      if (orbits === 'none' || !dotsOn) tail(o, r);
      g.globalAlpha = dA; g.fillStyle = o.d.col; g.strokeStyle = 'rgba(0, 0, 0, 0.8)'; g.lineWidth = 1.5;
      circ(o.A, r); g.fill(); g.stroke();
      g.strokeStyle = ink; g.lineWidth = 1.3; circ(o.A, r + 2); g.stroke();
      if (o.d === mark) { g.globalAlpha = 1; g.lineWidth = 2.5; circ(o.A, r + 6.5); g.stroke(); }   // the ring stays at full strength
    }
    // the words, last and over everything; one that would cover another is put under it
    const taken = [];
    for (const [p, text] of words) {
      const q = p && scr(p);
      if (!q) continue;
      g.font = '600 13px ' + font; g.textBaseline = 'middle'; g.setLineDash([]); g.globalAlpha = 1;
      const tw = g.measureText(text).width, x = clamp(q[0] + 10, P.x0 + 4, Math.max(P.x0 + 4, P.x1 - tw - 8));
      let y = clamp(q[1], 12, h - 12);
      for (let tries = 0; tries < 12 && taken.some(r => x < r[0] + r[2] + 6 && r[0] < x + tw + 6 && Math.abs(r[1] - y) < 22); tries++) y = y + 22 > h - 12 ? 12 : y + 22;
      taken.push([x, y, tw]);
      g.fillStyle = `rgba(${theme.stage.map(c => Math.round(255 * c)).join(', ')}, 0.82)`; g.fillRect(x - 4, y - 10, tw + 8, 20);
      g.fillStyle = theme.brass; g.fillText(text, x, y);
    }
    g.restore();
  }
  // A sentence or two under the bar, so that the steps keep their room: the notes in their order for as long as
  // they stay short, and the first of them in any case. All of them are in the line's tooltip.
  let brief = '';
  for (const line of notes) { if (brief && brief.length + line.length > 230) break; brief += (brief ? ' ' : '') + line; }
  say.hidden = !brief;
  say.textContent = brief;
  say.title = notes.length > 1 ? notes.join(' ') : '';
}
function cuOverInit() {
  const cv = document.createElement('canvas');
  cv.className = 'cu-dots'; cv.setAttribute('aria-hidden', 'true');
  $('view').after(cv);
  CUD.cv = cv;
  const again = () => { CUD.drawn = ''; cuOverDraw(); };
  // the choices for the dots (how many, where they start and how far out, their colours, the orbits, new dots) need the dots
  const picks = [['cuCount', 'count'], ['cuLay', 'lay'], ['cuTint', 'tint'], ['cuOrbits', 'orbits']];
  const able = () => { for (const id of [...picks.map(x => x[0]), 'cuRefill', 'cuReach', 'cuDotsA']) $(id).disabled = S.custom.see === 'skin'; };
  // how strongly the dots and the surface are drawn: the dots on their own canvas, the surface by the style sheet (--cu-skin)
  const skin = () => document.documentElement.style.setProperty('--cu-skin', String(clamp(+(S.custom.skinA ?? 1), 0, 1)));
  $('cuDotsA').value = Math.round(100 * (S.custom.dotsA ?? 1)); $('cuSkinA').value = Math.round(100 * (S.custom.skinA ?? 1));
  $('cuDotsA').addEventListener('input', () => { S.custom.dotsA = clamp(+$('cuDotsA').value / 100, 0.05, 1); again(); });
  $('cuSkinA').addEventListener('input', () => { S.custom.skinA = clamp(+$('cuSkinA').value / 100, 0, 1); skin(); });
  skin();
  for (const [id, key] of [['cuGuidesOn', 'guides'], ['cuRefill', 'refill']]) {
    $(id).checked = S.custom[key] !== false;
    $(id).addEventListener('change', () => { S.custom[key] = $(id).checked; again(); });
  }
  for (const [id, key] of [...picks, ['cuSee', 'see'], ['cuSpeed', 'speed']]) {
    $(id).value = S.custom[key];
    $(id).addEventListener('change', () => { S.custom[key] = $(id).value; able(); again(); });
  }
  $('cuReach').value = cuShort(S.custom.reach);
  $('cuReach').addEventListener('change', () => { S.custom.reach = clamp(+$('cuReach').value || 2, 0.25, 16); $('cuReach').value = cuShort(S.custom.reach); again(); });
  able();
  // both pictures at once: the shader draws the two halves (see cuUniforms), and the Julia panel shows for its c
  $('cuThrough').checked = S.custom.through !== false;
  $('cuThrough').addEventListener('change', () => { S.custom.through = $('cuThrough').checked; });
  $('cuBothOn').checked = !!S.custom.both;
  $('cuBothOn').addEventListener('change', () => { S.custom.both = $('cuBothOn').checked; CUI.barSig = ''; refresh(); });
  hooks.view.push(cuOverDraw); hooks.refresh.push(again);
  addEventListener('resize', again);
}
