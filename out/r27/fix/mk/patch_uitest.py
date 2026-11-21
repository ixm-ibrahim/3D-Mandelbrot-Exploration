"""Round 27, fixer: make my copy of the builder's ui.js (out/r27/fix/mk/ui.js) expect what the page does after the
fixes. Run once, on a fresh copy of out/r27/entry/mk/ui.js with the page names already changed.
  python out/r27/fix/mk/patch_uitest.py
"""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'ui.js')
s = io.open(p, encoding='utf-8', newline='').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90])
    s = s.replace(old, new)


rep("// Steps 3 and 4: the state,", """// (Round 27, fixer: the builder's list, changed where the fixes changed what the page does: the Approach section is
// put away while Balls on balls is on show, the panel comes into view after the click on the row, the table under the
// picture is put away with one sentence, the trap-solid choice and the Examples are put away with one sentence, the
// depth dial starts at 5, and at 100 the page says what is on the screen.)
// Steps 3 and 4: the state,""")
rep("""if ($('apMenuName').textContent !== 'Balls on balls') fail('menu name: ' + $('apMenuName').textContent);
""", """if ($('apMenuName').textContent === 'Balls on balls') fail('the Approach button should keep the name of the approach');
""")
rep("""if (!shown('secApproach') || shown('secEq') || shown('secMod') || shown('apPanels') || shown('apAboutBtn')) fail('Approach section: menu should stay, equation and dials go');
""", """if (shown('secApproach') || shown('secEq') || shown('secMod') || shown('apPanels') || shown('apAboutBtn')) fail('the Approach section should be put away, as for the first group');
{ const top = id => Math.round($(id).getBoundingClientRect().top), bot = id => Math.round($(id).getBoundingClientRect().bottom);
  if (top('stage') < 0 || top('kleinGroup') < 0 || bot('ballsDepth') > innerHeight || bot('ballsFrame') > innerHeight) fail('after the click the picture, the choice of group and the three dials should be in the window: stage ' + top('stage') + ', choice ' + top('kleinGroup') + ', depth dial ' + bot('ballsDepth') + ', Frame it ' + bot('ballsFrame') + ' of ' + innerHeight);
  ok('after the click, without scrolling: picture top at ' + top('stage') + ', choice of group at ' + top('kleinGroup') + ', Frame it ends at ' + bot('ballsFrame') + ' (window ' + innerHeight + ')'); }
if (!shown('ballsCardNote') || shown('card')) fail('the table under the picture should be put away with its sentence');
ok('table under the picture: put away, with "' + $('ballsCardNote').textContent + '"');
""")
rep("""ok('one click: Kleinian, Balls on balls, framed (' + g0[0] + ' of 165 probes hit, none on the outer ring); menu reads "Balls on balls"; note""",
    """ok('one click: Kleinian, Balls on balls, framed (' + g0[0] + ' of 165 probes hit, none on the outer ring); note""")
rep("""if (!shown('ballsWarn') || !/Drawing radius/.test($('ballsWarn').textContent)) fail('no note about the endless chain at 100');""",
    """if (!shown('ballsWarn') || !/^At 100 the chain never ends/.test($('ballsWarn').textContent)) fail('no sentence about the endless chain at 100: ' + $('ballsWarn').textContent);
const said100 = $('ballsWarn').textContent;
type('ballsSize', 99); await settle();
if (!shown('ballsWarn') || !/Drawing radius/.test($('ballsWarn').textContent)) fail('at 99 the chain runs past the Drawing radius and the page should say so: ' + $('ballsWarn').textContent);
type('ballsSize', 100); await settle();""")
rep("""ok('size dial: 100 gives t = 1 (and the note "' + 'The chain of balls runs out past the Drawing radius…"), 25""",
    """ok('size dial: 100 gives t = 1 (and the sentence "' + said100 + '"), 99 the sentence about the Drawing radius, 25""")
rep("""type('ballsDepth', 3); await settle(); const s3 = sig();
type('ballsDepth', 40); await settle(); const s40 = sig();
if (s3 === s0) fail('depth 3 should swell the balls');
type('ballsDepth', L.BALLS.rounds); await settle();
ok('depth: 3 rounds changes the picture (' + hits(s3) + ' probes hit against ' + hits(s0) + '), 40 rounds ' + (s40 === s0 ? 'gives the same probes as the default' : 'differs from the default in the probes'));""",
    """if ($('ballsDepth').min !== '5') fail('the depth slider should start at 5: ' + $('ballsDepth').min);
type('ballsDepth', 1); await settle();
if (S.k.bit !== 5) fail('a depth below 5 should be held at 5: ' + S.k.bit);
const s5 = sig();
type('ballsDepth', 40); await settle(); const s40 = sig();
type('ballsDepth', L.BALLS.rounds); await settle();
ok('depth: the dial starts at 5 (1 is held at 5; ' + hits(s5) + ' probes hit against ' + hits(s0) + ' at the default), 40 rounds ' + (s40 === s0 ? 'gives the same probes as the default' : 'differs from the default in the probes'));""")
rep("""  if (!notes.includes('Balls on balls has no trap solid: in this view the trap only colours the balls.')) fail('no sentence about the trap solid: ' + notes.join(' / ').slice(0, 300));
  if (shown('col-thick') || shown('col-skip')) fail('the dials of a trap solid should be put away');""",
    """  if (!notes.includes('Balls on balls has no trap solid, and so none of the examples, which are all trap solids: in this view the trap only colours the balls.')) fail('no sentence about the trap solid: ' + notes.join(' / ').slice(0, 300));
  if (notes.some(t => /Three tones has no shape/.test(t))) fail('the sentence about Three tones shows although the trap is not Three tones');
  if (shown('col-thick') || shown('col-skip') || shown('col-solid') || shown('trapExamples')) fail('the choice of a trap solid, its dials and the Examples list should be put away');""")
