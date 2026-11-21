"""Round 27, entry: fifth set of edits. Under the Learn tab the Approach menu is the approach's, also when the picture
left behind is Balls on balls (Learn does there what it does for the first Kleinian group)."""
import io, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patch_ui import patch, O
patch(O + 'js/80-ui.js', [
 ("  const k = S.mode === 'k', balls = ballsShown();\n", "  const k = S.mode === 'k', balls = uiBallsMenu();\n"),
 ("  const on = ballsShown() ? $('ap-balls') : $('ap-' + ap().id),", "  const on = uiBallsMenu() ? $('ap-balls') : $('ap-' + ap().id),"),
 ("  if (ballsShown()) { S.approach = order[dir > 0 ? 0 : order.length - 1]; uiBallsLeave(); refresh(false); return; }", "  if (uiBallsMenu()) { S.approach = order[dir > 0 ? 0 : order.length - 1]; uiBallsLeave(); refresh(false); return; }"),
 ("  const a = ap(), balls = ballsShown(), name = balls ? BALLS_NAME : a.name;", "  const a = ap(), balls = uiBallsMenu(), name = balls ? BALLS_NAME : a.name;"),
 ("// The row Balls on balls of the Approach list: the Kleinian view, that group, and its start view. The kind of\n// picture it was chosen from is kept, for the way back.\nfunction uiBallsShow() {\n  if (S.mode !== 'k') UI.ballsBack = S.mode;\n  uiApMenu(false);\n  S.mode = 'k'; S.k.group = 1;\n",
  "// Balls on balls holds the Approach menu (its row marked, its name on the button) while it is on show. Not under\n// the Learn tab: Learn is about the chosen approach whatever picture was left behind, so there the menu is the\n// approach's, as it is for the first Kleinian group.\nconst uiBallsMenu = () => ballsShown() && !S.learn;\n// The row Balls on balls of the Approach menu: the Kleinian view, that group, and its start view. The kind of\n// picture it was chosen from is kept, for the way back. Chosen under the Learn tab, it leaves Learn the way the\n// Kleinian button under Show does.\nfunction uiBallsShow() {\n  if (S.mode !== 'k') UI.ballsBack = S.mode;\n  uiApMenu(false);\n  S.k.group = 1;\n  if (S.learn) $('mode-k').click();\n  S.mode = 'k';\n"),
 ("function uiBallsLeave() {\n  if (!ballsShown()) return;", "function uiBallsLeave() {\n  if (!uiBallsMenu()) return;"),
 ("if (UI.apKeys && !apPop.hidden && !ballsShown()) apMark(", "if (UI.apKeys && !apPop.hidden && !uiBallsMenu()) apMark("),
 ("  $('ap-balls').addEventListener('click', uiBallsShow);\n", "  $('ap-balls').addEventListener('click', uiBallsShow);\n  // going into the Learn tab and out of it changes what the menu shows while Balls on balls is the picture behind it\n  new MutationObserver(uiApPaint).observe(document.body, { attributes: true, attributeFilter: ['class'] });\n"),
])
