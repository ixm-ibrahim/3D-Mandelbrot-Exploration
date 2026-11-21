"""Round 22, entry, second pass: one test step for each defect the checker found (out/r22/entrycheck/NOTES.md, section 6).
smoke.py puts STEPS into the smoke list (after the steps of the two entries, before the last step).
  python out/r22/entry/second.py        runs these steps alone -> second.log"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

HEAD = run.HEAD + """
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const cardText = () => $('card').innerText.replace(/\\s+/g, ' ');
const cardIdle = async () => { await settle(); await sleep(500); for (let i = 0; i < 600 && ($('card').getAttribute('aria-busy') || !L.idle()); i++) await sleep(20); if ($('card').getAttribute('aria-busy')) fail('the card never finished'); };
const cell = id => ($('s-' + id) ? $('s-' + id).textContent : '').replace(/\\s+/g, ' ');
const RABBIT = [-0.122561, 0.744862, 0];
"""

STEPS = [
    # defect 1 (major): the card of Pulled plane after "Jump to a point", after a saved point; defect 5: the Mandelbrot
    # card and the hidden Julia constant; defect 7b: no re-measuring for Along once, no heap of remembered measurements
    dict(js=HEAD + """
$('mode-j').click(); await sleep(150);
$('ap-pulledplane').click(); await sleep(250); S.n = 2; S.eq = 'z^n + c'; S.z0 = '0'; S.c = [-1, 0, 0]; go(); await cardIdle();
const atMinus1 = cardText(), out = ['card at c = -1: ' + cell('round').slice(0, 14) + ' | ' + cell('wrap')];
// "Jump to a point": the rabbit, through the menu itself, and nothing else is touched afterwards
const sel = $('juliaPreset'), opt = [...sel.options].find(o => /abbit/.test(o.textContent));
if (!opt) fail('no rabbit in the list "Jump to a point"');
sel.value = opt.value; sel.dispatchEvent(new Event('change', { bubbles: true })); await cardIdle();
if (Math.abs(S.c[1] - 0.744862) > 1e-3) fail('the jump did not take: ' + S.c);
const afterMenu = cardText();
go(); await cardIdle();
const afterRefresh = cardText();
if (afterMenu === atMinus1) fail('the card did not follow "Jump to a point"');
if (afterMenu !== afterRefresh) fail('the card after "Jump to a point" is not the card of that c: ' + afterMenu + ' /// ' + afterRefresh);
out.push('after the jump to the rabbit (same after a refresh): ' + cell('round').slice(0, 14) + ' | ' + cell('wrap'));
// a point that is in no list goes the same way (applyJuliaPreset is what a saved point calls)
L.applyJuliaPreset({ name: 'second pass', c: [-1, 0, 0] }); await cardIdle();
if (cardText() !== atMinus1) fail('back at c = -1 through applyJuliaPreset the card is not the first card');
// the Mandelbrot view: the card must not depend on the Julia constant, which that view hides
$('mode-m').click(); await sleep(200); await cardIdle();
const m1 = cardText();
S.c = RABBIT.slice(); L.touch(); await cardIdle();
const m2 = cardText();
go(); await cardIdle();
if (m1 !== m2 || m2 !== cardText()) fail('the Mandelbrot card of Pulled plane depends on the hidden Julia constant');
if (m1 === atMinus1) fail('the Mandelbrot card should be measured with c at the point itself, not with c = -1');
out.push('Mandelbrot card, the same for both hidden c: ' + cell('round').slice(0, 14) + ' | ' + cell('wrap') + ' | ' + cell('slice').slice(0, 60));
// the step figure follows as well: its rule is the card's rule
const f1 = L.MATH.pulledplane([0.3, 0.4, 0.5], 2, S.param.pulledplane, [0.3, 0.4, 0.5]).map(x => x.toFixed(6)).join();
// remembered measurements: a c dial that sweeps leaves one for Pulled plane, none new for Along once
$('mode-j').click(); await sleep(200); S.c = [-1, 0, 0]; go(); await cardIdle();
for (const v of ['0.1', '0.2', '0.3', '0.4']) { type('cy', v); await cardIdle(); }
const keys = [...L.cardRun.cache.keys()].filter(k => k.includes(' c='));
if (keys.length !== 1 || !keys[0].startsWith('pulledplane ')) fail('remembered measurements that depend on c: ' + JSON.stringify(keys));
type('cy', '0'); await cardIdle();
if (cardText() !== atMinus1) fail('back at c = -1 through the dial the card is not the first card');
$('ap-alongonce').click(); await sleep(250); go(); await cardIdle();
const n0 = L.cardRun.cache.size, a0 = cardText();
type('cy', '0.3'); await cardIdle();
const n1 = L.cardRun.cache.size, a1 = cardText();
type('cy', '0'); await cardIdle();
if (n1 !== n0 || a1 !== a0) fail('the card of Along once was measured again for another c: ' + n0 + ' -> ' + n1);
out.push('c dial swept: 1 remembered measurement for Pulled plane, Along once not measured again (' + n0 + ' -> ' + n1 + ')');
// the dial's name
$('ap-pulledplane').click(); await sleep(250);
const page = $('pd-pulledplane') ? $('pd-pulledplane').textContent : '';
if (!page.includes('How little a thing near the page turns it') || /Ease of a pull/.test(document.body.textContent)) fail('the second dial of Pulled plane is not named in plain words: ' + page.slice(0, 300));
S.c = [-1, 0, 0]; go(); await settle();
return out.join('; ');
""", wait='done', timeout=1500),

    # defect 4: the Learn tab follows the entry's own orbit after "Next step"; defect 3: the Stretch sentences
    dict(js=HEAD + """
