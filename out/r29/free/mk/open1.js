// Round 29, builder, test 1: the page opens, the row gives Balls on balls with its defaults, all three programs
// compile, the dials are free of each other, and the sentences read as docs/ROUND29.md fixes them.
const out = [];
out.push('as the page opens: mode ' + S.mode + ', brho ' + S.k.brho + ', status "' + $('status').textContent + '"');
$('ap-balls').click(); await settle();
const sig = () => String(L.R.sig).replace(/\n/g, '/');
const say = what => out.push(what + ': t ' + S.k.bt + ', rho ' + S.k.brho + ', size shows ' + $('ballsSizeNum').value + ', second sphere shows ' + $('ballsRhoNum').value + ', depth ' + S.k.bit +
  ', program ' + sig() + ', bound ' + S.view.bound + ', status "' + $('status').textContent + '", warn "' + warn() + '"');
say('after the row');
const dial = id => { const r = $(id), n = $(id + 'Num'); return id + ': slider ' + r.min + ' to ' + r.max + ' step ' + r.step + ', typed ' + n.getAttribute('aria-valuemin') + ' to ' + n.getAttribute('aria-valuemax') + ', shows ' + n.value + ', title "' + n.title + '"'; };
for (const id of ['ballsSize', 'ballsRho', 'ballsDepth']) out.push(dial(id));
out.push('help: ' + [...document.querySelectorAll('#ballsDials .dial-help')].map(e => e.textContent).join(' || '));
const type = async (id, text) => { const n = $(id + 'Num'); n.focus(); n.value = text; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); n.blur(); await settle(); };
await type('ballsSize', '150'); say('typed size 150');
out.push('  reach ' + L.ballsReach() + ', inside at (1.2, 0, 0): ' + L.ballsInside(1.2, 0, 0) + ', estimate at (0, 1.5, 0): ' + L.ballsEstimate(0, 1.5, 0));
$('ballsFrame').click(); await settle(); say('Frame it');
S.flat = true; go(); await settle(); say('the 2D view'); $('ballsFrame').click(); await settle(); say('the 2D view, Frame it');
S.flat = false; go(); await settle();
await type('ballsRho', '33.33'); say('typed second sphere 33.33');
await type('ballsSize', '120'); say('typed size 120');
await type('ballsRho', '100'); say('typed second sphere 100'); $('ballsFrame').click(); await settle(); say('Frame it');
await type('ballsRho', '62.5'); say('typed second sphere 62.5');
await type('ballsSize', '80'); say('typed size 80');
await type('ballsRho', '75'); say('typed second sphere 75');
await type('ballsSize', '133.33'); say('typed size 133.33');
await type('ballsRho', '50'); say('typed second sphere 50');
await type('ballsSize', '60'); say('typed size 60');
await type('ballsSize', '400'); await type('ballsRho', '100'); say('typed 400 and 100');
S.flat = true; go(); await settle(); say('400 / 100 in the 2D view');
S.flat = false; go(); await settle();
await type('ballsSize', '5000'); say('typed size 5000'); await type('ballsSize', '0.2'); say('typed size 0.2');
await type('ballsRho', '1'); say('typed second sphere 1'); await type('ballsRho', '250'); say('typed second sphere 250');
await type('ballsDepth', '3'); say('typed depth 3');
document.querySelector('#ballsReset button').click(); await settle(); say('Reset this section');
out.push('t exactly 1.4: ' + (S.k.bt === 1.4) + ', rho exactly 1: ' + (S.k.brho === 1));
return JSON.stringify(out, null, 1);
