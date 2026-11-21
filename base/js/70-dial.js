// ---------- controls kit: dials (a slider with a typed box), checkboxes, drop-downs, and controls built from specs.
// `host` is an element or the id of one. Every control registers itself so it can be re-read or reset.
const controls = [];   // { el, group, sync(), reset() }
const hostEl = h => (typeof h === 'string' ? $(h) : h);
function addDial(host, id, label, min, max, step, get, set, o = {}) {
  const el = document.createElement('div');
  el.className = 'dial';
  el.innerHTML = `<label class="label" for="${id}">${label}</label><input class="num" type="number" id="${id}Num" step="${step}" aria-label="${label}, typed value"><input type="range" id="${id}" min="${min}" max="${max}" step="${step}">`;
  hostEl(host).appendChild(el);
  const r = el.querySelector('input[type=range]'), n = el.querySelector('.num');
  const lo = o.lo === undefined ? min : o.lo, hi = o.hi === undefined ? max : o.hi, def = o.def === undefined ? get() : o.def;
  const fix = v => { v = clamp(v, lo, hi); if (o.int || o.odd) v = Math.round(v); if (o.odd && v % 2 === 0) v += 1; return v; };
  const sync = () => { const v = get(); r.value = v; n.value = +(+v).toFixed(4); };
  sync();
  r.addEventListener('input', () => { set(fix(+r.value)); n.value = +(+get()).toFixed(4); });
  n.addEventListener('change', () => { const v = parseFloat(n.value); if (isFinite(v)) set(fix(v)); sync(); });
  const c = { el, group: o.group, sync, reset: () => { set(def); sync(); } };
  controls.push(c);
  return c;
}
function addCheck(host, id, label, get, set, o = {}) {
  const el = document.createElement('label');
  el.className = 'check';
  el.innerHTML = `<input type="checkbox" id="${id}"> ${label}`;
  hostEl(host).appendChild(el);
  const box = el.querySelector('input'), def = o.def === undefined ? get() : o.def;
  const sync = () => { box.checked = !!get(); };
  sync();
  box.addEventListener('change', () => set(box.checked));
  const c = { el, group: o.group, sync, reset: () => { set(def); sync(); } };
  controls.push(c);
  return c;
}
function addSelect(host, id, label, options, get, set, o = {}) {   // options: [[value, text], ...]
  const el = document.createElement('div');
  el.className = 'field';
  el.innerHTML = `<label class="label" for="${id}">${label}</label><select id="${id}"></select>`;
  hostEl(host).appendChild(el);
  const sel = el.querySelector('select'), def = o.def === undefined ? get() : o.def;
  options.forEach(([, text], i) => sel.add(new Option(text, i)));
  const sync = () => { sel.value = String(Math.max(0, options.findIndex(([v]) => v === get()))); };
  sync();
  sel.addEventListener('change', () => set(options[+sel.value][0]));
  const c = { el, group: o.group, sync, reset: () => { set(def); sync(); } };
  controls.push(c);
  return c;
}
// Build controls from specs: { type: 'dial' | 'select' | 'check' | 'note', key, label, def, ... , when: obj => bool }.
// Values are read from and written to obj[key]; onChange() runs after every change; `when` hides a control.
function buildControls(host, specs, obj, onChange, o = {}) {
  const made = [];
  const update = () => made.forEach(([s, c]) => { if (s.when) c.el.hidden = !s.when(obj); });
  const changed = () => { update(); if (onChange) onChange(); };
  specs.forEach(s => {
    const id = (o.idPrefix || '') + (s.key === undefined ? 'note' + made.length : s.key);
    const get = () => obj[s.key], set = v => { obj[s.key] = v; changed(); };
    let c;
    if (s.type === 'dial') c = addDial(host, id, s.label, s.min, s.max, s.step, get, set, { ...s, group: o.group });
    else if (s.type === 'select') c = addSelect(host, id, s.label, s.options, get, set, { def: s.def, group: o.group });
    else if (s.type === 'check') c = addCheck(host, id, s.label, get, set, { def: s.def, group: o.group });
    else { const p = document.createElement('p'); p.className = 'note'; p.textContent = s.text; hostEl(host).appendChild(p); c = { el: p, sync() {}, reset() {} }; }
    made.push([s, c]);
  });
  update();
  return { sync: () => { made.forEach(([, c]) => c.sync()); update(); } };
}
function syncControls() { controls.forEach(c => c.sync()); }
function resetGroup(group) { controls.filter(c => c.group === group).forEach(c => c.reset()); }
