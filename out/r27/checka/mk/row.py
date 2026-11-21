"""Round 27, checker A, bullet 7: the row in the Approach list, and leaving it again. The state before and after
(S.mode, the group choice, S.approach); nothing added to APPROACHES. Also what the frozen page does when an approach
is chosen in the Kleinian view (to compare "behaves as it does today").
  python row.py  -> ../logs/row.json, ../logs/row.txt, ../shots/row-*.png
"""
import json, os, sys
import drive as D

ST = """
const st = () => ({ mode: S.mode, group: S.k.group === undefined ? null : S.k.group, approach: S.approach, id: L.APPROACHES[S.approach].id, flat: S.flat, learn: !!S.learn,
  modeRadio: ['m', 'j', 'k'].find(m => $('mode-' + m).checked) || null, groupRadio: $('kleinGroup1') ? ($('kleinGroup1').checked ? 1 : 0) : null,
  menuName: $('apMenuName').textContent, yaw: +L.cam.yaw.toFixed(3), pitch: +L.cam.pitch.toFixed(3), dist: +L.cam.dist.toFixed(3),
  apSectionShown: $('secApproach').getBoundingClientRect().height > 0 && !$('secApproach').hidden, kleinPanelShown: $('kleinPanel') ? $('kleinPanel').getBoundingClientRect().height > 0 : null,
  bt: S.k.bt, bgrid: S.k.bgrid, bit: S.k.bit });
const hits = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) if (L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11)) n++; return n; };
"""
NEW = D.HEAD + ST + """
const out = {};
out.approaches = { n: L.APPROACHES.length, ids: L.APPROACHES.map(a => a.id), hasBalls: L.APPROACHES.some(a => /ball/i.test(a.id + ' ' + a.name)) };
const row = $('ap-balls');
out.row = { there: !!row, tag: row.tagName, insideRules: !!row.closest('#rules'), insideApPop: !!row.closest('#apPop'), radiosInRules: $('rules').querySelectorAll('input[type=radio]').length,
  rowsInRules: $('rules').querySelectorAll('.rule').length, heading: $('apgh-cousin').textContent, name: row.querySelector('.name').textContent, label: row.querySelector('.cousin-tag').textContent, title: row.title };
out.s0 = st();
// open the menu as a user does, look that the row is on show, one click on it
$('apMenuBtn').click(); await sleep(300);
const rb = row.getBoundingClientRect(), pb = $('apPop').getBoundingClientRect();
out.rowShown = { w: Math.round(rb.width), h: Math.round(rb.height), top: Math.round(rb.top), bottom: Math.round(rb.bottom), popTop: Math.round(pb.top), popBottom: Math.round(pb.bottom), winH: innerHeight,
  expanded: $('apMenuBtn').getAttribute('aria-expanded') };
return JSON.stringify(out);
"""
CLICK = D.HEAD + ST + """
$('ap-balls').click(); await settle();
return JSON.stringify({ s1: st(), hits: hits(), menuOpen: $('apMenuBtn').getAttribute('aria-expanded'), trouble: L.kleinTrouble ? L.kleinTrouble() : null, swallowed: L.kleinSwallowed ? L.kleinSwallowed() : null,
  note: $('ballsPart').innerText.slice(0, 400), oldHidden: $('kleinOld').hidden, ballsHidden: $('ballsPart').hidden, status: $('status').textContent });
"""
LEAVE = D.HEAD + ST + """
const out = {};
// leave by choosing a real approach (the row was chosen from the Mandelbrot view)
$('apMenuBtn').click(); await sleep(200); $('ap-lathe').click(); await settle();
out.s2_leave_by_approach = st(); out.s2_hits = hits();
// back through the Show button: the Kleinian view brings the group chosen last
$('mode-k').click(); await settle(); out.s3_back_by_show = st();
// leave through a Show button
$('mode-j').click(); await settle(); out.s4_leave_by_show = st();
// from the Julia view: row, then another approach
$('ap-balls').click(); await settle(); out.s5_row_from_julia = st();
$('ap-quat4').click(); await settle(); out.s6_leave_to = st();
// reached another way (Show: Kleinian, then the group choice), then an approach
$('mode-m').click(); await settle(); $('mode-k').click(); await settle();
out.s7_show_kleinian = st();
$('kleinGroup0').click(); await settle(); out.s8_first_group = st(); out.s8_hits = hits();
$('ap-fold').click(); await settle(); out.s9_approach_in_first_group = st();
$('mode-k').click(); await settle(); $('kleinGroup1').click(); await settle(); out.s10_group_choice = st();
$('ap-tilt').click(); await settle(); out.s11_leave_reached_another_way = st();
// Learn: the row chosen under Learn
$('mode-l').click(); await sleep(500); out.s12_learn = st();
$('ap-balls').click(); await settle(); out.s13_row_under_learn = st();
// Reset everything
$('resetAll').click(); await settle(); out.s14_reset_everything = st();
out.approachesAfter = { n: L.APPROACHES.length, ids: L.APPROACHES.map(a => a.id).join(' ') };
return JSON.stringify(out);
"""
OLD = D.HEAD + """
const st = () => ({ mode: S.mode, approach: S.approach, id: L.APPROACHES[S.approach].id, flat: S.flat, modeRadio: ['m', 'j', 'k'].find(m => $('mode-' + m).checked) || null,
  menuName: $('apMenuName').textContent, yaw: +L.cam.yaw.toFixed(3), pitch: +L.cam.pitch.toFixed(3), dist: +L.cam.dist.toFixed(3),
  apSectionShown: $('secApproach').getBoundingClientRect().height > 0 && !$('secApproach').hidden });
const out = { approaches: { n: L.APPROACHES.length, ids: L.APPROACHES.map(a => a.id) } };
out.s0 = st();
$('mode-k').click(); await settle(); out.s7_show_kleinian = st();
$('ap-fold').click(); await settle(); out.s9_approach_in_kleinian = st();
$('mode-j').click(); await settle(); out.sj = st();
$('mode-k').click(); await settle(); $('ap-tilt').click(); await settle(); out.s11_approach_in_kleinian_from_julia = st();
return JSON.stringify(out);
"""
code, vals, text = D.run(D.PAGE, [D.UP, {'js': NEW, 'shot': 'out/r27/checka/shots/row-menu-open.png'}, {'js': CLICK, 'wait': 'done', 'shot': 'out/r27/checka/shots/row-after-click.png'}, {'js': LEAVE, 'wait': 'done'}], 'row-new')
code2, vals2, text2 = D.run(D.BASE, [D.UP, {'js': OLD, 'wait': 'done'}], 'row-old')
res = dict(new=vals[1:], old=vals2[1:], exit_new=code, exit_old=code2, problems_new=text[text.find('PAGE PROBLEMS'):][:1500] if 'PAGE PROBLEMS' in text else 'no console errors',
           problems_old=text2[text2.find('PAGE PROBLEMS'):][:1500] if 'PAGE PROBLEMS' in text2 else 'no console errors')
with open(os.path.join(D.LOGS, 'row.json'), 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False)[:9000])
if code != 0:
    print(text[-1500:])
