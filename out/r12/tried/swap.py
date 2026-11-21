"""One-off: in the three tried entries, put the verdict ("Tried for ... Why it fails ...") where the page shows it
first (the paragraph under the formula, `about`), and how the rule works in the note above the dials.
Also: the smooth row of Blended planes with the pinch no longer speaks of a blend that folds over."""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(p, encoding='utf-8').read()
n = 0
for eid in ('softfold', 'axisbulb', 'pillow'):
    a = s.index("    id: '%s', name:" % eid)
    b = s.index("    roundNote:", a)
    block = s[a:b]
    note = re.search(r"\{ type: 'note', text: '(Tried for: [^']*)' \},", block)
    about = re.search(r"\n    about: '([^']*)',\n", block)
    assert note and about, eid
    new = block.replace(note.group(0), "{ type: 'note', text: 'How it works: %s' }," % about.group(1))
    new = new.replace(about.group(0), "\n    about: '%s',\n" % note.group(1))
    assert new != block
    s = s[:a] + new + s[b:]
    n += 1
old = "      return ['part', 'No jump with 2 planes (measured at n = 2, 3 and −2). The blend between the planes is steep, and it folds over itself.' + aprPole(n)];"
assert s.count(old) == 1
s = s.replace(old, old.replace("' + aprPole(n)];", "'];"))
old2 = "      if (p.planes > 2) return ['no', 'With 3 or 4 planes single rays"
assert s.count(old2) == 1
s = s.replace(old2, "      if (p.mix > 1.5) return ['part', 'No jump was found with the pinch (measured with 2 and 3 planes at n = 2, 3 and −2), but toward each seam the rule is squeezed flat.'];\n" + old2)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('swapped in %d entries' % n)