rep("""out.push('   trap solid choices 1 and 2: the sentence "Balls on balls has no trap solid: in this view the trap only colours the balls." shows, the picture is the plain one');""",
    """out.push('   trap solid set to 1 and 2 from a script: the choice, its dials and the Examples list are put away, one sentence stands there ("Balls on balls has no trap solid, and so none of the examples, ..."), no sentence about Three tones, the picture is the plain one');""")
rep("""ok('Examples: a Kleinian example goes to the first group (its panel, no Approach menu)');""",
    """ok('Examples: the list is put away for Balls on balls; a Kleinian example applied from a script goes to the first group (its panel, no Approach menu)');""")
rep("""  if ($('apMenuName').textContent !== 'Balls on balls' || shown('apPanels')) fail('back from Learn the menu should read Balls on balls again');""",
    """  if (shown('secApproach') || shown('apPanels') || !shown('ballsCardNote')) fail('back from Learn the Approach section should be put away again, and the table too');""")
rep("""  if (document.body.classList.contains('is-learn') || !(S.mode === 'k' && S.k.group === 1) || $('apMenuName').textContent !== 'Balls on balls') fail('the row chosen under Learn should leave Learn and show Balls on balls');""",
    """  if (document.body.classList.contains('is-learn') || !(S.mode === 'k' && S.k.group === 1) || shown('secApproach')) fail('the row chosen under Learn should leave Learn and show Balls on balls');""")
rep("""document.querySelectorAll('#rules input[type=radio]:checked').length !== 1) fail('under Learn the Approach menu should show the approach');""",
    """document.querySelectorAll('#rules input[type=radio]:checked').length !== 1) fail('under Learn the Approach menu should show the approach');
  if (!shown('card') || shown('ballsCardNote')) fail('under Learn the table belongs to the approach and should be on show');""")
i = s.index("// 11. choosing a real approach afterwards"); j = s.index("// 12. Reset everything")
s = s[:i] + """// 11. choosing a real approach afterwards: as with the first group. The Approach section is put away in the Kleinian
// view, the way back is the Show buttons, and there the approaches do what they always did.
const other = L.APPROACHES[(S.approach + 3) % L.APPROACHES.length];
$('ap-' + other.id).click(); await sleep(200);
if (S.mode !== 'k' || S.k.group !== 1 || apId() !== other.id) fail('an approach chosen from a script while Balls on balls is on show should stay in the Kleinian view, as with the first group: ' + S.mode + ' ' + apId());
$('mode-m').click(); await sleep(200);
if (S.mode !== 'm' || apId() !== other.id) fail('the Mandelbrot button: ' + S.mode + ' ' + apId());
if (!shown('secApproach') || !shown('secEq') || !shown('apPanels') || shown('kleinPanel') || $('apMenuName').textContent === 'Balls on balls' || !shown('card') || shown('ballsCardNote')) fail('the Approach section and the table did not come back whole');
await settle();
const camM = JSON.stringify(L.cam);
$('mode-k').click(); await sleep(100); $('mode-m').click(); await sleep(100);
if (JSON.stringify(L.cam) !== camM) fail('the camera after leaving is not the one the Mandelbrot button gives');
ok('leaving by the Mandelbrot button: the approach "' + other.name.replace(/<[^>]*>/g, '') + '", the Approach section and the table are back, the camera is the Mandelbrot start view');
$('mode-j').click(); await sleep(150); await settle();
$('ap-balls').click(); await sleep(150); await settle();
if (!(S.mode === 'k' && S.k.group === 1)) fail('the row from the Julia view');
$('apNext').click(); await sleep(200);
if (S.mode !== 'k') fail('the step button of the hidden Approach section should not leave the Kleinian view (as with the first group)');
$('mode-j').click(); await sleep(150); await settle();
if (S.mode !== 'j' || !shown('secApproach')) fail('the Julia button after Balls on balls');
ok('from the Julia view: the row, then the Julia button: back in the Julia view with the Approach section');
// with the first group on show an approach's radio does what it did: the Kleinian view stays
$('mode-k').click(); await sleep(100); $('kleinGroup0').click(); await sleep(150);
$('ap-' + other.id).click(); await sleep(150);
if (S.mode !== 'k' || apId() !== other.id) fail('with the first group the radio of an approach should not leave the Kleinian view');
ok('with either group on show, an approach chosen from a script stays in the Kleinian view, as on the frozen page');

""" + s[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ui.js patched')
