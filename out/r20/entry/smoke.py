"""Round 20, entry: the page's smoke list (tools/smoke-v14.json, 62 steps, unchanged except that its pictures go to
out/r20/entry/smoke/) followed by steps for the new entry (Julia mode only), on dist/r20-entry.html at 1400x950.
  python out/r20/entry/smoke.py -> smoke-steps.json, smoke.log"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const apId = () => L.APPROACHES[S.approach].id;
// 15 x 11 probes: [hits, hits on the outermost row or column, the pattern]
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0, s = ''; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) { const hit = !!L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11); s += hit ? '1' : '0'; if (hit) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } } return [n, ring, s]; };
"""
NEW = [
    # 1. choose the entry in Julia mode from the menu's own radio; c = -1 at 40 iterations
    dict(js=HEAD + """
$('mode-j').click(); await sleep(150);
if (S.mode !== 'j') fail('not in Julia mode');
const r = $('ap-windsq'); if (!r) fail('the list has no entry windsq');
r.click(); await sleep(250);
if (apId() !== 'windsq') fail('choosing the entry did not take: ' + apId());
const a = L.APPROACHES[S.approach];
if (a.name !== 'Wind, then square' || a.group !== 'inversions') fail('name or group wrong: ' + a.name + ', ' + a.group);
if (L.APPROACHES.indexOf(a) !== L.APPROACHES.length - 1 || L.APPROACHES[L.APPROACHES.length - 2].id !== 'turnalong') fail('the entry should stand at the end of the list, after turnalong');
if ((a.params || []).some(p => p.type === 'dial')) fail('the entry should have no dial');
if (a.deMax !== 0) fail('the entry should cap the distance estimate at Rough');
S.n = 2; S.iter = 40; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; L.resetCam(); go(); await sleep(200);
return 'windsq chosen in Julia mode; menu reads ' + $('apMenuName').textContent;
""", wait='done', timeout=600, shot='out/r20/entry/smoke/r20-1-windsq-basilica.png'),
    # 2. the picture is there and whole; the words are on the page; the cap holds whatever the setting says
    dict(js=HEAD + """
if (apId() !== 'windsq' || S.mode !== 'j') fail('lost the entry or the mode');
if ($('apMenuName').textContent !== 'Wind, then square') fail('the menu should name the entry, it reads ' + $('apMenuName').textContent);
const g = grid();
if (g[0] < 8) fail('the picture of c = -1 is empty: ' + g[0] + ' of 165 probes hit');
if (g[1] > 4) fail('c = -1 is not whole in the frame: ' + g[1] + ' probes on the outer ring');
const all = document.body.innerText;
for (const t of ['P(W(v))', '3φ − 2·sin 6φ / 6']) if (!all.includes(t)) fail('missing on the page: ' + t);
// the explanation opens with "About this approach": tag, about and note
const btn = $('apAboutBtn'), box = $('apAbout'), wasHidden = box.hidden;
if (wasHidden) { btn.click(); await sleep(150); }
if (box.hidden) fail('"About this approach" did not open the explanation');
for (const t of ['Wind each point round the x-axis three times', 'The lab always draws this rule with “Distance estimate” at “Rough”', 'has not been judged yet', 'Where it falls short']) if (!box.textContent.includes(t)) fail('missing in the explanation: ' + t);
if (/undefined|NaN|TEXT PENDING|<|>/.test(box.textContent.replace(/[xyz] [<>] 0/g, ''))) fail('the explanation shows a stray mark');
if (wasHidden) { btn.click(); await sleep(150); }
for (const t of ['TEXT PENDING', 'undefined', 'NaN']) if ($('secApproach').innerText.includes(t)) fail('the Approach section shows ' + t);
const was = S.q.de;
S.q.de = 0; go(); await sleep(300); for (let i = 0; i < 2000 && !L.idle(); i++) await sleep(20);
const p0 = grid()[2];
S.q.de = 3; go(); await sleep(300); for (let i = 0; i < 2000 && !L.idle(); i++) await sleep(20);
const p3 = grid()[2];
S.q.de = was; go();
if (p0 !== p3) fail('the picture changed with the Distance estimate setting: the cap at Rough does not hold');
if (L.R.failed) fail('a program failed: ' + L.R.failed);
return 'c = -1 drawn (' + g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring); words on the page; same probes with the setting at Rough and at Exact';
""", wait='done', timeout=600),
    # 3. the 2D view: the cut at z = 0
    dict(js=HEAD + """
$('flat').click(); await sleep(200);
if (!S.flat) fail('the 2D view did not come on');
const w = $('stage').clientWidth, h = $('stage').clientHeight, p = L.pick(w / 2, h / 2);
if (!p || Math.abs(p[2]) > 1e-9) fail('the 2D view is not the cut at z = 0');
return 'the 2D view shows the cut at z = ' + p[2];
""", wait='done', timeout=600, shot='out/r20/entry/smoke/r20-2-windsq-flat.png'),
    # 4. powers 3, 4 and 5 (Julia, c = 0.3 on the x-axis) and the rabbit at power 2: a picture each, no failed program
    dict(js=HEAD + """
$('flat').click(); await sleep(200);
if (S.flat) fail('the 3D view did not come back');
const out = [];
for (const [n, c] of [[3, [0.3, 0, 0]], [4, [0.3, 0, 0]], [5, [0.3, 0, 0]], [2, [-0.122561, 0.744862, 0]]]) {
  S.n = n; S.c = c; S.iter = 30; L.resetCam(); go(); await sleep(300);
  for (let i = 0; i < 6000 && !L.idle(); i++) await sleep(20);
  if (!L.idle()) fail('power ' + n + ' never finished drawing');
  if (L.R.failed) fail('power ' + n + ': a program failed: ' + L.R.failed);
  const g = grid(); if (g[0] < 5) fail('power ' + n + ': the picture is empty (' + g[0] + ' probes hit)');
  const f = L.APPROACHES[S.approach].formula({}, n); if (/undefined|NaN/.test(f)) fail('power ' + n + ': bad formula text');
  out.push('power ' + n + ' c ' + JSON.stringify(c) + ': ' + g[0] + ' probes hit');
}
return out.join('; ');
""", wait='done', timeout=900, shot='out/r20/entry/smoke/r20-3-windsq-rabbit.png'),
    # 5. Reset everything brings the opening state back (the one-plane rule)
    dict(js=HEAD + """
$('resetAll').click(); await sleep(400);
if (apId() !== 'mercator' || S.approach !== 0 || S.flat) fail('Reset everything did not bring the opening state back: ' + apId());
return 'reset: ' + apId() + ', mode ' + S.mode;
""", wait='done', timeout=600),
]

if __name__ == '__main__':
    base = json.load(open(os.path.join(run.ROOT, 'tools', 'smoke-v14.json'), encoding='utf-8'))
    os.makedirs(os.path.join(HERE, 'smoke'), exist_ok=True)
    for s in base:
        if 'shot' in s:
            s['shot'] = 'out/r20/entry/smoke/' + os.path.basename(s['shot'])
    steps = base + NEW
    code, text, vals = run.shot(run.PAGE, steps, 'smoke-steps', '1400x950')
    text += 'exit %d\n' % code
    run.write('smoke.log', text)
    lines = text.splitlines()
    print('\n'.join(lines[:3])); print('...'); print('\n'.join(lines[-24:]))
    print('steps:', len(base), '+', len(NEW))
    sys.exit(code)
