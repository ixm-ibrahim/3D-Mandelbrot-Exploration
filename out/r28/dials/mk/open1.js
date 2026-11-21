// Round 28, builder, test 1: the page opens, the row gives Balls on balls with its defaults, the two programs
// compile, and the dials are there with their new ends. Returns a list of plain lines.
const out = [];
out.push('as the page opens: mode ' + S.mode + ', brho ' + S.k.brho + ', status "' + $('status').textContent + '"');
$('ap-balls').click(); await settle();
out.push('after the row: mode ' + S.mode + ', group ' + S.k.group + ', t ' + S.k.bt + ', rho ' + S.k.brho + ', grid ' + S.k.bgrid + ', depth ' + S.k.bit + ', status "' + $('status').textContent + '", warn "' + warn() + '"');
const dial = id => { const r = $(id), n = $(id + 'Num'); return id + ': slider ' + r.min + ' to ' + r.max + ' step ' + r.step + ', typed ' + n.getAttribute('aria-valuemin') + ' to ' + n.getAttribute('aria-valuemax') + ', shows ' + n.value; };
for (const id of ['ballsSize', 'ballsRho', 'ballsDepth']) out.push(dial(id));
out.push('labels: ' + [...document.querySelectorAll('#ballsDials .label')].map(e => e.textContent).join(' | '));
out.push('help: ' + [...document.querySelectorAll('#ballsDials .dial-help')].map(e => e.textContent).join(' || '));
out.push('programs in the cache: ' + [...L.R.sig ? [L.R.sig.replace(/\n/g, '/')] : []].join(', '));
// the size past 100 through the state setters the dial uses: type 150 into the box
const type = async (id, text) => { const n = $(id + 'Num'); n.focus(); n.value = text; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); await settle(); };
await type('ballsSize', '150');
out.push('typed 150: t ' + S.k.bt + ', rho ' + S.k.brho + ', size shows ' + $('ballsSizeNum').value + ', second sphere shows ' + $('ballsRhoNum').value + ', sig ' + L.R.sig.replace(/\n/g, '/') + ', status "' + $('status').textContent + '", warn "' + warn() + '"');
out.push('reach ' + L.ballsReach() + ', inside at (1.2, 0, 0): ' + L.ballsInside(1.2, 0, 0) + ', estimate at (0, 1.5, 0): ' + L.ballsEstimate(0, 1.5, 0));
await type('ballsSize', '300');
out.push('typed 300: t ' + S.k.bt + ', rho ' + S.k.brho + ', size shows ' + $('ballsSizeNum').value + ', second sphere shows ' + $('ballsRhoNum').value + ', status "' + $('status').textContent + '", warn "' + warn() + '"');
return JSON.stringify(out);
