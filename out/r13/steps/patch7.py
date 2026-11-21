def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (s.count(a), a[:70])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

sub('src/js/65-learn-steps.js', [
 ("const LEARN_PROBE_FLAT = [[0.7, 0.4, 0], [-0.9, 0.3, 0], [-0.2, -1.1, 0], [1.3, -0.5, 0], [-0.6, -0.1, 0]];\n",
  "// probes: a ring of 360 directions in the plane z = 0 (half a degree off the whole degrees, two lengths), and 8 numbers on the x-axis\nconst LEARN_PROBE_FLAT = Array.from({ length: 360 }, (x, k) => { const a = (k + 0.5) * PI / 180, r = k % 2 ? 1.2 : 0.8; return [r * Math.cos(a), r * Math.sin(a), 0]; });\nconst LEARN_PROBE_LINE = [-1.7, -1.1, -0.6, -0.2, 0.3, 0.8, 1.2, 1.9].map(x => [x, 0, 0]);\n"),
 ("""    const same = learnAgree(F, power, LEARN_PROBE_FLAT);
    note = space === 1
      ? 'On a line a number can lean only two ways from the positive side: 0° or 180°. The turn is the same turn as on a page, so a negative number has to swing through a direction the line does not have. Every approach in the list agrees on a line.'
      : 'On a page every approach in the list does the same two things: it turns the point and it stretches it. That is ordinary multiplication of complex numbers. The one exception is “Mandelbulb, classic”, which does not keep the flat plane.'
        + (same || id === 'classic' ? '' : ` With its dials as they are set now, “${A.name}” does not follow this flat rule in the plane z = 0 either.`);
    if (space === 1 && !aprWhole(n)) note += ' With a power that is not a whole number a negative number does not come back to the line.';""",
  """    // does the chosen approach, as its dials stand, give this same answer on the x-axis (line) or in the plane z = 0 (page)?
    const same = learnAgree(F, power, space === 1 ? LEARN_PROBE_LINE : LEARN_PROBE_FLAT), where = space === 1 ? 'on the x-axis' : 'in the plane z = 0';
    note = (space === 1
      ? 'On a line a number can lean only two ways from the positive side: 0° or 180°. The turn is the same turn as on a page, so a negative number has to swing through a direction the line does not have.'
      : 'On a page the point is turned and then stretched. That is ordinary multiplication of complex numbers.')
      + (same ? ` “${A.name}” does exactly this ${where}.`
        : id === 'classic' ? ` “${A.name}” is the one approach in the list that does not keep the flat plane, so ${where} it does not follow this picture.`
        : ` As the power and its dials are set now, “${A.name}” does not follow this picture ${where}.`);
    if (space === 1 && !aprWhole(n)) note += ' With a power that is not a whole number a negative number does not come back to the line.';"""),
])
sub('out/r13/steps/test.js', [
 ("  window.__LT = { space3, flat, samples, extra };", """  // which approaches, with their dials at the start, follow the complex power in the plane z = 0 and on the x-axis?
  function agree() {
    const pl = points(2).filter(p => len(p) > 1e-3), li = points(1).filter(p => len(p) > 1e-3), out = [];
    for (const a of AP) for (const n of POWERS) {
      const q = L.S.param[a.id], cnt = pts => pts.filter(p => { const w = MATH[a.id](p, n, q), z = cpow(p[0], p[1], n), want = [z[0], z[1], 0]; return len(sub(w, want)) <= 1e-9 * Math.max(1, len(want)); }).length;
      out.push(`${a.id} n=${n}: plane ${cnt(pl)}/${pl.length} line ${cnt(li)}/${li.length} | note2: ${learnPlan({ space: 2, id: a.id, n, params: q }).note.split('numbers.')[1]} | note1: ${learnPlan({ space: 1, id: a.id, n, params: q }).note.split('have.')[1]}`);
    }
    for (const [id, q, n] of [['mercator', { turn: 40 }, 2], ['mercator', { lift: 0.5 }, 2], ['tilt', { tilt: 1 }, 2.5], ['tilt', { tilt: 1 }, 2], ['bulb', { lat: 30 }, 2], ['bulb', { lon: 30 }, 3], ['classic', { theta: -90 }, 2], ['pillow', { layout: 1 }, 2], ['axisbulb', { k: 2 }, 2], ['axisbulb', { k: 5 }, 2], ['lathe', { spin: 3 }, 2]])
      out.push(`${id} ${JSON.stringify(q)} n=${n} | note2: ${learnPlan({ space: 2, id, n, params: q }).note.split('numbers.')[1]} | note1: ${learnPlan({ space: 1, id, n, params: q }).note.split('have.')[1]}`);
    return out.join('\n');
  }
  window.__LT = { space3, flat, samples, extra, agree };"""),
])
sub('out/r13/steps/run_tests.py', [
 ("        elif w == 'extra':", "        elif w == 'agree':\n            acts.append({'js': \"return '@@A' + window.__LT.agree()\"})\n        elif w == 'extra':"),
 ("what = sys.argv[1:] or IDS + ['flat1', 'flat2', 'extra', 'samples']", "what = sys.argv[1:] or IDS + ['flat1', 'flat2', 'extra', 'agree', 'samples']"),
 ("        elif val.startswith('@@R'):", "        elif val.startswith('@@A'):\n            with open(os.path.join(HERE, 'agree.txt'), 'w', encoding='utf-8') as f:\n                f.write(val[3:])\n        elif val.startswith('@@R'):"),
])
