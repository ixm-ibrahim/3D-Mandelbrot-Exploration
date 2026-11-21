"""Replace everything after the data blocks of src/js/75-presets.js with out/r4/page/presets_tail.js.

  python out/r4/page/splice_presets.py

The data blocks (between the marker lines) are written by notes/ui_embed.py and are left alone here.
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TARGET = os.path.join(ROOT, 'src', 'js', '75-presets.js')
MARK = '// </klein-data>\n'

src = io.open(TARGET, encoding='utf-8').read()
head = src[:src.index(MARK) + len(MARK)]
tail = io.open(os.path.join(ROOT, 'out', 'r4', 'page', 'presets_tail.js'), encoding='utf-8').read()
io.open(TARGET, 'w', encoding='utf-8', newline='\n').write(head + tail)
print('75-presets.js: tail replaced, %d bytes' % len(head + tail))
