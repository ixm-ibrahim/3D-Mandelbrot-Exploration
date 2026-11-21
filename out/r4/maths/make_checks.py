"""Write out/r4/maths/checks.json: numbers, texts and controls of the maths module, checked on the built page.

  python out/r4/maths/make_checks.py
  python tools/shot.py --url dist/r4-maths.html --actions out/r4/maths/checks.json
Each step throws on a wrong state, so a failure shows as a page error with the reason.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = r"""const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const A = L.APPROACHES.find(a => a.id === 'mercator'), M = L.MATH.mercator;
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
"""
steps = []


def step(js, shot=None, clip=None, wait='done', timeout=300):
    a = {'js': PRE + js.strip()}
    if wait:
        a['wait'] = wait
        a['timeout'] = timeout
    if shot:
        a['shot'] = 'out/r4/maths/' + shot
        if clip:
            a['clip'] = clip
    steps.append(a)


# 1 where the folded rule jumps: walk round the x-axis and note every angle where the result moves by a jump
step(r"""
L.R.warmOn = false; S.q.aa = 3; L.touch();
const out = [];
for (const k of [1, 2, 3, 4, 5, 8]) {
  const jumps = [], N = 7200, at = t => M([0.3, 0.8 * Math.cos(t), 0.8 * Math.sin(t)], 2, { planes: k });
  // samples sit a quarter of a step off the round angles, so a jump at 45 or 90 degrees falls between two of them
  for (let i = 0; i < N; i++) {
    const t = -Math.PI + 2 * Math.PI * (i + 0.25) / N, h = 2 * Math.PI / N, d = dist(at(t), at(t + h));
    if (d > 0.05) jumps.push(Math.round((t + h / 2) * 180 / Math.PI));
  }
  out.push(k + ' plane(s): jumps at ' + (jumps.length ? [...new Set(jumps)].join(', ') + ' degrees round the x-axis, counted from the y-axis' : 'none'));
  if (k === 1 && jumps.length) fail('the one-plane rule jumps: ' + jumps);
  if (k > 1 && [...new Set(jumps.map(Math.abs))].join() !== '90') fail('with ' + k + ' planes the jumps are not on the plane y = 0: ' + jumps);
}
return out.join(' | ');
""")

# 2 the scorecard measurement for one plane, and the roundness at n = -1 with and without a lift
step(r"""
const m2 = L.measure(v => M(v, 2, { planes: 1 }), 2), m3 = L.measure(v => M(v, 3, { planes: 1 }), 3);
const a = L.measure(v => M(v, -1, { planes: 1 }), -1), b = L.measure(v => M(v, -1, { planes: 1, lift: 0.5 }), -1), c = L.measure(v => M(v, -1, { planes: 2, lift: 0.5 }), -1);
if (!m2.plane || !m3.plane) fail('one plane: the plane z = 0 does not follow z^n');
if (!(a.round > 0.999)) fail('n = -1, no lift: roundness should be 100%');
if (b.round > 0.999) fail('n = -1 with a lift measured as shape-keeping, so the plain note would be right after all');
const note = (q, n) => A.roundNote(q, n);
if (note({ planes: 1, lift: 0.5 }, -1).includes('single sphere inversion')) fail('roundNote still calls a lifted n = -1 a single inversion');
if (!note({ planes: 1, lift: 0 }, -1).includes('single sphere inversion')) fail('roundNote lost the n = -1 sentence');
return 'one plane n=2: plane exact ' + m2.plane + ', roundness ' + m2.round.toFixed(3) + ', wraps ' + m2.sheets.toFixed(2) + ', mirrored share ' + m2.rev.toFixed(3) +
  ' | n=3: plane exact ' + m3.plane + ', wraps ' + m3.sheets.toFixed(2) +
  ' | n=-1 roundness: no lift ' + a.round.toFixed(4) + ', lift 0.5 ' + b.round.toFixed(4) + ', 2 planes lift 0.5 ' + c.round.toFixed(4);
