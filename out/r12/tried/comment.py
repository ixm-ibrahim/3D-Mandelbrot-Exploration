"""One-off: the comment above the three tried entries says where the verdict stands."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(p, encoding='utf-8').read()
old = """  // beads) without the tear of the two-planes rule, and failed. Each starts with a note that says what it was
  // tried for and why it fails. Their prototypes, numbers and pictures are in out/lab2/<softfold|axisbulb|pillow2>/.
"""
new = """  // beads) without the tear of the two-planes rule, and failed. Each says what it was tried for and why it fails
  // in the two places the list shows first: in short in `tag` (the line under the name, shown for every entry),
  // and in full in `about` (the paragraph under the formula). How the rule works is the note above its dials.
  // Their prototypes, numbers and pictures are in out/lab2/<softfold|axisbulb|pillow2>/; this round's checks in out/r12/tried/.
"""
assert s.count(old) == 1
io.open(p, 'w', encoding='utf-8', newline='\n').write(s.replace(old, new))
print('comment updated')
