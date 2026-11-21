// Layout audit run inside the page. Returns a plain object.
const out = {};
const de = document.documentElement;
const vis = e => !!(e.checkVisibility ? e.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true }) : e.offsetParent);
const name = e => {
  let s = e.tagName.toLowerCase();
  if (e.id) s += '#' + e.id; else if (typeof e.className === 'string' && e.className.trim()) s += '.' + e.className.trim().split(/\s+/).join('.');
  const t = (e.getAttribute('aria-label') || e.textContent || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 36);
  return s + (t ? ' "' + t + '"' : '');
};
const R = e => { const r = e.getBoundingClientRect(); return { l: r.left, t: r.top + scrollY, r: r.right, b: r.bottom + scrollY, w: r.width, h: r.height }; };
const rnd = x => Math.round(x * 10) / 10;

out.win = [innerWidth, innerHeight];
out.doc = [de.scrollWidth, de.scrollHeight, de.clientWidth];
out.hscroll = de.scrollWidth - de.clientWidth;
out.coarse = matchMedia('(pointer: coarse)').matches;

// 1. anything sticking out of the window sideways
out.offSide = [];
for (const e of document.querySelectorAll('body *')) {
  if (!vis(e)) continue;
  const r = e.getBoundingClientRect();
  if (!r.width || !r.height) continue;
  if (r.right > innerWidth + 0.5 || r.left < -0.5) out.offSide.push([name(e), rnd(r.left), rnd(r.right)]);
}
out.offSide = out.offSide.slice(0, 40);

// 2. controls wider than their column (the nearest section body / sidebar / card)
out.wider = [];
for (const e of document.querySelectorAll('aside.dials *, .lower *, footer *, .masthead *')) {
  if (!vis(e)) continue;
  const host = e.parentElement.closest('.sec-body, details.sec, aside.dials, .card, .step, .score, footer, .masthead, .page');
  if (!host) continue;
  const r = e.getBoundingClientRect(), h = host.getBoundingClientRect();
  if (!r.width) continue;
  if (r.left < h.left - 0.6 || r.right > h.right + 0.6) out.wider.push([name(e), 'in ' + name(host).slice(0, 30), rnd(r.left - h.left), rnd(r.right - h.right)]);
}
out.wider = out.wider.slice(0, 40);

// 3. clipped text: boxes that hide overflow and hold more than they show; selects and inputs whose text is wider than the box
out.clipped = [];
const cv = document.createElement('canvas').getContext('2d');
const textW = (txt, cs) => { cv.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily; let w = cv.measureText(txt).width; const ls = parseFloat(cs.letterSpacing); if (ls) w += ls * txt.length; return w; };
for (const e of document.querySelectorAll('body *')) {
  if (!vis(e)) continue;
  const cs = getComputedStyle(e);
  if (e.tagName === 'SELECT') {
    let txt = e.selectedOptions[0] ? e.selectedOptions[0].textContent : '';
    if (cs.textTransform === 'uppercase') txt = txt.toUpperCase();
    const room = e.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 18;
    const w = textW(txt, cs);
    if (w > room + 1) out.clipped.push(['select', name(e), 'shown text ' + rnd(w) + ' px, room ' + rnd(room)]);
    let worst = 0, wt = '';
    for (const o of e.options) { const ww = textW(o.textContent, cs); if (ww > worst) { worst = ww; wt = o.textContent; } }
    if (worst > room + 1) out.clipped.push(['select-option', name(e), 'longest option "' + wt.slice(0, 50) + '" ' + rnd(worst) + ' px, room ' + rnd(room)]);
    continue;
  }
  if (e.tagName === 'INPUT' && /^(text|search|)$/.test(e.type)) {
    const txt = e.value || e.placeholder || '';
    const room = e.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    const w = textW(txt, cs);
    if (w > room + 1) out.clipped.push([e.value ? 'input-value' : 'input-placeholder', name(e), '"' + txt.slice(0, 40) + '" ' + rnd(w) + ' px, room ' + rnd(room)]);
    continue;
  }
  if ((cs.overflowX !== 'visible' || cs.overflowY !== 'visible') && e.tagName !== 'CANVAS' && e.tagName !== 'HTML' && e.tagName !== 'BODY') {
    if (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) out.clipped.push(['overflow', name(e), 'scroll ' + e.scrollWidth + 'x' + e.scrollHeight + ' client ' + e.clientWidth + 'x' + e.clientHeight + ' ' + cs.overflowX + '/' + cs.overflowY]);
  }
}
out.clipped = out.clipped.slice(0, 60);

