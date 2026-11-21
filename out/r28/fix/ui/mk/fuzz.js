// Round 28, dial checker (ui): 3000 random moves of the three dials of Balls on balls, one after another, and after
// each move the rules of docs/ROUND28.md section 1.2 are asked of the page.
// BY SCRIPT, not real input: a value is put into the typed box and the box's own "input" and Enter-key events are
// sent (so the dial's own code takes the value, clamps it and calls its setter), or the slider's value is set and
// its "input" and "change" events are sent. Run through tools/shot.py (out/r28/fix/ui/mk/fuzz.py).
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const vis = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await sleep(400); }
let seed = 2026112001; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const type = (id, text) => { const n = $(id + 'Num'); n.focus(); n.value = text; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true })); };
const slide = (id, v) => { const r = $(id); r.value = v; r.dispatchEvent(new Event('input', { bubbles: true })); r.dispatchEvent(new Event('change', { bubbles: true })); };
const key = (id, k, onSlider) => { const e = onSlider ? $(id) : $(id + 'Num'); e.focus(); e.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true })); };
const warn = () => (vis($('ballsWarn')) ? $('ballsWarn').textContent : '');
const pick = a => a[Math.floor(rnd() * a.length)];
const SIZES = [0, 1, 1.5, 2, 10, 49.99, 50, 55.56, 80, 99.9, 100, 100.1, 101, 120, 150, 199.9, 200, 200.1, 250, 300, 399.9, 400, 400.1, 800, 1000, 1999.9, 2000, 5000, -5];
const RHOS = [0, 1, 2, 2.5, 5, 10, 12.5, 16.67, 20, 25, 30, 33.33, 40, 45, 49.5, 49.99, 50, 50.01, 51, 60, 74.99, 75, 75.01, 76, 90, 99, 100, 150, -5];
const DEPTHS = [0, 1, 2, 4, 5, 16, 40, 100, 101, 1000, 5000];
const bad = [], count = {}, tell = (k, text) => { count[k] = (count[k] || 0) + 1; if (bad.length < 40 && count[k] <= 4) bad.push(k + ': ' + text); };
const rhoFrom = v => (v > 75 ? 100 : Math.min(50, Math.max(2, v)));
let moves = 0, gaveSize = 0, gaveRho = 0, touching = 0, past100 = 0;
const hist = [];
for (let i = 0; i < 3000; i++) {
  const before = { p: +$('ballsSizeNum').value, r: +$('ballsRhoNum').value, d: +$('ballsDepthNum').value, bt: S.k.bt, brho: S.k.brho };
  const kind = rnd(); let what, wantP = null, wantR = null, wantD = null;
  if (kind < 0.40) { const v = rnd() < 0.7 ? pick(SIZES) : +(1 + rnd() * rnd() * 700).toFixed(1); type('ballsSize', String(v)); what = 'size typed ' + v; wantP = Math.min(2000, Math.max(1, v)); }
  else if (kind < 0.50) { const v = +(2 + Math.floor(rnd() * 3981) / 10).toFixed(1); slide('ballsSize', v); what = 'size slider ' + v; wantP = v; }
  else if (kind < 0.78) { const v = rnd() < 0.8 ? pick(RHOS) : +(2 + rnd() * 98).toFixed(2); type('ballsRho', String(v)); what = 'second sphere typed ' + v; wantR = rhoFrom(Math.min(100, Math.max(2, v))); }
  else if (kind < 0.86) { const v = 2 + Math.floor(rnd() * 99); slide('ballsRho', v); what = 'second sphere slider ' + v; wantR = rhoFrom(v); }
  else if (kind < 0.90) { const k = pick(['ArrowUp', 'ArrowDown']), s = rnd() < 0.5; key('ballsRho', k, s); what = 'second sphere ' + k + (s ? ' on the slider' : ' in the box'); }
  else if (kind < 0.93) { const k = pick(['ArrowUp', 'ArrowDown']); key('ballsSize', k, false); what = 'size ' + k + ' in the box'; }
  else if (kind < 0.99) { const v = pick(DEPTHS); type('ballsDepth', String(v)); what = 'depth typed ' + v; wantD = Math.min(1000, Math.max(1, Math.round(v))); }
  else { document.querySelector('#ballsReset button').click(); what = 'Reset this section'; wantP = 55.56; wantR = 100; wantD = 16; }
  moves++;
  const p = +$('ballsSizeNum').value, r = +$('ballsRhoNum').value, d = +$('ballsDepthNum').value, bt = S.k.bt, rho = S.k.brho, w = warn();
  hist.push(what); if (hist.length > 6) hist.shift();
  const at = ' [after: ' + hist.join(' / ') + '; now size ' + p + ', second sphere ' + r + ', depth ' + d + ', t ' + bt + ', rho ' + rho + ']';
  const trueP = 100 / (2 * bt - 1);
  // 1. the state is one the brief allows
  if (!(rho === 1 || (rho >= 0.02 - 1e-12 && rho <= 0.5 + 1e-12))) tell('rho not allowed', at);
  if (!(trueP * rho <= 100 * (1 + 1e-7))) tell('the two spheres cut into each other (p rho > 100)', at);
  if (!(bt >= (1 + rho) / 2 - 1e-12)) tell('t below (1 + rho) / 2', at);
  if (!(Number.isInteger(S.k.bit) && S.k.bit >= 1 && S.k.bit <= 1000)) tell('depth not a whole number 1..1000', at);
  // 2. the boxes show the state, inside their ends
  if (Math.abs(p - +trueP.toFixed(2)) > 1e-9) tell('size box is not the state', at);
  if (Math.abs(r - +(100 * rho).toFixed(2)) > 1e-9) tell('second-sphere box is not the state', at);
  if (d !== S.k.bit) tell('depth box is not the state', at);
  if (!(p >= 1 && p <= 2000)) tell('size outside 1..2000', at);
  if (!((r >= 2 && r <= 50) || r === 100)) tell('second sphere outside 2..50 or 100', at);
  // 3. the dial that was moved wins
  if (wantP !== null && Math.abs(p - wantP) > 0.051 && !(Math.abs(wantP - 55.5556) < 0.06 && p === 55.56)) tell('the size dial did not get its value (wanted ' + wantP + ')', at);
  if (wantR !== null && Math.abs(r - wantR) > 0.0051) tell('the second-sphere dial did not get its value (wanted ' + wantR + ')', at);
  if (wantD !== null && d !== wantD) tell('the depth dial did not get its value (wanted ' + wantD + ')', at);
  // 4. the other dial moves only when it has to (the letter of 1.2 point 4), counted apart: not an error by itself
  if (wantP !== null && what !== 'Reset this section' && Math.abs(r - before.r) > 0.0051) { gaveRho++; if (!(wantP * before.r / 100 > 100)) count['second sphere moved although size x second sphere was not over 100 (the builder\'s "follows")'] = (count['second sphere moved although size x second sphere was not over 100 (the builder\'s "follows")'] || 0) + 1;
    else if (Math.abs(r - +(100 * Math.max(0.02, Math.min(0.5, 50 / wantP))).toFixed(2)) > 0.0051) tell('second sphere gave way to something other than min(50, 5000 / p)', at); }
  if (wantP !== null && what !== 'Reset this section' && Math.abs(r - before.r) <= 0.0051 && wantP * before.r / 100 > 100 * (1 + 1e-9)) tell('second sphere did not give way', at);
  if (wantR !== null && what !== 'Reset this section' && Math.abs(p - before.p) > 0.0051) { gaveSize++;
    if (!(before.p * wantR / 100 > 100)) tell('size moved although size x second sphere was not over 100', at);
    else if (Math.abs(p - +(5000 / wantR).toFixed(2)) > 0.0051) tell('size gave way to something other than 5000 / second sphere', at); }
  if (wantR !== null && what !== 'Reset this section' && Math.abs(p - before.p) <= 0.0051 && before.p * wantR / 100 > 100 * (1 + 1e-6)) tell('size did not give way', at);
  // 5. the sentences fit the state
  const touch = rho === 1 ? !(bt > 1) : !(2 * bt - 1 - rho > 1e-9);
  if (touch) touching++; if (trueP > 100) past100++;
  if (touch !== /the chain never ends/.test(w)) tell('"the chain never ends" sentence ' + (touch ? 'missing' : 'shown without touching'), at + ' "' + w + '"');
  if (touch && !w.startsWith('At ' + (rho === 1 ? '100' : String(p)) + ' the chain')) tell('the touching sentence names another number', at + ' "' + w.slice(0, 40) + '"');
  if ((rho < 1 && trueP > 100 * (1 + 1e-9)) !== /Past 100 the second sphere has to be smaller/.test(w)) tell('"Past 100" sentence wrong way round', at + ' "' + w + '"');
  if (rho < 1 && !w.includes(' ' + r + ' % of the first')) tell('the sentence does not give the second sphere as the box shows it', at + ' "' + w + '"');
  if (rho === 1 && /second sphere/.test(w)) tell('a sentence about the second sphere with two equal spheres', at + ' "' + w + '"');
  if ((S.k.bit < 5) !== /so few rounds/.test(w)) tell('"so few rounds" sentence wrong way round', at + ' "' + w + '"');
  if (/NaN|undefined|Infinity/.test(w + $('ballsSizeNum').value + $('ballsRhoNum').value + $('status').textContent)) tell('NaN, undefined or Infinity in a text', at + ' "' + w + '" status "' + $('status').textContent + '"');
  if (i % 250 === 249) { await sleep(60); if (L.R.failed) tell('a program failed', String(L.R.failed)); }
}
document.querySelector('#ballsReset button').click(); await sleep(300);
for (let i = 0; i < 3000 && !L.idle(); i++) await sleep(20);
return JSON.stringify({ moves, timesTheSecondSphereMovedWithTheSize: gaveRho, timesTheSizeMovedWithTheSecondSphere: gaveSize, statesTouching: touching, statesPast100: past100, kindsOfTrouble: count, firstCases: bad,
  afterReset: { size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, t: S.k.bt, rho: S.k.brho, warn: warn(), failed: String(L.R.failed || '') } });
