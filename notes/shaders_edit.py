"""Apply a list of exact replacements to src/js/30-shaders.js (each old text must occur exactly once).
Usage: python notes/shaders_edit.py edits.txt   where edits.txt holds blocks  <<<<\nold\n====\nnew\n>>>>
(an empty new part deletes the old text together with its line break)."""
import sys
p = 'src/js/30-shaders.js'
s = open(p, encoding='utf-8').read()
blocks = open(sys.argv[1], encoding='utf-8').read().split('<<<<\n')[1:]
for b in blocks:
    body = b.split('>>>>')[0]
    old, new = body.split('\n====\n')
    new = new[:-1] if new.endswith('\n') else new
    if new == '':
        old += '\n'
    assert s.count(old) == 1, 'expected exactly one match for:\n' + old
    s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('applied', len(blocks), 'edits')