// 4. labels and buttons whose text wraps onto more than one line
out.wrapped = [];
for (const e of document.querySelectorAll('button, summary, .seg span, label, .label, legend, .dial-step, .cam-end, option')) {
  if (!vis(e) || e.tagName === 'OPTION') continue;
  const tn = [...e.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim());
  if (!tn.length && e.children.length) continue;
  const rg = document.createRange(); rg.selectNodeContents(e);
  const tops = new Set([...rg.getClientRects()].filter(r => r.width > 1).map(r => Math.round(r.top / 4)));
  if (tops.size > 1) out.wrapped.push([name(e), tops.size + ' lines', rnd(e.getBoundingClientRect().width) + ' px wide']);
}
out.wrapped = out.wrapped.slice(0, 60);

// 5. touch targets
out.small = [];
const seen = new Set();
for (const e of document.querySelectorAll('a[href], button, input, select, summary, textarea, [tabindex]:not([tabindex="-1"]), [role="slider"]')) {
  if (!vis(e) || e.disabled) continue;
  let r = e.getBoundingClientRect();
  let lab = e.closest('label') || (e.id && document.querySelector('label[for="' + CSS.escape(e.id) + '"]'));
  if (lab && /^(checkbox|radio)$/.test(e.type || '')) { const q = lab.getBoundingClientRect(); r = { width: Math.max(r.right, q.right) - Math.min(r.left, q.left), height: Math.max(r.bottom, q.bottom) - Math.min(r.top, q.top) }; }
  if (!r.width && !r.height) continue;
  const key = e.tagName + '.' + (typeof e.className === 'string' ? e.className : '') + '|' + (e.type || '') + '|' + Math.round(r.width) + 'x' + Math.round(r.height);
  if (Math.min(r.width, r.height) < 30) { if (!seen.has(key)) { seen.add(key); out.small.push([name(e), rnd(r.width) + 'x' + rnd(r.height)]); } }
}

// 6. contrast of every visible piece of text against the nearest solid background
const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) { const q = c.match(/color\(srgb ([\d.]+) ([\d.]+) ([\d.]+)(?: \/ ([\d.]+))?\)/); if (q) return [q[1] * 255, q[2] * 255, q[3] * 255, q[4] === undefined ? 1 : +q[4]]; return [0, 0, 0, 1]; } const p = m[1].split(/[ ,/]+/).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
const over = (f, b) => [f[0] * f[3] + b[0] * (1 - f[3]), f[1] * f[3] + b[1] * (1 - f[3]), f[2] * f[3] + b[2] * (1 - f[3]), 1];
const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
const bgOf = e => { const stack = []; for (let n = e; n; n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c[3] > 0) { stack.push(c); if (c[3] >= 0.999) break; } } let b = [255, 255, 255, 1]; if (!stack.length || stack[stack.length - 1][3] < 0.999) { const root = parse(getComputedStyle(document.body).backgroundColor); b = root[3] > 0 ? over(root, b) : b; } for (let i = stack.length - 1; i >= 0; i--) b = over(stack[i], b); return b; };
const hex = c => '#' + [0, 1, 2].map(i => Math.round(c[i]).toString(16).padStart(2, '0')).join('');
const groups = new Map();
const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
for (let n = tw.nextNode(); n; n = tw.nextNode()) {
  const txt = n.textContent.trim(); if (!txt) continue;
  const e = n.parentElement; if (!e || !vis(e) || /^(SCRIPT|STYLE|OPTION|TITLE)$/.test(e.tagName)) continue;
  const cs = getComputedStyle(e); let op = 1; for (let m = e; m; m = m.parentElement) op *= parseFloat(getComputedStyle(m).opacity);
  const bg = bgOf(e); let fg = parse(cs.color); fg[3] *= op; fg = over(fg, bg);
  const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700; const big = size >= 24 || (size >= 18.66 && bold);
  const cr = ratio(fg, bg);
  const dis = !!e.closest(':disabled, [aria-disabled="true"]');
  const key = hex(fg) + ' on ' + hex(bg) + ' ' + size + 'px' + (dis ? ' disabled' : '');
  if (!groups.has(key)) groups.set(key, { key, ratio: rnd(cr), big, n: 0, eg: [] });
  const g = groups.get(key); g.n++; if (g.eg.length < 4) g.eg.push(name(e).slice(0, 60));
}
for (const e of document.querySelectorAll('input[placeholder], select, input[type=text]')) {
  if (!vis(e)) continue;
  const bg = bgOf(e);
  if (e.placeholder && !e.value) { const fg = over(parse(getComputedStyle(e, '::placeholder').color), bg); const key = 'placeholder ' + hex(fg) + ' on ' + hex(bg); if (!groups.has(key)) groups.set(key, { key, ratio: rnd(ratio(fg, bg)), n: 0, eg: [] }); const g = groups.get(key); g.n++; if (g.eg.length < 3) g.eg.push(name(e).slice(0, 60)); }
  else { const cs = getComputedStyle(e); let fg = over(parse(cs.color), bg); const key = 'control-text ' + hex(fg) + ' on ' + hex(bg) + ' ' + cs.fontSize; if (!groups.has(key)) groups.set(key, { key, ratio: rnd(ratio(fg, bg)), n: 0, eg: [] }); const g = groups.get(key); g.n++; if (g.eg.length < 3) g.eg.push(name(e).slice(0, 60)); }
}
out.contrast = [...groups.values()].sort((a, b) => a.ratio - b.ratio).filter(g => g.ratio < 4.6);
out.contrastAll = [...groups.values()].length;

