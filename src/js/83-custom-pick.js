// The list of the kinds of step, as a panel that opens under a button: the one beside "Add step", and a step's
// Change. It holds a box to search in, the user's saved steps, which can be renamed and deleted here, and the kinds
// by group, each group open or shut. cuPickOpen(anchor, now, done) shows it with `now` marked; done(value) gets the
// choice: a kind, or @0, @1, ... for a saved step (cuKeptAt). Which groups are shut is kept in localStorage.
const CU_PICK_KEY = 'squaringLab.customPick';
const CU_PICK_MINE = 'Your saved steps';
const CUP = {
  el: null, anchor: null, done: null, now: '',
  shut: new Set(),       // the groups that are shut, by name
  edit: -1,              // the saved step that is being renamed (its place in CUI.kept), or -1
};

// The groups with their entries: { v, t, sub, k }, the value, the name, for a saved step its kind and its place.
// A saved container has, in the place of a kind, how many steps it holds.
function cuPickGroups() {
  const held = s => { const n = cuLeaves(s.steps); return `${n} step${n === 1 ? '' : 's'} in one`; };
  return [[CU_PICK_MINE, CUI.kept.map((s, k) => ({ v: '@' + k, t: s.name, sub: s.steps ? held(s) : CU_BLOCKS[s.kind].title, k }))],
    ...CU_GROUPS.map(g => [g, Object.entries(CU_BLOCKS).filter(([, B]) => B.group === g).map(([v, B]) => ({ v, t: B.title }))])];
}
function cuPickSay(text) { const p = $('cuPickSay'); p.textContent = text || ''; p.hidden = !text; }
function cuPickDraw() {
  const words = $('cuPickQ').value.toLowerCase().split(/\s+/).filter(Boolean), groups = cuPickGroups();
  const hit = o => words.every(w => (o.t + ' ' + (o.sub || '')).toLowerCase().includes(w));
  let html = '', found = 0;
  for (const [g, all] of groups) {
    const items = words.length ? all.filter(hit) : all, mine = g === CU_PICK_MINE;
    if (words.length && !items.length) continue;
    found += items.length;
    const open = words.length > 0 || !CUP.shut.has(g);   // a search looks into every group
    html += `<section class="cu-pick-sec"><button type="button" class="cu-pick-head" data-g="${cuEsc(g)}" aria-expanded="${open}">${cuEsc(g)}<span class="note">${items.length}</span></button>`;
    if (open && mine && !all.length) html += '<p class="note cu-pick-none">None yet. Save, among a step’s tools, keeps that step here with its settings. Several steps that are selected (Shift-click, Ctrl-click) can be saved as one.</p>';
    if (open) {
      html += '<ul>' + items.map(o => (mine && CUP.edit === o.k
        ? `<li class="cu-pick-mine"><input type="text" class="cu-in" id="cuPickName" maxlength="40" value="${cuEsc(o.t)}" aria-label="The new name of this saved step" spellcheck="false" autocomplete="off">` +
          `<button type="button" class="cu-tool" data-mine="ok" data-k="${o.k}">Save</button><button type="button" class="cu-tool" data-mine="cancel">Cancel</button></li>`
        : `<li${mine ? ' class="cu-pick-mine"' : ''}><button type="button" class="cu-pick-item${o.v === CUP.now ? ' is-on' : ''}" data-value="${o.v}">${cuEsc(o.t)}${o.sub ? `<span class="cu-of-kind">${cuEsc(o.sub)}</span>` : ''}</button>` +
          (mine ? `<button type="button" class="cu-tool" data-mine="rename" data-k="${o.k}" title="Give this saved step another name">Rename</button>` +
            `<button type="button" class="cu-tool" data-mine="delete" data-k="${o.k}" title="Take this saved step off the list. The steps of your approach stay as they are.">Delete</button>` : '') + '</li>')).join('') + '</ul>';
    }
    html += '</section>';
  }
  $('cuPickList').innerHTML = words.length && !found ? '<p class="note cu-pick-none">No step has that in its name.</p>' : html;
  const shut = $('cuPickShut');
  shut.textContent = groups.every(([g]) => CUP.shut.has(g)) ? 'Open all' : 'Collapse all';
  shut.disabled = words.length > 0;
}
function cuPickKeep() {
  try { localStorage.setItem(CU_PICK_KEY, JSON.stringify([...CUP.shut])); } catch (err) { /* storage blocked: the groups are as they are for this visit */ }
}
function cuPickOpen(anchor, now, done) {
  const P = CUP;
  if (!P.el) cuPickBuild();
  P.anchor = anchor; P.now = String(now); P.done = done; P.edit = -1;
  $('cuPickQ').value = ''; cuPickSay('');
  cuPickDraw();
  P.el.hidden = false;
  cuPickPlace();
  anchor.setAttribute('aria-expanded', 'true');
  const list = $('cuPickList'), on = list.querySelector('.cu-pick-item.is-on');
  list.scrollTop = on ? Math.max(0, on.offsetTop - list.offsetTop - list.clientHeight / 2) : 0;
  $('cuPickQ').focus({ preventScroll: true });
}
// The panel stands under its button, as tall as the window has room for there; over the button where there is more
// room. It is put there again when the window changes or the page moves under it: a phone's keyboard does both
// when the search box takes the focus.
function cuPickPlace() {
  const P = CUP;
  if (!P.el || P.el.hidden) return;
  if (!P.anchor || !P.anchor.isConnected) { cuPickClose(false); return; }
  const r = P.anchor.getBoundingClientRect(), below = innerHeight - r.bottom - 12, above = r.top - 12, under = below >= 300 || below >= above;
  P.el.style.maxHeight = clamp(under ? below : above, 180, 540) + 'px';
  P.el.style.left = clamp(r.left, 8, Math.max(8, innerWidth - P.el.offsetWidth - 8)) + 'px';
  P.el.style.top = under ? Math.max(8, r.bottom + 4) + 'px' : 'auto';
  P.el.style.bottom = under ? 'auto' : Math.max(8, innerHeight - r.top + 4) + 'px';
}
// back: the keyboard goes back to the button that opened the panel
function cuPickClose(back) {
  const P = CUP, anchor = P.anchor;
  if (!P.el || P.el.hidden) return;
  P.el.hidden = true; P.anchor = null; P.done = null;
  if (anchor) { anchor.setAttribute('aria-expanded', 'false'); if (back && anchor.isConnected) anchor.focus({ preventScroll: true }); }
}
function cuPickBuild() {
  const P = CUP, el = document.createElement('div');
  el.className = 'cu-pick'; el.id = 'cuPick'; el.hidden = true;
  el.setAttribute('role', 'dialog'); el.setAttribute('aria-label', 'The kinds of step, and your saved steps');
  el.innerHTML = '<div class="cu-pick-top"><input type="search" class="cu-in" id="cuPickQ" placeholder="Search the steps" aria-label="Search the steps by name" autocomplete="off" spellcheck="false">' +
    '<button type="button" class="cu-tool" id="cuPickShut">Collapse all</button></div><p class="note" id="cuPickSay" role="status" hidden></p><div class="cu-pick-list" id="cuPickList"></div>';
  document.body.append(el);
  P.el = el;
  try {
    const shut = JSON.parse(localStorage.getItem(CU_PICK_KEY) || '[]');
    if (Array.isArray(shut)) P.shut = new Set(shut.filter(g => typeof g === 'string'));
  } catch (err) { /* storage blocked: every group starts open */ }
  const pick = v => { const done = P.done; cuPickClose(true); if (done) done(v); };
  const rename = k => { const say = cuKeptRename(k, $('cuPickName').value); if (say) { cuPickSay(say); return; } P.edit = -1; cuPickSay(''); cuPickDraw(); };
  $('cuPickQ').addEventListener('input', () => { P.edit = -1; cuPickDraw(); $('cuPickList').scrollTop = 0; });
  el.addEventListener('click', e => {
    const head = e.target.closest('.cu-pick-head'), tool = e.target.closest('[data-mine]'), item = e.target.closest('.cu-pick-item');
    if (e.target.closest('#cuPickShut')) {
      const names = cuPickGroups().map(x => x[0]);
      P.shut = names.every(g => P.shut.has(g)) ? new Set() : new Set(names);
      cuPickKeep(); cuPickDraw();
    } else if (head) {
      const g = head.dataset.g;
      if (P.shut.has(g)) P.shut.delete(g); else P.shut.add(g);
      cuPickKeep(); cuPickDraw();
      const again = [...el.querySelectorAll('.cu-pick-head')].find(b => b.dataset.g === g);
      if (again) again.focus({ preventScroll: true });
    } else if (tool) {
      const what = tool.dataset.mine, k = +tool.dataset.k;
      cuPickSay('');
      if (what === 'ok') { rename(k); return; }
      if (what === 'delete') { const name = CUI.kept[k] ? CUI.kept[k].name : ''; cuKeptDrop(k); if (P.now[0] === '@') P.now = ''; cuPickSay(`“${name}” is off the list. The steps of your approach stay as they are.`); }
      P.edit = what === 'rename' ? k : -1;
      cuPickDraw();
      if (what === 'rename') { $('cuPickName').focus(); $('cuPickName').select(); }
    } else if (item) pick(item.dataset.value);
  });
  el.addEventListener('keydown', e => {
    const items = [...el.querySelectorAll('.cu-pick-item')], at = items.indexOf(document.activeElement);
    if (e.key === 'Escape') {
      e.preventDefault();
      if (P.edit >= 0) { P.edit = -1; cuPickDraw(); $('cuPickQ').focus(); } else cuPickClose(true);
    } else if (e.key === 'Enter' && e.target.id === 'cuPickName') { e.preventDefault(); rename(P.edit); }
    else if (e.key === 'Enter' && e.target.id === 'cuPickQ') { e.preventDefault(); if ($('cuPickQ').value.trim() && items.length) pick(items[0].dataset.value); }
    else if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && items.length && e.target.id !== 'cuPickName') {
      e.preventDefault();
      const to = e.key === 'ArrowDown' ? at + 1 : at - 1;
      if (to < 0) $('cuPickQ').focus(); else items[Math.min(to, items.length - 1)].focus();
    }
  });
  // a press anywhere else puts the panel away
  document.addEventListener('pointerdown', e => { if (!el.hidden && !el.contains(e.target) && !(P.anchor && P.anchor.contains(e.target))) cuPickClose(false); }, true);
  window.addEventListener('resize', cuPickPlace);
  window.addEventListener('scroll', e => { if (!el.hidden && !(e.target instanceof Node && el.contains(e.target))) cuPickPlace(); }, true);
}
