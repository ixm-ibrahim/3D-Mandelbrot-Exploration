// Round 16, entry: does the Learn tab's step plan work with the two new entries selected? (no exception, the chain ends where MATH ends)
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const out = [];
for (const id of ['turnaway', 'turnalong']) {
  $('ap-' + id).click(); await sleep(300);
  try {
    const v = [0.3, 0.4, 0.5], plan = L.learnPlan ? L.learnPlan({ id, v, n: 2, space: 3 }) : null;
    const end = plan && (plan.end || (plan.steps && plan.steps.length && plan.steps[plan.steps.length - 1].to));
    out.push(id + ': learnPlan ' + (plan ? 'gave ' + (plan.steps ? plan.steps.length + ' steps' : Object.keys(plan).join(',')) + ', end ' + JSON.stringify(end) + ', MATH ' + JSON.stringify(L.MATH[id](v, 2, {})) : 'is not on this page'));
  } catch (e) { out.push(id + ': learnPlan threw ' + e.message); }
}
$('ap-turnaway').click(); await sleep(200);
return out.join('\n');
