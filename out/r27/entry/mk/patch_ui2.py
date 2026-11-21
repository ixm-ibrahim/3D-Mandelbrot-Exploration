"""Round 27, entry: second set of edits (the choice of group as two radios, so that the label is shown whole)."""
import io, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patch_ui import patch, O
patch(O + 'body.html', [
 ('            <div id="kleinGroupHost"></div>\n',
  '            <fieldset class="kgroup" id="kleinGroup">\n'
  '              <legend class="label">Group</legend>\n'
  '              <label class="check kgroup-opt"><input type="radio" name="kleinGroup" id="kleinGroup0" value="0" checked> <span>Pearls between two walls</span></label>\n'
  '              <label class="check kgroup-opt"><input type="radio" name="kleinGroup" id="kleinGroup1" value="1"> <span>Balls on balls <span class="kgroup-tag">a cousin of the flat picture: no c, no power</span></span></label>\n'
  '            </fieldset>\n'),
])
patch(O + 'js/80-ui.js', [
 ("  addSelect('kleinGroupHost', 'kleinGroup', 'Group', [[0, 'Pearls between two walls'], [1, `${BALLS_NAME} (${BALLS_TAG})`]], () => (K.group === 1 ? 1 : 0),\n"
  "    v => { K.group = +v === 1 ? 1 : 0; resetCam(); syncControls(); refresh(false); }, { def: 0 });\n",
  "  for (const g of [0, 1]) $('kleinGroup' + g).addEventListener('change', () => { K.group = g; resetCam(); syncControls(); refresh(false); });\n"),
 ("  $('kleinOld').hidden = balls; $('ballsPart').hidden = !balls;\n",
  "  $('kleinOld').hidden = balls; $('ballsPart').hidden = !balls;\n  $('kleinGroup' + (balls ? 1 : 0)).checked = true;\n"),
])