// 7. overlays on the stage: boxes and pairwise overlap
const stage = document.getElementById('stage');
if (stage) {
  const sr = stage.getBoundingClientRect();
  out.stage = { w: rnd(sr.width), h: rnd(sr.height), top: rnd(sr.top + scrollY), left: rnd(sr.left) };
  const leaves = [];
  for (const e of stage.querySelectorAll('*')) {
    if (e.tagName === 'CANVAS' || !vis(e)) continue;
    if (e.closest('svg') && e.tagName !== 'svg') continue;
    const r = e.getBoundingClientRect(); if (r.width < 1 || r.height < 1) continue;
    const kids = [...e.children].filter(k => vis(k) && k.getBoundingClientRect().width > 0);
    const ownText = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (kids.length && !ownText && e.tagName !== 'svg' && getComputedStyle(e).backgroundColor === 'rgba(0, 0, 0, 0)' && !/cam-rail/.test(e.className)) continue;
    leaves.push({ e, n: name(e).slice(0, 50), r });
  }
  out.overlays = leaves.map(o => [o.n, rnd(o.r.left - sr.left), rnd(o.r.top - sr.top), rnd(o.r.width), rnd(o.r.height)]);
  out.overlap = [];
  for (let i = 0; i < leaves.length; i++) for (let j = i + 1; j < leaves.length; j++) {
    const a = leaves[i], b = leaves[j]; if (a.e.contains(b.e) || b.e.contains(a.e)) continue;
    const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left), h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
    if (w > 0.5 && h > 0.5) out.overlap.push([a.n, b.n, rnd(w) + 'x' + rnd(h)]);
  }
  let area = 0; for (const o of leaves) area += o.r.width * o.r.height;
  out.overlayShare = rnd(100 * area / (sr.width * sr.height));
  out.outsideStage = leaves.filter(o => o.r.left < sr.left - 0.5 || o.r.right > sr.right + 0.5 || o.r.top < sr.top - 0.5 || o.r.bottom > sr.bottom + 0.5).map(o => o.n);
}

// 8. section rhythm: summary boxes, gaps, reset buttons
out.sections = [...document.querySelectorAll('#sections > details.sec')].filter(vis).map(d => {
  const s = d.querySelector('summary'), body = d.querySelector('.sec-body'); const r = R(d), sr2 = R(s); const cs = getComputedStyle(d), bs = body ? getComputedStyle(body) : null;
  const reset = [...d.querySelectorAll('button')].filter(b => /reset/i.test(b.textContent) && vis(b)).pop();
  const rr = reset ? R(reset) : null;
  return { id: d.id, sum: s.textContent.trim().slice(0, 30), l: rnd(r.l), w: rnd(r.w), sumH: rnd(sr2.h), padT: cs.paddingTop, padB: cs.paddingBottom, mb: cs.marginBottom, bt: cs.borderTopWidth, bodyGap: bs ? bs.gap : '', bodyPad: bs ? bs.padding : '',
    reset: reset ? { text: reset.textContent.trim(), l: rnd(rr.l - r.l), w: rnd(rr.w), h: rnd(rr.h), fromBottom: rnd(r.b - rr.b), prevGap: reset.previousElementSibling ? rnd(rr.t - R(reset.previousElementSibling).b) : null } : null };
});
return out;
