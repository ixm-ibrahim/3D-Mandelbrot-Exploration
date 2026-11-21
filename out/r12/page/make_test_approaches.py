"""Round 12, page: a test copy of the approach list with more entries and groups than the frozen one, to check
that the page's list code works for any number of them. Nothing here is for the published page.

  python out/r12/page/make_test_approaches.py   ->  out/r12/page/10-approaches-test.js
  python build.py --name r12-page-tried --base base12a --use <the page files> --swap js/10-approaches.js=out/r12/page/10-approaches-test.js

It is base12a/js/10-approaches.js (the frozen file) with three stand-in entries pushed on the end: two in the
group 'tried' and one in a group that has no heading. The stand-ins reuse the Split rule.
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src = io.open(os.path.join(ROOT, 'base12a', 'js', '10-approaches.js'), encoding='utf-8').read()
src += r"""
// ---- test only (out/r12/page/make_test_approaches.py): stand-ins for entries that other people may add
{
  const base = APPROACHES.find(a => a.id === 'split');
  APPROACHES.push(
    { ...base, id: 'try1', name: 'Stand-in rule one', group: 'tried', tag: 'A stand-in for a rule that was tried. It draws the Split solid.',
      params: [{ type: 'note', text: 'Tried for the test of the list. It fails at nothing: it is the Split rule under another name.' }] },
    { ...base, id: 'try2', name: 'Stand-in rule two', group: 'tried', tag: 'A second stand-in, with a long one-line description that has to wrap at phone width without pushing the page wide.' },
    { ...base, id: 'odd1', name: 'Stand-in with no heading', group: 'nowhere', tag: 'Its group has no heading, so it comes last.' },
  );
  MATH.try1 = MATH.split; MATH.try2 = MATH.split; MATH.odd1 = MATH.split;
}
"""
out = os.path.join(ROOT, 'out', 'r12', 'page', '10-approaches-test.js')
io.open(out, 'w', encoding='utf-8', newline='\n').write(src)
print('wrote ' + os.path.relpath(out, ROOT))