const own = (id, z0, c, steps, q) => { const R = L.CARRY[id]; let st = R.start(q), z = z0.slice(); const o = [z.slice()]; for (let k = 0; k < steps; k++) { st = R.step(st, z, c, q); const w = R.pw(st, z, 2); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; o.push(z.slice()); } return o; };
const plain = (id, z0, c, steps, q) => { let z = z0.slice(); const o = [z.slice()]; for (let k = 0; k < steps; k++) { const w = L.MATH[id](z, 2, q); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; o.push(z.slice()); } return o; };
const far = (a, b) => Math.max(...a.map((v, i) => Math.hypot(v[0] - b[i][0], v[1] - b[i][1], v[2] - b[i][2])));
const Z0 = [0.6, 0.3, 0.4], C = [-0.3, 0.2, 0.1], out = [], says = {};
for (const id of ['alongonce', 'pulledplane', 'turnalong', 'mercator', 'lathe']) {
  $('mode-j').click(); await sleep(200); $('ap-' + id).click(); await sleep(250); S.n = 2; S.eq = 'z^n + c'; S.abs = [0, 0, 0]; S.flip = [0, 0]; go(); await sleep(100);
  $('mode-l').click(); await sleep(400);
  if (!document.body.classList.contains('is-learn')) fail('Learn did not switch on');
  $('learnSpace3').click(); await sleep(300);
  L.learn.set({ z: Z0, c: C });
  says[id] = L.learn.cache.say.slice();
  let taken = 0;
  for (let k = 0; k < 4; k++) { $('learnNext').click(); await sleep(120); taken = L.learn.k; }
  const st = L.learn.state(), want = (L.CARRY[id] ? own : plain)(id, Z0, C, st.orbit.length - 1, S.param[id]);
  const d = far(st.orbit, want);
  if (st.orbit.length < 3) fail(id + ': Next step did not go on: ' + st.orbit.length);
  if (!(d < 1e-9)) fail(id + ': after ' + (st.orbit.length - 1) + ' steps the Learn tab is ' + d.toExponential(2) + ' away from the entry\\u2019s own orbit: ' + JSON.stringify(st.orbit[2].map(x => +x.toFixed(3))) + ' against ' + JSON.stringify(want[2].map(x => +x.toFixed(3))));
  if (L.learn.cache.fault || /undefined|NaN/.test(L.learn.cache.say.join(' ') + st.note)) fail(id + ': Learn says ' + L.learn.cache.fault + ' ' + L.learn.cache.say.join(' '));
  if (L.CARRY[id] && !/after \\u201cNext step\\u201d they are the moves of the squaring the orbit has come to/.test(st.note)) fail(id + ': the Learn note does not say what Next step shows: ' + st.note);
  // the moves on show end where the orbit goes next
  const end = st.end, nxt = (L.CARRY[id] ? own : plain)(id, Z0, C, st.orbit.length, S.param[id]).pop();
  if (!(Math.hypot(end[0] - nxt[0], end[1] - nxt[1], end[2] - nxt[2]) < 1e-9)) fail(id + ': the moves of step ' + (taken + 1) + ' do not end where the orbit goes');
  out.push(id + ': ' + (st.orbit.length - 1) + ' steps, second point ' + st.orbit[2].map(x => x.toFixed(2)).join(', ') + ', off the own orbit by ' + d.toExponential(1));
  $('learnAgain').click(); await sleep(150);
  // with |x| |y| |z| ticked the carried thing is changed by the point as the modifiers leave it
  if (L.CARRY[id]) {
    $('mode-j').click(); await sleep(200); S.abs = [1, 1, 1]; go(); await sleep(100); $('mode-l').click(); await sleep(400); $('learnSpace3').click(); await sleep(200);
    L.learn.set({ z: [0.5, -0.3, -0.4], c: [-0.3, -0.2, -0.1] });
    for (let k = 0; k < 3; k++) { $('learnNext').click(); await sleep(120); }
    const s2 = L.learn.state(), R = L.CARRY[id], q = S.param[id];
    let st2 = R.start(q), z = [0.5, -0.3, -0.4]; const o2 = [z.slice()];
    for (let k = 0; k < s2.orbit.length - 1; k++) { const m = z.map(Math.abs); st2 = R.step(st2, m, [-0.3, -0.2, -0.1], q); const w = R.pw(st2, m, 2); z = [w[0] - 0.3, w[1] - 0.2, w[2] - 0.1]; o2.push(z.slice()); }
    const d2 = far(s2.orbit, o2);
    if (!(d2 < 1e-9) || s2.orbit.length < 3) fail(id + ' with |x| |y| |z|: Learn is ' + d2.toExponential(2) + ' off the own orbit after ' + (s2.orbit.length - 1) + ' steps');
    out.push(id + ' with |x||y||z|: ' + (s2.orbit.length - 1) + ' steps, off by ' + d2.toExponential(1));
    $('learnAgain').click(); await sleep(150); $('mode-j').click(); await sleep(200); S.abs = [0, 0, 0]; go(); await sleep(100);
  }
}
// the Stretch sentences: the contrast with doubling, with a number that tells the two apart
const st = id => says[id].find(s => /length/.test(s) && /squared|multiplied by itself/.test(s)) || '';
for (const id of ['alongonce', 'pulledplane', 'turnalong']) if (!/multiplied by itself, not doubled: 0\\.78 becomes 0\\.61, and 3 would become 9, not 6\\./.test(st(id))) fail(id + ': Stretch says: ' + says[id].join(' / '));
for (const id of ['mercator', 'lathe']) if (!/is squared: 0\\.61\\. Squared means multiplied by itself, not doubled: 3 would become 9, not 6\\. A length under 1 gets shorter\\./.test(st(id))) fail(id + ': Stretch says: ' + says[id].join(' / '));
if (/2 would become 4/.test(JSON.stringify(says))) fail('the old example is still there');
out.push('Stretch (turnalong): ' + st('turnalong')); out.push('Stretch (mercator): ' + st('mercator'));
// power 3 and a power that is not whole
const P3 = L.learnPlan({ space: 3, id: 'mercator', params: S.param.mercator, n: 3, c: C }), r3 = P3.run(Z0), i3 = P3.moves.findIndex(m => m.name === 'Stretch');
const s3 = P3.moves[i3].say(r3[i3], r3[i3 + 1]);
if (!/Cubed means multiplied by itself twice, not tripled: 3 would become 27, not 9\\./.test(s3)) fail('power 3: ' + s3);
const P25 = L.learnPlan({ space: 3, id: 'mercator', params: S.param.mercator, n: 2.5, c: C }), r25 = P25.run(Z0), i25 = P25.moves.findIndex(m => m.name === 'Stretch');
const s25 = P25.moves[i25].say(r25[i25], r25[i25 + 1]);
if (/not doubled|would become/.test(s25)) fail('power 2.5 should keep the old sentence: ' + s25);
out.push('power 3: ' + s3);
$('mode-j').click(); await sleep(300);
return out.join('; ');
""", wait='done', timeout=1500),

    # defect 2 (major): a c out of the flat plane. The texts say what the picture shows; the pictures are kept.
    dict(js=HEAD + """
