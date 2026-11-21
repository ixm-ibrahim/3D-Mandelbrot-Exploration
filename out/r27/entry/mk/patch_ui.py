"""Round 27, entry: the edits of 80-ui.js, body.html and 90-boot.js, applied once to the copies in overlay/.
Kept as the record of what was changed (each pair: the old text, the new text). Run from the project root."""
import io


def patch(p, reps):
    s = io.open(p, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    for a, b in reps:
        a = a.replace('\n', nl)
        assert s.count(a) == 1, (p, a[:80], s.count(a))
        s = s.replace(a, b.replace('\n', nl))
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('patched', p)


O = 'out/r27/entry/overlay/'
UI = [
 ("  kleinAt: 0,        // the Kleinian entry last chosen\n",
  "  kleinAt: 0,        // the Kleinian entry last chosen\n  ballsBack: '',     // the kind of picture ('m' or 'j') the row Balls on balls of the Approach list was chosen from\n"),
 ("const UI_GROUPS = ['mandel', 'julia', 'klein', 'approach', 'eq', 'mod', 'cut', 'colour', 'view', 'q'];",
  "const UI_GROUPS = ['mandel', 'julia', 'klein', 'balls', 'approach', 'eq', 'mod', 'cut', 'colour', 'view', 'q'];   // 'balls': the dials of the second Kleinian group"),
 ("  const k = S.mode === 'k';\n  $('mandelPanel').hidden = S.mode !== 'm'; $('juliaPanel').hidden = S.mode !== 'j'; $('kleinPanel').hidden = !k;\n  ['secApproach', 'secEq', 'secMod'].forEach(id => { $(id).hidden = k; });",
  "  const k = S.mode === 'k', balls = ballsShown();\n  $('mandelPanel').hidden = S.mode !== 'm'; $('juliaPanel').hidden = S.mode !== 'j'; $('kleinPanel').hidden = !k;\n  // (Balls on balls has a row in the Approach list, so while it is on show the menu stays, without the equation\n  // and without any approach's dials: see uiApPaint)\n  ['secApproach', 'secEq', 'secMod'].forEach(id => { $(id).hidden = k && !(balls && id === 'secApproach'); });"),
 ("  const on = $('ap-' + ap().id), row = on.closest('.rule'), list = $('rules');",
  "  const on = ballsShown() ? $('ap-balls') : $('ap-' + ap().id), row = on.closest('.rule, .cousin-row'), list = $('rules');"),
 ("  if (!order.length) return;\n  S.approach = order[((at < 0 ? 0 : at + dir) % order.length + order.length) % order.length];\n  refresh(false);",
  "  if (!order.length) return;\n  // the row Balls on balls stands after the last approach: from it, the next is the first approach and the previous the last\n  if (ballsShown()) { S.approach = order[dir > 0 ? 0 : order.length - 1]; uiBallsLeave(); refresh(false); return; }\n  S.approach = order[((at < 0 ? 0 : at + dir) % order.length + order.length) % order.length];\n  refresh(false);"),
 ("function uiApPaint() {\n  const a = ap();\n  if ($('apMenuName').textContent !== a.name) $('apMenuName').innerHTML = a.name;\n  document.querySelectorAll('#rules .rule').forEach(el => el.classList.toggle('is-on', el.dataset.ap === a.id));\n  APPROACHES.forEach((x, i) => {\n    $('ap-' + x.id).checked = i === S.approach;",
  "function uiApPaint() {\n  const a = ap(), balls = ballsShown(), name = balls ? BALLS_NAME : a.name;\n  if ($('apMenuName').textContent !== name) $('apMenuName').innerHTML = name;\n  document.querySelectorAll('#rules .rule').forEach(el => el.classList.toggle('is-on', !balls && el.dataset.ap === a.id));\n  // While Balls on balls is on show its row is the marked one, no approach is ticked (so that a click on any of\n  // them is a change), and the approach's own dials and explanation are put away (86-balls.css).\n  if ($('apBallsRow')) $('apBallsRow').classList.toggle('is-on', balls);\n  $('apPart').classList.toggle('is-cousin', balls);\n  APPROACHES.forEach((x, i) => {\n    $('ap-' + x.id).checked = !balls && i === S.approach;"),
 ("function uiKleinMark() {\n  if (!UI.kleinSel) return;\n  UI.kleinSel.sync();",
  "// The row Balls on balls of the Approach list: the Kleinian view, that group, and its start view. The kind of\n// picture it was chosen from is kept, for the way back.\nfunction uiBallsShow() {\n  if (S.mode !== 'k') UI.ballsBack = S.mode;\n  uiApMenu(false);\n  S.mode = 'k'; S.k.group = 1;\n  ballsFrame();\n  syncControls();\n  refresh(false);\n}\n// An approach was chosen while Balls on balls is on show. An approach means nothing to a Kleinian group, so the page\n// leaves the Kleinian view as the Show buttons leave it (start view and all): back to the kind of picture the row\n// was chosen from, or to the Julia set when it was reached another way (as uiOnePlane does).\nfunction uiBallsLeave() {\n  if (!ballsShown()) return;\n  S.mode = UI.ballsBack === 'm' ? 'm' : 'j';\n  resetCam(); syncControls();\n}\nfunction uiKleinMark() {\n  if (!UI.kleinSel) return;\n  // the panel holds two groups: the parts of the one that is not chosen are put away\n  const balls = ballsOn(), bw = $('ballsWarn'), bt = ballsTrouble();\n  $('kleinOld').hidden = balls; $('ballsPart').hidden = !balls;\n  if (bw.textContent !== bt) bw.textContent = bt;\n  bw.hidden = !bt;\n  UI.kleinSel.sync();"),
 ("  uiOnce('klein', JSON.stringify(S.k) + (kleinSwallowed() ? '|near' : '') + (kleinReach() > S.view.bound ? '|cut' : ''), uiKleinMark);",
  "  uiOnce('klein', JSON.stringify(S.k) + (kleinSwallowed() ? '|near' : '') + (kleinReach() > S.view.bound ? '|cut' : '') + '|' + ballsTrouble(), uiKleinMark);"),
 ("  S.flat = false; S.mode = 'm'; S.approach = 0;\n  UI.presetCut = false; UI.mosaicCut = null; UI.mosaicWas = false;\n  resetGroup(UI_GROUPS);",
  "  S.flat = false; S.mode = 'm'; S.approach = 0;\n  S.k.group = 0; UI.ballsBack = '';   // the Kleinian view goes back to its first group\n  UI.presetCut = false; UI.mosaicCut = null; UI.mosaicWas = false;\n  resetGroup(UI_GROUPS);"),
 ("  addReset('kleinReset', 'klein', { after: () => { UI.kleinAt = 0; uiKleinMark(); } });\n",
  "  addReset('kleinReset', 'klein', { after: () => { UI.kleinAt = 0; uiKleinMark(); } });\n"
  "  // The choice between the two groups, at the top of the panel, and the second group's own part: its note, its\n"
  "  // three dials (group 'balls'), Frame it and a reset of its own. A change of group is a change of picture, so the\n"
  "  // view goes to that group's start, as it does for a change of the kind of picture.\n"
  "  addSelect('kleinGroupHost', 'kleinGroup', 'Group', [[0, 'Pearls between two walls'], [1, `${BALLS_NAME} (${BALLS_TAG})`]], () => (K.group === 1 ? 1 : 0),\n"
  "    v => { K.group = +v === 1 ? 1 : 0; resetCam(); syncControls(); refresh(false); }, { def: 0 });\n"
  "  $('ballsNote').textContent = BALLS_NOTE;\n"
  "  const bSet = () => { uiKleinMark(); touch(); };\n"
  "  addDial('ballsDials', 'ballsSize', 'Size of the neighbours, % of the middle ball', 10, 100, 0.1, () => +ballsShare(K.bt).toFixed(2), v => { K.bt = ballsFromShare(v); bSet(); },\n"
  "    { lo: 2, hi: 100, def: +ballsShare(BALLS_T).toFixed(2), group: 'balls', help: 'How wide the two big neighbours are, next to the middle ball. At 100 they are as big as the middle ball and the chain never ends. Smaller neighbours give a shorter chain.' });\n"
  "  addSelect('ballsDials', 'ballsGrid', 'Whole numbers', BALLS_GRIDS, () => K.bgrid | 0, v => { K.bgrid = +v | 0; bSet(); },\n"
  "    { def: 0, group: 'balls', help: 'The slides go by the whole numbers of this grid. The square grid sets the buds four-fold round the chain, the honeycomb grid six-fold. With a line only, buds grow only round the flat picture. All three have the same flat cut.' });\n"
  "  addDial('ballsDials', 'ballsDepth', 'Depth of the search', 2, 40, 1, () => K.bit, v => { K.bit = Math.round(v); bSet(); },\n"
  "    { lo: 1, hi: 200, int: true, def: BALLS_ROUNDS, group: 'balls', help: 'How many rounds of the recipe a point may take: a slide, then a sphere inversion. A point that is still undecided after that counts as inside, so with too few rounds the balls look swollen. Raise it when you zoom far in.' });\n"
  "  $('ballsFrame').addEventListener('click', ballsFrame);\n"
  "  addReset('ballsReset', 'balls', { after: uiKleinMark });\n"),
 ("    inp.addEventListener('change', () => { S.approach = i; refresh(false); });",
  "    inp.addEventListener('change', () => { S.approach = i; uiBallsLeave(); refresh(false); });"),
 ("  // the closing text names the entries kept for the record, whichever of them this page has\n",
  "  // Balls on balls is not an approach (it is the second group of the Kleinian view), but this list is where entries\n"
  "  // are looked for: it has a row of its own here, last, under its own heading. The row is a button, not one of the\n"
  "  // radios, and it is not in APPROACHES.\n"
  "  const cousin = document.createElement('div');\n"
  "  cousin.className = 'rule-group'; cousin.id = 'apg-cousin'; cousin.setAttribute('role', 'group'); cousin.setAttribute('aria-labelledby', 'apgh-cousin');\n"
  "  cousin.innerHTML = `<p class=\"label rule-group-head\" id=\"apgh-cousin\">A cousin, not a rule</p><div class=\"cousin-row\" id=\"apBallsRow\"><button type=\"button\" class=\"rule-head cousin-head\" id=\"ap-balls\" title=\"Shows this object in the Kleinian view, where its dials are.\"><span class=\"mark\"></span><span class=\"name\">${BALLS_NAME}</span><span class=\"cousin-tag\">${BALLS_TAG}</span></button></div>`;\n"
  "  $('rules').appendChild(cousin);\n"
  "  $('ap-balls').addEventListener('click', uiBallsShow);\n"
  "  $('ap-balls').addEventListener('keydown', e => {\n"
  "    if (e.key === 'Escape') { e.preventDefault(); uiApMenu(false, true); }\n"
  "    else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); const all = $('rules').querySelectorAll('input[type=radio]'); if (all.length) all[all.length - 1].focus(); }\n"
  "  });\n"
  "  // the closing text names the entries kept for the record, whichever of them this page has\n"),
 ("    if (to !== undefined) { e.preventDefault(); UI.apKeys = true; const t = all[clamp(to, 0, all.length - 1)]; t.focus(); apMark(t); }",
  "    if (to === all.length && e.key !== 'End') { e.preventDefault(); apMark(null); uiApInfo(null); $('ap-balls').focus(); }   // past the last approach: the row Balls on balls\n    else if (to !== undefined) { e.preventDefault(); UI.apKeys = true; const t = all[clamp(to, 0, all.length - 1)]; t.focus(); apMark(t); }"),
 ("  apBtn.addEventListener('click', e => { UI.apKeys = e.detail === 0; uiApMenu(apPop.hidden, true); if (UI.apKeys && !apPop.hidden) apMark($('ap-' + ap().id)); });",
  "  apBtn.addEventListener('click', e => { UI.apKeys = e.detail === 0; uiApMenu(apPop.hidden, true); if (UI.apKeys && !apPop.hidden && !ballsShown()) apMark($('ap-' + ap().id)); });"),
]
BODY = [
 ("          <div class=\"sec-body\">\n            <p class=\"note\">A true 3D Kleinian group:",
  "          <div class=\"sec-body\">\n            <div id=\"kleinGroupHost\"></div>\n            <div class=\"klein-part\" id=\"kleinOld\">\n            <p class=\"note\">A true 3D Kleinian group:"),
 ("            <div id=\"kleinReset\"></div>\n",
  "            <div id=\"kleinReset\"></div>\n            </div>\n"
  "            <!-- the second group, Balls on balls (32-balls.js; its dials are built by boot() in 80-ui.js) -->\n"
  "            <div class=\"klein-part\" id=\"ballsPart\" hidden>\n"
  "            <p class=\"note\" id=\"ballsNote\"></p>\n"
  "            <p class=\"note warn-note\" id=\"ballsWarn\" role=\"status\" hidden></p>\n"
  "            <div id=\"ballsDials\" class=\"sec-inner\"></div>\n"
  "            <div class=\"row-btns\"><button class=\"btn\" id=\"ballsFrame\" type=\"button\" title=\"Move the camera to a view that shows the whole chain. Nothing else changes.\">Frame it</button></div>\n"
  "            <div id=\"ballsReset\"></div>\n"
  "            </div>\n"),
]
BOOT = [
 ("boot();\n",
  "// Balls on balls, the second group of the Kleinian view (round 27): the twin of its inside test and of its distance,\n"
  "// for the checks. ballsInside(x, y, z, { t, grid, rounds }) -> true / false, in picture coordinates.\n"
  "if (typeof ballsInside === 'function') Object.assign(window.squaringLab, { ballsInside, ballsEstimate, ballsReach, ballsFrame, ballsShow: uiBallsShow, ballsOn, BALLS: { k2: BALLS_K2, t: BALLS_T, rounds: BALLS_ROUNDS, name: BALLS_NAME, tag: BALLS_TAG, note: BALLS_NOTE } });\n"
  "boot();\n"),
]
if __name__ == '__main__':
    patch(O + 'js/80-ui.js', UI)
    patch(O + 'body.html', BODY)
    patch(O + 'js/90-boot.js', BOOT)
