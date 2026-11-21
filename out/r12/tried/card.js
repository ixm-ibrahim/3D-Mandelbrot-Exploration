const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
$('ap-__AP__').click(); await sleep(300);
__EXTRA__
await sleep(300);
for (let i = 0; i < 300 && !L.idle(); i++) await sleep(100);
const id = L.APPROACHES[S.approach].id, rule = $('ap-' + id).closest('.rule'), note = rule.querySelector('.sec-body .note');
const lines = ['__NAME__',
  '  name and tag: ' + rule.querySelector('.rule-head').textContent,
  '  formula: ' + $('f-' + id).textContent,
  '  first note: ' + (note ? note.textContent : '(none)'),
  '  first control in the list is the note: ' + (rule.querySelector('.sec-body').firstElementChild === note),
  '  controls: ' + [...rule.querySelectorAll('.sec-body label')].map(e => e.textContent).join(' | '),
  '  card: ' + $('card').innerText.split('\n').filter(Boolean).join(' / ')];
return lines.join('\n');