const out = [];
for (const id of ['alongonce', 'pulledplane']) {
  $('mode-j').click(); await sleep(150); $('ap-' + id).click(); await sleep(250);
  const a = L.APPROACHES[S.approach], note = a.params.find(p => p.type === 'note').text, about = a.about;
  for (const w of ['which all lie in the flat plane', 'For a c out of the flat plane (the dial \\u201cc along z\\u201d away from 0) that does not hold', 'the picture can show what is not there', 'A power written into the start value'])
    if (!note.includes(w)) fail(id + ': the note does not say: ' + w);
  if (!about.includes('The picture does not show that emptiness')) fail(id + ': the About text does not say what the picture shows for a c out of the flat plane');
  const box = $('apAbout'); if (box.hidden) { $('apAboutBtn').click(); await sleep(150); }
  if (!box.textContent.includes('the picture can show what is not there') || !box.textContent.includes('The picture does not show that emptiness')) fail(id + ': "About this approach" does not show the new sentences');
  $('apAboutBtn').click(); await sleep(100);
  // the rabbit's c turned 10 degrees about the x-axis: the picture is not empty (that is the fault the texts name)
  const t = 10 * Math.PI / 180;
  S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 40; S.c = [RABBIT[0], RABBIT[1] * Math.cos(t), RABBIT[1] * Math.sin(t)]; S.flat = false; S.cutOn = false; L.resetCam(); go(); await settle();
  const g = grid();
  out.push(id + ', rabbit c turned 10 degrees: ' + g[0] + ' of 165 probes stop');
  S.c = [-1, 0, 0.3]; go(); await settle();
  const g2 = grid();
  out.push(id + ', c = (-1, 0, 0.3): ' + g2[0] + ' of 165 probes stop');
  if (g[0] + g2[0] === 0) fail(id + ': the pictures for a c out of the flat plane are empty, so the new sentences are wrong');
}
// the "One smooth formula" cell of Pulled plane quotes its measurement only where it was made (power 2, first dial 0.05)
const A = L.APPROACHES.find(x => x.id === 'pulledplane'), def = { hold: 0.05, ease: 0.7, cpull: 16 };
const sm = (p, n) => A.smooth(p, n)[1];
if (!/measured with c = \\u22121 at x = \\u22120\\.8/.test(sm(def, 2)) || !sm(def, 2).includes('z = \\u00b10.22')) fail('power 2: ' + sm(def, 2));
for (const [p, n] of [[def, 3], [def, 2.5], [def, -2], [{ ...def, hold: 0.2 }, 2]]) if (/measured with/.test(sm(p, n)) || !/read off the rule\\)/.test(sm(p, n))) fail('the measurement is quoted where it was not made: ' + sm(p, n));
if (!sm({ ...def, hold: 0.2 }, 2).includes('z = \\u00b10.45')) fail('the line does not follow the first dial');
if (!/With the first dial at 0/.test(sm({ ...def, hold: 0 }, 2)) || /undefined|NaN/.test(sm({ ...def, hold: 0 }, 2))) fail('first dial at 0: ' + sm({ ...def, hold: 0 }, 2));
out.push('smooth cell: measurement quoted at power 2 with the first dial at 0.05 only');
S.c = [-1, 0, 0]; go(); await settle();
return out.join('; ');
""", wait='done', timeout=900, shot='out/r22/entry/smoke/r22-second-offplane-last.png'),
]

if __name__ == '__main__':
    code, text, vals = run.shot(run.PAGE, [run.UP] + STEPS, 'second-steps', '1400x950')
    run.write('second.log', text + 'exit %d\n' % code)
    print(text[-7000:]); print('exit', code)
    sys.exit(code)
