"""Move the six Julia entries that were found with two planes under their own heading.

  python out/r5/page/julia_headings.py      then      python notes/ui_embed.py

Only the `source` field of those six lines of data/julia-presets.json changes (from "explored" to "two planes");
the page takes the heading of a list entry from that field (uiJuliaOptions in src/js/80-ui.js).
"""
import io, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PATH = os.path.join(ROOT, 'data', 'julia-presets.json')
NAMES = ['Cracked Basilica', 'Split conch', 'Flint', 'Plated egg', 'Plated ball', 'Cracked gourd']
with io.open(PATH, encoding='utf-8', newline='') as f:
    lines = f.read().split('\n')
done = []
for i, line in enumerate(lines):
    for n in NAMES:
        if line.lstrip().startswith('{"name": "%s",' % n):
            if '"source": "explored"' in line:
                lines[i] = line.replace('"source": "explored"', '"source": "two planes"')
                done.append(n)
            elif '"source": "two planes"' in line:
                done.append(n + ' (already)')
with io.open(PATH, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(lines))
items = json.load(io.open(PATH, encoding='utf-8'))
print('changed:', done)
print('entries:', len(items), '| by source:', {s: sum(1 for it in items if it['source'] == s) for s in sorted({it['source'] for it in items})})