""")

# 3 the texts, as data
step(r"""
const P = A.params, out = [];
out.push('TAG: ' + A.tag); out.push('ABOUT (' + A.about.split(/\s+/).length + ' words): ' + A.about);
for (const s of P) out.push((s.type + ' ' + (s.key || '')).trim() + ': ' + (s.label || s.text) + (s.help ? ' || HELP: ' + s.help : '') + (s.animate ? ' || animate ' + s.animate : '') +
  (s.xmax !== undefined ? ' || wide ' + [s.xmin, s.xmax, s.xlo, s.xhi].join('/') : ''));
for (const q of [{ planes: 1, turn: 0, lift: 0 }, { planes: 2, turn: 0, lift: 0 }, { planes: 1, turn: 0, lift: 0.5 }]) for (const n of [2, 3, 2.5, -1]) {
  out.push(JSON.stringify(q) + ' n=' + n + '\n   formula: ' + A.formula(q, n) + '\n   round: ' + A.roundNote(q, n) + '\n   crush: ' + A.crush(q, n).join(' / ') + '\n   smooth: ' + A.smooth(q, n).join(' / ') + '\n   slice: ' + A.slice(true, q, n));
}
const all = [A.tag, A.about, ...P.map(s => (s.label || '') + ' ' + (s.text || '') + ' ' + (s.help || ''))].join(' ');
if (/[—!]/.test(all)) fail('an em dash or an exclamation mark in the texts');
if (/pulse/i.test(P.find(s => s.key === 'lift').help)) fail('the Lift help still promises a pulse');
if (P.find(s => s.key === 'lift').animate !== 'bounce') fail('Lift should sweep there and back');
if (P.find(s => s.key === 'planes').def !== 1) fail('planes should start at 1');
return out.join('\n');
""", wait=None)

# 4 the panel as the page opens (one plane)
step(r"""
document.querySelectorAll('details.sec').forEach(d => { d.open = d.id === 'secApproach'; });
$('secApproach').scrollIntoView();
const notes = [...document.querySelectorAll('#pd-mercator p.note')].filter(p => !p.hidden && !p.classList.contains('dial-help')).map(p => p.textContent);
if (S.param.mercator.planes !== 1) fail('the page should open with one plane');
if (notes.length !== 1 || !notes[0].startsWith('One plane is the rule')) fail('with one plane exactly the one-plane note should show: ' + JSON.stringify(notes));
if ($('par-mercator-turn').closest('.dial').hidden) fail('the turn dial should show with one plane');
if (!$('par-mercator-liftPlay') || !$('par-mercator-turnPlay')) fail('a play button is missing');
return 'one plane: ' + notes.length + ' note; label: ' + $('par-mercator-planes').closest('.dial').querySelector('label').textContent;
""", shot='panel-1plane.png', clip='#rules .rule', wait=None)

# 5 two planes: the other note, the Turn note, the scorecard
step(r"""
type('par-mercator-planesNum', '2');
const notes = [...document.querySelectorAll('#pd-mercator p.note')].filter(p => !p.hidden && !p.classList.contains('dial-help')).map(p => p.textContent);
if (notes.length !== 2 || !notes[0].startsWith('An earlier version') || !notes[1].startsWith('Set the planes to 1 to get a Turn dial')) fail('wrong notes with two planes: ' + JSON.stringify(notes));
if (!$('par-mercator-turn').closest('.dial').hidden) fail('the turn dial should be hidden with two planes');
if (!$('f-mercator').textContent.includes('folded onto the xy-plane')) fail('the formula line does not mention the fold');
return notes.join(' || ');
""", shot='panel-2planes.png', clip='#rules .rule')
step(r"""
return [...document.querySelectorAll('#card .row')].map(r => r.innerText.replace(/\s+/g, ' ')).join('\n');
""", shot='card-2planes.png', clip='#card')
step(r"""
type('par-mercator-planesNum', '1');
await sleep(400);
return 'back to one plane';
""")
step(r"""
return [...document.querySelectorAll('#card .row')].map(r => r.innerText.replace(/\s+/g, ' ')).join('\n');
""", shot='card-1plane.png', clip='#card')

# 6 Lift: play turns round at the end of the slider instead of jumping to the other end
step(r"""
type('par-mercator-liftNum', '1.9');
$('par-mercator-liftPlay').click();
const seen = [];
for (let i = 0; i < 70; i++) { await sleep(30); seen.push(S.param.mercator.lift); }
$('par-mercator-liftPlay').click();
let worst = 0;
for (let i = 1; i < seen.length; i++) worst = Math.max(worst, Math.abs(seen[i] - seen[i - 1]));
const top = Math.max(...seen), last = seen[seen.length - 1];
type('par-mercator-liftNum', '0');
if (worst > 0.5) fail('Lift jumped by ' + worst.toFixed(2) + ' during the sweep');
if (!(top > 1.95)) fail('the sweep did not reach the end of the slider: top ' + top);
if (!(last < top)) fail('the sweep did not turn round: ' + seen.slice(-5));
return 'lift sweep from 1.9: top ' + top.toFixed(3) + ', then back down to ' + last.toFixed(3) + ', largest change between samples ' + worst.toFixed(3) + '; button title: ' + $('par-mercator-liftPlay').title;
""")

# 7 extreme ranges on the approach dials
step(r"""
if (typeof L.setExtreme !== 'function') return 'skipped: no setExtreme on this page';
const rng = id => $(id).min + '..' + $(id).max;
const before = [rng('par-mercator-planes'), rng('par-mercator-lift'), rng('par-lathe-spin')].join(' ');
L.setExtreme(true);
const after = [rng('par-mercator-planes'), rng('par-mercator-lift'), rng('par-lathe-spin')].join(' ');
if (after !== '1..16 -6..6 -31..33') fail('wide ranges are ' + after);
const tags = ['par-mercator-planesWide', 'par-mercator-liftWide', 'par-lathe-spinWide'].filter(id => $(id) && !$(id).hidden).length;
if (tags !== 3) fail('expected three wide tags, saw ' + tags);
if ($('par-mercator-turnWide') || $('par-bulb-latWide')) fail('an angle dial got a wide range');
type('par-mercator-planesNum', '40'); type('par-mercator-liftNum', '15');
const p = S.param.mercator;
if (p.planes !== 40 || p.lift !== 15) fail('typed wide values not taken: ' + JSON.stringify(p));
type('par-mercator-planesNum', '100');
if (p.planes !== 64) fail('planes should stop at 64 when typed, it is ' + p.planes);
type('par-mercator-planesNum', '12'); type('par-mercator-liftNum', '0');
return 'ordinary ' + before + ' -> wide ' + after + '; typed 40 planes and lift 15 taken, 100 planes held at 64; now 12 planes';
""", shot='wide-12planes.png', clip='#stage')
step(r"""
if (typeof L.setExtreme !== 'function') return 'skipped';
type('par-mercator-liftNum', '15');
$('ap-lathe').click(); type('par-lathe-spinNum', '21');
if (S.param.lathe.spin !== 21) fail('spin 21 not taken: ' + S.param.lathe.spin);
type('par-lathe-spinNum', '20');
if (S.param.lathe.spin % 2 === 0) fail('an even spin was taken: ' + S.param.lathe.spin);
return 'lathe spin ' + S.param.lathe.spin;
""", shot='wide-spin.png', clip='#stage')
step(r"""
if (typeof L.setExtreme !== 'function') return 'skipped';
L.setExtreme(false);
const p = S.param.mercator, q = S.param.lathe;
if (p.planes !== 8 || p.lift !== 6 || q.spin !== 9) fail('switching extreme ranges off should pull values back to 8, 6 and 9: ' + JSON.stringify([p, q]));
document.querySelector('#approachReset .dial-reset').click();
if (S.approach !== 0 || p.planes !== 1 || p.lift !== 0 || q.spin !== 1) fail('the Approach reset left ' + JSON.stringify([S.approach, p, q]));
return 'extreme off pulled planes to 8, lift to 6, spin to 9; the Approach reset put back 1, 0, 1';
""")
with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
    json.dump(steps, f, ensure_ascii=False, indent=1)
print(len(steps), 'steps written')
