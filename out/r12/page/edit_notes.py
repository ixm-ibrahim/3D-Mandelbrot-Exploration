# Round 12, page: the Julia entries whose note sent the reader to a Planes dial under Sphere inversions now name
# the entry of the Approach list. The notes live in data/julia-presets.json; notes/ui_embed.py copies them into
# src/js/75-presets.js (run it after this).
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, 'data', 'julia-presets.json')
OLD = ': set Planes to 2 under Sphere inversions.'
NEW = ': choose Sphere inversions, two planes in the Approach section.'
raw = io.open(path, encoding='utf-8', newline='').read()
n = raw.count(OLD)
if n != 7:
    sys.exit('expected 7 notes with the old wording, found %d' % n)
io.open(path, 'w', encoding='utf-8', newline='').write(raw.replace(OLD, NEW))
print('%d notes reworded in data/julia-presets.json' % n)
