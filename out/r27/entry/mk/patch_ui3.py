"""Round 27, entry: third set of edits. The row of Balls on balls stands in the open menu under the list of
approaches, not inside it: the smoke list reads every heading and row of #rules and expects the approaches only."""
import io, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patch_ui import patch, O
patch(O + 'js/80-ui.js', [
 ("  cousin.className = 'rule-group'; cousin.id = 'apg-cousin';", "  cousin.className = 'cousin-group'; cousin.id = 'apg-cousin';"),
 ('<p class=\\"label rule-group-head\\" id=\\"apgh-cousin\\">'.replace('\\"', '"'), '<p class="label cousin-group-head" id="apgh-cousin">'),
 ("  $('rules').appendChild(cousin);\n", "  $('rules').after(cousin);   // in the open menu, right under the list (the list itself holds the approaches and nothing else)\n"),
 ("  // are looked for: it has a row of its own here, last, under its own heading.", "  // are looked for: it has a row of its own in the open menu, under the list, with its own heading."),
 ("  list.scrollTop = Math.max(0, row.offsetTop - (list.clientHeight - row.offsetHeight) / 2);", "  if (list.contains(row)) list.scrollTop = Math.max(0, row.offsetTop - (list.clientHeight - row.offsetHeight) / 2);"),
])
